import os
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# --- Configuration (Must match Azure AI Deployment) ---
# Fetch configuration from environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Check if essential variables are set
if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, DEPLOYMENT_NAME]):
    print("Error: Required environment variables (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME) are not set.")
    exit()

# Initialize the Azure OpenAI Client
# Note: The 'api_version' is necessary when initializing the AzureOpenAI client.
# This version is a specific date, not the general API version.
try:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version="2024-05-01-preview" # Use a stable, recent API version
    )
except Exception as e:
    print(f"Error initializing AzureOpenAI client: {e}")
    exit()


# --- Function to call the LLM with exponential backoff ---

def generate_response_with_retry(prompt: str, max_retries: int = 5) -> str:
    """
    Sends a prompt to the Azure OpenAI model and handles potential transient errors
    using exponential backoff.
    """
    conversation_history = [
        {"role": "system", "content": "You are a helpful and friendly AI assistant running on Azure AI Foundry. Keep your answers concise and accurate."},
        {"role": "user", "content": prompt}
    ]

    for attempt in range(max_retries):
        try:
            print(f"Attempting to generate content (Attempt {attempt + 1})...")
            
            # The key difference for Azure is using 'model' parameter (deployment name)
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=conversation_history,
                temperature=0.7,
                max_tokens=500
            )

            # Extract the text content
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            
            return "Error: Model returned an empty response."

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff (1s, 2s, 4s, 8s...)
                print(f"API call failed with error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return f"Error: Failed to generate response after {max_retries} attempts. Last error: {e}"
    
    return "Unknown error occurred during processing."

# --- Example Usage ---

if __name__ == "__main__":
    user_prompt = "Explain the difference between Azure AI Foundry and Azure OpenAI Service in two sentences."
    print(f"\nUser Query: {user_prompt}")
    
    generated_text = generate_response_with_retry(user_prompt)
    
    print("\n--- AI Response ---")
    print(generated_text)
    print("-------------------\n")
    
    # You can also use Google Search grounding, but that functionality
    # requires a specific setup that isn't compatible with the
    # Azure OpenAI Service API structure used here.