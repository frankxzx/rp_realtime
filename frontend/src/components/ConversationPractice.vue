<template>
  <div class="conversation-practice">
    <div class="practice-container">
      <!-- Camera View -->
      <div class="camera-section">
        <video ref="videoElement" class="video-preview" autoplay playsinline></video>
        <div v-if="snapshotCount > 0" class="snapshot-indicator">
          📷 {{ snapshotCount }} snapshots captured
        </div>
      </div>

      <!-- Recording Controls -->
      <div class="controls-section">
        <div class="turn-info">
          <h3>Turn {{ sessionStore.currentTurn + 1 }}</h3>
          <div class="mode-selector">
            <label>
              <input type="radio" v-model="useWebSocket" :value="false" :disabled="sessionStore.isRecording" />
              Standard Mode
            </label>
            <label>
              <input type="radio" v-model="useWebSocket" :value="true" :disabled="sessionStore.isRecording" />
              ⚡ WebSocket Mode (Low Latency)
            </label>
          </div>
          <div v-if="useWebSocket && wsConnected" class="ws-status connected">
            🟢 WebSocket Connected
          </div>
          <div v-else-if="useWebSocket && !wsConnected" class="ws-status disconnected">
            🔴 WebSocket Disconnected
          </div>
          <div v-if="errorMessage" class="error-notification">
            ⚠️ {{ errorMessage }}
          </div>
        </div>

        <div v-if="!sessionStore.isRecording" class="control-buttons">
          <button @click="startRecording" class="btn-record" :disabled="isProcessing">
            🎤 Start Recording
          </button>
        </div>

        <div v-else class="recording-active">
          <div class="timer">
            <div class="timer-display">{{ formatTime(recordingTime) }}</div>
            <div class="timer-bar">
              <div 
                class="timer-progress" 
                :style="{ width: `${(recordingTime / sessionStore.maxRecordingDuration) * 100}%` }"
              ></div>
            </div>
            <div class="timer-max">Max: {{ sessionStore.maxRecordingDuration }}s</div>
          </div>
          <button @click="sendRecording" class="btn-send" :disabled="isProcessing">
            📤 Send
          </button>
        </div>

        <!-- Transcription Input -->
        <div v-if="sessionStore.isRecording" class="transcription-section">
          <label for="userInput">Your Response:</label>
          <textarea
            id="userInput"
            v-model="userInput"
            placeholder="Type what you're saying (for analysis)..."
            rows="3"
          ></textarea>
        </div>
      </div>

      <!-- Feedback Display -->
      <div v-if="latestFeedback || streamingResponse" class="feedback-section">
        <h3>AI Response</h3>
        <div class="ai-response">
          <span v-if="streamingResponse" class="streaming">{{ streamingResponse }}</span>
          <span v-else-if="latestFeedback">{{ latestFeedback.ai_response }}</span>
          <span v-if="isStreaming" class="cursor">▊</span>
        </div>

        <div v-if="latestFeedback" class="feedback-grid">
          <div class="feedback-card">
            <h4>💡 Ideal Answer</h4>
            <p>{{ latestFeedback.ideal_answer }}</p>
          </div>

          <div class="feedback-card">
            <h4>📊 Scores</h4>
            <div class="scores">
              <div v-for="(score, dimension) in latestFeedback.scores" :key="dimension" class="score-item">
                <span class="dimension">{{ dimension }}:</span>
                <span class="score">{{ score }}/10</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${score * 10}%` }"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="feedback-card">
            <h4>💬 Suggestions</h4>
            <ul>
              <li v-for="(suggestion, index) in latestFeedback.suggestions" :key="index">
                {{ suggestion }}
              </li>
            </ul>
          </div>

          <div class="feedback-card">
            <h4>🔍 Insights</h4>
            <ul>
              <li v-for="(insight, index) in latestFeedback.insights" :key="index">
                {{ insight }}
              </li>
            </ul>
          </div>

          <div class="feedback-card direction">
            <h4>🎯 Next Direction</h4>
            <p>{{ latestFeedback.direction }}</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="endConversation" class="btn-secondary" :disabled="isProcessing || sessionStore.turns.length === 0">
          End Conversation & Get Report
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useSessionStore } from '../stores/session'
import { AudioRecorder, CameraCapture } from '../services/media'
import { sessionService } from '../services/api'
import { websocketService } from '../services/websocket'

export default {
  name: 'ConversationPractice',
  emits: ['conversation-ended'],
  setup(props, { emit }) {
    const sessionStore = useSessionStore()
    const videoElement = ref(null)
    const audioRecorder = new AudioRecorder()
    const cameraCapture = new CameraCapture()

    const userInput = ref('')
    const recordingTime = ref(0)
    const isProcessing = ref(false)
    const snapshotCount = ref(0)
    const latestFeedback = ref(null)
    
    // WebSocket specific state
    const useWebSocket = ref(true) // Default to WebSocket mode for low latency
    const wsConnected = ref(false)
    const streamingResponse = ref('')
    const isStreaming = ref(false)
    const errorMessage = ref('')

    let recordingTimer = null
    let snapshotTimer = null

    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    // WebSocket handlers
    const handleStreamChunk = (chunk) => {
      streamingResponse.value += chunk
    }

    const handleStreamComplete = (fullResponse, turnNumber) => {
      isStreaming.value = false
      
      // Create feedback object with the streaming response
      // Note: WebSocket mode prioritizes speed - full feedback requires separate API calls
      const feedback = {
        ai_response: fullResponse,
        turn_number: turnNumber,
        user_input: userInput.value || 'User response (audio only)',
        scores: {}, // Scores available in Standard mode
        suggestions: [], // Suggestions available in Standard mode
        insights: [], // Insights available in Standard mode
        direction: '', // Direction available in Standard mode
        ideal_answer: '', // Ideal answer available in Standard mode
        websocket_mode: true // Flag to indicate this is a WebSocket response
      }
      
      sessionStore.addTurn(feedback)
      latestFeedback.value = feedback
      streamingResponse.value = ''
    }

    const handleStreamError = (errorMessage) => {
      isStreaming.value = false
      console.error('WebSocket stream error:', errorMessage)
      errorMessage.value = `Streaming error: ${errorMessage}`
      streamingResponse.value = ''
      // Clear error after 5 seconds
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
    }

    const handleStreamStart = (turnNumber) => {
      isStreaming.value = true
      streamingResponse.value = ''
    }

    // Setup WebSocket connection when mode is enabled
    const setupWebSocket = async () => {
      if (useWebSocket.value && sessionStore.sessionId) {
        try {
          await websocketService.connect(sessionStore.sessionId)
          wsConnected.value = true
          
          // Register handlers
          websocketService.on('chunk', handleStreamChunk)
          websocketService.on('complete', handleStreamComplete)
          websocketService.on('error', handleStreamError)
          websocketService.on('start', handleStreamStart)
        } catch (error) {
          console.error('Failed to connect WebSocket:', error)
          wsConnected.value = false
        }
      }
    }

    // Watch for WebSocket mode changes
    watch(useWebSocket, async (newValue) => {
      if (newValue) {
        await setupWebSocket()
      } else {
        websocketService.disconnect()
        wsConnected.value = false
      }
    })

    const startRecording = async () => {
      const success = await audioRecorder.startRecording()
      if (!success) {
        alert('Failed to start recording. Please check microphone permissions.')
        return
      }

      sessionStore.setRecording(true)
      recordingTime.value = 0

      // Start recording timer
      recordingTimer = setInterval(() => {
        recordingTime.value++
        sessionStore.setRecordingTime(recordingTime.value)

        // Auto-stop at max duration
        if (recordingTime.value >= sessionStore.maxRecordingDuration) {
          sendRecording()
        }
      }, 1000)

      // Start snapshot timer
      snapshotTimer = setInterval(async () => {
        const snapshot = cameraCapture.captureSnapshot()
        if (snapshot) {
          try {
            await sessionService.submitSnapshot(sessionStore.sessionId, snapshot)
            snapshotCount.value++
          } catch (error) {
            console.error('Error submitting snapshot:', error)
          }
        }
      }, sessionStore.snapshotInterval * 1000)
    }

    const sendRecording = async () => {
      if (recordingTimer) {
        clearInterval(recordingTimer)
        recordingTimer = null
      }
      if (snapshotTimer) {
        clearInterval(snapshotTimer)
        snapshotTimer = null
      }

      isProcessing.value = true
      sessionStore.setRecording(false)

      try {
        const audioBlob = await audioRecorder.stopRecording()
        if (!audioBlob) {
          throw new Error('Failed to get recording')
        }

        // Use WebSocket or standard HTTP based on mode
        if (useWebSocket.value && wsConnected.value) {
          // Send via WebSocket for low latency streaming
          const userMessage = userInput.value || 'User response (audio only)'
          websocketService.sendMessage(userMessage, sessionStore.currentTurn)
          
          // Upload audio to blob storage via HTTP in background
          sessionService.submitTurn(
            sessionStore.sessionId,
            sessionStore.currentTurn,
            userMessage,
            audioBlob
          ).catch(error => {
            console.error('Error uploading audio:', error)
            errorMessage.value = 'Warning: Audio upload failed. Your conversation will continue but audio may not be saved.'
            setTimeout(() => {
              errorMessage.value = ''
            }, 5000)
          })
          
          userInput.value = ''
        } else {
          // Standard HTTP mode with full feedback
          const feedback = await sessionService.submitTurn(
            sessionStore.sessionId,
            sessionStore.currentTurn,
            userInput.value || 'User response (audio only)',
            audioBlob
          )

          sessionStore.addTurn(feedback)
          latestFeedback.value = feedback
          userInput.value = ''
        }
      } catch (error) {
        console.error('Error submitting turn:', error)
        alert('Failed to submit recording. Please try again.')
      } finally {
        isProcessing.value = false
      }
    }

    const endConversation = async () => {
      isProcessing.value = true
      try {
        const report = await sessionService.completeSession(sessionStore.sessionId)
        sessionStore.setAssessmentReport(report)
        emit('conversation-ended', report)
      } catch (error) {
        console.error('Error completing session:', error)
        alert('Failed to generate report. Please try again.')
      } finally {
        isProcessing.value = false
      }
    }

    onMounted(async () => {
      if (videoElement.value) {
        await cameraCapture.startCamera(videoElement.value)
      }
      
      // Setup WebSocket if enabled
      if (useWebSocket.value) {
        await setupWebSocket()
      }
    })

    onUnmounted(() => {
      if (recordingTimer) clearInterval(recordingTimer)
      if (snapshotTimer) clearInterval(snapshotTimer)
      audioRecorder.cleanup()
      cameraCapture.stopCamera()
      
      // Cleanup WebSocket
      websocketService.disconnect()
    })

    return {
      sessionStore,
      videoElement,
      userInput,
      recordingTime,
      isProcessing,
      snapshotCount,
      latestFeedback,
      useWebSocket,
      wsConnected,
      streamingResponse,
      isStreaming,
      errorMessage,
      formatTime,
      startRecording,
      sendRecording,
      endConversation
    }
  }
}
</script>

<style scoped>
.conversation-practice {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.practice-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.camera-section {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-preview {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}

.snapshot-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
}

.controls-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.turn-info h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.mode-selector {
  margin: 15px 0;
  display: flex;
  gap: 20px;
}

.mode-selector label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #495057;
}

.mode-selector input[type="radio"] {
  cursor: pointer;
}

.mode-selector input[type="radio"]:disabled {
  cursor: not-allowed;
}

.ws-status {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 10px;
}

.ws-status.connected {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.ws-status.disconnected {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.error-notification {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  margin-top: 10px;
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-response .streaming {
  color: #0056b3;
}

.ai-response .cursor {
  animation: blink 1s infinite;
  color: #007bff;
  font-weight: bold;
}

@keyframes blink {
  0%, 49% {
    opacity: 1;
  }
  50%, 100% {
    opacity: 0;
  }
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.btn-record {
  flex: 1;
  padding: 15px 30px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-record:hover:not(:disabled) {
  background-color: #c82333;
}

.btn-record:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.recording-active {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.timer {
  text-align: center;
}

.timer-display {
  font-size: 48px;
  font-weight: bold;
  color: #dc3545;
  margin-bottom: 10px;
}

.timer-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.timer-progress {
  height: 100%;
  background: #dc3545;
  transition: width 1s linear;
}

.timer-max {
  font-size: 12px;
  color: #6c757d;
}

.btn-send {
  padding: 15px 30px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-send:hover:not(:disabled) {
  background-color: #218838;
}

.btn-send:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.transcription-section {
  margin-top: 15px;
}

.transcription-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #495057;
}

.transcription-section textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.feedback-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.feedback-section h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
}

.ai-response {
  background: #e7f3ff;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 16px;
  line-height: 1.6;
}

.feedback-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.feedback-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #007bff;
}

.feedback-card h4 {
  margin: 0 0 10px 0;
  color: #495057;
  font-size: 14px;
}

.feedback-card p {
  margin: 0;
  color: #6c757d;
  line-height: 1.6;
}

.feedback-card ul {
  margin: 0;
  padding-left: 20px;
}

.feedback-card li {
  margin-bottom: 8px;
  color: #6c757d;
}

.feedback-card.direction {
  grid-column: 1 / -1;
  border-left-color: #28a745;
}

.scores {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dimension {
  flex: 0 0 120px;
  font-weight: 600;
  color: #495057;
  text-transform: capitalize;
}

.score {
  flex: 0 0 50px;
  color: #007bff;
  font-weight: bold;
}

.score-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #dc3545, #ffc107, #28a745);
  transition: width 0.3s;
}

.action-buttons {
  display: flex;
  justify-content: center;
}

.btn-secondary {
  padding: 12px 24px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

.btn-secondary:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}
</style>
