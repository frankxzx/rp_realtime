# Quick Start - WebSocket Mode

## 1. Backend Setup

```bash
cd backend

# Create .env file with your Azure credentials
cat > .env << EOF
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-10-01-preview

AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_AUDIO=audio-recordings
AZURE_STORAGE_CONTAINER_IMAGES=camera-snapshots

MAX_RECORDING_DURATION=60
SNAPSHOT_INTERVAL=5
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

SCORING_DIMENSIONS=fluency,accuracy,relevance,confidence,engagement
EOF

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

## 3. Using WebSocket Mode

1. Open browser to `http://localhost:5173`
2. Configure your scenario (context, audience, purpose, language)
3. Click "Start Session"
4. **Select "⚡ WebSocket Mode (Low Latency)"** (default)
5. Check the connection status shows "🟢 WebSocket Connected"
6. Start recording your response
7. Send your message
8. Watch the AI response stream in real-time with a blinking cursor

## 4. Performance Comparison

### WebSocket Mode:
- ✅ Response starts in 300-800ms
- ✅ Total response time: 1-3 seconds
- ✅ Real-time chunk streaming
- ℹ️ Limited feedback (focuses on speed)

### Standard Mode:
- ⏱️ Response time: 2-5 seconds
- ✅ Full feedback with scores
- ✅ Suggestions and insights
- ✅ Multi-dimensional analysis

## 5. WebSocket Protocol Flow

```
User clicks Send
    ↓
Frontend: websocketService.sendMessage(userInput, turnNumber)
    ↓
WebSocket: {"type": "user_message", "content": "...", "turn_number": 1}
    ↓
Backend: WebSocket endpoint receives message
    ↓
Backend: LangChain streams response from Azure OpenAI
    ↓
Backend: Sends chunks → {"type": "chunk", "content": "partial"}
    ↓
Frontend: Appends chunks to streamingResponse
    ↓
Frontend: Shows response with blinking cursor
    ↓
Backend: Sends complete → {"type": "complete", "content": "full response"}
    ↓
Frontend: Updates turn history and shows final response
```

## 6. Troubleshooting

### WebSocket won't connect
- Verify backend is running on port 8000
- Check browser console for errors
- Ensure session was created successfully

### No streaming chunks received
- Verify Azure OpenAI credentials in .env
- Check deployment name matches your Azure setup
- Review backend logs: `uvicorn app.main:app --log-level debug`

### Latency still high
- Check network connection
- Verify Azure OpenAI region proximity
- Consider using a closer Azure region
- Review Azure OpenAI quota and throttling

## 7. Testing Without Full Setup

You can test the LangChain streaming service independently:

```bash
cd backend
python tests/test_websocket.py
```

This requires valid Azure credentials but doesn't need the full web stack.

## 8. Production Deployment

For production:
1. Use `wss://` (WebSocket Secure) instead of `ws://`
2. Add authentication to WebSocket endpoint
3. Implement rate limiting per session
4. Enable WebSocket compression
5. Use a reverse proxy (nginx) for SSL termination
6. Monitor WebSocket connection metrics

## 9. Next Steps

- Test with real audio recordings
- Implement additional feedback via separate API calls
- Add audio streaming over WebSocket
- Implement typing indicators
- Add multi-user support
