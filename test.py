print("=" * 50)
print("AI INTERVIEW COACH — FULL FLOW TEST")
print("=" * 50)

from agents.resume_parser import parse_resume
from agents.interview_manager import interview_manager
from agents.technical_agent import technical_agent
from agents.behavioral_agent import behavioral_agent
from agents.evaluator_agent import evaluator_agent
from agents.feedback_agent import feedback_agent

# Step 1: Parse resume
print("\n[1] Testing Resume Agent...")
resume_data = parse_resume("Ahmed-Awan-Front-End-Engineer.pdf")  # change to your actual PDF filename
print("✅ Resume parsed successfully")
print(resume_data[:150], "...\n")

# Step 2: Build state
state = {
    "job_role": "Frontend Developer",
    "company": "Google",
    "resume_data": resume_data,
    "interview_history": "",
    "round": "",
    "question": "",
    "evaluation": ""
}

# Step 3: Interview Manager decides round
print("[2] Testing Interview Manager...")
round_decision = interview_manager(state)
state["round"] = round_decision
print(f"✅ Round decided: {round_decision}\n")

# Step 4: Generate first question
print("[3] Testing Technical/Behavioral Agent...")
if "Technical" in round_decision:
    question = technical_agent(state, include_code=True)
else:
    question = behavioral_agent(state)
print(f"✅ Question generated:\n{question}\n")

# Step 5: Simulate an answer and evaluate
print("[4] Testing Evaluator Agent...")
fake_answer = "I would use useState and useEffect to manage the component state and side effects."
evaluation = evaluator_agent(question, fake_answer)
print(f"✅ Evaluation: {evaluation}\n")

# Step 6: Add to history and generate feedback
state["interview_history"] += f"\nQ: {question}\nA: {fake_answer}\nScore: {evaluation}\n"

print("[5] Testing Feedback Agent...")
report = feedback_agent(state)
print(f"✅ Final report generated:\n{report}\n")

print("=" * 50)
print("ALL 6 AGENTS WORKING — PIPELINE COMPLETE ✅")
print("=" * 50)