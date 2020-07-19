import math


class SudokuSolver:
    EMPTY_CELL = 0

    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.chunk_size = int(math.sqrt(self.grid_size))
        self.possibilities_rows = list()
        self.possibilities_columns = list()
        self.possibilities_chunks = list()
        self.grid = None

    def read_grid(self, grid):
        self.possibilities_rows = list()
        self.possibilities_columns = list()
        self.possibilities_chunks = list()
        self.grid = grid
        self.create_rows_possibilities()
        self.create_columns_possibilities()
        self.create_chunks_possibilities()

    def create_rows_possibilities(self):
        for row in self.grid:
            used_numbers = list()
            for cell in row:
                if cell != self.EMPTY_CELL:
                    used_numbers.append(cell)
            not_used_numbers = self.find_complements(used_numbers)
            if not_used_numbers is None:
                self.possibilities_rows = None
                return
            else:
                self.possibilities_rows.append(not_used_numbers)

    def create_columns_possibilities(self):
        for i in range(self.grid_size):
            used_numbers = list()
            for j in range(self.grid_size):
                if self.grid[j][i] != self.EMPTY_CELL:
                    used_numbers.append(self.grid[j][i])
            not_used_numbers = self.find_complements(used_numbers)
            if not_used_numbers is None:
                self.possibilities_columns = None
                return
            else:
                self.possibilities_columns.append(not_used_numbers)

    def create_chunks_possibilities(self):
        for i in range(self.grid_size):
            used_numbers = self.get_chunk_numbers(i)
            not_used_numbers = self.find_complements(used_numbers)
            if not_used_numbers is None:
                self.possibilities_chunks = None
                return
            else:
                self.possibilities_chunks.append(not_used_numbers)

    def solve(self, grid):
        self.read_grid(grid)
        if not self.is_solvable():
            print('Grid is invalid')
            return grid

        while self.solve_step():
            pass

        return grid

    def solve_step(self):
        new_number_added = False
        for row_index in range(self.grid_size):
            for column_index in range(self.grid_size):
                cell = self.grid[row_index][column_index]
                if cell != self.EMPTY_CELL:
                    continue
                candidates = self.get_cell_candidates(row_index, column_index)
                if len(candidates) == 1:
                    self.put_new_number(row_index, column_index, candidates[0])
                    new_number_added = True
                else:
                    for cand in candidates:
                        if not self.can_number_be_somewhere_else_in_row(row_index, column_index, cand) \
                                or not self.can_number_be_somewhere_else_in_column(row_index, column_index, cand) \
                                or not self.can_number_be_somewhere_else_in_chunk(row_index, column_index, cand):
                            self.put_new_number(row_index, column_index, cand)
                            new_number_added = True
                            break

        return new_number_added

    def can_number_be_somewhere_else_in_row(self, row_index, column_index, number):
        for i in range(self.grid_size):
            if column_index == i:
                continue
            num = self.grid[row_index][i]
            if num != self.EMPTY_CELL:
                continue
            candidates = self.get_cell_candidates(row_index, i)
            if number in candidates:
                return True
        return False

    def can_number_be_somewhere_else_in_column(self, row_index, column_index, number):
        for i in range(self.grid_size):
            if row_index == i:
                continue
            num = self.grid[i][column_index]
            if num != self.EMPTY_CELL:
                continue
            candidates = self.get_cell_candidates(i, column_index)
            if number in candidates:
                return True
        return False

    def can_number_be_somewhere_else_in_chunk(self, row_index, column_index, number):
        chunk_id = self.get_chunk_id(row_index, column_index)
        start_row = self.chunk_size * (chunk_id // self.chunk_size)
        start_col = int(self.chunk_size * (chunk_id % self.chunk_size))

        for i in range(start_row, start_row + self.chunk_size):
            for j in range(start_col, start_col + self.chunk_size):
                num = self.grid[i][j]
                if num != self.EMPTY_CELL:
                    continue
                candidates = self.get_cell_candidates(i, j)
                if number in candidates:
                    return True
        return False

    def put_new_number(self, row_index, col_index, number):
        self.possibilities_rows[row_index].remove(number)
        self.possibilities_columns[col_index].remove(number)
        chunk_id = self.get_chunk_id(row_index, col_index)
        self.possibilities_chunks[chunk_id].remove(number)
        self.grid[row_index][col_index] = number

    def get_cell_candidates(self, row_index, column_index):
        row_possibilities = self.possibilities_rows[row_index]
        column_possibilities = self.possibilities_columns[column_index]
        chunk_id = self.get_chunk_id(row_index, column_index)
        chunk_possibilities = self.possibilities_chunks[chunk_id]
        return self.get_intersection(self.get_intersection(row_possibilities, column_possibilities),
                                     chunk_possibilities)

    def get_chunk_id(self, row_index, column_index):
        return (row_index // self.chunk_size) * self.chunk_size + (column_index // self.chunk_size)

    def get_chunk_numbers(self, chunk_id):
        start_row = self.chunk_size * (chunk_id // self.chunk_size)
        start_col = int(self.chunk_size * (chunk_id % self.chunk_size))

        chunk = list()
        for i in range(start_row, start_row + self.chunk_size):
            for j in range(start_col, start_col + self.chunk_size):
                if self.grid[i][j] != self.EMPTY_CELL:
                    chunk.append(self.grid[i][j])
        return chunk

    def find_complements(self, used_numbers):
        possible_values = [item for item in range(1, self.grid_size + 1)]
        for number in used_numbers:
            if number not in possible_values:
                return None
            possible_values.remove(number)
        return possible_values

    def is_solvable(self):
        return self.possibilities_chunks is not None \
               and self.possibilities_columns is not None \
               and self.possibilities_rows is not None

    @staticmethod
    def get_intersection(list1, list2):
        intersection = list()
        for i in list1:
            for j in list2:
                if i == j:
                    intersection.append(j)
                    break
        return intersection

    @staticmethod
    def print_grid(grid):
        for row in grid:
            print(row)


if __name__ == "__main__":
    table = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],

        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],

        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    sudokuSolver = SudokuSolver(9)
    solve_table = sudokuSolver.solve(table)
    sudokuSolver.print_grid(solve_table)
