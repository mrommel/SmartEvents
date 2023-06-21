import unittest

from game.achievements import CivicAchievements, TechAchievements
from game.ai.baseTypes import MilitaryStrategyType
from game.ai.economicStrategies import EconomicStrategyType
from game.ai.homeland import HomelandMoveType
from game.baseTypes import HandicapType, GameState
from game.buildings import BuildingType
from game.cities import City, CityStateType
from game.cityStates import CityStateCategory
from game.civilizations import LeaderType, CivilizationType, CivilizationAbility
from game.districts import DistrictType
from game.game import GameModel
from game.generation import GameGenerator
from game.governments import GovernmentType
from game.loyalties import LoyaltyState
from game.moments import MomentType
from game.notifications import NotificationType
from game.players import Player
from game.policyCards import PolicyCardType
from game.states.accessLevels import AccessLevel
from game.states.ages import AgeType
from game.states.builds import BuildType
from game.states.dedications import DedicationType
from game.states.gossips import GossipType
from game.states.victories import VictoryType
from game.types import CivicType, TechType, EraType
from game.unitTypes import UnitType
from game.units import Unit, UnitActivityType, UnitAutomationType
from game.wonders import WonderType
from map.base import HexPoint
from map.generation import MapGenerator, MapOptions
from map.improvements import ImprovementType
from map.map import MapModel, Tile
from map.types import TerrainType, MapSize, MapType
from tests.testBasics import UserInterfaceMock, MapModelMock


class TestGameAssets(unittest.TestCase):

	def test_handicap_data(self):
		for handicap in list(HandicapType):
			_ = handicap.name()

	def test_gossip_data(self):
		for gossip in list(GossipType):
			_ = gossip.name()

	def test_accessLevel_data(self):
		for accessLevel in list(AccessLevel):
			_ = accessLevel.name()

	def test_era_data(self):
		for era in list(EraType):
			_ = era.name()

	def test_age_data(self):
		for age in list(AgeType):
			_ = age.name()

	def test_techs_data(self):
		for tech in list(TechType):
			_ = tech.name()

	def test_civics_data(self):
		for civic in list(CivicType):
			_ = civic.name()

	def test_districts_data(self):
		for district in list(DistrictType):
			_ = district.name()

			mapModel = MapModelMock(10, 10, TerrainType.grass)
			simulation = GameModel(
				victoryTypes=[VictoryType.domination],
				handicap=HandicapType.chieftain,
				turnsElapsed=0,
				players=[],
				map=mapModel
			)
			_ = district.canBuildOn(HexPoint(1, 1), simulation)

	def test_wonders_data(self):
		for wonder in list(WonderType):
			_ = wonder.name()

			mapModel = MapModelMock(10, 10, TerrainType.grass)
			simulation = GameModel(
				victoryTypes=[VictoryType.domination],
				handicap=HandicapType.chieftain,
				turnsElapsed=0,
				players=[],
				map=mapModel
			)
			_ = wonder.canBuildOn(HexPoint(1, 1), simulation)

	def test_buildings_data(self):
		for building in list(BuildingType):
			_ = building.name()

	def test_improvements_data(self):
		player = Player(LeaderType.trajan)
		player.initialize()

		for improvement in list(ImprovementType):
			_ = improvement.name()
			_ = improvement.yieldsFor(player)

	def test_builds_data(self):
		for build in list(BuildType):
			_ = build.name()

	def test_policyCard_data(self):
		for policyCard in list(PolicyCardType):
			_ = policyCard.name()

	def test_moment_data(self):
		for moment in list(MomentType):
			_ = moment.name()

	def test_dedication_data(self):
		for dedication in list(DedicationType):
			_ = dedication.name()

	def test_cityState_data(self):
		for cityStateCategory in list(CityStateCategory):
			_ = cityStateCategory.name()

		for cityState in list(CityStateType):
			_ = cityState.name()

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

	def test_military_state_data(self):
		for militaryStrategy in list(MilitaryStrategyType):
			_ = militaryStrategy.name()

	def test_economic_state_data(self):
		for economicStrategy in list(EconomicStrategyType):
			_ = economicStrategy.name()

	def test_civilization_data(self):
		for civilization in list(CivilizationType):
			_ = civilization.name()

		for civilizationAbility in list(CivilizationAbility):
			_ = civilizationAbility.name()

	def test_leader_data(self):
		for leader in list(LeaderType):
			_ = leader.name()

	def test_unit_data(self):
		for unit in list(UnitType):
			_ = unit.name()

	def test_loyalties_data(self):
		for loyalty in list(LoyaltyState):
			_ = loyalty.name()
			_ = loyalty.yieldPercentage()

	def test_homelandMoves_data(self):
		for homelandMove in list(HomelandMoveType):
			_ = homelandMove.name()

	def test_notification_data(self):
		for notificationType in list(NotificationType):
			_ = notificationType.name()


class TestCity(unittest.TestCase):

	def setUp(self) -> None:
		mapModel = MapModel(10, 10)

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

		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
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
		self.assertEqual(foodYield, 7.0)
		self.assertEqual(productionYield, 4.0)
		self.assertEqual(goldYield, 6.0)

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
		self.assertEqual(foodYield, 8.0)
		self.assertEqual(productionYield, 4.0)
		self.assertEqual(goldYield, 6.0)

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
		self.assertAlmostEqual(foodAfter, 6.5)


class TestPlayerTechs(unittest.TestCase):
	def setUp(self) -> None:
		self.map = MapModel(10, 10)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.map
		)

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
		self.map = MapModel(10, 10)
		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=self.map
		)

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
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

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


