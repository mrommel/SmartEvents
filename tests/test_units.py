import unittest

from game.baseTypes import HandicapType
from game.cities import City
from game.civilizations import LeaderType
from game.game import GameModel
from game.players import Player
from game.states.ages import AgeType
from game.states.builds import BuildType
from game.states.dedications import DedicationType
from game.states.victories import VictoryType
from game.unitMissions import UnitMission
from game.unitTypes import UnitMissionType, UnitType, UnitActivityType, UnitPromotionType
from game.units import Unit
from map.base import HexPoint
from map.improvements import ImprovementType
from map.types import TerrainType
from tests.testBasics import MapModelMock, UserInterfaceMock


class TestUnit(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.mapModel
		)

		self.playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		self.playerTrajan.initialize()
		self.simulation.players.append(self.playerTrajan)

		playerVictoria = Player(leader=LeaderType.victoria, cityState=None, human=True)
		playerVictoria.initialize()
		self.simulation.players.append(playerVictoria)

		# add UI
		self.simulation.userInterface = UserInterfaceMock()

	def test_move(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		warrior.doMoveOnto(HexPoint(6, 5), self.simulation)

		# THEN
		self.assertEqual(warrior.location, HexPoint(6, 5))

	def test_maxMoves(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		builder = Unit(HexPoint(5, 6), UnitType.builder, self.playerTrajan)

		# WHEN
		maxMovesWarriorNormal = warrior.maxMoves(self.simulation)
		maxMovesBuilderNormal = builder.maxMoves(self.simulation)

		# golden age + monumentality
		self.playerTrajan._currentAgeValue = AgeType.golden
		self.playerTrajan._currentDedicationsValue = [DedicationType.monumentality]
		maxMovesBuilderGoldenAgeMonumentality = builder.maxMoves(self.simulation)

		# golden age + exodusOfTheEvangelists
		self.playerTrajan._currentAgeValue = AgeType.golden
		self.playerTrajan._currentDedicationsValue = [DedicationType.exodusOfTheEvangelists]
		maxMovesBuilderGoldenAgeExodusOfTheEvangelists = builder.maxMoves(self.simulation)

		# reset
		self.playerTrajan._currentAgeValue = AgeType.normal
		self.playerTrajan._currentDedicationsValue = []

		# promotion commando
		warrior.doPromote(UnitPromotionType.commando, self.simulation)
		maxMovesWarriorCommando = warrior.maxMoves(self.simulation)

		# THEN
		self.assertEqual(maxMovesWarriorNormal, 2)
		self.assertEqual(maxMovesBuilderNormal, 2)
		self.assertEqual(maxMovesBuilderGoldenAgeMonumentality, 4)
		self.assertEqual(maxMovesBuilderGoldenAgeExodusOfTheEvangelists, 4)
