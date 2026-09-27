
import chromadb
from chromadb.utils import embedding_functions
from langchain_ollama import OllamaLLM
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(title="AI Placement Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# RAG SETUP
# -----------------------------

client = chromadb.PersistentClient(path="../data/chroma_db")

embedding_function = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_collection(
    name="resume",
    embedding_function=embedding_function
)

llm = OllamaLLM(model="llama3.2:3b")


# -----------------------------
# REQUEST MODELS
# -----------------------------

class QuestionRequest(BaseModel):
    question: str


class JobRequest(BaseModel):
    job_description: str


# -----------------------------
# HELPER: RETRIEVE RESUME
# -----------------------------

def get_resume_context(query, n_results=5):

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = results["documents"][0]

    return "\n\n".join(documents)


# -----------------------------
# HOME
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "AI Placement Assistant API is running"
    }


# -----------------------------
# ASK RESUME
# -----------------------------

@app.post("/ask")
def ask_resume(request: QuestionRequest):

    context = get_resume_context(request.question)

    prompt = f"""
You are an AI placement assistant.

Answer the user's question using ONLY the information
provided in the resume context.

If the answer is not present in the context, say:
"I couldn't find that information in the resume."

Resume context:
----------------
{context}
----------------

Question:
{request.question}

Answer clearly and concisely.
"""

    answer = llm.invoke(prompt)

    return {
        "question": request.question,
        "answer": answer
    }


# -----------------------------
# JOB MATCH / SKILL GAP
# -----------------------------

@app.post("/analyze-job")
def analyze_job(request: JobRequest):

    # Retrieve resume information relevant to the JD
    resume_context = get_resume_context(
        request.job_description,
        n_results=8
    )

    prompt = f"""
You are an AI placement assistant performing a strict
resume-to-job comparison.

Use ONLY information explicitly present in the resume context.

RESUME CONTEXT:
----------------
{resume_context}
----------------

JOB DESCRIPTION:
----------------
{request.job_description}
----------------

Rules:

1. MATCHING SKILLS
List only requirements from the job description for which
there is clear evidence in the resume.

2. MISSING SKILLS
List only requirements from the job description for which
there is no clear evidence in the resume.

3. RELEVANT EXPERIENCE
List only projects, technologies, education, or experience
explicitly present in the resume that relate to the job.

4. PREPARATION PRIORITIES
Recommend learning topics only from the missing skills.

IMPORTANT:
- Never invent candidate skills or experience.
- Never put the same requirement in both matching and missing.
- Do not infer expertise from unrelated experience.
- If evidence is uncertain, do not classify it as matching.

Return exactly these sections:

MATCHING SKILLS
MISSING SKILLS
RELEVANT EXPERIENCE
PREPARATION PRIORITIES
"""

    analysis = llm.invoke(prompt)

    return {
        "analysis": analysis
    }


# -----------------------------
# INTERVIEW QUESTIONS
# -----------------------------

@app.post("/interview")
def generate_interview(request: JobRequest):

    resume_context = get_resume_context(
        request.job_description,
        n_results=8
    )

    prompt = f"""
You are an AI placement interview coach.

Generate personalized interview questions using ONLY
the resume context and job description below.

RESUME CONTEXT:
----------------
{resume_context}
----------------

JOB DESCRIPTION:
----------------
{request.job_description}
----------------

Generate exactly 10 questions.

SECTION 1 — RESUME & PROJECT QUESTIONS
Generate 3 questions based only on projects, technologies,
education, or experience explicitly mentioned in the resume.

SECTION 2 — TECHNICAL QUESTIONS
Generate 4 questions based on technical requirements
in the job description.

SECTION 3 — SKILL GAP QUESTIONS
Generate 3 questions related to important requirements
from the job description that are not clearly demonstrated
in the resume.

IMPORTANT:
- Do not invent projects.
- Do not claim the candidate has a skill unless it appears
  in the resume context.
- Do not claim the candidate has experience with a technology
  unless it appears in the resume context.
- Do not include answers.
- Make questions suitable for an AI/ML Engineer internship.
"""

    questions = llm.invoke(prompt)

    return {
        "questions": questions
    }