from utils import get_llm

def feedback_agent(state):
  llm = get_llm()

  prompt = f"""
  You are a career coach.
  Here is the full interview transcript:
  {state.get('interview_history', "")}

  Generate a final report with:
  1. Overall Score
  2. Top 3 Strengths
  3. Top 3 Weaknesses
  4. Learning Roadmap for next 30 days
  Be specific and encouraging.
  """

  result = llm.invoke(prompt)
  return result.content