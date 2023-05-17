from game.baseTypes import CityStateType, GameState
from game.ai.economics import EconomicAI
from game.ai.grandStrategies import GrandStrategyAI
from game.ai.militaries import MilitaryAI
from game.cities import City, AgeType, DedicationType, CityState, YieldValues
from game.cityConnections import CityConnections
from game.civilizations import LeaderType
from game.flavors import Flavors, FlavorType
from game.governments import PlayerGovernment
from game.greatPersons import GreatPersonType
from game.notifications import Notifications, NotificationType, Notification
from game.playerMechanics import PlayerTechs, PlayerCivics, BuilderTaskingAI, TacticalAI, DiplomacyAI, HomelandAI, \
    DiplomacyRequests
from game.policyCards import PolicyCardType
from game.religions import PantheonType
from game.types import EraType
from game.unitTypes import UnitMissionType, UnitTaskType
from game.wonders import WonderType
from map.base import HexPoint
from map.types import Tutorials


class Player:
    pass


class DiplomaticAI:
    def __init__(self, player):
        self.player = player

    def update(self, simulation):
        pass

    def hasMetWith(self, player):
        return False


class TradeRoute:
    pass


class PlayerTradeRoutes:
    def __init__(self, player):
        self.player = player

    def tradeRoutesStartingAt(self, city) -> [TradeRoute]:
        return []


class PlayerGreatPeople:
    def __init__(self, player):
        self.player = player

    def hasRetired(self, greatPerson: GreatPersonType) -> bool:
        return False


class PlayerReligion:
    def __init__(self, player):
        self.player = player

    def pantheon(self) -> PantheonType:
        return PantheonType.none


