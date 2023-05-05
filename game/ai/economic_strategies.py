import abc

from game.flavors import Flavor, FlavorType, Flavors
from utils.base import ExtendedEnum, InvalidEnumError
from game.ai.grand_strategies import GrandStrategyAIType
from game.ai.military_strategies import MilitaryStrategyType, ReconStateType
from game.unit_types import UnitTask, OperationType


class EconomicStrategyType(ExtendedEnum):
    NEED_RECON = 0
    EARLY_EXPANSION = 1
    FOUND_CITY = 2

    def requiredTech(self):
        return EconomicStrategies().strategy(self).requiredTech

    def obsoleteTech(self):
        return EconomicStrategies().strategy(self).obsoleteTech

    def notBeforeTurnElapsed(self):
        return EconomicStrategies().strategy(self).notBeforeTurnElapsed

    def shouldBeActive(self, player, simulation):
        return EconomicStrategies().strategy(self).shouldBeActive(player, simulation)

    def flavors(self) -> [Flavor]:
        return []

    def checkEachTurns(self) -> int:
        return EconomicStrategies().strategy(self).checkTriggerTurnCount

    def minimumAdoptionTurns(self) -> int:
        return EconomicStrategies().strategy(self).minimumNumTurnsExecuted


class EconomicStrategy(abc.ABC):
    def __init__(self, name):
        self.name = name
        self.checkTriggerTurnCount = 1
        self.minimumNumTurnsExecuted = 1
        self.weightThreshold = 1
        self.requiredTech = None
        self.obsoleteTech = None
        self.notBeforeTurnElapsed = 0
        self.flavorThresholdModifiers = Flavors()

    # Figure out what the WeightThreshold Mod should be by looking at the Flavors for this player & the Strategy
    def weightThresholdModifier(self, player):
        modifier = 0

        # Look at all Flavors for the Player & this Strategy
        for flavorType in list(FlavorType):
            personalityFlavor = player.valueOfPersonalityIndividualFlavor(flavorType)
            strategyFlavorMod = self.flavorThresholdModifiers.value(flavorType)

            modifier += (personalityFlavor * strategyFlavorMod)

        return modifier

    def shouldBeActive(self, player, simulation) -> bool:
        raise NotImplementedError

    def __str__(self):
        return self.name


class EarlyExpansionStrategy(EconomicStrategy):
    """'Early Expansion' Player Strategy: An early Strategy simply designed to get player up to 3 Cities quickly."""
    def __init__(self):
        super().__init__('Early Expansion')
        self.checkTriggerTurnCount = 5
        self.minimumNumTurnsExecuted = 10
        self.weightThreshold = 3

    def shouldBeActive(self, player, simulation) -> bool:
        flavorExpansion = player.valueOfStrategyAndPersonalityFlavor(FlavorType.EXPANSION)
        flavorGrowth = player.valueOfStrategyAndPersonalityFlavor(FlavorType.GROWTH)
        maxCultureCities = 6  # AI_GS_CULTURE_MAX_CITIES

        desiredCities = (3 * flavorExpansion) / max(flavorGrowth, 1)
        difficulty = max(0, simulation.handicap.value - 3)
        desiredCities += difficulty

        if player.grandStrategyAI.activeStrategy == GrandStrategyAIType.CULTURE:
            desiredCities = min(desiredCities, maxCultureCities)

        desiredCities = max(desiredCities, maxCultureCities)

        # scale this based on world size
        # standardMapSize: MapSize = .standard
        # desiredCities = desiredCities * gameModel.mapSize().numberOfTiles() / standardMapSize.numberOfTiles()

        # See how many unowned Tiles there are on this player's landmass
        capital = simulation.capitalOf(player)
        if capital is not None:
            # Make sure city specialization has gotten one chance to specialize the capital before we adopt this
            if simulation.currentTurn > 25:  # AI_CITY_SPECIALIZATION_EARLIEST_TURN
                numberOfCities = len(simulation.citiesOf(player))
                return numberOfCities < desiredCities

        return False


