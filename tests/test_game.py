import unittest

from game.achievements import CivicAchievements, TechAchievements
from game.ai.baseTypes import MilitaryStrategyType
from game.baseTypes import HandicapType
from game.buildings import BuildingType
from game.cities import City
from game.civilizations import LeaderType, CivilizationType
from game.districts import DistrictType
from game.game import Game
from game.governments import GovernmentType
from game.moments import MomentType
from game.players import Player
from game.policyCards import PolicyCardType
from game.states.builds import BuildType
from game.types import CivicType, TechType
from game.unitTypes import UnitType
from game.units import Unit
from game.wonders import WonderType
from map.base import HexPoint
from map.improvements import ImprovementType
from map.map import Map, Tile
from map.types import TerrainType
from tests.testBasics import UserInterfaceMock, MapMock


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

	def test_improvements_data(self):
		for improvement in list(ImprovementType):
			_ = improvement.name()

	def test_builds_data(self):
		for build in list(BuildType):
			_ = build.name()

	def test_policyCard_data(self):
		for policyCard in list(PolicyCardType):
			_ = policyCard.name()

	def test_moment_data(self):
		for moment in list(MomentType):
			_ = moment.name()

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
			self.assertTrue(civic_with_governors.hasGovernorTitle(), f'envoys of {civic_with_governors} should be True')

	def test_civic_achievements(self):
		achievements = CivicAchievements(CivicType.gamesAndRecreation)

		self.assertCountEqual(achievements.buildingTypes, [BuildingType.arena])
		self.assertCountEqual(achievements.wonderTypes, [WonderType.colosseum])
		self.assertCountEqual(achievements.districtTypes, [DistrictType.entertainmentComplex])
		self.assertCountEqual(achievements.policyCards, [PolicyCardType.insulae])
		self.assertCountEqual(achievements.governments, [])

	def test_tech_achievements(self):
		achievements = TechAchievements(TechType.writing)

		self.assertCountEqual(achievements.buildingTypes, [BuildingType.library])
		self.assertCountEqual(achievements.unitTypes, [])
		self.assertCountEqual(achievements.wonderTypes, [WonderType.etemenanki])
		self.assertCountEqual(achievements.buildTypes, [])
		self.assertCountEqual(achievements.districtTypes, [DistrictType.campus])

	def test_governments_data(self):
		for government in list(GovernmentType):
			_ = government.name()


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
		simulation.userInterface = UserInterfaceMock()

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


class TestPlayerTechs(unittest.TestCase):
	def setUp(self) -> None:
		self.map = Map(10, 10)
		self.simulation = Game(map=self.map)

		self.player = Player(leader=LeaderType.alexander, cityState=None, human=False)
		self.player.initialize()

		self.playerTechs = self.player.techs

	def test_possible_techs(self):
		# GIVEN
		self.playerTechs.discover(tech=TechType.pottery, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.animalHusbandry, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.mining, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.sailing, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.astrology, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.irrigation, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.writing, simulation=self.simulation)
		self.playerTechs.discover(tech=TechType.bronzeWorking, simulation=self.simulation)

		# WHEN
		possibleTechs = self.playerTechs.possibleTechs()

		# THEN
		# self.assertEqual(playerTech.currentTech(), None)
		expected = [
			TechType.masonry,
			TechType.archery,
			TechType.wheel,
			TechType.celestialNavigation,
			TechType.horsebackRiding,
			TechType.currency,
			TechType.ironWorking,
			TechType.shipBuilding
		]
		self.assertCountEqual(possibleTechs, expected)

	def test_current_tech(self):
		# GIVEN
		self.playerTechs.discover(tech=TechType.pottery, simulation=self.simulation)

		# WHEN
		self.playerTechs.setCurrentTech(TechType.writing, self.simulation)

		# THEN
		self.assertEqual(self.playerTechs.currentTech(), TechType.writing)

	def test_choose_next_techs(self):
		# GIVEN

		# WHEN
		nextTech = self.playerTechs.chooseNextTech()

		# THEN
		expected = [
			TechType.mining,
			TechType.pottery,
			TechType.animalHusbandry
		]
		self.assertTrue(nextTech in expected, f'{nextTech} not in {expected}')

	def test_eureka(self):
		# GIVEN
		self.playerTechs.discover(tech=TechType.pottery, simulation=self.simulation)

		self.playerTechs.setCurrentTech(TechType.writing, self.simulation)
		progressBefore = self.playerTechs.currentScienceProgress()

		# WHEN
		self.playerTechs.triggerEurekaFor(tech=TechType.writing, simulation=self.simulation)
		progressAfter = self.playerTechs.currentScienceProgress()

		# THEN
		self.assertEqual(self.playerTechs.eurekaTriggeredFor(TechType.writing), True)
		self.assertEqual(progressBefore, 0.0)
		self.assertEqual(progressAfter, 25.0)


