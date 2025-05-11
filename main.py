import subprocess
import os

def run_gobuster():
    """
    Prompts the user for a website URL and wordlist, then runs gobuster with default arguments.
    """
    # Prompt the user for the target URL
    url = input("Enter the target website URL (e.g., http://example.com): ").strip()
    if not url:
        print("Error: URL is required.")
        return

    # Ensure the URL starts with http:// or https://
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
        print(f"URL updated to: {url}")

    # Prompt the user for the wordlist
    wordlist = input("Enter the path to the wordlist file (e.g., /usr/share/wordlists/dirb/common.txt): ").strip()
    if not wordlist:
        print("Error: Wordlist is required.")
        return

    # Check if the wordlist file exists
    if not os.path.isfile(wordlist):
        print(f"Error: The wordlist file '{wordlist}' does not exist.")
        return

    # Set default arguments
    output_file = "gobuster_output.txt"  # Default output file
    threads = 10  # Default number of threads

    # Construct the gobuster command
    command = [
        "gobuster", "dir",
        "-u", url,
        "-w", wordlist,
        "-o", output_file,
        "-t", str(threads)
    ]

    print(f"Running: {' '.join(command)}")

    try:
        # Run the gobuster command
        subprocess.run(command, check=True)
        print(f"Scan completed. Results saved to {output_file}.")
    except FileNotFoundError:
        print("Error: gobuster is not installed or not in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error: gobuster failed with exit code {e.returncode}")

if __name__ == "__main__":
    run_gobuster()