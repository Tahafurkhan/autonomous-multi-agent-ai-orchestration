from backend import run_travel_agent

print ("\n please enter your travel query (e.g., 'plan a 7-day trip to Japan from India'):")
user_input = input("Enter your travel query: ")
result = run_travel_agent(user_input,thread_id="user")

print ("\n--- Travel Agent Response ---")
print(result["answer"])