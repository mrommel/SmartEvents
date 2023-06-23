import unittest

from game.baseTypes import HandicapType
from game.cities import City
from game.civilizations import LeaderType
from game.game import GameModel
from game.players import Player
from game.promotions import UnitPromotionType, UnitPromotions
from game.states.ages import AgeType
from game.states.dedications import DedicationType
from game.states.victories import VictoryType
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint
from map.types import TerrainType
from tests.testBasics import MapModelMock, UserInterfaceMock


class TestUnitPromotions(unittest.TestCase):
	def test_possiblePromotions_melee(self):
		# GIVEN
		playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		playerTrajan.initialize()
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, playerTrajan)
		promotions = UnitPromotions(warrior)

		# WHEN
		initialPromotions = promotions.possiblePromotions()

		promotions.earnPromotion(UnitPromotionType.battlecry)
		promotions.earnPromotion(UnitPromotionType.tortoise)
		secondPromotions = promotions.possiblePromotions()

		# THEN
		self.assertEqual(initialPromotions, [UnitPromotionType.embarkation, UnitPromotionType.healthBoostMelee,
		                                     UnitPromotionType.battlecry, UnitPromotionType.tortoise])
		self.assertEqual(secondPromotions, [UnitPromotionType.embarkation, UnitPromotionType.healthBoostMelee,
		                                    UnitPromotionType.commando, UnitPromotionType.amphibious,
		                                    UnitPromotionType.zweihander])


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
		missionary = Unit(HexPoint(5, 7), UnitType.missionary, self.playerTrajan)
		cavalry = Unit(HexPoint(5, 8), UnitType.horseman, self.playerTrajan)

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
		maxMovesBuilderGoldenAgeExodusOfTheEvangelists = missionary.maxMoves(self.simulation)

		# reset
		self.playerTrajan._currentAgeValue = AgeType.normal
		self.playerTrajan._currentDedicationsValue = []

		# promotion commando
		self.assertTrue(warrior.doPromote(UnitPromotionType.battlecry, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.commando, self.simulation))
		maxMovesWarriorCommando = warrior.maxMoves(self.simulation)

		# promotion pursuit
		cavalry._promotions._promotions = []
		self.assertTrue(cavalry.doPromote(UnitPromotionType.caparison, self.simulation))
		self.assertTrue(cavalry.doPromote(UnitPromotionType.depredation, self.simulation))
		self.assertTrue(cavalry.doPromote(UnitPromotionType.pursuit, self.simulation))
		maxMovesCavalryPursuit = cavalry.maxMoves(self.simulation)

		# THEN
		self.assertEqual(maxMovesWarriorNormal, 2)
		self.assertEqual(maxMovesBuilderNormal, 2)
		self.assertEqual(maxMovesBuilderGoldenAgeMonumentality, 4)
		self.assertEqual(maxMovesBuilderGoldenAgeExodusOfTheEvangelists, 5)

		self.assertEqual(maxMovesWarriorCommando, 3)
		self.assertEqual(maxMovesCavalryPursuit, 5)

		# fixme more conditions

	def test_readyToMove(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		readyToMoveNormal = warrior.readyToMove()

		# garrison
		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)
		warrior.doGarrison(self.simulation)
		readyToMoveGarrisoned = warrior.readyToMove()

		# THEN
		self.assertTrue(readyToMoveNormal)
		self.assertFalse(readyToMoveGarrisoned)
