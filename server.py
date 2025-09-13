# server.py
from datetime import datetime, timezone
from fastmcp import FastMCP
import base64
import io
import requests
from bs4 import BeautifulSoup
import urllib.parse
import google.generativeai as genai
import os
from quiz_api_client import QuizAPIClient

mcp = FastMCP(name="demo-fastmcp")

# Use the FastMCP app directly
app = mcp.http_app

# ---- Tools ----
from documents.document1 import summary as summary1, documentation as documentation1
from documents.document2 import summary as summary2, documentation as documentation2
from documents.document3 import summary as summary3, documentation as documentation3

# German Quiz Helper Functions
def german_cheat_sheet() -> str:
    """German grammar cheat sheet for quiz generation."""
    return """
    GERMAN GRAMMAR CHEAT SHEET:
    
    ARTICLES:
    - Definite: der (masc), die (fem), das (neut), die (pl)
    - Indefinite: ein (masc), eine (fem), ein (neut), keine (pl)
    - Cases: Nominativ, Akkusativ, Dativ, Genitiv
    
    ADJECTIVES:
    - Strong declension: when no article precedes
    - Weak declension: when definite article precedes
    - Mixed declension: when indefinite article precedes
    
    VERBS:
    - Regular: -en ending, stem changes in present tense
    - Irregular: strong verbs with vowel changes
    - Modal verbs: können, müssen, sollen, wollen, dürfen, mögen
    - Separable verbs: prefix separates in main clause
    
    WORD ORDER:
    - Main clause: Subject-Verb-Object
    - Subordinate clause: Subject-Object-Verb
    - Time-Manner-Place rule
    - Verb always in second position in main clause
    
    PREPOSITIONS:
    - Accusative: durch, für, gegen, ohne, um
    - Dative: aus, bei, mit, nach, seit, von, zu
    - Two-way: an, auf, hinter, in, neben, über, unter, vor, zwischen
    
    PRONOUNS:
    - Personal: ich, du, er/sie/es, wir, ihr, sie
    - Possessive: mein, dein, sein/ihr, unser, euer, ihr
    - Demonstrative: dieser, jener
    - Relative: der, die, das
    
    CONJUNCTIONS:
    - Coordinating: und, oder, aber, sondern, denn
    - Subordinating: weil, dass, wenn, als, obwohl
    """

def explanation_format() -> str:
    return """
    strictly follow the the following format for explanation otherwise you will be penalized.
    TRANSLATION: [English translation of the German question]
    AI_ANSWER: [Solve the quesiton and give the correct answer but don't include the option letter in the answer]
    AI_CORRECTION: [If the sentence with the provided options is incorrect, provide the complete correct German sentence and additionally you must explain your reasoning. If correct, write "No correction needed"] 
    EXPLANATION: [Brief explantion of the grammar rule in simple terms in English explaining which answer is correct and why. Make your explanation beginner friendly. Don't include the option letter in the explanation]
    ADDITIONAL_EXAMPLES: example2, example3, example4
    """

