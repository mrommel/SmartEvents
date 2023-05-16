from utils.base import InvalidEnumError
from game.ai.economicStrategies import EconomicStrategyType
from game.ai.militaryStrategies import ReconStateType


class EconomicStrategyAdoptionItem:
    def __init__(self, economicStrategyType: EconomicStrategyType, adopted: bool, turnOfAdoption: int):
        self.economicStrategyType = economicStrategyType
        self.adopted = adopted
        self.turnOfAdoption = turnOfAdoption


class EconomicStrategyAdoptions:
    def __init__(self):
        self.adoptions = []

        for economicStrategyType in list(EconomicStrategyType):
            self.adoptions.append(EconomicStrategyAdoptionItem(economicStrategyType, False, -1))

    def adopted(self, economicStrategyType: EconomicStrategyType) -> bool:
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.economicStrategyType == economicStrategyType), None)

        if item is not None:
            return item.adopted

        raise InvalidEnumError(economicStrategyType)

    def turnOfAdoption(self, economicStrategyType: EconomicStrategyType) -> int:
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.economicStrategyType == economicStrategyType), None)

        if item is not None:
            return item.turnOfAdoption

        raise InvalidEnumError

    def adopt(self, economicStrategyType: EconomicStrategyType, turnOfAdoption: int):
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.economicStrategyType == economicStrategyType), None)

        if item is not None:
            item.adopted = True
            item.turnOfAdoption = turnOfAdoption
        else:
            raise InvalidEnumError(economicStrategyType)

    def abandon(self, economicStrategyType: EconomicStrategyType):
        item = next((adoptionItem for adoptionItem in self.adoptions if
                     adoptionItem.economicStrategyType == economicStrategyType), None)

        if item is not None:
            item.adopted = False
            item.turnOfAdoption = -1
        else:
            raise InvalidEnumError(economicStrategyType)


class EconomicAI:
    def __init__(self, player):
        self.player = player
        self.economicStrategyAdoptions = EconomicStrategyAdoptions()
        self.flavors = []
        self.reconStateValue = ReconStateType.NEEDED

    def doTurn(self, simulation):
        for economicStrategyType in list(EconomicStrategyType):
            # check tech
            requiredTech = economicStrategyType.requiredTech()
            isTechGiven = True if requiredTech is None else self.player.hasTech(requiredTech)
            obsoleteTech = economicStrategyType.obsoleteTech()
            isTechObsolete = False if obsoleteTech is None else self.player.hasTech(obsoleteTech)

            # Do we already have this EconomicStrategy adopted?
            shouldCityStrategyStart = True
            if self.economicStrategyAdoptions.adopted(economicStrategyType):
                shouldCityStrategyStart = False
            elif not isTechGiven:
                shouldCityStrategyStart = False
            elif simulation.currentTurn < economicStrategyType.notBeforeTurnElapsed():  # Not time to check this yet?
                shouldCityStrategyStart = False

            shouldCityStrategyEnd = False
            if self.economicStrategyAdoptions.adopted(economicStrategyType):
                turnOfAdoption = self.economicStrategyAdoptions.turnOfAdoption(economicStrategyType)

                if economicStrategyType.checkEachTurns() > 0:
                    # Is it a turn where we want to check to see if this Strategy is maintained?
                    if (simulation.currentTurn - turnOfAdoption) % economicStrategyType.checkEachTurns() == 0:
                        shouldCityStrategyEnd = True

                if shouldCityStrategyEnd and economicStrategyType.minimumAdoptionTurns() > 0:
                    # Has the minimum # of turns passed for this Strategy?
                    if simulation.currentTurn < (turnOfAdoption + economicStrategyType.minimumAdoptionTurns()):
                        shouldCityStrategyEnd = False

            # Check EconomicStrategy Triggers
            # Functionality and existence of specific CityStrategies is hardcoded
            # here, but data is stored in XML so it's easier to modify
            if shouldCityStrategyStart or shouldCityStrategyEnd:
                # Has the Tech which obsoletes this Strategy? If so, Strategy should be deactivated regardless of
                # other factors
                strategyShouldBeActive = False

                # Strategy isn't obsolete, so test triggers as normal
                if not isTechObsolete:
                    strategyShouldBeActive = economicStrategyType.shouldBeActive(self.player, simulation)

                # This variable keeps track of whether we should be doing something (i.e. Strategy is active now but
                # should be turned off, OR Strategy is inactive and should be enabled)
                adoptOrEndStrategy = False

                # Strategy should be on, and if it's not, turn it on
                if strategyShouldBeActive:
                    if shouldCityStrategyStart:
                        adoptOrEndStrategy = True
                    elif shouldCityStrategyEnd:
                        adoptOrEndStrategy = False
                else:  # Strategy should be off, and if it's not, turn it off
                    if shouldCityStrategyStart:
                        adoptOrEndStrategy = False
                    elif shouldCityStrategyEnd:
                        adoptOrEndStrategy = True

                if adoptOrEndStrategy:
                    if shouldCityStrategyStart:
                        self.economicStrategyAdoptions.adopt(economicStrategyType, simulation.currentTurn)
                        print(f'Player {self.player.leader} has adopted {economicStrategyType} in {simulation.currentTurn}')
                        self.updateFlavors()
                    elif shouldCityStrategyEnd:
                        self.economicStrategyAdoptions.abandon(economicStrategyType)
                        print(f'Player {self.player.leader} has abandoned {economicStrategyType} in {simulation.currentTurn}')
                        self.updateFlavors()

    def reconState(self):
        return self.reconStateValue

    def updateFlavors(self):
        self.flavors = []

        for economicStrategyType in list(EconomicStrategyType):
            if self.economicStrategyAdoptions.adopted(economicStrategyType):
                for economicStrategyTypeFlavor in economicStrategyType.flavors():
                    self.flavors += economicStrategyTypeFlavor
