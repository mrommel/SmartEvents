import unittest

from game.base_types import LeaderType, HandicapType
from game.game import Game
from game.players import Player
from map.base import HexPoint
from map.map import Map


class TestSimulation(unittest.TestCase):
	def test_found_capital(self):
		"""Test the Simulation constructor"""
		# GIVEN
		map = Map(10, 10)
		simulation = Game(map)
		player = Player(LeaderType.TRAJAN, human=True)

		capitalBefore = simulation.capitalOf(player)
		totalCitiesFoundedBefore = player.numberOfCitiesFounded()

		# WHEN
		player.foundCity(HexPoint(4, 5), "Berlin", simulation)

		capitalAfter = simulation.capitalOf(player)
		totalCitiesFoundedAfter = player.numberOfCitiesFounded()

		# THEN
		self.assertIsNone(capitalBefore)
		self.assertEqual(totalCitiesFoundedBefore, 0)
		self.assertIsNotNone(capitalAfter)
		self.assertEqual(totalCitiesFoundedAfter, 1)

	def test_player_turn(self):
		"""Test the Simulation constructor"""
		# GIVEN
		map = Map(10, 10)
		simulation = Game(map, handicap=HandicapType.CHIEFTAIN)

		playerBarbar = Player(LeaderType.BARBAR, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		playerTrajan = Player(LeaderType.TRAJAN, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander = Player(LeaderType.ALEXANDER, human=True)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		# add UI
		simulation.userInterface = object()

		playerTrajan.foundCity(HexPoint(4, 5), "Berlin", simulation)

		# WHEN
		while not(playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()):
			simulation.update()
			print(f'-- loop -- active player: {simulation.activePlayer()} --', flush=True)

			if playerAlexander.isTurnActive():
				playerAlexander.finishTurn()
				playerAlexander.setAutoMovesTo(True)

		# THEN

