import unittest

from game.ai.cities import BuildableType, CityStrategyAdoptions, CityStrategyType
from game.baseTypes import HandicapType
from game.buildings import BuildingType
from game.cities import City
from game.civilizations import LeaderType
from game.game import Game
from game.players import Player
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
		self.assertEqual(city.currentBuildableItem().buildableType, BuildableType.building)
		self.assertEqual(city.currentBuildableItem().buildingType, BuildingType.monument)
