import random
import requests
from collections import Counter
import re

# Step 1: Load the French dictionary
def load_french_dictionary():
    url = "https://raw.githubusercontent.com/Taknok/French-Wordlist/master/francais.txt"
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        words = response.text.splitlines()
        french_dictionary = set(word.lower() for word in words)
        return french_dictionary
    else:
        print(f"Error fetching dictionary: {response.status_code}")
        return set()

french_dictionary = load_french_dictionary()

# Step 2: Define scoring function
def score_decrypted_text(decrypted_text, french_dictionary):
    words = re.findall(r'\b\w+\b', decrypted_text.lower())
    if not words:
        return 0
    valid_word_count = sum(1 for word in words if word in french_dictionary)
    score = valid_word_count / len(words)
    return score

# Step 3: Load corpus and define frequency functions
def load_french_corpus():
    url1 = "https://www.gutenberg.org/files/13846/13846-0.txt"
    url2 = "https://www.gutenberg.org/files/4650/4650-0.txt"
    response1 = requests.get(url1)
    response2 = requests.get(url2)
    corpus = response1.text + response2.text
    return corpus

corpus = load_french_corpus()

# Define symbols list and calculate frequencies
symbols = ['b', 'j', '\r', 'J', '”', ')', 'Â', 'É', 'ê', '5', 't', '9', 'Y', '%', 'N', 'B', 'V', '\ufeff', 'Ê', '?',
                '’', 'i', ':', 's', 'C', 'â', 'ï', 'W', 'y', 'p', 'D', '—', '«', 'º', 'A', '3', 'n', '0', 'q', '4', 'e',
                'T', 'È', '$', 'U', 'v', '»', 'l', 'P', 'X', 'Z', 'À', 'ç', 'u', '…', 'î', 'L', 'k', 'E', 'R', '2', '_',
                '8', 'é', 'O', 'Î', '‘', 'a', 'F', 'H', 'c', '[', '(', "'", 'è', 'I', '/', '!', ' ', '°', 'S', '•', '#',
                'x', 'à', 'g', '*', 'Q', 'w', '1', 'û', '7', 'G', 'm', '™', 'K', 'z', '\n', 'o', 'ù', ',', 'r', ']', '.',
                'M', 'Ç', '“', 'h', '-', 'f', 'ë', '6', ';', 'd', 'ô', 'e ', 's ', 't ', 'es', ' d', '\r\n', 'en', 'qu',
                ' l', 're', ' p', 'de', 'le', 'nt', 'on', ' c', ', ', ' e', 'ou', ' q', ' s', 'n ', 'ue', 'an', 'te',
                ' a', 'ai', 'se', 'it', 'me', 'is', 'oi', 'r ', 'er', ' m', 'ce', 'ne', 'et', 'in', 'ns', ' n', 'ur',
                'i ', 'a ', 'eu', 'co', 'tr', 'la', 'ar', 'ie', 'ui', 'us', 'ut', 'il', ' t', 'pa', 'au', 'el', 'ti',
                'st', 'un', 'em', 'ra', 'e,', 'so', 'or', 'l ', ' f', 'll', 'nd', ' j', 'si', 'ir', 'e\r', 'ss', 'u ',
                'po', 'ro', 'ri', 'pr', 's,', 'ma', ' v', ' i', 'di', ' r', 'vo', 'pe', 'to', 'ch', '. ', 've', 'nc',
                'om', ' o', 'je', 'no', 'rt', 'à ', 'lu', "'e", 'mo', 'ta', 'as', 'at', 'io', 's\r', 'sa', "u'", 'av',
                'os', ' à', ' u', "l'", "'a", 'rs', 'pl', 'é ', '; ', 'ho', 'té', 'ét', 'fa', 'da', 'li', 'su', 't\r',
                'ée', 'ré', 'dé', 'ec', 'nn', 'mm', "'i", 'ca', 'uv', '\n\r', 'id', ' b', 'ni', 'bl'] # The list of 256 symbols, same as provided

