import unittest

from game.baseTypes import HandicapType
from game.civilizations import LeaderType
from game.combat import Combat
from game.game import GameModel
from game.players import Player
from game.states.victories import VictoryType
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint
from map.types import TerrainType, MapSize
from tests.testBasics import MapModelMock


class TestCombat(unittest.TestCase):
	def test_combat_warrior_against_warrior(self):
		# GIVEN

		# players
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		# map
		mapModel = MapModelMock(MapSize.duel, TerrainType.grass)

		# game
		gameModel = GameModel(
			victoryTypes=[VictoryType.domination, VictoryType.cultural, VictoryType.diplomatic],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[barbarianPlayer, playerTrajan, playerAlexander],
			map=mapModel
		)

		attacker = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		gameModel.addUnit(attacker)

		defender = Unit(HexPoint(6, 6), UnitType.warrior, playerTrajan)
		gameModel.addUnit(attacker)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, defender, gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 26)
		self.assertEqual(result.defenderDamage, 33)
