# Quick Start: Public Chat API

## 🚀 Get Started in 5 Minutes

### Step 1: Database Migration (Already Done ✅)

The migration has been applied successfully. You now have:
- `public_chat_configs` table
- `public_chat_sessions` table
- `public_chat_messages` table
- `public_chat_feedback` table

### Step 2: Start the Server

```bash
python run_app.py
```

The server will start on `http://localhost:8000`

### Step 3: Configure Public Chat

#### Option A: Using curl

```bash
# 1. Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Get available knowledge bases
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/public-chat/available-kbs

# 3. Enable public chat (replace KB_ID with your actual KB ID)
curl -X PUT http://localhost:8000/api/v1/admin/public-chat/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "allowed_kbs": ["KB_ID"],
    "welcome_message": "Hi! How can I help you today?",
    "suggested_questions": [
      "What services do you offer?",
      "How can I contact support?",
      "What are your business hours?"
    ],
    "branding": {
      "primary_color": "#0066CC",
      "company_name": "Your Company"
    },
    "rate_limit": {
      "queries_per_minute": 10,
      "max_messages_per_session": 50
    },
    "features": {
      "show_sources": true,
      "allow_feedback": true,
      "show_suggested_questions": true
    }
  }'
```

#### Option B: Using Python Test Script

```bash
# Update credentials in test_public_chat.py first
python test_public_chat.py
```

### Step 4: Test Public Endpoints

#### Get Configuration
```bash
curl http://localhost:8000/api/v1/public-chat/config
```

Expected response:
```json
{
  "enabled": true,
  "welcome_message": "Hi! How can I help you today?",
  "suggested_questions": [...],
  "branding": {...},
  "rate_limit": {...},
  "features": {...}
}
```

#### Send a Query
```bash
curl -X POST http://localhost:8000/api/v1/public-chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "query": "What services do you offer?",
    "conversation_history": []
  }'
```

Expected response:
```json
{
  "answer": "Based on our documents...",
  "sources": [...],
  "session_id": "test-session-123",
  "timestamp": "2024-11-24T10:30:00Z"
}
```

#### Submit Feedback
```bash
curl -X POST http://localhost:8000/api/v1/public-chat/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "message_id": "msg-abc123",
    "feedback_type": "positive",
    "comment": "Very helpful!"
  }'
```

### Step 5: View API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Look for:
- **"14. Public Chat"** - Public endpoints
- **"Public Chat Admin"** - Admin endpoints

## 📊 View Analytics

```bash
# Get analytics for last 30 days
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/public-chat/analytics?days=30"
```

## 🔍 View Session Details

```bash
# Get detailed session information
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/admin/public-chat/sessions/test-session-123"
```

## 🎨 Frontend Integration

### React Example

```javascript
// 1. Get configuration
const config = await fetch('http://localhost:8000/api/v1/public-chat/config')
  .then(r => r.json());

// 2. Send query
const response = await fetch('http://localhost:8000/api/v1/public-chat/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionId,
    query: userMessage,
    conversation_history: []
  })
}).then(r => r.json());

// 3. Submit feedback
await fetch('http://localhost:8000/api/v1/public-chat/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: sessionId,
    message_id: response.message_id,
    feedback_type: 'positive'
  })
});
```

## 🛠️ Troubleshooting

### "Public chat is currently disabled"
```bash
# Check config
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/public-chat/config

# Enable it
curl -X PUT http://localhost:8000/api/v1/admin/public-chat/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, ...}'
```

### "No knowledge bases configured"
```bash
# List available KBs
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/admin/public-chat/available-kbs

# Add KB to config
curl -X PUT http://localhost:8000/api/v1/admin/public-chat/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"allowed_kbs": ["your-kb-id"], ...}'
```

### Rate Limit Exceeded (429)
- Wait 60 seconds before retrying
- Or increase rate limits in config

## 📝 Configuration Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | false | Enable/disable public chat |
| `allowed_kbs` | array | [] | List of KB IDs to use |
| `welcome_message` | string | "Hi! How can I help you today?" | Greeting message |
| `suggested_questions` | array | [] | Up to 10 pre-defined questions |
| `branding.logo` | string | null | Logo URL |
| `branding.primary_color` | string | "#0066CC" | Primary color (hex) |
| `branding.company_name` | string | - | Company name |
| `rate_limit.queries_per_minute` | number | 10 | Max queries per minute |
| `rate_limit.max_messages_per_session` | number | 50 | Max messages per session |
| `features.show_sources` | boolean | true | Show source documents |
| `features.allow_feedback` | boolean | true | Allow user feedback |
| `features.show_suggested_questions` | boolean | true | Show suggested questions |

## 🔐 Security Features

✅ Rate limiting per session  
✅ Session expiry (24 hours)  
✅ Input validation  
✅ Admin-only configuration  
✅ Audit logging  
✅ CORS enabled  

## 📚 Next Steps

1. **Frontend**: Connect your UI to the API
2. **Customize**: Update branding and messages
3. **Monitor**: Check analytics regularly
4. **Optimize**: Adjust rate limits based on usage

## 🆘 Need Help?

- Check `PUBLIC_CHAT_API_COMPLETE.md` for detailed documentation
- View API docs at http://localhost:8000/docs
- Run tests: `python test_public_chat.py`

---

**Ready to go!** 🎉
