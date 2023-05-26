import unittest

from game.ai.homeland import HomelandUnit
from game.civilizations import LeaderType
from game.players import Player
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint


class TestGameAI(unittest.TestCase):
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
