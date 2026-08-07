import json
import os
import chromadb
from typing import List

# Initialize an in-memory ChromaDB client for vector storage
chroma_client = chromadb.Client()

def setup_policy_vector_db():
    """Indexes policies from policies.json into ChromaDB."""
    collection = chroma_client.get_or_create_collection(name="policies")
    
    # Avoid re-indexing if already populated
    if collection.count() > 0:
        return collection
        
    policies_path = os.path.join(os.path.dirname(__file__), "../../data/policies.json")
    
    if os.path.exists(policies_path):
        with open(policies_path, "r") as f:
            policies = json.load(f)
            
        documents = [p["rule"] for p in policies]
        metadatas = [{"category": p["category"]} for p in policies]
        ids = [p["id"] for p in policies]
        
        # Add to ChromaDB vector store
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    return collection

def search_relevant_policies(query: str, top_k: int = 2) -> List[str]:
    """Retrieves the top-k most relevant policy rules for a query."""
    collection = setup_policy_vector_db()
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    # Extract matching policy texts
    if results and "documents" in results and len(results["documents"]) > 0:
        return results["documents"][0]
    return []