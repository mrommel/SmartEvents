import unittest

from game.baseTypes import HandicapType
from game.civilizations import LeaderType
from game.game import GameModel
from game.players import Player
from game.states.victories import VictoryType
from map.map import MapModel


class TestDiplomacyAI(unittest.TestCase):
	def test_constructor(self):
		player = Player(LeaderType.trajan)
		self.assertEqual(player.diplomacyAI.player, player)

	def test_atWar(self):
		# GIVEN
		map = MapModel(10, 10)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=map
		)

		playerAlexander = Player(leader=LeaderType.alexander, cityState=None, human=False)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=True)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander.diplomacyAI.doFirstContactWith(playerTrajan, simulation)
		playerTrajan.diplomacyAI.doFirstContactWith(playerAlexander, simulation)

		# WHEN
		isAtWarBefore = playerAlexander.isAtWar()
		playerAlexander.doDeclareWarTo(playerTrajan, simulation)
		isAtWarAfter = playerAlexander.isAtWar()

		# THEN
		self.assertEqual(isAtWarBefore, False)
		self.assertEqual(isAtWarAfter, True)
