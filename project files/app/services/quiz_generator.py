from app.core.granite_client import query_granite
import re

def generate_quiz_prompt(topic: str, difficulty: str = "medium", num_questions: int = 10) -> str:
    return f"""
You are an AI that generates multiple-choice quizzes. Create a {num_questions}-question quiz on the topic: {topic}.
Difficulty level: {difficulty}.
Each question must have four options labeled A, B, C, D; the correct answer; and explanation for the answer.

Format:
Question 1: ...
A. option1
B. option2
C. option3
D. option4
Answer: C
Explanation: ...

"""

def generate_quiz(topic: str, difficulty: str = "medium", num_questions: int = 10) -> list:
    prompt = generate_quiz_prompt(topic, difficulty, num_questions)
    raw_text = query_granite(prompt, temperature=0.7, max_tokens=800)

    # Parse generated text into structured quiz list [{question, options, answer, explanation}]
    quiz = []
    question_blocks = re.split(r'Question \d+:', raw_text, flags=re.IGNORECASE)[1:]
    for block in question_blocks:
        lines = block.strip().split('\n')
        question_text = lines[0].strip()
        options = {}
        explanation = ""
        answer = None

        for line in lines[1:]:
            line = line.strip()
            # Parse options labeled A., B., C., D.
            if re.match(r'^[A-D]\.', line):
                key = line[0]
                options[key] = line[3:].strip()
            # Parse answer line
            elif line.lower().startswith('answer:'):
                answer = line.split(':',1)[1].strip()
            # Parse explanation line
            elif line.lower().startswith('explanation:'):
                explanation = line.split(':',1)[1].strip()

        quiz.append({
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": explanation
        })
    return quiz
