import unittest

from game.ai.cities import BuildableType, CityStrategyAdoptions, CityStrategyType
from game.baseTypes import HandicapType
from game.buildings import BuildingType
from game.cities import City
from game.civilizations import LeaderType
from game.districts import DistrictType
from game.game import Game
from game.governments import GovernmentType
from game.players import Player
from game.unitTypes import UnitType
from map.base import HexPoint
from map.types import TerrainType
from tests.testBasics import MapMock, UserInterfaceMock


class TestCityProduction(unittest.TestCase):
	def test_chooseProduction(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

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
			self.assertIn(city.currentBuildableItem().unitType, [UnitType.warrior, UnitType.builder, UnitType.slinger])


class TestCityDistricts(unittest.TestCase):
	def test_districts(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

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
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

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


class TestCity(unittest.TestCase):
	def test_turn(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

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
