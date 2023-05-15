from enum import Enum

from game.ai.barbarians import BarbarianAI
from game.ai.religions import Religions
from game.base_types import HandicapType, VictoryType, GameState
from game.cities import City
from game.civilizations import LeaderType
from game.players import Player
from game.types import TechType
from game.unit_types import BuildType
from game.units import Unit
from map.base import HexPoint
from map.map import Map, Tile
from map.types import FeatureType


class Interface:
    def __init__(self):
        pass


class ScreenType(Enum):
    diplomatic = 0


class Game:
    def __init__(self, map: Map, handicap: HandicapType = HandicapType.settler):
        self.turnSliceValue = 0
        self.waitDiploPlayer = None
        self.players = []
        self.currentTurn = 0
        self.victoryTypes = [
            VictoryType.domination,
            VictoryType.cultural
        ]
        self.handicap = handicap
        self._map = map
        self.userInterface = None
        self.gameStateValue = GameState.on

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
        featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeForest)
        featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeRainforest)
        featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeMarsh)

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

    def valid(self, point: HexPoint) -> bool:
        return self._map.valid(point)

    def isCoastalAt(self, location) -> bool:
        return self._map.isCoastalAt(location)

    def tutorial(self):
        return None

    def showTutorialInfos(self) -> bool:
        return False

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
        playersToProcess = []
        processPlayerAutoMoves = False

        for player in self.players:

            if player.isAlive() and player.isActive() and not player.isHuman():
                playersToProcess.append(player)
                processPlayerAutoMoves = False

                # Notice the break. Even if there is more than one AI with an active turn, we do them sequentially.
                break

        # If no AI with an active turn, check humans.
        if len(playersToProcess) == 0:
            processPlayerAutoMoves = True

            for player in self.players:
                # player.checkInitialTurnAIProcessed()
                if player.isActive() and player.isHuman():
                    playersToProcess.append(player)

        if len(playersToProcess) > 0:
            player = playersToProcess[0]

            readyUnitsBeforeMoves = player.countReadyUnits(self)

            if player.isAlive():
                needsAIUpdate = player.hasUnitsThatNeedAIUpdate(self)
                if player.isActive() or needsAIUpdate:
                    if not player.isAutoMoves() or needsAIUpdate:
                        if needsAIUpdate or not player.isHuman():
                            # ------- this is where the important stuff happens! --------------
                            player.unitUpdate(self)
                            # print("updateMoves() : player.unitUpdate() called for player \(player.leader.name())")

                        readyUnitsNow = player.countReadyUnits(self)

                        # Was a move completed, if so save off which turn slice this was
                        if readyUnitsNow < readyUnitsBeforeMoves:
                            player.setLastSliceMoved(self.turnSlice())

                        if not player.isHuman() and not player.hasBusyUnitOrCity():

                            if readyUnitsNow == 0:
                                player.setAutoMovesTo(True)
                            else:
                                if player.hasReadyUnit(self):
                                    waitTime = 5

                                    if self.turnSlice() - player.lastSliceMoved() > waitTime:
                                        print("GAME HANG - Please show and send save. Stuck units will have their turn ended so game can advance.")
                                        # debug
                                        for unit in self.unitsOf(player):
                                            if not unit.readyToMove():
                                                continue

                                            print(f"GAME HANG - unit of {player.leader.name()} has no orders: {unit.name()} at {unit.location}")

                                        # debug
                                        player.endTurnsForReadyUnits(self)

                        if player.isAutoMoves() and (not player.isHuman() or processPlayerAutoMoves):
                            repeatAutomoves = False
                            repeatPassCount = 2  # Prevent getting stuck in a loop

                            while True:
                                for loopUnit in self.unitsOf(player):
                                    loopUnit.autoMission(self)

                                    # Does the unit still have movement points left over?
                                    if player.isHuman() and loopUnit.hasCompletedMoveMission(self) and loopUnit.canMove() and not loopUnit.isAutomated():

                                        if player.turnFinished():
                                            repeatAutomoves = True  # Do another pass.

                                    # This is a short - term solution to a problem where a unit
                                    # with an auto-mission (a queued, multi-turn) move order cannot reach its destination, but
                                    # does not re-enter the "need order" list because this code is processed at the end of turns.The result is that the player could easily "miss" moving
                                    # the unit this turn because it displays "next turn" rather than "skip unit turn" and the unit is not added to the "needs orders" list.
                                    # To correctly fix this problem, we would need some way to determine if any of the auto-missions are invalid before the player can end the turn and
                                    # activate the units that have a problem.
                                    # The problem with evaluating this is that, with one unit per tile, we don't know what is a valid move until other units have moved.
                                    # (For example, if one unit was to follow another, we would want the unit in the lead to move first and then have the following unit move, in order
                                    # to prevent the following unit from constantly waking up because it can't move into the next tile. This is currently not supported.)

                                    # This short-term solution will reactivate a unit after the player clicks "next turn".It will appear strange, because the player will be asked to move
                                    # a unit after they clicked "next turn", but it is to give the player a chance to move all of their units.

                                    # jrandall sez: In MP matches, let's not OOS or stall the game.

                                repeatPassCount -= 1

                                if not(repeatAutomoves and repeatPassCount > 0):
                                    break

                            # check if the(for now human) player is overstacked and move the units
                            # if (player.isHuman())

                            # slewis - I changed this to only be the AI because human players should have the tools to deal with this now
                            if not player.isHuman():
                                for loopUnit in self.unitsOf(player):
                                    loopUnit.doDelayedDeath(self)

                        # If we completed the processing of the auto - moves, flag it.
                        if player.turnFinished() or not player.isHuman():
                            player.setProcessedAutoMovesTo(True)

                    # KWG: This code should go into CheckPlayerTurnDeactivate
                    if not player.turnFinished() and player.isHuman():
                        if not player.hasBusyUnitOrCity():
                            player.setEndTurn(True, self)

                            if player.isEndTurn():
                                # If the player's turn ended, indicate it in the log.  We only do so when the end turn state has changed to prevent useless log spamming in multiplayer.
                                # NET_MESSAGE_DEBUG_OSTR_ALWAYS("UpdateMoves() : player.setEndTurn(true) called for player " << player.GetID() << " " << player.getName())
                                pass
                        else:
                            # if !player.hasBusyUnitUpdatesRemaining() {
                            # NET_MESSAGE_DEBUG_OSTR_ALWAYS("Received turn complete for player " << player.GetID() << " " << player.getName() << " but there is a busy unit. Forcing the turn to advance")
                            player.setEndTurn(True, self)

    def updateTimers(self):
        activePlayer = self.activePlayer()
        if activePlayer is None or not activePlayer.isHuman():
            return

        for player in self.players:
            if player.isAlive():
                player.updateTimers(self)

    def updatePlayers(self, simulation):
        for player in self.players:
            if player.isAlive() and player.isActive():
                player.updateNotifications(simulation)

    def checkPlayerTurnDeactivate(self):
        """ Check to see if the player's turn should be deactivated.
            This occurs when the player has set its EndTurn and its AutoMoves to true
            and all activity has been completed."""
        if self.userInterface is None:
            raise Exception("no UI")

        for player in self.players:
            if player.isAlive() and player.isActive():
                # For some reason, AI players don't set EndTurn, why not?
                if player.turnFinished() or (not player.isHuman() and not player.hasActiveDiplomacyRequests()):
                    # debug
                    if player.isHuman():
                        print(f'auto moves: {player.hasProcessedAutoMoves()}')
                    #debug
                    if player.hasProcessedAutoMoves():
                        autoMovesComplete = False
                        if not player.hasBusyUnitOrCity():
                            autoMovesComplete = True
                            # print("+++ GameModel - CheckPlayerTurnDeactivate() : auto-moves complete for \(player.leader.name())")

                        if autoMovesComplete:
                            # Activate the next player
                            # In that case, the local human is (should be) the player we just deactivated the turn for
                            # and the AI players will be activated all at once in CvGame::doTurn, once we have received
                            # all the moves from the other human players
                            if not self.userInterface.isShown(ScreenType.diplomatic):
                                player.endTurn(self)

                                # If it is a hot seat game and the player is human and is dead, don't advance the player,
                                # we want them to get the defeat screen
                                if player.isAlive() or not player.isHuman():
                                    hasReachedCurrentPlayer = False
                                    for nextPlayer in self.players:

                                        if nextPlayer.leader == player.leader:
                                            hasReachedCurrentPlayer = True
                                            continue

                                        if not hasReachedCurrentPlayer:
                                            continue

                                        if nextPlayer.isAlive():
                                            # the player is alive and also running sequential turns.they're up!
                                            nextPlayer.startTurn(self)
                                            # self.resetTurnTimer(false)
                                            break
                            else:
                                # KWG: This doesn't actually do anything other than print to the debug log
                                print(f"Because the diplomatic screen is blocking, I am bumping this up for player "
                                      f"{player.leader}")
                                # changeNumGameTurnActive(1, std::string("Because the diplo screen is blocking I am
                                # bumping this up for player ") + getName());

    def setWaitingForBlockingInput(self, player):
        self.waitDiploPlayer = player

    def activePlayer(self):
        return next((player for player in self.players if player.isAlive() and player.isActive()), None)

    def updateTacticalAnalysisMap(self, player):
        pass
