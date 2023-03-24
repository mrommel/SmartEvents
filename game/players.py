from game.base_types import LeaderType, FlavorType, Flavors, CityStateType
from game.ai.economics import EconomicAI
from game.ai.grand_strategies import GrandStrategyAI
from game.ai.militaries import MilitaryAI
from game.cities import City
from game.notifications import Notifications, NotificationType, Notification
from game.player_mechanics import Techs, Civics
from game.unit_types import UnitMissionType
from map.base import HexPoint
from map.types import Tutorials


class Player:
    pass


class Player:
    def __init__(self, leader: LeaderType, cityState: CityStateType = None, human: bool = False):
        self.leader = leader
        self.cityState = cityState
        self.human = human
        self.barbarian = False

        # ais
        self.grandStrategyAI = GrandStrategyAI(self)
        self.economicAI = EconomicAI(self)
        self.militaryAI = MilitaryAI(self)
        self.tacticalAI = None
        self.diplomacyAI = None
        self.homelandAI = None
        self.builderTaskingAI = None

        self.notifications = Notifications(self)

        # special ais
        self.techs = Techs(self)
        self.civics = Civics(self)

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

    def initialize(self):
        pass

    def doTurn(self, simulation):
        self.grandStrategyAI.doTurn(simulation)
        self.economicAI.doTurn(simulation)
        self.militaryAI.doTurn(simulation)

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
        return self.barbarian

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
        pass

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
        if not self.isTurnActive():
            print("try to start already active turn")
            return

        if self.isHuman():
            print(f'--- start turn for HUMAN player {self.leader} ---')
        elif self.isBarbarian():
            print("--- start turn for barbarian player ---")
        elif self.leader == LeaderType.CITY_STATE:
            print(f'--- start turn for city state {self.cityState.name()} ---')
        elif self.isMajorAI():
            print(f'--- start turn for AI player {self.leader} ---')

        simulation.userInterface.updatePlayer(self)

        self.turnActive = True
        self.setEndTurnTo(False, simulation)
        self.setAutoMovesTo(False)

        # ////////////// // // // // // // // // // // // // // // /
        # TURN IS BEGINNING
        # // // // // // // // // // // // // // // // // // // // // // /

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

    def setAutoMovesTo(self, value: bool):
        if self.autoMovesValue != value:
            self.autoMovesValue = value
            self.processedAutoMovesValue = False

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
