# LLM Provider Switching Guide

This guide explains how to use multiple LLM providers (Gemini, Groq) with the QuickShip agent.

## Supported Providers

### 1. Google Gemini
- **Models**: `gemini-2.5-flash-lite`, `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-1.0-pro`
- **API Key**: `GOOGLE_API_KEY`
- **Get API Key**: https://makersuite.google.com/app/apikey

### 2. Groq
- **Models**: `llama-3.1-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, `gemma2-9b-it`, `llama3-70b-8192`, `llama3-8b-8192`
- **API Key**: `GROQ_API_KEY`
- **Get API Key**: https://console.groq.com/

## Configuration

### Environment Variables (.env)

```env
# LLM Provider Selection
LLM_PROVIDER=gemini  # Options: gemini, groq

# API Keys
GOOGLE_API_KEY=your-google-api-key-here
GROQ_API_KEY=your-groq-api-key-here

# Model Configuration
AGENT_MODEL=gemini-2.5-flash-lite  # Or any supported model
AGENT_TEMPERATURE=0.3
```

## Usage

### 1. Using Default Provider (from .env)

```python
from quickship_agent.agent_service import AgentService

# Creates agent with provider from LLM_PROVIDER env var
agent = AgentService()

# Chat with the agent
response = agent.chat(
    session_id="user_123",
    message="Track shipment QS250001"
)
```

### 2. Specifying Provider at Initialization

```python
from quickship_agent.agent_service import AgentService

# Use Gemini
agent = AgentService(llm_provider="gemini", model="gemini-1.5-pro")

# Use Groq
agent = AgentService(llm_provider="groq", model="llama-3.1-70b-versatile")
```

### 3. Switching Providers Dynamically

```python
from quickship_agent.agent_service import AgentService

# Start with Gemini
agent = AgentService(llm_provider="gemini")

# Chat with Gemini
response = agent.chat("session_1", "Hello!")

# Switch to Groq
switch_result = agent.switch_llm_provider(
    provider="groq",
    model="llama-3.1-70b-versatile"
)

if switch_result["success"]:
    # Now using Groq
    response = agent.chat("session_1", "What are your rates?")
```

### 4. Getting Current Provider Info

```python
from quickship_agent.agent_service import AgentService

agent = AgentService()

# Get current LLM information
llm_info = agent.get_current_llm_info()

print(f"Provider: {llm_info['provider']}")
print(f"Model: {llm_info['model']}")
print(f"Temperature: {llm_info['temperature']}")
print(f"Available providers: {llm_info['available_providers']}")
```

### 5. Checking Available Providers

```python
from quickship_agent.llm_factory import LLMFactory

# Get all available providers and their status
providers = LLMFactory.get_available_providers()

for provider, info in providers.items():
    if info["available"]:
        print(f"{provider}: Available")
        print(f"  Models: {info['models']}")
    else:
        print(f"{provider}: Not configured (missing API key)")
```

## API Endpoints

### Get Current LLM Provider
```http
GET /api/v1/admin/agent/llm-provider
Authorization: Bearer <token>
```

**Response:**
```json
{
  "provider": "gemini",
  "model": "gemini-2.5-flash-lite",
  "temperature": 0.3,
  "available_providers": {
    "gemini": {
      "available": true,
      "models": ["gemini-2.5-flash-lite", "gemini-1.5-pro", ...]
    },
    "groq": {
      "available": true,
      "models": ["llama-3.1-70b-versatile", ...]
    }
  }
}
```

### Switch LLM Provider
```http
POST /api/v1/admin/agent/llm-provider/switch
Authorization: Bearer <token>
Content-Type: application/json

{
  "provider": "groq",
  "model": "llama-3.1-70b-versatile"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully switched to groq with model llama-3.1-70b-versatile",
  "previous_provider": "gemini",
  "previous_model": "gemini-2.5-flash-lite",
  "current_provider": "groq",
  "current_model": "llama-3.1-70b-versatile"
}
```

### Get Available Providers
```http
GET /api/v1/admin/agent/llm-provider/available
Authorization: Bearer <token>
```

## Testing

### Run Demo Script
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run demo
python scripts/demo_llm_switching.py
```

### Run Full Test Suite
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run tests
python scripts/test_llm_providers.py
```

## Model Recommendations

### For Speed (Low Latency)
- **Gemini**: `gemini-2.5-flash-lite`
- **Groq**: `llama-3.1-8b-instant`

### For Quality (Better Responses)
- **Gemini**: `gemini-1.5-pro`
- **Groq**: `llama-3.1-70b-versatile`

### For Balance
- **Gemini**: `gemini-1.5-flash`
- **Groq**: `mixtral-8x7b-32768`

## Troubleshooting

### "Invalid API Key" Error
- Check that the API key is correctly set in `.env`
- Verify the API key is valid by testing it directly with the provider
- Make sure there are no extra spaces or quotes in the `.env` file

### "Provider not available" Error
- Ensure the API key environment variable is set
- Check that the provider name is correct (lowercase: "gemini" or "groq")
- Verify the `.env` file is in the project root

### Model Not Found
- Check the model name matches exactly (case-sensitive)
- Refer to the supported models list above
- Some models may require special access or billing setup

## Cost Considerations

### Gemini Pricing
- Free tier available with rate limits
- Pay-as-you-go pricing for higher usage
- Check: https://ai.google.dev/pricing

### Groq Pricing
- Free tier with generous limits
- Very fast inference speeds
- Check: https://console.groq.com/pricing

## Best Practices

1. **Use environment variables** for API keys (never hardcode)
2. **Set appropriate temperature** (0.0-0.3 for factual, 0.7-1.0 for creative)
3. **Monitor usage** to stay within free tier limits
4. **Test both providers** to find the best fit for your use case
5. **Implement fallback** logic in case one provider is unavailable
6. **Cache responses** when possible to reduce API calls

## Adding New Providers

To add a new LLM provider:

1. Install the LangChain integration:
   ```bash
   pip install langchain-<provider>
   ```

2. Update `quickship_agent/config.py`:
   ```python
   PROVIDER_API_KEY = os.getenv("PROVIDER_API_KEY")
   PROVIDER_MODELS = ["model-1", "model-2"]
   ```

3. Update `quickship_agent/llm_factory.py`:
   ```python
   @staticmethod
   def _create_provider_llm(model: str, temperature: float):
       if not PROVIDER_API_KEY:
           raise ValueError("PROVIDER_API_KEY not found")
       return ChatProvider(
           api_key=PROVIDER_API_KEY,
           model=model,
           temperature=temperature
       )
   ```

4. Add to `create_llm()` method:
   ```python
   elif provider == "provider":
       return LLMFactory._create_provider_llm(model, temperature)
   ```
