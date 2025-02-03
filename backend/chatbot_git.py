from openai import OpenAI
import json
from fastapi import FastAPI
from pydantic import BaseModel
import os

def load_rules(json_path):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the JSON file
    full_path = os.path.join(script_dir, json_path)
    with open(full_path, "r") as file:
        data = json.load(file)
    return data["rules"]

def search_rules(query, rules):
    results = []
    query_lower = query.lower()
    for rule in rules:
        if ("content" in rule and query_lower in rule["content"].lower()) or \
                ("title" in rule and query_lower in rule["title"].lower()):
            results.append(rule)
    return results

def ask_gpt(question, rules, client):
    results = search_rules(question, rules)
    if results:
        context = ". ".join([
            f"Section {r.get('section', 'Unknown Section')}: {r.get('content', 'No content available')}"
            for r in results
        ])
    else:
        context = "No specific matching rules found in the ruleset."

    prompt = (
        f"You are a pickleball rules expert. Answer the user's question based on the following rules:\n"
        f"{context}\n\n"
        f"User's question: {question}"
    )

    # Using the new API format
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-3.5-turbo" for a cheaper option
        messages=[
            {"role": "system", "content": "You are a pickleball rules expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# FastAPI setup
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# Add this after initializing `app`
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define request and response models
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# Load rules once during startup
rules = load_rules("pickleball_rules.json")

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Initialize the OpenAI client
    client = OpenAI(
        api_key="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"
    )
    answer = ask_gpt(request.question, rules, client)
    return ChatResponse(answer=answer)

def chatbot():
    # Initialize the OpenAI client
    client = OpenAI(
        api_key="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"
    )

    rules = load_rules("pickleball_rules.json")
    print("Pickleball Rule Bot: Ask me any question about pickleball rules! Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            print("Pickleball Rule Bot: Goodbye!")
            break
        if not user_input:
            continue

        try:
            response = ask_gpt(user_input, rules, client)
            print(f"Pickleball Rule Bot: {response}")
        except Exception as e:
            print(f"Pickleball Rule Bot: Sorry, something went wrong. {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Uncomment the following line to run the terminal chatbot
    # chatbot()
    
    # Run the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
