import gettext

from game.base_types import LeaderType
from map.generation import MapGenerator, MapOptions
from map.types import MapSize, MapType
from simulation import Simulation
from utils.translation import gettext_lazy as _

if __name__ == '__main__':
    print(_("SmartEvents"))

    def callbackFunc(state):
        print(f'Progress: {state.value} - {state.message}')

    humanLeader = LeaderType.TRAJAN
    options = MapOptions(MapSize.TINY, MapType.CONTINENTS, humanLeader)
    generator = MapGenerator(options)

    map = generator.generate(callbackFunc)

    simulation = Simulation(map)
    simulation.initialize(humanLeader)

    # add players
    # simulation.players.append(Player(LeaderType.ALEXANDER, True, False))
    # simulation.players.append(Player(LeaderType.TRAJAN, False, False))

    # run simulation
    for _ in range(10):
        simulation.turn()
