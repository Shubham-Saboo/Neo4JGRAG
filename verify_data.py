from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Neo4j connection details
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

def verify_data():
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # Count nodes by label
            result = session.run("""
                MATCH (n)
                RETURN labels(n) as label, count(*) as count
                ORDER BY label
            """)
            
            print("\nNode Counts:")
            for record in result:
                print(f"{record['label']}: {record['count']}")
            
            # Count relationships by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY type
            """)
            
            print("\nRelationship Counts:")
            for record in result:
                print(f"{record['type']}: {record['count']}")
            
            # Sample data verification
            result = session.run("""
                MATCH (p:Product)
                RETURN p.name as name, p.description as description
                LIMIT 5
            """)
            
            print("\nSample Products:")
            for record in result:
                print(f"Name: {record['name']}")
                print(f"Description: {record['description']}\n")
            
    except Exception as e:
        print(f"Error verifying data: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    verify_data() 