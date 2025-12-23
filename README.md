# TTB Chatbot

A conversational AI chatbot built for Thai Techno Bank (TTB) that provides intelligent customer support using Retrieval-Augmented Generation (RAG) technology. The chatbot leverages a knowledge base of credit risk management guidelines to answer customer inquiries about loans, account opening, and payment issues.

## 🎯 Features

- **RAG-Powered AI**: Uses vector embeddings and semantic search to retrieve relevant information from a credit risk management knowledge base
- **Intelligent Routing**: Classifies customer queries into categories:
  - สินเชื่อ (Credit/Loans)
  - เปิดบัญชีอย่างไร (How to Open Account)
  - ยอดเงินไม่เข้า (Money Not Received)
  - สแกนจ่ายไม่ได้ (QR Payment Failed)
  - Greeting responses
- **Multi-Turn Conversations**: Maintains conversation context across multiple exchanges
- **Chat Audit Logging**: Records all interactions for compliance and analysis
- **CORS-Enabled API**: Ready for cross-origin requests from web and mobile clients

## 📁 Project Structure

```
ttb-chatbot/
├── backend.py                                    # FastAPI backend server
├── ai_agent.py                                   # AI agent logic with LangGraph
├── ai_test.py                                    # AI agent tests
├── ragds.ipynb                                   # RAG development notebook
├── test_case.json                                # Test cases
├── chat_audit_log.txt                            # Chat interaction logs
├── credit_risk_management_guidebook_vectorstore/ # Vector store with embeddings
└── ttb-chatbot-ui/                               # React TypeScript frontend
    ├── src/
    │   ├── App.tsx                              # Main React component
    │   ├── App.css                              # Application styles
    │   ├── main.tsx                             # Entry point
    │   ├── index.css                            # Global styles
    │   └── assets/                              # Static assets
    ├── public/                                  # Public files
    ├── package.json                             # Frontend dependencies
    ├── tsconfig.json                            # TypeScript config
    ├── vite.config.ts                           # Vite build config
    └── eslint.config.js                         # Linting rules
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Ollama (for local LLM and embeddings)

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install fastapi uvicorn langgraph langchain-community langchain-ollama chroma-db pydantic
   ```

2. **Configure Ollama Models**
   ```bash
   # Pull the required models
   ollama pull gemma3:4b
   ollama pull mxbai-embed-large:latest
   ```

3. **Start the Backend Server**
   ```bash
   uvicorn backend:app --reload
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd ttb-chatbot-ui
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   The UI will be available at `http://localhost:5173`

## 🔧 API Endpoints

### Chat Endpoint

**POST** `/chat`

Sends a user message and receives an AI response.

**Request Body:**
```json
{
  "user_input": "I want to apply for a loan",
  "thread_id": "user-123"
}
```

**Response:**
```json
{
  "final_output": "AI response text here",
  "decision": "สินเชื่อ",
  "raw_metadata": {
    "source_documents": [...],
    "confidence": 0.95
  }
}
```

## 🤖 How It Works

### Architecture Flow

1. **Query Processing**: User input is received by the FastAPI backend
2. **Classification**: LLM classifies the query into one of the predefined categories
3. **Document Retrieval**: Relevant documents are fetched from the vector store using semantic similarity
4. **Response Generation**: LLM generates a response based on retrieved context
5. **Logging**: Interaction is logged for audit and compliance
6. **Response Delivery**: Response is sent to the frontend

### Key Components

- **ai_agent.py**: 
  - LangGraph state machine for managing conversation flow
  - Vector store integration with Chroma
  - LLM configuration (Ollama with Gemma 3)
  - Document retrieval with similarity scoring

- **backend.py**:
  - FastAPI application
  - CORS middleware configuration
  - Chat endpoint implementation
  - Conversation memory management

## 📊 Configuration

### Vector Store Settings
- **Location**: `credit_risk_management_guidebook_vectorstore/`
- **Embedding Model**: `mxbai-embed-large:latest`
- **Similarity Threshold**: Configurable in `ai_agent.py`

### Knowledge Sources (PDFs and Documents)
- **Included PDF**: `PrinciplesForManagementofCreditRisk.pdf` — placed at the repository root. This PDF is part of the credit risk guidebook used as a source for retrieval.
- **How it's used**: The project loads documents (PDFs) and converts them into vector embeddings stored in `credit_risk_management_guidebook_vectorstore/` for semantic search during RAG. The loader in `ai_agent.py` uses `PyMuPDFLoader` to read PDF content and `OllamaEmbeddings` to create embeddings.

### Updating the Vector Store with New Documents
If you add or update PDFs or other source documents, re-create the vector store with these steps:

1. Install required extras (if not already):
```bash
pip install pymupdf
```

2. Run your ingestion script or open `ragds.ipynb` and re-run the cells that:
  - Load documents using `PyMuPDFLoader`
  - Split text (if applicable) with `CharacterTextSplitter`
  - Generate embeddings using `OllamaEmbeddings`
  - Persist the vectorstore to `credit_risk_management_guidebook_vectorstore/`

3. Restart the backend so the updated vectorstore is picked up by the agent.

Notes:
- Keep large source files out of the repo when possible; store them externally and populate the vector store during deployment or provisioning.
- If you need help writing an ingestion script, I can add a small helper that walks a folder and updates the Chroma store.

### LLM Settings
- **Model**: `gemma3:4b`
- **Temperature**: 0.2 (low for consistent responses)
- **Max Tokens**: 50

## 📝 Logging

Chat interactions are logged in `chat_audit_log.txt` with:
- Timestamp
- Thread ID
- User query
- Bot response
- Retrieved metadata
- Decision classification

## 🧪 Testing

Run the test suite:
```bash
python ai_test.py
```

View test cases in `test_case.json`

## 🛠️ Development

### Running in Development Mode

**Terminal 1 - Backend:**
```bash
python backend.py
```

**Terminal 2 - Frontend:**
```bash
cd ttb-chatbot-ui
npm run dev
```

### Code Quality

Lint the frontend code:
```bash
cd ttb-chatbot-ui
npm run lint
```

### Building for Production

**Frontend:**
```bash
cd ttb-chatbot-ui
npm run build
```

## � Docker

Docker is used to containerize both the backend and frontend for consistent deployments across environments.

### Build Backend Image

```bash
# Build the backend Docker image
docker build -f Dockerfile -t ttb-chatbot-backend:latest .

# Run the container locally
docker run --rm -it -p 8000:8000 ttb-chatbot-backend:latest
```

### Build Frontend Image

```bash
# Build the frontend Docker image
cd ttb-chatbot-ui
docker build -f Dockerfile -t ttb-chatbot-frontend:latest .

# Run the container
docker run --rm -it -p 5173:5173 ttb-chatbot-frontend:latest
```

### Docker Compose

Run both services together:

```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up -d --build

# Stop services
docker compose down
```


## �📦 Dependencies

### Backend
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `langchain`: LLM framework
- `langgraph`: Graph-based agent orchestration
- `chroma-db`: Vector database
- `pydantic`: Data validation

### Frontend
- `react`: UI framework
- `typescript`: Type safety
- `tailwindcss`: Styling
- `vite`: Build tool

## 🔐 Security Considerations

- CORS is currently set to allow all origins (`allow_origins=["*"]`) - restrict in production
- Input validation should be enhanced for production use
- Consider adding authentication/authorization
- Sanitize logged data to avoid sensitive information exposure


