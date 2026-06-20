import PyPDF2
from utils import get_llm

def parse_resume(pdf_path):
  reader = PyPDF2.PdfReader(pdf_path)
  text = ""
  for page in reader.pages:
    text += page.extract_text()

  llm = get_llm()
  prompt = f"Extract skills, experience and projects from this resume:\n\n{text}"
  result = llm.invoke(prompt)
  return result.content