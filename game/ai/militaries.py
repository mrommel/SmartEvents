from enum import Enum

from game.civilizations import TraitType
from game.unitTypes import UnitDomainType, UnitTaskType
from utils.base import InvalidEnumError
from game.baseTypes import FlavorType
from game.ai.grandStrategies import GrandStrategyAIType
from game.ai.militaryStrategies import MilitaryStrategyType


class MilitaryThreatType(Enum):
    NONE = 0


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
            return item.turnOfAdoption(militaryStrategyType)

        raise InvalidEnumError

    def adopt(self, militaryStrategyType: MilitaryStrategyType, turnOfAdoption: int):
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.militaryStrategyType == militaryStrategyType), None)

        if item is not None:
            item.adopted = True
            item.turnOfAdoption = turnOfAdoption

        raise InvalidEnumError

    def abandon(self, militaryStrategyType: MilitaryStrategyType):
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.militaryStrategyType == militaryStrategyType), None)

        if item is not None:
            item.adopted = False
            item.turnOfAdoption = -1

        raise InvalidEnumError


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


class MilitaryAI:
    def __init__(self, player):
        self.player = player
        self.militaryStrategyAdoption = MilitaryStrategyAdoptions()
        self.baseData = MilitaryBaseData()

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
            if unit.task() == UnitTaskType.explore or unit.task() == UnitTaskType.explore_sea:
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
        multiplier = (0.40 + float(self.highestThreat(simulation).value) + flavorOffense + flavorDefense) / 100.0

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
        highestThreatByPlayer: MilitaryThreatType = MilitaryThreatType.NONE

        for otherPlayer in simulation.players:
            if otherPlayer.leader == self.player.leader:
                continue

            if not self.player.hasMet(otherPlayer):
                continue

            threat = self.player.diplomacyAI.militaryThreat(otherPlayer)

            if highestThreatByPlayer.value < threat.value:
                highestThreatByPlayer = threat

        return highestThreatByPlayer

    def updateBarbarianData(self, simulation):
        pass

    def updateDefenseState(self, simulation):
        pass

    def updateMilitaryStrategies(self, simulation):
        pass

    def updateThreats(self, simulation):
        pass

    def updateOperations(self, simulation):
        pass
