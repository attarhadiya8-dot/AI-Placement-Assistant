
import chromadb
import os
from pypdf import PdfReader
from chromadb.utils import embedding_functions
from langchain_ollama import OllamaLLM
from fastapi import FastAPI , UploadFile, File
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
# UPLOAD RESUME
# -----------------------------

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF resumes are supported."
        }

    os.makedirs("../data/uploads", exist_ok=True)

    file_path = f"../data/uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Extract PDF text
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    if not text.strip():
        return {
            "success": False,
            "message": "Could not extract text from the resume."
        }

    # Split resume into chunks
    chunk_size = 1000
    overlap = 150

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    # Create a fresh collection for the uploaded resume
    try:
        client.delete_collection("current_resume")
    except Exception:
        pass

    resume_collection = client.create_collection(
        name="current_resume",
        embedding_function=embedding_function
    )

    # Add chunks to ChromaDB
    ids = [f"resume_chunk_{i}" for i in range(len(chunks))]

    resume_collection.add(
        documents=chunks,
        ids=ids
    )

    return {
        "success": True,
        "filename": file.filename,
        "message": "Resume uploaded and added to the RAG system successfully.",
        "chunks_created": len(chunks),
        "text_length": len(text)
    }

    if not file.filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF resumes are supported."
        }

    os.makedirs("../data/uploads", exist_ok=True)

    file_path = f"../data/uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    if not text.strip():
        return {
            "success": False,
            "message": "Could not extract text from the resume."
        }

    return {
        "success": True,
        "filename": file.filename,
        "message": "Resume uploaded and text extracted successfully.",
        "text_length": len(text)
    }
# -----------------------------
# HELPER: RETRIEVE RESUME
# -----------------------------

def get_resume_context(query, n_results=5):

    current_collection = client.get_collection(
        name="current_resume",
        embedding_function=embedding_function
    )

    results = current_collection.query(
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

Your most important task is to classify each important
job requirement consistently.

RESUME CONTEXT:
----------------
{resume_context}
----------------

JOB DESCRIPTION:
----------------
{request.job_description}
----------------

==================================================
STEP 1 — EXTRACT JOB REQUIREMENTS
==================================================

Identify the important requirements from the job description.

Include:
- Required skills
- Required experience
- Education/degree requirements
- Responsibilities that require specific experience
- Important soft skills

Do not include trivial wording.

==================================================
STEP 2 — CLASSIFY EACH REQUIREMENT
==================================================

For EVERY requirement, assign EXACTLY ONE classification:

MATCH
PARTIAL
MISSING

Use these rules:

MATCH:
Use MATCH when the resume contains clear and direct evidence
that satisfies the requirement.

PARTIAL:
Use PARTIAL when the resume contains related or transferable
evidence, but the exact requirement is not fully demonstrated.

MISSING:
Use MISSING only when there is no meaningful evidence in the
resume supporting the requirement.

==================================================
IMPORTANT EVIDENCE RULES
==================================================

1. Explicit evidence always counts.

Example:

JD:
"Experience managing volunteers."

Resume:
"Managed 25 volunteer workers."

Classification:
MATCH

2. Equivalent demonstrated experience can count as MATCH.

Example:

JD:
"Experience maintaining client databases."

Resume:
"Maintained client databases and records."

Classification:
MATCH

3. Related but incomplete experience should be PARTIAL.

Example:

JD:
"Experience coordinating childcare programs."

Resume:
"Oversaw daily activity and outing planning for 100 clients."

Classification:
PARTIAL

The resume demonstrates activity planning, but does not
explicitly establish responsibility for an entire childcare
program.

4. Do NOT require the exact wording of the JD.

5. Do NOT invent experience.

6. Do NOT assume a skill merely because it is common for
the candidate's profession.

7. Do NOT classify a clearly demonstrated requirement as
MISSING.

8. Do NOT classify a clearly demonstrated requirement as
PARTIAL just because the exact wording differs.

==================================================
EDUCATION RULE
==================================================

Compare the actual degree in the resume with the education
requirement.

If the job accepts a related field and the resume contains
a clearly related degree, classify it as MATCH.

Do not mark a degree as missing when the candidate clearly
has a qualifying related degree.

==================================================
STEP 3 — INTERNAL CLASSIFICATION TABLE
==================================================

Before creating the final answer, internally create a table:

REQUIREMENT | CLASSIFICATION | RESUME EVIDENCE

Every requirement must appear exactly once.

Example:

Experience managing volunteers | MATCH |
"Managed 25 volunteer workers."

Experience coordinating childcare programs | PARTIAL |
"Oversaw daily activity and outing planning..."

Do not show this internal table in the final answer.

==================================================
STEP 4 — FINAL ANSWER
==================================================

After completing the classification table, generate the
following sections.

MATCHING SKILLS

List ONLY requirements classified as MATCH.

PARTIALLY MATCHING / NEEDS MORE EVIDENCE

List ONLY requirements classified as PARTIAL.

MISSING SKILLS

List ONLY requirements classified as MISSING.

RELEVANT EXPERIENCE

List concrete evidence from the resume that supports the
MATCH or PARTIAL classifications.

Do not invent evidence.

PREPARATION PRIORITIES

List ONLY requirements classified as PARTIAL or MISSING.

Do NOT include anything classified as MATCH.

==================================================
FINAL CONSISTENCY CHECK
==================================================

Before returning the answer, verify:

- Every requirement has exactly one classification.
- No MATCH requirement appears under PARTIAL.
- No MATCH requirement appears under MISSING.
- No PARTIAL requirement appears under MISSING.
- No MATCH requirement appears in PREPARATION PRIORITIES.
- Every PREPARATION PRIORITY comes from PARTIAL or MISSING.
- Every claim about the candidate is supported by the resume.
- Do not invent skills, experience, education, or projects.

Return ONLY these sections:

MATCHING SKILLS
1. ...

PARTIALLY MATCHING / NEEDS MORE EVIDENCE
1. ...

MISSING SKILLS
1. ...

RELEVANT EXPERIENCE
1. ...

PREPARATION PRIORITIES
1. ...
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