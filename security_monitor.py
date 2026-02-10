
import os
import hashlib
import json
import re

# --- Configuration ---
BASELINE_FILE = 'integrity_baseline.json'
REPO_DIR = './'  # Your local git repository
DEPLOYED_DIR = './deployed_code'  # A simulated directory for deployed code

# --- 1. Sanitizer and Scanner ---
SUSPICIOUS_KEYWORDS = ['eval', 'exec', 'subprocess', 'os.system', 'dangerouslySetInnerHTML']

def scan_for_malicious_code(directory='.'):
    """Scans for suspicious keywords in all files in a directory."""
    print("\n--- Starting Malicious Code Scan ---")
    found_suspicious_code = False
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for keyword in SUSPICIOUS_KEYWORDS:
                            if re.search(r'\b' + keyword + r'\b', content):
                                print(f"WARNING: Suspicious keyword '{keyword}' found in {file_path}")
                                found_suspicious_code = True
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")

    if not found_suspicious_code:
        print("No suspicious keywords found.")
    return found_suspicious_code

# --- 2. Integrity Checker ---
def calculate_hash(file_path):
    """Calculates the SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_baseline(directory='.'):
    """Creates a baseline of file hashes for the specified directory."""
    baseline = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                baseline[file_path] = calculate_hash(file_path)

    with open(BASELINE_FILE, 'w') as f:
        json.dump(baseline, f, indent=4)
    print(f"--- Baseline created and saved to {BASELINE_FILE} ---")

def check_integrity(directory='.'):
    """Checks the integrity of files against the baseline."""
    print("\n--- Starting Integrity Check ---")
    if not os.path.exists(BASELINE_FILE):
        print("Baseline file not found. Please create a baseline first.")
        return True  # Return True to indicate a problem

    with open(BASELINE_FILE, 'r') as f:
        baseline = json.load(f)

    integrity_failed = False
    for file_path, baseline_hash in baseline.items():
        if not os.path.exists(file_path):
            print(f"ALERT: File is missing: {file_path}")
            integrity_failed = True
            continue

        current_hash = calculate_hash(file_path)
        if current_hash != baseline_hash:
            print(f"ALERT: File has been modified: {file_path}")
            integrity_failed = True

    if not integrity_failed:
        print("Integrity check passed.")
    return integrity_failed

# --- 3. Repo vs. Origin Check ---
def check_repo_vs_origin():
    """Compares the local repo with the 'deployed' code."""
    print("\n--- Starting Repo vs. Origin Check ---")
    repo_files = set()
    deployed_files = set()

    for root, _, files in os.walk(REPO_DIR):
        for file in files:
            repo_files.add(os.path.join(root, file))

    for root, _, files in os.walk(DEPLOYED_DIR):
        for file in files:
            deployed_files.add(os.path.join(root, file))

    if repo_files != deployed_files:
        print("ALERT: File mismatch between repo and deployed code.")
        print(f"Files only in repo: {repo_files - deployed_files}")
        print(f"Files only in deployed: {deployed_files - repo_files}")
        return True

    mismatch = False
    for file_path in repo_files:
        # Simple comparison, for real-world use, this could be more robust
        if os.path.isfile(file_path) and DEPLOYED_DIR in file_path:
             continue # ignore files in deployed folder
        if os.path.isfile(file_path) and calculate_hash(file_path) != calculate_hash(os.path.join(DEPLOYED_DIR, file_path)):
            print(f"ALERT: Content mismatch for file: {file_path}")
            mismatch = True

    if not mismatch:
        print("Repo and origin match.")
    return mismatch

# --- Main Execution --- 
def main():
    # Simulate a deployed environment for demonstration
    if not os.path.exists(DEPLOYED_DIR):
        os.makedirs(DEPLOYED_DIR)
        with open(os.path.join(DEPLOYED_DIR, 'index.html'), 'w') as f:
            f.write("<html><body><h1>Deployed App</h1></body></html>")


    # Create a baseline on the first run
    if not os.path.exists(BASELINE_FILE):
        create_baseline(REPO_DIR)

    # --- Run all security checks ---
    malicious_code_found = scan_for_malicious_code(REPO_DIR)
    integrity_failed = check_integrity(REPO_DIR)
    origin_mismatch = check_repo_vs_origin()

    # --- Invalidate Session if any check fails ---
    if malicious_code_found or integrity_failed or origin_mismatch:
        print("\n*** SECURITY ALERT: Potential breach detected. Tossing session. ***")
        # In a real app, you would invalidate the user's session here.
        # For example: session.invalidate() or by calling an API endpoint.
    else:
        print("\n--- All security checks passed successfully. ---")

if __name__ == '__main__':
    main()
