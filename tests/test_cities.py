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
from game.unitTypes import UnitType
from map.base import HexPoint
from map.types import TerrainType
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


class TestCity(unittest.TestCase):
	def test_turn(self):
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
		city.doTurn(simulation=simulation)

		# THEN
		self.assertNotEqual(city.currentBuildableItem(), None)

	def test_bestLocationForDistrict(self):
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
		campusLocation = city.bestLocationForDistrict(DistrictType.campus, simulation=simulation)
		harborLocation = city.bestLocationForDistrict(DistrictType.harbor, simulation=simulation)

		# THEN
		self.assertIn(campusLocation, [HexPoint(4, 5), HexPoint(5, 5), HexPoint(4, 4)])
		self.assertIsNone(harborLocation)
