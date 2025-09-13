# server.py
from datetime import datetime, timezone
from fastmcp import FastMCP
import cv2
import numpy as np
from PIL import Image
import base64
import io
import requests
from bs4 import BeautifulSoup
import urllib.parse

mcp = FastMCP(name="demo-fastmcp")

# Use the FastMCP app directly
app = mcp.http_app

# ---- Tools ----
from documents.document1 import summary as summary1, documentation as documentation1
from documents.document2 import summary as summary2, documentation as documentation2
from documents.document3 import summary as summary3, documentation as documentation3

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

# @mcp.tool
# def process_sudoku_image(dummy: str = "") -> str:
#     """Process a Sudoku image and extract the puzzle. Reads image from /Users/bhrz/Documents/mcpserver3/client/app/images/image.png
#     Returns the puzzle in string format that can be used with solve_sudoku tool.
#     Takes a dummy parameter of string type."""
    
#     def preprocess_image(image):
#         """Preprocess the image for better digit recognition"""
#         # Convert to grayscale
#         gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
#         # Apply Gaussian blur to reduce noise
#         blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
#         # Apply adaptive threshold to get binary image
#         thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
#                                       cv2.THRESH_BINARY_INV, 11, 2)
        
#         return thresh
    
#     def find_largest_contour(image):
#         """Find the largest contour which should be the Sudoku grid"""
#         contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         if not contours:
#             return None
        
#         # Find the largest contour
#         largest_contour = max(contours, key=cv2.contourArea)
#         return largest_contour
    
#     def extract_grid_corners(contour):
#         """Extract the four corners of the Sudoku grid"""
#         # Approximate the contour to get corners
#         epsilon = 0.02 * cv2.arcLength(contour, True)
#         approx = cv2.approxPolyDP(contour, epsilon, True)
        
#         if len(approx) == 4:
#             return approx.reshape(4, 2)
#         else:
#             # If we don't have 4 corners, try to find them manually
#             # This is a simplified approach - in practice you might need more sophisticated corner detection
#             return None
    
#     def perspective_transform(image, corners):
#         """Apply perspective transform to get a square view of the Sudoku grid"""
#         # Define the destination points (square)
#         dst_points = np.array([
#             [0, 0],
#             [450, 0],
#             [450, 450],
#             [0, 450]
#         ], dtype=np.float32)
        
#         # Apply perspective transform
#         matrix = cv2.getPerspectiveTransform(corners.astype(np.float32), dst_points)
#         warped = cv2.warpPerspective(image, matrix, (450, 450))
        
#         return warped
    
#     def extract_cells(warped_image):
#         """Extract individual cells from the warped Sudoku grid"""
#         cells = []
#         cell_size = 50  # Each cell is 50x50 pixels
        
#         for row in range(9):
#             row_cells = []
#             for col in range(9):
#                 # Calculate cell boundaries
#                 y1 = row * cell_size
#                 y2 = (row + 1) * cell_size
#                 x1 = col * cell_size
#                 x2 = (col + 1) * cell_size
                
#                 # Extract cell
#                 cell = warped_image[y1:y2, x1:x2]
#                 row_cells.append(cell)
#             cells.append(row_cells)
        
#         return cells
    
#     def recognize_digit(cell_image):
#         """Recognize digit in a cell using simple template matching approach"""
#         # This is a simplified digit recognition
#         # In practice, you might want to use a trained model or more sophisticated OCR
        
#         # Resize cell to standard size
#         cell_resized = cv2.resize(cell_image, (28, 28))
        
#         # Count non-zero pixels (rough estimate of digit presence)
#         non_zero_pixels = cv2.countNonZero(cell_resized)
        
#         # If there are very few pixels, it's likely empty
#         if non_zero_pixels < 50:
#             return '.'
        
#         # For this simplified version, we'll use a basic approach
#         # You might want to implement actual digit recognition here
#         # For now, we'll return a placeholder that indicates we found something
#         return '?'
    
#     try:
#         # Read image from specified path
#         image_path = "/Users/bhrz/Documents/mcpserver3/client/app/images/image.png"
#         image_cv = cv2.imread(image_path)
        
#         if image_cv is None:
#             return f"Error: Could not read image from {image_path}. Please make sure the file exists."
        
#         # Preprocess image
#         processed = preprocess_image(image_cv)
        
