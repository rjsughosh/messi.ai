 # Messi AI Project

An AI-powered application that provides information about Lionel Messi using FastAPI, OpenAI, and Wikipedia APIs.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables:
   - Create a `.env` file
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

## Running the Application

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

