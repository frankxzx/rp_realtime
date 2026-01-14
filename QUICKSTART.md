# Quick Start Guide

## 1. Clone the Repository
```bash
git clone https://github.com/frankxzx/rp_realtime.git
cd rp_realtime
```

## 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env file with your Azure credentials:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_STORAGE_CONNECTION_STRING

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## 3. Setup Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be running at: http://localhost:5173

## 4. Using the Application

### Step 1: Configure Scenario
1. Open http://localhost:5173 in your browser
2. Fill in the scenario configuration form:
   - **Context**: e.g., "Job interview for software engineer position"
   - **Target Audience**: e.g., "Senior hiring manager"
   - **Purpose**: e.g., "Interview skills practice"
   - **Language**: e.g., "English"
   - **Custom Instructions**: (Optional) Any additional AI instructions
3. Click "Start Practice Session"

### Step 2: Practice Conversation
1. Allow camera and microphone permissions when prompted
2. Click "Start Recording" to begin speaking
3. Speak your response (max 60 seconds)
4. Type what you're saying in the text area (for better analysis)
5. Click "Send" to submit your turn
6. Review the AI feedback:
   - AI's response
   - Ideal answer
   - Scores across dimensions
   - Improvement suggestions
   - Insights and next steps

### Step 3: Continue Practice
- Repeat the recording process for multiple turns
- The camera automatically captures snapshots every 5 seconds
- Each turn receives immediate feedback

### Step 4: Get Final Assessment
1. Click "End Conversation & Get Report"
2. Review comprehensive assessment:
   - Overall performance scores
   - Visual analysis (facial expressions, body language)
   - Audio analysis (tone, pace, clarity)
   - Turn-by-turn breakdown
   - Personalized recommendations
3. Download report or start a new session

## Troubleshooting

### Backend Issues

**Problem**: Module not found errors
```bash
# Make sure you're in the backend directory and venv is activated
pip install -r requirements.txt
```

**Problem**: Connection errors to Azure
- Verify your .env file has correct credentials
- Check Azure OpenAI endpoint is accessible
- Ensure Azure Blob Storage connection string is valid

### Frontend Issues

**Problem**: Cannot connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in backend .env file
- Verify proxy configuration in vite.config.js

**Problem**: Camera/Microphone not working
- Grant permissions in browser
- Use HTTPS (or localhost)
- Check if another app is using the devices
- Try Chrome or Edge browser

### Common Issues

**Problem**: No audio being recorded
- Check microphone permissions
- Ensure MediaRecorder API is supported (Chrome/Edge recommended)
- Try refreshing the page

**Problem**: Snapshots not capturing
- Check camera permissions
- Verify camera is working in other applications
- Look for errors in browser console

## Testing the Setup

### Test Backend
```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### Test Frontend
1. Open browser developer console (F12)
2. Check for any errors
3. Verify network requests are reaching backend
4. Test camera/microphone access

## Next Steps

- Customize Q&A data in `backend/app/core/qa_data.py`
- Adjust scoring dimensions in `.env`
- Modify scenario prompts in `backend/app/core/prompts.py`
- Customize UI styling in Vue components

## Support

For issues or questions:
1. Check the main README.md for detailed documentation
2. Review API docs at http://localhost:8000/docs
3. Open an issue on GitHub