#         # Find the largest contour (Sudoku grid)
#         contour = find_largest_contour(processed)
#         if contour is None:
#             return "Error: Could not find Sudoku grid in the image"
        
#         # Extract grid corners
#         corners = extract_grid_corners(contour)
#         if corners is None:
#             return "Error: Could not identify Sudoku grid corners"
        
#         # Apply perspective transform
#         warped = perspective_transform(image_cv, corners)
        
#         # Convert to grayscale for digit recognition
#         warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
#         # Extract individual cells
#         cells = extract_cells(warped_gray)
        
#         # Recognize digits in each cell
#         puzzle_string = ""
#         for row in cells:
#             for cell in row:
#                 digit = recognize_digit(cell)
#                 puzzle_string += digit
        
#         # Validate the extracted puzzle
#         if len(puzzle_string) != 81:
#             return f"Error: Extracted puzzle has {len(puzzle_string)} characters, expected 81"
        
#         # Count how many digits we successfully recognized
#         recognized_digits = sum(1 for c in puzzle_string if c.isdigit())
#         unknown_cells = sum(1 for c in puzzle_string if c == '?')
        
#         result = f"Successfully processed Sudoku image!\n\n"
#         result += f"Recognized digits: {recognized_digits}\n"
#         result += f"Unknown cells: {unknown_cells}\n"
#         result += f"Empty cells: {puzzle_string.count('.')}\n\n"
#         result += f"Extracted puzzle string:\n{puzzle_string}\n\n"
        
#         if unknown_cells > 0:
#             result += "⚠️  Note: Some cells could not be recognized ('?' characters). "
#             result += "You may need to manually correct these before solving.\n\n"
        
#         result += "You can now use this string with the solve_sudoku tool!"
        
#         return result
        
#     except Exception as e:
#         return f"Error processing image: {str(e)}"

@mcp.tool
def web_search(query: str, num_results: int = 10) -> str:
    """Search the web for information. Takes a search query and optional number of results (default 5).
    Returns formatted search results with titles, URLs, and snippets."""
    
    def search_duckduckgo(query, num_results=5):
        """Search using DuckDuckGo (no API key required)"""
        try:
            # DuckDuckGo search URL
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            result_divs = soup.find_all('div', class_='result')
            
            for i, div in enumerate(result_divs[:num_results]):
                try:
                    # Extract title
                    title_elem = div.find('a', class_='result__a')
                    title = title_elem.get_text().strip() if title_elem else "No title"
                    
                    # Extract URL
                    url = title_elem.get('href') if title_elem else "No URL"
                    
                    # Extract snippet
                    snippet_elem = div.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else "No snippet available"
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            return f"Error searching DuckDuckGo: {str(e)}"
    
    def search_bing(query, num_results=5):
        """Alternative search using Bing (fallback)"""
        try:
            # Simple Bing search (this is a basic implementation)
            search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            result_divs = soup.find_all('li', class_='b_algo')
            
            for i, div in enumerate(result_divs[:num_results]):
                try:
                    # Extract title
                    title_elem = div.find('h2')
                    title = title_elem.get_text().strip() if title_elem else "No title"
                    
                    # Extract URL
                    url_elem = div.find('h2').find('a') if div.find('h2') else None
                    url = url_elem.get('href') if url_elem else "No URL"
                    
                    # Extract snippet
                    snippet_elem = div.find('p')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else "No snippet available"
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
                except Exception as e:
                    continue
            
            return results
            
        except Exception as e:
            return f"Error searching Bing: {str(e)}"
    
    try:
        # Validate input
        if not query or not query.strip():
            return "Error: Search query cannot be empty"
        
        if num_results < 1 or num_results > 10:
            num_results = 5
        
        # Try DuckDuckGo first
        results = search_duckduckgo(query.strip(), num_results)
        
        # If DuckDuckGo fails, try Bing
        if isinstance(results, str) and "Error" in results:
            results = search_bing(query.strip(), num_results)
        
        # If both fail, return error
        if isinstance(results, str) and "Error" in results:
            return results
        
        # Format results
        if not results:
            return f"No results found for query: '{query}'"
        
        formatted_results = f"🔍 Search Results for: '{query}'\n"
        formatted_results += f"Found {len(results)} results:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. **{result['title']}**\n"
            formatted_results += f"   URL: {result['url']}\n"
            formatted_results += f"   {result['snippet']}\n\n"
        
        return formatted_results
        
    except Exception as e:
        return f"Error performing web search: {str(e)}"

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
