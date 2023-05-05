import unittest

from game.base_types import LeaderType, HandicapType
from game.game import Game
from game.players import Player
from game.types import CivicType, TechType
from map.base import HexPoint
from map.map import Map


class TestGameAssets(unittest.TestCase):
	def test_techs_data(self):
		for tech in list(TechType):
			_ = tech.name()

	def test_civics_data(self):
		for civic in list(CivicType):
			_ = civic.name()

	def test_civics_envoys(self):
		# https://civilization.fandom.com/wiki/Envoy_(Civ6)
		# The following civics grant free Envoy Envoys upon discovery: Mysticism, Military Training, Theology,
		# Naval Tradition, Mercenaries, Colonialism, Opera and Ballet, Natural History, Scorched Earth, Conservation,
		# Capitalism, Nuclear Program, and Cultural Heritage (and, in Gathering Storm, Near Future Governance and
		# Global Warming Mitigation). The civics between Mercenaries and Conservation grant +2, while Conservation and
		# all others afterward grant +3.
		civics_with_envoys = [
			CivicType.mysticism, CivicType.militaryTradition, CivicType.theology, CivicType.navalTradition,
			CivicType.mercenaries, CivicType.colonialism, CivicType.operaAndBallet, CivicType.naturalHistory,
			CivicType.scorchedEarth, CivicType.conservation, CivicType.capitalism, CivicType.nuclearProgram,
			CivicType.culturalHeritage, CivicType.nearFutureGovernance, CivicType.globalWarmingMitigation
		]

		for civic_with_envoys in civics_with_envoys:
			self.assertGreater(civic_with_envoys.envoys(), 0,
			                   f'envoys of {civic_with_envoys} should be greater than zero')

	def test_civics_governors(self):
		# Civic Tree - There are a total of 13 civics that will grant 1 Governor Title. They are State Workforce,
		# Early Empire, Defensive Tactics, Recorded History, Medieval Faires, Guilds, Civil Engineering, Nationalism,
		# Mass Media, Mobilization, Globalization, Social Media, and Near Future Governance. Advancing through the
		# civic tree is the most basic and most common way of acquiring Governor Titles.
		civics_with_governors = [
			CivicType.stateWorkforce, CivicType.earlyEmpire, CivicType.defensiveTactics, CivicType.recordedHistory,
			CivicType.medievalFaires, CivicType.guilds, CivicType.civilEngineering, CivicType.nationalism,
			CivicType.massMedia, CivicType.mobilization, CivicType.globalization, CivicType.socialMedia,
			CivicType.nearFutureGovernance
		]

		for civic_with_governors in civics_with_governors:
			self.assertTrue(civic_with_governors.governorTitle(), f'envoys of {civic_with_governors} should be True')

	# def test_civic_achievements(self):
	# 	achievements = CivicAchievements(CivicType.gamesAndRecreation)
	#
	# 	self.assertIn(BuildingType.arena, achievements.buildingTypes)


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

