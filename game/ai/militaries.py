from enum import Enum

from game.ai.baseTypes import MilitaryStrategyType
from game.civilizations import TraitType
from game.flavors import Flavors, FlavorType
from game.unitTypes import UnitDomainType, UnitTaskType, ImprovementType, UnitMapType
from utils.base import InvalidEnumError
from game.ai.grandStrategies import GrandStrategyAIType


class MilitaryThreatType(Enum):
    none = 'none'

    minor = 'minor'
    major = 'major'
    severe = 'severe'
    critical = 'critical'

    def value(self) -> int:
        if self == MilitaryThreatType.none:
            return 0
        elif self == MilitaryThreatType.minor:
            return 1
        elif self == MilitaryThreatType.major:
            return 2
        elif self == MilitaryThreatType.severe:
            return 3
        elif self == MilitaryThreatType.critical:
            return 4

    def weight(self) -> int:
        if self == MilitaryThreatType.none:
            return 0
        elif self == MilitaryThreatType.minor:
            return 1
        elif self == MilitaryThreatType.major:
            return 3
        elif self == MilitaryThreatType.severe:
            return 6
        elif self == MilitaryThreatType.critical:
            return 10


class MilitaryStrategyAdoptionItem:
    def __init__(self, militaryStrategyType: MilitaryStrategyType, adopted: bool, turnOfAdoption: int):
        self.militaryStrategyType = militaryStrategyType
        self.adopted = adopted
        self.turnOfAdoption = turnOfAdoption


class MilitaryStrategyAdoptions:
    def __init__(self):
        self.adoptions = []

        for militaryStrategyType in list(MilitaryStrategyType):
            self.adoptions.append(MilitaryStrategyAdoptionItem(militaryStrategyType, False, -1))

    def adopted(self, militaryStrategyType: MilitaryStrategyType) -> bool:
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.militaryStrategyType == militaryStrategyType), None)

        if item is not None:
            return item.adopted

        raise InvalidEnumError(militaryStrategyType)

    def turnOfAdoption(self, militaryStrategyType: MilitaryStrategyType) -> int:
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.militaryStrategyType == militaryStrategyType), None)

        if item is not None:
            return item.turnOfAdoption

        raise Exception()

    def adopt(self, militaryStrategyType: MilitaryStrategyType, turnOfAdoption: int):
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.militaryStrategyType == militaryStrategyType), None)

        if item is not None:
            item.adopted = True
            item.turnOfAdoption = turnOfAdoption
            return

        raise InvalidEnumError(militaryStrategyType)

    def abandon(self, militaryStrategyType: MilitaryStrategyType):
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.militaryStrategyType == militaryStrategyType), None)

        if item is not None:
            item.adopted = False
            item.turnOfAdoption = -1
            return

        raise InvalidEnumError(militaryStrategyType)


class MilitaryBaseData:
    def __init__(self):
        self.numLandUnits = 0
        self.numRangedLandUnits = 0
        self.numMobileLandUnits = 0
        # var numAirUnits = 0
        # var numAntiAirUnits = 0
        self.numMeleeLandUnits = 0
        self.numNavalUnits = 0
        self.numLandUnitsInArmies = 0
        self.numNavalUnitsInArmies = 0
        self.recommendedMilitarySize = 0
        self.mandatoryReserveSize = 0

    def reset(self):
        self.numLandUnits = 0
        self.numRangedLandUnits = 0
        self.numMobileLandUnits = 0
        # self.numAirUnits = 0
        # self.numAntiAirUnits = 0
        self.numMeleeLandUnits = 0
        self.numNavalUnits = 0
        self.numLandUnitsInArmies = 0
        self.numNavalUnitsInArmies = 0
        self.recommendedMilitarySize = 0
        self.mandatoryReserveSize = 0


class BarbarianData:
    def __str__(self):
        self.barbarianCampCount = 0
        self.visibleBarbarianCount = 0

    def reset(self):
        self.barbarianCampCount = 0
        self.visibleBarbarianCount = 0


