import sys

from core.base import ExtendedEnum, WeightedBaseList
from game.states.builds import BuildType
from game.unitTypes import UnitMapType
from map.base import HexPoint
from map.improvements import ImprovementType
from map.path_finding.finder import AStarPathfinder
from map.types import ResourceType, UnitMovementType, UnitDomainType, RouteType, ResourceUsage, YieldType


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

	def __hash__(self):
		return hash((self.directiveType, self.build, self.target))


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

		bestRouteType: RouteType = self.player.bestRouteAt(None)

		# if the player can't build a route, bail out!
		if bestRouteType == RouteType.none:
			return BuilderDirectiveWeightedList()

		if tile.hasRoute(bestRouteType) and not tile.isRoutePillaged():
			return BuilderDirectiveWeightedList()

		# the plot was not flagged this turn, so ignore
		if tile.builderAIScratchPad().turn != simulation.currentTurn or tile.builderAIScratchPad().leader != unitPlayer.leader:
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
		buildTime = min(1, routeBuild.buildTimeOn(tile))

		weight = weight / (turnsAway + 1)
		weight *= weight
		weight += 100 / buildTime  # GetBuildTimeWeight(pUnit, pPlot, eRouteBuild, false, iMoveTurnsAway);
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

	def addImprovingResourcesDirectives(self, unit, tile, dist: int, simulation) -> BuilderDirectiveWeightedList:
		"""Evaluating a plot to see if we can build resources there"""
		# if we have a great improvement in a plot that's not pillaged, DON'T DO NOTHIN'
		# existingPlotImprovement = pPlot.improvement()
		# if existingPlotImprovement !=.none and / *GC.getImprovementInfo(
		#	existingPlotImprovement)->IsCreatedByGreatPerson() & & * / not pPlot.isImprovementPillaged()
		#	return BuilderDirectiveWeightedList()

		# check to see if a resource is here. If not, bail out!
		if not tile.hasAnyResourceFor(self.player):
			return BuilderDirectiveWeightedList()

		resource: ResourceType = ResourceType.none
		for resourceType in list(ResourceType):
			if tile.hasResource(resourceType, self.player):
				resource = resourceType

		# evaluate bonus resources as normal improvements
		if resource == ResourceType.none or resource.usage() == ResourceUsage.bonus:
			return BuilderDirectiveWeightedList()

		# loop through the build types to find one that we can use
		doBuild: BuildType = BuildType.none

		directiveList = BuilderDirectiveWeightedList()

		for buildType in list(BuildType):
			doBuild = buildType

			improvement = buildType.improvement()

			if improvement is None:
				continue

			existingPlotImprovement = tile.improvement()

			if improvement == existingPlotImprovement:
				if tile.isImprovementPillaged():
					doBuild = BuildType.repair
				else:
					# this plot already has the appropriate improvement to use the resource
					break
			else:
				# if the plot has an un-pillaged great person's creation on it, DO NOT DESTROY
				if existingPlotImprovement != ImprovementType.none:
					# CvImprovementEntry * pkExistingPlotImprovementInfo = GC.getImprovementInfo(eExistingPlotImprovement);
					# if (pkExistingPlotImprovementInfo & & pkExistingPlotImprovementInfo->IsCreatedByGreatPerson())
					# continue
					pass

			if not unit.canBuild(doBuild, tile.point, testVisible=True, testGold=False, simulation=simulation):
				break

			directiveType = BuilderDirectiveType.buildImprovementOnResource
			weight = 10  # BUILDER_TASKING_BASELINE_BUILD_RESOURCE_IMPROVEMENTS
			if doBuild == BuildType.repair:
				directiveType = BuildType.repair
				weight = 200  # BUILDER_TASKING_BASELINE_REPAIR

			# this is to deal with when the plot is already improved with another improvement that doesn't enable the resource
			investedImprovementTime = 0
			if existingPlotImprovement != ImprovementType.none:
				existingBuild: BuildType = BuildType.none

				for buildType in list(BuildType):
					if buildType.improvement() == existingPlotImprovement:
						existingBuild = buildType
						break

				if existingPlotImprovement != ImprovementType.none:
					investedImprovementTime = existingBuild.buildTimeOn(tile)

			buildtime = min(1, doBuild.buildTimeOn(tile) + investedImprovementTime + dist)
			buildTimeWeight = 100 / buildtime
			weight += buildTimeWeight
			# weight = CorrectWeight(iWeight);

			weight += self.resourceWeightFor(resource, improvement, tile.resourceQuantity())
			# weight = CorrectWeight(iWeight);

			# UpdateProjectedPlotYields(tile, eBuild);
			score = self.scorePlot(tile, buildType)
			if score > 0:
				weight *= score
				# weight = CorrectWeight(iWeight);

			production = tile.productionFromFeatureRemoval(buildType)
			if self.doesBuildHelpRush(unit, tile,buildType):
				weight += production # a nominal benefit for choosing this production

			if weight <= 0:
				continue

			directive = BuilderDirective(directiveType, buildType, resource, tile.point, dist)
			directiveList.addWeight(float(weight), directive)

		return directiveList

	def addImprovingPlotsDirectives(self, unit, tile, dist: int, simulation) -> BuilderDirectiveWeightedList:
		"""Evaluating a plot to determine what improvement could be best there"""
		existingImprovement = tile.improvement()

		# if we have a great improvement in a plot that's not pillaged, DON'T DO NOTHIN'
		#if let existingImprovement = existingImprovement & & existingImprovement !=.none & & GC.getImprovementInfo(
		#	eExistingImprovement)->IsCreatedByGreatPerson() & & !pPlot->IsImprovementPillaged())
		#     return BuilderDirectiveWeightedList()

		# if it's not within a city radius
		if not simulation.isWithinCityRadius(tile, self.player):
			return BuilderDirectiveWeightedList()

		# check to see if a non - bonus resource is here. if so, bail out!
		resource = tile.resourceFor(self.player)
		if resource != ResourceType.none:
			if resource.usage() != ResourceUsage.bonus:
				return BuilderDirectiveWeightedList()

		if tile.workingCity() is None:
			return BuilderDirectiveWeightedList()

		directiveList: BuilderDirectiveWeightedList = BuilderDirectiveWeightedList()
		tmpBuildType: BuildType = BuildType.none

		for buildType in list(BuildType):
			tmpBuildType = buildType
			improvement = tmpBuildType.improvement()

			if improvement is None:
				continue

			# if this improvement has a defense modifier, ignore it for now
			if improvement.defenseModifier() > 0:
				continue

			if improvement == tile.improvement():
				if tile.isImprovementPillaged():
					tmpBuildType = BuildType.repair
				else:
					continue
			else:
				# if the plot has an un-pillaged great person's creation on it, DO NOT DESTROY
				if existingImprovement != ImprovementType.none:
					# if improvement.->IsCreatedByGreatPerson() | | GET_PLAYER(pUnit->getOwner()).isOption(PLAYEROPTION_SAFE_AUTOMATION))
					# continue;
					pass

			# Only check to make sure our unit can build this after possibly switching this to a repair build in the block of code above
			if not unit.canBuild(tmpBuildType, tile.point, testVisible=True, testGold=True, simulation=simulation):
				continue

			# UpdateProjectedPlotYields(pPlot, eBuild);
			score = self.scorePlot(tile, tmpBuildType)

			# if we're going backward, bail out!
			if score <= 0:
				continue

			directiveType = BuilderDirectiveType.buildImprovement
			weight = 1  # BUILDER_TASKING_BASELINE_BUILD_IMPROVEMENTS
			if tmpBuildType == BuildType.repair:
				directiveType = BuildType.repair
				weight = 200  # BUILDER_TASKING_BASELINE_REPAIR
			elif improvement.yieldsFor(self.player).culture > 0:
				weight = int(100 * improvement.yieldsFor(self.player).culture)  # BUILDER_TASKING_BASELINE_ADDS_CULTURE * /
				# adjacentCulture = pImprovement->GetCultureAdjacentSameType();
				# if (iAdjacentCulture > 0)
				#	iScore *= pPlot->ComputeCultureFromImprovement(*pImprovement, eImprovement);

			buildTimeWeight = max(1, tmpBuildType.buildTimeOn(tile) + dist)
			weight += 10 if (unit.location == tile.point) else 0  # bonus for current plot
			weight += 100 / buildTimeWeight
			weight *= score
			# weight = CorrectWeight(iWeight);

			directive = BuilderDirective(directiveType, tmpBuildType, ResourceType.none, tile.point, dist)
			directiveList.addWeight(float(weight), directive)

		return directiveList

	def scorePlot(self, tile, buildType: BuildType) -> int:
		if tile is None:
			return -1

		city = tile.workingCity()
		if city is None:
			return -1

		cityStrategy = city.cityStrategy

		# preparation
		currentYields = tile.yields(self.player, ignoreFeature=False)
		projectedYields = tile.yieldsWith(buildType, self.player, ignoreFeature=False)

		score = 0.0
		anyNegativeMultiplier = False
		focusYield: YieldType = cityStrategy.focusYield

		for yieldType in list(YieldType):

			multiplier = cityStrategy.yieldDeltaFor(yieldType)
			absMultiplier = abs(multiplier)
			yieldDelta = projectedYields.value(yieldType) - currentYields.value(yieldType)

			# the multiplier being lower than zero means that we need more of this resource
			if multiplier < 0:
				anyNegativeMultiplier = True
				# this would be an improvement to the yield
				if yieldDelta > 0:
					score += projectedYields.value(yieldType) * absMultiplier
				elif yieldDelta < 0:
					# the yield would go down
					score += yieldDelta * absMultiplier
			else:
				if yieldDelta >= 0:
					score += projectedYields.value(yieldType)  # provide a nominal score to plots that improve anything
				elif yieldDelta < 0:
					score += yieldDelta * absMultiplier

		if not anyNegativeMultiplier and focusYield != YieldType.none:

			yieldDelta = projectedYields.value(focusYield) - currentYields.value(focusYield)
			if yieldDelta > 0:
				score += projectedYields.value(focusYield) * 100

		return int(score)
