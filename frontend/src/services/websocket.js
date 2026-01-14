/**
 * WebSocket service for real-time conversation with FastAPI backend
 * Provides low-latency streaming responses from Azure OpenAI via LangChain
 */

class WebSocketService {
  constructor() {
    this.ws = null
    this.sessionId = null
    this.messageHandlers = {
      chunk: [],
      complete: [],
      error: [],
      start: []
    }
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 3
    this.reconnectDelay = 1000 // ms
    this.reconnecting = false // Flag to prevent multiple simultaneous reconnect attempts
  }

  /**
   * Connect to WebSocket endpoint
   * @param {string} sessionId - Session ID for the conversation
   * @returns {Promise<void>}
   */
  connect(sessionId) {
    return new Promise((resolve, reject) => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      this.sessionId = sessionId
      
      // Determine WebSocket URL from environment or default to current host
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      
      // Check for environment variable (Vite uses import.meta.env)
      const wsHost = import.meta?.env?.VITE_WS_HOST || 
                     (window.location.host.includes('localhost:5173') 
                       ? 'localhost:8000'  // Development fallback
                       : window.location.host)  // Production
      
      const wsUrl = `${protocol}//${wsHost}/ws/conversation/${sessionId}`
      
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log(`WebSocket connected to session ${sessionId}`)
        this.reconnectAttempts = 0
        resolve()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        this.handleReconnect()
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
    })
  }

  /**
   * Handle incoming WebSocket messages
   * @param {object} data - Parsed message data
   */
  handleMessage(data) {
    const { type } = data

    if (type === 'chunk' && this.messageHandlers.chunk.length > 0) {
      this.messageHandlers.chunk.forEach(handler => handler(data.content))
    } else if (type === 'complete' && this.messageHandlers.complete.length > 0) {
      this.messageHandlers.complete.forEach(handler => handler(data.content, data.turn_number))
    } else if (type === 'error' && this.messageHandlers.error.length > 0) {
      this.messageHandlers.error.forEach(handler => handler(data.message))
    } else if (type === 'start' && this.messageHandlers.start.length > 0) {
      this.messageHandlers.start.forEach(handler => handler(data.turn_number))
    }
  }

  /**
   * Handle reconnection logic
   */
  handleReconnect() {
    if (this.reconnecting) {
      return // Prevent multiple simultaneous reconnection attempts
    }
    
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.sessionId) {
      this.reconnecting = true
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect(this.sessionId).catch(error => {
          console.error('Reconnection failed:', error)
        }).finally(() => {
          this.reconnecting = false
        })
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  /**
   * Send user message to backend
   * @param {string} content - User's message
   * @param {number} turnNumber - Current turn number
   */
  sendMessage(content, turnNumber) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected')
    }

    this.ws.send(JSON.stringify({
      type: 'user_message',
      content,
      turn_number: turnNumber
    }))
  }

  /**
   * Register event handler
   * @param {string} event - Event type (chunk, complete, error, start)
   * @param {function} handler - Handler function
   */
  on(event, handler) {
    if (this.messageHandlers[event]) {
      this.messageHandlers[event].push(handler)
    }
  }

  /**
   * Remove event handler
   * @param {string} event - Event type
   * @param {function} handler - Handler function to remove
   */
  off(event, handler) {
    if (this.messageHandlers[event]) {
      this.messageHandlers[event] = this.messageHandlers[event].filter(h => h !== handler)
    }
  }

  /**
   * Clear all event handlers for a specific event
   * @param {string} event - Event type
   */
  clearHandlers(event) {
    if (this.messageHandlers[event]) {
      this.messageHandlers[event] = []
    }
  }

  /**
   * Send ping to keep connection alive
   */
  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'ping' }))
    }
  }

  /**
   * Disconnect WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.sessionId = null
    
    // Clear all handlers
    Object.keys(this.messageHandlers).forEach(event => {
      this.messageHandlers[event] = []
    })
  }

  /**
   * Check if WebSocket is connected
   * @returns {boolean}
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// Export singleton instance
export const websocketService = new WebSocketService()
