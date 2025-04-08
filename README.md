# Neo4j Graph RAG Application

A Graph RAG (Retrieval-Augmented Generation) application using Neo4j as the knowledge graph and OpenAI for text generation.
<img width="1421" alt="Screenshot 2025-04-08 at 15 03 29" src="https://github.com/user-attachments/assets/c4c76371-5c1f-41e0-8dc2-7d3358fc6055" />

## Prerequisites

- Python 3.11 or higher
- Neo4j Database (local or cloud instance)
- OpenAI API key
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Neo4JGRAG
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Edit the `.env` file with your credentials:
```
# Neo4j Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# OpenAI API Configuration
OPENAI_API_KEY=your_api_key
```

## Testing the Setup

Before proceeding, verify your connections to Neo4j and OpenAI:

```bash
python test_connection.py
```

This script will test both the Neo4j database connection and OpenAI API connection. You should see success messages for both services.

## Loading Data

To load the sample data into Neo4j:

```bash
python load_data.py
```

This will:
- Create product nodes with vector embeddings
- Create supplier nodes
- Create warehouse nodes
- Create transportation routes
- Set up the necessary relationships

## Running the RAG Application

To start the RAG application:

```bash
python rag_app.py
```

## Project Structure

- `load_data.py`: Script to load sample data into Neo4j
- `rag_app.py`: Main RAG application
- `test_connection.py`: Script to verify Neo4j and OpenAI connections
- `requirements.txt`: Python dependencies
- `.env.example`: Template for environment variables
- `.gitignore`: Specifies files to ignore in version control

## Troubleshooting

If you encounter any issues:

1. Verify your Neo4j database is running and accessible
2. Check your OpenAI API key is valid
3. Ensure all environment variables are set correctly
4. Try running the test connection script to identify any connection issues
5. Make sure all dependencies are installed correctly

## License

[Your License Here] 
