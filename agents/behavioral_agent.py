from utils import get_llm

def behavioral_agent(state, user_answer=None):
    llm = get_llm()

    asked = ""
    if state.get("interview_history"):
        asked = f"\nQuestions already asked (DO NOT repeat these):\n{state['interview_history']}"

    company = state.get("company", "a general tech company")

    # Detect if user doesn't know
    idk_phrases = ["i don't know", "idk", "not sure", "no idea", "i have no idea", "don't know"]
    is_idk = user_answer and any(phrase in user_answer.lower() for phrase in idk_phrases)

    if user_answer is None:
        prompt = f"""
        You are a friendly and encouraging HR interviewer at {company} using the STAR method.
        Role: {state['job_role']}
        {asked}
        Ask ONE new behavioral question about teamwork, challenges or leadership, reflecting values typical of {company} if you know them.
        Keep it clear and simple, not too complex.
        Make it different from any questions already asked above.
        Only ask the question, nothing else.
        """
    elif is_idk:
        prompt = f"""
        You are a friendly and encouraging HR interviewer at {company}.
        The candidate said they don't know the answer.
        {asked}
        DO NOT go deeper or ask something harder.
        Instead ask a very simple and basic behavioral question like
        "Tell me about a time you worked in a team" or similar.
        Be warm and supportive in tone.
        Only ask the question, nothing else.
        """
    else:
        prompt = f"""
        You are an HR interviewer at {company} using the STAR method.
        The candidate just answered: {user_answer}
        {asked}
        Ask ONE natural STAR-based follow-up question.
        Keep it conversational and not too deep.
        Only ask the question, nothing else.
        """

    result = llm.invoke(prompt)
    return result.content