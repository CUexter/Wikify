import os
import logging
import json
from datetime import datetime
import litellm

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
)

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"

# Configure LiteLLM logging
# This enables LiteLLM's built-in logging capabilities
litellm.success_callback = ["file"]  # Log successful calls to a file
litellm.failure_callback = ["file"]  # Log failed calls to a file

# Set the file path for LiteLLM's logs
os.environ["LITELLM_LOG_FILE"] = os.path.join(log_directory, "litellm_logs.json")


# By default, we use Google Gemini 2.5 pro, as it shows great performance for code understanding
def call_llm(prompt: str, use_cache: bool = True) -> str:
    # Log the prompt
    logger.info(f"PROMPT: {prompt}")

    # Check cache if enabled
    if use_cache:
        # Load cache from disk
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except:
                logger.warning(f"Failed to load cache, starting with empty cache")

        # Return from cache if exists
        if prompt in cache:
            logger.info(f"RESPONSE: {cache[prompt]}")
            return cache[prompt]

    # Call the LLM if not in cache or cache disabled
    # Using LiteLLM instead of direct Google API
    try:
        model = os.getenv("LLM_MODEL", "google/gemini-2.5-pro-preview")
        # Set API key for OPENROUTER
        api_key = os.getenv("OPENROUTER_API_KEY", "")

        # Make the call using LiteLLM
        response = litellm.completion(
            model=model, messages=[{"role": "user", "content": prompt}], api_key=api_key
        )

        # Extract the response text
        response_text = response.choices[0].message.content

        # Log the response
        logger.info(f"RESPONSE: {response_text}")

        # Update cache if enabled
        if use_cache:
            # Load cache again to avoid overwrites
            cache = {}
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache = json.load(f)
                except:
                    pass

            # Add to cache and save
            cache[prompt] = response_text
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")

        return response_text

    except Exception as e:
        logger.error(f"Error calling LLM: {str(e)}")
        raise


if __name__ == "__main__":
    test_prompt = "Hello, how are you?"

    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