class NeedReconStrategy(EconomicStrategy):
    def __init__(self):
        super().__init__('Need recon')
        self.checkTriggerTurnCount = 1
        self.minimumNumTurnsExecuted = 1
        self.firstTurnExecuted = 5

    def shouldBeActive(self, player, simulation) -> bool:
        militaryStrategyAdoption = player.militaryAI.militaryStrategyAdoption

        # Never desperate for explorers, if we are at war
        if militaryStrategyAdoption.adopted(MilitaryStrategyType.AT_WAR):
            return False

        return player.economicAI.reconState() == ReconStateType.NEEDED


class FoundCityStrategy(EconomicStrategy):
    def __init__(self):
        super().__init__('Found city')
        self.checkTriggerTurnCount = 1
        self.minimumNumTurnsExecuted = 1
        self.weightThreshold = 10

    def shouldBeActive(self, player, simulation) -> bool:
        economicAI = player.economicAI

        if player.isHuman() or player.isBarbarian():
            return False

        firstLooseSettler = None
        looseSettlers = 0

        for unit in simulation.unitsOf(player):
            if unit.hasTask(UnitTask.SETTLE):
                if unit.army() is None:
                    looseSettlers += 1
                    if looseSettlers == 1:
                        firstLooseSettler = unit

        strategyWeight = looseSettlers * 10  # Just one settler will trigger this
        weightThresholdModifier = self.weightThresholdModifier(player)
        weightThreshold = self.weightThreshold + weightThresholdModifier

        # Don't run this strategy if have 0 cities, in that case we just want to drop down a city wherever we happen
        # to be
        if strategyWeight >= weightThreshold and len(simulation.citiesOf(player)) >= 1:
            (numAreas, bestArea, _) = player.bestSettleAreasWithFertility(economicAI.minimumSettleFertility(), simulation)

            if numAreas == 0:
                return False

            bestSettlePlot = player.bestSettlePlotFor(firstLooseSettler, simulation, True, None)

            if bestSettlePlot is None:
                return False

            area = bestSettlePlot.area

            canEmbark = player.canEmbark()
            isAtWarWithSomeone = player.atWarCount() > 0

            # CASE 1: Need a city on this area
            if bestArea == area:
                player.addOperation(OperationType.FOUND_CITY, None, None, bestArea, None, simulation)
                return True
            elif canEmbark and self.isSafeForQuickColonyIn(area, simulation, player):
                # CASE 2: Need a city on a safe distant area
                # Have an overseas we can get to safely
                player.addOperation(OperationType.COLONIZE, None, None, bestArea, None, simulation)
                return True

                # CASE 3: My embarked units can fight, I always do quick colonization overseas
                #             /*else if canEmbark && pPlayer->GetPlayerTraits()->IsEmbarkedNotCivilian() {
                #                 player.addOperation(of: .notSoQuickColonize, towards: nil, target: nil, area: iArea)
                #                 return true
                #             }*/
            elif canEmbark and not isAtWarWithSomeone:
                # CASE 3a: Need a city on a not so safe distant area
                # not at war with anyone
                player.addOperation(OperationType.NOT_SO_QUICK_COLONIZE, None, None, area, None, simulation)
                return True
            elif canEmbark:
                # CASE 4: Need a city on distant area
                player.addOperation(OperationType.COLONIZE, None, None, area, None, simulation)
                return True

        return False


class EconomicStrategies(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EconomicStrategies, cls).__new__(cls)

            # populate strategies
            cls._instance.strategies = dict()
            for economicStrategyType in list(EconomicStrategyType):
                cls._instance.strategies[economicStrategyType] = EconomicStrategies._strategy(economicStrategyType)

        return cls._instance

    @classmethod
    def _strategy(cls, economicStrategyType: EconomicStrategyType):
        if economicStrategyType == EconomicStrategyType.NEED_RECON:
            return NeedReconStrategy()
        elif economicStrategyType == EconomicStrategyType.EARLY_EXPANSION:
            return EarlyExpansionStrategy()
        elif economicStrategyType == EconomicStrategyType.FOUND_CITY:
            return FoundCityStrategy()

        raise InvalidEnumError(economicStrategyType)

    def strategy(self, economicStrategyType: EconomicStrategyType) -> EconomicStrategy:
        return self._instance.strategies[economicStrategyType]
