"""
Groq LLM Integration for Istanbul Neighborhood Agent
Using llama-3.1-8b-instant model
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GroqLLM:
    """Wrapper for Groq API with Llama models"""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client
        
        Args:
            model_name: Model to use (default: llama-3.1-8b-instant)
                       Other options: llama-3.2-90b-text-preview, llama-3.1-70b-versatile
        """
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please add it to your .env file")
        
        self.client = Groq(api_key=self.api_key)
        self.model_name = model_name
        
        print(f"✅ Groq API initialized with model: {model_name}")
    
    def _call(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.1, **kwargs) -> str:
        """
        Call Groq API with a prompt
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Temperature for sampling (0.0-2.0)
            
        Returns:
            Response text from the model
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=kwargs.get('top_p', 1),
                stream=False,
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            error_msg = f"Groq API error: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Error: {error_msg}"
    
    def test_connection(self):
        """Test the Groq API connection"""
        try:
            response = self._call("Say 'Hello, I'm working!' in one sentence.", max_tokens=50)
            if not response.startswith("Error:"):
                print(f"✅ Successfully connected to Groq API")
                print(f"📝 Test response: {response}")
                return True
            else:
                print(f"⚠️ Warning: {response}")
                return False
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False


# Initialize Groq LLM
try:
    groq_llm = GroqLLM(model_name="llama-3.1-8b-instant")
    groq_llm.test_connection()
    print("✅ GroqLLM initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize GroqLLM: {str(e)}")
    print("⚠️ Please check your .env file and ensure GROQ_API_KEY is set correctly")
    print("⚠️ Get your API key from: https://console.groq.com/keys")
    groq_llm = None
