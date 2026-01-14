# Architecture Documentation

## System Overview

The RP Realtime application is a full-stack web application for AI-powered conversation practice with multi-modal feedback.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend (Vue 3)                        │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────┐ │
│  │  Scenario      │  │  Conversation  │  │   Assessment      │ │
│  │  Configuration │→ │  Practice      │→ │   Report          │ │
│  └────────────────┘  └────────────────┘  └───────────────────┘ │
│         ↓                    ↓                      ↑            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Media Services (Audio Recording + Camera Capture)       │  │
│  └──────────────────────────────────────────────────────────┘  │
│         ↓                                                        │
└─────────┼────────────────────────────────────────────────────────┘
          │
          │ HTTP/REST API
          │
┌─────────┼────────────────────────────────────────────────────────┐
│         ↓                  Backend (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  API Endpoints (sessions.py)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│         ↓                                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Session Manager (Orchestration)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│         ↓                                                        │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │  Realtime    │   Scoring    │    Audio     │    Blob     │  │
│  │  API Service │   Service    │   Processor  │   Storage   │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
│         ↓                                           ↓            │
└─────────┼───────────────────────────────────────────┼────────────┘
          │                                           │
          ↓                                           ↓
┌─────────────────────────┐              ┌─────────────────────┐
│   Azure OpenAI API      │              │  Azure Blob Storage │
│   (GPT-mini-realtime)   │              │  (Audio + Images)   │
└─────────────────────────┘              └─────────────────────┘
```

## Component Details

### Frontend Components

#### 1. ScenarioConfig.vue
- **Purpose**: Scenario configuration form
- **Features**:
  - Context input (scenario description)
  - Target audience definition
  - Purpose specification
  - Language selection
  - Custom prompt (optional)
- **Output**: Creates new session via API

#### 2. ConversationPractice.vue
- **Purpose**: Main conversation interface
- **Features**:
  - Push-to-talk controls (Start Recording / Send)
  - Configurable countdown timer (max 60s)
  - Video preview with camera feed
  - Real-time feedback display
  - Turn-by-turn conversation flow
- **Services Used**:
  - AudioRecorder (media.js)
  - CameraCapture (media.js)
  - Session Store (Pinia)

#### 3. AssessmentReport.vue
- **Purpose**: Final assessment display
- **Features**:
  - Overall performance scores
  - Visual analysis results
  - Audio analysis results
  - Turn-by-turn breakdown
  - Recommendations
  - Report download

### Frontend Services

#### media.js
- **AudioRecorder Class**:
  - Uses MediaRecorder API
  - Captures audio chunks
  - Converts to MP3 blob
  
- **CameraCapture Class**:
  - Uses getUserMedia API
  - Captures video stream
  - Takes snapshots at intervals
  - Converts to base64 JPEG

#### api.js
- HTTP client wrapper using Axios
- Endpoints:
  - `startSession()`: Initialize conversation
  - `submitTurn()`: Send audio + transcript
  - `submitSnapshot()`: Upload camera snapshot
  - `completeSession()`: Generate final report

#### session.js (Pinia Store)
- State management:
  - Session ID
  - Scenario configuration
  - Turns array
  - Recording state
  - Assessment report

### Backend Services

#### 1. Session Manager (session_manager.py)
- **Core orchestration service**
- **Methods**:
  - `create_session()`: Initialize new conversation
  - `process_turn()`: Handle complete turn workflow
  - `add_snapshot()`: Store camera snapshots
  - `generate_assessment_report()`: Create final report

#### 2. Realtime API Service (realtime_api.py)
- **Azure OpenAI integration**
- **Methods**:
  - `generate_response()`: AI conversation response
  - `generate_suggestions()`: Improvement tips
  - `generate_insights()`: Performance insights
  - `generate_direction()`: Next steps guidance
  - `analyze_visual()`: Facial/body language analysis

#### 3. Scoring Service (scoring.py)
- **Multi-dimensional scoring**
- **Dimensions** (configurable):
  - Fluency
  - Accuracy
  - Relevance
  - Confidence
  - Engagement
- **Methods**:
  - `score_response()`: Score single turn
  - `calculate_overall_scores()`: Aggregate scores

#### 4. Audio Processor (audio_processor.py)
- **Audio manipulation**
- **Methods**:
  - `pcm_to_mp3()`: Convert format
  - `base64_to_pcm()`: Decode audio
  - `analyze_audio_tone()`: Extract tone, pace, clarity

#### 5. Blob Storage (blob_storage.py)
- **Azure Blob Storage interface**
- **Methods**:
  - `upload_audio()`: Store MP3 files
  - `upload_image()`: Store JPEG snapshots
  - `get_session_snapshots()`: Retrieve session images

### Core Modules

#### config.py
- Environment variable management
- Settings class with validation
- Configuration properties

#### qa_data.py
- Hardcoded Q&A database
- Categories:
  - Job interviews
  - Customer service
  - Sales pitches
  - Presentations
- `get_ideal_answer()`: Match user input to ideal response

#### prompts.py
- LangChain prompt templates
- Templates for:
  - Scenario context
  - Feedback generation
  - Suggestions
  - Insights
  - Directions
  - Visual analysis
  - Assessment summary

## Data Flow

### 1. Session Creation Flow
```
User → ScenarioConfig → POST /api/sessions/start → SessionManager.create_session()
  → Returns: session_id, max_recording_duration, snapshot_interval
```

### 2. Turn Submission Flow
```
User speaks → AudioRecorder.startRecording()
  → Timer countdown (max 60s)
  → User clicks Send → AudioRecorder.stopRecording()
  → POST /api/sessions/{id}/turns (FormData: audio_file, user_input, turn_number)
  → SessionManager.process_turn():
      1. Upload audio to Blob Storage
      2. Generate AI response (RealtimeAPIService)
      3. Get ideal answer (qa_data)
      4. Generate suggestions (RealtimeAPIService)
      5. Generate insights (RealtimeAPIService)
      6. Generate direction (RealtimeAPIService)
      7. Score response (ScoringService)
      8. Return TurnFeedback
  → Display feedback in UI
```

### 3. Snapshot Flow
```
Every 5 seconds during recording:
  → CameraCapture.captureSnapshot()
  → POST /api/sessions/{id}/snapshots (base64 image)
  → BlobStorage.upload_image()
  → Store URL in session
```

### 4. Assessment Report Flow
```
User clicks "End Conversation"
  → POST /api/sessions/{id}/complete
  → SessionManager.generate_assessment_report():
      1. Analyze visual data (RealtimeAPIService.analyze_visual)
      2. Aggregate audio analysis
      3. Calculate overall scores (ScoringService)
      4. Generate summary
      5. Generate recommendations
      6. Create AssessmentReport
  → Display comprehensive report
```

## Key Design Decisions

### 1. Push-to-Talk Pattern
- **Reason**: Ensures clear turn boundaries
- **Implementation**: Start Recording → Speak → Send button
- **Benefits**: Better audio segmentation, clear conversation structure

### 2. In-Memory Session Storage
- **Current**: Dictionary in SessionManager
- **Reason**: Simplicity for MVP
- **Future**: Can be replaced with database (Redis, PostgreSQL)

### 3. Hardcoded Q&A Data
- **Current**: Python dictionary with scenarios
- **Reason**: Fast lookup, simple implementation
- **Future**: Can use vector database with embeddings

### 4. Simplified Audio/Visual Analysis
- **Current**: Basic heuristics and placeholders
- **Reason**: MVP demonstration
- **Future**: Integration with specialized ML models

### 5. Configurable Dimensions
- **Implementation**: Environment variable with comma-separated values
- **Reason**: Easy customization without code changes
- **Usage**: Different use cases need different evaluation criteria

## Security Considerations

### 1. Authentication
- **Current**: Not implemented
- **Recommendation**: Add JWT-based auth for production

### 2. Blob Storage Access
- **Current**: Connection string in environment
- **Recommendation**: Use managed identities or SAS tokens

### 3. Input Validation
- **Current**: Pydantic models
- **Status**: Good foundation
- **Enhancement**: Add rate limiting, file size limits

### 4. CORS Configuration
- **Current**: Configurable via environment
- **Status**: Properly restricted
- **Production**: Lock down to specific origins

## Scalability Considerations

### 1. Session Storage
- Current: In-memory
- Scale: Add Redis or database
- Benefit: Distributed sessions, persistence

### 2. Audio Processing
- Current: Synchronous in request
- Scale: Add task queue (Celery, RQ)
- Benefit: Handle large files, better performance

### 3. Blob Storage
- Current: Azure Blob Storage
- Scale: CDN for audio/image delivery
- Benefit: Faster access, reduced costs

### 4. API Rate Limiting
- Current: None
- Scale: Add rate limiting middleware
- Benefit: Prevent abuse, control costs

## Testing Strategy

### Unit Tests
- Services: RealtimeAPI, Scoring, AudioProcessor
- Utils: QA data matching, prompt templates

### Integration Tests
- API endpoints with mock services
- Session workflow end-to-end

### E2E Tests
- Browser automation (Playwright/Cypress)
- Full user journey simulation

## Deployment

### Backend
- Container: Docker
- Platform: Azure App Service, AWS ECS, or Kubernetes
- Environment: Production .env configuration

### Frontend
- Build: `npm run build`
- Deploy: Azure Static Web Apps, Netlify, Vercel
- CDN: CloudFront or Azure CDN

### Dependencies
- Azure OpenAI: Ensure deployment exists
- Azure Blob Storage: Create containers
- Monitoring: Application Insights or similar

## Future Enhancements

1. **Real-time Streaming**: Use WebSockets for live audio streaming
2. **Speech Recognition**: Automatic transcription of user input
3. **Multi-language Support**: Detect and support multiple languages
4. **Advanced Analytics**: ML models for better scoring
5. **User Profiles**: Save progress, history, preferences
6. **Collaborative Practice**: Multiple users in same session
7. **Custom Scenarios**: User-created scenario templates
8. **Mobile App**: Native iOS/Android applications
