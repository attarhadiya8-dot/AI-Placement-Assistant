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
You are an AI placement assistant performing a strict resume-to-job comparison.

Use ONLY the information explicitly present in the resume context.

RESUME CONTEXT:
----------------
{context}
----------------

JOB DESCRIPTION:
----------------
{job_description}
----------------

Rules:

1. MATCHING SKILLS
List only skills/requirements from the job description for which
there is clear evidence in the resume.

2. MISSING SKILLS
List only skills/requirements explicitly mentioned in the job
description for which there is NO clear evidence in the resume.

3. RELEVANT EXPERIENCE
List only projects, technologies, education, or experience
explicitly mentioned in the resume that relate to the job.

4. PREPARATION PRIORITIES
Recommend learning topics ONLY from the missing skills.

IMPORTANT:
- Do not infer skills from unrelated experience.
- Do not assume that mentioning a library means expertise in it.
- Do not treat a preferred requirement differently from a required
  requirement; simply label it as "(Preferred)" when appropriate.
- Never put the same skill in both MATCHING and MISSING.
- Do not invent information.
- If evidence is uncertain, do not classify the skill as matching.

Return exactly these sections:

MATCHING SKILLS
MISSING SKILLS
RELEVANT EXPERIENCE
PREPARATION PRIORITIES
"""
analysis = llm.invoke(analysis_prompt)

print("\nSKILL GAP ANALYSIS")
print("=" * 60)
print(analysis)

# -----------------------------
# GROUNDED INTERVIEW QUESTION GENERATOR
# -----------------------------

interview_prompt = f"""
You are an AI placement interview coach.

Your job is to generate interview questions using ONLY the
information explicitly present in the provided resume context
and job description.

IMPORTANT RULES:
- Never claim that the candidate has a skill unless it appears
  explicitly in the resume context.
- Never claim that the candidate has experience with a technology
  unless it appears explicitly in the resume context.
- Do not invent projects, achievements, contributions, or experience.
- For resume-based questions, use only evidence from the resume context.
- For skill-gap questions, use only skills that appear in the
  job description but are NOT clearly present in the resume context.

Resume context:
----------------
{context}
----------------

Job Description:
----------------
{job_description}
----------------

Generate exactly 10 questions.

SECTION 1 — RESUME & PROJECT QUESTIONS
Generate 3 questions based ONLY on projects, technologies,
education, or experience explicitly mentioned in the resume context.

SECTION 2 — TECHNICAL QUESTIONS
Generate 4 technical questions based on the requirements
in the job description.

SECTION 3 — SKILL GAP QUESTIONS
Generate 3 questions about important job requirements that
are NOT clearly demonstrated in the resume context.

Before generating each question, verify that it follows
the rules above.

Do not include answers.
Do not make assumptions about the candidate.
"""

interview_questions = llm.invoke(interview_prompt)

print("\nGROUNDED INTERVIEW QUESTIONS")
print("=" * 60)
print(interview_questions)