from utils import get_llm

def interview_manager(state):
  llm = get_llm()
  prompt = f"""
    You are an interview coordinator.
    Job role: {state['job_role']}
    Resume summary: {state['resume_data']}
    Decide whether to start with Technical or Behavioral round.
    Reply with one word only: Technical or Behavioral.
  """
  result = llm.invoke(prompt)
  return result.content.strip()