import { defineStore } from 'pinia'

export const useSessionStore = defineStore('session', {
  state: () => ({
    sessionId: null,
    scenario: null,
    maxRecordingDuration: 60,
    snapshotInterval: 5,
    turns: [],
    currentTurn: 0,
    isRecording: false,
    recordingTime: 0,
    assessmentReport: null
  }),

  actions: {
    setSession(sessionData) {
      this.sessionId = sessionData.session_id
      this.scenario = sessionData.scenario
      this.maxRecordingDuration = sessionData.max_recording_duration
      this.snapshotInterval = sessionData.snapshot_interval
    },

    addTurn(turnFeedback) {
      this.turns.push(turnFeedback)
      this.currentTurn++
    },

    setRecording(isRecording) {
      this.isRecording = isRecording
    },

    setRecordingTime(time) {
      this.recordingTime = time
    },

    setAssessmentReport(report) {
      this.assessmentReport = report
    },

    resetSession() {
      this.sessionId = null
      this.scenario = null
      this.turns = []
      this.currentTurn = 0
      this.isRecording = false
      this.recordingTime = 0
      this.assessmentReport = null
    }
  },

  getters: {
    hasActiveSession: (state) => !!state.sessionId,
    latestTurn: (state) => state.turns[state.turns.length - 1] || null
  }
})
