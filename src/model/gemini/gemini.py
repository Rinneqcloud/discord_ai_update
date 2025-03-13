from loguru import logger
import os
import google.generativeai as genai
from typing import Tuple


def ask_gemini(api_key: str, model: str, user_message: str, prompt: str, proxy: str = "") -> Tuple[bool, str]:
    """
    Send a message to Google Gemini and get a response.

    Args:
        api_key (str): Gemini API key
        model (str): Gemini model to use (e.g., "gemini-2.0-flash")
        user_message (str): The message to send to Gemini
        prompt (str): System prompt/instructions
        proxy (str): Proxy in format user:pass@ip:port or ip:port

    Returns:
        Tuple[bool, str]: Success status and Gemini's response or error message
    """
    try:
        # Set environment variables
        os.environ["GEMINI_API_KEY"] = api_key

        # Configure proxy if provided
        if proxy:
            logger.info(f"Using proxy: {proxy} for Gemini")
            # Format proxy URL with scheme if not present
            if not proxy.startswith(("http://", "https://")):
                proxy = f"http://{proxy}"
            
            # Configure client with proxy
            # Note: as of now, genai doesn't have direct proxy support in Client,
            # so we're setting the HTTP_PROXY environment variable
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy

        # Configure API key
        genai.configure(api_key=api_key)

        # Create generation config
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Prepare content for the request
        messages = []
        
        # Add system prompt if provided
        if prompt:
            messages.append({"role": "user", "parts": [prompt]})
        
        # Add user message
        messages.append({"role": "user", "parts": [user_message]})
        
        # Get Gemini model
        model = genai.GenerativeModel(model_name=model)
        
        # Generate response
        response = model.generate_content(messages, generation_config=generation_config)
        
        return True, response.text

    except Exception as e:
        error_message = str(e)
        logger.error(f"Gemini Error: {error_message}")
        
        if "quota" in error_message.lower() or "billing" in error_message.lower():
            return False, "Your Gemini API key has no remaining quota."
        
        if "rate" in error_message.lower() and "limit" in error_message.lower():
            return False, "Gemini rate limit reached, please try again later."
        
        return False, f"Gemini Error occurred: {error_message}" 