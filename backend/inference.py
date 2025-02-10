from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import requests

# Define the prompt template
template = """
answer the question below.

Here is the conversation history: {context}

question: {question}

Answer: 
"""

def format_prompt(conversation_history, user_question, context_text, max_history=3):
    """Formats the prompt with the conversation history and context."""
    prompt_template = """
    You are Ghumti, an intelligent assistant that helps people navigate local bus routes in Kathmandu Valley.
    Your job is to provide accurate and easy-to-understand travel guidance based on available bus routes and stops.
    
    - If a user provides a **starting location** that is not a bus stop, guide them to the nearest bus stop.
    - If a user provides both a **start and destination**, find the best bus routes and list multiple options for them.
    - If no direct route is available, suggest alternative ways to reach the destination.
    - Use Google Maps API data to provide walking directions to the nearest stop if necessary.
    - Keep your responses **clear, concise, and user-friendly**.

    **Example Scenarios:**
    1. User: "How do I get from Bhaktapur Durbar Square to Kaushaltar?"
       Ghumti: "You are at Bhaktapur Durbar Square, which is not a bus stop. The nearest stop is **Suryabinayak**, about 400m away. Walk there and take the **Lagankhel-Bhaktapur Naya Baato** bus, passing through **Aadarsha, Jagati, Koteshor, Lokanthali**, and finally, you’ll reach **Kaushaltar**. You can also take the **Bhaktapur-Kathmandu** bus, passing through **Jadibuti, Baneshwor, New Baneshwor**, and finally reaching **Kaushaltar**."

    2. User: "Which bus goes to Ratnapark from Koteshor?"
       Ghumti: "From Koteshor, you can take the **Koteshor-Ratnapark** bus, stopping at **Jadibuti, Baneshwor, New Baneshwor, Singha Durbar**, and then reaching **Ratnapark**. Alternatively, you can take the **Lagankhel-Koteshor** bus and transfer at **New Baneshwor** to another bus heading to **Ratnapark**."

    **Conversation History:**
    {conversation_history}

    **Current User Question:** 
    {user_question}

    **Retrieved Context (Bus Stops & Routes):**
    {context}
    
    Provide **multiple route suggestions** if applicable, including transfers or walking directions where necessary.
    """
    trimmed_history = conversation_history[-max_history:]
    formatted_history = "\n".join([f"User: {entry['user']}\nAssistant: {entry['assistant']}" for entry in trimmed_history])

    return prompt_template.format(
        conversation_history=formatted_history,
        user_question=user_question,
        context=context_text
    )


# Initialize the OllamaLLM model
model = OllamaLLM(model="llama3")

def handle_conversation():
    context = ""
    conversation_history = []  # Track conversation history
    print("Welcome to the chatbot, type 'exit' to quit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Format the prompt with the current conversation context
        prompt = format_prompt(conversation_history, user_input, context)

        # Get the model's response (Pass the prompt string directly)
        result = model.invoke(prompt)  # Fix: Pass the formatted string directly

        # Extract and process multiple route suggestions
        route_suggestions = result.split("Alternatively") if "Alternatively" in result else [result]

        # Update the context properly
        context = f"User: {user_input}\nAI:\n" + "\n".join(route_suggestions)

        # Store the conversation history
        conversation_history.append({"user": user_input, "assistant": result})

        # Print all route suggestions properly formatted
        print("Bot:\n" + "\n\n".join(route_suggestions))


MAPS_API_URL = "http://127.0.0.1:8000/directions/"

def fetch_directions(origin, destination):
    params = {"origin": origin, "destination": destination, "alternatives": True}
    response = requests.get(MAPS_API_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_model_response(user_input):
    global last_context

    # Extract origin and destination from user input (use NLP for better extraction)
    if "to" in user_input:
        parts = user_input.split(" to ")
        if len(parts) == 2:
            origin, destination = parts[0].strip(), parts[1].strip()
            directions = fetch_directions(origin, destination)

            if directions:
                response_text = "Here are the best routes:\n\n"
                for i, route in enumerate(directions["routes"]):
                    response_text += f"🚏 Route {i+1} ({route['summary']}):\n"
                    for step in route["steps"]:
                        response_text += f"- {step['instruction']} ({step['distance']}, {step['duration']})\n"
                    response_text += "\n"
                
                return response_text
            else:
                return "Sorry, I couldn't find any routes for that journey."

    return "I can help with bus routes! Try asking: 'How do I get from Koteshor to Ratnapark?'"


if __name__ == "__main__":
    handle_conversation()

