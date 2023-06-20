import sys

from core.base import ExtendedEnum, WeightedBaseList
from game.states.builds import BuildType
from game.unitTypes import UnitMapType
from map.base import HexPoint
from map.path_finding.finder import AStarPathfinder
from map.types import ResourceType, UnitMovementType, UnitDomainType, RouteType


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

	def findTurnsAway(self, unit, tile, simulation) -> int:
		"""Determines if the builder can get to the plot. Returns -1 if no path can be found,
		otherwise it returns the # of turns to get there"""
		targetTile = simulation.tileAt(unit.location)
		if unit.location == tile.point:
			return 0

		# If this plot is far away, we'll just use its distance as an estimate of the time to get there
		# (to avoid hitting the pathfinder)
		# We'll be sure to check later to make sure we have a real path before we execute this
		if unit.domain() == UnitDomainType.land and not tile.sameContinentAs(targetTile) and not unit.canEverEmbark():
			return -1

		plotDistance = unit.location.distance(tile.point)
		if plotDistance >= 8:  # AI_HOMELAND_ESTIMATE_TURNS_DISTANCE
			return plotDistance
		else:
			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				unit.movementType(),
				unit.player,
				UnitMapType.combat,
				unit.player.canEmbark(),
				unit.player.canEnterOcean()
			)
			pathFinder = AStarPathfinder(pathFinderDataSource)

			result = pathFinder.turnsToReachTarget(unit, tile.point, simulation)
			if result == sys.maxsize:
				return -1

			return result

	def addRouteDirectives(self, unit, tile, dist: int, simulation) -> BuilderDirectiveWeightedList:
		"""Adds a directive if the unit can construct a road in the plot"""
		unitPlayer = unit.player

		bestRouteType: RouteType = self.player.bestRoute()

		# if the player can't build a route, bail out!
		if bestRouteType == RouteType.none:
			return BuilderDirectiveWeightedList()

		if pPlot.hasRoute(bestRouteType) and not tile.isRoutePillaged():
			return BuilderDirectiveWeightedList()

		# the plot was not flagged this turn, so ignore
		if pPlot.builderAIScratchPad().turn != simulation.currentTurn or tile.builderAIScratchPad().leader != unitPlayer.leader:
			return BuilderDirectiveWeightedList()

		# find the route build
		routeBuild: BuildType = BuildType.none
		if tile.isRoutePillaged():
			routeBuild = BuildType.repair
		else:
			routeType: RouteType = tile.builderAIScratchPad().routeType

			for buildType in list(BuildType):
				if buildType.route() == routeType:
					routeBuild = buildType
					break

		if routeBuild == BuildType.none:
			return BuilderDirectiveWeightedList()

		if not unit.canBuild(routeBuild, tile.point, testVisible=False, testGold=True, simulation=simulation):
			return BuilderDirectiveWeightedList()

		weight = 100  # BUILDER_TASKING_BASELINE_BUILD_ROUTES
		builderDirectiveType: BuilderDirectiveType = BuilderDirectiveType.buildRoute
		if routeBuild == BuildType.repair:
			weight = 200  # BUILDER_TASKING_BASELINE_REPAIR
			builderDirectiveType = BuilderDirectiveType.repair

		turnsAway = self.findTurnsAway(unit, tile, simulation)
		buildtime = min(1, routeBuild.buildTime(tile))

		weight = weight / (turnsAway + 1)
		weight *= weight
		weight += 100 / buildtime  # GetBuildTimeWeight(pUnit, pPlot, eRouteBuild, false, iMoveTurnsAway);
		weight *= tile.builderAIScratchPad().value
		# FIXME weight = CorrectWeight(iWeight);

		items = BuilderDirectiveWeightedList()

		directive = BuilderDirective(
			directiveType=builderDirectiveType,
			build=routeBuild,
			resource=ResourceType.none,
			target=tile.point,
			moveTurnsAway=turnsAway
		)

		items.addWeight(float(weight), directive)
		return items
