import sys
import os
import re

# Keywords that might indicate malicious code
SUSPICIOUS_KEYWORDS = ['eval', 'exec', 'subprocess', 'os.system', 'dangerouslySetInnerHTML']

def scan_file_for_keywords(file_path):
    """Scans a single file for suspicious keywords."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for keyword in SUSPICIOUS_KEYWORDS:
                if re.search(r'\b' + keyword + r'\b', content, re.IGNORECASE):
                    print(f"Suspicious keyword '{keyword}' found in {file_path}")
                    return True
    except Exception as e:
        print(f"Could not read file {file_path}: {e}")
        # If we can't read it, we can't scan it. Treat as suspicious.
        return True 
    return False

def scan_with_virustotal(file_path):
    """
    Placeholder for VirusTotal integration.
    In a real implementation, you would use the 'requests' library to send the 
    file to the VirusTotal API and check the results.
    """
    print("Performing placeholder VirusTotal scan...")
    # For now, we will assume the file is not malicious.
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python file_scanner.py <path_to_file>")
        sys.exit(1) # Exit with 1 to indicate an error

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        sys.exit(1)

    # 1. Scan for suspicious keywords
    if scan_file_for_keywords(file_path):
        sys.exit(2) # Exit with 2 to indicate a malicious file

    # 2. Perform the advanced scan (placeholder)
    if scan_with_virustotal(file_path):
        sys.exit(2) # Exit with 2 to indicate a malicious file

    # If all checks pass, exit with 0
    print(f"File {file_path} seems clean.")
    sys.exit(0)

if __name__ == "__main__":
    main()
