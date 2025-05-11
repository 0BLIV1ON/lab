import subprocess
import argparse
import sys

def run_gobuster(url, wordlist='wordlist.txt', threads=10, extensions=None):
    cmd = ['gobuster', 'dir', 
           '-u', url,
           '-w', wordlist,
           '-t', str(threads)]

    if extensions:
        cmd.extend(['-x', ','.join(extensions)])

    try:
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        rc = process.poll()
        if rc != 0:
            print("Error running gobuster:", process.stderr.read())
            sys.exit(1)

    except FileNotFoundError:
        print("Error: Gobuster not found. Please install Gobuster first.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Gobuster Directory Scanner Wrapper')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('-w', '--wordlist', default='wordlist.txt', help='Path to wordlist')
    parser.add_argument('-t', '--threads', type=int, default=10, help='Number of threads')
    parser.add_argument('-x', '--extensions', nargs='+', help='File extensions to check')

    args = parser.parse_args()
    run_gobuster(args.url, args.wordlist, args.threads, args.extensions)

if __name__ == "__main__":
    main()