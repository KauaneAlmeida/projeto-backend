# AI Chat Backend

A production-ready FastAPI backend for AI chat functionality with WhatsApp integration via Evolution API. This application provides a scalable, well-structured foundation for building chat applications with AI integration and seamless WhatsApp messaging capabilities.

## Features

- 🚀 **FastAPI Framework**: Modern, fast web framework for building APIs
- 🔒 **Input Validation**: Robust request validation using Pydantic models
- 🌐 **CORS Support**: Cross-origin resource sharing for frontend integration
- 📝 **Comprehensive Logging**: Structured logging for monitoring and debugging
- 🛡️ **Error Handling**: Centralized error handling with proper HTTP status codes
- 🏥 **Health Checks**: Built-in health monitoring endpoints
- 📚 **Auto Documentation**: Interactive API docs with Swagger UI
- 🔧 **Modular Structure**: Clean, extensible architecture
- 📱 **WhatsApp Integration**: Full WhatsApp messaging via Evolution API
- 🤖 **AI Conversation Flow**: Guided intake process with Firebase storage
- 🔄 **Seamless Handoff**: Bot-to-WhatsApp conversation transition
- 🐳 **Docker Support**: Complete containerized setup with Evolution API

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat endpoint routes
│   │   ├── whatsapp.py         # WhatsApp webhook routes (Evolution API)
│   │   ├── conversation.py     # Guided conversation flow routes
│   │   └── evolution.py        # Direct Evolution API management routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # AI integration service
│   │   ├── ai_chain.py         # LangChain integration with Gemini
│   │   ├── gemini_service.py   # Direct Gemini API service
│   │   ├── whatsapp_service.py # WhatsApp messaging via Evolution API
│   │   ├── evolution_service.py # Evolution API integration
│   │   ├── firebase_service.py # Firebase/Firestore integration
│   │   └── conversation_service.py # Guided conversation management
│   └── models/
│       ├── __init__.py
│       ├── request.py          # Request Pydantic models
│       └── response.py         # Response Pydantic models
├── docker-compose.yml          # Evolution API Docker setup
├── frontend/
│   └── index.html              # Enhanced test frontend with WhatsApp controls
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## API Endpoints

### Core Endpoints

- **POST** `/api/v1/chat` - Process chat messages
- **GET** `/api/v1/chat/status` - Get chat service status

### Conversation Flow Endpoints

- **POST** `/api/v1/conversation/start` - Start guided intake conversation
- **POST** `/api/v1/conversation/respond` - Process user response in flow
- **GET** `/api/v1/conversation/status/{session_id}` - Get conversation status
- **GET** `/api/v1/conversation/flow` - Get current flow configuration
- **GET** `/api/v1/conversation/service-status` - Get conversation service status

### WhatsApp Integration Endpoints

- **GET** `/api/v1/whatsapp/webhook` - Evolution API webhook verification
- **POST** `/api/v1/whatsapp/webhook` - Evolution API message handler
- **POST** `/api/v1/whatsapp/initialize` - Initialize WhatsApp instance
- **GET** `/api/v1/whatsapp/qr` - Get QR code for authentication
- **GET** `/api/v1/whatsapp/instance-status` - Get instance connection status
- **POST** `/api/v1/whatsapp/send-message` - Send WhatsApp message
- **GET** `/api/v1/whatsapp/status` - WhatsApp service status

### Evolution API Management Endpoints

- **POST** `/api/v1/evolution/initialize` - Initialize Evolution API instance
- **GET** `/api/v1/evolution/status` - Get Evolution API service status
- **GET** `/api/v1/evolution/qr` - Get QR code for WhatsApp authentication
- **GET** `/api/v1/evolution/instance-status` - Get instance connection status
- **POST** `/api/v1/evolution/create-instance` - Create new WhatsApp instance
- **POST** `/api/v1/evolution/send-test-message` - Send test message

### System Endpoints

- **GET** `/health` - Health check endpoint
- **GET** `/` - API information

### Documentation

- **GET** `/docs` - Interactive Swagger UI documentation
- **GET** `/redoc` - ReDoc documentation

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Docker and Docker Compose (for Evolution API)
- Firebase project (for conversation flow and lead storage)
- Google Gemini API key (for AI responses)

### Local Development

1. **Clone or download the project**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

5. **Start Evolution API with Docker**:
   ```bash
   docker-compose up -d
   ```

6. **Run the development server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Access the application**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Test frontend: Open `frontend/index.html` in your browser
   - Health check: http://localhost:8000/health
   - Evolution API: http://localhost:8080
   - Redis Commander: http://localhost:8081

