import unittest

from game.baseTypes import HandicapType
from game.cities import City
from game.civilizations import LeaderType
from game.flavors import Flavors, FlavorType, Flavor
from game.game import Game
from game.playerMechanics import AccessLevel
from game.players import Player
from map.base import HexPoint
from map.types import TerrainType
from tests.testBasics import MapMock, UserInterfaceMock


class TestFlavors(unittest.TestCase):
	def test_initial_value(self):
		# GIVEN
		self.objectToTest = Flavors()

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 0)

	def test_add_value(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 5)

	def test_add_two_values(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)
		self.objectToTest += Flavor(FlavorType.culture, value=2)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 7)

	def test_add_values(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)
		self.objectToTest.addFlavor(FlavorType.culture, value=3)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 8)

	def test_reset(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest.addFlavor(FlavorType.culture, value=3)
		self.objectToTest.reset()
		self.objectToTest.addFlavor(FlavorType.culture, value=2)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 2)


class AccessLevelTests(unittest.TestCase):
	def test_initial_no_contact(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		playerTrajan = Player(LeaderType.trajan)
		playerTrajan.initialize()

		# setup the map
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		simulation.userInterface = UserInterfaceMock()

		# WHEN
		accessLevel = playerAlexander.diplomacyAI.accessLevelTowards(playerTrajan)

		# THEN
		self.assertEqual(accessLevel, AccessLevel.none)

	def test_initial_first_contact(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		playerTrajan = Player(LeaderType.trajan)
		playerTrajan.initialize()

		# setup the map
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		simulation.userInterface = UserInterfaceMock()

		# WHEN
		playerAlexander.doFirstContactWith(playerTrajan, simulation)
		accessLevel = playerAlexander.diplomacyAI.accessLevelTowards(playerTrajan)

		# THEN
		self.assertEqual(accessLevel, AccessLevel.none)

	def test_limited_after_delegation(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		playerTrajan = Player(LeaderType.trajan)
		playerTrajan.initialize()

		# setup the map
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		simulation.userInterface = UserInterfaceMock()

		playerTrajanCapital = City("Capital", HexPoint(5, 5), True, playerTrajan)
		playerTrajanCapital.initialize(simulation)
		simulation.addCity(playerTrajanCapital)

		playerAlexander.treasury.changeGoldBy(50)
		playerAlexander.doFirstContactWith(playerTrajan, simulation)

		# WHEN
		playerAlexander.diplomacyAI.doSendDelegationTo(playerTrajan, simulation)
		accessLevel = playerAlexander.diplomacyAI.accessLevelTowards(playerTrajan)

		# THEN
		self.assertEqual(accessLevel, AccessLevel.limited)