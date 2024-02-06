import random
import time
from os import system

BOUNDARY_X = 5
BOUNDARY_Y = 5

ANT: str = "A"
FRUIT: str = "F"
EMPTY: str = " "

class Ant:
    pass

class GameBoard:

    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.world = [[self.select_entity() for _ in range(self.width)] for _ in range(self.height)]
        self.antList = [ [tile == ANT for tile in line] for line in self.world ]
        self.fruitList = [ [tile == FRUIT for tile in line] for line in self.world ]
        self.current_ant_index = 0
    
    def select_entity(self, ant_mod: float = 0.2, fruit_mod: float = 0.3, space_mod: float = 0.5) -> str:
        ant_chance: float = random.random() * ant_mod
        fruit_chance: float = random.random() * fruit_mod
        if ant_chance == fruit_chance:
            return EMPTY
        space_chance: float = random.random() * space_mod
        chosen: float = max(ant_chance, fruit_chance, space_chance)
        if chosen == ant_chance:
            return ANT
        elif chosen == fruit_chance:
            return FRUIT
        else:
            return EMPTY
    
    def get_new_fruit_location(self, new_row: int, new_col: int, antList: list[list[bool]]) -> tuple[int, int]:
        return random.choice([
                (x, y)
                for x, line in enumerate(self.world)
                for y, line in enumerate(line)
                if x != new_row and y != new_col
                if not antList[x][y] and not self.fruitList[x][y]
            ])
                 
    def print_world(self) -> None:
        system('cls')
        for line in self.world:
            print(line)
        print("-"*(self.width*5))
    
    def move_ants(self):
        antList = [row.copy() for row in self.antList]

        for row in range(len(self.world)):
            for col in range(len(self.world[row])):
                if self.antList[row][col]: 
                    possible_moves = []

                    if row - 1 >= 0 and not antList[row - 1][col]:
                        possible_moves.append((row - 1, col))
                    if row + 1 < len(self.world) and not antList[row + 1][col]:
                        possible_moves.append((row + 1, col))
                    if col - 1 >= 0 and not antList[row][col - 1]:
                        possible_moves.append((row, col - 1))
                    if col + 1 < len(self.world[row]) and not antList[row][col + 1]:
                        possible_moves.append((row, col + 1)) 

                    if possible_moves:
                        new_row, new_col = random.choice(possible_moves)

                        antList[row][col] = False
                        self.world[row][col] = EMPTY
                        antList[new_row][new_col] = True
                        self.world[new_row][new_col] = ANT

                        if self.fruitList[new_row][new_col]:
                            #print(f"Ant at ({row}, {col}) ate a fruit!")
                            self.fruitList[new_row][new_col] = False 

                            respawn_row, respawn_col = self.get_new_fruit_location(new_row, new_col, antList)

                            self.fruitList[respawn_row][respawn_col] = True
                            self.world[respawn_row][respawn_col] = FRUIT

        self.antList = antList

def main() -> None:
    World = GameBoard(BOUNDARY_X, BOUNDARY_Y)
    while True:
        World.print_world()
        World.move_ants()
        time.sleep(1)  

if __name__ == "__main__":
    main()
