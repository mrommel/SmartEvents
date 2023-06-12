import random

from game.civilizations import TraitType
from game.flavors import FlavorType, Flavor
from game.states.victories import VictoryType
from core.base import InvalidEnumError, ExtendedEnum


class GrandStrategyAIType(ExtendedEnum):
	none = 'none'

	conquest = 'conquest'
	culture = 'culture'
	council = 'council'

	def flavor(self, flavorType: FlavorType) -> int:
		return self._flavorBase() + self.flavorModifier(flavorType)

	def _flavorBase(self) -> int:
		if self == GrandStrategyAIType.none:
			return 0
		elif self == GrandStrategyAIType.conquest:
			return 11
		elif self == GrandStrategyAIType.culture:
			return 11
		elif self == GrandStrategyAIType.council:
			return 10

		raise InvalidEnumError(self)

	def flavorModifier(self, flavorType: FlavorType) -> int:
		item = next((flavorModifier for flavorModifier in self._flavorModifiers() if
					 flavorModifier.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def _flavorModifiers(self) -> [Flavor]:
		if self == GrandStrategyAIType.none:
			return []
		elif self == GrandStrategyAIType.conquest:
			return [
				Flavor(FlavorType.militaryTraining, 2),
				Flavor(FlavorType.growth, -1),
				Flavor(FlavorType.amenities, 1)
			]
		elif self == GrandStrategyAIType.culture:
			return [
				Flavor(FlavorType.defense, 1),
				Flavor(FlavorType.cityDefense, 1),
				Flavor(FlavorType.offense, -1)
			]
		elif self == GrandStrategyAIType.council:
			return [
				Flavor(FlavorType.defense, 1),
				Flavor(FlavorType.offense, -1),
				Flavor(FlavorType.recon, 1)
			]

		raise InvalidEnumError(self)


class GrandStrategyAIEntry:
	def __init__(self, grandStrategyAIType: GrandStrategyAIType):
		self.grandStrategyAIType = grandStrategyAIType
		self.value = 0


class GrandStrategyAIDict:
	def __init__(self):
		self.conquestStrategy = GrandStrategyAIEntry(GrandStrategyAIType.conquest)
		self.cultureStrategy = GrandStrategyAIEntry(GrandStrategyAIType.culture)
		self.councilStrategy = GrandStrategyAIEntry(GrandStrategyAIType.council)

	def add(self, value, grandStrategyAIType):
		if grandStrategyAIType == GrandStrategyAIType.none:
			pass
		elif grandStrategyAIType == GrandStrategyAIType.conquest:
			self.conquestStrategy.value += value
		elif grandStrategyAIType == GrandStrategyAIType.culture:
			self.cultureStrategy.value += value
		elif grandStrategyAIType == GrandStrategyAIType.council:
			self.councilStrategy.value += value
		else:
			raise InvalidEnumError(grandStrategyAIType)

	def value(self, grandStrategyAIType) -> float:
		if grandStrategyAIType == GrandStrategyAIType.none:
			return 0
		elif grandStrategyAIType == GrandStrategyAIType.conquest:
			return self.conquestStrategy.value
		elif grandStrategyAIType == GrandStrategyAIType.culture:
			return self.cultureStrategy.value
		elif grandStrategyAIType == GrandStrategyAIType.council:
			return self.councilStrategy.value
		else:
			raise InvalidEnumError(grandStrategyAIType)


class GrandStrategyAI:
	def __init__(self, player):
		self.player = player
		self.activeStrategy = GrandStrategyAIType.none
		self.turnActiveStrategySet = 0

	def doTurn(self, simulation):
		# hold the score for each strategy
		grandStrategyAIDict = GrandStrategyAIDict()

		for grandStrategyAIType in list(GrandStrategyAIType):
			if grandStrategyAIType == GrandStrategyAIType.none:
				continue

			# Base Priority looks at Personality Flavors (0 - 10) and multiplies * the Flavors attached to a Grand
			# Strategy (0-10), so expect a number between 0 and 100 back from this
			grandStrategyAIDict.add(self.priority(grandStrategyAIType), grandStrategyAIType)

			# real value, based on current game state
			if grandStrategyAIType == GrandStrategyAIType.conquest:
				grandStrategyAIDict.add(self.conquestGameValue(simulation), grandStrategyAIType)
			elif grandStrategyAIType == GrandStrategyAIType.culture:
				grandStrategyAIDict.add(self.cultureGameValue(simulation), grandStrategyAIType)
			elif grandStrategyAIType == GrandStrategyAIType.council:
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
		if VictoryType.domination not in simulation.victoryTypes:
			return -100

		priority = 0

		priority += self.player.leader.traitValue(TraitType.boldness) * 10

		# How many turns must have passed before we test for having met nobody?
		if simulation.currentTurn > 20:
			metAnybody = False

			for otherPlayer in simulation.players:
				if self.player.leader == otherPlayer.leader:
					continue

				if self.player.hasMetWith(otherPlayer):
					metAnybody = True

			if not metAnybody:
				priority += -50

		if self.player.isAtWar():
			priority += 10

		return priority

	def cultureGameValue(self, simulation):
		"""Returns Priority for Culture Grand Strategy"""
		# If Culture Victory isn't even available then don't bother with anything
		if VictoryType.cultural not in simulation.victoryTypes:
			return -100

		return 0

	def councilGameValue(self, simulation):
		return 0
