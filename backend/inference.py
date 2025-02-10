from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
import os

# Define ChromaDB storage path
CHROMA_PATH = "chroma"

# Initialize conversation history
conversation_history = []
last_context = None  # Keep track of the last retrieved context

# Load Hugging Face embeddings (Free & Local)
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load ChromaDB
def load_vector_store():
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

db = load_vector_store()

# Load Local Llama 3 Model via Ollama
llm = OllamaLLM(model="llama3")  # Uses Ollama instead of llama.cpp

def query_vector_store(db, query_text):
    """Retrieves relevant context from the vector database."""
    results = db.similarity_search_with_relevance_scores(query_text, k=5)
    if len(results) == 0 or results[0][1] < 0.3:
        return "No relevant information found."
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    return context_text

def format_prompt(conversation_history, user_question, context_text, max_history=3):
    """Formats the prompt for Llama 3 with chat history and retrieved context."""
    prompt_template = """
    You are Ghumti, an intelligent assistant that helps people navigate local bus routes in Kathmandu Valley.
    Your sole purpose is to provide accurate and easy-to-understand travel guidance using only public buses.
    Rules:

    -If a user provides a location that is not a bus stop, guide them to the nearest one.
    -If a user provides both a start and destination, find the best bus route and list the stops in order.
    -If no direct bus is available, suggest alternative routes using transfers between buses.
    -Use Google Maps API data to provide walking directions to the nearest bus stop when needed.
    -Do not suggest taxis, ride-sharing, private vehicles, or any transport other than buses.
    -Keep responses clear, concise, and user-friendly.
    -Ignore unrelated questions, such as those about food recipes.

Example Scenarios:

    User: "How do I get from Bhaktapur Durbar Square to Kaushaltar?"
    Ghumti: "Bhaktapur Durbar Square is not a bus stop. The nearest stop is Suryabinayak, about 400m away. Walk there and take the Lagankhel-Bhaktapur Naya Baato bus. This route stops at Aadarsha, Jagati, Koteshor, Lokanthali, and finally, Kaushaltar. Safe travels!"

    User: "Which bus goes to Ratnapark from Koteshor?"
    Ghumti: "From Koteshor, take the Koteshor-Ratnapark bus. It stops at Jadibuti, Baneshwor, New Baneshwor, Singha Durbar, and finally, Ratnapark."
    *Conversation History:*
    {conversation_history}

    *Current User Question:* 
    {user_question}

    *Retrieved Context (Bus Stops & Routes):*
    {context}
    """

    trimmed_history = conversation_history[-max_history:]
    formatted_history = "\n".join([f"User: {entry['user']}\nAssistant: {entry['assistant']}" for entry in trimmed_history])

    return prompt_template.format(
        conversation_history=formatted_history,
        user_question=user_question,
        context=context_text
    )

def get_model_response(user_input, conversation_history):
    """Retrieves relevant context and generates a response using Ollama Llama 3."""
    global last_context

    # Retrieve relevant documents from ChromaDB
    context_text = query_vector_store(db, user_input) if last_context is None else last_context

    # Format the prompt
    prompt = format_prompt(conversation_history, user_input, context_text)

    # Run Llama 3 locally via Ollama
    response = llm.invoke(prompt)  # Uses Ollama instead of llama.cpp

    # Store conversation history
    conversation_history.append({"user": user_input, "assistant": response})
    last_context = context_text  # Save last context for future queries

    return response

def main():
    """Runs the chatbot in a loop."""
    while True:
        user_question = input("You: ")
        response = get_model_response(user_question)
        print(f"Ghumti: {response}")

if __name__ == "__main__":
    main()