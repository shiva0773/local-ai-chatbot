from agent.agent import run_agent

question = "What is 15% of 85000?"

answer = run_agent(question)

print("User Question:", question)
print("Agent Answer:", answer)