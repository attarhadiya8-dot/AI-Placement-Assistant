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

# -----------------------------
# JOB DESCRIPTION ANALYSIS
# -----------------------------

jd_path = "../data/job_description.txt"

with open(jd_path, "r", encoding="utf-8") as file:
    job_description = file.read()

print("\nJOB DESCRIPTION")
print("=" * 60)
print(job_description)

# -----------------------------
# SKILL GAP ANALYSIS
# -----------------------------

analysis_prompt = f"""
You are an AI placement assistant.

Compare the candidate's resume with the job description.

Resume context:
----------------
{context}
----------------

Job Description:
----------------
{job_description}
----------------

Analyze the candidate against the job description.

Give the result in exactly these sections:

1. MATCHING SKILLS
List the skills from the job description that are clearly present
in the resume.

2. MISSING SKILLS
List the important skills from the job description that are not
clearly present in the resume.

3. RELEVANT EXPERIENCE
Mention projects, technologies, or experience from the resume
that are relevant to this job.

4. PREPARATION PRIORITIES
Suggest the most useful topics the candidate should learn or
practice based on the missing skills.

Do not invent skills or experience that are not present in the resume.
"""

analysis = llm.invoke(analysis_prompt)

print("\nSKILL GAP ANALYSIS")
print("=" * 60)
print(analysis)