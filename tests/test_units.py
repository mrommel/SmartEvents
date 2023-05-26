import unittest

from game.baseTypes import HandicapType
from game.civilizations import LeaderType
from game.game import Game
from game.players import Player
from game.unitMissions import UnitMission
from game.unitTypes import UnitMissionType, UnitType
from game.units import Unit
from map.base import HexPoint
from map.path_finding.path import HexPath
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