## WhatsApp Setup

### Evolution API Configuration

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Initialize WhatsApp instance**:
   - Open the test frontend: `frontend/index.html`
   - Click "WhatsApp Setup" to show the WhatsApp section
   - Click "Initialize WhatsApp" to create the instance
   - Scan the QR code with WhatsApp (Settings → Linked Devices → Link a Device)

3. **Test the integration**:
   - Once connected, click "Send Test Message"
   - Check your WhatsApp for the test message

### Environment Variables

Configure these in your `.env` file:

```bash
# Evolution API Configuration
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=B6D711FCDE4D4FD5936544120E713976
EVOLUTION_INSTANCE_NAME=lawfirm_bot
EVOLUTION_WEBHOOK_URL=http://host.docker.internal:8000/api/v1/whatsapp/webhook

# WhatsApp Configuration
WHATSAPP_TEST_NUMBER=5511918368812
WHATSAPP_BUSINESS_NAME=Law Firm Assistant

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Firebase Configuration
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_CLIENT_EMAIL=your_client_email@your_project.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
```

## Usage Examples

### Guided Conversation Flow

Start a guided intake conversation:

```bash
curl -X POST "http://localhost:8000/api/v1/conversation/start" \
     -H "Content-Type: application/json"
```

Response user input:
```bash
curl -X POST "http://localhost:8000/api/v1/conversation/respond" \
     -H "Content-Type: application/json" \
     -d '{"message": "John Smith", "session_id": "session_abc123"}'
```

### Chat Endpoint

Send a POST request to `/api/v1/chat`:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, how can you help me?"}'
```

Response:
```json
{
  "reply": "AI Response: Hello, how can you help me?",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "model_used": "echo_placeholder",
  "confidence": 1.0
}
```

### WhatsApp Integration

Send a WhatsApp message:

```bash
curl -X POST "http://localhost:8000/api/v1/whatsapp/send-message" \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "5511918368812", "message": "Hello from the AI assistant!"}'
```

Get WhatsApp QR code:

```bash
curl -X GET "http://localhost:8000/api/v1/whatsapp/qr"
```

### Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

Response:
```json
{
  "status": "healthy",
  "message": "FastAPI backend is running successfully"
}
```

### Test Frontend

An enhanced HTML test interface is provided in `frontend/index.html`. Open this file in your browser to:

1. Check backend connectivity
2. Send test messages to the chat API
3. View AI responses in real-time
4. Initialize WhatsApp integration
5. Scan QR codes for WhatsApp authentication
6. Send test WhatsApp messages
7. Monitor WhatsApp connection status

The frontend automatically connects to `http://127.0.0.1:8000` and provides a comprehensive interface for testing all API endpoints and WhatsApp functionality.

## Deployment

### Docker Deployment (Recommended)

The project includes a complete Docker setup for Evolution API:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services included:
- **Evolution API**: WhatsApp integration (port 8080)
- **PostgreSQL**: Database for Evolution API (port 5432)
- **Redis**: Caching and session management (port 6379)
- **Redis Commander**: Redis management interface (port 8081)

### Render Deployment

