import requests
import concurrent.futures
import sys
from urllib.parse import urljoin
from colorama import Fore, init

init()

class DirectoryScanner:
    def __init__(self, url, wordlist="wordlist.txt", threads=50):
        self.url = url.rstrip('/')
        self.wordlist = wordlist
        self.threads = threads
        self.session = requests.Session()
        self.found_paths = []

    def scan_path(self, path):
        try:
            # Test both with and without leading dot
            paths_to_test = [
                path,
                f".{path}",
                f"/.{path}",
                f"_{path}",
                f"~{path}"
            ]

            for test_path in paths_to_test:
                full_url = urljoin(self.url, test_path)
                response = self.session.get(full_url, allow_redirects=True, timeout=10)

                if response.status_code in [200, 301, 302, 403]:
                    print(f"{Fore.GREEN}[+] Found: {full_url} (Status: {response.status_code}){Fore.RESET}")
                    self.found_paths.append((full_url, response.status_code))

        except Exception as e:
            pass

    def run(self):
        print(f"{Fore.YELLOW}[*] Starting scan on {self.url}{Fore.RESET}")

        with open(self.wordlist, 'r') as f:
            paths = f.read().splitlines()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.scan_path, paths)

        print(f"\n{Fore.BLUE}[*] Scan complete. Found {len(self.found_paths)} paths{Fore.RESET}")
        return self.found_paths

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <url>")
        sys.exit(1)

    scanner = DirectoryScanner(sys.argv[1])
    scanner.run()