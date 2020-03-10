import re
import nltk
import enchant
from nltk.corpus import words
import findspark
from pyspark import *
import googlesearch
# This is a continuation of HW2 in order to successfully decipher a
# Caesar Cypher. Here are the steps:
#
# 1. Run the text file through a method that will detect the frequencies of
# each character.
# 2. Given the most frequent character, use this as a reference
# to shift against
# the most common letters used in the english language. With e being the
# most common, start with e, then to a, etc.
# 3. For each shift iteration, review the success rate of words in
# the english language.
# 4. If the rate is 60%, it is safe to assume that that is the letter is the
# value shifted against the original ciphered text.
#
# auth: Michael Kellam
# Midterm
# date: 3/9/2020


max_char = 'a'
max_val = 0
corr_diff = 0
found_char = ''
dictionary = enchant.Dict('en-US')


def view_words_chars(words_list):
    global max_char
    global max_val
    word_count = 0
    char_count = 0
    words_dict = dict()
    word_rep_set = set()
    word_rep_count = dict()
    chars_dict = dict()
    char_rep_set = set()
    char_rep_count = dict()

    # If the word hasn't been added yet, it's then added.
    # It sets to 0, then each iteration of that letter is incremented.
    for word in words_list:
        if words_dict.get(str(word).lower()) is None:
            words_dict[str(word).lower()] = 0
        words_dict[str(word).lower()] += 1
        word_rep_set.add(str(word))
        word_count += 1

        # If the character hasn't been added yet, it's then added.
        # It sets to 0, then each iteration of that letter is incremented.
        for char in word:
            if chars_dict.get(str(char).lower()) is None:
                chars_dict[str(char).lower()] = 0
            chars_dict[str(char).lower()] += 1
            char_rep_set.add(char)

        char_count += len(word)

    # Checks if the word has already been in the set.
    # If not, it creates a new list of it, and is then added.
    # If it already has been, it's simply added to it.
    for word in word_rep_set:
        low_word = word.lower()
        if word_rep_count.get(low_word) is None:
            word_rep_count[low_word] = []
        word_rep_count[low_word].append(word)

    # The same applies to the chars.
    for char in char_rep_set:
        low_char = char.lower()
        if char_rep_count.get(low_char) is None:
            char_rep_count[low_char] = []
        char_rep_count[low_char].append(char)

    # Here, we have all the data we need.
    # Now we just need to display that data properly.
    for word in words_dict.keys():
        total_occurrences = words_dict.get(word)
        total_representations = word_rep_count.get(word)
        freq_analysis = (
            round(float(total_occurrences) / float(word_count), 3))*100

        print("word: {}, {} total occurrences, {} total representations, \
            {}, {}% frequency".format(
            word, total_occurrences, len(total_representations),
            total_representations, freq_analysis
        ))

    # Just like earlier, we have the variables and data
    # that we need. All we have to do is extract that data and
    # turn it into something meaningful.
    for char in chars_dict.keys():
        total_occurrences = chars_dict.get(char)
        total_representations = char_rep_count.get(char)
        freq_analysis = (
            round(float(total_occurrences) / float(char_count), 3)) * 100

        print("char: {}, {} total occurrences, {} total representations, \
             {}, {}% frequency".format(
            char, total_occurrences, len(total_representations),
            total_representations, freq_analysis
        ))

        if total_occurrences > max_val and str.isalpha(char):
            max_char = char
            max_val = total_occurrences


# This method simply takes all of the words inside of a text file.
# By seperating this method from the other one, we can filter out the
# meaningless parts of the file so that we get strictly words.
def get_words_chars(full_read):
    re.sub(r'\W+', '', full_read)
    lines = full_read.splitlines()
    fixed_words = []
    for line in lines:
        full_read = line.split(' ')
        # We only care about letters, all this must be taken away.
        for word in full_read:
            word = word.strip(
                '.,!p#><?|}{[];:()*&^%$#@/~\'\"\n\t`+=1234567890')
            fixed_words.append(word)

    view_words_chars(fixed_words)


# Converts the words into numbers, then shifts them accordingly.
def shift_characters(text, shift):
    converted = ""
    for i in range(len(text)):
        char = text[i]
        if str.isalpha(char):
            converted += chr((ord(char) + shift - 65) % 26 + 65)
        else:
            converted += chr((ord(char)))
    return converted


# Iterates through each letter in the alphabet and shifts it by that value,
# then gets the rate of success. I decided to make the rate cutoff 60%, as I
# feel that that is a good value to try to reach.
def find_good_rate(text):
    commons = {
        'e', 'a', 'r', 'i', 'o', 't', 'n', 's', 'l', 'c', 'u', 'd',
        'p', 'm', 'h', 'g', 'b', 'f', 'y', 'w', 'k', 'v', 'x', 'z', 'j', 'q'}
    for i in commons:
        shift = get_shift_amt(i)
        new_text = shift_characters(text, shift)
        rate = get_rate(new_text)
        if (rate >= .60):
            corr_diff = ord(max_char) - ord(i)
            print('rate: ' + str(rate))
            found_char = i
            return new_text


# This method will get the rate of success for a given shift
def get_rate(text):
    good = 0
    bad = 0
    txt_words = text.split(' ')
    for i in txt_words:
        i = i.strip(
                '.,!p#><?|}{[];:()*&^%$#@/~\'\"\n\t`+=1234567890')
        if i and dictionary.check(i):
            good += 1
        elif str.isalpha(i):
            bad += 1
    print('Working...')
    total = good + bad
    return float(good / total)


def get_shift_amt(char):
    return ord(max_char) - ord(char)


def search_converted(text):
    length = 25
    words = text.split(' ')
    query = ''
    if len(words) < length:
        length = len(words)
    ind = 0
    for i in words:
        if str.isalpha(i):
            query += i + ' '
            ind += 1
        if ind > length:
            break
    results = googlesearch.search(
        query=query, tld="com", lang='en', num=3, stop=3, pause=2.0)
    if results:
        print("Here's some sources we could find:")
        for result in results:
            print(result)
    else:
        print("Could not find any possible sources.")


name = input('Enter name of file you\'d like decrypted\n>')
text = open(name + '.txt', 'r')
full_text = text.read()
get_words_chars(full_text)
print('MAX: ' + max_char)
conv_text = find_good_rate(full_text)
print(conv_text)
search_converted(conv_text)
f = open(name + '_decrypted.txt', 'w+')
f.write(conv_text)
