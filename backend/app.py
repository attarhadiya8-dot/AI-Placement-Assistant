import chromadb
from chromadb.utils import embedding_functions
from langchain_ollama import OllamaLLM


# -----------------------------
# 1. Connect to ChromaDB
# -----------------------------

client = chromadb.PersistentClient(
    path="../data/chroma_db"
)

embedding_function = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_collection(
    name="resume",
    embedding_function=embedding_function
)


# -----------------------------
# 2. Create local LLM
# -----------------------------

llm = OllamaLLM(
    model="llama3.2:3b"
)


# -----------------------------
# 3. Ask a question
# -----------------------------

question = "What programming languages does this candidate know?"


# -----------------------------
# 4. Retrieve relevant context
# -----------------------------

results = collection.query(
    query_texts=[question],
    n_results=3
)

documents = results["documents"][0]

context = "\n\n".join(documents)


# -----------------------------
# 5. Create RAG prompt
# -----------------------------

prompt = f"""
You are an AI placement assistant.

Answer the user's question using ONLY the information
provided in the resume context below.

If the answer is not present in the context, say:
"I couldn't find that information in the resume."

Resume context:
----------------
{context}
----------------

Question:
{question}

Answer clearly and concisely.
"""


# -----------------------------
# 6. Generate answer
# -----------------------------

answer = llm.invoke(prompt)

print("\nQUESTION")
print(question)

print("\nANSWER")
print("=" * 60)
print(answer)