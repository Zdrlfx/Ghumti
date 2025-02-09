from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_cpp import Llama
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

# Load Local Llama 3 Model (Make sure you have the `.gguf` model file)
LLAMA_MODEL_PATH = "models/llama-3-8B.gguf"  # Update with the actual path to your model
llm = Llama(model_path=LLAMA_MODEL_PATH, n_ctx=4096, n_batch=512, verbose=False)

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
    Your job is to provide accurate and easy-to-understand travel guidance based on available bus routes and stops.
    
    - If a user provides a **starting location** that is not a bus stop, guide them to the nearest bus stop.
    - If a user provides both a **start and destination**, find the best bus route and list the stops in order.
    - If no direct route is available, suggest alternative ways to reach the destination.
    - Use Google Maps API data to provide walking directions to the nearest stop if necessary.
    - Keep your responses **clear, concise, and user-friendly**.
    
    **Example Scenarios:**
    1. User: "How do I get from Bhaktapur Durbar Square to Kaushaltar?"
       Ghumti: "You are at Bhaktapur Durbar Square, which is not a bus stop. The nearest stop is **Suryabinayak**, about 400m away. Walk there and take the **Lagankhel-Bhaktapur Naya Baato** bus, passing through **Aadarsha, Jagati, Koteshor, Lokanthali**, and finally, you’ll reach **Kaushaltar**. Safe travels!"

    2. User: "Which bus goes to Ratnapark from Koteshor?"
       Ghumti: "From Koteshor, you can take the **Koteshor-Ratnapark** bus, stopping at **Jadibuti, Baneshwor, New Baneshwor, Singha Durbar**, and then reaching **Ratnapark**."

    **Conversation History:**
    {conversation_history}

    **Current User Question:** 
    {user_question}

    **Retrieved Context (Bus Stops & Routes):**
    {context}
    """

    trimmed_history = conversation_history[-max_history:]
    formatted_history = "\n".join([f"User: {entry['user']}\nAssistant: {entry['assistant']}" for entry in trimmed_history])

    return prompt_template.format(
        conversation_history=formatted_history,
        user_question=user_question,
        context=context_text
    )


def get_model_response(user_input):
    """Retrieves relevant context and generates a response using Llama 3."""
    global last_context

    # Retrieve relevant documents from ChromaDB
    context_text = query_vector_store(db, user_input) if last_context is None else last_context

    # Format the prompt
    prompt = format_prompt(conversation_history, user_input, context_text)

    # Run Llama 3 locally
    response = llm(prompt)["choices"][0]["text"].strip()

    # Store conversation history
    conversation_history.append({"user": user_input, "assistant": response})
    last_context = context_text  # Save last context for future queries

    return response

def main():
    """Runs the chatbot in a loop."""
    while True:
        user_question = input("You: ")
        response = get_model_response(user_question)
        print(f"Lumi: {response}")

if __name__ == "__main__":
    main()
