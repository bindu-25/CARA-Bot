"""
Utility functions for safely parsing LLM JSON responses.
Handles truncated, malformed, and markdown-wrapped JSON.
"""

import json
import re


def safe_parse_json(content: str, fallback: dict = None) -> dict:
    """
    Robustly parse JSON from LLM response, handling common issues:
    - Markdown code blocks (```json ... ```)
    - Truncated JSON (closing brackets/braces missing)
    - Trailing commas
    - Unterminated strings
    
    Args:
        content: Raw LLM response string
        fallback: Dictionary to return if all parsing fails
        
    Returns:
        Parsed dictionary or fallback
    """
    if fallback is None:
        fallback = {}
    
    if not content or not content.strip():
        return fallback
    
    content = content.strip()
    
    # Step 1: Strip markdown code blocks
    if content.startswith("```"):
        content = re.sub(r'^```json?\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)
        content = content.strip()
    
    # Step 2: Try direct parse first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Step 3: Try to repair truncated JSON
    repaired = _repair_truncated_json(content)
    if repaired:
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    
    # Step 4: Try aggressive repair - find the outermost { }
    try:
        # Find first { and try to extract valid JSON from there
        start = content.index('{')
        # Count brackets to find where JSON likely ends
        repaired = _force_close_json(content[start:])
        return json.loads(repaired)
    except (ValueError, json.JSONDecodeError):
        pass
    
    print(f"⚠️ JSON repair failed. Content preview: {content[:200]}...")
    return fallback


def _repair_truncated_json(content: str) -> str:
    """
    Attempt to repair truncated JSON by:
    1. Removing the last incomplete value/key
    2. Closing all open brackets and braces
    """
    # Remove any trailing incomplete string (unterminated quote)
    # Find the last complete key-value pair
    
    # Strategy: truncate back to the last complete structure
    # Look for the last complete entry (ends with }, ], ", number, true, false, null)
    
    # First, remove any trailing partial string
    lines = content.split('\n')
    
    # Remove lines from the end until we find a "complete" line
    while lines:
        last_line = lines[-1].strip()
        
        # Check if this line looks complete
        if last_line.endswith((',', '}', ']', '"', 'true', 'false', 'null')) or \
           re.search(r'[}\]"\d]$', last_line):
            break
        
        lines.pop()
    
    if not lines:
        return None
    
    content = '\n'.join(lines)
    
    # Remove trailing comma if present
    content = re.sub(r',\s*$', '', content)
    
    # Count open vs close brackets
    open_braces = content.count('{') - content.count('}')
    open_brackets = content.count('[') - content.count(']')
    
    # Check for unterminated strings
    in_string = False
    escaped = False
    for char in content:
        if escaped:
            escaped = False
            continue
        if char == '\\':
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
    
    # If we're inside a string, close it
    if in_string:
        content += '"'
    
    # Remove any trailing comma after closing the string
    content = re.sub(r',\s*$', '', content.rstrip())
    
    # Close open brackets and braces
    content += ']' * max(0, open_brackets)
    content += '}' * max(0, open_braces)
    
    return content


def _force_close_json(content: str) -> str:
    """
    Aggressively close JSON by tracking bracket depth.
    Truncates at the last valid point and closes everything.
    """
    result = []
    stack = []
    in_string = False
    escaped = False
    last_valid_pos = 0
    
    for i, char in enumerate(content):
        if escaped:
            escaped = False
            result.append(char)
            continue
            
        if char == '\\' and in_string:
            escaped = True
            result.append(char)
            continue
        
        if char == '"':
            in_string = not in_string
            result.append(char)
            if not in_string:
                last_valid_pos = len(result)
            continue
        
        if in_string:
            result.append(char)
            continue
        
        if char == '{':
            stack.append('}')
            result.append(char)
        elif char == '[':
            stack.append(']')
            result.append(char)
        elif char in ('}', ']'):
            if stack and stack[-1] == char:
                stack.pop()
            result.append(char)
            last_valid_pos = len(result)
        else:
            result.append(char)
            if char in (',', ':'):
                pass  # These need following content
            elif char.strip():  # Non-whitespace
                last_valid_pos = len(result)
    
    # If still in string, close it
    if in_string:
        result.append('"')
    
    # Build result string
    result_str = ''.join(result)
    
    # Remove trailing comma
    result_str = re.sub(r',\s*$', '', result_str.rstrip())
    
    # Close remaining open brackets/braces
    while stack:
        result_str += stack.pop()
    
    return result_str