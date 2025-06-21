# llm_question_generator.py

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

# ✅ Initialize Ollama LLM
llm = Ollama(model="mistral")  # You can change to llama2, gemma, etc.

# ✅ Interview question generation prompt
template = """
You are an expert technical interviewer.
Based on the following resume details, generate 5 technical and 3 behavioral interview questions.

Candidate Name: {name}
Skills: {skills}
Projects: {projects}
Experience: {experience}

Only return the list of questions, clearly numbered.
"""

question_prompt = PromptTemplate(
    input_variables=["name", "skills", "projects", "experience"],
    template=template
)

def generate_llm_questions(name, skills, projects, experience):
    formatted_prompt = question_prompt.format(
        name=name,
        skills=', '.join(skills),
        projects=projects,
        experience=experience
    )
    response = llm.invoke(formatted_prompt)  # ✅ Use invoke (not __call__)
    return [
    q.strip() for q in response.strip().split('\n')
    if q.strip() and not q.strip().lower().endswith("questions:")
    ] # ✅ Clean question list


# ✅ Feedback evaluation for each answer
def evaluate_answer(question, answer):
    prompt = f"""
You are an expert interviewer. Evaluate the following answer.

Question: {question}
Answer: {answer}

Give:
1. A score out of 10
2. A short feedback message

Respond in this format:
Score: <number>/10
Feedback: <message>
"""
    result = llm.invoke(prompt)  # ✅ Use invoke here too
    return result.strip()
