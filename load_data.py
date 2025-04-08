from neo4j import GraphDatabase
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Neo4jVector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neo4j connection details
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

# Initialize Neo4j driver
driver = GraphDatabase.driver(URI, auth=AUTH)

def load_products():
    """Load product data into Neo4j and create vector embeddings."""
    # Sample product data
    products = [
        {
            "id": "P1",
            "name": "Laptop",
            "description": "High-performance laptop with 16GB RAM and 512GB SSD, perfect for business and creative work",
            "price": 999.99,
            "category": "Electronics"
        },
        {
            "id": "P2",
            "name": "Smartphone",
            "description": "Latest smartphone with 5G capability, 128GB storage, and advanced camera system",
            "price": 699.99,
            "category": "Electronics"
        },
        {
            "id": "P3",
            "name": "Wireless Headphones",
            "description": "Premium noise-cancelling wireless headphones with 30-hour battery life",
            "price": 249.99,
            "category": "Audio"
        },
        {
            "id": "P4",
            "name": "Smart Watch",
            "description": "Fitness tracker and smartwatch with heart rate monitoring and GPS",
            "price": 199.99,
            "category": "Wearables"
        },
        {
            "id": "P5",
            "name": "Tablet",
            "description": "10-inch tablet with 256GB storage, perfect for entertainment and productivity",
            "price": 449.99,
            "category": "Electronics"
        }
    ]
    
    # Create vector index for product descriptions
    with driver.session() as session:
        session.run("""
            CREATE VECTOR INDEX product_description_embeddings IF NOT EXISTS
            FOR (p:Product) ON (p.description_embedding)
            OPTIONS {indexConfig: {
                `vector.dimensions`: 1536,
                `vector.similarity_function`: 'cosine'
            }}
        """)
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings()
    
    # Process each product
    for product in products:
        # Create document for embedding
        doc = Document(
            page_content=product["description"],
            metadata={"id": product["id"]}
        )
        
        # Generate embedding
        embedding = embeddings.embed_documents([doc.page_content])[0]
        
        # Create product node with embedding
        with driver.session() as session:
            session.run("""
                MERGE (p:Product {id: $id})
                SET p.name = $name,
                    p.description = $description,
                    p.price = $price,
                    p.category = $category,
                    p.description_embedding = $embedding
            """, {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "category": product["category"],
                "embedding": embedding
            })

def load_suppliers():
    """Load supplier data into Neo4j."""
    suppliers = [
        {"id": "S1", "name": "Tech Supplier Inc", "location": "USA", "specialization": "Electronics"},
        {"id": "S2", "name": "Global Electronics", "location": "China", "specialization": "Components"},
        {"id": "S3", "name": "Audio Solutions Ltd", "location": "Germany", "specialization": "Audio Equipment"},
        {"id": "S4", "name": "Wearable Tech Co", "location": "South Korea", "specialization": "Wearables"},
        {"id": "S5", "name": "Smart Devices Corp", "location": "Japan", "specialization": "Smart Devices"}
    ]
    
    with driver.session() as session:
        for supplier in suppliers:
            session.run("""
                MERGE (s:Supplier {id: $id})
                SET s.name = $name,
                    s.location = $location,
                    s.specialization = $specialization
            """, supplier)

def load_warehouses():
    """Load warehouse data into Neo4j."""
    warehouses = [
        {"id": "W1", "name": "Main Warehouse", "location": "New York", "capacity": 10000},
        {"id": "W2", "name": "West Coast Hub", "location": "Los Angeles", "capacity": 8000},
        {"id": "W3", "name": "European Distribution", "location": "Amsterdam", "capacity": 7500},
        {"id": "W4", "name": "Asia Pacific Center", "location": "Singapore", "capacity": 9000},
        {"id": "W5", "name": "Southern Hub", "location": "Miami", "capacity": 6000}
    ]
    
    with driver.session() as session:
        for warehouse in warehouses:
            session.run("""
                MERGE (w:Warehouse {id: $id})
                SET w.name = $name,
                    w.location = $location,
                    w.capacity = $capacity
            """, warehouse)

def load_transportation_routes():
    """Load transportation routes between warehouses."""
    routes = [
        {"from": "W1", "to": "W2", "distance": 2800, "duration": 48},
        {"from": "W2", "to": "W1", "distance": 2800, "duration": 48}
    ]
    
    with driver.session() as session:
        for route in routes:
            session.run("""
                MATCH (w1:Warehouse {id: $from})
                MATCH (w2:Warehouse {id: $to})
                MERGE (w1)-[r:CONNECTED_TO]->(w2)
                SET r.distance = $distance,
                    r.duration = $duration
            """, route)

def create_relationships():
    """Create relationships between products and other entities."""
    relationships = [
        {"product_id": "P1", "supplier_id": "S1", "warehouse_id": "W1"},
        {"product_id": "P2", "supplier_id": "S2", "warehouse_id": "W2"},
        {"product_id": "P3", "supplier_id": "S3", "warehouse_id": "W3"},
        {"product_id": "P4", "supplier_id": "S4", "warehouse_id": "W4"},
        {"product_id": "P5", "supplier_id": "S5", "warehouse_id": "W5"},
        # Additional relationships for redundancy
        {"product_id": "P1", "supplier_id": "S2", "warehouse_id": "W5"},
        {"product_id": "P2", "supplier_id": "S1", "warehouse_id": "W3"},
        {"product_id": "P3", "supplier_id": "S5", "warehouse_id": "W1"},
        {"product_id": "P4", "supplier_id": "S3", "warehouse_id": "W2"},
        {"product_id": "P5", "supplier_id": "S4", "warehouse_id": "W4"}
    ]
    
    with driver.session() as session:
        for rel in relationships:
            # Create SUPPLIES relationship between supplier and product
            session.run("""
                MATCH (s:Supplier {id: $supplier_id})
                MATCH (p:Product {id: $product_id})
                MERGE (s)-[:SUPPLIES]->(p)
            """, rel)
            
            # Create STORED_AT relationship between product and warehouse
            session.run("""
                MATCH (p:Product {id: $product_id})
                MATCH (w:Warehouse {id: $warehouse_id})
                MERGE (p)-[:STORED_AT]->(w)
            """, rel)

def load_all_data():
    """Load all data into Neo4j."""
    print("Loading products...")
    load_products()
    print("Loading suppliers...")
    load_suppliers()
    print("Loading warehouses...")
    load_warehouses()
    print("Loading transportation routes...")
    load_transportation_routes()
    print("Creating relationships...")
    create_relationships()
    print("Data loading completed!")

if __name__ == "__main__":
    load_all_data()
    driver.close() 