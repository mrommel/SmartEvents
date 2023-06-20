import unittest

from game.ai.cities import BuildableItem
from game.baseTypes import HandicapType
from game.buildings import BuildingType
from game.civilizations import LeaderType
from game.game import GameModel
from game.governments import GovernmentType
from game.players import Player
from game.states.victories import VictoryType
from game.types import TechType, CivicType
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint
from map.generation import MapOptions, MapGenerator
from map.types import MapSize, TerrainType, ResourceType, MapType
from tests.testBasics import MapModelMock, UserInterfaceMock


class TestTradeRoutes(unittest.TestCase):

	def setUp(self) -> None:
		self.sourceLocation = HexPoint(3, 5)
		self.targetLocation = HexPoint(8, 5)

		self.hasVisited = False
		self.targetVisited = 0
		self.sourceVisited = 0
		self.hasExpired = False

	def moveCallback(self, location: HexPoint):
		if location == self.targetLocation:
			self.hasVisited = True
			self.targetVisited += 1

		if location == self.sourceLocation:
			self.sourceVisited += 1

		# print(f'moveCallback({location})')

	def test_both_cities_homeland(self):
		# GIVEN
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		aiPlayer = Player(LeaderType.victoria, human=False)
		aiPlayer.initialize()

		humanPlayer = Player(LeaderType.alexander, human=True)
		humanPlayer.initialize()

		mapModel = MapModelMock(MapSize.small, TerrainType.grass)
		mapModel.modifyTerrainAt(HexPoint(1, 2), TerrainType.plains)
		mapModel.modifyIsHillsAt(HexPoint(1, 2), True)
		mapModel.modifyResourceAt(HexPoint(1, 2), ResourceType.wheat)
		mapModel.modifyTerrainAt(HexPoint(3, 2), TerrainType.plains)
		mapModel.modifyResourceAt(HexPoint(3, 2), ResourceType.iron)

		mapOptions = MapOptions(MapSize.duel, MapType.continents, LeaderType.alexander, [LeaderType.victoria])

		mapGenerator = MapGenerator(mapOptions)
		mapGenerator._identifyContinents(mapModel)
		mapGenerator._identifyOceans(mapModel)
		mapGenerator._identifyStartPositions(mapModel)

		gameModel = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.king,
			turnsElapsed=0,
			players=[barbarianPlayer, aiPlayer, humanPlayer],
			map=mapModel
		)

		# add UI
		gameModel.userInterface = UserInterfaceMock()

		# Human - setup
		humanPlayer.techs.discover(TechType.pottery, gameModel)
		humanPlayer.techs.setCurrentTech(TechType.irrigation, gameModel)
		humanPlayer.civics.discover(CivicType.codeOfLaws, gameModel)
		humanPlayer.civics.discover(CivicType.foreignTrade, gameModel)
		humanPlayer.civics.setCurrentCivic(CivicType.craftsmanship, gameModel)
		humanPlayer.government.setGovernment(GovernmentType.chiefdom, gameModel)
		# humanPlayer.government.set(policyCardSet: PolicyCardSet(cards: [.godKing, .discipline]))

		# AI units
		aiPlayer.foundCity(HexPoint(25, 5), "AI Capital", gameModel)

		# Human - city 1
		humanPlayer.foundCity(HexPoint(3, 5), "Human Capital", gameModel)

		humanCapital = gameModel.cityAt(HexPoint(3, 5))
		humanCapital._buildQueue.append(BuildableItem(BuildingType.granary))

		# Human - city 2
		humanPlayer.foundCity(HexPoint(8, 5), "Human City", gameModel)
		humanCity = gameModel.cityAt(HexPoint(8, 5))
		humanCity._buildQueue.append(BuildableItem(BuildingType.granary))

		traderUnit = Unit(HexPoint(4, 5), UnitType.trader, humanPlayer)
		traderUnit._originLocation = HexPoint(3, 5)
		gameModel.addUnit(traderUnit)
		gameModel.userInterface.showUnit(traderUnit, HexPoint(4, 5))

		mapModel.discover(humanPlayer, gameModel)

		traderUnit.unitMoved = self.moveCallback

		# WHEN
		traderUnit.doEstablishTradeRouteTo(humanCity, gameModel)

		self.sourceLocation = HexPoint(3, 5)
		self.targetLocation = HexPoint(8, 5)

		self.hasVisited = False
		self.targetVisited = 0
		self.sourceVisited = 0
		self.hasExpired = False

		while gameModel.currentTurn < 35 and not self.hasExpired:
			gameModel.update()

			while not(humanPlayer.hasProcessedAutoMoves() and humanPlayer.turnFinished()):
				gameModel.update()

				if humanPlayer.isTurnActive():
					humanPlayer.setProcessedAutoMovesTo(True)
					humanPlayer.finishTurn()

			if not traderUnit.isTrading():
				self.hasExpired = True

		# THEN
		self.assertEqual(self.hasVisited, True, "not visited trade city within first 30 turns")
		self.assertEqual(self.targetVisited, 3)
		self.assertEqual(self.sourceVisited, 3)
		self.assertEqual(self.hasExpired, True)
