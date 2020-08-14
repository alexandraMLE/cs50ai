import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """
    # the AI is playing the game, not me
    # Trying to perform model checking on this type of problem would quickly become intractable: on an 8x8 grid, Microsoft's Beginner, we’d have 64 variables, and therefore 2^64 possible models to check – far too many for a computer to compute in any reasonable amount of time.
            # for example Or(A, B, C, D, E, F, G, H) is now going to be represented by {A, B, C, D, E, F, G, H} = 1; the Or statement for only 1 mine in the set would by incredibly long because I would have to specify And(Not(A), B, Not(C), etc)

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
            # i is the row number, 0 to height-1
            # j is the column number, 0 to width-1
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """
    # the structure is {sentence} = count; {sentence} is a set of cells on the board, and count representing the number count of how many of those cells are mines
                # ex: {A, B, C, D, E, F, G, H} = 1
    # any time the number of cells is equal to the count, we know that all of that sentence’s cells must be mines
    # More generally, any time we have two sentences set1 = count1 and set2 = count2 where set1 is a subset of set2, then we can construct the new sentence set2 - set1 = count2 - count1.

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # under what circumstances do you know for sure that a sentence’s cells are mines?
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # under what circumstances do you know for sure that a sentence’s cells are safe? when the count is 0 (0 means no mines)
        if self.count == 0:
            return self.cells
        else:
            return set()


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1
    

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    # DEFINE THE NEIGHBORS FOR ADDING NEW SENTENCES
    def the_neighbors(self, cell):
        # returns the neighbors of cell, inital set
        # loop over row and columns, watch your range: recall i (height-1), aka height-1 is 0 (first cell) & j (width-1), same idea
            # range for i will be from cell(0) to cell(+1), ditto for j
                # i.e. cell0 = height - 1 & cell+1 = height - 1; solve for height
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # do not want the cell, i want the boundary for the neighbors, pay attention
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.add((i, j))
        return neighbors
        
    
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as one of the moves made
        self.moves_made.add(cell)
        
        # 2) mark the cell as a safe cell, self.safes, updating other sentences with the cell, mark_safe
        if cell not in self.safes:
            self.mark_safe(cell)
            
        # 3) new SENTENCE to AI KB based on 'cell' and 'count' to indicate the count of the cell's NEIGHBORS that are mines, only include still undetermined cells -- set2 - set1 = count2 - count1; loop through self.mines & mark_mine and self.safes & mark_safe; add to self.knowledge
        
        # NEED TO DEFINE THE NEIGHBORS ABOVE
        new_sentence = Sentence(self.the_neighbors(cell), count)
        for mine in self.mines:
            new_sentence.mark_mine(mine)
        for safe in self.safes:
            new_sentence.mark_safe(safe)
            
        self.knowledge.append(new_sentence)
        
        # 4) mark additional cells as mines or safes and add to self.knowledge
        new_mines = set()
        new_safes = set()
        for sentence in self.knowledge:
            for cell in sentence.known_mines():
                new_mines.add(cell)
            for cell in sentence.known_safes():
                new_safes.add(cell)
        
        for mine in new_mines:
            self.mark_mine(mine)
        for safe in new_safes:
            self.mark_safe(safe)
        
        # 5) add new sentences if they can be inferred [inferred_cells] by existing AI KB in self.knowledge-- old_sentence, new_sentence, new_inferences
        old_sentence = new_sentence
        new_inferences = []
        
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
            elif old_sentence == sentence:
                break
            # only include still undetermined cells -- set2 - set1 = count2 - count1 [inferred_cells and inferred_count]
            elif old_sentence.cells <= sentence.cells:
                inferred_cells = sentence.cells - old_sentence.cells
                inferred_count = sentence.count - old_sentence.count
                
                # .append new_inferences to Sentence set.
                new_inferences.append(Sentence(inferred_cells, inferred_count))
                
            # remember that old_sentence is also in sentence
            old_sentence = sentence
            
        # add new_interences to self.knowledge [ += ]
        self.knowledge += new_inferences
        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        if len(self.safes) == 0:
            return None
        
        for safe in self.safes:
            if safe not in self.mines and safe not in self.moves_made:
                print(safe)
                return safe
        return None
        

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height - 1):
            for j in range(self.width - 1):
                cell = (i, j)
                if cell not in self.mines and cell not in self.moves_made:
                    return cell
        return None
