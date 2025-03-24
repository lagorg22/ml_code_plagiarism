import os
import re
import tokenize
from io import StringIO

# Directory containing the code files
DIRECTORY = "codefiles"  # Replace with your directory path

# Core preprocessing functions
def normalize_whitespace(code):
    """Normalize whitespace: collapse multiple spaces/tabs, remove empty lines."""
    lines = [re.sub(r'\s+', ' ', line.strip()) for line in code.splitlines()]
    return '\n'.join(line for line in lines if line)

def remove_comments_python(code):
    try:
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)

        # Step 2: Use tokenize to remove # comments and preserve structure
        result = []
        code_io = StringIO(code)
        tokens = tokenize.generate_tokens(code_io.readline)
        prev_end = (0, 0)
        for token in tokens:
            if token.type != tokenize.COMMENT:  # Skip # comments
                start_line, _ = token.start
                prev_line, _ = prev_end
                if start_line > prev_line + 1:
                    result.append('\n' * (start_line - prev_line - 1))
                result.append(token.string)
                prev_end = token.end
        return "".join(result)
    except Exception:
        return code  # Return original if processing fails

def remove_comments_c_style(code):
    """Remove comments from C-style languages (C, C++, Java, JS)."""
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    return code

def remove_comments_xml_html(code):
    """Remove comments from XML/HTML files."""
    code = re.sub(r'<!--[\s\S]*?-->', '', code)
    return code

def remove_boilerplate(code, ext):
    """Remove common boilerplate code based on file extension."""
    if ext in ['.c', '.h', '.cpp', '.cc']:
        code = re.sub(r'#include\s*[<"][\w\./]+[>"]', '', code)
    elif ext == '.java':
        code = re.sub(r'import\s+[\w\.*]+;', '', code)
    elif ext == '.py':
        code = re.sub(r'import\s+\w+|from\s+\w+\s+import\s+[\w,*]+', '', code)
    elif ext == '.html':
        code = re.sub(r'<!DOCTYPE[^>]*>|<html>|<body>|</html>|</body>', '', code, flags=re.IGNORECASE)
    return code

def remove_strings_c_style(code):
    """Replace string literals with a placeholder in C-style languages."""
    code = re.sub(r'"[^"]*"', 'STRING', code)
    code = re.sub(r"'[^']*'", 'STRING', code)
    return code

def extract_code_html(code):
    """Extract code from <script> tags in HTML."""
    script_content = re.findall(r'<script[^>]*>(.*?)</script>', code, re.DOTALL)
    return '\n'.join(script_content) if script_content else code

# Mapping of file extensions to comment removal functions
COMMENT_REMOVERS = {
    '.py': remove_comments_python,
    '.java': remove_comments_c_style,
    '.c': remove_comments_c_style,
    '.cc': remove_comments_c_style,
    '.cpp': remove_comments_c_style,
    '.h': remove_comments_c_style,
    '.js': remove_comments_c_style,
    '.xml': remove_comments_xml_html,
    '.html': remove_comments_xml_html
}

def preprocess_code(code, ext):
    """Apply all preprocessing steps to the code based on its extension."""
    if ext in COMMENT_REMOVERS:
        code = COMMENT_REMOVERS[ext](code)
    else:
        return code

    code = normalize_whitespace(code)
    code = remove_boilerplate(code, ext)
    if ext in ['.c', '.cpp', '.cc', '.h', '.java', '.js']:
        code = remove_strings_c_style(code)
    if ext == '.html':
        code = extract_code_html(code)
    return code

def process_file(filepath, output_filepath):
    """Process a single file and apply all preprocessing steps."""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    if ext not in COMMENT_REMOVERS:
        print(f"Skipping {filepath}: Unsupported file type")
        return

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        cleaned_content = preprocess_code(content, ext)

        if not cleaned_content.strip():
            print(f"Skipping {filepath}: Empty after preprocessing")
            return

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"Processed {filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")

def main():
    """Process all files in the directory."""
    if not os.path.exists(DIRECTORY):
        print(f"Error: Directory {DIRECTORY} does not exist")
        return
    for filename in os.listdir(DIRECTORY):
        filepath = os.path.join(DIRECTORY, filename)
        if os.path.isfile(filepath):
            output_filepath = filepath  # Overwrite the original file
            process_file(filepath, output_filepath)

if __name__ == "__main__":
    main()