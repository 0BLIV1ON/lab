import random
import string

def generate_random_word(length):
    """Generate a random word of a given length."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def generate_wordlist(filename="wordlist.txt", word_count=1000, min_length=5, max_length=12):
    """
    Generate a wordlist with random words.
    
    Args:
        filename (str): The name of the output file.
        word_count (int): The number of words to generate.
        min_length (int): The minimum length of each word.
        max_length (int): The maximum length of each word.
    """
    print(f"Generating a wordlist with {word_count} random words...")

    with open(filename, 'w') as file:
        for _ in range(word_count):
            word_length = random.randint(min_length, max_length)
            word = generate_random_word(word_length)
            file.write(word + '\n')

    print(f"Wordlist saved to {filename}")

if __name__ == "__main__":
    generate_wordlist()