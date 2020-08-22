import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page a random surfer would visit next,
    given a current page [a corpus of pages] and a damping factor.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # corpus -- Python dictionary [dict()]  mapping a [page] name to a set of all pages linked [ link ] to by that page
    # 1 - d probability of choosing a page at random is split evenly among all N possible pages
    #                                                                   [ len(corpus) ]
    t_mod = {}
    # initial is 0, add to t_mod dictionary
    for a_page in corpus:
        t_mod[a_page] = 0
    # probability all pages randomly picked, from background info
    prob_rand = (1 - damping_factor) / len(corpus)
    for a_page in corpus:
        # += adds to a variable in the pre-made dictionary
        t_mod[a_page] += prob_rand
    # probability a linked page will be picked
    if len(corpus[page]) != 0:
        prob_link = damping_factor / len(corpus[page])
        for linkpage in corpus[page]:
            t_mod[linkpage] += prob_link
    # normalize, all values sum to 1
    sum = 0 
    for a_page in t_mod:
        sum += t_mod[a_page]
    for a_page in t_mod:
        t_mod[a_page] /= sum

    return t_mod


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # stores the pageranks of the sample pages
    sample_rank = {}
    for page in corpus:
        # initally set to 0
        sample_rank[page] = 0
    # refer to random functions in python for the nuances between .choice and .choices
    page = random.choice(list(corpus))
    # add the randomly chosen page
    sample_rank[page] += 1
    # loop n times, each loop pick a new page
    for _ in range(n):
        # loop through the transition model
        model = transition_model(corpus, page, damping_factor)
        # pages and weights for the .choices function
        pages = []
        weights = []
        for page in model:
            pages.append(page)
            weights.append(model[page])
        page = random.choices(pages, weights)
        page = page[0]
        # add the page and rank to the dictionary
        sample_rank[page] += 1

    # normalize, sum of all pageranks is 1
    # same normalization for the transition model
    sum = 0
    for page in sample_rank:
        # all the pagerank values to the dictionary
        sum += sample_rank[page]
    for page in sample_rank:
        # divide all pagerank values in the sample_rank dictionary by the sum to normalize, basically a proportion
        sample_rank[page] /= sum

    return sample_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    iterate_rank = {}
    # new dictionary and assign inital values to 1/n, not 0 unlike in sample
    for a_page in corpus:
        iterate_rank[a_page] = 1 / len(corpus)

    d = damping_factor
    n = len(corpus)
    # new dictionary to keep track of changes in values because the previous way i had .copy was overwriting my loop
    iterate_rank_c = {}
    # string 'r' -- stands for a specific page
    for r in iterate_rank:
        iterate_rank_c[r] = 0
    
    repeat = True
    # float("inf") takes care of that problem i had before when all values ended up being inf
    change = float("inf")
    while repeat:
        for r in iterate_rank:
            if change <= 0.001:
                iterate_rank_c[r] = 1
            # loop done when for all values 't' in the iterable converge, returns True [in this case repeat=False]
            # all(i: Iterable[object]) Return True if bool(x) is True for all values x in the iterable. If the iterable is empty, return True.
            if all(t == 1 for t in iterate_rank_c.values()):
                repeat = False
            # the equation in background info
            sigma = 0 
            # string 'y' -- all pages 'y' that point to page 'r'
            for y in link_pages(corpus, r):
                sigma += iterate_rank[y] / num_links(corpus, y)
            
            old_iterate = iterate_rank[r]

            iterate_rank[r] = (1 - d)/n + d * sigma

            change = abs(old_iterate - iterate_rank[r])
    # NORMALIZE
    sum = 0 
    for page in iterate_rank:
        sum += iterate_rank[page]
    for page in iterate_rank:
        # divide pagerank values by sum to normalize, proportion type thing to sum to 1
        iterate_rank[page] /= sum

    return iterate_rank

def link_pages(corpus, r):
    # list of all pages y that point to page r
    link_pages = []
    # iterate over y
    for y in corpus:
        if r in corpus[y]:
            # if page y links to page r, append to link_pages
            # refer to the nuances between .add and .append, usually end up using .append
            link_pages.append(y)
    return link_pages

def num_links(corpus, y):
    # if a page has NO links, pretend links to every page, as described in background
    if len(corpus[y]) == 0:
        return len(corpus)
    return len(corpus[y])


if __name__ == "__main__":
    main()
