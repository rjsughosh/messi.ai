from fastapi import FastAPI
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re  # Add this import for regular expressions
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv  # Add this import


# Create FastAPI app instance
app = FastAPI()

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
genai.configure(api_key=GEMINI_API_KEY)

def get_wikipedia_info(url):
    """
    Enhanced Wikipedia scraping with better content extraction and debugging
    """
    try:
        print(f"Fetching URL: {url}")
        # Add more complete headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        print("Parsing content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main content div
        main_content = soup.find('div', {'id': 'mw-content-text'})
        
        if main_content:
            # Get all paragraphs within the main content
            paragraphs = main_content.select('.mw-parser-output > p')
            print(f"Found {len(paragraphs)} paragraphs")
            
            relevant_paragraphs = []
            
            for i, p in enumerate(paragraphs):
                text = p.get_text(strip=True)
                # Remove citations [1], [2], etc.
                text = re.sub(r'\[\d+\]', '', text)
                # Only include substantial paragraphs (longer than 50 characters)
                if len(text) > 50:  # Reduced minimum length
                    print(f"Adding paragraph {i} with length {len(text)}")
                    relevant_paragraphs.append(text)
                    # Get first 5 substantial paragraphs
                    if len(relevant_paragraphs) >= 5:
                        break
            
            if relevant_paragraphs:
                result = ' '.join(relevant_paragraphs)
                print(f"Successfully extracted {len(result)} characters")
                return result
            else:
                # For debugging, print the first few characters of the HTML
                print("No relevant paragraphs found")
                print("First 500 chars of HTML:", response.text[:500])
                return None
        else:
            print(f"Could not find main content for {url}")
            print("Available classes:", [c.get('class', []) for c in soup.find_all(class_=True)][:10])
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        print("Exception details:", str(e))
        return None

def retrieve_info(sources):
    """
    Retrieves and combines information from multiple sources
    """
    print("Starting to retrieve information...")
    all_info = []
    for url in sources:
        print(f"\nProcessing source: {url}")
        if 'wikipedia' in url.lower():
            info = get_wikipedia_info(url)
            if info:
                print(f"Got info of length: {len(info)}")
                all_info.append(info)
            else:
                print("No information retrieved from this source")
    
    if all_info:
        result = '\n\n'.join(all_info)
        print(f"Total information gathered: {len(result)} characters")
        return result
    else:
        print("No information gathered from any source")
        return "No information could be retrieved from the sources."

def query_ai_model(question):
    """
    Uses Google's Gemini model with RAG to generate an answer.
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # List of relevant sources
        sources = [
            "https://en.wikipedia.org/wiki/Lionel_Messi",
            # Temporarily comment out other sources for debugging
            # "https://en.wikipedia.org/wiki/Inter_Miami_CF",
            # "https://en.wikipedia.org/wiki/Argentina_national_football_team"
        ]
        
        print("\nStarting content retrieval...")
        # Get latest information
        current_context = retrieve_info(sources)
        
        print("\n--------------------------------")
        print("Retrieved context:")
        print(current_context)
        print("--------------------------------\n")
        
        if not current_context or current_context.isspace():
            print("Warning: No context was retrieved!")
            
        prompt = f"""
        You are an expert on Lionel Messi. Answer the following question using:
        1. Your comprehensive knowledge about Messi's career, life, and personal details
        2. The current context below (if relevant for recent updates)

        Current Context (Recent Information):
        {current_context}

        Question: {question}

        Instructions:
        - Provide a concise answer (under 100 words)
        - Use your built-in knowledge for general facts about Messi
        - Only refer to the context for very recent events or updates
        - If you're certain about information from your knowledge, use it even if it's not in the context
        - Be clear about what information is recent vs. general knowledge
        - Do not mention anything about context, sources, or knowledge base
        """

        response = model.generate_content(prompt)
        
        if response.prompt_feedback.block_reason:
            return "I'm sorry, I cannot provide an answer to that question."
            
        return response.text
            
    except Exception as e:
        print(f"Error querying Gemini: {str(e)}")
        return "I'm sorry, I encountered an error while generating the response."

# Root endpoint to test if the API is running
@app.get("/")
def home():
    return {"message": "Messi AI Backend is running!"}

    # New endpoint to handle Messi-related questions
@app.get("/ask")
def ask_messi(question: str):
    """
    Endpoint to handle Messi-related questions
    """
    ai_answer = query_ai_model(question)
    
    return {
        "question": question,
        "answer": ai_answer,
        "source": "Gemini AI with RAG",
        "timestamp": datetime.now().isoformat()
    }

# Add this after creating the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run the server using: uvicorn app.main:app --reload
