from graph import graph

result = graph.invoke({
    "job_role": "Frontend Developer",
    "resume_data": "Skills: React, JavaScript, Tailwind CSS",
    "answer": "I use useState for local state and useEffect for side effects",
    "interview_history": "",
    "round": "",
    "question": "",
    "evaluation": ""
})

print(result['interview_history'])