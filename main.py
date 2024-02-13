from enum import Enum
import time
import random

Position = tuple[int, int]

MAX_FRUIT_NUM: int = 9
ANT_SPAWN_RATE: float = 0.15
FRUIT_SPAWN_RATE: float = 0.2
SPACE_SPAWN_RATE: float = 0.6

class Entity(Enum):
    ANT = "A"
    FRUIT = "F"
    SPACE = " "

class Ant:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    def _str__(self) -> str:
        return f"({self.x}, {self.y})"

    def position(self) -> Position:
        return (self.x, self.y)

    def move(self) -> Position:
        return (self.x + random.choice([-1, 0, 1]), self.y + random.choice([-1, 0, 1]))

    def reproduce(self) -> "Ant":
        return Ant(self.x + random.choice([-1, 0, 1]), self.y + random.choice([-1, 0, 1]))

class Fruit:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    def _str__(self) -> str:
        return f"({self.x}, {self.y})"

    def position(self) -> Position:
        return (self.x, self.y)

class GameBoard:
    def __init__(self, width: int, heigth: int) -> None:
        self.width = width
        self.heigth = heigth
        self.world: list[list[Entity]] = [
                [ self._select_entity() for _ in range(width)]
                for _ in range(heigth)
                ]
        self.ants: list[Ant] = [
                Ant(x, y)
                for x, line in enumerate(self.world)
                for y, entity in enumerate(line)
                if entity == Entity.ANT
                ]
        if len(self.ants) == 0:
            raise Exception("No ants spawned on the map")
        self.fruits: list[Fruit] = [
                Fruit(x, y)
                for x, line in enumerate(self.world)
                for y, entity in enumerate(line)
                if entity == Entity.FRUIT
                ]
        if len(self.fruits) == 0:
            raise Exception("No fruits spawned on the map")
    def _can_be_placed(self, x: int, y: int) -> bool:
        return 0 <= x < self.heigth and 0 <= y < self.width and self.world[x][y] == Entity.SPACE

    def _select_entity(self,
             ant_mod: float = ANT_SPAWN_RATE,
             fruit_mod: float = FRUIT_SPAWN_RATE,
             space_mod: float = SPACE_SPAWN_RATE) -> Entity:

        ant_chance: float = random.random() * ant_mod
        fruit_chance: float = random.random() * fruit_mod

        if ant_chance == fruit_chance:
            return Entity.SPACE

        space_chance: float = random.random() * space_mod
        chosen: float = max(ant_chance, fruit_chance, space_chance)

        if chosen == ant_chance:
            return Entity.ANT
        elif chosen == fruit_chance:
            return Entity.FRUIT
        else:
            return Entity.SPACE
        
    def _move_ants(self) -> list[tuple[int, Position]]:
        all_moves = {
                index: pos
                for index, ant, in enumerate(self.ants)
                if self._can_be_placed(*(pos:=ant.move()))
                }
        return [ pair for pair in all_moves.items() if pair[1] in set(all_moves.values()) ]

    def _reproduce_ants(self) -> None:
        for ant in self.ants:
            new_ant = ant.reproduce()
            if not self._can_be_placed(x:=new_ant.x, y:=new_ant.y):
                continue
            self.world[x][y] = Entity.ANT
            self.ants.append(new_ant)
        
    def _update_ants(self, other_ants: list[tuple[int, Position]]) -> None:
        for index, new_pos in other_ants:
            x, y = self.ants[index].position()
            self.world[x][y] = Entity.SPACE
            x, y = new_pos
            self.world[x][y] = Entity.ANT
            self.ants[index].x = x
            self.ants[index].y = y

            
    def _update_fruits(self) -> None:
        if len(self.fruits) == 0:
            return
        to_pop = [
                index
                for index, fruit in enumerate(self.fruits)
                for ant in self.ants
                if ant.position() == fruit.position()
                ]
        to_pop.reverse()
        for index in to_pop:
            self.fruits.pop(index)

    def _spawn_fruits(self) -> None:
        #If the fruit number fall to 1 it means almost all tiles are captured by ants
        if not (1 < len(self.fruits) < MAX_FRUIT_NUM):
            return
        x, y = random.choice([
            (x, y)
            for x, line in enumerate(self.world)
            for y, tile in enumerate(line)
            if tile == Entity.SPACE
            ])
        self.world[x][y] = Entity.FRUIT
        self.fruits.append(Fruit(x, y))

    def print_world(self) -> None:
        print(self.width * "-")
        for line in self.world:
            print("".join([tile.value for tile in line]))
        print(self.width * "-")

    def main_loop(self) -> None:
        self._update_ants(self._move_ants())
        self._reproduce_ants()
        self._update_fruits()
        self._spawn_fruits()
        self.print_world()

def main():
    game = GameBoard(5, 5)
    while True:
        game.main_loop()
        time.sleep(1)
if __name__ == "__main__":
    main()
