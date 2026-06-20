from utils import get_llm

def technical_agent(state, user_answer=None, include_code=False):
    llm = get_llm()

    asked = ""
    if state.get("interview_history"):
        asked = f"\nQuestions already asked (DO NOT repeat these):\n{state['interview_history']}"

    company = state.get("company", "a general tech company")

    idk_phrases = ["i don't know", "idk", "not sure", "no idea", "i have no idea", "don't know"]
    is_idk = user_answer and any(phrase in user_answer.lower() for phrase in idk_phrases)

    code_instruction = ""
    if include_code:
        code_instruction = """
        YOU MUST include a short code snippet (5-10 lines) related to the candidate's skills.
        Format EXACTLY like this:
        [Brief question text]

```language
        code here
```

        [What should they explain, fix, or predict about this code]
        """

    if user_answer is None:
        prompt = f"""
        You are a friendly and encouraging senior technical interviewer for {state['job_role']} at {company}.
        Candidate skills: {state['resume_data']}
        {asked}
        {code_instruction}
        Ask ONE new specific technical interview question based on their skills.
        Keep it clear and straightforward. Not too complex.
        Only ask the question, nothing else.
        """
    elif is_idk:
        prompt = f"""
        You are a friendly and encouraging senior technical interviewer for {state['job_role']} at {company}.
        The candidate said they don't know the answer.
        {asked}
        DO NOT go deeper or ask a harder question.
        Instead ask a much simpler and basic question related to {state['job_role']}.
        Be warm and encouraging in tone.
        Only ask the question, nothing else.
        """
    else:
        prompt = f"""
        You are a senior technical interviewer at {company}.
        The candidate just answered: {user_answer}
        {asked}
        {code_instruction}
        Ask ONE natural follow-up question based on their answer.
        Keep it conversational, not too deep or complex.
        Only ask the question, nothing else.
        """

    result = llm.invoke(prompt)
    return result.content