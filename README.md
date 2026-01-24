# CortexLab - AI Research Agent

An AI-powered research assistant that helps researchers discover research gaps, plan experiments, and generate research paper drafts.

## Features

- 🔍 **Research Gap Discovery**: Analyze a research domain to identify current trends, unexplored areas, and opportunities
- 📊 **Deep Dive Analysis**: Get detailed experiment recommendations for your chosen research direction
- 📝 **Paper Drafting**: Generate publication-ready research paper drafts from your experiment results
- 📤 **Export to Word**: Download your paper drafts as .docx files

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL / SQLite
- **ORM**: SQLAlchemy 2.0
- **AI**: LangGraph + LangChain + Google Gemini
- **Auth**: Google OAuth

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query + Zustand
- **Routing**: React Router v6

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your Google Client ID
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

The app will be available at http://localhost:5173

## Environment Variables

### Backend (.env)

```
DATABASE_URL=sqlite+aiosqlite:///./cortexlab.db
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_API_KEY=your-gemini-api-key
SESSION_SECRET_KEY=your-secret-key-at-least-32-chars
```

### Frontend (.env)

```
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
CortexLab/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API routes
│   │   ├── agents/         # LangGraph agent system
│   │   ├── core/           # Database, security, streaming
│   │   ├── models/         # SQLAlchemy ORM models
│   │   └── schemas/        # Pydantic schemas
│   └── requirements.txt
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── lib/            # API client, utilities
│   │   └── stores/         # Zustand stores
│   └── package.json
│
└── README.md
```

## License

MIT
