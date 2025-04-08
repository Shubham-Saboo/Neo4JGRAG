import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import openai

# Load environment variables
load_dotenv()

def test_neo4j_connection():
    """Test connection to Neo4j database"""
    try:
        # Get Neo4j credentials from environment variables
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        # Create driver instance
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Test connection with a simple query
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                print("✅ Neo4j connection successful!")
            else:
                print("❌ Neo4j connection failed: Unexpected result")
    except Exception as e:
        print(f"❌ Neo4j connection error: {str(e)}")
    finally:
        driver.close()

def test_openai_connection():
    """Test connection to OpenAI API"""
    try:
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        # Set the API key
        openai.api_key = api_key
        
        # Test connection with a simple completion using the latest GPT model
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi"}
            ],
            max_tokens=10
        )
        
        if response and hasattr(response, 'choices') and response.choices:
            print("✅ OpenAI connection successful!")
            print(f"Response: {response.choices[0].message.content}")
        else:
            print("❌ OpenAI connection failed: No response received")
    except ValueError as ve:
        print(f"❌ OpenAI connection error: {str(ve)}")
    except Exception as e:
        print(f"❌ OpenAI connection error: {str(e)}")

if __name__ == "__main__":
    print("Testing connections...")
    test_neo4j_connection()
    test_openai_connection() 