import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file. pip3 install pillow is necessary.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        node consistency -- every value in a variable’s domain satisfy the unary constraints
        arc consistency -- ensuring that binary constraints are satisfied
        call backtrack on inially empty assignment to try to calculate solution
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # To remove a value x from the domain of a variable v, 
        # since self.domains is a dictionary mapping variables to sets of values, 
        # can call self.domains[v].remove(x)
        # no return value necessary
        for var in self.domains:
            for word in set(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # self.crossword.overlaps calls any overlap between variables x and y 
        # follow pseudocode idea from lecture notes
        revised = False
        i, j = self.crossword.overlaps[x, y]

        for word_x in set(self.domains[x]):
            delete = True
            
            for word_y in self.domains[y]:
                # if i, j are the same value and the words are not the same
                if word_x[i] == word_y[j] and word_x != word_y:
                    delete = False
            # self.domains[x].remove(word_x) to remove values
            # a value was removed, return true
            if delete:
                self.domains[x].remove(word_x)
                revised = True
        
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # example pseudocode in notes
        # satisfy variables binary constraints
        if arcs is None:
            arcs = []
            for x in self.domains:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))
                
                for x, y in arcs:
                    if self.revise(x, y):
                    # nothing in the domain, no possible values = no solution
                        if len(self.domains[x]) == 0:
                            return False
                # to implement AC3, revise each arc in the queue one at a time. 
                # Any time you make a change to a domain, 
                # need to add additional arcs to your queue to 
                # ensure that other arcs stay consistent
                    # add arcs w to the queue
                for w in self.crossword.neighbors(x) - self.domains[y]:
                    arcs.append((w, x))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # assignment is a dictionary where the keys are Variable objects and the 
        # values are strings representing the words those variables will take on
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False
            if assignment[var] not in self.crossword.words:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used = set()
        # assignment is consistent if it satisfies all of the constraints of the problem
        for x in assignment:
            if assignment[x] not in used:
                used.add(assignment[x])
            else:
                return False
            # if the word length does not satisfy the length of the variable space in the crossword
            if x.length != len(assignment[x]):
                return False
        
            for y in self.crossword.neighbors(x):
                if y in assignment:
                    overlap = self.crossword.overlaps[x, y]
                    # i, j must overlap
                    i, j = overlap
                    # if the letter in the position for word x is 
                    # not the same letter in that same position for word y,
                    # overlap constraint is not consistent
                    if assignment[x][i] != assignment[y][j]:
                        # if the two variables map to the same word, not consistent
                        if assignment[x] == assignment[y]:
                            return False
        # if all constraints met
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # least-constraining values heuristic is computed as the 
        # number of values ruled out for neighboring unassigned variables
            # if assigning var to a particular value results in 
            # eliminating n possible choices for neighboring variables, 
            # order results in ascending order of n

        # n must be a dictionary {dict()} not a list { [] } in order to use .get
        n = dict()
        for value in self.domains[var]:
            # inital condition
            # compute number of values [n] ruled out for neighboring unassigned vars
            n[value] = 0
            # any variable present in assignment already has a value, 
            # therefore shouldn’t be counted
            for neighbor_var in self.crossword.neighbors(var):
                if neighbor_var not in assignment:
                    if value in self.domains[neighbor_var]:
                        # add and equate value to dictionary of eliminating n possible choices
                        n[value] += 1
        # sort a list according to a particular key: Python contains these functions
        # list.sort() method that modifies the list in-place, only defined for lists
        # sorted() builds a new sorted list from an iterable, accepts any iterable
            # sorted(iterable, *, key=None, reverse=False) 
            # -- key should extract a comparison key from each n=iterable
                # key=lambda n: (n[1]) {(n[1])--first n in ascending order}
            # -- key= n.get -- .get returns the value of the item with the specified key
        return sorted(n, key=n.get)


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # MRV heurisitc -- select the variable with the smallest domain
        # degree heuristic -- degree of a node is the number of nodes that are constrained by that particular node
        variables = []
        for var in self.crossword.variables:
            if var not in assignment:
                variables.append([var, len(self.domains[var]), len(self.crossword.neighbors(var))])

        if variables:
            # x[1]-- [1]:ascending order n; -x[2]-- (-):descending order degree
            variables.sort(key=lambda x: (x[1], -x[2]))
            # [0][0] -- multiplying string of length [#] by string of length [#]
            return variables[0][0]
        return None


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        # algorithm is more efficient if 
        # optional: interleave search with inference 
            # as by maintaining arc consistency every time you make a new assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is None:
                    assignment[var] = None
                else:
                    return result
        # no satisfying assignment is possible, function should return None
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
