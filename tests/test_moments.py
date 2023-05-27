import unittest

from game.baseTypes import HandicapType
from game.civilizations import LeaderType, CivilizationType
from game.game import Game
from game.moments import MomentType
from game.players import Player
from map.types import TerrainType
from tests.testBasics import MapMock, UserInterfaceMock


class TestMoments(unittest.TestCase):
	def test_moment_cityNearVolcano(self):  # 5
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.cityNearVolcano, cityName='Berlin')
		playerTrajan.addMoment(MomentType.cityNearVolcano, cityName='Berlin', simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.cityNearVolcano, cityName='Berlin'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.cityNearVolcano, cityName='Potsdam'))

	def test_moment_cityOfAwe(self):  # 6
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.cityOfAwe, cityName='Berlin')
		playerTrajan.addMoment(MomentType.cityOfAwe, cityName='Berlin', simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.cityOfAwe, cityName='Berlin'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.cityOfAwe, cityName='Potsdam'))

	# 	cityOnNewContinent = 'cityOnNewContinent' (cityName: String, continentName: String) # 7

	def test_moment_metNewCivilization(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.english)
		playerTrajan.addMoment(MomentType.metNewCivilization, civilization=CivilizationType.english, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.english))
		self.assertFalse(playerTrajan.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.greek))

	def test_trigger_metNewCivilization(self):
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
		self.assertEqual(player.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.greek), True)
		self.assertEqual(player.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.english), False)