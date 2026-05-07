import requests
import json
from typing import Optional, Dict, List

class EPPChatbotAPI:
    """
    Electric Power Projects Chatbot API Client
    Integrates with Qwen chatbot for domain-specific queries
    """
    
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_completion(self, 
                      prompt: str, 
                      system_context: str,
                      model: str = "qwen-max",
                      temperature: float = 0.7,
                      max_tokens: int = 2000) -> Dict:
        """
        Get completion from Qwen API
        
        Args:
            prompt: User's query
            system_context: Domain-specific context
            model: Model to use (qwen-max, qwen-plus, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary containing API response
        """
        endpoint = f"{self.base_url}/services/aigc/text-generation/generation"
        
        payload = {
            "model": model,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": system_context
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "message",
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            }
    
    def get_chat_response(self, 
                         messages: List[Dict], 
                         system_context: str) -> Dict:
        """
        Get chat response with conversation history
        
        Args:
            messages: List of conversation messages
            system_context: Domain context
            
        Returns:
            API response dictionary
        """
        endpoint = f"{self.base_url}/services/aigc/text-generation/generation"
        
        full_messages = [
            {"role": "system", "content": system_context}
        ]
        full_messages.extend(messages)
        
        payload = {
            "model": "qwen-max",
            "input": {
                "messages": full_messages
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if "output" in result and "choices" in result["output"]:
                return {
                    "success": True,
                    "response": result["output"]["choices"][0]["message"]["content"],
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected API response format",
                    "data": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

# Usage example
if __name__ == "__main__":
    # Initialize API client
    api_client = EPPChatbotAPI(api_key="your-api-key-here")
    
    # Example query
    query = "What are the key components of BoP services in thermal power plants?"
    
    system_context = """
    You are an expert in Electric Power Projects specializing in:
    - Thermal and Gas Power Plant BoP Services
    - Solar Power Plant Turnkey Solutions
    - Ground-mounted Solar Installations
    Provide detailed, professional answers.
    """
    
    response = api_client.get_completion(query, system_context)
    
    if response["success"]:
        print(response["data"])
    else:
        print(f"Error: {response['error']}")
