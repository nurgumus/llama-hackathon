import os
import sys
import requests
from typing import Optional, List, Any
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class LlamaLLM(LLM):
    """LangChain LLM implementation for Llama via vLLM"""
    
    api_url: str = None
    model_name: str = "meta-llama/Llama-3.2-3B-Instruct"  # or Llama-3.1-8B-Instruct
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    
    @property
    def _llm_type(self) -> str:
        return "llama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        headers = {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                if run_manager:
                    run_manager.on_llm_error(Exception(error_msg))
                return f"Error: {error_msg}"
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout - model may be processing"
            if run_manager:
                run_manager.on_llm_error(Exception(error_msg))
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            if run_manager:
                run_manager.on_llm_error(Exception(error_msg))
            return f"Error: {error_msg}"

class LlamaAPI:
    """Singleton class to manage Llama API connection"""
    _instance = None
    _initialized = False
    _llm = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LlamaAPI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.base_url = os.getenv("NGROK_API_URL")
            if not self.base_url:
                raise ValueError("NGROK_API_URL not found in environment variables")
            
            self.api_url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
            self._llm = LlamaLLM(api_url=self.api_url)
            self._verify_connection()
            LlamaAPI._initialized = True

    def _verify_connection(self):
        """Test the connection to the API"""
        try:
            response = self._llm._call("Merhaba! Test mesajı.", max_tokens=50)
            if not response.startswith("Error:"):
                print(f"✅ Successfully connected to Llama API at {self.base_url}")
                print(f"📝 Test response: {response[:100]}...")
            else:
                print(f"⚠️ Warning: Could not connect to Llama API at {self.base_url}")
                print(f"Error: {response}")
                print("⚠️ Continuing without verification - API may be offline")
        except Exception as e:
            print(f"⚠️ Warning: Could not connect to Llama API at {self.api_url}")
            print(f"Error: {str(e)}")
            print("⚠️ Continuing without verification - API may be offline")
            # Don't raise - allow initialization to continue

    def get_llm(self) -> LlamaLLM:
        return self._llm
        
    def get_base_url(self) -> str:
        return self.base_url

# Singleton instance - wrapped in try/except for graceful failure
try:
    llama_api = LlamaAPI()
    llama_llm = llama_api.get_llm()
    print("✅ LlamaAPI initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize LlamaAPI: {str(e)}")
    print("⚠️ Please check your .env file and ensure NGROK_API_URL is set correctly")
    print("⚠️ Make sure your ngrok tunnel is running")
    llama_api = None
    llama_llm = None