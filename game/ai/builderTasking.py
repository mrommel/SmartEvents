from core.base import ExtendedEnum, WeightedBaseList
from game.states.builds import BuildType
from game.unitTypes import UnitMapType
from map.base import HexPoint
from map.types import ResourceType, UnitMovementType, UnitDomainType


class BuilderDirectiveType(ExtendedEnum):
	none = 'none'

	buildImprovementOnResource = 'buildImprovementOnResource'  # BUILD_IMPROVEMENT_ON_RESOURCE, enabling a special resource
	buildImprovement = 'buildImprovement'  # BUILD_IMPROVEMENT, improving a tile
	buildRoute = 'buildRoute'  # BUILD_ROUTE, build a route on a tile
	repair = 'repair'  # REPAIR, repairing a pillaged route or improvement
	chop = 'chop'  # CHOP, remove a feature to improve production
	removeRoad = 'removeRoad'  # REMOVE_ROAD, remove a road from a plot


class BuilderDirective:
	def __init__(self, directiveType: BuilderDirectiveType, build: BuildType, resource: ResourceType, target: HexPoint,
				 moveTurnsAway: int):
		self.directiveType = directiveType
		self.build = build
		self.resource = resource
		self.target = target
		self.moveTurnsAway = moveTurnsAway

	def __eq__(self, other):
		if isinstance(other, BuilderDirective):
			return self.directiveType == other.directiveType and self.build == other.build and \
				self.target == other.target


class BuilderDirectiveWeightedList(WeightedBaseList):
	def __init__(self):
		super().__init__()

	def addItems(self, items):
		pass


class BuilderTaskingAI:
	def __init__(self, player):
		self.player = player

		self._numberOfCities = 0
		self._nonTerritoryPlots = []

	def update(self, simulation):
		self.updateRoutePlots(simulation)

		cities = simulation.citiesOf(self.player)
		self._numberOfCities = len(cities)

		for city in cities:
			city.cityStrategy.updateBestYields(simulation)

		return

	def evaluateBuilder(self, unit, onlyKeepBest: bool = False, onlyEvaluateWorkersPlot: bool = False, simulation=None):
		"""Use the flavor settings to determine what the worker should do"""
		if simulation is None:
			raise Exception("simulation must not be None")

		# number of cities has changed mid - turn, so we need to re-evaluate what workers should do
		if len(simulation.citiesOf(self.player)) != self._numberOfCities:
			self.update(simulation)

		tiles = []

		if onlyEvaluateWorkersPlot:
			# can't build on plots others own
			tile = simulation.tileAt(unit.location)
			if tile is not None:
				if self.player.isEqualTo(tile.owner()):
					tiles.append(tile)
		else:
			for point in self.player.area():
				tile = simulation.tileAt(point)
				if tile is not None:
					if self.player.isEqualTo(tile.owner()):
						tiles.append(tile)

		directives = BuilderDirectiveWeightedList()

		# go through all the plots the player has under their control
		for tile in tiles:
			if not self.shouldBuilderConsiderPlot(tile, unit, simulation):
				continue

			# distance weight
			# find how many turns the plot is away
			moveTurnsAway = self.findTurnsAway(unit, tile, simulation)
			if moveTurnsAway < 0:
				continue

			directives.addItems(self.addRouteDirectives(unit, tile, moveTurnsAway, simulation))
			directives.addItems(self.addImprovingResourcesDirectives(unit, tile, moveTurnsAway, simulation))
			directives.addItems(self.addImprovingPlotsDirectives(unit, tile, moveTurnsAway, simulation))
			directives.addItems(self.addChopDirectives(unit, tile, moveTurnsAway, simulation))
			# FIXME m_aDirectives.append(contentsOf: self.addScrubFalloutDirectives(unit, plot, moveTurnsAway))

		# we need to evaluate the tiles outside of our territory to build roads
		for nonTerritoryPlot in self._nonTerritoryPlots:
			if onlyEvaluateWorkersPlot:
				if nonTerritoryPlot.point != unit.location:
					continue

			if not self.shouldBuilderConsiderPlot(nonTerritoryPlot, unit, simulation):
				continue

			# distance weight
			# find how many turns the plot is away
			moveTurnsAway = self.findTurnsAway(unit, nonTerritoryPlot, simulation)
			if moveTurnsAway < 0:
				continue

			directives.addItems(self.addRouteDirectives(unit, nonTerritoryPlot, moveTurnsAway, simulation))

		bestDirective = directives.chooseLargest()

		if bestDirective is not None:
			return bestDirective

		return None

	def updateRoutePlots(self, simulation):
		"""Looks at city connections and marks plots that can be added as routes by EvaluateBuilder"""
		self._nonTerritoryPlots = []

		return

	def shouldBuilderConsiderPlot(self, tile, unit, simulation) -> bool:
		"""Evaluates all the circumstances to determine if the builder can and should evaluate the given plot"""
		dangerPlotsAI = self.player.dangerPlotsAI

		# if plot is impassable, bail!
		if tile.isImpassable(UnitMovementType.walk):
			return False

		# can't build on plots others own (unless inside a minor)
		if not self.player.isEqualTo(tile.owner()):
			return False

		# workers should not be able to work in plots that do not match their default domain
		if unit.domain() == UnitDomainType.land:
			if tile.terrain().isWater():
				return False

		elif unit.domain() == UnitDomainType.sea:
			if not tile.terrain().isWater():
				return False

		# need more planning for amphibious units
		# we should include here the ability for work boats to cross to other areas with cities
		targetTile = simulation.tileAt(unit.location)

		if not tile.sameContinentAs(targetTile):
			canCrossToNewArea = False

			if unit.domain() == UnitDomainType.sea:
				# if (pPlot->isAdjacentToArea(pUnit->area()))
				# canCrossToNewArea = true
				pass
			else:
				if unit.canEverEmbark():
					canCrossToNewArea = True

			if not canCrossToNewArea:
				return False

		# check to see if someone already has a mission here
		# if (pUnit->GetMissionAIPlot() != pPlot):
		# 	if (m_pPlayer->AI_plotTargetMissionAIs(pPlot, MISSIONAI_BUILD) > 0):
		# 		return False

		if dangerPlotsAI.dangerAt(tile.point) > 0:
			return False

		# other unit at target
		if unit.location != tile.point and simulation.unitAt(tile.point, UnitMapType.civilian) is not None:
			return False

		return True