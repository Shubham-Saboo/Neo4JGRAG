import streamlit as st
from neo4j import GraphDatabase
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Supply Chain RAG Assistant",
    page_icon="📦",
    layout="wide"
)

# Neo4j connection details
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

# Initialize OpenAI components
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model="gpt-4-turbo-preview")

def get_relevant_context(question: str) -> str:
    """Retrieve relevant context from Neo4j based on the question."""
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # Get question embedding
            question_embedding = embeddings.embed_query(question)
            
            # Query Neo4j for relevant context
            result = session.run("""
                MATCH (p:Product)
                WHERE p.description_embedding IS NOT NULL
                WITH p, 
                     reduce(s = 0, i in range(0, size(p.description_embedding)-1) | 
                           s + p.description_embedding[i] * $embedding[i]) as similarity
                ORDER BY similarity DESC
                LIMIT 3
                OPTIONAL MATCH (p)<-[:SUPPLIES]-(s:Supplier)
                OPTIONAL MATCH (p)-[:STORED_AT]->(w:Warehouse)
                RETURN p.name as product_name, 
                       p.description as product_description,
                       collect(DISTINCT {type: 'SUPPLIES', name: s.name}) as suppliers,
                       collect(DISTINCT {type: 'STORED_AT', name: w.name, location: w.location}) as warehouses
            """, embedding=question_embedding)
            
            # Format the context
            context = []
            for record in result:
                context.append(f"Product: {record['product_name']}")
                context.append(f"Description: {record['product_description']}")
                if record['suppliers']:
                    for supplier in record['suppliers']:
                        if supplier['name']:
                            context.append(f"Supplied by: {supplier['name']}")
                if record['warehouses']:
                    for warehouse in record['warehouses']:
                        if warehouse['name']:
                            context.append(f"Stored at: {warehouse['name']} in {warehouse['location']}")
                context.append("---")
            
            return "\n".join(context) if context else "No relevant context found."
            
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return "Error retrieving context."
    finally:
        driver.close()

# Define the prompt template
template = """You are a helpful supply chain assistant. Use the following context to answer the question.
If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

Context: {context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)

# Create the RAG chain
rag_chain = (
    {"context": lambda x: get_relevant_context(x), "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def ask_question(question: str) -> str:
    """Ask a question about the supply chain data."""
    try:
        return rag_chain.invoke(question)
    except Exception as e:
        return f"Error processing question: {e}"

# Streamlit UI
st.title("📦 Supply Chain RAG Assistant")

# Add sidebar with information
with st.sidebar:
    st.header("About")
    st.write("""
    This application uses Neo4j and OpenAI to answer questions about the supply chain.
    
    You can ask questions about:
    - Products and their descriptions
    - Suppliers and their locations
    - Warehouse locations and capacities
    - Product storage and distribution
    """)
    
    st.header("Example Questions")
    st.write("""
    - What products are available?
    - Where are the laptops stored?
    - Which suppliers provide smartphones?
    - What audio products are available?
    - Tell me about the supply chain for tablets
    """)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about the supply chain..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        response = ask_question(prompt)
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response}) 