from inference import get_model_response

def main():
    """Runs the chatbot in a loop."""
    conversation_history = []
    print("Welcome to Ghumti Bus Assistant! Type 'exit' to quit.")

    while True:
        user_question = input("You: ")
        if user_question.lower() == "exit":
            break

        response = get_model_response(user_question, conversation_history)
        print(f"Ghumti: {response}")

if __name__ == "__main__":
    main()