
import os
import hashlib
import json

BASELINE_FILE = 'integrity_baseline.json'

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
    print(f"Baseline created and saved to {BASELINE_FILE}")

def check_integrity(directory='.'):
    """Checks the integrity of files against the baseline."""
    if not os.path.exists(BASELINE_FILE):
        print("Baseline file not found. Please create a baseline first.")
        return

    with open(BASELINE_FILE, 'r') as f:
        baseline = json.load(f)

    for file_path, baseline_hash in baseline.items():
        if not os.path.exists(file_path):
            print(f"ALERT: File is missing: {file_path}")
            continue

        current_hash = calculate_hash(file_path)
        if current_hash != baseline_hash:
            print(f"ALERT: File has been modified: {file_path}")

    print("Integrity check complete.")

if __name__ == '__main__':
    # Example usage:
    # 1. Create a baseline (run this once)
    # create_baseline()

    # 2. Check the integrity (run this to check for changes)
    check_integrity()
