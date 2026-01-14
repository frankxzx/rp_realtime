import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export const sessionService = {
  async startSession(scenario) {
    const response = await api.post('/sessions/start', { scenario })
    return response.data
  },

  async submitTurn(sessionId, turnNumber, userInput, audioBlob) {
    const formData = new FormData()
    formData.append('turn_number', turnNumber)
    formData.append('user_input', userInput)
    formData.append('audio_file', audioBlob, 'audio.mp3')

    const response = await api.post(
      `/sessions/${sessionId}/turns`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    return response.data
  },

  async submitSnapshot(sessionId, imageData) {
    const response = await api.post(`/sessions/${sessionId}/snapshots`, {
      session_id: sessionId,
      image_data: imageData
    })
    return response.data
  },

  async completeSession(sessionId) {
    const response = await api.post(`/sessions/${sessionId}/complete`)
    return response.data
  },

  async getSession(sessionId) {
    const response = await api.get(`/sessions/${sessionId}`)
    return response.data
  }
}
