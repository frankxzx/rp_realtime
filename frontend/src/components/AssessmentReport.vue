<template>
  <div class="assessment-report">
    <div class="report-container">
      <h2>📊 Assessment Report</h2>

      <div class="report-section">
        <h3>Scenario</h3>
        <div class="info-grid">
          <div class="info-item">
            <strong>Context:</strong> {{ report.scenario.context }}
          </div>
          <div class="info-item">
            <strong>Target Audience:</strong> {{ report.scenario.target_audience }}
          </div>
          <div class="info-item">
            <strong>Purpose:</strong> {{ report.scenario.purpose }}
          </div>
          <div class="info-item">
            <strong>Language:</strong> {{ report.scenario.target_language }}
          </div>
        </div>
      </div>

      <div class="report-section">
        <h3>Overall Performance</h3>
        <div class="overall-scores">
          <div v-for="(score, dimension) in report.overall_scores" :key="dimension" class="overall-score-item">
            <div class="score-label">{{ dimension }}</div>
            <div class="score-value">{{ score }}/10</div>
            <div class="score-bar-large">
              <div class="score-fill" :style="{ width: `${score * 10}%` }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="report-section">
        <h3>Summary</h3>
        <p class="summary-text">{{ report.summary }}</p>
      </div>

      <div class="report-section">
        <h3>Visual Analysis</h3>
        <div class="analysis-grid">
          <div class="analysis-item">
            <strong>Facial Expression:</strong>
            <p>{{ report.visual_analysis.facial_expression }}</p>
          </div>
          <div class="analysis-item">
            <strong>Body Language:</strong>
            <p>{{ report.visual_analysis.body_language }}</p>
          </div>
          <div class="analysis-item">
            <strong>Confidence Level:</strong>
            <p>{{ report.visual_analysis.confidence_level }}</p>
          </div>
          <div class="analysis-item">
            <strong>Engagement Indicators:</strong>
            <ul>
              <li v-for="(indicator, index) in report.visual_analysis.engagement_indicators" :key="index">
                {{ indicator }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="report-section">
        <h3>Audio Analysis</h3>
        <div class="analysis-grid">
          <div class="analysis-item">
            <strong>Tone:</strong>
            <p>{{ report.audio_analysis.tone }}</p>
          </div>
          <div class="analysis-item">
            <strong>Pace:</strong>
            <p>{{ report.audio_analysis.pace }}</p>
          </div>
          <div class="analysis-item">
            <strong>Clarity:</strong>
            <p>{{ report.audio_analysis.clarity }}</p>
          </div>
          <div class="analysis-item">
            <strong>Emotional Indicators:</strong>
            <ul>
              <li v-for="(indicator, index) in report.audio_analysis.emotional_indicators" :key="index">
                {{ indicator }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="report-section">
        <h3>Recommendations</h3>
        <ul class="recommendations-list">
          <li v-for="(recommendation, index) in report.recommendations" :key="index">
            {{ recommendation }}
          </li>
        </ul>
      </div>

      <div class="report-section">
        <h3>Turn-by-Turn Details</h3>
        <div v-for="turn in report.turns" :key="turn.turn_number" class="turn-detail">
          <h4>Turn {{ turn.turn_number + 1 }}</h4>
          <div class="turn-content">
            <div class="turn-item">
              <strong>Your Response:</strong>
              <p>{{ turn.user_input }}</p>
            </div>
            <div class="turn-item">
              <strong>AI Response:</strong>
              <p>{{ turn.ai_response }}</p>
            </div>
            <div class="turn-item">
              <strong>Scores:</strong>
              <div class="turn-scores">
                <span v-for="(score, dim) in turn.scores" :key="dim" class="turn-score">
                  {{ dim }}: {{ score }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="startNewSession" class="btn-primary">
          Start New Practice Session
        </button>
        <button @click="downloadReport" class="btn-secondary">
          Download Report
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { useSessionStore } from '../stores/session'

export default {
  name: 'AssessmentReport',
  props: {
    report: {
      type: Object,
      required: true
    }
  },
  emits: ['new-session'],
  setup(props, { emit }) {
    const sessionStore = useSessionStore()

    const startNewSession = () => {
      sessionStore.resetSession()
      emit('new-session')
    }

    const downloadReport = () => {
      const reportData = JSON.stringify(props.report, null, 2)
      const blob = new Blob([reportData], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `assessment-report-${props.report.session_id}.json`
      a.click()
      URL.revokeObjectURL(url)
    }

    return {
      startNewSession,
      downloadReport
    }
  }
}
</script>

<style scoped>
.assessment-report {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.report-container {
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

h3 {
  color: #495057;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

h4 {
  color: #6c757d;
  margin-bottom: 10px;
}

.report-section {
  margin-bottom: 40px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.info-item strong {
  color: #495057;
  display: block;
  margin-bottom: 5px;
}

.overall-scores {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overall-score-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.score-label {
  flex: 0 0 150px;
  font-weight: 600;
  color: #495057;
  text-transform: capitalize;
  font-size: 18px;
}

.score-value {
  flex: 0 0 80px;
  color: #007bff;
  font-weight: bold;
  font-size: 24px;
}

.score-bar-large {
  flex: 1;
  height: 30px;
  background: #e9ecef;
  border-radius: 15px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #dc3545, #ffc107, #28a745);
  transition: width 0.5s;
}

.summary-text {
  font-size: 16px;
  line-height: 1.8;
  color: #495057;
  background: #e7f3ff;
  padding: 20px;
  border-radius: 4px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.analysis-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

.analysis-item strong {
  color: #495057;
  display: block;
  margin-bottom: 8px;
}

.analysis-item p {
  margin: 0;
  color: #6c757d;
}

.analysis-item ul {
  margin: 0;
  padding-left: 20px;
}

.analysis-item li {
  color: #6c757d;
  margin-bottom: 5px;
}

.recommendations-list {
  background: #fff3cd;
  padding: 20px 40px;
  border-radius: 4px;
  border-left: 4px solid #ffc107;
}

.recommendations-list li {
  margin-bottom: 10px;
  color: #856404;
  font-size: 16px;
}

.turn-detail {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.turn-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 10px;
}

.turn-item strong {
  color: #495057;
  display: block;
  margin-bottom: 5px;
}

.turn-item p {
  margin: 0;
  color: #6c757d;
  line-height: 1.6;
}

.turn-scores {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.turn-score {
  background: #007bff;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  text-transform: capitalize;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  padding-top: 30px;
  border-top: 2px solid #e9ecef;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style>
