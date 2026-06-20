from utils import get_llm
import json
import re

def evaluator_agent(question, answer):
  llm = get_llm()
  prompt = f"""
    You are an interview evaluator.
    Question asked: {question}
    Candidate's answer: {answer}
    
    Score the answer out of 10 for:
    1. technical_accuracy
    2. communication
    3. confidence

    Respond ONLY in this exact JSON format, nothing else, no markdown backticks:
    {{
        "technical_accuracy": <number 0-10>,
        "communication": <number 0-10>,
        "confidence": <number 0-10>,
        "feedback": "<one short sentence of feedback>"
    }}
  """

  result = llm.invoke(prompt)
  raw = result.content.strip()

  # remove markdown code if the model adds them anyway
  raw = re.sub(r"```json|```", "", raw).strip()

  try:
    scores = json.loads(raw)
  except:
    # fallback if parsing fails, so app never crashes
    scores = {
      "technical_accuracy": 5,
      "communication": 5,
      "confidence": 5,
      "feedback": "Could not parse evaluation."
    }

  return scores