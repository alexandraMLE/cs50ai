import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene, the probability that i know nothing about the kid's parents
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability, gene mutates from being the gene in question to not being that gene, and vice versa
    "mutation": 0.01
}


def main():

    # Check for proper usage; main loads data from a file into a dictionary 'people'
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # people maps each person’s name to another dictionary containing information about them
    # Keep track of gene and trait probabilities for each person, initially set to 0
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    # probabilities dictionary is created using a Python dictionary comprehension, which in this case creates one key/value pair for each person in our dictionary of people
    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # people is a dictionary of people: keys represent names, values are dictionaries that contain mother and father keys
    j_probability = 1
    # create a zero_genes like the already made one_gene and two_genes
    zero_genes = set()
    # keys represent names, values are dictionaries containing mother & father keys
    for i in people.keys():
        if i not in one_gene and i not in two_genes:
            # .add(i) puts i into the set
            zero_genes.add(i)

    # zero_genes
    for i in zero_genes:
        if people[i]["mother"] == None and people[i]["father"] == None:
            # no parents listed, use PROBS["gene"]
            probabil = PROBS["gene"][0]
        # difference between elif and else
        elif people[i]["father"] != None and people[i]["mother"] != None:
            probabil = 1
            # for ease, mother and father variables
            mother = people[i]["mother"]
            father = people[i]["father"]
            # with parents, each parent will pass one of their two genes on to their child randomly, 
            # PROBS["mutation"] chance that it mutates (from being the gene to not being the gene, vice versa)
            # i.e. thinking -- if there is zero gene, 1-PROBS["mutation"]  
            # *= multiplication
            # consider all options: mother zero*father in zero,one,two; mother in one*father in zero,one,two; mother in two*father in zero,one,two
            if mother in zero_genes and father in zero_genes:
                probabil *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
            elif mother in zero_genes and father in one_gene:
                # one_gene: 50% chance of passing the gene to kid
                probabil *= (1 - PROBS["mutation"]) * 0.5
            elif mother in zero_genes and father in two_genes:
                # two_genes: parent will pass one of two genes to kid randomly, PROBS["mutation"] chance that it mutates
                probabil *= (1 - PROBS["mutation"]) * (PROBS["mutation"])
            
            elif mother in one_gene and father in zero_genes:
                probabil *= 0.5 * (1 - PROBS["mutation"])
            elif mother in one_gene and father in one_gene:
                probabil *= 0.5 * 0.5
            elif mother in one_gene and father in two_genes:
                probabil *= 0.5 * (PROBS["mutation"])

            elif mother in two_genes and father in zero_genes:
                probabil *= (PROBS["mutation"]) * (1 - PROBS["mutation"])
            elif mother in two_genes and father in one_gene:
                probabil *= (PROBS["mutation"]) * 0.5
            elif mother in two_genes and father in two_genes:
                probabil *= (PROBS["mutation"]) * (PROBS["mutation"])
        # PROBS["trait"] to compute the probability that a person does or does not have a particular trait
        # TRUE or FALSE
        if i in have_trait:
            probabil *= PROBS["trait"][0][True]
        elif i not in have_trait:
            probabil *= PROBS["trait"][0][False]
        j_probability *= probabil

    # one_gene -- kid WILL HAVE ONE GENE
    for i in one_gene:
        if people[i]["mother"] == None and people[i]["father"] == None:
            probabil = PROBS["gene"][1]
        elif people[i]["mother"] != None and people[i]["father"] != None:
            probabil = 1
            mother = people[i]["mother"]
            father = people[i]["father"]
        # probability of the KID HAVING 1 GENE if mother * father
            if mother in zero_genes and father in zero_genes:
                probabil *= (1 - PROBS["mutation"]) * PROBS["mutation"] + (1 - PROBS["mutation"]) * PROBS["mutation"]
            elif mother in zero_genes and father in one_gene:
                probabil *= (1 - PROBS["mutation"]) * 0.5 + PROBS["mutation"] * 0.5 
            elif mother in zero_genes and father in two_genes:
                probabil *= (PROBS["mutation"]) * (PROBS["mutation"]) + (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
        # consider all scenarios with mutation
            elif mother in one_gene and father in zero_genes:
                probabil *= 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]
            elif mother in one_gene and father in one_gene:
                probabil *= 0.5 * 0.5 + 0.5 * 0.5
        # this one is confusing
            elif mother in one_gene and father in two_genes:
                probabil *= 0.5 * (PROBS["mutation"]) + 0.5 * (1 - PROBS["mutation"])

            elif mother in two_genes and father in zero_genes:
                probabil *= (PROBS["mutation"]) * (PROBS["mutation"]) + (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
        # confusing
            elif mother in two_genes and father in one_gene:
                probabil *= (PROBS["mutation"]) * 0.5 + (1 - PROBS["mutation"]) * 0.5 
            elif mother in two_genes and father in two_genes:
                probabil *= (PROBS["mutation"]) * (1 - PROBS["mutation"]) + (PROBS["mutation"]) * (1 - PROBS["mutation"])

        if i in have_trait:
            probabil *= PROBS["trait"][1][True]
        elif i not in have_trait:
            probabil *= PROBS["trait"][1][False]
        j_probability *= probabil
    
    # two_genes -- kid has both genes
    for i in two_genes:
        if people[i]["mother"] == None and people[i]["father"] == None:
            probabil = PROBS["gene"][2]
        elif people[i]["mother"] != None and people[i]["father"] != None:
            probabil = 1
            mother = people[i]["mother"]
            father = people[i]["father"]

            if mother in zero_genes and father in zero_genes:
                probabil *= (PROBS["mutation"]) * (PROBS["mutation"])
            elif mother in zero_genes and father in one_gene:
                # one_gene: 50% chance of passing the gene to kid
                probabil *= (PROBS["mutation"]) * 0.5
            elif mother in zero_genes and father in two_genes:
                # two_genes: parent will pass one of two genes to kid randomly, PROBS["mutation"] chance that it mutates
                probabil *= (PROBS["mutation"]) * (1 - PROBS["mutation"])
            
            elif mother in one_gene and father in zero_genes:
                probabil *= 0.5 * (PROBS["mutation"])
            elif mother in one_gene and father in one_gene:
                probabil *= 0.5 * 0.5
            elif mother in one_gene and father in two_genes:
                probabil *= 0.5 * (1 - PROBS["mutation"])

            elif mother in two_genes and father in zero_genes:
                probabil *= (1 - PROBS["mutation"]) * (PROBS["mutation"])
            elif mother in two_genes and father in one_gene:
                probabil *= (1 - PROBS["mutation"]) * 0.5
            elif mother in two_genes and father in two_genes:
                probabil *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])

        if i in have_trait:
            probabil *= PROBS["trait"][2][True]
        elif i not in have_trait:
            probabil *= PROBS["trait"][2][False]
        j_probability *= probabil

    return j_probability
        

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # update probabilities[person]["gene"] and probabilities[person]["trait"] by adding p to the appropriate value
    # function should not return any value
    for person in probabilities:
        if person not in two_genes and person not in one_gene:
            probabilities[person]["gene"][0] += p
        elif person in one_gene:
            probabilities[person]["gene"][1] += p
        else:
            probabilities[person]["gene"][2] += p
        
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        elif person not in have_trait:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # divide and add [ /= ] individual probabilities[person]["gene"] by total .value of genes
    # divide and add [ /= ] individual probabilities[person]["trait"] by total .value of traits
        # this makes relative proportions that sum to 1
    for person in probabilities:

        t_genes = sum(probabilities[person]["gene"].values())
        for i in probabilities[person]["gene"]:
            probabilities[person]["gene"][i] /= t_genes

        t_traits = sum(probabilities[person]["trait"].values())  
        for i in probabilities[person]["trait"]:
            probabilities[person]["trait"][i] /= t_traits


if __name__ == "__main__":
    main()
