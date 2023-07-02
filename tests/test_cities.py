import unittest

from game.ai.cities import BuildableType, CitySpecializationType
from game.baseTypes import HandicapType
from game.buildings import BuildingType
from game.cities import City
from game.civilizations import LeaderType
from game.districts import DistrictType
from game.game import GameModel
from game.governments import GovernmentType
from game.players import Player
from game.states.victories import VictoryType
from game.types import CivicType, TechType
from game.unitTypes import UnitType
from game.wonders import WonderType
from map.base import HexPoint
from map.types import TerrainType, FeatureType
from tests.testBasics import MapModelMock, UserInterfaceMock


class TestCityProduction(unittest.TestCase):
	def test_chooseProduction(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		# WHEN
		city.doProduction(allowNoProduction=False, simulation=simulation)

		# THEN
		self.assertNotEqual(city.currentBuildableItem(), None)
		self.assertIn(city.currentBuildableItem().buildableType, [BuildableType.building, BuildableType.unit])

		if city.currentBuildableItem().buildableType == BuildableType.building:
			self.assertEqual(city.currentBuildableItem().buildingType, BuildingType.monument)
		elif city.currentBuildableItem().buildableType == BuildableType.unit:
			self.assertIn(city.currentBuildableItem().unitType, [UnitType.warrior, UnitType.builder, UnitType.scout, UnitType.slinger])


class TestCityDistricts(unittest.TestCase):
	def test_districts(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		# WHEN
		city.districts.build(DistrictType.campus, HexPoint(5, 5))

		# THEN
		self.assertEqual(city.districts.hasAny(), True)
		self.assertEqual(city.districts.hasAnySpecialtyDistrict(), True)
		self.assertEqual(city.districts.hasDistrict(DistrictType.campus), True)
		self.assertEqual(city.districts.hasDistrict(DistrictType.theaterSquare), False)
		self.assertEqual(city.districts.numberOfSpecialtyDistricts(), 1)

	def test_district_location(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		# WHEN
		city.districts.build(DistrictType.campus, HexPoint(5, 5))

		# THEN
		self.assertEqual(city.districts.hasDistrict(DistrictType.campus), True)
		self.assertEqual(city.districts.locationOfDistrict(DistrictType.campus), HexPoint(5, 5))
		self.assertEqual(city.districts.locationOfDistrict(DistrictType.theaterSquare), None)


class TestCityBuildings(unittest.TestCase):
	def test_housing(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerTrajan.government.setGovernment(GovernmentType.monarchy, simulation)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		# WHEN
		housingBefore = city.buildings.housing()
		city.buildings.build(BuildingType.ancientWalls)
		housingAfter = city.buildings.housing()

		# THEN
		self.assertEqual(city.buildings.hasBuilding(BuildingType.ancientWalls), True)
		self.assertEqual(housingBefore, 1.0)
		self.assertEqual(housingAfter, 2)


class TestCityCitizens(unittest.TestCase):
	def test_turn_small(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=False, player=playerTrajan)
		city.initialize(simulation)

		# WHEN
		city.setLastTurnFoodEarned(5)
		city.cityCitizens.doTurn(simulation=simulation)

		# THEN
		# self.assertNotEqual(city.currentBuildableItem(), None)

	def test_turn_capital(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		# WHEN
		city.cityStrategy.specializationValue = CitySpecializationType.productionWonder
		city.setLastTurnFoodEarned(2)
		city.cityCitizens.doTurn(simulation=simulation)

		# THEN
		# self.assertNotEqual(city.currentBuildableItem(), None)

	def test_workedTileLocations(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)

		# WHEN
		workedTileLocations = city.cityCitizens.workedTileLocations()

		# THEN
		self.assertListEqual(workedTileLocations, [city.location])

	def test_turn_forceWorking(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)
		# city.setPopulation(newPopulation=2, reassignCitizen=True, simulation=simulation)

		# WHEN
		city.cityCitizens.doTurn(simulation)
		# city.cityCitizens.forceWorkingPlotAt(HexPoint(4, 4), force=True, simulation=simulation)

		# THEN
		numUnassignedCitizens = city.cityCitizens.numberOfUnassignedCitizens()
		numCitizensWorkingPlots = city.cityCitizens.numberOfCitizensWorkingPlots()
		self.assertEqual(numUnassignedCitizens, 0)
		self.assertEqual(numCitizensWorkingPlots, 1)
		# self.assertEqual(city.cityCitizens.isForcedWorkedAt(HexPoint(4, 4)), True)
		# self.assertEqual(city.cityCitizens.isForcedWorkedAt(HexPoint(4, 6)), False)

	def test_canWorkAt(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)
		simulation.addCity(city)

		otherCity = City('Potsdam', HexPoint(9, 5), isCapital=False, player=playerTrajan)
		otherCity.initialize(simulation)
		simulation.addCity(otherCity)
		otherCity.doAcquirePlot(HexPoint(7, 4), simulation)

		simulation.tileAt(HexPoint(4, 5)).setTerrain(TerrainType.sea)
		simulation.tileAt(HexPoint(4, 5)).setFeature(FeatureType.ice)

		# WHEN
		canWorkAtOtherCity = city.cityCitizens.canWorkAt(HexPoint(7, 4), simulation)
		canWorkAtIce = city.cityCitizens.canWorkAt(HexPoint(4, 5), simulation)
		canWorkAtValid = city.cityCitizens.canWorkAt(HexPoint(5, 4), simulation)

		# THEN
		self.assertFalse(canWorkAtOtherCity)
		self.assertFalse(canWorkAtIce)
		self.assertTrue(canWorkAtValid)

	def test_forceWorkingPlotAt(self):
		# GIVEN
		mapModel = MapModelMock(24, 20, TerrainType.grass)
		simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[],
			map=mapModel
		)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerTrajan)
		city.initialize(simulation)
		city.setPopulation(2, True, simulation)
		city.cityCitizens.doReallocateCitizens(simulation)
		simulation.addCity(city)

		simulation.tileAt(HexPoint(5, 3)).setTerrain(TerrainType.tundra)

		# WHEN
		city.cityCitizens.forceWorkingPlotAt(HexPoint(5, 4), force=True, simulation=simulation)
		forceWorkingPlotAtValid = city.cityCitizens.isForcedWorkedAt(HexPoint(5, 4))

		city.cityCitizens.forceWorkingPlotAt(HexPoint(5, 4), force=True, simulation=simulation)
		city.cityCitizens.forceWorkingPlotAt(HexPoint(4, 4), force=True, simulation=simulation)
		city.cityCitizens.forceWorkingPlotAt(HexPoint(5, 3), force=True, simulation=simulation)
		forceWorkingPlotAtRemoved = city.cityCitizens.isForcedWorkedAt(HexPoint(5, 3))

		# THEN
		self.assertTrue(forceWorkingPlotAtValid)
		self.assertFalse(forceWorkingPlotAtRemoved)


class TestCity(unittest.TestCase):

	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)

		# players
		playerBarbarian = Player(LeaderType.barbar, human=False)
		playerBarbarian.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=False)
		self.playerAlexander.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=True)
		self.playerTrajan.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[playerBarbarian, self.playerAlexander, self.playerTrajan],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceMock()

	def test_turn(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerAlexander)
		city.initialize(self.simulation)

		# WHEN
		city.doTurn(simulation=self.simulation)

		# THEN
		self.assertNotEqual(city.currentBuildableItem(), None)

	def test_bestLocationForDistrict(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		campusLocation = city.bestLocationForDistrict(DistrictType.campus, simulation=self.simulation)
		harborLocation = city.bestLocationForDistrict(DistrictType.harbor, simulation=self.simulation)

		# THEN
		self.assertIn(campusLocation, [HexPoint(4, 5), HexPoint(5, 5), HexPoint(4, 4)])
		self.assertIsNone(harborLocation)

	def test_healthPoints(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)

		# WHEN
		healthPointsNormal = city.maxHealthPoints()
		city.buildings.build(BuildingType.ancientWalls)
		healthPointsAncientWalls = city.maxHealthPoints()

		# THEN
		self.assertEqual(healthPointsNormal, 200)
		self.assertEqual(healthPointsAncientWalls, 300)

	def test_cityShrink(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		city.setPopulation(4, False, self.simulation)
		city.cityCitizens.doReallocateCitizens(self.simulation)

		# WHEN
		workedTilesBefore = len(city.cityCitizens.workedTileLocations())
		city.setPopulation(3, True, self.simulation)
		city.cityCitizens.doValidateForcedWorkingPlots(self.simulation)
		workedTilesAfter = len(city.cityCitizens.workedTileLocations())

		# THEN
		self.assertEqual(workedTilesBefore, 5)
		self.assertEqual(workedTilesAfter, 4)

	def test_updateEurekas(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city2 = City('Berlin', HexPoint(10, 5), isCapital=False, player=self.playerTrajan)
		city2.initialize(self.simulation)
		self.simulation.addCity(city2)

		# WHEN
		# CivicType.stateWorkforce
		stateWorkforceTriggeredBefore = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.stateWorkforce)
		city.buildDistrict(DistrictType.campus, HexPoint(4, 4), self.simulation)
		stateWorkforceTriggeredAfter = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.stateWorkforce)

		# CivicType.militaryTraining
		militaryTrainingTriggeredBefore = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.militaryTraining)
		city.buildDistrict(DistrictType.encampment, HexPoint(4, 5), self.simulation)
		militaryTrainingTriggeredAfter = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.militaryTraining)

		# CivicType.recordedHistory
		recordedHistoryTriggeredBefore = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.recordedHistory)
		city2.buildDistrict(DistrictType.campus, HexPoint(11, 5), self.simulation)
		recordedHistoryTriggeredAfter = self.playerTrajan.civics.inspirationTriggeredFor(CivicType.recordedHistory)

		# TechType.construction
		constructionTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.construction)
		city.buildBuilding(BuildingType.waterMill, self.simulation)
		constructionTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.construction)

		# TechType.engineering
		engineeringTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.engineering)
		city.buildBuilding(BuildingType.ancientWalls, self.simulation)
		engineeringTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.engineering)

		# TechType.shipBuilding
		shipBuildingTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.shipBuilding)
		city.trainUnit(UnitType.galley, self.simulation)
		city.trainUnit(UnitType.galley, self.simulation)
		shipBuildingTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.shipBuilding)

		# TechType.economics
		economicsTriggeredBefore = self.playerTrajan.techs.eurekaTriggeredFor(TechType.economics)
		city.buildBuilding(BuildingType.bank, self.simulation)
		city2.buildBuilding(BuildingType.bank, self.simulation)
		economicsTriggeredAfter = self.playerTrajan.techs.eurekaTriggeredFor(TechType.economics)

		# THEN
		self.assertFalse(stateWorkforceTriggeredBefore)
		self.assertTrue(stateWorkforceTriggeredAfter)
		self.assertFalse(militaryTrainingTriggeredBefore)
		self.assertTrue(militaryTrainingTriggeredAfter)
		self.assertFalse(recordedHistoryTriggeredBefore)
		self.assertTrue(recordedHistoryTriggeredAfter)
		self.assertFalse(constructionTriggeredBefore)
		self.assertTrue(constructionTriggeredAfter)
		self.assertFalse(engineeringTriggeredBefore)
		self.assertTrue(engineeringTriggeredAfter)
		self.assertFalse(shipBuildingTriggeredBefore)
		self.assertTrue(shipBuildingTriggeredAfter)
		self.assertFalse(economicsTriggeredBefore)
		self.assertTrue(economicsTriggeredAfter)

	def test_productionPerTurn_petra(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setTerrain(TerrainType.desert)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# city has petra: +2 Food, +2 Gold, and +1 Production
		# on all Desert tiles for this city(non - Floodplains).
		city.buildWonder(WonderType.petra, HexPoint(5, 5), self.simulation)

		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)
		productionPetra = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionPetra, 4.0)

	def test_productionPerTurn_motherRussia(self):
		# GIVEN
		playerPeter = Player(LeaderType.peter, cityState=None, human=False)
		playerPeter.initialize()

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=playerPeter)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setTerrain(TerrainType.tundra)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# motherRussia - Tundra tiles provide + 1 Faith and +1 Production, in addition to their usual yields.
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)
		productionMotherRussia = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionMotherRussia, 4.0)

	def test_productionPerTurn_stBasilsCathedral(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		self.simulation.tileAt(HexPoint(5, 5)).setTerrain(TerrainType.tundra)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# stBasilsCathedral - +1 Food, +1 Production, and +1 Culture on all Tundra tiles for this city.
		city.buildWonder(WonderType.stBasilsCathedral, HexPoint(6, 5), self.simulation)

		productionStBasilsCathedral = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionStBasilsCathedral, 4.0)

	def test_productionPerTurn_hueyTeocalli_in_another_city(self):
		# GIVEN

		# city
		city = City('Berlin', HexPoint(4, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)

		city2 = City('Potsdam', HexPoint(10, 5), isCapital=False, player=self.playerTrajan)
		city2.initialize(self.simulation)
		self.simulation.addCity(city2)

		self.simulation.tileAt(HexPoint(5, 5)).setFeature(FeatureType.lake)
		city.cityCitizens.setWorkedAt(HexPoint(5, 5), worked=True)

		# WHEN
		productionNormal = city.productionPerTurn(self.simulation)

		# player has hueyTeocalli: +1 Food and +1 Production for each Lake tile in your empire.
		city2.buildWonder(WonderType.hueyTeocalli, HexPoint(9, 5), self.simulation)

		productionHueyTeocalli = city.productionPerTurn(self.simulation)

		# THEN
		self.assertEqual(productionNormal, 3.0)
		self.assertEqual(productionHueyTeocalli, 4.0)
