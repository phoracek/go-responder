import uuid

import time


class MatchNotFound(Exception):
    pass


class StoneNotFound(Exception):
    pass


class OutOfRange(Exception):
    pass


class InvalidMove(Exception):
    pass


class MatchManager:
    def __init__(self):
        self.matches = {}

    def create_match(self, board_size):
        match_id = uuid.uuid1().hex
        self.matches[match_id] = Match(board_size)
        return match_id

    def create_custom_match(self, name, board_size):
        self.matches[name] = Match(board_size)

    def access_match(self, match_id):
        try:
            return self.matches[match_id]
        except:
            raise MatchNotFound


# TODO: stone authentication.
class Match:
    def __init__(self, board_size):
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.board_size = board_size
        self.winner = 0
        self.on_turn = 1
        self.num_of_passes = 0

        self.debug_history = []

    def get_board(self):
        """
        Returns the game board.
        """
        return self.board

    def to_string(self, x):
        res = ""
        for i in x:
            for j in i:
                res += str(j)
            res += "\n"
        return res

    def get_board_string(self):
        """
        Returns the game board as a string.
        """
        res = ""
        for i in self.get_board():
            for j in i:
                res += str(j)
            res += "\n"
        return res

    def place_stone(self, x, y, stone):
        """
        Places stone on the game board. Returns True if successful.
        """
        if stone == self.on_turn:
            if not (0 <= x < self.board_size and 0 <= y < self.board_size):
                raise OutOfRange
            if not self.board[y][x] == 0:
                raise InvalidMove

            # check recursion??? some rule or something
            board_check = [[j for j in i] for i in self.board]

            board_check[y][x] = stone
            if self.__flood(x, y, stone, board_check, []):
                self.num_of_passes = 0  # for ending the game
                self.__switch_on_turn()
                self.board[y][x] = stone
                self.__check_take(self.on_turn)

                self.debug_history.append((x, y, stone))  # DEBUG

                return True

        return False

    def __take(self, area):
        """
        Clears stones in area from the board.
        """
        for x, y in area:
            self.board[y][x] = 0

    def __flood_part(self, x, y, stone, board_check, record):
        """
        Sub-function of __flood(). Returns False if there is no escape (the stone should be taken).
        """
        if board_check[y][x] == 0:
            return True
        elif board_check[y][x] == stone:
            if self.__flood(x, y, stone, board_check, record):
                return True
        return False

    def __flood(self, x, y, stone, board_check, record):
        res = False
        """
        Returns False if there is no escape (the stone should be taken).
        """
        board_check[y][x] = 3
        record.append((x, y))

        if 0 < y:
            if self.__flood_part(x, y - 1, stone, board_check, record):
                res = True
        if y < self.board_size - 1:
            if self.__flood_part(x, y + 1, stone, board_check, record):
                res = True
        if 0 < x:
            if self.__flood_part(x - 1, y, stone, board_check, record):
                res = True
        if x < self.board_size - 1:
            if self.__flood_part(x + 1, y, stone, board_check, record):
                res = True

        return res

    # TODO: zkontrolovat jestli nema byt public
    def __check_take(self, stone):
        """
        Checks if stones should be removed, and removes them.
        """
        start = time.clock()

        board_check = [[n for n in m] for m in self.board]

        for i in range(self.board_size):
            for j in range(self.board_size):
                if board_check[j][i] == stone:
                    last_take = []
                    if not self.__flood(i, j, stone, board_check, last_take):
                        self.__take(last_take)
        print time.clock() - start

    def get_winner(self):
        return self.winner

    def get_on_turn(self):
        return self.on_turn

    # TODO: make private
    def __switch_on_turn(self):
        if self.on_turn == 1:
            self.on_turn = 2
        else:
            self.on_turn = 1

    # TODO: left to implement, snad....
    def __count_win(self):
        black = sum([sum([1 if i == 1 else 0 for i in row]) for row in self.board])
        white = sum([sum([1 if i == 2 else 0 for i in row]) for row in self.board])
        return 1 if black > white else 2

    def pass_turn(self, stone):
        if self.on_turn == stone:
            self.num_of_passes += 1
            self.__switch_on_turn()
            if self.num_of_passes >= 2:
                self.on_turn = 0
                self.winner = self.__count_win()
                return True
        return False

    def forfeit(self, stone):
        self.on_turn = 0
        if stone == 1:
            self.winner = 2
        else:
            self.winner = 1
