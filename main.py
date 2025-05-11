
import requests
from generator import generate_wordlist
import sys
import time

def check_directory(url, word):
    try:
        full_url = f"{url.rstrip('/')}/{word}"
        response = requests.get(full_url)
        if response.status_code == 200:
            return full_url
    except requests.RequestException:
        pass
    return None

def enumerate_directories(url, wordlist_file="wordlist.txt"):
    print(f"Starting directory enumeration for: {url}")
    print("Generating wordlist...")
    generate_wordlist(wordlist_file, word_count=1000, min_length=3, max_length=10)
    
    found_dirs = []
    with open(wordlist_file, 'r') as file:
        words = file.readlines()
        total = len(words)
        
        for i, word in enumerate(words, 1):
            word = word.strip()
            result = check_directory(url, word)
            if result:
                found_dirs.append(result)
                print(f"\nFound directory: {result}")
            
            # Progress indicator
            sys.stdout.write(f"\rProgress: {i}/{total} ({(i/total)*100:.1f}%)")
            sys.stdout.flush()
            time.sleep(0.1)  # Delay to prevent overwhelming the server
    
    return found_dirs

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <url>")
        print("Example: python main.py https://example.com")
        sys.exit(1)

    url = sys.argv[1]
    print("\nDirectory Enumeration Tool")
    print("=" * 30)
    
    found = enumerate_directories(url)
    
    print("\n\nResults:")
    print("=" * 30)
    if found:
        print("Found directories:")
        for directory in found:
            print(f"- {directory}")
    else:
        print("No directories found.")

if __name__ == "__main__":
    main()