class TestSimulation(unittest.TestCase):
	def test_found_capital(self):
		# GIVEN
		mapModel = MapModelMock(10, 10, TerrainType.ocean)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)
		
		playerTrajan = Player(LeaderType.trajan, human=True)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=False)
		playerAlexander.initialize()

		simulation.players.append(playerAlexander)
		simulation.players.append(playerTrajan)

		simulation.userInterface = UserInterfaceMock()

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
		mapModel = MapModelMock(20, 10, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

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

		playerAlexander.foundCity(HexPoint(14, 5), "Potsdam", simulation)

		# WHEN
		iteration = 0
		while not(playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()) and iteration < 25:
			simulation.update()  # the checks happen here
			print(f'-- loop {iteration} -- active player: {simulation.activePlayer()} --', flush=True)

			if playerAlexander.isTurnActive():
				playerAlexander.setProcessedAutoMovesTo(True)  # units have moved
				playerAlexander.finishTurn()  # turn button clicked

			iteration += 1

		# THEN
		self.assertLess(iteration, 25, 'maximum iterations reached')


class TestUsecases(unittest.TestCase):
	def test_first_city_build(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# players
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

		# initial units
		playerAlexanderWarrior = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		simulation.addUnit(playerAlexanderWarrior)

		playerAugustusSettler = Unit(HexPoint(15, 15), UnitType.settler, playerTrajan)
		simulation.addUnit(playerAugustusSettler)

		playerAugustusWarrior = Unit(HexPoint(15, 16), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerAugustusWarrior)

		playerBarbarianWarrior = Unit(HexPoint(10, 10), UnitType.barbarianWarrior, playerBarbar)
		simulation.addUnit(playerBarbarianWarrior)

		# this is cheating
		mapModel.discover(playerAlexander, simulation)
		mapModel.discover(playerTrajan, simulation)
		mapModel.discover(playerBarbar, simulation)

		numberOfCitiesBefore = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsBefore = len(simulation.unitsOf(playerTrajan))

		# WHEN
		iteration = 0
		while not(playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()) and iteration < 25:
			simulation.update()

			if playerAlexander.isTurnActive():
				playerAlexander.setProcessedAutoMovesTo(True)  # units have moved
				playerAlexander.finishTurn()  # turn button clicked

			iteration += 1

		# THEN
		self.assertEqual(numberOfCitiesBefore, 0)
		self.assertEqual(numberOfUnitsBefore, 2)
		numberOfCitiesAfter = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsAfter = len(simulation.unitsOf(playerTrajan))
		self.assertEqual(numberOfCitiesAfter, 1)
		self.assertEqual(numberOfUnitsAfter, 1)

		self.assertEqual(playerAugustusWarrior.activityType(), UnitActivityType.none)  # warrior has skipped
		# XCTAssertEqual(playerAugustusWarrior.peekMission()!.buildType, BuildType.repair)

	def test_first100turns(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# players
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

		# trajan units
		playerTrajanWarrior = Unit(HexPoint(15, 16), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerTrajanWarrior)

		playerTrajanSettler = Unit(HexPoint(15, 15), UnitType.settler, playerTrajan)
		simulation.addUnit(playerTrajanSettler)

		# alexander units
		playerAlexanderScout = Unit(HexPoint(5, 6), UnitType.scout, playerAlexander)
		playerAlexanderScout.automate(UnitAutomationType.explore, simulation)
		simulation.addUnit(playerAlexanderScout)

		# barbarian units
		playerBarbarianWarrior = Unit(HexPoint(10, 10), UnitType.barbarianWarrior, playerBarbar)
		simulation.addUnit(playerBarbarianWarrior)

		# this is cheating
		# mapModel.discover(playerAlexander, simulation)
		mapModel.discover(playerTrajan, simulation)
		mapModel.discover(playerBarbar, simulation)

		numberOfCitiesBefore = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsBefore = len(simulation.unitsOf(playerTrajan))

		# WHEN
		counter = 0
		while simulation.currentTurn < 50:
			simulation.update()

			while not (playerAlexander.hasProcessedAutoMoves() and playerAlexander.turnFinished()):
				simulation.update()

				if playerAlexander.isTurnActive():
					# playerAlexander.setProcessedAutoMovesTo(True)
					playerAlexanderScout.finishMoves()
					playerAlexander.finishTurn()

				counter += 1

		# THEN
		self.assertEqual(numberOfCitiesBefore, 0)
		self.assertEqual(numberOfUnitsBefore, 2)
		numberOfCitiesAfter = len(simulation.citiesOf(playerTrajan))
		numberOfUnitsAfter = len(simulation.unitsOf(playerTrajan))
		self.assertGreater(numberOfCitiesAfter, 0)
		self.assertGreater(numberOfUnitsAfter, 0)

		self.assertEqual(simulation.gameState(), GameState.on)
		self.assertEqual(simulation.currentTurn, 50)


class TestGameGeneration(unittest.TestCase):
	def test_generation_emperor(self):
		# GIVEN
		mapModel = MapModelMock(MapSize.duel, TerrainType.grass)
		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.trajan)
		mapGenerator = MapGenerator(options=options)
		mapGenerator.update(mapModel)

		gameGenerator = GameGenerator()

		# WHEN
		game = gameGenerator.generate(mapModel, HandicapType.emperor)

		# THEN
		self.assertEqual(game.currentTurn, 0)
		self.assertEqual(len(game.players), 6)
