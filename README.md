# AI Chat Backend

A production-ready FastAPI backend for AI chat functionality. This application provides a scalable, well-structured foundation for building chat applications with AI integration.

## Features

- 🚀 **FastAPI Framework**: Modern, fast web framework for building APIs
- 🔒 **Input Validation**: Robust request validation using Pydantic models
- 🌐 **CORS Support**: Cross-origin resource sharing for frontend integration
- 📝 **Comprehensive Logging**: Structured logging for monitoring and debugging
- 🛡️ **Error Handling**: Centralized error handling with proper HTTP status codes
- 🏥 **Health Checks**: Built-in health monitoring endpoints
- 📚 **Auto Documentation**: Interactive API docs with Swagger UI
- 🔧 **Modular Structure**: Clean, extensible architecture

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat endpoint routes
│   │   └── whatsapp.py         # WhatsApp webhook routes (placeholder)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py       # AI integration service
│   │   └── whatsapp_service.py # WhatsApp Business API service (placeholder)
│   └── models/
│       ├── __init__.py
│       ├── request.py          # Request Pydantic models
│       └── response.py         # Response Pydantic models
├── frontend/
│   └── index.html              # Simple test frontend for API testing
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## API Endpoints

### Core Endpoints

- **POST** `/api/v1/chat` - Process chat messages
- **GET** `/api/v1/chat/status` - Get chat service status
- **GET** `/api/v1/whatsapp/webhook` - WhatsApp webhook verification (placeholder)
- **POST** `/api/v1/whatsapp/webhook` - WhatsApp message handler (placeholder)
- **GET** `/api/v1/whatsapp/status` - WhatsApp service status
- **GET** `/health` - Health check endpoint
- **GET** `/` - API information

### Documentation

- **GET** `/docs` - Interactive Swagger UI documentation
- **GET** `/redoc` - ReDoc documentation

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

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

4. **Run the development server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the application**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Test frontend: Open `frontend/index.html` in your browser
   - Health check: http://localhost:8000/health

## Usage Examples

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

A simple HTML test interface is provided in `frontend/index.html`. Open this file in your browser to:

1. Check backend connectivity
2. Send test messages to the chat API
3. View AI responses in real-time

The frontend automatically connects to `http://127.0.0.1:8000` and provides a clean interface for testing your API endpoints.

## Deployment

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

## AI Integration

The application is structured to easily integrate with AI services. The current implementation in `app/services/ai_service.py` is a placeholder that echoes messages.

## WhatsApp Integration (Placeholder)

The project includes placeholder structure for WhatsApp Business API integration:

- **Routes**: `app/routes/whatsapp.py` - Webhook endpoints
- **Service**: `app/services/whatsapp_service.py` - WhatsApp API integration logic
- **Endpoints**: 
  - `GET /api/v1/whatsapp/webhook` - Webhook verification
  - `POST /api/v1/whatsapp/webhook` - Message handler
  - `GET /api/v1/whatsapp/status` - Service status

### WhatsApp Integration Steps (TODO)

1. Set up WhatsApp Business API account
2. Configure webhook verify token in environment variables
3. Configure access token and phone number ID
4. Implement actual API calls in `whatsapp_service.py`
5. Test webhook endpoints with WhatsApp

The structure is ready - just need to fill in the actual WhatsApp API implementation.

### Integration Examples

**OpenAI Integration**:
```python
import openai

async def process_chat_message(message: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content
```

**Anthropic Claude Integration**:
```python
import anthropic

async def process_chat_message(message: str) -> str:
    client = anthropic.Anthropic(api_key="your-api-key")
    response = await client.completions.create(
        model="claude-3-sonnet-20240229",
        prompt=f"Human: {message}\n\nAssistant:",
        max_tokens=1000
    )
    return response.completion
```

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

- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Enable debug mode (default: False)

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

## Support

For questions or issues:
1. Check the interactive documentation at `/docs`
2. Review the logs for error details
3. Verify the health check endpoint
4. Check the project structure and configuration

## License

This project is provided as-is for educational and development purposes.