class MilitaryAI:
    def __init__(self, player):
        self.player = player
        self.militaryStrategyAdoption = MilitaryStrategyAdoptions()
        self.baseData = MilitaryBaseData()
        self._barbarianDataValue = BarbarianData()
        self._flavors = Flavors()

    def doTurn(self, simulation):
        self.updateBaseData(simulation)
        self.updateBarbarianData(simulation)
        self.updateDefenseState(simulation)
        self.updateMilitaryStrategies(simulation)
        self.updateThreats(simulation)

        if not self.player.isHuman():
            self.updateOperations(simulation)
            # self.makeEmergencyPurchases()
            # self.requestImprovements()
            # self.disbandObsoleteUnits()

    def updateBaseData(self, simulation):
        self.baseData.reset()

        for unit in simulation.unitsOf(self.player):
            # Don't count exploration units
            if unit.task() == UnitTaskType.explore or unit.task() == UnitTaskType.exploreSea:
                continue

            # Don't count civilians
            if not unit.hasTask(UnitTaskType.attack):
                continue

            if unit.domain() == UnitDomainType.land:
                self.baseData.numLandUnits += 1

                if unit.hasTask(UnitTaskType.ranged):
                    self.baseData.numRangedLandUnits += 1

                if unit.moves() > 2:
                    self.baseData.numMobileLandUnits += 1

            elif unit.domain() == UnitDomainType.sea:
                self.baseData.numNavalUnits += 1

        flavorOffense = float(self.player.valueOfStrategyAndPersonalityFlavor(FlavorType.offense))
        flavorDefense = float(self.player.valueOfStrategyAndPersonalityFlavor(FlavorType.defense))

        # Scale up or down based on true threat level and a bit by flavors(multiplier should range from about 0.5 to
        # about 1.5)
        multiplier = (0.40 + float(self.highestThreat(simulation).value()) + flavorOffense + flavorDefense) / 100.0

        # first get the number of defenders that we think we need

        # Start with 3, to protect the capital
        numUnitsWanted = 3.0

        # 1 Unit per City & 1 per Settler
        numUnitsWanted += float(len(simulation.citiesOf(self.player))) * 1.0
        allUnits = simulation.unitsOf(self.player)
        settlers = list(filter(lambda unit: unit.task() == UnitTaskType.settle, allUnits))
        numUnitsWanted += float(len(settlers)) * 1.0

        self.baseData.mandatoryReserveSize = int(float(numUnitsWanted) * multiplier)

        # add in a few for the difficulty level (all above Chieftain are boosted)
        # int iDifficulty = max(0, GC.getGame().getHandicapInfo().GetID() - 1);
        # m_iMandatoryReserveSize += (iDifficulty * 3 / 2);

        self.baseData.mandatoryReserveSize = max(1, self.baseData.mandatoryReserveSize)

        # now we add in the strike forces we think we will need
        numUnitsWanted = 7 # size of a basic attack

        # if we are going for conquest we want at least one more task force
        if self.player.grandStrategyAI.activeStrategy == GrandStrategyAIType.conquest:
            numUnitsWanted *= 2

        # add in a few more if the player is bold
        numUnitsWanted += float(self.player.leader.traitValue(TraitType.boldness))

        # add in more if we are playing on a high difficulty
        # iNumUnitsWanted += iDifficulty * 3

        numUnitsWanted *= multiplier

        numUnitsWanted = max(1, numUnitsWanted)

        self.baseData.recommendedMilitarySize = self.baseData.mandatoryReserveSize + int(numUnitsWanted)

    def highestThreat(self, simulation):
        # See if the threats we are facing have changed
        highestThreatByPlayer: MilitaryThreatType = MilitaryThreatType.none

        for otherPlayer in simulation.players:
            if otherPlayer.leader == self.player.leader:
                continue

            if not self.player.hasMetWith(otherPlayer):
                continue

            threat = self.player.diplomacyAI.militaryThreatOf(otherPlayer)

            if highestThreatByPlayer.value < threat.value:
                highestThreatByPlayer = threat

        return highestThreatByPlayer

    def barbarianData(self) -> BarbarianData:
        return self._barbarianDataValue

    def updateBarbarianData(self, simulation):
        self._barbarianDataValue.reset()

        for point in simulation.points():
            tile = simulation.tileAt(point)

            if tile.isDiscoveredBy(self.player):

                if tile.hasImprovement(ImprovementType.barbarianCamp):
                    self._barbarianDataValue.barbarianCampCount += 1

                    # Count it as 5 camps if sitting inside our territory, that is annoying!
                    if self.player.isEqualTo(tile.owner()):
                        self._barbarianDataValue.barbarianCampCount += 4

            if tile.isVisibleTo(self.player):
                unit = simulation.unitAt(point, UnitMapType.combat)
                if unit is not None:
                    if unit.isBarbarian() and unit.unitType == UnitMapType.combat:
                        self._barbarianDataValue.visibleBarbarianCount += 1


    def updateDefenseState(self, simulation):
        pass

    def adopted(self, militaryStrategy: MilitaryStrategyType) -> bool:
        return self.militaryStrategyAdoption.adopted(militaryStrategy)

    def updateMilitaryStrategies(self, simulation):
        for militaryStrategyType in list(MilitaryStrategyType):
            # Minor Civs can't run some Strategies
            # FIXME

            # check tech
            requiredTech = militaryStrategyType.requiredTech()
            isTechGiven = True if requiredTech is None else self.player.hasTech(requiredTech)
            obsoleteTech = militaryStrategyType.obsoleteTech()
            isTechObsolete = False if obsoleteTech is None else self.player.hasTech(obsoleteTech)

            # Do we already have this EconomicStrategy adopted?
            shouldCityStrategyStart = True
            if self.militaryStrategyAdoption.adopted(militaryStrategyType):
                shouldCityStrategyStart = False
            elif not isTechGiven:
                shouldCityStrategyStart = False
            elif simulation.currentTurn < militaryStrategyType.notBeforeTurnElapsed():  # Not time to check this yet?
                shouldCityStrategyStart = False

            shouldCityStrategyEnd = False
            if self.militaryStrategyAdoption.adopted(militaryStrategyType):
                if militaryStrategyType.checkEachTurns() > 0:
                    # Is it a turn where we want to check to see if this Strategy is maintained?
                    if simulation.currentTurn - self.militaryStrategyAdoption.turnOfAdoptionOf(militaryStrategyType) % militaryStrategyType.checkEachTurns() == 0:
                        shouldCityStrategyEnd = True

                if shouldCityStrategyEnd and militaryStrategyType.minimumAdoptionTurns() > 0:
                    # Has the minimum # of turns passed for this Strategy?
                    if simulation.currentTurn < self.militaryStrategyAdoption.turnOfAdoptionOf(militaryStrategyType) + militaryStrategyType.minimumAdoptionTurns():
                        shouldCityStrategyEnd = False

            # Check EconomicStrategy Triggers
            # Functionality and existence of specific CityStrategies is hardcoded here, but data is stored in XML
            # so it's easier to modify
            if shouldCityStrategyStart or shouldCityStrategyEnd:
                # Has the Tech which obsoletes this Strategy? If so, Strategy should be deactivated regardless of other factors
                strategyShouldBeActive = False

                # Strategy isn't obsolete, so test triggers as normal
                if not isTechObsolete:
                    strategyShouldBeActive = militaryStrategyType.shouldBeActiveFor(self.player, simulation)

                # This variable keeps track of whether or not we should be doing something(i.e.Strategy is active now
                # but should be turned off, OR Strategy is inactive and should be enabled)
                bAdoptOrEndStrategy = False

                # Strategy should be on, and if it's not, turn it on
                if strategyShouldBeActive:
                    if shouldCityStrategyStart:
                        bAdoptOrEndStrategy = True
                    elif shouldCityStrategyEnd:
                        bAdoptOrEndStrategy = False
                else:
                    # Strategy should be off, and if it's not, turn it off
                    if shouldCityStrategyStart:
                        bAdoptOrEndStrategy = False
                    elif shouldCityStrategyEnd:
                        bAdoptOrEndStrategy = True

                if bAdoptOrEndStrategy:
                    if shouldCityStrategyStart:
                        self.militaryStrategyAdoption.adopt(militaryStrategyType, turnOfAdoption=simulation.currentTurn)
                        print(f'Player {self.player.leader} has adopted {militaryStrategyType} in turn {simulation.currentTurn}')
                    elif shouldCityStrategyEnd:
                        self.militaryStrategyAdoption.abandon(militaryStrategyType)
                        print(f'Player {self.player.leader} has abandoned {militaryStrategyType} in turn {simulation.currentTurn}')

        self.updateFlavors()

        # print("military strategy flavors")
        # print(self.flavors)

    def updateThreats(self, simulation):
        pass

    def updateOperations(self, simulation):
        pass

    def updateFlavors(self):
        self._flavors.reset()

        for militaryStrategyType in list(MilitaryStrategyType):
            if self.militaryStrategyAdoption.adopted(militaryStrategyType):
                for militaryStrategyTypeFlavor in militaryStrategyType.flavorModifiers():
                    self._flavors += militaryStrategyTypeFlavor
