import random

from utils.base import InvalidEnumError, ExtendedEnum
from game.base_types import FlavorType, Flavor, TraitType, VictoryType


class GrandStrategyAIType(ExtendedEnum):
	CONQUEST = 1
	CULTURE = 2
	COUNCIL = 3

	def flavor(self, flavorType: FlavorType) -> int:
		return self._flavorBase() + self._flavorModifier(flavorType)

	def _flavorBase(self) -> int:
		if self == GrandStrategyAIType.CONQUEST:
			return 11
		elif self == GrandStrategyAIType.CULTURE:
			return 11
		elif self == GrandStrategyAIType.COUNCIL:
			return 10

		raise InvalidEnumError(self)

	def _flavorModifier(self, flavorType: FlavorType) -> int:
		item = next((flavorModifier for flavorModifier in self._flavorModifiers() if
		             flavorModifier.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def _flavorModifiers(self) -> [Flavor]:
		if self == GrandStrategyAIType.CONQUEST:
			return [
				Flavor(FlavorType.MILITARY_TRAINING, 2),
				Flavor(FlavorType.GROWTH, -1),
				Flavor(FlavorType.AMENITIES, 1)
			]
		elif self == GrandStrategyAIType.CULTURE:
			return [
				Flavor(FlavorType.DEFENSE, 1),
				Flavor(FlavorType.CITY_DEFENSE, 1),
				Flavor(FlavorType.OFFENSE, -1)
			]
		elif self == GrandStrategyAIType.COUNCIL:
			return [
				Flavor(FlavorType.DEFENSE, 1),
				Flavor(FlavorType.OFFENSE, -1),
				Flavor(FlavorType.RECON, 1)
			]

		raise InvalidEnumError(self)

class GrandStrategyAIEntry:
    def __init__(self, grandStrategyAIType: GrandStrategyAIType):
        self.grandStrategyAIType = grandStrategyAIType
        self.value = 0


class GrandStrategyAIDict:
    def __init__(self):
        self.conquestStrategy = GrandStrategyAIEntry(GrandStrategyAIType.CONQUEST)
        self.cultureStrategy = GrandStrategyAIEntry(GrandStrategyAIType.CULTURE)
        self.councilStrategy = GrandStrategyAIEntry(GrandStrategyAIType.COUNCIL)

    def add(self, value, grandStrategyAIType):
        if grandStrategyAIType == GrandStrategyAIType.CONQUEST:
            self.conquestStrategy.value += value
        elif grandStrategyAIType == GrandStrategyAIType.CULTURE:
            self.cultureStrategy.value += value
        elif grandStrategyAIType == GrandStrategyAIType.COUNCIL:
            self.councilStrategy.value += value

    def value(self, grandStrategyAIType):
        if grandStrategyAIType == GrandStrategyAIType.CONQUEST:
            return self.conquestStrategy.value
        elif grandStrategyAIType == GrandStrategyAIType.CULTURE:
            return self.cultureStrategy.value
        elif grandStrategyAIType == GrandStrategyAIType.COUNCIL:
            return self.councilStrategy.value


class GrandStrategyAI:
    def __init__(self, player):
        self.player = player
        self.activeStrategy = None
        self.turnActiveStrategySet = 0

    def doTurn(self, simulation):
        # hold the score for each strategy
        grandStrategyAIDict = GrandStrategyAIDict()

        for grandStrategyAIType in list(GrandStrategyAIType):
            # Base Priority looks at Personality Flavors (0 - 10) and multiplies * the Flavors attached to a Grand
            # Strategy (0-10), so expect a number between 0 and 100 back from this
            grandStrategyAIDict.add(self.priority(grandStrategyAIType), grandStrategyAIType)

            # real value, based on current game state
            if grandStrategyAIType == GrandStrategyAIType.CONQUEST:
                grandStrategyAIDict.add(self.conquestGameValue(simulation), grandStrategyAIType)
            elif grandStrategyAIType == GrandStrategyAIType.CULTURE:
                grandStrategyAIDict.add(self.cultureGameValue(simulation), grandStrategyAIType)
            elif grandStrategyAIType == GrandStrategyAIType.COUNCIL:
                grandStrategyAIDict.add(self.councilGameValue(simulation), grandStrategyAIType)

            # random
            grandStrategyAIDict.add(random.randrange(50), grandStrategyAIType)

            # make the current strategy most likely
            if grandStrategyAIType == self.activeStrategy:
                grandStrategyAIDict.add(50, grandStrategyAIType)

        # Now see which Grand Strategy should be active, based on who has the highest Priority right now
        # Grand Strategy must be run for at least 10 turns
        if self.activeStrategy is None or self.numTurnsSinceActiveStrategySet(simulation.currentTurn) > 10:
            bestStrategy: GrandStrategyAIType = None
            bestPriority = -1

            for grandStrategyAIType in list(GrandStrategyAIType):
                if grandStrategyAIDict.value(grandStrategyAIType) > bestPriority:
                    bestStrategy = grandStrategyAIType
                    bestPriority = grandStrategyAIDict.value(grandStrategyAIType)

            if self.activeStrategy != bestStrategy:
                self.activeStrategy = bestStrategy
                self.turnActiveStrategySet = simulation.currentTurn
                # inform about change ?
                print(f'Player {self.player.leader} has adopted {self.activeStrategy} in turn {simulation.currentTurn}')

    def priority(self, grandStrategyAIType: GrandStrategyAIType):
        value = 0

        for flavorType in list(FlavorType):
            value += grandStrategyAIType.flavor(flavorType) * self.player.leader.flavor(flavorType)

        return 0

    def numTurnsSinceActiveStrategySet(self, turnsElapsed):
        return turnsElapsed - self.turnActiveStrategySet

    def conquestGameValue(self, simulation):
        if VictoryType.DOMINATION not in simulation.victoryTypes:
            return -100

        priority = 0

        priority += self.player.leader.traitValue(TraitType.BOLDNESS) * 10

        # How many turns must have passed before we test for having met nobody?
        if simulation.currentTurn > 20:
            metAnybody = False

            for otherPlayer in simulation.players:
                if self.player.leader == otherPlayer.leader:
                    continue

                if self.player.hasMet(otherPlayer):
                    metAnybody = True

            if not metAnybody:
                priority += -50

        if self.player.isAtWar():
            priority += 10

        return priority

    def cultureGameValue(self, simulation):
        """Returns Priority for Culture Grand Strategy"""
        # If Culture Victory isn't even available then don't bother with anything
        if VictoryType.CULTURAL not in simulation.victoryTypes:
            return -100

        return 0

    def councilGameValue(self, simulation):
        return 0
