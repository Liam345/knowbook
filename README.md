# KnowBook

KnowBook is an AI-powered knowledge assistant that helps you organize, chat with, and generate content from your documents and sources.

## Features

- **Project Management**: Organize your work into projects
- **Document Processing**: Upload and process various document formats
- **AI Chat**: Chat with your documents using advanced AI
- **Content Generation**: Generate presentations, reports, and more from your sources

## Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python Flask + SQLite
- **AI**: Claude (Anthropic), OpenAI, Pinecone

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- API Keys for Claude, OpenAI, and Pinecone

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

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   OPENAI_API_KEY=sk-your-key-here
   PINECONE_API_KEY=your-key-here
   PINECONE_INDEX_NAME=your-index-name
   ```

6. Run the backend:
   ```bash
   python run.py
   ```

   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## Project Structure

```
knowbook/
├── backend/                # Python Flask backend
│   ├── app/               # Application code
│   ├── data/              # Data storage (auto-created)
│   ├── config.py          # Configuration
│   └── run.py             # Entry point
└── frontend/              # React frontend
    ├── src/               # Source code
    ├── public/            # Static assets
    └── package.json       # Dependencies
```

## Module Development

This project is built incrementally in modules:

- **Module 1**: Core Project Management ✅
- **Module 2**: Basic Settings & Configuration
- **Module 3**: Source Management - Basic
- **Module 4**: Chat System - Core
- **Module 5**: Source Management - Advanced
- **Module 6**: Chat System - Enhanced
- **Module 7**: Studio - Document Generation
- **Module 8**: Studio - Visual Content
- **Module 9**: Studio - Interactive Content
- **Module 10**: Studio - Media & Code
- **Module 11**: Google Integration

## License

MIT License - see LICENSE file for details