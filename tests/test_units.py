import unittest

from game.baseTypes import HandicapType
from game.cities import City
from game.civilizations import LeaderType
from game.game import Game
from game.players import Player
from game.unitMissions import UnitMission
from game.unitTypes import UnitMissionType, UnitType
from game.units import Unit
from map.base import HexPoint
from map.types import TerrainType
from tests.testBasics import MapMock, UserInterfaceMock


class TestUnitMissions(unittest.TestCase):
	def test_found_mission(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerTrajanSettler = Unit(HexPoint(5, 5), UnitType.settler, playerTrajan)
		simulation.addUnit(playerTrajanSettler)

		# WHEN
		playerTrajanSettler.pushMission(UnitMission(missionType=UnitMissionType.found), simulation)
		playerTrajanSettler.updateMission(simulation)

		# THEN
		self.assertEqual(playerTrajanSettler.peekMission(), None)

	def test_moveTo_mission(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# players
		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		playerTrajanScout = Unit(HexPoint(5, 5), UnitType.scout, playerTrajan)
		simulation.addUnit(playerTrajanScout)

		# WHEN
		playerTrajanScout.pushMission(UnitMission(missionType=UnitMissionType.moveTo, target=HexPoint(4, 1)), simulation)
		playerTrajanScout.updateMission(simulation)

		# THEN
		self.assertEqual(playerTrajanScout.peekMission().missionType, UnitMissionType.moveTo)
		self.assertEqual(playerTrajanScout.location, HexPoint(3, 2))

	def test_followPath_mission(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# players
		playerTrajan = Player(LeaderType.trajan, human=True)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# initial unit
		playerTrajanWarrior = Unit(HexPoint(15, 16), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerTrajanWarrior)

		# this is cheating
		mapModel.discover(playerTrajan, simulation)

		# WHEN
		path = playerTrajanWarrior.pathTowards(HexPoint(2, 3), options=None, simulation=simulation)
		playerTrajanWarrior.pushMission(UnitMission(missionType=UnitMissionType.followPath, path=path), simulation=simulation)

		# THEN
		self.assertIsNotNone(playerTrajanWarrior.peekMission())
		self.assertEqual(playerTrajanWarrior.peekMission().missionType, UnitMissionType.followPath)
		self.assertEqual(playerTrajanWarrior.peekMission().path, path)
		self.assertNotEqual(playerTrajanWarrior.location, HexPoint(15, 16))

	def test_fortify_mission(self):
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# players
		playerTrajan = Player(LeaderType.trajan, human=True)
		playerTrajan.initialize()
		simulation.players.append(playerTrajan)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		# initial unit
		playerTrajanWarrior = Unit(HexPoint(15, 16), UnitType.warrior, playerTrajan)
		simulation.addUnit(playerTrajanWarrior)

		# initial city
		city = City(name='Berlin', location=HexPoint(15, 16), isCapital=True, player=playerTrajan)
		city.initialize(simulation)
		simulation.addCity(city)

		# this is cheating
		mapModel.discover(playerTrajan, simulation)

		# WHEN
		playerTrajanWarrior.pushMission(UnitMission(missionType=UnitMissionType.fortify), simulation=simulation)

		# THEN
		self.assertIsNone(playerTrajanWarrior.peekMission())
		self.assertEqual(playerTrajanWarrior.isFortified(), True)
		self.assertEqual(playerTrajanWarrior.location, HexPoint(15, 16))
