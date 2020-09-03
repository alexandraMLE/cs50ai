import nltk
import sys
from nltk.tokenize import word_tokenize
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""


NONTERMINALS = """
S -> NP VP | S Conj S | S Conj VP
AP -> Adj | Adj N | Adj AP
NP -> N | Det NP | AP NP | PP NP
PP -> P NP | P S
VP -> V | V NP | V PP | V NP PP | VP PP | VP Adv | Adv VP
"""


# the words the function will map are only the words defined in Terminals=
grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # can assume sentence is a string, want all in lowercase -- .lower()
    sentence = sentence.lower()
    # tokenize the string into a list of words
    token = word_tokenize(sentence)
    # use the re library to exculde tokens/words that do not contain letters
    preprocessed = [word for word in token if re.search('[a-z]', word)]
    
    return preprocessed


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # initally started with just 'chunks = []' to test the parser function
    # .subtrees() -- Generate all the subtrees of this tree,
        # restricted to trees matching the filter function
        # -- separate noun phrase chunks
    chunks = []
    for subtree in tree.subtrees(lambda t: t.label() == 'NP'):
                # calls the below definition
                # ensures NO 'NP' overlap
        if not np_c(subtree):
            chunks.append(subtree)
            
    return chunks
    
    
def np_c(subtree):
    # .label() -- Return the node label of the tree.
        # iterates over noun phrases, makes sure the 'NP' itself does not contain other 'NP's as subtrees, e.g. no overlap
        for sub in subtree.subtrees():
            if sub == subtree:
                continue
            elif sub.label() == 'NP':
                return True
        return False


if __name__ == "__main__":
    main()
