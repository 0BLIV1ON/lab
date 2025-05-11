import random
import string
import argparse
from typing import List
import os


def generate_common_paths() -> List[str]:
    """Generate a list of common web directories and files"""
    common_dirs = [
        'admin', 'administrator', 'backup', 'backups', 'bin', 'cache',
        'config', 'conf', 'core', 'data', 'database', 'db', 'debug', 'dev',
        'development', 'files', 'home', 'img', 'images', 'includes', 'js',
        'lib', 'libs', 'log', 'logs', 'media', 'old', 'private', 'pub',
        'public', 'scripts', 'secure', 'security', 'services', 'src', 'system',
        'temp', 'test', 'tests', 'tmp', 'upload', 'uploads', 'util', 'utils',
        'web', 'website', 'wp-admin', 'wp-content', 'wp-includes'
    ]

    common_files = [
        'admin.php', 'backup.sql', 'config.php', 'connection.php',
        'database.sql', 'db.php', 'error.log', 'index.php', 'info.php',
        'install.php', 'login.php', 'phpinfo.php', 'robots.txt',
        'server-status', 'test.php', 'web.config', '.htaccess', '.env',
        '.git/HEAD', '.svn/', '.DS_Store', 'sitemap.xml', 'wp-config.php',
        'config.inc.php', 'configuration.php'
    ]

    variations = []
    for base in common_dirs:
        variations.append(base)
        variations.append(base + '/')
        variations.append(base + '.old')
        variations.append(base + '.bak')
        variations.append(base + '_backup')
        variations.append('.' + base)
        variations.append('_' + base)

    for file in common_files:
        variations.append(file)
        variations.append(file + '.bak')
        variations.append(file + '.old')
        variations.append(file + '~')
        variations.append('.' + file)

    return list(set(variations))


def generate_wordlist(filename: str = "wordlist.txt",
                      word_count: int = 1000,
                      include_numbers: bool = False) -> None:
    """Generate a comprehensive wordlist focused on web directories and files"""
    paths = generate_common_paths()

    # Add year-based variations
    years = range(2020, 2025)
    for path in paths[:]:
        for year in years:
            paths.append(f"{path}_{year}")
            paths.append(f"{path}.{year}")

    # Add numeric variations if requested
    if include_numbers:
        for path in paths[:]:
            for i in range(1, 6):
                paths.append(f"{path}{i}")
                paths.append(f"{path}_{i}")

    # Ensure uniqueness and limit to requested count
    final_paths = list(set(paths))[:word_count]
    final_paths.sort()

    print(f"Generating wordlist with {len(final_paths)} words...")
    with open(filename, 'w') as file:
        for path in final_paths:
            file.write(path + '\n')

    print(f"Wordlist saved to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate a wordlist for directory enumeration')
    parser.add_argument('-o',
                        '--output',
                        default='wordlist.txt',
                        help='Output filename')
    parser.add_argument('-c',
                        '--count',
                        type=int,
                        default=1000,
                        help='Number of words')
    parser.add_argument('--numbers',
                        action='store_true',
                        help='Include number variations')

    args = parser.parse_args()

    generate_wordlist(filename=args.output,
                      word_count=args.count,
                      include_numbers=args.numbers)