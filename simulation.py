from enum import Enum

from game.base_types import LeaderType, HandicapType, VictoryType
from game.cities import City
from game.players import Player
from game.types import TechType
from game.unit_types import BuildType
from game.units import Unit
from map.map import Map, Tile
from map.types import FeatureType


class Interface:
    def __init__(self):
        pass


class ScreenType(Enum):
    diplomatic = 0


class GameState(Enum):
    pass


class Simulation:
    def __init__(self, map: Map, handicap: HandicapType = HandicapType.SETTLER):
        self.players = []
        self.currentTurn = 0
        self.victoryTypes = [
            VictoryType.DOMINATION,
            VictoryType.CULTURAL
        ]
        self.handicap = handicap
        self._map = map
        self.interface = None

    def initialize(self, humanLeader: LeaderType):
        # init human player and units
        humanPlayer = Player(humanLeader, human=True)
        humanStartLocation = next((startLocation for startLocation in self._map.startLocations if startLocation.leader == humanLeader), None)

        if humanStartLocation is None:
            raise Exception(f'no start location for {humanLeader} provided')

        for unitType in self.handicap.freeHumanStartingUnitTypes():
            unit = Unit(humanStartLocation.location, unitType, humanPlayer)
            self._map.addUnit(unit)

            if len(self.unitsAt(humanStartLocation)) > 1:
                unit.jumpToNearestValidPlotWithin(2, self)

        self.players.append(humanPlayer)

        # add ai players
        #for aiLeader in selectedLeaders:
        #	aiPlayer = Player(aiLeader, human=False, barbarian=False)
        #	self.players.append(aiPlayer)

    # def doTurn(self):
    # 	print(f'start turn {self.currentTurn}')
    # 	for player in self.players:
    # 		player.doTurn(self)
    #
    # 	self.currentTurn += 1

    def update(self):
        if self.userInterface is None:
            print("no UI")
            return

        if self.isWaitingForBlockingInput():
            if not self.userInterface.isShown(ScreenType.diplomatic):
                # when diplomatic screen is visible - we can't update
                self.waitDiploPlayer.doTurnPostDiplomacy(self)
                self.setWaitingForBlockingInput(None)
            else:
                return

        # if the game is single player, it's ok to block all processing until
        # the user selects an extended match or quits.
        if self.gameState() == GameState.over:
            # self.testExtendedGame()
            return

        # self.sendPlayerOptions()

        if self.turnSlice() == 0 and not self.isPaused():
            # gDLL->AutoSave(true);
            pass

        # If there are no active players, move on to the AI
        if self.numGameTurnActive() == 0:
            self.doTurn()

        # Check for paused again, the doTurn call might have called something that paused the game and we don't want an update to sneak through
        if not self.isPaused():
            # self.updateWar()
            self.updateMoves()

            # And again, the player can change after the automoves and that can pause the game
        if not self.isPaused():
            self.updateTimers()

            self.updatePlayers(self)  # slewis added!

            # self.testAlive()

            if not self.humanPlayer().isAlive():
                self.setGameState(GameState.over)

            # next player ???
            self.checkPlayerTurnDeactivate()

            self.changeTurnSlice(1)

    def capitalOf(self, player: Player) -> City:
        return self._map.capitalOf(player)

    def unitsOf(self, player: Player) -> [Unit]:
        return self._map.unitsOf(player)

    def unitsAt(self, location) -> [Unit]:
        return self._map.unitsAt(location)

    def citiesOf(self, player) -> [City]:
        return self._map.citiesOf(player)

    def addCity(self, city):
        tile = self.tileAt(city.location)

        # check feature removal
        featureRemovalSurplus = 0
        featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.REMOVE_FOREST)
        featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.REMOVE_RAINFOREST)
        featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.REMOVE_MARSH)

        city.changeFeatureProduction(featureRemovalSurplus)

        tile.setFeature(FeatureType.none)

        self._map.addCity(city, self)
        # self.userInterface?.show(city: city)

        # update area around the city
        for pt in city.location.areaWithRadius(3):
            if not self._map.valid(pt):
                continue

            neighborTile = self.tileAt(pt)
            # self.userInterface.refreshTile(neighborTile)

        # update eureka
        if not city.player.techs.eurekaTriggeredForTech(TechType.sailing):
            if self._map.isCoastalAt(city.location):
                city.player.techs.triggerEurekaForTech(TechType.sailing, self)

        self._map.addCity(city, simulation=self)

    def tileAt(self, location) -> Tile:
        return self._map.tileAt(location)

    def tutorial(self):
        return None