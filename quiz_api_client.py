#!/usr/bin/env python3
"""
Quiz API Client for sending generated quizzes to the database API
"""

import requests
import sys
import os
from typing import Optional, Dict, Any

class QuizAPIClient:
    """Client for interacting with the German Quiz API"""
    
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the API client
        
        Args:
            endpoint: The API endpoint URL (defaults to QUIZ_API_ENDPOINT env var)
            api_key: Optional API key for authentication
        """
        self.endpoint = endpoint or os.getenv('QUIZ_API_ENDPOINT', 'http://127.0.0.1:8090/quizzes/parse')
        self.api_key = api_key
    
    def send_quiz(self, quiz_text: str, content_type: str = "german_quiz", source: str = "mcp-server") -> Dict[str, Any]:
        """
        Send quiz text to the API for parsing and storage
        
        Args:
            quiz_text: The generated quiz text
            content_type: Type of content being sent
            source: Source identifier for the quiz
            
        Returns:
            Dictionary containing the API response
            
        Raises:
            requests.RequestException: If the API call fails
        """
        payload = {
            "text": quiz_text,
            "content_type": content_type,
            "source": source
        }
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = self.api_key
        
        try:
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            
            # Try to return JSON response, fallback to text
            try:
                return resp.json()
            except ValueError:
                return {"status": "success", "response": resp.text[:1000]}
                
        except requests.HTTPError as e:
            error_msg = f"HTTP error: {e}"
            if hasattr(e.response, 'text'):
                error_msg += f" — body: {e.response.text[:1000]}"
            raise requests.RequestException(error_msg)
        except requests.RequestException as e:
            raise requests.RequestException(f"Request failed: {e}")

def main():
    """Example usage of the QuizAPIClient"""
    
    # Example quiz text
    quiz_text = """German Quiz Generated on: 2025-09-13 14:22:54
Number of Questions: 5
Content Source: Deutschland ist ein Land in Mitteleuropa...
================================================================================

TOPIC: Das Perfekt
EXPLANATION: Dieses Thema ist angemessen...

Question 1
Prompt: Gestern ______ ich meine Hausaufgaben _______.
A) bin ... gemacht
B) habe ... gemacht
C) bin ... machen
D) habe ... machen
Answer: B
Explanation:
***
TRANSLATION: Yesterday I did my homework.
AI_ANSWER: habe ... gemacht
AI_CORRECTION: No correction needed
EXPLANATION: The verb "machen" takes an accusative object and forms the Perfekt with "haben".
ADDITIONAL_EXAMPLES: Er hat einen Kuchen gebacken., Wir haben ein Buch gelesen.
***
"""

    # Initialize client
    client = QuizAPIClient()
    
    try:
        result = client.send_quiz(quiz_text)
        print(f"✅ Quiz sent successfully!")
        print(f"Response: {result}")
        
    except requests.RequestException as e:
        print(f"❌ Failed to send quiz: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
