from enum import Enum
import time
import random

Position = tuple[int, int]

MAX_FRUIT_NUM: int = 9
ANT_SPAWN_RATE: float = 0.25
FRUIT_SPAWN_RATE: float = 0.4
SPACE_SPAWN_RATE: float = 0.6

def unique_only(lt: list)-> None:
    to_pop = list(set([
            j
            for i in range(len(lt))
            for j in range(len(lt))
            if i != j
            if lt[i][1] == lt[j][1]
                           ]))
    to_pop.sort(reverse=True)
    for i in to_pop:
        lt.pop(i)


class Entity(Enum):
    ANT = "A"
    FRUIT = "F"
    SPACE = " "

class Actions(Enum):
    MOVE = "move"
    REPRODUCE = "reproduce"

class Ant:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.actions = {
            Actions.MOVE: lambda self: (self.x + random.choice([-1, 0, 1]), self.y + random.choice([-1, 0, 1])),
            Actions.REPRODUCE: lambda self: (self.x + random.choice([-1, 0, 1]), self.y + random.choice([-1, 0, 1]))
            }
    def set_position(self, x:int, y:int) -> None:
        self.x = x
        self.y = y
    def _str__(self) -> str:
        return f"({self.x}, {self.y})"

    def position(self) -> Position:
        return (self.x, self.y)

    def act(self):
        action = random.choice([Actions.MOVE, Actions.REPRODUCE])
        return (action, self.actions[action](self))

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
        self.actions = {
                Actions.MOVE: lambda index, position: self._move_ant(index, position),
                Actions.REPRODUCE: lambda _, position: self._reproduce_ant(position)
                }
        if len(self.actions) != len(Actions):
            raise Exception("Some functionality specified by Actions wasn't implemented")
        

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

    def _move_ant(self, index: int, position: Position) -> None:
        x, y = self.ants[index].position()
        self.world[x][y] = Entity.SPACE
        x, y = position
        self.ants[index].set_position(x, y)
        self.world[x][y] = Entity.ANT

    def _reproduce_ant(self, position: Position) -> None:
        x, y = position
        self.world[x][y] = Entity.ANT
        self.ants.append(Ant(x,y))

    def _process_ants(self) -> None:
        processes= [
                (index, action)
                for index, ant in enumerate(self.ants)
                if self._can_be_placed(*(action := ant.act())[1])
                ]
        unique_only(processes)
        for process in processes:
            index, action = process
            self.actions[action[0]](index, action[1])


    def main_loop(self) -> None:
        self._process_ants()
        self._update_fruits()
        if  4 < len(self.fruits) < MAX_FRUIT_NUM:
            self._spawn_fruits()
        self.print_world()



def main():
    game = GameBoard(10, 10)
    while(50):
        game.main_loop()
        time.sleep(1)
        

if __name__ == "__main__":
    main()
