import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()
embedding_func = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="enterprise_policies_deep",
    embedding_function=embedding_func
)

def search_relevant_policies(query: str, platform_type: str = "E-Commerce Platforms", top_k: int = 2):
    """Domain-isolated vector search using metadata filtering on 'platform'."""
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"platform": platform_type}
        )
        
        retrieved_docs = []
        if results and "documents" in results and results["documents"]:
            for doc in results["documents"][0]:
                retrieved_docs.append(doc)
                
        return retrieved_docs if retrieved_docs else [f"Standard {platform_type} domain terms apply."]
    except Exception as e:
        return [f"Standard {platform_type} policy applied (Vector search fallback: {str(e)})"]