import os
import requests
from generator import generate_wordlist
import sys
import time
import argparse
import threading
from queue import Queue
from urllib.parse import urljoin
import json
import re
from colorama import init, Fore
from typing import List, Dict, Set
import concurrent.futures
import signal
import subprocess
import platform

init(autoreset=True)


class GoBusterWrapper:

    def __init__(self, url: str, options: Dict):
        self.url = url.rstrip('/')
        self.options = options
        self.found_paths: Set[str] = set()
        self.queue = Queue()
        self.session = requests.Session()
        self.stop_scan = False
        self.results = []

        # Set up authentication if provided
        if options.get('auth'):
            username, password = options['auth'].split(':')
            self.session.auth = (username, password)

        # Set up custom headers
        if options.get('headers'):
            self.session.headers.update(options['headers'])

        signal.signal(signal.SIGINT, self.handle_interrupt)

    def handle_interrupt(self, signum, frame):
        print(f"\n{Fore.YELLOW}[!] Stopping scan gracefully...")
        self.stop_scan = True

    def check_directory(self, path: str) -> dict:
        if self.stop_scan:
            return None

        def analyze_response(resp):
        # Auto-updating fingerprints from response analysis
            fingerprints = {
                'wordpress': ['wp-content', 'wp-includes', 'wp-json'],
                'joomla': ['com_content', 'mod_', 'joomla.javascript'],
                'drupal': ['drupal.js', 'drupal.min.js', 'drupal-settings'],
                'apache': ['Apache/', 'httpd', 'mod_perl', 'mod_ssl'],
                'nginx': ['nginx', 'openresty', 'tengine'],
                'php': ['X-Powered-By: PHP', 'PHPSESSID', '.php'],
                'laravel': ['laravel_session', 'laravel-token', 'laravel.js'],
                'rails': ['_rails_', 'rails-ujs', 'rails.js'],
                'node': ['node_modules', 'express', 'nextjs'],
                'django': ['django-admin', 'csrftoken', 'djangojs'],
                'react': ['react.development.js', 'react.production.min.js'],
                'vue': ['vue.js', 'vue.min.js', 'vue-router'],
                'angular': ['angular.js', 'ng-app', 'ng-controller'],
                'database': ['mysql', 'postgresql', 'mongodb', 'oracle', 'redis'],
                'cdn': ['cloudflare', 'akamai', 'fastly', 'cloudfront'],
                'analytics': ['google-analytics', 'hotjar', 'mixpanel'],
                'security': ['waf', 'captcha', 'recaptcha', 'hcaptcha']
            }

            # Dynamic pattern learning
            headers = str(resp.headers).lower()
            body = resp.text.lower()

            # Auto-detect new patterns
            new_patterns = set()

            # Version detection
            version_pattern = r'(?:v|version|ver)[.-]?\s*([0-9]+(?:\.[0-9]+)*)'
            versions = re.findall(version_pattern, body + headers)

            # Framework detection from common paths
            common_paths = ['/api', '/admin', '/login', '/dashboard']

            detected = []
            for tech, patterns in fingerprints.items():
                if any(p.lower() in (body + headers) for p in patterns):
                    detected.append(tech)
                    # Learn new patterns
                    context = body[max(0, body.find(tech)-50):body.find(tech)+50]
                    new_patterns.update(re.findall(r'[\w-]+\.[\w-]+', context))

            # Update fingerprints with new patterns
            if new_patterns:
                fingerprints['custom'] = list(new_patterns)

            return detected

        methods = self.options.get('methods', ['GET'])
        extensions = self.options.get('extensions', [''])
        results = []

        for method in methods:
            for ext in extensions:
                if ext and not path.endswith(ext):
                    full_path = f"{path}{ext}"
                else:
                    full_path = path

                full_url = urljoin(self.url, full_path.lstrip('/'))

                try:
                    response = self.session.request(
                        method=method,
                        url=full_url,
                        allow_redirects=self.options.get(
                            'follow_redirects', False),
                        timeout=self.options.get('timeout', 10),
                        verify=self.options.get('verify_ssl', True))

                    status_code = response.status_code

                    if self.should_report(status_code, response):
                        result = {
                            'url':
                            full_url,
                            'method':
                            method,
                            'status':
                            status_code,
                            'size':
                            len(response.content),
                            'words':
                            len(response.text.split()),
                            'lines':
                            len(response.text.splitlines()),
                            'title':
                            self.extract_title(
                                response.text) if response.headers.get(
                                    'content-type', '').startswith('text/html')
                            else None
                        }

                        if self.options.get('pattern'):
                            result['pattern_match'] = bool(
                                re.search(self.options['pattern'],
                                          response.text))

                        results.append(result)

                        # Handle recursive scanning
                        if self.options.get(
                                'recursive'
                        ) and status_code == 200 and full_path not in self.found_paths:
                            self.found_paths.add(full_path)
                            self.queue_paths(full_path)

                except requests.RequestException:
                    continue

        return results[0] if results else None

    def extract_title(self, html_content: str) -> str:
        match = re.search(r'<title>(.*?)</title>', html_content,
                          re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ''

    def should_report(self, status_code: int, response) -> bool:
        status_codes = self.options.get('status_codes',
                                        [200, 204, 301, 302, 307, 401, 403])

        if status_code not in status_codes:
            return False

        if self.options.get('size_filter'):
            if len(response.content) == self.options['size_filter']:
                return False

        if self.options.get('exclude_length'):
            if len(response.content) == self.options.get('exclude_length'):
                return False

        return True

    def queue_paths(self, base_path: str = '') -> None:
        wordlist = self.options.get('wordlist', 'wordlist.txt')
        if not os.path.exists(wordlist):
            print(f"{Fore.YELLOW}[!] Generating wordlist...")
            generate_wordlist(wordlist)

        with open(wordlist, 'r') as f:
            for word in f:
                if self.stop_scan:
                    break
                word = word.strip()
                if base_path:
                    path = f"{base_path}/{word}"
                else:
                    path = word
                self.queue.put(path)

    def scan_worker(self) -> None:
        while True:
            if self.stop_scan:
                break

            try:
                path = self.queue.get_nowait()
            except Queue.Empty:
                break

            result = self.check_directory(path)
            if result:
                self.results.append(result)
                self.print_result(result)

            self.queue.task_done()

    def print_result(self, result: dict) -> None:
        status_colors = {
            200: Fore.GREEN,
            301: Fore.BLUE,
            302: Fore.BLUE,
            401: Fore.RED,
            403: Fore.RED
        }

        color = status_colors.get(result['status'], Fore.WHITE)
        output = f"{color}[{result['status']}] {result['method']} {result['url']} ({result['size']} bytes)"

        if result.get('title'):
            output += f" - {result['title']}"

        print(output)

    def save_results(self) -> None:
        if not self.results:
            return

        output_format = self.options.get('output_format', 'txt')
        filename = f"gobuster_results.{output_format}"

        if output_format == 'json':
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
        else:
            with open(filename, 'w') as f:
                for result in self.results:
                    f.write(
                        f"{result['status']} {result['method']} {result['url']}\n"
                    )

    def run(self) -> None:
        print(f"\n{Fore.CYAN}GoBuster Python Implementation")
        print("=" * 50)

        print(f"\n{Fore.YELLOW}[*] Target URL: {self.url}")
        print(f"[*] Threads: {self.options.get('threads', 10)}")
        print(f"[*] Wordlist: {self.options['wordlist']}")
        if self.options.get('extensions'):
            print(f"[*] Extensions: {', '.join(self.options['extensions'])}")

        self.queue_paths()

        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.options.get('threads', 10)) as executor:
            workers = [
                executor.submit(self.scan_worker)
                for _ in range(self.options.get('threads', 10))
            ]
            concurrent.futures.wait(workers)

        if self.options.get('output_format'):
            self.save_results()