unigrams = [s for s in symbols if len(s) == 1]
bigrams = [s for s in symbols if len(s) == 2]

# Calculate unigram frequencies in corpus
unigram_counts = Counter(corpus)
total_unigrams = sum(unigram_counts.values())
unigram_freqs = {k: v / total_unigrams for k, v in unigram_counts.items() if k in unigrams}

# Calculate bigram frequencies in corpus
bigram_list = [corpus[i:i+2] for i in range(len(corpus)-1)]
bigram_counts = Counter(bigram_list)
total_bigrams = sum(bigram_counts.values())
bigram_freqs = {k: v / total_bigrams for k, v in bigram_counts.items() if k in bigrams}

combined_freqs = {**unigram_freqs, **bigram_freqs}

# Step 4: Define the function to perform symbol shifting
def shift_symbols(sorted_symbols, shift, direction):
    """ Shift elements in sorted_symbols by `shift` steps in `direction` (-1 for left, +1 for right). """
    new_symbols = sorted_symbols[:]
    for i in range(len(sorted_symbols)):
        if 0 <= i + direction * shift < len(sorted_symbols):
            new_symbols[i], new_symbols[i + direction * shift] = new_symbols[i + direction * shift], new_symbols[i]
    return new_symbols

# Step 5: Decrypt function with limited generations and optimized shifting
def decrypt(C):
    def split_into_blocks(C):
        block_size = 8
        cipher_symbols = [C[i:i + block_size] for i in range(0, len(C), block_size)]
        cipher_symbols = [block for block in cipher_symbols if len(block) == block_size]
        return cipher_symbols

    cipher_symbols = split_into_blocks(C)
    cipher_symbol_counts = Counter(cipher_symbols)
    total_cipher_symbols = sum(cipher_symbol_counts.values())
    cipher_symbol_freqs = {k: v / total_cipher_symbols for k, v in cipher_symbol_counts.items()}

    sorted_cipher_symbols = sorted(cipher_symbol_freqs.items(), key=lambda item: (-item[1], item[0]))
    cipher_symbols_sorted = [k for k, v in sorted_cipher_symbols]

    sorted_plaintext_symbols = sorted(combined_freqs.items(), key=lambda item: (-item[1], item[0]))
    plaintext_symbols_sorted = [k for k, v in sorted_plaintext_symbols]

    # Initial mapping
    mapping = dict(zip(cipher_symbols_sorted, plaintext_symbols_sorted))
    decrypted_symbols = [mapping.get(symbol, '') for symbol in cipher_symbols]
    decrypted_text = ''.join(decrypted_symbols)

    # Evaluate initial score
    best_score = score_decrypted_text(decrypted_text, french_dictionary)
    best_mapping = mapping

    # Define maximum generations and shift range
    max_generations = 256
    generation = 0

    # Iterative improvement with directional shifts
    while generation < max_generations and best_score < 0.95:
        for shift in range(1, 7):  # Shift range from 1 to 2 to avoid excessive computations
            for direction in [-1, 1]:  # Left (-1) and right (+1) shifts
                new_plaintext_symbols_sorted = shift_symbols(plaintext_symbols_sorted, shift, direction)
                new_mapping = dict(zip(cipher_symbols_sorted, new_plaintext_symbols_sorted))
                
                # Decrypt and score the new mapping
                decrypted_symbols = [new_mapping.get(symbol, '') for symbol in cipher_symbols]
                decrypted_text = ''.join(decrypted_symbols)
                score = score_decrypted_text(decrypted_text, french_dictionary)
                # print(score)
                
                # Update best score and mapping if improved
                if score > best_score:
                    best_score = score
                    best_mapping = new_mapping
                    plaintext_symbols_sorted = new_plaintext_symbols_sorted
                    break
            if best_score >= 0.55:
                break
        generation += 1

    final_decrypted_text = ''.join([best_mapping.get(symbol, '') for symbol in cipher_symbols])
    return final_decrypted_text