class TestPlayerCivics(unittest.TestCase):
	def setUp(self) -> None:
		self.map = Map(10, 10)
		self.simulation = Game(map=self.map)

		self.player = Player(leader=LeaderType.alexander, cityState=None, human=False)
		self.player.initialize()

		self.playerCivics = self.player.civics

	def test_possible_civics(self):
		# GIVEN
		self.playerCivics.discover(civic=CivicType.codeOfLaws, simulation=self.simulation)

		# WHEN
		possibleCivics = self.playerCivics.possibleCivics()

		# THEN
		# self.assertEqual(playerCivics.currentCivic(), None)
		expected = [
			CivicType.foreignTrade,
			CivicType.craftsmanship
		]
		self.assertCountEqual(possibleCivics, expected)

	def test_current_civic(self):
		# GIVEN
		self.playerCivics.discover(civic=CivicType.codeOfLaws, simulation=self.simulation)

		# WHEN
		self.playerCivics.setCurrentCivic(CivicType.foreignTrade, self.simulation)

		# THEN
		self.assertEqual(self.playerCivics.currentCivic(), CivicType.foreignTrade)

	def test_inspiration(self):
		# GIVEN
		self.playerCivics.discover(civic=CivicType.codeOfLaws, simulation=self.simulation)

		self.playerCivics.setCurrentCivic(CivicType.foreignTrade, self.simulation)
		progressBefore = self.playerCivics.currentCultureProgress()

		# WHEN
		self.playerCivics.triggerInspirationFor(civic=CivicType.foreignTrade, simulation=self.simulation)
		progressAfter = self.playerCivics.currentCultureProgress()

		# THEN
		self.assertEqual(self.playerCivics.inspirationTriggeredFor(CivicType.foreignTrade), True)
		self.assertEqual(progressBefore, 0.0)
		self.assertEqual(progressAfter, 20.0)

	def test_eureka_of_craftsmanship(self):
		# GIVEN
		self.playerCivics.discover(CivicType.codeOfLaws, simulation=self.simulation)

		tile0: Tile = self.map.tileAt(HexPoint(0, 0))
		tile0.setOwner(self.player)
		tile1: Tile = self.map.tileAt(HexPoint(1, 0))
		tile1.setOwner(self.player)
		tile2: Tile = self.map.tileAt(HexPoint(0, 1))
		tile2.setOwner(self.player)

		# WHEN
		beforeEureka = self.playerCivics.inspirationTriggeredFor(CivicType.craftsmanship)
		tile0.changeBuildProgressOf(BuildType.farm, change=1000, player=self.player, simulation=self.simulation)
		tile1.changeBuildProgressOf(BuildType.farm, change=1000, player=self.player, simulation=self.simulation)
		tile2.changeBuildProgressOf(BuildType.farm, change=1000, player=self.player, simulation=self.simulation)
		afterEureka = self.playerCivics.inspirationTriggeredFor(CivicType.craftsmanship)

		# THEN
		self.assertEqual(beforeEureka, False)
		self.assertEqual(afterEureka, True)


class TestPlayerStrategies(unittest.TestCase):
	def test_eradicate_barbarian(self):
		# GIVEN
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()
		simulation.players.append(player)

		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()
		simulation.players.append(barbarianPlayer)

		simulation.userInterface = UserInterfaceMock()
		simulation.currentTurn = 30  # not before 25 and check every 5 turns

		tile0 = simulation.tileAt(HexPoint(3, 3))
		# tile0.sightBy(player)
		tile0.discoverBy(player, simulation)
		tile0.setOwner(player)
		tile0.setImprovement(ImprovementType.barbarianCamp)

		tile1 = simulation.tileAt(HexPoint(3, 4))
		tile1.sightBy(player)

		barbarianWarrior = Unit(HexPoint(3, 4), UnitType.barbarianWarrior, player)
		simulation.addUnit(barbarianWarrior)

		# WHEN
		player.doTurn(simulation)

		# THEN
		self.assertEqual(player.militaryAI.adopted(MilitaryStrategyType.eradicateBarbarians), True)


class TestPlayerMoments(unittest.TestCase):
	def test_met_civilization(self):
		# GIVEN
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()

		otherPlayer = Player(LeaderType.alexander, human=False)
		otherPlayer.initialize()

		simulation.userInterface = UserInterfaceMock()

		# WHEN
		player.doFirstContactWith(otherPlayer, simulation)

		# THEN
		self.assertEqual(player.hasMomentType(MomentType.metNewCivilization, civilization=CivilizationType.greek), True)
		self.assertEqual(player.hasMomentType(MomentType.metNewCivilization, civilization=CivilizationType.english), False)


class TestSimulation(unittest.TestCase):
	def test_found_capital(self):
		# GIVEN
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel)
		
		playerTrajan = Player(LeaderType.trajan, human=True)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=False)
		playerAlexander.initialize()

		simulation.players.append(playerAlexander)
		simulation.players.append(playerTrajan)

		capitalBefore = simulation.capitalOf(playerTrajan)
		totalCitiesFoundedBefore = playerTrajan.numberOfCitiesFounded()

		# WHEN
		playerTrajan.foundCity(HexPoint(4, 5), "Berlin", simulation)

		capitalAfter = simulation.capitalOf(playerTrajan)
		totalCitiesFoundedAfter = playerTrajan.numberOfCitiesFounded()

		# THEN
		self.assertIsNone(capitalBefore)
		self.assertEqual(totalCitiesFoundedBefore, 0)
		self.assertIsNotNone(capitalAfter)
		self.assertEqual(totalCitiesFoundedAfter, 1)

	def test_player_turn(self):
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
		simulation.userInterface = UserInterfaceMock()

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

