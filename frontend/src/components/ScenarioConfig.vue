<template>
  <div class="scenario-config">
    <h2>Configure Your Practice Scenario</h2>
    <form @submit.prevent="startSession" class="config-form">
      <div class="form-group">
        <label for="context">Scenario Context:</label>
        <input
          id="context"
          v-model="scenario.context"
          type="text"
          placeholder="e.g., Job interview for software engineer position"
          required
        />
      </div>

      <div class="form-group">
        <label for="target_audience">Target Audience:</label>
        <input
          id="target_audience"
          v-model="scenario.target_audience"
          type="text"
          placeholder="e.g., Senior hiring manager with technical background"
          required
        />
      </div>

      <div class="form-group">
        <label for="purpose">Purpose:</label>
        <input
          id="purpose"
          v-model="scenario.purpose"
          type="text"
          placeholder="e.g., Interview skills practice"
          required
        />
      </div>

      <div class="form-group">
        <label for="target_language">Target Language:</label>
        <input
          id="target_language"
          v-model="scenario.target_language"
          type="text"
          placeholder="e.g., English"
          value="English"
        />
      </div>

      <div class="form-group">
        <label for="custom_prompt">Custom Instructions (Optional):</label>
        <textarea
          id="custom_prompt"
          v-model="scenario.custom_prompt"
          placeholder="Any additional instructions for the AI..."
          rows="3"
        ></textarea>
      </div>

      <button type="submit" class="btn-primary" :disabled="loading">
        {{ loading ? 'Starting...' : 'Start Practice Session' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import { sessionService } from '../services/api'
import { useSessionStore } from '../stores/session'

export default {
  name: 'ScenarioConfig',
  emits: ['session-started'],
  setup(props, { emit }) {
    const sessionStore = useSessionStore()
    const loading = ref(false)
    const scenario = ref({
      context: '',
      target_audience: '',
      purpose: '',
      target_language: 'English',
      custom_prompt: ''
    })

    const startSession = async () => {
      loading.value = true
      try {
        const sessionData = await sessionService.startSession(scenario.value)
        sessionStore.setSession(sessionData)
        emit('session-started')
      } catch (error) {
        console.error('Error starting session:', error)
        alert('Failed to start session. Please try again.')
      } finally {
        loading.value = false
      }
    }

    return {
      scenario,
      loading,
      startSession
    }
  }
}
</script>

<style scoped>
.scenario-config {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.config-form {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #495057;
}

input,
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.btn-primary {
  width: 100%;
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>
