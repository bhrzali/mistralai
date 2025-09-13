# MistralAI MCP Server

This is a FastMCP server with various tools including a German language quiz generator.

## Running the App

```bash
uvicorn server:app --host 127.0.0.1 --port 8000
```

## German Quiz Tool

The server includes a `generate_german_quiz` tool that creates German language multiple-choice questions based on provided content.

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google API key:
```bash
export GEMINI_API_KEY='your-google-api-key'
```

3. Set up the Quiz API endpoint (optional):
```bash
export QUIZ_API_ENDPOINT='http://127.0.0.1:8090/quizzes/parse'
```

Get your API key from: https://makersuite.google.com/app/apikey

### Usage

The tool accepts two parameters:
- `content` (string): The text content to base questions on
- `num_questions` (int): Number of questions to generate (default: 10, max: 100)

### Example

```python
from server import generate_german_quiz

content = "Deutschland ist ein Land in Mitteleuropa. Die Hauptstadt ist Berlin."
quiz = generate_german_quiz(content, num_questions=5)
print(quiz)
```

### Features

- Generates practical, application-based German grammar questions
- Includes multiple question types: fill-in-the-blank, grammar correction, word order, etc.
- Provides detailed explanations for each answer
- Follows proper German grammar rules and conventions
- Beginner-friendly but grammatically correct
- Avoids offensive or political content

### Question Types

The tool generates various types of questions:
- Fill in the blank (with multiple blanks when appropriate)
- Choose the grammatically correct sentence
- Identify the sentence with correct word order
- Select the appropriate word/phrase for context
- Find the sentence that best expresses a given meaning

### Output Format

Each quiz includes:
- Topic and explanation
- Multiple-choice questions with 4 options (A-D)
- Correct answers
- Detailed explanations in both German and English
- Grammar rules and concepts being tested

### File Saving & API Integration

The tool automatically:
1. **Saves each generated quiz** to a timestamped text file:
   - Filename format: `german_quiz_YYYYMMDD_HHMMSS.txt`
   - Includes metadata: generation time, number of questions, content source
   - Saved in the current working directory
   - UTF-8 encoding for proper German character support

2. **Sends the quiz to the database API**:
   - Endpoint: Configurable via `QUIZ_API_ENDPOINT` environment variable
   - Default: `http://127.0.0.1:8090/quizzes/parse`
   - Automatically parses and stores the quiz in the database
   - Provides feedback on API success/failure
   - Graceful fallback if API is unavailable

### API Configuration

The API client can be configured in two ways:

1. **Environment Variable** (Recommended):
   ```bash
   export QUIZ_API_ENDPOINT='http://your-api-server:port/quizzes/parse'
   ```

2. **Code Configuration**:
   Modify the `QuizAPIClient` in `quiz_api_client.py`:
   - Change the endpoint URL if needed
   - Add API key authentication if required
   - Customize content type and source identifiers