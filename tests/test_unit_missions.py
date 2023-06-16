import unittest

from game.baseTypes import HandicapType
from game.civilizations import LeaderType
from game.game import GameModel
from game.players import Player
from game.states.victories import VictoryType
from game.unitMissions import UnitMission
from game.unitTypes import UnitType, UnitMissionType
from game.units import Unit
from map.base import HexPoint
from map.generation import MapOptions, MapGenerator
from map.path_finding.finder import MoveTypeIgnoreUnitsOptions, MoveTypeIgnoreUnitsPathfinderDataSource, AStarPathfinder
from map.types import MapSize, TerrainType, MapType, UnitMovementType
from tests.testBasics import MapModelMock, UserInterfaceMock


class TestUnitMissions(unittest.TestCase):
    def test_follow_path(self):

        # GIVEN
        aiPlayer = Player(LeaderType.victoria, human=False)
        aiPlayer.initialize()

        mapModel = MapModelMock(MapSize.small, TerrainType.grass)

        mapOptions = MapOptions(MapSize.duel, MapType.continents, LeaderType.alexander, [LeaderType.victoria])

        mapGenerator = MapGenerator(mapOptions)
        mapGenerator._identifyContinents(mapModel)
        mapGenerator._identifyOceans(mapModel)
        mapGenerator._identifyStartPositions(mapModel)

        gameModel = GameModel(
            victoryTypes=[VictoryType.domination],
            handicap=HandicapType.king,
            turnsElapsed=0,
            players=[aiPlayer],
            map=mapModel
        )

        # add UI
        gameModel.userInterface = UserInterfaceMock()

        # AI units
        warriorUnit = Unit(HexPoint(2, 2), UnitType.warrior, aiPlayer)
        gameModel.addUnit(warriorUnit)

        mapModel.discover(aiPlayer, gameModel)

        datasource_options = MoveTypeIgnoreUnitsOptions(ignore_sight=True, can_embark=False, can_enter_ocean=False)
        datasource = MoveTypeIgnoreUnitsPathfinderDataSource(mapModel, UnitMovementType.walk, aiPlayer, datasource_options)
        finder = AStarPathfinder(datasource)

        path = finder.shortestPath(HexPoint(2, 2), HexPoint(4, 2))

        # WHEN
        warriorUnit.pushMission(UnitMission(UnitMissionType.followPath, path=path), simulation=gameModel)

        warriorUnit.doTurn(gameModel)
        warriorUnit.doTurn(gameModel)

        # THEN
        self.assertEqual(warriorUnit.location, HexPoint(4, 2))
        self.assertEqual(warriorUnit.peekMission(), None)