class Player:
    def __init__(self, leader: LeaderType, cityState: CityStateType = None, human: bool = False):
        self.leader = leader
        self.cityState = cityState
        self.human = human

        # ais
        self.grandStrategyAI = GrandStrategyAI(player=self)
        self.economicAI = EconomicAI(player=self)
        self.militaryAI = MilitaryAI(player=self)
        self.tacticalAI = TacticalAI(player=self)
        self.diplomacyAI = DiplomacyAI(player=self)
        self.homelandAI = HomelandAI(player=self)
        self.builderTaskingAI = BuilderTaskingAI(player=self)

        self.notifications = Notifications(self)
        self.diplomacyRequests = DiplomacyRequests(player=self)

        # special ais
        self.techs = PlayerTechs(self)
        self.civics = PlayerCivics(self)

        self.personalityFlavors = Flavors()
        # state values
        self.isAliveVal = True
        self.turnActive = False
        self.finishTurnButtonPressedValue = False
        self.processedAutoMovesValue = False
        self.autoMovesValue = False
        self.endTurnValue = False
        self.lastSliceMovedValue = 0
        # cities stats values
        self.citiesFoundValue = 0
        self.citiesLostValue = 0
        self.builtCityNames = []
        self.originalCapitalLocationValue = HexPoint(-1, -1)
        self.lostCapitalValue = False
        self.conquerorValue = None

        self.government = PlayerGovernment(player=self)
        self.religion = PlayerReligion(player=self)
        self.tradeRoutes = PlayerTradeRoutes(player=self)
        self.cityConnections = CityConnections(player=self)
        self.greatPeople = PlayerGreatPeople(player=self)
        
        self.currentEraVal: EraType = EraType.ancient
        self.currentAgeVal: AgeType = AgeType.normal
        self.currentDedicationsVal: [DedicationType] = []
        self.numberOfDarkAgesVal: int = 0
        self.numberOfGoldenAgesVal: int = 0

    def initialize(self):
        pass

    def doTurn(self, simulation):
        self.grandStrategyAI.doTurn(simulation)
        self.economicAI.doTurn(simulation)
        self.militaryAI.doTurn(simulation)

    def doTurnUnits(self, simulation):
        pass

    def name(self) -> str:
        return self.leader.name

    def foundCity(self, location: HexPoint, name: str, simulation):
        tile = simulation.tileAt(location)

        cityName = name if name is not None else self.newCityName(simulation)

        # moments
        # ...

        isCapital = len(simulation.citiesOf(self)) == 0
        city = City(cityName, location, isCapital, self)
        city.initialize(simulation)

        simulation.addCity(city)

        if self.isHuman():
            # Human player is prompted to choose production BEFORE the AI runs for the turn.
            # So we'll force the AI strategies on the city now, just after it is founded.
            # And if the very first turn, we haven't even run player strategies once yet, so do that too.
            if simulation.currentTurn == 0:
                self.economicAI.doTurn(simulation)
                self.militaryAI.doTurn(simulation)

                city.cityStrategyAI.doTurn(simulation)

                if self.isActive():
                    self.notifications.add(Notification(NotificationType.PRODUCTION_NEEDED, city=city))

                city.doFoundMessage()

                # If this is the first city (or we still aren't getting tech for some other reason) notify the player
                if self.techs.needToChooseTech() and self.science(simulation) > 0.0:
                    self.notifications.add(Notification(NotificationType.TECH_NEEDED))

                # If this is the first city (or ..) notify the player
                if self.civics.needToChooseCivic() and self.culture(simulation, consume=False) > 0.0:
                    self.notifications.add(Notification(NotificationType.CIVIC_NEEDED))

                if isCapital:
                    self.notifications.add(Notification(NotificationType.POLICY_NEEDED))
            else:
                city.doFoundMessage()

                # AI civ, may need to redo city specializations
                self.citySpecializationAI.setSpecializationsDirty()

        # roman roads
        # if self.leader.civilization().ability() == .allRoadsLeadToRome {
        #
        #             if !isCapital {
        #                 guard let capital = gameModel.capital(of: self) else {
        #                     fatalError("cant get capital")
        #                 }
        #
        #                 let pathFinderDataSource = gameModel.ignoreUnitsPathfinderDataSource(
        #                     for: .walk,
        #                     for: self,
        #                     unitMapType: .combat,
        #                     canEmbark: false,
        #                     canEnterOcean: self.canEnterOcean()
        #                 )
        #                 let pathFinder = AStarPathfinder(with: pathFinderDataSource)
        #
        #                 if let path = pathFinder.shortestPath(fromTileCoord: location, toTileCoord: capital.location) {
        #                     // If within TradeRoute6 Trade Route range of the Capital6 Capital, a road to it.
        #                     if path.count <= TradeRoutes.landRange {
        #
        #                         for pathLocation in path {
        #
        #                             if let pathTile = gameModel.tile(at: pathLocation) {
        #                                 pathTile.set(route: self.bestRoute())

        # send gossip
        # gameModel.sendGossip(type: .cityFounded(cityName: cityName), of: self)

        self.citiesFoundValue += 1

        if simulation.tutorial() == Tutorials.FOUND_FIRST_CITY and self.isHuman():
            if self.citiesFoundValue >= Tutorials.citiesToFound():
                pass
        #       gameModel.userInterface?.finish(tutorial: .foundFirstCity)
        #       gameModel.enable(tutorial: .none)


    def isAtWar(self) -> bool:
        return False

    def valueOfStrategyAndPersonalityFlavor(self, flavorType: FlavorType) -> int:
        activeStrategy = self.grandStrategyAI.activeStrategy

        if activeStrategy is None:
            return self.personalityFlavors.value(flavorType)

        return self.personalityFlavors.value(flavorType) + activeStrategy.flavor(flavorType)

    def valueOfPersonalityFlavor(self, flavor: FlavorType) -> int:
        return self.leader.flavor(flavor)

    def valueOfPersonalityIndividualFlavor(self, flavorType: FlavorType) -> int:
        return self.personalityFlavors.value(flavorType)

    def isHuman(self) -> bool:
        return self.human

    def isBarbarian(self) -> bool:
        return self.leader == LeaderType.barbar

    def hasMet(self, otherPlayer: Player) -> bool:
        return False

    def canFinishTurn(self) -> bool:
        if not self.isHuman():
            return False

        if not self.isAlive():
            return False

        if not self.isActive():
            return False

        if not self.hasProcessedAutoMoves():
            return False

        if self.blockingNotification() is not None:
            return False

        return True

    def turnFinished(self) -> bool:
        return self.finishTurnButtonPressedValue

    def finishTurn(self):
        self.finishTurnButtonPressedValue = True

    def resetFinishTurnButtonPressed(self):
        self.finishTurnButtonPressedValue = False

    def lastSliceMoved(self) -> int:
        return self.lastSliceMovedValue

    def setLastSliceMoved(self, value: int):
        self.lastSliceMovedValue = value

    def isTurnActive(self) -> bool:
        return self.turnActive

    def __eq__(self, other):
        return self.leader == other.leader

    def __str__(self):
        return f'Player {self.leader}'

    def isActive(self) -> bool:
        return self.turnActive

    def numberOfCitiesFounded(self) -> int:
        return self.citiesFoundValue

    def science(self, simulation) -> float:
        value: YieldValues = YieldValues(value=0.0, percentage=1.0)

        # Science from our Cities
        value += self.scienceFromCities(simulation)
        value += self.scienceFromCityStates(simulation)

        return max(value.calc(), 0)

    def scienceFromCities(self, simulation) -> YieldValues:
        scienceVal: YieldValues = YieldValues(value=0.0, percentage=0.0)

        for city in simulation.citiesOf(player=self):
            scienceVal += city.sciencePerTurn(simulation)

        return scienceVal

    def scienceFromCityStates(self, simulation) -> YieldValues:
        scienceVal = 0.0
        scienceModifier = 0.0

        # internationalSpaceAgency - 5% Science per City-State you are the Suzerain of.
        if self.government.hasCard(PolicyCardType.internationalSpaceAgency):
            numberOfCityStatesMet: int = 0
            for cityState in self.metCityStates(simulation):
                if self.isSuzerainOf(cityState, simulation):
                    numberOfCityStatesMet += 1

            scienceModifier += 0.05 * float(numberOfCityStatesMet)

        return YieldValues(value=scienceVal, percentage=scienceModifier)

    def culture(self, simulation, consume: bool) -> float:
        pass

    def isAlive(self) -> bool:
        return self.isAliveVal

    def prepareTurn(self, simulation):
        # Barbarians get all Techs that 3 / 4 of alive players get
        if self.isBarbarian():
            # self.doBarbarianTech()
            pass

        # / * for (iI = 0; iI < GC.getNumTechInfos();
        # iI + +)  {
        #     GetTeamTechs()->SetNoTradeTech(((TechTypes)iI), false);
        # }
        #
        # DoTestWarmongerReminder();
        #
        # DoTestSmallAwards(); * /
        self.checkWorldCircumnavigated(simulation)

    def startTurn(self, simulation):
        if self.isTurnActive():
            print("try to start already active turn")
            return

        if self.isHuman():
            print(f'--- start turn for HUMAN player {self.leader} ---')
        elif self.isBarbarian():
            print("--- start turn for barbarian player ---")
        elif self.leader == LeaderType.cityState:
            print(f'--- start turn for city state {self.cityState.name()} ---')
        elif self.isMajorAI():
            print(f'--- start turn for AI player {self.leader} ---')

        simulation.userInterface.updatePlayer(self)

        self.turnActive = True
        self.setEndTurnTo(False, simulation)
        self.setAutoMovesTo(False)

        # ##################################################################
        # TURN IS BEGINNING
        # ##################################################################

        # self.doUnitAttrition()
        self.verifyAlive(simulation)

        self.setAllUnitsUnprocessed(simulation)

        simulation.updateTacticalAnalysisMap(self)

        self.updateTimers(simulation)

        # This block all has things which might change based on city connections changing
        self.cityConnections.doTurn(simulation)
        self.builderTaskingAI.update(simulation)

        if simulation.currentTurn > 0:
            if self.isAlive():
                self.doTurn(simulation)
                self.doTurnUnits(simulation)

        if simulation.currentTurn == 1 and simulation.showTutorialInfos():
            if self.isHuman():
                # simulation.userInterface.showPopup(popupType: .tutorialStart(tutorial: gameModel.tutorialInfos()))
                pass

    def endTurn(self, simulation):
        if not self.isTurnActive():
            raise Exception("try to end an inactive turn")

        # print("--- unit animation running: \(gameModel?.userInterface?.animationsAreRunning(for: self.leader)) ---")
        playerType = 'HUMAN' if self.isHuman() else 'AI'
        print(f'--- end turn for {playerType} player {self.leader} ---')

        self.turnActive = False

        # /////////////////////////////////////////////
        # // TURN IS ENDING
        # /////////////////////////////////////////////

        self.doUnitReset(simulation)
        self.setCanChangeGovernmentTo(False)

        self.notifications.cleanUp(simulation)

        self.diplomacyRequests.endTurn()

    def hasProcessedAutoMoves(self) -> bool:
        return self.processedAutoMovesValue

    def setProcessedAutoMovesTo(self, value: bool):
        self.processedAutoMovesValue = value

    def doUnitReset(self, game):
        """Units heal and then get their movement back"""
        for loopUnit in game.unitsOf(self):
            # HEAL UNIT?
            if not loopUnit.isEmbarked():
                if not loopUnit.hasMoved(game):
                    if loopUnit.isHurt():
                        loopUnit.doHeal(game)

            # Finally(now that healing is done), restore movement points
            loopUnit.resetMoves(game)
            # pLoopUnit->SetIgnoreDangerWakeup(false);
            loopUnit.setMadeAttackTo(False)
            # pLoopUnit->setMadeInterception(false);

            if not self.isHuman():
                mission = loopUnit.peekMission()
                if mission is not None:
                    if mission.type == UnitMissionType.rangedAttack:
                        # CvAssertMsg(0, "An AI unit has a combat mission queued at the end of its turn.");
                        loopUnit.clearMissions() # Clear the whole thing, the AI will re-evaluate next turn.

    def setCanChangeGovernmentTo(self, param):
        pass

    def checkWorldCircumnavigated(self, game):
        pass

    def updatePlots(self, simulation):
        pass

    def setCapitalCity(self, city, simulation):
        pass

    def currentAge(self) -> AgeType:
        return self.currentAgeVal

    def hasDedication(self, dedication: DedicationType) -> bool:
        return dedication in self.currentDedicationsVal

    def hasWonder(self, wonder: WonderType, simulation) -> bool:
        return False

    def isSuzerainOf(self, cityState: CityState, simulation) -> bool:
        return False

    def isMajorAI(self) -> bool:
        # return not self.isHuman() and not self.isFreeCity() and not self.isBarbarian() and not self.isCityState()
        return not self.isHuman() and not self.isBarbarian() and not self.isCityState()

    def isCityState(self) -> bool:
        return self.leader == LeaderType.cityState

    def setEndTurnTo(self, value: bool, simulation):
        if not self.isEndTurn() and self.isHuman() and simulation.activePlayer().leader != self.leader:
            if self.hasBusyUnitOrCity() or self.hasReadyUnit(simulation):
                return
        elif not self.isHuman():
            if self.hasBusyUnitOrCity():
                return

        if self.isEndTurn() != value:
            assert(self.isTurnActive(), "isTurnActive is expected to be true")

            self.endTurnValue = value

            if self.isEndTurn():
                self.setAutoMovesTo(True)
            else:
                self.setAutoMovesTo(False)
        else:
            # This check is here for the AI.
            # Currently, the setEndTurn(true) never seems to get called for AI players, the auto moves are just 
            # set directly
            # Why is this?  It would be great if all players were processed the same.
            if not value and self.isAutoMoves():
                self.setAutoMovesTo(False)

    def isEndTurn(self) -> bool:
        return self.endTurnValue

    def hasBusyUnitOrCity(self) -> bool:
        # @fixme
        return False

    def isAutoMoves(self) -> bool:
        return self.autoMovesValue

    def setAutoMovesTo(self, value: bool):
        if self.autoMovesValue != value:
            self.autoMovesValue = value
            self.processedAutoMovesValue = False

    def hasReadyUnit(self, simulation) -> bool:
        activePlayer = simulation.activePlayer()

        for loopUnit in simulation.unitsOf(activePlayer):
            if loopUnit.readyToMove() and not loopUnit.isDelayedDeath():
                return True

        return False

    def countReadyUnits(self, simulation) -> int:
        rtnValue = 0
        activePlayer = simulation.activePlayer()

        for loopUnit in simulation.unitsOf(activePlayer):
            if loopUnit.readyToMove() and not loopUnit.isDelayedDeath():
                rtnValue += 1

        return rtnValue

    def hasUnitsThatNeedAIUpdate(self, simulation) -> bool:
        for loopUnit in simulation.unitsOf(self):
            if not loopUnit.processedInTurn() and (loopUnit.isAutomated() and loopUnit.task() != UnitTaskType.none and loopUnit.canMove()):
                return True

        return False

    def unitUpdate(self, simulation):
        # CvPlayerAI::AI_unitUpdate()
        # Now its the homeland AI's turn.
        if self.isHuman():
            self.homelandAI.doTurn(simulation)
        else:
            # Now let the tactical AI run.  Putting it after the operations update allows units who have
            # just been handed off to the tactical AI to get a move in the same turn they switch between
            self.tacticalAI.doTurn(simulation)
            self.homelandAI.doTurn(simulation)

    def verifyAlive(self, simulation):
        if self.isAlive():
            if not self.isBarbarian(): # and not self.isFreeCity():
                if self.numberOfCities(simulation) == 0 and self.numberOfUnits(simulation) == 0:
                    self.setAliveTo(False, simulation)
        else:
            # if dead but has received units / cities - revive
            if self.numberOfUnits(simulation) > 0 or self.numberOfCities(simulation) > 0:
                self.setAliveTo(True, simulation)

    def numberOfCities(self, simulation) -> int:
        return simulation.citiesOf(player=self)

    def numberOfUnits(self, simulation) -> int:
        return simulation.unitsOf(player=self)

    def setAliveTo(self, alive, simulation):
        if self.isAliveVal != alive:
            self.isAliveVal = alive

            if not alive:
                # cleanup
                # killUnits();
                # killCities();
                # GC.getGame().GetGameDeals()->DoCancelAllDealsWithPlayer(GetID());

                if self.isHuman():
                    simulation.setGameStateTo(GameState.over)

                self.endTurn(simulation)

    def setAllUnitsUnprocessed(self, simulation):
        for unit in simulation.unitsOf(player=self):
            unit.setTurnProcessedTo(False)

    def updateTimers(self, simulation):
        for unit in simulation.unitsOf(player=self):
            unit.updateMission(simulation)
            unit.doDelayedDeath(simulation)

        self.diplomacyAI.update(simulation)

    def updateNotifications(self, simulation):
        pass

    def hasActiveDiplomacyRequests(self) -> bool:
        return False

    def doUpdateTradeRouteCapacity(self, simulation):
        pass

    def envoyEffects(self, simulation):
        return []
