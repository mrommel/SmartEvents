from game.baseTypes import HandicapType
from game.civilizations import LeaderType
from game.game import GameModel
from game.governments import GovernmentType
from game.players import Player
from game.states.victories import VictoryType
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint
from map.map import MapModel
from tests.testBasics import UserInterfaceMock


class GameGenerator:
	def __init__(self):
		pass
	
	def freeCityStateStartingUnitTypes(self) -> [UnitType]:
		return [UnitType.settler, UnitType.warrior, UnitType.builder]

	def generate(self, map: MapModel, handicap: HandicapType) -> GameModel:
		players: [Player] = []
		units: [Unit] = []

		# ---- Barbar
		playerBarbar = Player(leader=LeaderType.barbar, human=False)
		playerBarbar.initialize()
		players.append(playerBarbar)

		for startLocation in map.startLocations:
			# print("startLocation: \(startLocation.leader) (\(startLocation.isHuman ? "human" : "AI")) => \(startLocation.point)")

			# player
			player = Player(leader=startLocation.leader, human=startLocation.isHuman)
			player.initialize()

			# free techs
			if startLocation.isHuman:
				for tech in handicap.freeHumanTechs():
					player.techs.discoverTech(tech, None)

				for civic in handicap.freeHumanCivics():
					player.civics.discoverCivic(civic, None)
			else:
				for tech in handicap.freeAITechs():
					player.techs.discoverTech(tech, None)

				for civic in handicap.freeAICivics():
					player.civics.discoverCivic(civic, None)

			# set first government
			player.government.setGovernment(GovernmentType.chiefdom, None)

			players.append(player)

			# units
			if startLocation.isHuman:
				self._allocateUnits(units, startLocation.location, handicap.freeHumanStartingUnitTypes(), player)
			else:
				self._allocateUnits(units, startLocation.location, handicap.freeAIStartingUnitTypes(), player)

		# handle city states
		for startLocation in map.cityStateStartLocations:

			cityStatePlayer = Player(leader=startLocation.leader, human=False)
			cityStatePlayer.initialize()
			players.insert(1, cityStatePlayer)

			self._allocateUnits(units, startLocation.location, self.freeCityStateStartingUnitTypes(), cityStatePlayer)

		gameModel = GameModel(
			victoryTypes=[VictoryType.cultural, VictoryType.conquest, VictoryType.domination],
			handicap=handicap,
			turnsElapsed=0,
			players=players,
			map=map
		)

		# add UI
		gameModel.userInterface = UserInterfaceMock()

		# add units
		self._addUnits(units, gameModel)

		return gameModel

	def _allocateUnits(self, units, startLocation: HexPoint, unitTypes: [UnitType], player):
		for unitType in unitTypes:
			unit = Unit(startLocation, unitType, player)
			units.append(unit)

	def _addUnits(self, units, gameModel):
		lastLeader: LeaderType = LeaderType.none
		for unit in units:
			gameModel.addUnit(unit)
			gameModel.sightAt(unit.location, unit.sight(), unit, unit.player)

			if lastLeader == unit.player.leader:
				if len(gameModel.unitsAt(unit.location)) > 1:
					jumped = unit.jumpToNearestValidPlotWithin(2, gameModel)
					if not jumped:
						print("--- could not jump unit to nearest valid plot ---")

			lastLeader = unit.player.leader

		return
