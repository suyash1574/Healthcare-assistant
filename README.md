# Healthcare AI Assistant

A RAG-based healthcare AI assistant that answers questions from medical documents, provides source citations, and handles appointment scheduling.

## Architecture

```
Documents → Chunking → Embeddings → ChromaDB → Retriever → Groq LLM → Answer
```

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **LLM**: Groq (Llama 3.3 70B)
- **Vector Store**: ChromaDB
- **Embeddings**: all-MiniLM-L6-v2
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker

## Setup

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd healthcare-ai-assistant
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
GROQ_API_KEY=your_api_key_here
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

### Docker

1. Build the image:
```bash
docker build -t healthcare-ai .
```

2. Run the container:
```bash
docker run -p 8000:8000 -e GROQ_API_KEY=your_key healthcare-ai
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Frontend UI |
| `/health` | GET | Health check |
| `/ingest` | POST | Load documents into vector store |
| `/ask` | POST | Ask a question |

## Features

- **RAG Pipeline**: Retrieves relevant document chunks before generating answers
- **Source Citations**: Shows which documents were used for each answer
- **Hallucination Prevention**: Refuses to answer when context is insufficient
- **Appointment Tool**: Routes appointment queries to a dedicated tool
- **Healthcare Guardrails**: No diagnosis or treatment advice

## Knowledge Base

- `telehealth.txt` - Telehealth consultation policies
- `appointment_policy.txt` - Appointment scheduling rules
- `insurance_faq.txt` - Insurance and billing information
- `medication_policy.txt` - Medication management policies
- `hipaa_policy.txt` - HIPAA privacy and security policies

## Example Questions

- "Can I refill medication via telehealth?"
- "What are the appointment cancellation policies?"
- "Book a cardiology appointment"
- "What insurance plans do you accept?"
