from enum import Enum

from game.ai.barbarians import BarbarianAI
from game.ai.religions import Religions
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
    ON = 0
    OVER = 1
    EXTENDED = 2


class Simulation:
    def __init__(self, map: Map, handicap: HandicapType = HandicapType.SETTLER):
        self.turnSliceValue = 0
        self.waitDiploPlayer = None
        self.players = []
        self.currentTurn = 0
        self.victoryTypes = [
            VictoryType.DOMINATION,
            VictoryType.CULTURAL
        ]
        self.handicap = handicap
        self._map = map
        self.userInterface = None
        self.gameStateValue = GameState.ON

        # game ai
        self.barbarianAI = BarbarianAI()
        self.religions = Religions()

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
            raise Exception("no UI")

        if self.isWaitingForBlockingInput():
            if not self.userInterface.isShown(ScreenType.diplomatic):
                # when diplomatic screen is visible - we can't update
                self.waitDiploPlayer.doTurnPostDiplomacy(self)
                self.setWaitingForBlockingInput(None)
            else:
                return

        # if the game is single player, it's ok to block all processing until
        # the user selects an extended match or quits.
        if self.gameState() == GameState.OVER:
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

            self.changeTurnSliceBy(1)

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

    def isWaitingForBlockingInput(self) -> bool:
        return self.waitDiploPlayer is not None

    def gameState(self) -> GameState:
        return self.gameStateValue

    def setGameState(self, gameState: GameState):
        self.gameStateValue = gameState

    def turnSlice(self) -> int:
        return self.turnSliceValue

    def setTurnSliceTo(self, value: int):
        self.turnSliceValue = value

    def changeTurnSliceBy(self, delta: int):
        self.turnSliceValue += delta

    def isPaused(self):
        return False

    def numGameTurnActive(self):
        numActive = 0
        for player in self.players:
            if player.isAlive() and player.isActive():
                numActive += 1

        return numActive

    def doTurn(self):
        print()
        print(f"::: TURN {self.currentTurn + 1} starts now :::")
        print()

        self.humanPlayer().resetFinishTurnButtonPressed()

        self.barbarianAI.doTurn(self)
        self.religions.doTurn(self)

        # doUpdateCacheOnTurn();
        # DoUpdateCachedWorldReligionTechProgress();

        self.updateScore()

        # m_kGameDeals.DoTurn();

        for player in self.players:
            player.prepareTurn(self)

        # map.doTurn()

        # GC.GetEngineUserInterface()->doTurn();

        self.barbarianAI.doCamps(self)
        self.barbarianAI.doUnits(self)

        # incrementGameTurn();
        self.currentTurn += 1

        # Sequential turns.
        # Activate the << FIRST >> player we find from the start, human or AI, who wants a sequential turn.
        for player in self.players:
            if player.isAlive():
                player.startTurn(self)

                # show stacked messages
                # if player.isHuman():
                #    self.showMessages()

                break

        # self.doUnitedNationsCountdown();

        self.doWorldEra()

        # Victory stuff
        self.doTestVictory()

        # Who's Winning every 25 turns (to be un-hardcoded later)
        human = self.humanPlayer()
        if human.isAlive():
            if self.currentTurn % 25 == 0:
                # This popup is the sync rand, so beware
                # self.userInterface.showScreen(screenType: .interimRanking, city: nil, other: nil, data: nil)
                pass

    def humanPlayer(self) -> Player:
        return next((player for player in self.players if player.isHuman()), None)

    def updateScore(self):
        pass

    def doWorldEra(self):
        pass

    def doTestVictory(self):
        pass

    def updateMoves(self):
        pass

    def updateTimers(self):
        pass

    def updatePlayers(self, self1):
        pass

    def checkPlayerTurnDeactivate(self):
        pass
