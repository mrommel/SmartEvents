import unittest

from game.ai.economicStrategies import EconomicStrategyType
from game.ai.economics import EconomicStrategyAdoptions
from game.ai.homeland import HomelandUnit
from game.civilizations import LeaderType
from game.players import Player
from game.states.builds import BuildType
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint
from map.types import TerrainType
from tests.testBasics import MapMock


class TestHomeland(unittest.TestCase):
	def test_homelandUnit_eq(self):
		# GIVEN
		player = Player(LeaderType.alexander)
		player.initialize()

		unit0 = Unit(location=HexPoint(1, 1), unitType=UnitType.settler, player=player)
		homelandUnit0 = HomelandUnit(unit0)

		unit1 = Unit(location=HexPoint(1, 2), unitType=UnitType.settler, player=player)
		homelandUnit1 = HomelandUnit(unit1)

		unit2 = Unit(location=HexPoint(1, 3), unitType=UnitType.settler, player=player)
		homelandUnit2 = HomelandUnit(unit2)

		# WHEN
		homelandUnit0.movesToTarget = 3
		homelandUnit1.movesToTarget = 3
		homelandUnit2.movesToTarget = 5

		# THEN
		self.assertTrue(homelandUnit0 == homelandUnit1)
		self.assertTrue(homelandUnit0 == homelandUnit0)
		self.assertFalse(homelandUnit0 == homelandUnit2)
		self.assertFalse(homelandUnit1 == homelandUnit2)

	def test_homelandUnit_lt(self):
		# GIVEN
		player = Player(LeaderType.alexander)
		player.initialize()

		unit0 = Unit(location=HexPoint(1, 1), unitType=UnitType.settler, player=player)
		homelandUnit0 = HomelandUnit(unit0)

		unit1 = Unit(location=HexPoint(1, 2), unitType=UnitType.settler, player=player)
		homelandUnit1 = HomelandUnit(unit1)

		unit2 = Unit(location=HexPoint(1, 3), unitType=UnitType.settler, player=player)
		homelandUnit2 = HomelandUnit(unit2)

		# WHEN
		homelandUnit0.movesToTarget = 3
		homelandUnit1.movesToTarget = 3
		homelandUnit2.movesToTarget = 5

		# THEN
		self.assertFalse(homelandUnit0 < homelandUnit1)
		self.assertTrue(homelandUnit0 < homelandUnit2)
		self.assertTrue(homelandUnit1 < homelandUnit2)
		self.assertFalse(homelandUnit1 < homelandUnit1)


class TestEconomics(unittest.TestCase):
	def test_adoption(self):
		# GIVEN
		adoptions = EconomicStrategyAdoptions()

		# WHEN
		adoptions.adopt(EconomicStrategyType.losingMoney, turnOfAdoption=2)

		# THEN
		self.assertTrue(adoptions.adopted(EconomicStrategyType.losingMoney))
		self.assertEqual(adoptions.turnOfAdoption(EconomicStrategyType.losingMoney), 2)
		self.assertFalse(adoptions.adopted(EconomicStrategyType.foundCity))
		self.assertEqual(adoptions.turnOfAdoption(EconomicStrategyType.foundCity), -1)

	def test_abandon(self):
		# GIVEN
		adoptions = EconomicStrategyAdoptions()
		adoptions.adopt(EconomicStrategyType.losingMoney, turnOfAdoption=2)

		# WHEN
		adoptions.abandon(EconomicStrategyType.losingMoney)

		# THEN
		self.assertFalse(adoptions.adopted(EconomicStrategyType.losingMoney))


class TestBuilds(unittest.TestCase):
	def test_buildOn(self):
		mapModel = MapMock(10, 10, TerrainType.grass)
		tile = mapModel.tileAt(HexPoint(1, 1))
		buildTime = BuildType.farm.buildTimeOn(tile)

		self.assertEqual(buildTime, 600)