def main():
    parser = argparse.ArgumentParser(
        description='Advanced Directory/File Enumeration Tool')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('-w',
                        '--wordlist',
                        default='wordlist.txt',
                        help='Path to wordlist')
    parser.add_argument('-t',
                        '--threads',
                        type=int,
                        default=10,
                        help='Number of threads')
    parser.add_argument('-m',
                        '--methods',
                        nargs='+',
                        default=['GET'],
                        help='HTTP methods to use')
    parser.add_argument('-x',
                        '--extensions',
                        nargs='+',
                        help='File extensions to check (use "all" for common web extensions)')
    parser.add_argument('--deep',
                        action='store_true',
                        help='Enable deep scanning with common backup extensions')
    parser.add_argument('--fuzzy',
                        action='store_true',
                        help='Enable fuzzy matching for common patterns')
    parser.add_argument('-s',
                        '--status-codes',
                        nargs='+',
                        type=int,
                        help='Status codes to report')
    parser.add_argument('-r',
                        '--recursive',
                        action='store_true',
                        help='Enable recursive scanning')
    parser.add_argument('-p',
                        '--pattern',
                        help='Pattern to match in responses')
    parser.add_argument('-o',
                        '--output',
                        choices=['txt', 'json'],
                        help='Output format')
    parser.add_argument('-a', '--auth', help='Basic auth (username:password)')
    parser.add_argument('--headers',
                        nargs='+',
                        help='Custom headers (key:value)')
    parser.add_argument('--exclude-length',
                        type=int,
                        help='Exclude responses of specific length')
    parser.add_argument('--follow-redirects',
                        action='store_true',
                        help='Follow redirects')
    parser.add_argument('--no-tls-validation',
                        action='store_true',
                        help='Skip TLS certificate validation')
    parser.add_argument('--timeout',
                        type=int,
                        default=10,
                        help='Request timeout in seconds')

    args = parser.parse_args()

    options = vars(args)

    # Handle "all" extensions option
    if options.get('extensions') and 'all' in options['extensions']:
        options['extensions'] = [
            '.php', '.html', '.htm', '.js', '.css', '.txt', '.pdf', '.json',
            '.xml', '.asp', '.aspx', '.jsp', '.sql', '.zip', '.tar.gz', '.tgz',
            '.doc', '.docx', '.xls', '.xlsx', '.conf', '.bak', '.backup', '.swp',
            '.env', '.ini', '.cfg', '.config', '.log', '.old', '.temp', '.tmp',
            '.bak~', '.php~', '.php.bak', '.php.old', '.php_', '_php',
            '.html.old', '.html.bak', '.htm.old', '.htm.bak', '.txt.old',
            '.inc', '.inc.php', '.inc.old', '.inc.bak', '.sql.gz', '.sql.bz2'
        ]

    scanner = GoBusterWrapper(args.url, options)
    scanner.run()


if __name__ == "__main__":
    main()