import random
import string
import argparse
from typing import List, Set
import os

def generate_random_word(length: int, include_numbers: bool = False, include_special: bool = False) -> str:
    """Generate a random word with advanced patterns."""
    patterns = {
        'admin': ['adm1n', 'admin_', '_admin', 'administrator', '@dmin'],
        'backup': ['bak', '.bak', '_backup', '.old', '.save', '~'],
        'config': ['conf', 'cfg', '.ini', '.env', '.config', '_config'],
        'test': ['test', 'testing', 'dev', 'stage', 'staging', 'uat'],
        'debug': ['dbg', 'debug', 'console', 'terminal', 'shell'],
        'upload': ['upl', 'upload', 'uploads', 'media', 'files'],
        'api': ['api', 'rest', 'v1', 'v2', 'v3', 'graphql', 'gql'],
        'auth': ['auth', 'login', 'signin', 'signup', 'register'],
        'cms': ['wp', 'wordpress', 'joomla', 'drupal', 'moodle'],
        'db': ['mysql', 'pgsql', 'oracle', 'mongodb', 'redis']
    }

    real_words = ['admin', 'login', 'dashboard', 'profile', 'settings', 'upload',
                'images', 'media', 'blog', 'posts', 'users', 'api', 'docs',
                'help', 'support', 'about', 'contact', 'search', 'register',
                'password', 'reset', 'config', 'setup', 'install', 'update',
                'backup', 'logs', 'stats', 'admin', 'test', 'dev', 'staging']

    # 80% chance to use pattern-based generation
    if random.random() < 0.8:
        category = random.choice(list(patterns.keys()))
        base_word = random.choice(patterns[category])

        # Apply transformations
        transformations = [
            lambda x: x,  # no change
            lambda x: x.upper(),
            lambda x: x.lower(),
            lambda x: x + str(random.randint(1, 9999)),
            lambda x: x + random.choice(['_old', '_bak', '_tmp', '_new']),
            lambda x: '.' + x,
            lambda x: '_' + x,
            lambda x: x + random.choice(['.php', '.asp', '.jsp', '.html'])
        ]

        return random.choice(transformations)(base_word)

    # 70% chance to use a real word if it matches the length criteria
    if random.random() < 0.7 and any(len(word) >= length and len(word) <= length for word in real_words):
        suitable_words = [w for w in real_words if len(w) >= length and len(w) <= length]
        return random.choice(suitable_words)

    # Otherwise generate random string
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
    """Generate a comprehensive wordlist with various options."""
    common_dirs = {
        'admin', 'administrator', 'wp-admin', 'cpanel', 'phpmyadmin',
        'wp-content', 'wp-includes', 'administrator', 'joomla', 'drupal',
        'dev', 'test', 'beta', 'staging', 'development', 'production',
        'backup', 'backups', '.bak', '.backup', '.old', '.save', '.swap', '.swp',
        'config', '.config', '.env', '.git', '.svn', 'log', 'logs', '.htaccess',
        'upload', 'uploads', 'media', 'static', 'assets', 'files', 'private',
        '.ssh', '.npm', '.tmp', '.temp', '.cache', '.hidden',
        'api', 'rest', 'v1', 'v2', 'docs', 'documentation', 'sdk',
        'phpinfo', 'server-status', 'server-info', '.well-known'
    }

    words = set()

    if include_common:
        words.update(common_dirs)

    while len(words) < word_count:
        length = random.randint(min_length, max_length)
        word = generate_random_word(length, include_numbers, include_special)
        words.add(word)

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