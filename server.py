# server.py
from datetime import datetime, timezone
from fastmcp import FastMCP

mcp = FastMCP(name="demo-fastmcp")

# Use the FastMCP app directly
app = mcp.http_app

# ---- Tools ----
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
def get_time() -> str:
    """Get the current UTC time in ISO 8601 format. Takes no parameters.
       Only use this tool if asked for the time. Please don't pass any parameters to this tool otherwise you will be penalized.
    """
    return datetime.now(timezone.utc).isoformat()

@mcp.tool
def interesting_fact() -> str:
    """Return an interesting fact. Takes no parameters."""
    return "The moon is 238,855 miles away from Earth."

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