1. **Create a new Web Service** on [Render](https://render.com)

2. **Connect your repository**

3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

4. **Set environment variables** (if needed):
   - `PYTHON_VERSION`: `3.11.0` (or your preferred version)

### Railway Deployment

1. **Create a new project** on [Railway](https://railway.app)

2. **Connect your repository**

3. **Railway will auto-detect** the Python application

4. **Set the start command** (if not auto-detected):
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t fastapi-backend .
docker run -p 8000:8000 fastapi-backend
```

**Note**: For production deployment, you'll need to deploy both the FastAPI backend and the Evolution API stack. Consider using Docker Swarm or Kubernetes for orchestration.

## AI Integration

The application includes comprehensive AI integration:

### Google Gemini Integration

- **Direct API calls**: Simple request/response via `gemini_service.py`
- **LangChain integration**: Conversation memory and system prompts via `ai_chain.py`
- **Automatic fallback**: Falls back to direct API if LangChain fails

### Conversation Flow

- **Guided intake**: Step-by-step questions for lead qualification
- **Firebase storage**: Conversation state and lead data persistence
- **AI transition**: Seamless handoff from guided flow to AI chat
- **WhatsApp integration**: Continue conversations via WhatsApp

## WhatsApp Integration

The project includes full WhatsApp integration via Evolution API:

- **Routes**: `app/routes/whatsapp.py` - Webhook and messaging endpoints
- **Service**: `app/services/whatsapp_service.py` - WhatsApp messaging logic
- **Evolution Service**: `app/services/evolution_service.py` - Evolution API integration
- **Endpoints**: 
  - `GET /api/v1/whatsapp/webhook` - Webhook verification
  - `POST /api/v1/whatsapp/webhook` - Message handler
  - `POST /api/v1/whatsapp/initialize` - Instance initialization
  - `GET /api/v1/whatsapp/qr` - QR code for authentication
  - `GET /api/v1/whatsapp/status` - Service status

### WhatsApp Integration Features

1. ✅ **Instance Management**: Create and manage WhatsApp instances
2. ✅ **QR Code Authentication**: Generate and display QR codes for linking
3. ✅ **Message Sending**: Send messages to WhatsApp users
4. ✅ **Webhook Processing**: Receive and process incoming messages
5. ✅ **AI Integration**: Automatic AI responses to WhatsApp messages
6. ✅ **Status Monitoring**: Real-time connection status monitoring
7. ✅ **Error Handling**: Comprehensive error handling and logging

### Message Flow

1. **User sends WhatsApp message** → Evolution API receives it
2. **Evolution API sends webhook** → FastAPI processes the message
3. **FastAPI processes with AI** → Gemini generates response
4. **FastAPI sends response** → Evolution API delivers to WhatsApp
5. **User receives AI response** → Conversation continues

### Integration Examples

The application demonstrates a complete law firm pre-sales assistant workflow:

1. **Web Chat**: User starts conversation on website
2. **Guided Intake**: Bot asks structured questions (name, legal area, situation)
3. **Lead Storage**: Information saved to Firebase
4. **AI Transition**: Bot switches to AI-powered conversation
5. **WhatsApp Handoff**: User invited to continue on WhatsApp
6. **Seamless Experience**: Conversation continues with full context

## Development

### Testing

Install development dependencies:
```bash
pip install pytest pytest-asyncio httpx
```

Run tests:
```bash
pytest
```

### Code Style

The codebase follows Python best practices:
- Type hints for better code documentation
- Comprehensive docstrings
- Modular architecture
- Error handling and logging
- Input validation

### Adding New Features

1. **Models**: Add new Pydantic models in `app/models/`
2. **Routes**: Create new route files in `app/routes/`
3. **Services**: Add business logic in `app/services/`
4. **Register routes**: Include new routers in `app/main.py`

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key for AI responses
- `FIREBASE_PROJECT_ID`: Firebase project identifier
- `FIREBASE_CLIENT_EMAIL`: Firebase service account email
- `FIREBASE_PRIVATE_KEY`: Firebase service account private key
- `EVOLUTION_API_URL`: Evolution API base URL (default: http://localhost:8080)
- `EVOLUTION_API_KEY`: Evolution API authentication key
- `EVOLUTION_INSTANCE_NAME`: WhatsApp instance name
- `WHATSAPP_TEST_NUMBER`: Test phone number for WhatsApp
- `AI_SYSTEM_PROMPT`: Custom system prompt for AI responses

### CORS Configuration

Update the CORS settings in `app/main.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Monitoring & Logging

The application includes comprehensive logging:
- Request/response logging
- Error tracking
- Service status monitoring
- WhatsApp message logging
- Evolution API integration logging

Logs are structured and can be easily integrated with monitoring services like:
- DataDog
- New Relic
- Sentry
- CloudWatch

## Security Considerations

- Input validation with Pydantic
- CORS configuration
- Error message sanitization
- Request size limits
- Rate limiting (implement as needed)
- WhatsApp webhook verification
- Evolution API authentication
- Firebase security rules

## Troubleshooting

### Common Issues

1. **Evolution API not starting**:
   ```bash
   docker-compose logs evolution-api
   docker-compose restart evolution-api
   ```

2. **QR code not appearing**:
   - Check if instance is already connected
   - Try recreating the instance
   - Verify Evolution API is running

3. **WhatsApp messages not being received**:
   - Check webhook URL configuration
   - Verify instance connection status
   - Check Evolution API logs

4. **Firebase connection issues**:
   - Verify service account credentials
   - Check Firebase project configuration
   - Ensure Firestore is enabled

## Support

For questions or issues:
1. Check the interactive documentation at `/docs`
2. Review the logs for error details
3. Verify the health check endpoint
4. Check the project structure and configuration
5. Test WhatsApp integration via the frontend interface
6. Monitor Evolution API logs: `docker-compose logs -f evolution-api`

## License

This project is provided as-is for educational and development purposes.