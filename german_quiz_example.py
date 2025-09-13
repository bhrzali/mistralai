#!/usr/bin/env python3
"""
Example usage of the German Quiz Tool

This example demonstrates how to use the generate_german_quiz tool
to create German language quizzes based on content.
"""

import os
from server import generate_german_quiz

def main():
    """Example usage of the German quiz generation tool."""
    
    # Example content about German culture
    content = """
    Deutschland ist ein Land in Mitteleuropa. Die Hauptstadt ist Berlin. 
    Deutschland hat eine reiche Geschichte und Kultur. Viele berühmte 
    Komponisten wie Bach, Beethoven und Mozart kommen aus Deutschland. 
    Das Land ist auch bekannt für seine Autos wie BMW, Mercedes und Audi.
    """
    
    print("=== German Quiz Generation Example ===\n")
    print("Content used for quiz generation:")
    print(content)
    print("\n" + "="*50 + "\n")
    
    # Set up environment variable (you would need to set this with your actual API key)
    # os.environ['GEMINI_API_KEY'] = 'your-api-key-here'
    
    try:
        # Generate quiz with 5 questions
        quiz_result = generate_german_quiz(content, num_questions=5)
        print("Generated Quiz:")
        print(quiz_result)
        
        print("\n" + "="*50)
        print("Note: The quiz has been:")
        print("1. Saved to a timestamped text file")
        print("2. Sent to the database API for storage")
        print("3. Displayed above for immediate review")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: To use this tool, you need to:")
        print("1. Install the required dependencies: pip install -r requirements.txt")
        print("2. Set your Google API key: export GEMINI_API_KEY='your-api-key'")
        print("3. Get a Google API key from: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    main()
