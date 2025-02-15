# Finance Audit LLM System

An intelligent audit assistant system that leverages LLM capabilities to analyze financial data and provide comprehensive audit insights.

## Features

- **Dynamic Dataset Handling**: Automatically processes CSV files and adapts to schema changes
- **Intelligent Audit Agents**:
  - Senior Auditor: Creates comprehensive audit plans
  - IT Auditor: Performs detailed technical analysis
  - Report Manager: Generates actionable reports
- **Real-time Chat Interface**: Interactive communication with audit agents
- **Multiple Analysis Categories**:
  - Revenue Cycle Audit
  - Expenditure Cycle Audit
  - Fraud Detection

## System Requirements

- Python 3.8+
- Node.js 14+ (for development tools)
- SQLite3

## Project Structure

```
finance-agentic-llm/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── database/
│   │   └── utils/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── LLMDataset/
    ├── Revenue Cycle Audit/
    ├── Expenditure Cycle Audit/
    └── Fraud Detection/
```

## Setup Instructions

1. Clone the repository:
```bash
git clone [repository-url]
cd finance-agentic-llm
```

2. Set up the Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd backend
pip install -r requirements.txt
```

3. Create a .env file in the backend directory:
```bash
OPENAI_API_KEY=your_api_key_here
DEBUG=True
```

4. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

5. Open the frontend:
- Simply open `frontend/index.html` in a web browser
- Or serve it using a local server:
```bash
python -m http.server 3000
```
Then visit `http://localhost:3000`

## Usage

1. **Dataset Management**:
- Place your CSV files in the appropriate category folders under `LLMDataset/`
- The system will automatically process and import the data
- Changes to CSV files are detected and synchronized automatically

2. **Interacting with Agents**:
- Select a category (Revenue, Expenditure, or Fraud)
- Type your question or request in the chat interface
- The system will coordinate between agents to provide comprehensive responses

3. **Types of Analysis**:
- Audit Planning: Get comprehensive audit strategies
- Data Analysis: Detailed investigation of specific areas
- Report Generation: Get formatted audit reports with findings

## API Endpoints

- `GET /health`: System health check
- `GET /tables`: List available database tables
- `GET /tables/{table_name}/schema`: Get table schema
- `GET /dataset/categories`: List dataset categories
- `GET /dataset/metadata`: Get dataset metadata
- `POST /dataset/sync`: Manually trigger dataset sync
- `WebSocket /ws/chat/{client_id}`: Real-time chat connection

## Development

To modify or extend the system:

1. Backend changes:
- Add new agent capabilities in `backend/app/agents/`
- Modify database handling in `backend/app/database/`
- Update API endpoints in `backend/app/main.py`

2. Frontend changes:
- Modify the UI in `frontend/index.html`
- Update styles in `frontend/style.css`
- Enhance functionality in `frontend/app.js`

## Security Considerations

- Replace the CORS settings with specific origins in production
- Implement proper authentication for the WebSocket connection
- Secure the OpenAI API key and other sensitive configurations
- Validate and sanitize all user inputs

## Limitations

- Currently supports CSV files only
- Limited to three main audit categories
- Requires OpenAI API key for LLM functionality

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]