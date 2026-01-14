# RP Realtime - AI-Powered Conversation Practice

A comprehensive role-playing conversation practice application with real-time AI feedback, built with Vue, FastAPI, LangChain, and Azure OpenAI Realtime API.

## ✨ NEW: WebSocket Streaming Support

**Low-latency real-time conversation with sub-3-second response times!**

- 🚀 **WebSocket Mode**: Ultra-fast streaming responses via WebSocket connection
- ⚡ **LangChain Integration**: Streaming Azure OpenAI responses using LangChain
- 🔄 **Dual Mode**: Choose between Standard (full feedback) or WebSocket (speed-optimized)
- 📡 **Connection Status**: Visual indicator showing WebSocket connection state

See [WEBSOCKET_GUIDE.md](WEBSOCKET_GUIDE.md) for detailed implementation details.

## Features

### 🎯 Core Functionality
- **Push-to-Talk Interface**: Turn-based conversation with recording controls
- **Configurable Timer**: Recording up to 60 seconds (configurable)
- **Audio Processing**: PCM chunks merged into MP3, uploaded to blob storage
- **Visual Snapshots**: Front camera captures every 5 seconds
- **Real-time Feedback**: Instant AI responses with multi-dimensional analysis
- **⚡ WebSocket Streaming**: Low-latency real-time AI responses (under 3 seconds)

### 📊 Real-time Analysis
- **Ideal Answers**: Generated from hardcoded Q&A data based on scenario
- **Conversation Suggestions**: AI-powered improvement tips
- **Multi-dimensional Scoring**: Customizable dimensions (fluency, accuracy, relevance, confidence, engagement)
- **Insights & Direction**: Real-time guidance for next steps

### 🎥 Multi-modal Assessment
- **Visual Analysis**: Facial expression and body language evaluation
- **Audio Analysis**: Spoken tone, pace, and clarity assessment
- **Comprehensive Report**: Final assessment combining all dimensions

### 🔧 Customization
- **Scenario Configuration**: Define context, target audience, purpose, and language
- **Custom Prompts**: Add specific instructions for AI behavior
- **Flexible Dimensions**: Configure scoring criteria via environment variables

## Architecture

```
Frontend (Vue 3)
├── Push-to-Talk UI
├── Audio Recording (MediaRecorder API)
├── Camera Snapshots (getUserMedia API)
├── WebSocket Client (Real-time Streaming)
└── Real-time Feedback Display

Backend (FastAPI)
├── Session Management
├── WebSocket Endpoint (Low-latency Streaming)
├── LangChain Streaming Service
├── Azure OpenAI Integration
├── LangChain Prompt Templates
├── Audio Processing (PCM → MP3)
├── Blob Storage (Audio & Images)
├── Multi-dimensional Scoring
└── Assessment Report Generation
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Azure OpenAI API access
- Azure Blob Storage account

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

5. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

4. Access the application at `http://localhost:5173`

## Configuration

### Environment Variables (Backend)

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-mini-realtime
AZURE_OPENAI_API_VERSION=2024-10-01-preview

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_STORAGE_CONTAINER_AUDIO=audio-recordings
AZURE_STORAGE_CONTAINER_IMAGES=camera-snapshots

# Application Settings
MAX_RECORDING_DURATION=60
SNAPSHOT_INTERVAL=5
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Scoring Dimensions
SCORING_DIMENSIONS=fluency,accuracy,relevance,confidence,engagement
```

### Customizing Q&A Data

Edit `backend/app/core/qa_data.py` to add or modify ideal answers for different scenarios.

### Customizing Scoring Dimensions

Modify the `SCORING_DIMENSIONS` environment variable to add custom evaluation criteria.

## Usage

### 1. Configure Scenario
- Enter conversation context (e.g., "Job interview for software engineer")
- Define target audience (e.g., "Senior hiring manager")
- Specify purpose (e.g., "Interview skills practice")
- Choose target language
- Add custom instructions (optional)

### 2. Practice Conversation
- Click "Start Recording" to begin
- Speak your response (max 60 seconds)
- Type transcription for better analysis
- Click "Send" to submit
- Review AI feedback:
  - AI response
  - Ideal answer
  - Scores across dimensions
  - Suggestions for improvement
  - Insights and next directions

### 3. Camera Snapshots
- Camera captures snapshots every 5 seconds automatically
- Used for facial expression and body language analysis

### 4. Complete Session
- Click "End Conversation & Get Report"
- Review comprehensive assessment:
  - Overall performance scores
  - Visual analysis (facial expressions, body language)
  - Audio analysis (tone, pace, clarity)
  - Turn-by-turn details
  - Personalized recommendations

## API Documentation

### Start Session
```
POST /api/sessions/start
{
  "scenario": {
    "context": "string",
    "target_audience": "string",
    "purpose": "string",
    "target_language": "string",
    "custom_prompt": "string"
  }
}
```

### Submit Turn
```
POST /api/sessions/{session_id}/turns
Form Data:
- turn_number: int
- user_input: string
- audio_file: file (MP3)
```

### Submit Snapshot
```
POST /api/sessions/{session_id}/snapshots
{
  "session_id": "string",
  "image_data": "base64_string"
}
```

### Complete Session
```
POST /api/sessions/{session_id}/complete
```

## Technology Stack

### Frontend
- **Vue 3**: Reactive UI framework
- **Pinia**: State management
- **Axios**: HTTP client
- **MediaRecorder API**: Audio recording
- **getUserMedia API**: Camera access
- **Vite**: Build tool

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **LangChain**: AI application framework
- **Azure OpenAI**: GPT-mini-realtime model
- **Azure Blob Storage**: Media storage
- **Pydub**: Audio processing
- **Pillow**: Image processing

## Development

### Running Tests
```bash
# Backend (if tests exist)
cd backend
pytest

# Frontend (if tests exist)
cd frontend
npm test
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
# Use gunicorn or similar WSGI server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Troubleshooting

### Audio Recording Issues
- Ensure microphone permissions are granted
- Check browser compatibility (Chrome/Edge recommended)
- Verify HTTPS connection (required for getUserMedia)

### Camera Issues
- Grant camera permissions
- Check if another application is using the camera
- Ensure browser supports getUserMedia API

### Azure Connection Issues
- Verify API keys and endpoints
- Check network connectivity
- Ensure proper CORS configuration

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## Support

For issues or questions, please open a GitHub issue or contact the development team.
