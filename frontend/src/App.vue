<template>
  <div id="app">
    <header class="app-header">
      <h1>🎭 RP Realtime - Conversation Practice</h1>
      <p class="tagline">Practice conversations with AI-powered feedback</p>
    </header>

    <main class="app-main">
      <ScenarioConfig 
        v-if="currentView === 'config'" 
        @session-started="handleSessionStarted"
      />
      
      <ConversationPractice 
        v-if="currentView === 'practice'" 
        @conversation-ended="handleConversationEnded"
      />
      
      <AssessmentReport 
        v-if="currentView === 'report' && assessmentReport" 
        :report="assessmentReport"
        @new-session="handleNewSession"
      />
    </main>

    <footer class="app-footer">
      <p>Powered by Azure OpenAI Realtime API & LangChain</p>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useSessionStore } from './stores/session'
import ScenarioConfig from './components/ScenarioConfig.vue'
import ConversationPractice from './components/ConversationPractice.vue'
import AssessmentReport from './components/AssessmentReport.vue'

export default {
  name: 'App',
  components: {
    ScenarioConfig,
    ConversationPractice,
    AssessmentReport
  },
  setup() {
    const sessionStore = useSessionStore()
    const currentView = ref('config')
    const assessmentReport = ref(null)

    const handleSessionStarted = () => {
      currentView.value = 'practice'
    }

    const handleConversationEnded = (report) => {
      assessmentReport.value = report
      currentView.value = 'report'
    }

    const handleNewSession = () => {
      currentView.value = 'config'
      assessmentReport.value = null
    }

    return {
      currentView,
      assessmentReport,
      handleSessionStarted,
      handleConversationEnded,
      handleNewSession
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  color: #2c3e50;
  font-size: 36px;
  margin-bottom: 10px;
}

.tagline {
  color: #6c757d;
  font-size: 18px;
}

.app-main {
  flex: 1;
  padding: 40px 20px;
}

.app-footer {
  background: rgba(0, 0, 0, 0.2);
  color: white;
  text-align: center;
  padding: 20px;
}

.app-footer p {
  font-size: 14px;
}
</style>
