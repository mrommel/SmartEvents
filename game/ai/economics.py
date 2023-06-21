import sys
from typing import Optional

from core.base import InvalidEnumError
from game.ai.economicStrategies import EconomicStrategyType
from game.ai.militaryStrategies import ReconStateType
from game.unitTypes import UnitTaskType
from map.base import HexPoint
from map.improvements import ImprovementType
from map.path_finding.finder import AStarPathfinder
from map.types import UnitDomainType, FeatureType


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


class GoodyHutUnitAssignment:
	def __init__(self, unit, location: HexPoint):
		self.unit = unit
		self.location = location  # of goody hut


class ExplorationPlot:
	def __init__(self, location: HexPoint, rating: int):
		self.location = location
		self.rating = rating


class EconomicAI:
	def __init__(self, player):
		self.player = player

		self.economicStrategyAdoptions = EconomicStrategyAdoptions()
		self.flavors = []
		self.reconStateValue = ReconStateType.needed
		self.goodyHutUnitAssignments: [GoodyHutUnitAssignment] = []
		self.explorationPlotsDirty = False
		self.explorationPlotsArray: [ExplorationPlot] = []
		self.explorers = []

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

	def reconState(self) -> ReconStateType:
		return self.reconStateValue

	def updateFlavors(self):
		self.flavors = []

		for economicStrategyType in list(EconomicStrategyType):
			if self.economicStrategyAdoptions.adopted(economicStrategyType):
				for economicStrategyTypeFlavor in economicStrategyType.flavors():
					self.flavors += economicStrategyTypeFlavor

	def updatePlots(self, simulation):
		"""Go through the plots for the exploration automation to evaluate"""
		# reset all plots
		self.explorationPlotsArray = []
		self.goodyHutUnitAssignments = []

		# find the center of all the cities
		totalX = 0
		totalY = 0
		cityCount = 0

		for city in simulation.citiesOf(self.player):
			totalX += city.location.x
			totalY += city.location.y
			cityCount += 1

		for point in simulation.points():
			tile = simulation.tileAt(point)

			if not tile.isDiscoveredBy(self.player):
				continue

			if tile.hasImprovement(ImprovementType.goodyHut) and not simulation.isEnemyVisibleAt(point, self.player):
				self.goodyHutUnitAssignments.append(GoodyHutUnitAssignment(None, point))

			if tile.hasImprovement(ImprovementType.barbarianCamp) and not simulation.isEnemyVisibleAt(point, self.player):
				self.goodyHutUnitAssignments.append(GoodyHutUnitAssignment(None, point))

			domain: UnitDomainType = UnitDomainType.land
			if tile.terrain().isWater():
				domain = UnitDomainType.sea

			score = self.scoreExplore(point, self.player, range=1, domain=domain, simulation=simulation)
			if score <= 0:
				continue

			self.explorationPlotsArray.append(ExplorationPlot(point, score))

		# assign explorers to goody huts

		# build explorer list
		self.explorers = []

		for unit in simulation.unitsOf(self.player):

			# non - automated human - controlled units should not be considered
			if self.player.isHuman() and not unit.isAutomated():
				continue

			if unit.task() != UnitTaskType.explore and unit.automateType() != UnitTaskType.explore:
				continue

			if unit.army() is not None:
				continue

			self.explorers.append(unit)

		if len(self.explorers) >= len(self.goodyHutUnitAssignments):
			self.assignExplorersToHuts(simulation)
		else:
			self.assignHutsToExplorers(simulation)

		self.explorationPlotsDirty = False

	def lastTurnBuilderDisbanded(self) -> Optional[int]:
		return None

	def unitTargetGoodyPlot(self, unit, simulation):
		if self.explorationPlotsDirty:
			self.updatePlots(simulation)

		for goodyHutUnitAssignment in self.goodyHutUnitAssignments:
			goodyHutUnit = goodyHutUnitAssignment.unit
			if goodyHutUnit is not None:
				if goodyHutUnit == unit:
					goodyHutPlot = simulation.tileAt(goodyHutUnitAssignment.location)
					return goodyHutPlot

		return None

	def assignExplorersToHuts(self, simulation):
		for goodyHutUnitAssignment in self.goodyHutUnitAssignments:
			if simulation.tileAt(goodyHutUnitAssignment.location) is None:
				continue

			closestEstimateTurns = sys.maxsize
			closestUnit = None

			for explorer in self.explorers:
				distance = explorer.location.distance(goodyHutUnitAssignment.location)

				estimateTurns = sys.maxsize
				if explorer.maxMoves(simulation) >= 1:
					estimateTurns = distance / explorer.maxMoves(simulation)

				if estimateTurns < closestEstimateTurns:
					# Now check path
					pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
						explorer.movementType(),
						self.player,
						UnitMapType.combat,
						canEmbark=True,
						canEnterOcean=False
					)
					pathFinder = AStarPathfinder(pathFinderDataSource)

					if pathFinder.doesPathExist(explorer.location, goodyHutUnitAssignment.location):
						closestEstimateTurns = estimateTurns
						closestUnit = explorer

			if closestUnit is not None:
				goodyHutUnitAssignment.unit = closestUnit
				self.explorers = list(filter(lambda ex: ex.location != closestUnit.location, self.explorers))

		return

	def scoreExplore(self, plot: HexPoint, player, range: int, domain: UnitDomainType, simulation) -> int:
		resultValue = 0
		adjacencyBonus = 1
		badScore = 10
		goodScore = 100
		reallyGoodScore = 200

		for evalPoint in plot.areaWithRadius(range):
			if evalPoint == plot:
				continue

			evalTile = simulation.tileAt(evalPoint)

			if evalTile is None:
				continue

			if evalTile.isDiscoveredBy(self.player):
				continue

			if simulation.isAdjacentDiscovered(evalPoint, self.player):

				if evalPoint.distance(plot) > 1:
					viewBlocked = True
					for adjacent in evalPoint.neighbors():

						adjacentTile = simulation.tileAt(adjacent)
						if adjacentTile is None:
							continue

						if adjacentTile.isDiscoveredBy(self.player):
							distance = adjacent.distance(plot)
							if distance > range:
								continue

							# this cheats, because we can't be sure that between the target and the viewer
							if evalTile.canSee(adjacentTile, self.player, range, hasSentry=False, simulation=simulation):
								viewBlocked = False

							if not viewBlocked:
								break

					if viewBlocked:
						continue

				# "cheating" to look to see what the next tile is.
				# a human should be able to do this by looking at the transition from the tile to the next
				if domain == UnitDomainType.sea:
					if evalTile.terrain().isWater():
						resultValue += badScore
					elif evalTile.hasFeature(FeatureType.mountains) or evalTile.isHills():
						resultValue += goodScore
					else:
						resultValue += reallyGoodScore

				elif domain == UnitDomainType.land:
					if evalTile.hasFeature(FeatureType.mountains) or evalTile.isHills():
						resultValue += badScore
					elif evalTile.isHills():
						resultValue += reallyGoodScore
					else:
						resultValue += goodScore

			else:
				resultValue += goodScore

			distance = plot.distance(evalPoint)
			resultValue += (range - distance) * adjacencyBonus

		return resultValue

	def minimumSettleFertility(self) -> int:
		return 5000  # AI_STRATEGY_MINIMUM_SETTLE_FERTILITY