# Initialize Google AI (requires API key)
def initialize_gemini():
    """Initialize Google Gemini AI client."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

@mcp.tool
def function_app_documentation(dummy: str = "") -> str:
    f"""
    This function takes a dummy parameter of string type and returns the documentation for the following summary
    summary: {summary1}
    """
    return documentation1

@mcp.tool
def data_platform_infrastructure_documentation(dummy: str = "") -> str:
    f"""
    This function takes a dummy parameter of string type and returns the documentation for the following summary
    summary: {summary2}
    """
    return documentation2

@mcp.tool
def microsoft_fabric_infrastructure_documentation(dummy: str = "") -> str:
    f"""
    This function takes a dummy parameter of string type and returns the documentation for the following summary
    summary: {summary3}
    """
    return documentation3

@mcp.tool
def hello(name: str) -> str:
    """Return a friendly greeting with the provided name."""
    return f"Hello, {name}! 👋"

@mcp.tool
def sum_numbers(numbers: list[float]) -> float:
    """Sum a list of numbers. Takes a list of float values."""
    return sum(numbers)

@mcp.tool
def multiply_numbers(numbers: list[float]) -> float:
    """Multiply a list of numbers. Takes a list of float values."""
    result = 1.0
    for num in numbers:
        result *= num
    return result

@mcp.tool
def get_time(dummy: str = "") -> str:
    """Get the current UTC time in ISO 8601 format. Takes a dummy paramter of string type.
       Only use this tool if asked for the time.
    """
    return datetime.now(timezone.utc).isoformat()

@mcp.tool
def interesting_fact(dummy: str = "") -> str:
    """Return an interesting fact. Takes a dummy paramter of string type."""
    return "The moon is 238,855 miles away from Earth."

@mcp.tool
def solve_sudoku(puzzle: str) -> str:
    """Solve a Sudoku puzzle. Takes a puzzle as a string of 81 characters where '.' represents empty cells.
    Example: '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
    Returns the solved puzzle in a nicely formatted grid."""
    
    def is_valid(board, row, col, num):
        # Check row
        for x in range(9):
            if board[row][x] == num:
                return False
        
        # Check column
        for x in range(9):
            if board[x][col] == num:
                return False
        
        # Check 3x3 box
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        return True
    
    def solve(board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == '.':
                    for num in range(1, 10):
                        if is_valid(board, i, j, str(num)):
                            board[i][j] = str(num)
                            if solve(board):
                                return True
                            board[i][j] = '.'
                    return False
        return True
    
    def format_board(board):
        result = "┌─────────┬─────────┬─────────┐\n"
        for i in range(9):
            if i % 3 == 0 and i != 0:
                result += "├─────────┼─────────┼─────────┤\n"
            row = "│"
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    row += "│"
                row += f" {board[i][j]} "
            row += "│\n"
            result += row
        result += "└─────────┴─────────┴─────────┘"
        return result
    
    # Validate input
    if len(puzzle) != 81:
        return "Error: Puzzle must be exactly 81 characters long (9x9 grid)"
    
    # Convert string to 2D array
    board = []
    for i in range(9):
        row = []
        for j in range(9):
            char = puzzle[i * 9 + j]
            if char not in '123456789.':
                return f"Error: Invalid character '{char}' at position {i*9+j}. Only digits 1-9 and '.' are allowed."
            row.append(char)
        board.append(row)
    
    # Make a copy for solving
    board_copy = [row[:] for row in board]
    
    # Try to solve
    if solve(board_copy):
        original = format_board(board)
        solution = format_board(board_copy)
        return f"Original Puzzle:\n{original}\n\nSolved Puzzle:\n{solution}"
    else:
        original = format_board(board)
        return f"Original Puzzle:\n{original}\n\n❌ This puzzle has no solution!"

@mcp.tool
def browse_url(url: str, max_length: int = 5000) -> str:
    """Browse and extract content from a URL. Takes a URL and optional max content length (default 2000 characters).
    Returns the main content of the webpage with title, text content, and metadata."""
    
    def clean_text(text):
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Cookie Policy',
            r'Privacy Policy',
            r'Terms of Service',
            r'Subscribe to our newsletter',
            r'Follow us on',
            r'Share this article',
            r'Advertisement',
            r'Advertisements',
            r'Related articles',
            r'You might also like',
            r'Recommended for you'
        ]
        
        import re
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_main_content(soup):
        """Extract the main content from the webpage"""
        # Try to find the main content area
        content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '#content',
            '#main'
        ]
        
        content_text = ""
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    # Remove script and style elements
                    for script in element(["script", "style", "nav", "footer", "header", "aside"]):
                        script.decompose()
                    
                    text = element.get_text()
                    if len(text) > len(content_text):
                        content_text = text
                break
        
        # If no main content found, get all text
        if not content_text:
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "menu"]):
                element.decompose()
            content_text = soup.get_text()
        
        return clean_text(content_text)
    
    def extract_metadata(soup):
        """Extract metadata from the webpage"""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '').strip()
        
        # Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title:
            metadata['og_title'] = og_title.get('content', '').strip()
        
        # Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            metadata['og_description'] = og_desc.get('content', '').strip()
        
        return metadata
    
    try:
        # Validate URL
        if not url or not url.strip():
            return "Error: URL cannot be empty"
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate max_length
        if max_length < 100 or max_length > 10000:
            max_length = 2000
        
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract metadata
        metadata = extract_metadata(soup)
        
        # Extract main content
        content = extract_main_content(soup)
        
        # Truncate content if too long
        if len(content) > max_length:
            content = content[:max_length] + "... [Content truncated]"
        
        # Format result
        result = f"🌐 **URL Content**: {url}\n\n"
        
        # Add title
        title = metadata.get('title') or metadata.get('og_title') or "No title found"
        result += f"📄 **Title**: {title}\n\n"
        
        # Add description if available
        description = metadata.get('description') or metadata.get('og_description')
        if description:
            result += f"📝 **Description**: {description}\n\n"
        
        # Add content
        result += f"📖 **Content** ({len(content)} characters):\n\n{content}\n\n"
        
        # Add metadata info
        result += f"ℹ️ **Page Info**:\n"
        result += f"   - Status: {response.status_code}\n"
        result += f"   - Content-Type: {response.headers.get('content-type', 'Unknown')}\n"
        result += f"   - Content Length: {len(response.content)} bytes\n"
        
        if metadata.get('keywords'):
            result += f"   - Keywords: {metadata['keywords']}\n"
        
        return result
        
    except requests.exceptions.Timeout:
        return f"Error: Request timed out for URL: {url}"
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to URL: {url}"
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP {e.response.status_code} for URL: {url}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error processing webpage: {str(e)}"

@mcp.tool
def generate_german_quiz(content: str, num_questions: int = 10) -> dict:
    """Generate German language quiz questions based on provided content.
    
    Args:
        content: The content/text to base the questions on
        num_questions: Number of questions to generate (default 10, max 100)
    
    Returns:
        Dictionary containing:
        - api_response: Response from the quiz API (or None if failed)
        - quiz_id: ID of the created quiz (if successful)
        - quiz_link: Link to access the quiz (format: http://localhost:8090/quizzes/<quiz_id>)
        - status: "success" or "error" 
        - error: Error message if something went wrong (optional)
    """
    try:
        # Validate inputs
        if not content or not content.strip():
            return {
                "api_response": None,
                "quiz_id": None,
                "quiz_link": None,
                "status": "error",
                "error": "Content cannot be empty"
            }
        
        if num_questions < 1 or num_questions > 100:
            num_questions = 10
        
        # Initialize Gemini AI
        try:
            model = initialize_gemini()
        except ValueError as e:
            return {
                "api_response": None,
                "quiz_id": None,
                "quiz_link": None,
                "status": "error",
                "error": f"{str(e)}. Please set the GOOGLE_API_KEY environment variable."
            }
        
        # Create the system prompt
        system_prompt = f"""
            You are an experienced German language instructor with 20 years of teaching experience.
            Your task is to create EXACTLY {num_questions} PRACTICAL, application-based multiple-choice questions based on the following content:

            Content for reference:
            {content}

            Guidelines:
            1. You MUST generate EXACTLY {num_questions} questions - no more, no less.
            2. Focus on real-world usage, not theory.
            3. Use authentic, natural German sentences.
            4. Across the whole set, include at least one of each question type:
            • Fill in the blank (For fill in the blanks, sentence can have multiple blanks). But make sure not to give unnecessary blanks.
            • Choose the grammatically correct sentence  
            • Identify the sentence with the correct word order  
            • Select the appropriate word/phrase for the context  
            • Find the sentence that best expresses the given meaning
            5. Each question must have exactly one correct answer and three plausible distractors.
            6. Generate varied questions.
            7. The topic should be a correct german grammar topic and concise
            8. If the content is not relevant to the german grammar, generate questions related to that content in german language.
            9. Avoid generating obscene or offensive questions.
            10. Avoid generating any political or religious questions.
            11. Make sure the questions are beginner friendly but grammatically correct.

            **GRAMMAR RULES:**
            Make sure that you are following the correct grammar rules for:
            - Articles, adjectives, and nouns (gender, case, number agreement)
            - Verb conjugations and tenses
            - Word order and sentence structure
            - Prepositions and their required cases
            - Pronouns and their declensions
            - Subordinate clause constructions
            - Adjectives and their cases
            - Adverbs and their cases
            - Prepositions and their cases
            - Pronouns and their cases
            - Conjunctions and their cases
            - Interjections and their cases
            - Adverbs and their cases
            - Prepositions and their cases
            - Pronouns and their cases
            - Conjunctions and their cases
            - Interjections and their cases
            - Commas and their rules

            Refer to the following German cheat sheet for more information:
            {german_cheat_sheet()}

            **CRITICAL FORMAT REQUIREMENTS:**
            1. First, output the topic in this EXACT format given below otherwise you will be penalized:
            
            TOPIC: <grammar topic in german>
            EXPLANATION: <brief explanation of why this topic is appropriate>

            2. Then for each question from 1 to {num_questions}, use this EXACT format otherwise you will be penalized:

            Question 1
            Prompt: <question text in German>
            A) <option A>
            B) <option B>
            C) <option C>
            D) <option D>
            Answer: <single uppercase letter A–D>
            Explanation:
            ***
            {explanation_format()}
            ***


            Question 2
            Prompt: <question text in German>
            A) <option A>
            B) <option B>
            C) <option C>
            D) <option D>
            Answer: <single uppercase letter A–D>
            Explanation:
            ***
            {explanation_format()}
            ***

            [Continue for all {num_questions} questions]

            Format Rules:
            • You MUST generate EXACTLY {num_questions} questions
            • Each question MUST start with "Question N" where N is the question number
            • Each question MUST have all components: Prompt, A-D options, Answer, and Explanation
            • Each question MUST have only 4 options A, B, C, D. If you follow the format you will be rewarded with big bonus.
            • Don't forget to enclose the explanation in *** and ***.
            • Don't forget to provide the explanation according to the format.
            • Keep the labels ("Prompt:", "A)", "Answer:", etc.) exactly as written
            • Place one blank line between questions
            • No extra blank lines inside a question block
            • Ensure German diacritics are correct
            • Do not add any markdown, bullets, or headers/footers

            Begin generating the questions now.
        """
        
        # Generate content using Gemini
        response = model.generate_content(system_prompt)
        
        if not response.text:
            return {
                "api_response": None,
                "quiz_id": None,
                "quiz_link": None,
                "status": "error",
                "error": "No questions were generated. Please try again."
            }
        
        # Send to API and return response
        try:
            from datetime import datetime
            
            # Prepare the full quiz text with metadata
            full_quiz_text = f"German Quiz Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            full_quiz_text += f"Number of Questions: {num_questions}\n"
            full_quiz_text += f"Content Source: {content[:100]}...\n"
            full_quiz_text += "="*80 + "\n\n"
            full_quiz_text += response.text
            
            # Send to API
            try:
                api_client = QuizAPIClient()
                api_response = api_client.send_quiz(full_quiz_text)
                
                # Extract quiz_id from API response
                quiz_id = None
                quiz_link = None
                
                if isinstance(api_response, dict):
                    # Try common field names for quiz ID
                    quiz_id = (api_response.get('quiz_id') or 
                             api_response.get('id') or 
                             api_response.get('quizId') or
                             api_response.get('data', {}).get('id') if isinstance(api_response.get('data'), dict) else None)
                
                if quiz_id:
                    quiz_link = f"http://localhost:8090/quizzes/{quiz_id}"
                
                # Return API response with quiz info
                result = {
                    "api_response": api_response,
                    "quiz_id": quiz_id,
                    "quiz_link": quiz_link,
                    "status": "success"
                }
                return result
                
            except Exception as api_error:
                # Return error if API fails
                result = {
                    "api_response": None,
                    "quiz_id": None,
                    "quiz_link": None,
                    "status": "error",
                    "error": f"Failed to send to API: {str(api_error)}"
                }
                return result
            
        except Exception as e:
            return {
                "api_response": None,
                "quiz_id": None,
                "quiz_link": None,
                "status": "error",
                "error": f"Error processing quiz: {str(e)}"
            }
        
    except Exception as e:
        return {
            "api_response": None,
            "quiz_id": None,
            "quiz_link": None,
            "status": "error",
            "error": f"Error generating German quiz: {str(e)}"
        }

# ---- Resource (read-only) ----
@mcp.resource("time://now")
def current_time() -> str:
    """Current UTC time in ISO 8601."""
    return datetime.now(timezone.utc).isoformat()

# ---- Prompt (reusable template) ----
@mcp.prompt
def summarize(text: str) -> str:
    """Return a prompt asking an LLM to summarize `text`."""
    return f"Summarize briefly:\n\n{text}"

if __name__ == "__main__":
    # Default transport is stdio; great for local MCP hosts
    # mcp.run()
    # To run as HTTP instead, use:
    mcp.run(transport="http", host="127.0.0.1", port=8000, sse_path="/mcp", message_path="/mcp")
