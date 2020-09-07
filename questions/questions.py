import nltk
import sys
import re
import os
import math
import string
from nltk import word_tokenize


# FILE_MATCHES -- how many files should be matched for any given query.
FILE_MATCHES = 1
# SENTENCES_MATCHES -- how many sentences within those files should be matched for any given query.
SENTENCE_MATCHES = 1
# By default, each of these values is 1: our AI will find the top sentence from the top matching document as the answer to our question.


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user to enter query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches/best matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract best match sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # first load the files from the corpus directory into memory
    corpus = dict()
    # Return a list specifiying a directory given by 'path'.
    for filename in os.listdir(directory):
        file_p = os.path.join(directory, filename)
        if os.path.isfile(file_p) and filename.endswith(".txt"):
                # os.path.join(path, *path) -- concatenation of path and *paths with exactly one directory separator (os.sep)
            with open(file_p, "r", encoding='utf8') as file:
                corpus[filename] = file.read()
    return corpus
    

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase [ .lower() ], and
    removing any punctuation or English stopwords.
    """
    words = nltk.word_tokenize(document)
    # tokenize files into a list of words
    return [
        word.lower() for word in words
        # filter out all punctuation (import string) and all stopwords
        if not all(char in string.punctuation for char in word) 
        and word not in nltk.corpus.stopwords.words("english")
    ]
    

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # compute inverse document frequency values for each of the words
    idf_words = set()
    for filename in documents:
        # map the words in the filename for documents dictionary
        idf_words.update(documents[filename])
    idfs = dict()
    for word in idf_words:
        # n = number of documents in which word appears
        n = sum(word in documents[filename] for filename in documents)
        # import math -- log is natural base e
        # idf of a word = natural logarithm of the number of documents divided by the number of documents in which the word appears.
        idf = math.log(len(documents) / n)
        idfs[word] = idf
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = dict()
    for key, value in files.items():
        tf_idfs[key] = 0
        for word in query:
            if word in list(idfs):
                # tf-idf for a term is computed by multiplying the number of times the term appears in the document by the IDF value for that term
                # len vs .count
                tf_idfs[key] += value.count(word) * idfs[word]
            else:
                tf_idfs[key] += 0
    # .items() -- Returns: A view object that displays a list of a given dictionary's (key, value) tuple pair
    # use sorted(iterable, *, key, reverse) -- key=lambda: numerical order, x[1]: second column i.e. sum of values from .count, reverse=TRUE: descending order
    # returned list of filenames should be of length n -- [:n] (begining of list to length n)
    return [key for key, value in sorted(tf_idfs.items(), key=lambda x: x[1], reverse=True)][:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # identifies the sentences that are the best match for the query.
    top_sens = dict()
    for sentence, tokens in sentences.items():
        # add query rank to the idfs dictionary
        # top_sens is a dictionary of two columns, both initally empty
        query_tokens = len([word for word in tokens if word in query])
        value = query_tokens / (len(tokens))
        for word, idf_score in idfs.items():
            if word in query and word in tokens:
                # 'matching word measure'
                value += idf_score
        top_sens[sentence] = value
        # if a tie, prefer a higher 'query term density' -- /= : divide by and update value
        # defined as the proportion of words in the sentence that are also words in the query. For example, if a sentence has 10 words, 3 of which are in the query, then the sentence’s query term density is 0.3.
        # list of sentences to query ranked according to idf x[1] and if a tie, then density x[2] ; reverse=True: descending order
    # sentence list x[0] of length n ( [:n] )
    top_sens_rank = sorted(top_sens, key=top_sens.get, reverse=True)
    return top_sens_rank[0:n]
    

if __name__ == "__main__":
    main()
