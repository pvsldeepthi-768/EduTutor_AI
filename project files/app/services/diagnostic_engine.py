# app/services/diagnostic_engine.py

from app.core.granite_client import query_granite


def generate_diagnostic_prompt(subject: str = "General Science") -> str:
    return f"""
    You are an AI tutor. Create a diagnostic test to evaluate a student's knowledge level in the subject: {subject}.
    Ask 5 multiple-choice questions. Each question should have 4 options (A, B, C, D) and mark the correct answer.
    Provide the quiz in a clear format:

    Question 1: ...
    A. ...
    B. ...
    C. ...
    D. ...
    Answer: B
    """


def generate_diagnostic_test(subject: str = "General Science") -> str:
    prompt = generate_diagnostic_prompt(subject)
    return query_granite(prompt, temperature=0.6, max_tokens=500)



