from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional

class InterviewState(TypedDict):
  job_role: str
  resume_data: str
  round: str
  question: str
  answer: str
  evaluation: str
  interview_history: str

from agents.resume_parser import parse_resume
from agents.interview_manager import interview_manager
from agents.technical_agent import technical_agent
from agents.behavioral_agent import behavioral_agent
from agents.evaluator_agent import evaluator_agent
from agents.feedback_agent import feedback_agent

def run_manager(state):
  decision = interview_manager(state)
  return {"round": decision}

def run_technical(state):
  question = technical_agent(state)
  return {"question": question}

def run_behavioral(state):
  question = behavioral_agent(state)
  return {"question": question}

def run_evaluator(state):
  evaluation = evaluator_agent(state['question'], state['answer'])
  return {"evaluation": evaluation, "interview_history": evaluation}

def run_feedback(state):
  report = feedback_agent(state)
  return {"interview_history": report}

# Route based on manager decision
def route(state):
  if "Technical" in state['round']:
    return "technical"
  return "behavioral"

# Build the graph

builder = StateGraph(InterviewState)

builder.add_node("manager", run_manager)
builder.add_node("technical", run_technical)
builder.add_node("behavioral", run_behavioral)
builder.add_node("evaluator", run_evaluator)
builder.add_node("feedback", run_feedback)

builder.set_entry_point("manager")
builder.add_conditional_edges("manager", route, {
  "technical": "technical",
  "behavioral": "behavioral"
})

builder.add_edge("technical", "evaluator")
builder.add_edge("behavioral", "evaluator")
builder.add_edge("evaluator", "feedback")
builder.add_edge("feedback", END)

graph = builder.compile()