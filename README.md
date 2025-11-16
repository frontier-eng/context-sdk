# Context API Service

A FastAPI service for managing context retrieval and trace storage using Gemini File Search and Supabase.

## Architecture

- **FastAPI** backend deployed on Railway
- **Supabase**: users, API keys, trace metadata
- **Gemini File Search**: trace storage (global store with user_id namespacing)
- **Flow**: SDK → API (retrieve context) → SDK calls LLM → SDK → API (store trace)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Supabase

1. Create a Supabase project
2. Run the SQL schema from `supabase_schema.sql` in the Supabase SQL editor
3. Get your Supabase URL and anon key

### 3. Get Gemini API Key

1. Get a Gemini API key from [Google AI Studio](https://ai.google.dev/)
2. Enable File Search API access

### 4. Configure Environment Variables

Create a `.env` file:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Run Locally

```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

**POST** `/api/v1/auth/create-key`
- Creates a new API key for a user
- Request: `{"email": "user@example.com"}`
- Response: `{"api_key": "ctx_...", "user_id": "..."}`

### Context Retrieval

**POST** `/api/v1/context/retrieve`
- Retrieves relevant context for a prompt
- Headers: `X-API-Key: your-api-key`
- Request: `{"prompt": "...", "system_prompt": "...", "provider": "openai", "model": "gpt-4"}`
- Response: `{"enhanced_context": "...", "relevant_traces": [...], "suggestions": {...}}`

### Trace Storage

**POST** `/api/v1/traces/store`
- Stores a trace after an LLM call
- Headers: `X-API-Key: your-api-key`
- Request: `{"input": {...}, "output": {...}, "metadata": {...}}`
- Response: `{"trace_id": "...", "stored": true}`

## Deployment to Railway

1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Add environment variables in Railway dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `GEMINI_API_KEY`
4. Deploy!

The `Procfile` and `railway.toml` are already configured.

## Testing

Run tests with:

```bash
pytest src/tests/
```

## Usage Example

```python
import requests

# Create API key
response = requests.post("https://your-api.railway.app/api/v1/auth/create-key", 
    json={"email": "user@example.com"})
api_key = response.json()["api_key"]

# Retrieve context
response = requests.post(
    "https://your-api.railway.app/api/v1/context/retrieve",
    headers={"X-API-Key": api_key},
    json={
        "prompt": "Write a story",
        "provider": "openai",
        "model": "gpt-4"
    }
)
context = response.json()

# Store trace after LLM call
response = requests.post(
    "https://your-api.railway.app/api/v1/traces/store",
    headers={"X-API-Key": api_key},
    json={
        "input": {"prompt": "Write a story", "parameters": {}},
        "output": {"text": "Once upon a time...", "tokens_used": 100},
        "metadata": {"provider": "openai", "model": "gpt-4", "success": True}
    }
)
```
