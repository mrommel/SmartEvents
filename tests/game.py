import unittest

import pytest

from game.achievements import CivicAchievements
from game.base_types import HandicapType
from game.buildings import BuildingType
from game.cities import City
from game.civilizations import LeaderType
from game.districts import DistrictType
from game.game import Game
from game.governments import GovernmentType
from game.players import Player
from game.types import CivicType, TechType
from game.unit_types import ImprovementType
from game.wonders import WonderType
from map.base import HexPoint
from map.map import Map
from map.types import TerrainType


class TestGameAssets(unittest.TestCase):
	def test_techs_data(self):
		for tech in list(TechType):
			_ = tech.name()

	def test_civics_data(self):
		for civic in list(CivicType):
			_ = civic.name()

	def test_districts_data(self):
		for district in list(DistrictType):
			_ = district.name()

	def test_wonders_data(self):
		for wonder in list(WonderType):
			_ = wonder.name()

	def test_buildings_data(self):
		for building in list(BuildingType):
			_ = building.name()

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

	def test_civic_achievements(self):
		achievements = CivicAchievements(CivicType.gamesAndRecreation)

		self.assertIn(BuildingType.arena, achievements.buildingTypes)
		self.assertIn(WonderType.colosseum, achievements.wonderTypes)
		self.assertIn(DistrictType.entertainmentComplex, achievements.districtTypes)


class TestUserInterface:
	def updateCity(self, city):
		pass

	def updatePlayer(self, player):
		pass

	def isShown(self, screenType) -> bool:
		return False


class TestCity(unittest.TestCase):

	def setUp(self) -> None:
		mapModel = Map(10, 10)

		# center
		centerTile = mapModel.tileAt(HexPoint(1, 1))
		centerTile.setTerrain(terrain=TerrainType.grass)
		centerTile.setHills(hills=False)
		centerTile.setImprovement(improvement=ImprovementType.farm)

		# another
		anotherTile = mapModel.tileAt(HexPoint(1, 2))
		anotherTile.setTerrain(terrain=TerrainType.plains)
		anotherTile.setHills(hills=True)
		anotherTile.setImprovement(improvement=ImprovementType.mine)

		simulation = Game(mapModel)
		simulation.userInterface = TestUserInterface()

		playerTrajan = Player(leader=LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerTrajan.government.setGovernment(governmentType=GovernmentType.autocracy, simulation=simulation)
		playerTrajan.techs.discover(tech=TechType.mining, simulation=simulation)

		city = City(name='Berlin', location=HexPoint(1, 1), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		self.city = city
		self.simulation = simulation

	def test_city_initial_yields(self):
		"""Test the initial city yields"""
		# GIVEN
		self.city.setPopulation(2, reassignCitizen=False, simulation=self.simulation)

		# WHEN
		foodYield = self.city.foodPerTurn(simulation=self.simulation)
		productionYield = self.city.productionPerTurn(simulation=self.simulation)
		goldYield = self.city.goldPerTurn(simulation=self.simulation)

		# THEN
		self.assertEqual(foodYield, 4.0)
		self.assertEqual(productionYield, 4.0)
		self.assertEqual(goldYield, 5.0)

	def test_city_worked_yields(self):
		"""Test the worked city yields"""
		self.city.setPopulation(3, reassignCitizen=False, simulation=self.simulation)

		self.city.cityCitizens.setWorkedAt(location=HexPoint(1, 0), worked=True)
		self.city.cityCitizens.setWorkedAt(location=HexPoint(1, 1), worked=True)

		# WHEN
		foodYield = self.city.foodPerTurn(simulation=self.simulation)
		productionYield = self.city.productionPerTurn(simulation=self.simulation)
		goldYield = self.city.goldPerTurn(simulation=self.simulation)

		# THEN
		self.assertEqual(foodYield, 5.0)
		self.assertEqual(productionYield, 4.0)
		self.assertEqual(goldYield, 5.0)

	def test_city_no_growth(self):
		# GIVEN

		# WHEN
		self.city.doTurn(self.simulation)

		# THEN
		self.assertEqual(self.city.population(), 1)

	def test_city_growth_from_food(self):
		# GIVEN
		self.city.setFoodBasket(20)

		# WHEN
		self.city.doTurn(self.simulation)

		# THEN
		self.assertEqual(self.city.population(), 2)

	def test_city_turn(self):
		# GIVEN
		self.city.setPopulation(2, reassignCitizen=False, simulation=self.simulation)

		# WHEN
		foodBefore = self.city.foodBasket()
		self.city.doTurn(self.simulation)
		foodAfter = self.city.foodBasket()

		# THEN
		self.assertEqual(foodBefore, 1.0)
		self.assertEqual(foodAfter, 1.0)


class TestSimulation(unittest.TestCase):
	def test_found_capital(self):
		"""Test the Simulation constructor"""
		# GIVEN
		map = Map(10, 10)
		simulation = Game(map)
		player = Player(LeaderType.trajan, human=True)
		player.initialize()

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
		simulation = Game(map, handicap=HandicapType.chieftain)

		playerBarbar = Player(LeaderType.barbar, human=False)
		playerBarbar.initialize()
		simulation.players.append(playerBarbar)

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()
		simulation.players.append(playerAlexander)

		# add UI
		simulation.userInterface = TestUserInterface()

		playerTrajan.foundCity(HexPoint(4, 5), "Berlin", simulation)

		# WHEN
		iteration = 0
		while not(playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()) and iteration < 25:
			simulation.update()  # the checks happen here
			print(f'-- loop -- active player: {simulation.activePlayer()} --', flush=True)

			if playerAlexander.isTurnActive():
				playerAlexander.setProcessedAutoMovesTo(True)  # units have moved
				playerAlexander.finishTurn()  # turn button clicked

			iteration += 1

		# THEN
		self.assertLess(iteration, 25, 'maximum iterations reached')

