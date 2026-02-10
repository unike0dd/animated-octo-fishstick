
import re
import os

def sanitize_file(file_path):
    """
    Sanitizes a file by removing comments, cleaning whitespace, and checking for
    suspicious keywords.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, 'r+') as f:
        content = f.read()
        
        # 1. Clear & Clean: Remove comments and extra whitespace
        # Remove single-line comments
        content = re.sub(r'#.*\n', '\n', content)
        # Remove multi-line comments (docstrings)
        content = re.sub(r'''''(.|\n)*?''''', '\n', content)
        content = re.sub(r'""".*?"""', '\n', content, flags=re.DOTALL)
        # Remove empty lines
        content = "\n".join([line for line in content.split('\n') if line.strip()])

        # 2. Scan & Sanitize: Check for suspicious keywords
        suspicious_keywords = ['eval', 'exec', 'subprocess', 'os.system']
        found_suspicious_code = False
        for keyword in suspicious_keywords:
            if re.search(r'\b' + keyword + r'\b', content):
                print(f"WARNING: Suspicious keyword '{keyword}' found in the code.")
                found_suspicious_code = True

        if not found_suspicious_code:
            print("No suspicious keywords found.")

        # 3. Write the sanitized content back to the file
        f.seek(0)
        f.write(content)
        f.truncate()
        print(f"Successfully sanitized {file_path}")

if __name__ == '__main__':
    # Example usage:
    # Create a dummy file to sanitize
    with open('test_file.py', 'w') as f:
        f.write('''
# This is a test file
import os

def my_function():
    """This is a docstring."""
    print("Hello, world!")
    # os.system("echo 'malicious command'")
''')
    sanitize_file('test_file.py')
