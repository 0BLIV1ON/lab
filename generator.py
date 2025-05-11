
import random
import string
import argparse
from typing import List, Set
import os

def generate_random_word(length: int, include_numbers: bool = False, include_special: bool = False) -> str:
    """Generate a random word of a given length with optional numbers and special characters."""
    chars = string.ascii_lowercase
    if include_numbers:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    return ''.join(random.choices(chars, k=length))

def load_common_words(filename: str = "common_words.txt") -> Set[str]:
    """Load common words from a file if it exists."""
    common_words = set()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            common_words = {line.strip() for line in f}
    return common_words

def generate_wordlist(filename: str = "wordlist.txt",
                     word_count: int = 1000,
                     min_length: int = 5,
                     max_length: int = 12,
                     include_numbers: bool = False,
                     include_special: bool = False,
                     include_common: bool = True) -> None:
    """
    Generate a comprehensive wordlist with various options.
    
    Args:
        filename (str): Output file name
        word_count (int): Number of words to generate
        min_length (int): Minimum word length
        max_length (int): Maximum word length
        include_numbers (bool): Include numbers in generated words
        include_special (bool): Include special characters
        include_common (bool): Include common directory names
    """
    common_dirs = {
        'admin', 'login', 'wp-admin', 'dashboard', 'api',
        'upload', 'images', 'css', 'js', 'static', 'media',
        'backup', 'db', 'test', 'dev', 'beta', 'prod'
    }
    
    words: Set[str] = set()
    
    # Add common directories if requested
    if include_common:
        words.update(common_dirs)
    
    # Generate random words until we reach word_count
    while len(words) < word_count:
        length = random.randint(min_length, max_length)
        word = generate_random_word(length, include_numbers, include_special)
        words.add(word)
    
    # Write to file
    print(f"Generating wordlist with {word_count} words...")
    with open(filename, 'w') as file:
        for word in sorted(words):
            file.write(word + '\n')
    
    print(f"Wordlist saved to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a wordlist for directory enumeration')
    parser.add_argument('-o', '--output', default='wordlist.txt', help='Output filename')
    parser.add_argument('-c', '--count', type=int, default=1000, help='Number of words')
    parser.add_argument('--min-length', type=int, default=5, help='Minimum word length')
    parser.add_argument('--max-length', type=int, default=12, help='Maximum word length')
    parser.add_argument('--numbers', action='store_true', help='Include numbers')
    parser.add_argument('--special', action='store_true', help='Include special characters')
    parser.add_argument('--no-common', action='store_true', help='Exclude common directory names')
    
    args = parser.parse_args()
    
    generate_wordlist(
        filename=args.output,
        word_count=args.count,
        min_length=args.min_length,
        max_length=args.max_length,
        include_numbers=args.numbers,
        include_special=args.special,
        include_common=not args.no_common
    )
