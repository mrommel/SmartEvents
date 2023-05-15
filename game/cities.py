import random
from typing import Optional

from game.ai.cities import CityStrategyAI, CitySpecializationType
from game.ai.economic_strategies import EconomicStrategyType
from game.ai.grand_strategies import GrandStrategyAIType
from game.amenities import AmenitiesState
from game.buildings import BuildingType, BuildingCategoryType
from game.civilizations import LeaderWeightList, CivilizationAbility, LeaderAbility, LeaderType, \
	WeightedCivilizationList, CivilizationType
from game.districts import DistrictType
from game.governments import GovernmentType
from game.governors import GovernorType, GovernorTitle, Governor
from game.loyalties import LoyaltyState
from game.policy_cards import PolicyCardType
from game.religions import PantheonType
from game.specialists import SpecialistType
from game.types import EraType, TechType
from game.unit_types import ImprovementType
from game.wonders import WonderType
from map.base import HexPoint
from map.types import YieldList, FeatureType, TerrainType, ResourceUsage, ResourceType, YieldType
from utils.base import ExtendedEnum


class CityDistricts:
	def __init__(self, city):
		self.city = city

	def build(self, district: DistrictType, location: HexPoint):
		pass

	def hasAny(self) -> bool:
		return False

	def hasDistrict(self, district: DistrictType) -> bool:
		return False

	def updateHousing(self):
		pass


class CityBuildings:
	def __init__(self, city):
		self.city = city
		self._buildings = []

		self._defenseValue = 0
		self._housingValue = 0.0

	def build(self, building: BuildingType):
		if building in self._buildings:
			raise Exception(f'Error: {building} already build in {self.city.name}')

		self._updateDefense()
		self.updateHousing()

		self._buildings.append(building)

		# update current health when walls are built
		if building == BuildingType.ancientWalls or building == BuildingType.medievalWalls or building == BuildingType.renaissanceWalls:
			self.city.addHealthPoints(100)

	def numberOfBuildingsOf(self, buildingCategory: BuildingCategoryType) -> int:
		num: int = 0

		for buildingType in list(BuildingType):
			if self.hasBuilding(buildingType) and buildingType.categoryType() == buildingCategory:
				num += 1

		return num

	def hasBuilding(self, building: BuildingType) -> bool:
		return building in self._buildings

	def defense(self):
		return self._defenseValue

	def _updateDefense(self):
		defenseValue = 0
		
		for building in list(BuildingType):
			if self.hasBuilding(building):
				defenseValue += building.defense()

		self._defenseValue = defenseValue

	def housing(self) -> float:
		return self._housingValue

	def updateHousing(self):
		housingValue = 0.0

		for building in list(BuildingType):
			if self.hasBuilding(building):
				housingValue += building.yields().housing

		# +1 Housing per level of Walls.
		if self.city.player.government.currentGovernment() == GovernmentType.monarchy:
			if self.hasBuilding(BuildingType.ancientWalls):
				housingValue += 1.0

			if self.hasBuilding(BuildingType.medievalWalls):
				housingValue += 2.0

			if self.hasBuilding(BuildingType.renaissanceWalls):
				housingValue += 3.0

		self._housingValue = housingValue


class CityWonders:
	def __init__(self, city):
		self.city = city

	def hasWonder(self, wonder: WonderType) -> bool:
		return False


class CityProjects:
	def __init__(self, city):
		self.city = city


class WorkingPlot:
	def __init__(self, location: HexPoint, worked: bool, workedForced: bool = False):
		self.location = location
		self.worked = worked
		self.workedForced = workedForced


class CityFocusType(ExtendedEnum):
	none = 'none'  # NO_CITY_AI_FOCUS_TYPE
	food = 'food'  # CITY_AI_FOCUS_TYPE_FOOD,
	production = 'production'  # CITY_AI_FOCUS_TYPE_PRODUCTION,
	gold = 'gold'  # CITY_AI_FOCUS_TYPE_GOLD,
	greatPeople = 'greatPeople'  # CITY_AI_FOCUS_TYPE_GREAT_PEOPLE,
	science = 'science'  # CITY_AI_FOCUS_TYPE_SCIENCE,
	culture = 'culture'  # CITY_AI_FOCUS_TYPE_CULTURE,
	productionGrowth = 'productionGrowth'  # CITY_AI_FOCUS_TYPE_PROD_GROWTH, // default
	goldGrowth = 'goldGrowth'  # CITY_AI_FOCUS_TYPE_GOLD_GROWTH,
	faith = 'faith'  # CITY_AI_FOCUS_TYPE_FAITH,


class CityCitizens:
	# Keeps track of Citizens and Specialists in a City
	def __init__(self, city):
		self.city = city

		self._automated = False
		self._inited = False
		self._focusTypeValue = CityFocusType.productionGrowth
		self._workingPlots = []

		self._numberOfUnassignedCitizensValue = 0
		self._numberOfCitizensWorkingPlotsValue = 0
		self._numberOfForcedWorkingPlotsValue = 0

		self._avoidGrowthValue = False
		self._forceAvoidGrowthValue = False

		# self.numberOfSpecialists = SpecialistCountList()
		# self.numberOfSpecialists.fill()
		#
		# self.numberOfSpecialistsInBuilding = []
		# self.numberOfForcedSpecialistsInBuilding = []
		#
		# self.specialistGreatPersonProgress = GreatPersonProgressList()
		# self.specialistGreatPersonProgress.fill()

	def initialize(self, simulation):
		for location in self.city.location.areaWithRadius(radius=City.workRadius):
			wrappedLocation = location  # simulation.wrap(point=location)

			if simulation.valid(wrappedLocation):
				self._workingPlots.append(WorkingPlot(location=wrappedLocation, worked=False))

	def doFound(self, simulation):
		# always work the home plot (center)
		self.setWorkedAt(self.city.location, worked=True, useUnassignedPool=False)

	def doTurn(self, simulation):
		self.doVerifyWorkingPlots(simulation)

		if not self.city.player.isHuman():

			if simulation.currentTurn % 8 == 0:
				self.setFocusType(CityFocusType.goldGrowth)
				self.setNoAutoAssignSpecialists(True, simulation)
				self.setForcedAvoidGrowth(False, simulation)

				if self.city.hasOnlySmallFoodSurplus():
					self.setFocusType(CityFocusType.none)
					self.setNoAutoAssignSpecialists(True, simulation)

			if self.city.isCapital() and \
				self.city.cityStrategy.specialization() == CitySpecializationType.productionWonder:
				
				self.setFocusType(CityFocusType.none)
				self.setNoAutoAssignSpecialists(False, simulation)
				self.setForcedAvoidGrowth(False, simulation)

				if self.city.hasFoodSurplus():
					self.setFocusType(CityFocusType.food)
					self.setNoAutoAssignSpecialists(True, simulation)

			elif self.city.cityStrategy.specialization() == CitySpecializationType.productionWonder:
				self.setFocusType(CityFocusType.production)
				self.setNoAutoAssignSpecialists(False, simulation)
				self.setForcedAvoidGrowth(False, simulation)

				if self.city.hasOnlySmallFoodSurplus():
					self.setFocusType(CityFocusType.none)
					self.setNoAutoAssignSpecialists(True, simulation)
					self.setForcedAvoidGrowth(False, simulation)

			elif self.city.population() < 5:
				# we want a balanced growth
				self.setFocusType(CityFocusType.none)
				self.setNoAutoAssignSpecialists(True, simulation)
				self.setForcedAvoidGrowth(False, simulation)
			else:
				# Are we running at a deficit?
				inDeficit = self.city.player.economicAI.adoptedEconomicStrategy(EconomicStrategyType.losingMoney)
				if inDeficit:
					self.setFocusType(CityFocusType.goldGrowth)
					self.setNoAutoAssignSpecialists(False, simulation)
					self.setForcedAvoidGrowth(False, simulation)

					if self.city.hasOnlySmallFoodSurplus():
						self.setFocusType(CityFocusType.none)
						self.setNoAutoAssignSpecialists(True, simulation)

					elif simulation.currentTurn % 3 == 0 and \
						self.city.player.grandStrategyAI.activeStrategy == GrandStrategyAIType.culture:

						self.setFocusType(CityFocusType.culture)
						self.setNoAutoAssignSpecialists(True, simulation)
						self.setForcedAvoidGrowth(False, simulation)

						if self.city.hasOnlySmallFoodSurplus():
							self.setFocusType(CityFocusType.none)
							self.setNoAutoAssignSpecialists(True, simulation)

					else:
						# we aren't a small city, building a wonder, or going broke
						self.setNoAutoAssignSpecialists(False, simulation)
						self.setForcedAvoidGrowth(False, simulation)

						currentSpecialization = self.city.cityStrategy.specialization()
						if currentSpecialization != CitySpecializationType.none:
							yieldType = currentSpecialization.yieldType()
							if yieldType == YieldType.food:
								self.setFocusType(CityFocusType.food)
							elif yieldType == YieldType.production:
								self.setFocusType(CityFocusType.productionGrowth)
							elif yieldType == YieldType.gold:
								self.setFocusType(CityFocusType.gold)
							elif yieldType == YieldType.science:
								self.setFocusType(CityFocusType.science)
							else:
								self.setFocusType(CityFocusType.none)
						else:
							self.setFocusType(CityFocusType.none)

		# print("working: \(self.numCitizensWorkingPlots()) + spec: \(self.totalSpecialistCount()) + unassigned: \(self.numUnassignedCitizens()) for \(city.population())")

		self.doReallocateCitizens(simulation)

		sum = self.numberOfCitizensWorkingPlots() + self.totalSpecialistCount() + self.numberOfUnassignedCitizens()
		assert (sum <= self.city.population(), "Gameplay: More workers than population in the city.")
		# print("working: \(self.numCitizensWorkingPlots()) + spec: \(self.totalSpecialistCount()) + unassigned: \(self.numUnassignedCitizens()) for \(city.population())")

	def workingTileLocations(self) -> [HexPoint]:
		locations: [HexPoint] = []

		for plot in self._workingPlots:
			locations.append(plot.location)

		return locations

	def workedTileLocations(self) -> [HexPoint]:
		locations: [HexPoint] = []

		for plot in self._workingPlots:
			if self.isWorkedAt(plot.location):
				locations.append(plot.location)

		return locations

	def setWorkedAt(self, location: HexPoint, worked: bool, useUnassignedPool: bool = True):
		# Tell a City to start or stop working a Plot.  Citizens will go to/from the Unassigned Pool
		# if the 3rd argument is true
		plot = next((p for p in self._workingPlots if p.location == location), None)

		if plot is None:
			raise Exception("not a valid plot to check for this city")

		if plot.worked != worked:
			# Don't look at the center Plot of a City, because we always work it for free
			if plot.location != self.city.location:
				plot.worked = worked

				# Alter the count of Plots being worked by Citizens
				if worked:
					self.changeNumberOfCitizensWorkingPlotsBy(delta=1)

					if useUnassignedPool:
						self.changeNumberOfUnassignedCitizensBy(delta=-1)
				else:
					self.changeNumberOfCitizensWorkingPlotsBy(delta=-1)

					if useUnassignedPool:
						self.changeNumberOfUnassignedCitizensBy(delta=1)

		return

	def forceWorkingPlatAt(self, location: HexPoint, force: bool, simulation):
		"""Tell our City it MUST work a particular CvPlot"""
		plot = next((p for p in self._workingPlots if p.location == location), None)

		if plot is None:
			raise Exception("not a valid plot to check for this city")

		if plot.workedForced != force:

			plot.workedForced = force

			# Change the count of how many are forced
			if force:
				self.changeNumberOfForcedWorkingPlotsBy(delta=1)
				self.doValidateForcedWorkingPlots(simulation)
			else:
				self.changeNumberOfForcedWorkingPlotsBy(delta=-1)

			self.doReallocateCitizens(simulation)

		return

	def isWorkedAt(self, location: HexPoint) -> bool:
		# Is our City working a CvPlot?
		plot: Optional[WorkingPlot] = next((p for p in self._workingPlots if p.location == location), None)

		if plot is None:
			return False

		return plot.worked

	def isForcedWorkedAt(self, location: HexPoint) -> bool:
		# Has our City been told it MUST a particular CvPlot?
		plot: Optional[WorkingPlot] = next((p for p in self._workingPlots if p.location == location), None)

		if plot is None:
			return False

		return plot.workedForced

	def focusType(self) -> CityFocusType:
		return self._focusTypeValue

	def setFocusType(self, focusType: CityFocusType):
		self._focusTypeValue = focusType

	def numberOfCitizensWorkingPlots(self) -> int:
		return self._numberOfCitizensWorkingPlotsValue

	def changeNumberOfCitizensWorkingPlotsBy(self, delta: int):
		"""Changes how many Citizens are working Plots"""
		self._numberOfCitizensWorkingPlotsValue += delta

	def numberOfUnassignedCitizens(self) -> int:
		"""How many Citizens need to be given a job?"""
		return self._numberOfUnassignedCitizensValue

	def changeNumberOfUnassignedCitizensBy(self, delta: int):
		"""Changes how many Citizens need to be given a job"""
		self._numberOfUnassignedCitizensValue += delta

		if self._numberOfUnassignedCitizensValue < 0:
			raise Exception('unassigned citizen must be positive')

	def numberOfForcedWorkingPlots(self) -> int:
		"""How many plots have we forced to be worked?"""
		return self._numberOfForcedWorkingPlotsValue

	def changeNumberOfForcedWorkingPlotsBy(self, delta: int):
		self._numberOfForcedWorkingPlotsValue += delta

	def doValidateForcedWorkingPlots(self, simulation):
		"""Make sure we don't have more forced working plots than we have citizens to work"""
		numForcedWorkingPlotsToDemote = self.numberOfForcedWorkingPlots() - self.numberOfCitizensWorkingPlots()

		if numForcedWorkingPlotsToDemote > 0:
			for _ in range(numForcedWorkingPlotsToDemote):
				self.doRemoveWorstForcedWorkingPlot(simulation)

	def doReallocateCitizens(self, simulation):
		"""Optimize our Citizen Placement"""
		# Make sure we don't have more forced working plots than we have citizens working.
		# If so, clean it up before reallocating
		self.doValidateForcedWorkingPlots(simulation)

		# Remove all the allocated guys
		numberOfCitizensToRemove = self.numberOfCitizensWorkingPlots()
		for _ in range(numberOfCitizensToRemove):
			self.doRemoveWorstCitizen(simulation)

		# Remove Non-Forced Specialists in Buildings
		for buildingType in list(BuildingType):
			# Have this Building in the City?
			if self.city.buildings.hasBuilding(building=buildingType):
				# Don't include Forced guys
				numSpecialistsToRemove = self.numberOfSpecialistsIn(buildingType) - self.numberOfForcedSpecialistsIn(buildingType)
				# Loop through guys to remove (if there are any)
				for _ in range(numSpecialistsToRemove):
					self.doRemoveSpecialistFrom(buildingType, forced=False, simulation=simulation)

		# Remove Default Specialists
		numDefaultsToRemove = self.numberOfDefaultSpecialists() - self.numberOfForcedDefaultSpecialists()
		for _ in range(numDefaultsToRemove):
			self.changeNumberOfDefaultSpecialistsBy(delta=-1)

		# Now put all the unallocated guys back
		numToAllocate = self.numberOfUnassignedCitizens()
		for _ in range(numToAllocate):
			self.doAddBestCitizenFromUnassigned(simulation)

	def isForcedAvoidGrowth(self) -> bool:
		return self._forceAvoidGrowthValue

	def setForcedAvoidGrowth(self, forcedAvoidGrowth: bool, simulation):
		if self._forceAvoidGrowthValue != forcedAvoidGrowth:
			self._forceAvoidGrowthValue = forcedAvoidGrowth
			self.doReallocateCitizens(simulation)

	def doRemoveWorstForcedWorkingPlot(self, simulation):
		"""Remove the Forced status from the worst ForcedWorking plot"""
		worstPlotValue: int = -1
		worstPlotPoint: Optional[HexPoint] = None

		# Look at all workable Plots
		for workableTile in self.workableTiles(simulation):
			if self.city is None:
				raise Exception("cant get city")

			# skip home plot
			if workableTile.point == self.city.location:
				continue

			if self.isForcedWorkedAt(workableTile.point):
				value = self.plotValueOf(workableTile.point, useAllowGrowthFlag=False, simulation=simulation)

				# First, or worst yet?
				if worstPlotValue == -1 or value < worstPlotValue:
					worstPlotValue = value
					worstPlotPoint = workableTile.point

		if worstPlotPoint is not None:
			self.forceWorkingPlotAt(worstPlotPoint, force=False, simulation=simulation)

	def plotValueOf(self, point: HexPoint, useAllowGrowthFlag: bool, simulation):
		"""What is the overall value of the current Plot?"""
		tile = simulation.tileAt(point)

		if tile is None:
			raise Exception('cant get tile')

		value = 0.0
		yields = tile.yieldsFor(self.city.player, ignoreFeature=False)

		# Yield Values
		foodYieldValue = 12 * yields.value(YieldType.food)
		productionYieldValue = 8 * yields.value(YieldType.production)
		goldYieldValue = 10 * yields.value(YieldType.gold)
		scienceYieldValue = 6 * yields.valueOf(YieldType.science)
		cultureYieldValue = 8 * yields.culture

		# How much surplus food are we making?
		# excessFoodTimes100 = city.foodConsumption()

		avoidGrowth = self.isAvoidGrowth()

		# City Focus
		focusType = self.focusType()
		if focusType == CityFocusType.food:
			foodYieldValue *= 5
		elif focusType == CityFocusType.production:
			productionYieldValue *= 4
		elif focusType == CityFocusType.gold:
			goldYieldValue *= 4
		elif focusType == CityFocusType.science:
			scienceYieldValue *= 4
		elif focusType == CityFocusType.culture:
			cultureYieldValue *= 4
		elif focusType == CityFocusType.goldGrowth:
			foodYieldValue *= 2
			goldYieldValue *= 5
		elif focusType == CityFocusType.productionGrowth:
			foodYieldValue *= 2
			productionYieldValue *= 5

		# Food can be worth less if we don't want to grow
		if useAllowGrowthFlag and self.city.hasEnoughFood() and avoidGrowth:
			# If we at least have enough Food to feed everyone, zero out the value of additional food
			foodYieldValue = 0
		else:
			# We want to grow here
			# If we have a non-default and non-food focus, only worry about getting to 0 food
			if focusType != CityFocusType.none and focusType != CityFocusType.food and \
				focusType != CityFocusType.productionGrowth and focusType != CityFocusType.goldGrowth:

				if not self.city.hasEnoughFood():
					foodYieldValue *= 2
			elif not avoidGrowth:
				# If our surplus is not at least 2, really emphasize food plots
				if self.city.hasOnlySmallFoodSurplus():
					foodYieldValue *= 2

		if focusType in [CityFocusType.none, CityFocusType.productionGrowth, CityFocusType.goldGrowth] and \
			not avoidGrowth and self.city.population() < 5:
			foodYieldValue *= 3

		value += foodYieldValue
		value += productionYieldValue
		value += goldYieldValue
		value += scienceYieldValue
		value += cultureYieldValue

		return int(value)

	def isAvoidGrowth(self) -> bool:
		"""Is this City avoiding growth?"""
		return self._avoidGrowthValue

	def forceWorkingPlotAt(self, worstPlotPoint, force, simulation):
		pass

	def doVerifyWorkingPlots(self, simulation):
		pass

	def setNoAutoAssignSpecialists(self, param, simulation):
		pass

	def totalSpecialistCount(self) -> int:
		return 0

	def doRemoveWorstCitizen(self, 
							 removeForcedStatus: bool = False,
							 dontChangeSpecialist: SpecialistType = SpecialistType.none,
							 simulation = None) -> bool:
		"""Pick the worst Plot to stop working"""
		# Are all of our guys already not working Plots?
		if self.numberOfUnassignedCitizens() == self.city.population():
			return False

		# Find default Specialist to pull off, if there is one
		if self.numberOfDefaultSpecialists() > 0:

			# Do we either have unforced default specialists we can remove?
			if self.numberOfDefaultSpecialists() > self.numberOfForcedDefaultSpecialists():
				self.changeNumberOfDefaultSpecialistsBy(-1)
				return True

			if self.numberOfDefaultSpecialists() > self.city.population():
				self.changeNumberOfForcedDefaultSpecialists(-1)
				self.changeNumberOfDefaultSpecialistsBy(-1)
				return True


		# No Default Specialists, remove a working Pop, if there is one
		worstPlot, _ = self.bestCityPlotWithValue(wantBest=False, wantWorked=True, simulation=simulation)

		if worstPlot is not None:
			self.setWorkedAt(worstPlot, worked=False)

			# If we were force - working this Plot, turn it off
			if removeForcedStatus:
				if self.isForcedWorkedAt(worstPlot):
					self.forceWorkingPlotAt(worstPlot, force=False, simulation=simulation)

			return True

		else:
			# Have to resort to pulling away a good Specialist
			if self.doRemoveWorstSpecialist(dontChangeSpecialist=dontChangeSpecialist, simulation=simulation):
				return True

		return False

	def numberOfDefaultSpecialists(self) -> int:
		return 0

	def doRemoveWorstSpecialist(self, dontChangeSpecialist, simulation):
		pass

	def numberOfForcedDefaultSpecialists(self) -> int:
		return 0

	def changeNumberOfDefaultSpecialistsBy(self, delta: int):
		pass

	def changeNumberOfForcedDefaultSpecialists(self, delta: int):
		pass

	def bestCityPlotWithValue(self, wantBest, wantWorked, simulation):
		pass

	def numberOfSpecialistsIn(self, buildingType: BuildingType) -> int:
		return 0

	def numberOfForcedSpecialistsIn(self, buildingType: BuildingType) -> int:
		return 0

	def doAddBestCitizenFromUnassigned(self, simulation):
		pass

	def doRemoveSpecialistFrom(self, buildingType, forced, simulation):
		pass

	def workableTiles(self, simulation):
		area = self.city.location.areaWithRadius(radius=City.workRadius)
		result = []

		for neighbor in area:
			if not simulation.valid(neighbor):
				continue

			tile = simulation.tileAt(neighbor)
			result.append(tile)

		return result


class CityGreatWorks:
	def __init__(self, city):
		self.city = city


class CityReligion:
	def __init__(self, city):
		self.city = city


class CityTradingPosts:
	def __init__(self, city):
		self.city = city

	def buildTradingPost(self, leader: LeaderType):
		pass


class CityTourism:
	def __init__(self, city):
		self.city = city


class AgeType(ExtendedEnum):
	normal = 'normal'


class RouteType(ExtendedEnum):
	ancientRoad = 'ancientRoad'


class GossipType(ExtendedEnum):
	districtConstructed = 'districtConstructed'


class MomentType(ExtendedEnum):
	dedicationTriggered = 'dedicationTriggered'
	worldsFirstNeighborhood = 'worldsFirstNeighborhood'
	firstNeighborhoodCompleted = 'firstNeighborhoodCompleted'


class DedicationType(ExtendedEnum):
	monumentality = 'monumentality'


class YieldValues:
	pass


class YieldValues:
	def __init__(self, value: float, percentage: float = 0.0):
		self.value = value
		self.percentage = percentage

	def calc(self) -> float:
		return self.value * self.percentage

	def __add__(self, other):
		if isinstance(other, float):
			return YieldValues(self.value + other, self.percentage)
		elif isinstance(other, YieldValues):
			return YieldValues(self.value + other.value, self.percentage + other.percentage)
		else:
			raise Exception(f'invalid parameter: {other}')


class CityState(ExtendedEnum):
	singapore = 'singapore'
	johannesburg = 'johannesburg'
	auckland = 'auckland'


class City:
	workRadius = 3

	def __init__(self, name: str, location: HexPoint, isCapital: bool, player):
		self.name = name
		self.location = location
		self.capitalValue = isCapital
		self.everCapitalValue = isCapital
		self._populationValue = 0
		self.gameTurnFoundedValue = 0
		self._foodBasketValue = 1.0

		self.player = player
		self.leader = player.leader
		self.originalLeaderValue = player.leader
		self.previousLeaderValue = None

		self.isFeatureSurroundedValue = False
		self.threatVal = 0
		self._garrisonedUnitValue = None

		self.healthPointsValue = 200
		self.amenitiesForWarWearinessValue = 0

		self._luxuries = []

		self.productionAutomatedValue = False
		self.baseYieldRateFromSpecialists = YieldList()
		self.extraSpecialistYield = YieldList()
		self.numPlotsAcquiredList = LeaderWeightList()

		self.featureProductionValue = 0.0

		# ai
		self.cityStrategyAI = CityStrategyAI(self)

		# init later via 'initialize' method
		self.districts = None
		self.buildings = None
		self.wonders = None
		self.projects = None

		self.cityStrategy = None
		self.cityCitizens = None
		self.greatWorks = None
		self.cityReligion = None
		self.cityTradingPosts = None
		self.cityTourism = None

	def __str__(self):
		return f'City "{self.name}" at {self.location}'

	def doFoundMessage(self):
		pass

	def initialize(self, simulation):
		self.gameTurnFoundedValue = simulation.currentTurn

		self.districts = CityDistricts(city=self)
		self.buildings = CityBuildings(city=self)
		self.wonders = CityWonders(city=self)
		self.projects = CityProjects(city=self)

		self.buildDistrict(district=DistrictType.cityCenter, location=self.location, simulation=simulation)

		if self.capitalValue:
			self.buildings.build(building=BuildingType.palace)

		self.cityStrategy = CityStrategyAI(city=self)
		self.cityCitizens = CityCitizens(city=self)
		self.greatWorks = CityGreatWorks(city=self)
		self.cityReligion = CityReligion(city=self)
		self.cityTradingPosts = CityTradingPosts(city=self)
		self.cityTourism = CityTourism(city=self)

		self.cityCitizens.initialize(simulation=simulation)

		if self.player.leader.civilization().ability() == CivilizationAbility.allRoadsLeadToRome:
			self.cityTradingPosts.buildTradingPost(leader=self.player.leader)

		if self.player.leader.ability() == LeaderAbility.trajansColumn:
			# All founded cities start with a free monument in the City Center.
			try:
				self.buildings.build(building=BuildingType.monument)
			except:
				pass

		# Update Proximity between this Player and all others
		for otherPlayer in simulation.players:
			if otherPlayer.leader != self.player.leader:
				if otherPlayer.isAlive() and self.player.diplomacyAI.hasMetWith(player=otherPlayer):
					# Fixme
					# Players do NOT have to know one another in order to calculate proximity.
					# Having this info available(even when they haven't met) can be useful
					self.player.doUpdateProximityTowards(otherPlayer, simulation)
					otherPlayer.doUpdateProximityTowards(self.player, simulation)

		self.doUpdateCheapestPlotInfluence(simulation=simulation)

		# discover the surrounding area
		for pointToDiscover in self.location.areaWithRadius(radius=2):
			if not simulation.valid(pointToDiscover):
				continue

			tile = simulation.tileAt(pointToDiscover)
			tile.discoverBy(self.player, simulation)

		# Every city automatically creates a road on its tile, which remains even 
		# if the feature is pillaged or the city is razed.
		tile = simulation.tileAt(self.location)
		tile.setRoute(RouteType.ancientRoad)

		# claim ownership for direct neighbors( if not taken)
		for pointToClaim in self.location.areaWithRadius(radius=1):
			tile = simulation.tileAt(pointToClaim)
			try:
				# FIXME
				tile.setOwner(player=self.player)
				tile.setWorkingCity(city=self)
			except Exception as e:
				raise Exception(f'cant set owner: {e}')

		# Founded cities start with eight additional tiles.
		if self.player.leader.civilization().ability() == CivilizationAbility.motherRussia:
			tiles = self.location.areaWithRadius(radius=2).points
			random.shuffle(tiles)
			additional = 0

			for pointToClaim in tiles:
				tile = simulation.tileAt(pointToClaim)

				if not tile.hasOwner() and additional < 8:
					try:           
						tile.setOwner(player=self.player)
						tile.setWorkingCity(city=self)

						additional += 1
					except:
						raise Exception('cant set owner')

		self.cityCitizens.doFound(simulation=simulation)

		self.player.updatePlots(simulation=simulation)

		if self.capitalValue:
			self.player.setCapitalCity(city=self, simulation=simulation)

		self.setPopulation(newPopulation=1, reassignCitizen=True, simulation=simulation)

	def featureProduction(self) -> float:
		return self.featureProductionValue

	def changeFeatureProduction(self, change: float):
		self.featureProductionValue += change

	def setFeatureProduction(self, value: float):
		self.featureProductionValue = value

	def buildDistrict(self, district: DistrictType, location: HexPoint, simulation):
		tile = simulation.tileAt(location)

		try:
			self.districts.build(district=district, location=location)
			self.updateEurekas(simulation)

			# moments
			if self.player.currentAge() == AgeType.normal and self.player.hasDedication(DedicationType.monumentality):
				if district.isSpecialty():
					self.player.addMoment(MomentType.dedicationTriggered, DedicationType.monumentality, simulation)

			# check quests
			# for quest in self.player.ownQuests(simulation):
			# 	if case .constructDistrict(type: let district) = quest.type {
			# 		if district == districtType && player.leader == quest.leader {
			# 			let cityStatePlayer = gameModel.cityStatePlayer(for: quest.cityState)
			# 			cityStatePlayer?.fulfillQuest(by: player.leader, in: gameModel)

			if district == DistrictType.preserve:
				# Initiate a Culture Bomb on adjacent unowned tiles
				for neighborPoint in location.neighbors():

					neighborTile = simulation.tileAt(neighborPoint)

					if not neighborTile.hasOwner() and not neighborTile.isWorked():
						self.doAcquirePlot(neighborPoint, simulation)

			if district == DistrictType.neighborhood:
				if not self.player.hasMoment(MomentType.firstNeighborhoodCompleted) and \
					not self.player.hasMoment(MomentType.worldsFirstNeighborhood):

					# check if someone else already had a built a neighborhood district
					if simulation.anyHasMoment(MomentType.worldsFirstNeighborhood):
						self.player.addMoment(MomentType.firstNeighborhoodCompleted, simulation)
					else:
						self.player.addMoment(MomentType.worldsFirstNeighborhood, simulation)

			if district == DistrictType.governmentPlaza:
				# governmentPlaza - Awards +1 Governor Title.
				self.player.addGovernorTitle()

			# send gossip
			if district.isSpecialty():
				simulation.sendGossip(type=GossipType.districtConstructed, meta=district, player=self.player)

			tile.buildDistrict(district)
			if district != DistrictType.cityCenter:
				# the city does not exist yet - so no update
				simulation.userInterface.refreshTile(tile)
		except Exception as e:
			raise Exception(f'cant build district: already build => {e}')

	def population(self) -> int:
		return int(self._populationValue)

	def setPopulation(self, newPopulation: int, reassignCitizen: bool, simulation):
		"""Be very careful with setting bReassignPop to false.  This assumes that the caller
		is manually adjusting the worker assignments *and* handling the setting of
		the CityCitizens unassigned worker value."""
		oldPopulation = self.population()
		populationChange = newPopulation - oldPopulation

		if oldPopulation != newPopulation:
			# If we are reducing population, remove the workers first
			if reassignCitizen and populationChange < 0:
				# Need to Remove Citizens
				for _ in range(-populationChange):
					self.cityCitizens.doRemoveWorstCitizen(simulation)

				# Fixup the unassigned workers
				unassignedWorkers = self.cityCitizens.numberOfUnassignedCitizens()
				self.cityCitizens.changeNumberOfUnassignedCitizensBy(max(populationChange, -unassignedWorkers))

			if populationChange > 0:
				self.cityCitizens.changeNumberOfUnassignedCitizensBy(populationChange)

		self._populationValue = float(newPopulation)

	def doUpdateCheapestPlotInfluence(self, simulation):
		pass

	def doAcquirePlot(self, point: HexPoint, simulation):
		pass

	def updateEurekas(self, simulation):
		pass

	def governor(self) -> Optional[Governor]:
		return None

	### yields ###

	def foodPerTurn(self, simulation) -> float:
		foodPerTurn: YieldValues = YieldValues(value=0.0, percentage=1.0)

		foodPerTurn += YieldValues(value=self._foodFromTiles(simulation))
		foodPerTurn += YieldValues(value=self._foodFromGovernmentType())
		foodPerTurn += YieldValues(value=self._foodFromBuildings(simulation))
		foodPerTurn += YieldValues(value=self._foodFromWonders(simulation))
		foodPerTurn += YieldValues(value=self._foodFromTradeRoutes(simulation))
		foodPerTurn += self._foodFromGovernors(simulation)

		# cap yields based on loyalty
		foodPerTurn += YieldValues(value=0.0, percentage=self.loyaltyState().yieldPercentage())

		return foodPerTurn.calc()

	def productionPerTurn(self, simulation) -> float:
		productionPerTurnValue: YieldValues = YieldValues(value=0.0, percentage=1.0)

		productionPerTurnValue += YieldValues(value=self._productionFromTiles(simulation))
		productionPerTurnValue += YieldValues(value=self._productionFromGovernmentType())
		productionPerTurnValue += YieldValues(value=self._productionFromDistricts(simulation))
		productionPerTurnValue += YieldValues(value=self._productionFromBuildings())
		productionPerTurnValue += YieldValues(value=self._productionFromTradeRoutes(simulation))
		productionPerTurnValue += YieldValues(value=self.featureProduction())

		# cap yields based on loyalty
		productionPerTurnValue += YieldValues(value=0.0, percentage=self.loyaltyState().yieldPercentage())

		return productionPerTurnValue.calc()

	def goldPerTurn(self, simulation) -> float:
		goldPerTurn: YieldValues = YieldValues(value=0.0, percentage=1.0)

		goldPerTurn += YieldValues(value=self._goldFromTiles(simulation))
		goldPerTurn += self._goldFromGovernmentType()
		goldPerTurn += YieldValues(value=self._goldFromDistricts(simulation))
		goldPerTurn += YieldValues(value=self._goldFromBuildings())
		goldPerTurn += YieldValues(value=self._goldFromWonders())
		goldPerTurn += YieldValues(value=self._goldFromTradeRoutes(simulation))
		goldPerTurn += YieldValues(value=self._goldFromEnvoys(simulation))

		# cap yields based on loyalty
		goldPerTurn += YieldValues(value=0.0, percentage=self.loyaltyState().yieldPercentage())

		return goldPerTurn.calc()

	def _productionFromTiles(self, simulation) -> float:
		hasHueyTeocalli = self.player.hasWonder(WonderType.hueyTeocalli, simulation)
		hasStBasilsCathedral = self.player.hasWonder(WonderType.stBasilsCathedral, simulation)
		productionValue: float = 0.0

		centerTile = simulation.tileAt(self.location)
		if centerTile is not None:
			productionValue += centerTile.yields(self.player, ignoreFeature=False).production

			# The yield of the tile occupied by the city center will be increased to 2 Food and 1 production, if either
			# was previously lower (before any bonus yields are applied).
			if productionValue < 1.0:
				productionValue = 1.0

		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				workedTile = simulation.tileAt(point)
				productionValue += workedTile.yields(self.player, ignoreFeature=False).production

				# city has petra: +2 Food, +2 Gold, and +1 Production
				# on all Desert tiles for this city(non - Floodplains).
				if workedTile.terrain() == TerrainType.desert and \
					not workedTile.hasFeature(FeatureType.floodplains) and \
					self.wonders.hasWonder(WonderType.petra):
					productionValue += 1.0

				# motherRussia
				if workedTile.terrain() == TerrainType.tundra and \
					self.player.leader.civilization().ability() == CivilizationAbility.motherRussia:
					# Tundra tiles provide + 1 Faith and +1 Production, in addition to their usual yields.
					productionValue += 1.0

				# stBasilsCathedral
				if workedTile.terrain() == TerrainType.tundra and hasStBasilsCathedral:
					# +1 Food, +1 Production, and +1 Culture on all Tundra tiles for this city.
					productionValue += 1.0

				# player has hueyTeocalli: +1 Food and +1 Production for each Lake tile in your empire.
				if workedTile.hasFeature(FeatureType.lake) and hasHueyTeocalli:
					productionValue += 1.0

				# city has chichenItza: +2 Culture and +1 Production to all Rainforest tiles for this city.
				if workedTile.hasFeature(FeatureType.rainforest) and self.hasWonder(WonderType.chichenItza):
					productionValue += 1.0

				# etemenanki - +2 Science and +1 Production to all Marsh tiles in your empire.
				if workedTile.hasFeature(FeatureType.marsh) and self.player.hasWonder(WonderType.etemenanki, simulation):
					productionValue += 1.0

				# etemenanki - +1 Science and +1 Production on all Floodplains tiles in this city.
				if workedTile.hasFeature(FeatureType.floodplains) and self.hasWonder(WonderType.etemenanki):
					productionValue += 1.0

				# godOfTheSea - 1 Production from Fishing Boats.
				if workedTile.improvement() == ImprovementType.fishingBoats and \
					self.player.religion.pantheon() == PantheonType.godOfTheSea:
					productionValue += 1.0

				# ladyOfTheReedsAndMarshes - +2 Production from Marsh, Oasis, and Desert Floodplains.
				if (workedTile.hasFeature(FeatureType.marsh) or workedTile.hasFeature(FeatureType.oasis) or \
					workedTile.hasFeature(FeatureType.floodplains)) and \
					self.player.religion.pantheon() == PantheonType.ladyOfTheReedsAndMarshes:
					productionValue += 1.0

				# godOfCraftsmen - +1 Production and +1 Faith from improved Strategic resources.
				if self.player.religion.pantheon() == PantheonType.godOfCraftsmen:
					if workedTile.resourceFor(self.player).usage() == ResourceUsage.strategic and \
						workedTile.hasAnyImprovement():
						productionValue += 1.0

				# goddessOfTheHunt - +1 Food and +1 Production from Camps.
				if workedTile.improvement() == ImprovementType.camp and \
					self.player.religion.pantheon() == PantheonType.goddessOfTheHunt:
					productionValue += 1.0

				# auckland suzerain bonus
				# Shallow water tiles worked by Citizens provide +1 Production.
				# Additional +1 when you reach the Industrial Era
				if self.player.isSuzerainOf(CityState.auckland, simulation):
					if workedTile.terrain() == TerrainType.shore:
						productionValue += 1.0

					if self.player.currentEra() == EraType.industrial:
						productionValue += 1.0

				# johannesburg suzerain bonus
				# Cities receive + 1 Production for every improved resource type.
				# After researching Industrialization it becomes +2[Production] Production.
				if self.player.isSuzerainOf(CityState.johannesburg, simulation):
					if workedTile.hasAnyImprovement() and workedTile.resourceFor(self.player) != ResourceType.none:
						productionValue += 1.0

						if self.player.hasTech(TechType.industrialization):
							productionValue += 1.0

		return productionValue

	def _productionFromGovernmentType(self):
		productionFromGovernmentType: float = 0.0

		# yields from government
		if self.player.government is not None:
			# https://civilization.fandom.com/wiki/Autocracy_(Civ6)
			# +1 to all yields for each government building and Palace in a city.
			if self.player.government.currentGovernment() == GovernmentType.autocracy:
				productionFromGovernmentType += self.buildings.numberOfBuildingsOf(BuildingCategoryType.government)

			# urbanPlanning: +1 Production in all cities.
			if self.player.government.hasCard(PolicyCardType.urbanPlanning):
				productionFromGovernmentType += 1

		return productionFromGovernmentType

	def _productionFromDistricts(self, simulation):
		productionFromDistricts: float = 0.0
		policyCardModifier: float = 1.0

		# yields from cards
		# craftsmen - +100% Industrial Zone adjacency bonuses.
		if self.player.government.hasCard(PolicyCardType.craftsmen):
			policyCardModifier += 1.0

		# fiveYearPlan - +100% Campus and Industrial Zone district adjacency bonuses.
		if self.player.government.hasCard(PolicyCardType.fiveYearPlan):
			policyCardModifier += 1.0

		# collectivism - Farms +1 [Food] Food. All cities +2 [Housing] Housing. +100% Industrial Zone adjacency bonuses.
		# BUT: Great People Points earned 50% slower.
		if self.player.government.hasCard(PolicyCardType.collectivism):
			policyCardModifier += 1.0

		if self.districts.hasDistrict(DistrictType.industrialZone):
			industrialLocation = self.locationOf(DistrictType.industrialZone)

			for neighbor in industrialLocation.neighbors():
				neighborTile = simulation.tileAt(neighbor)

				# Major bonus (+2 Production) for each adjacent Aqueduct, Dam, Canal or Bath
				if neighborTile.district() == DistrictType.aqueduct:  # or
					# neighborTile.district() == .dam or
					# neighborTile.district() == .canal or
					# neighborTile.district() == .bath */ {
					productionFromDistricts += 2.0 * policyCardModifier
					continue

				# Standard bonus (+1 Production) for each adjacent Strategic Resource and Quarry
				if neighborTile.hasImprovement(ImprovementType.quarry):
					productionFromDistricts += 1.0 * policyCardModifier
					continue

				if neighborTile.resourceFor(self.player).usage() == ResourceUsage.strategic:
					productionFromDistricts += 1.0 * policyCardModifier

				# Minor bonus (+½ Production) for each adjacent district tile, Mine or Lumber Mill
				if neighborTile.hasImprovement(ImprovementType.mine):  # /*|| neighborTile.has(improvement: .lumberMill)*/ {
					productionFromDistricts += 0.5 * policyCardModifier

				if neighborTile.district() != DistrictType.none:
					productionFromDistricts += 0.5 * policyCardModifier

		return productionFromDistricts

	def _productionFromBuildings(self):
		productionFromBuildings: float = 0.0

		# gather food from builds
		for building in list(BuildingType):
			if self.buildings.hasBuilding(building):
				productionFromBuildings += building.yields().production

		return productionFromBuildings

	def _productionFromTradeRoutes(self, simulation):
		productionFromTradeRoutes: float = 0.0
		civilizations: WeightedCivilizationList = WeightedCivilizationList()
		tradeRoutes = self.player.tradeRoutes.tradeRoutesStartingAt(self)

		for tradeRoute in tradeRoutes:
			productionFromTradeRoutes += tradeRoute.yields(simulation).production

			if tradeRoute.isInternational(simulation):
				endCity = tradeRoute.endCity(simulation)
				endCityPlayer = endCity.player

				if endCityPlayer.isBarbarian() or endCityPlayer.isFreeCity() or endCityPlayer.isCityState():
					continue

				civilizations.addWeight(1.0, endCityPlayer.leader.civilization())

		numberOfForeignCivilizations: int = 0

		for civilization in list(CivilizationType):
			if civilizations.weight(civilization) > 0.0:
				numberOfForeignCivilizations += 1

		# Singapore suzerain bonus
		# Your cities receive +2 Production for each foreign civilization they have a Trade Route to.
		if self.player.isSuzerainOf(CityState.singapore, simulation):
			productionFromTradeRoutes += 2.0 * float(numberOfForeignCivilizations)

		return productionFromTradeRoutes

	def loyaltyState(self) -> LoyaltyState:
		return LoyaltyState.loyal

	def _foodFromTiles(self, simulation) -> float:
		hasHueyTeocalli = self.player.hasWonder(WonderType.hueyTeocalli, simulation)
		hasStBasilsCathedral = self.player.hasWonder(WonderType.stBasilsCathedral, simulation)

		foodValue: float = 0.0

		centerTile = simulation.tileAt(self.location)
		if centerTile is not None:
			foodValue += centerTile.yields(self.player, ignoreFeature=False).food

			# The yield of the tile occupied by the city center will be increased to 2 Food and 1 Production,
			# if either was previously lower (before any bonus yields are applied).
			if foodValue < 2.0:
				foodValue = 2.0

		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				adjacentTile = simulation.tileAt(point)

				if adjacentTile is not None:
					foodValue += adjacentTile.yields(self.player, ignoreFeature=False).food

					#  +2 Food, +2 Gold, and +1 Production on all Desert tiles for this city (non-Floodplains).
					if adjacentTile.terrain() == TerrainType.desert and \
						not adjacentTile.hasFeature(FeatureType.floodplains) and \
						self.wonders.hasWonder(WonderType.petra):
						foodValue += 2.0

					# +1 Food and +1 Production for each Lake tile in your empire.
					if adjacentTile.hasFeature(FeatureType.lake) and hasHueyTeocalli:
						foodValue += 1.0

					# stBasilsCathedral
					if adjacentTile.terrain() == TerrainType.tundra and hasStBasilsCathedral:
						# +1 Food, +1 Production, and +1 Culture on all Tundra tiles for this city.
						foodValue += 1.0

					# goddessOfTheHunt - +1 Food and +1 Production from Camps.
					if adjacentTile.improvement() == ImprovementType.camp and \
						self.player.religion.pantheon() == PantheonType.goddessOfTheHunt:

						foodValue += 1.0

					# waterMill - Bonus resources improved by Farms gain +1 Food each.
					if self.buildings.hasBuilding(BuildingType.waterMill) and \
						adjacentTile.improvement() == ImprovementType.farm and \
						adjacentTile.resourceFor(self.player).usage() == ResourceUsage.bonus:

						foodValue += 1.0

					# collectivism - Farms +1 Food. All cities +2 Housing. +100% Industrial Zone adjacency bonuses.
					# BUT: Great People Points earned 50% slower.
					if adjacentTile.improvement() == ImprovementType.farm and \
						self.player.government.hasCard(PolicyCardType.collectivism):

						foodValue += 1.0

		return foodValue

	def _foodFromGovernmentType(self) -> float:
		foodFromGovernmentValue: float = 0.0

		# yields from government
		if self.player.government is not None:
			# https://civilization.fandom.com/wiki/Autocracy_(Civ6)
			# +1 to all yields for each government building and Palace in a city.
			if self.player.government.currentGovernment() == GovernmentType.autocracy:
				foodFromGovernmentValue += float(self.buildings.numberOfBuildingsOf(BuildingCategoryType.government))

		return foodFromGovernmentValue

	def _foodFromBuildings(self, simulation) -> float:
		foodFromBuildings: float = 0.0

		# gather food from builds
		for building in list(BuildingType):
			if self.buildings.hasBuilding(building):
				foodFromBuildings += building.yields().food

		# handle special building rules
		if self.buildings.hasBuilding(BuildingType.waterMill):
			foodFromBuildings += self.amountOfNearbyResource(ResourceType.rice, simulation)
			foodFromBuildings += self.amountOfNearbyResource(ResourceType.wheat, simulation)

		if self.buildings.hasBuilding(BuildingType.lighthouse):
			foodFromBuildings += self.amountOfNearbyTerrain(TerrainType.shore, simulation)
			# fixme: lake feature

		return foodFromBuildings

	def _foodFromWonders(self, simulation) -> float:
		return 0.0

	def _foodFromTradeRoutes(self, simulation) -> float:
		return 0.0

	def _foodFromGovernors(self, simulation) -> float:
		return 0.0

	def amountOfNearbyResource(self, resource: ResourceType, simulation) -> float:
		resourceValue = 0.0

		for neighbor in self.location.areaWithRadius(2):
			neighborTile = simulation.tileAt(neighbor)
			if neighborTile.resourceFor(self.player) == resource:
				resourceValue += 1.0

		return resourceValue

	def amountOfNearbyTerrain(self, terrain: TerrainType, simulation) -> float:
		terrainValue = 0.0

		for neighbor in self.location.areaWithRadius(2):
			neighborTile = simulation.tileAt(neighbor)
			if neighborTile.terrain() == terrain:
				terrainValue += 1.0

		return terrainValue

	def _goldFromTiles(self, simulation):
		goldValue: float = 0.0

		centerTile = simulation.tileAt(self.location)
		if centerTile is not None:
			goldValue += centerTile.yields(self.player, ignoreFeature=False).gold

		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				adjacentTile = simulation.tileAt(point)
				goldValue += adjacentTile.yields(self.player, ignoreFeature=False).gold

				# +2 Food, +2 Gold, and +1 Production on all Desert tiles for this city(non - Floodplains).
				if adjacentTile.terrain() == TerrainType.desert and \
					not adjacentTile.hasFeature(FeatureType.floodplains) and \
					self.wonders.hasWonder(WonderType.petra):

					goldValue += 2.0

				# Reyna + forestryManagement - This city receives +2 Gold for each unimproved feature.
				if adjacentTile.hasFeature(FeatureType.forest) and not adjacentTile.hasAnyImprovement():
					if self.governor() is not None:
						if self.governor().type() == GovernorType.reyna and self.governor().hasTitle(GovernorTitle.forestryManagement):
							goldValue = 2.0

		return goldValue

	def _goldFromGovernmentType(self):
		return 0.0

	def _goldFromDistricts(self, simulation):
		return 0.0

	def _goldFromBuildings(self) -> float:
		goldFromBuildings: float = 0.0

		# gather yields from builds
		for building in list(BuildingType):
			if self.buildings.hasBuilding(building):
				goldFromBuildings += building.yields().gold

		return goldFromBuildings

	def _goldFromWonders(self):
		return 0.0

	def _goldFromTradeRoutes(self, simulation):
		return 0.0

	def _goldFromEnvoys(self, simulation):
		return 0.0

	def doTurn(self, simulation):
		if self.damage() > 0:
			# CvAssertMsg(m_iDamage <= GC.getMAX_CITY_HIT_POINTS(), "Somehow a city has more damage than hit points. Please show this to a gameplay programmer immediately.");
			hitsHealed = 20  # CITY_HIT_POINTS_HEALED_PER_TURN
			if self.isCapital():
				hitsHealed += 1

			self.addHealthPoints(hitsHealed)

		if self.damage() < 0:
			self.setDamage(0)

		# setDrafted(false);
		# setAirliftTargeted(false);
		# setCurrAirlift(0);
		self.setMadeAttackTo(False)
		# GetCityBuildings()->SetSoldBuildingThisTurn(false);

		self.updateFeatureSurrounded(simulation)

		self.cityStrategy.doTurn(simulation)

		self.cityCitizens.doTurn(simulation)

		#  AI_doTurn();
		if not self.player.isHuman():
			# AI_stealPlots();
			pass

		# elf.doResistanceTurn();

		allowNoProduction = not self.doCheckProduction(simulation)

		self.doGrowth(simulation)

		# self.doUpdateIndustrialRouteToCapital();

		self.doProduction(allowNoProduction=allowNoProduction, simulation=simulation)

		# self.doDecay();
		# self.doMeltdown();

		for loopPoint in self.location.areaWithRadius(radius=City.workRadius):
			loopPlot = simulation.tileAt(loopPoint)
			if self.cityCitizens.isWorkedAt(loopPoint):
				loopPlot.doImprovement()

		# Following function also looks at WLTKD stuff
		# self.doTestResourceDemanded();

		# Culture accumulation
		currentCulture = self.culturePerTurn(simulation)

		if self.player.religion.pantheon() == PantheonType.religiousSettlements:
			# Border expansion rate is 15% faster.
			currentCulture *= 1.15

		if currentCulture > 0:
			self.updateCultureStoredTo(self.cultureStored() + currentCulture)

		# Enough Culture to acquire a new Plot?
		if self.cultureStored() >= self.cultureThreshold():
			self.cultureLevelIncrease(simulation)

		# Resource Demanded Counter
		# if (GetResourceDemandedCountdown() > 0) {
		#   ChangeResourceDemandedCountdown(-1)
		#
		#   if (GetResourceDemandedCountdown() == 0) {
		#     # Pick a Resource to demand
		#     self.doPickResourceDemanded();

		self.updateStrengthValue(simulation)
		self.updateLoyaltyValue(simulation)

		self.doNearbyEnemy(simulation)

		# Check for Achievements
		#         /*if(isHuman() && !GC.getGame().isGameMultiPlayer() && GET_PLAYER(GC.getGame().getActivePlayer()).isLocalPlayer()) {
		#             if(getJONSCulturePerTurn()>=100) {
		#                 gDLL->UnlockAchievement( ACHIEVEMENT_CITY_100CULTURE );
		#             }
		#             if(getYieldRate(YIELD_GOLD)>=100) {
		#                 gDLL->UnlockAchievement( ACHIEVEMENT_CITY_100GOLD );
		#             }
		#             if(getYieldRate(YIELD_SCIENCE)>=100 ) {
		#                 gDLL->UnlockAchievement( ACHIEVEMENT_CITY_100SCIENCE );
		#             }
		#         }*/

		# sending notifications on when routes are connected to the capital
		if not self.isCapital():
			#
			#             /*CvNotifications* pNotifications = GET_PLAYER(m_eOwner).GetNotifications();
			#             if (pNotifications)
			#             {
			#                 CvCity* pPlayerCapital = GET_PLAYER(m_eOwner).getCapitalCity();
			#                 CvAssertMsg(pPlayerCapital, "No capital city?");
			#
			#                 if (m_bRouteToCapitalConnectedLastTurn != m_bRouteToCapitalConnectedThisTurn && pPlayerCapital)
			#                 {
			#                     Localization::String strMessage;
			#                     Localization::String strSummary;
			#
			#                     if (m_bRouteToCapitalConnectedThisTurn) // connected this turn
			#                     {
			#                         strMessage = Localization::Lookup( "TXT_KEY_NOTIFICATION_TRADE_ROUTE_ESTABLISHED" );
			#                         strSummary = Localization::Lookup("TXT_KEY_NOTIFICATION_SUMMARY_TRADE_ROUTE_ESTABLISHED");
			#                     }
			#                     else // lost connection this turn
			#                     {
			#                         strMessage = Localization::Lookup( "TXT_KEY_NOTIFICATION_TRADE_ROUTE_BROKEN" );
			#                         strSummary = Localization::Lookup("TXT_KEY_NOTIFICATION_SUMMARY_TRADE_ROUTE_BROKEN");
			#                     }
			#
			#                     strMessage << getNameKey();
			#                     strMessage << pPlayerCapital->getNameKey();
			#                     pNotifications->Add( NOTIFICATION_GENERIC, strMessage.toUTF8(), strSummary.toUTF8(), -1, -1, -1 );
			#                 }
			#             }*/
			self._routeToCapitalConnectedLastTurn = self._routeToCapitalConnectedThisTurn

	def isCapital(self) -> bool:
		return self.capitalValue

	def hasOnlySmallFoodSurplus(self) -> bool:
		return False

	def damage(self) -> int:
		return 0

	def setDamage(self, damage: int):
		pass

	def setMadeAttackTo(self, madeAttack):
		pass

	def updateFeatureSurrounded(self, simulation):
		pass

	def doCheckProduction(self, simulation):
		pass

	def doGrowth(self, simulation):
		# update housing value
		self.buildings.updateHousing()
		self.districts.updateHousing()

		foodPerTurn = self.foodPerTurn(simulation)
		self.setLastTurnFoodHarvested(foodPerTurn)
		foodEatenPerTurn = self.foodConsumption()
		foodDiff = foodPerTurn - foodEatenPerTurn

		if foodDiff < 0:
			# notify human about starvation
			if self.player.isHuman():
				# @fixme self.player.notifications()?.add(notification: .starving(cityName: self.name, location: self.location))
				pass

		# modifier
		modifier = self.housingGrowthModifier(simulation) * self._amenitiesGrowthModifier(simulation)
		modifier += self.wonderGrowthModifier(simulation)
		modifier += self.religionGrowthModifier()
		modifier += self.governmentGrowthModifier()

		foodDiff *= modifier

		self.setLastTurnFoodEarned(foodDiff)
		self.setFoodBasket(self.foodBasket() + foodDiff)

		if self.foodBasket() >= self.growthThreshold():

			if self.cityCitizens.isForcedAvoidGrowth():
				# don't grow a city, if we are at avoid growth
				self.setFoodBasket(self.growthThreshold())
			else:
				self.setFoodBasket(0)
				self.setPopulation(self.population() + 1, reassignCitizen=True, simulation=simulation)

				simulation.userInterface.updateCity(city=self)

				# Only show notification if the city is small
				if self._populationValue <= 5:

					if self.player.isHuman():
						# @fixme self.player.notifications()?.add(notification:.cityGrowth(cityName: self.name, population: self.population(), location: self.location)
						pass

				# check for improving city tutorial
				# if simulation.tutorialInfos() == TutorialType.improvingCity and self.player.isHuman():
				# 	if int(self._populationValue) >= Tutorials.ImprovingCityTutorial.citizenInCityNeeded and
				# 		buildings.has(building: .granary) and buildings.has(building:.monument):
				#
				# 		gameModel.userInterface?.finish(tutorial:.improvingCity)
				# 		gameModel.enable(tutorial:.none)

				# moments
				# if self._populationValue > 10:
				# 	if not self.player.hasMoment(of:.firstBustlingCity(cityName: self.name)) and
				# 		not player.hasMoment(of:.worldsFirstBustlingCity(cityName: self.name)):
				#
				#         # check if someone else already had a bustling city
				# 		if gameModel.anyHasMoment(of: .worldsFirstBustlingCity(cityName: self.name)):
				# 			player.addMoment(of:.firstBustlingCity(cityName: self.name), in: gameModel)
				# 		else:
				# 			player.addMoment(of:.worldsFirstBustlingCity(cityName: self.name), in: gameModel)

				# if self._populationValue > 15:
				# 	if not player.hasMoment(of: .firstLargeCity(cityName: self.name)) and
				# 		not player.hasMoment(of:.worldsFirstLargeCity(cityName: self.name)):
				#
				#         #  check if someone else already had a bustling city
				# 		if gameModel.anyHasMoment(of: .worldsFirstLargeCity(cityName: self.name)):
				# 			player.addMoment(of:.firstLargeCity(cityName: self.name), in: gameModel)
				# 		else:
				# 			player.addMoment(of:.worldsFirstLargeCity(cityName: self.name), in: gameModel)

				# if self.populationValue > 20:
				# 	if not self.player.hasMoment(of: .firstEnormousCity(cityName: self.name)) and
				# 		not self.player.hasMoment(of:.worldsFirstEnormousCity(cityName: self.name)):
				#
				#         # check if someone else already had a bustling city
				# 		if simulation.anyHasMoment(of: .worldsFirstEnormousCity(cityName: self.name)) {
				# 			player.addMoment(of:.firstEnormousCity(cityName: self.name), in: gameModel)
				# 		else:
				# 			player.addMoment(of:.worldsFirstEnormousCity(cityName: self.name), in: gameModel)

				# if self._populationValue > 25:
				# 	if not self.player.hasMoment(of: .firstGiganticCity(cityName: self.name)) and
				# 		not player.hasMoment(of:.worldsFirstGiganticCity(cityName: self.name)):
				#
				#         # check if someone else already had a bustling city
				# 		if gameModel.anyHasMoment(of: .worldsFirstGiganticCity(cityName: self.name)):
				# 			player.addMoment(of:.firstGiganticCity(cityName: self.name), in: gameModel)
				# 		else:
				# 			player.addMoment(of:.worldsFirstGiganticCity(cityName: self.name), in: gameModel)

		elif self.foodBasket() < 0:
			self.setFoodBasket(0)

			if self.population() > 1:
				self.setPopulation(self.population() - 1, simulation=simulation)

	def doProduction(self, allowNoProduction, simulation):
		pass

	def culturePerTurn(self, simulation) -> float:
		return 0.0

	def cultureStored(self) -> float:
		return 0.0

	def cultureThreshold(self) -> float:
		return 1000.0

	def updateStrengthValue(self, simulation):
		pass

	def updateLoyaltyValue(self, simulation):
		pass

	def doNearbyEnemy(self, simulation):
		pass

	def foodBasket(self) -> float:
		return self._foodBasketValue

	def setFoodBasket(self, value):
		self._foodBasketValue = value

	def setLastTurnFoodEarned(self, foodDiff):
		pass

	def setLastTurnFoodHarvested(self, foodPerTurn):
		pass

	def growthThreshold(self) -> float:
		# https://forums.civfanatics.com/threads/formula-thread.600534/
		# https://forums.civfanatics.com/threads/mathematical-model-comparison.634332/
		#  Population growth (food)
		# 15+8*n+n^1.5 (n is current population-1)
		# 15+8*(N-1)+(N-1)^1.5
		# 1=>2 =>> 15+0+0^1.5=15
		# 2=>3 =>> 15+8+1^1.5=24
		# 3=>4 =>> 15+16+2^1.5=34
		tmpPopulationValue = max(1, self._populationValue)

		growthThreshold = 15.0  # BASE_CITY_GROWTH_THRESHOLD
		growthThreshold += (float(tmpPopulationValue) - 1.0) * 8.0  # CITY_GROWTH_MULTIPLIER
		growthThreshold += pow(tmpPopulationValue - 1.0, 1.5)  # CITY_GROWTH_EXPONENT

		return growthThreshold

	def foodConsumption(self) -> float:
		"""Each Citizen6 Citizen living in a city consumes 2 Food per turn, which forms the city's total food
		consumption."""
		return float(self.population()) * 2.0

	def housingGrowthModifier(self, simulation) -> float:
		# https://civilization.fandom.com/wiki/Housing_(Civ6)
		housing = self.housingPerTurn(simulation)
		housingDiff = int(housing) - int(self._populationValue)

		if housingDiff >= 2:  # 2 or more    100 %
			return 1.0
		elif housingDiff == 1:  # 1    50 %
			return 0.5
		elif 0 <= housingDiff <= -4:  # 0 to -4    25 %
			return 0.25
		else:  # -5 or less 0 %
			return 0.0

	def housingPerTurn(self, simulation):
		housingPerTurn: YieldValues = YieldValues(value=0.0, percentage=1.0)

		housingPerTurn += YieldValues(value=self._baseHousing(simulation))
		housingPerTurn += YieldValues(value=self._housingFromBuildings())
		housingPerTurn += YieldValues(value=self._housingFromDistricts(simulation))
		housingPerTurn += YieldValues(value=self._housingFromWonders(simulation))
		housingPerTurn += YieldValues(value=self._housingFromImprovements(simulation))
		housingPerTurn += YieldValues(value=self._housingFromGovernment())
		housingPerTurn += YieldValues(value=self._housingFromGovernors())

		# cap yields based on loyalty
		housingPerTurn += YieldValues(value=0.0, percentage=self.loyaltyState().yieldPercentage())

		return housingPerTurn.calc()

	def _baseHousing(self, simulation):
		tile = simulation.tileAt(self.location)

		for neighbor in self.location.neighbors():
			neighborTile = simulation.tileAt(neighbor)
			if tile.isRiverToCrossTowards(neighborTile):
				return 5

		if simulation.isCoastalAt(self.location):
			return 3

		return 2

	def _housingFromBuildings(self) -> float:
		housingFromBuildings: float = 0.0

		housingFromBuildings += self.buildings.housing()

		# audienceChamber - +2 Amenities and +4 Housing in Cities with Governors.
		if self.buildings.hasBuilding(BuildingType.audienceChamber) and self.governor() is not None:
			housingFromBuildings += 4

		return housingFromBuildings

	def _housingFromDistricts(self, simulation) -> float:
		housingFromDistricts: float = 0.0

		# aqueduct district
		if self.hasDistrict(DistrictType.aqueduct):
			hasFreshWater: bool = False
			tile = simulation.tileAt(self.location)
			for neighbor in self.location.neighbors():
				neighborTile = simulation.tileAt(neighbor)
				if tile.isRiverToCrossTowards(neighborTile):
					hasFreshWater = True

			# Cities that do not yet have existing fresh water receive up to 6 Housing.
			if not hasFreshWater:
				housingFromDistricts += 6
			else:
				# Cities that already have existing fresh water will instead get 2 Housing.
				housingFromDistricts += 2

		#for now there can only be one
		if self.hasDistrict(DistrictType.neighborhood):
			# A district in your city that provides Housing based on the Appeal of the tile.
			neighborhoodLocation = self.locationOf(DistrictType.neighborhood)
			neighborhoodTile = simulation.tileAt(neighborhoodLocation)
			appeal = neighborhoodTile.appealLevel(simulation)
			housingFromDistricts += float(appeal.housing())

		if self.hasDistrict(DistrictType.preserve):
			# Grants up to 3 Housing based on tile's Appeal
			tile = simulation.tileAt(self.location)
			appealLevel = tile.appealLevel(simulation)
			housingFromDistricts += float(appealLevel.housing()) / 2.0

		if self.hasDistrict(DistrictType.holySite):
			# riverGoddess - +2 Amenities and +2 Housing to cities if they have a Holy Site district adjacent to a River.
			holySiteLocation = self.locationOf(DistrictType.holySite)
			isHolySiteAdjacentToRiver = False

			for neighbor in holySiteLocation.neighbors():
				if simulation.riverAt(neighbor):
					isHolySiteAdjacentToRiver = True
					break

			if isHolySiteAdjacentToRiver:
				housingFromDistricts += 2.0

		# medinaQuarter - +2 Housing in all cities with at least 3 specialty Districts.
		if self.player.government.hasCard(PolicyCardType.medinaQuarter):
			if self.districts.numberOfSpecialtyDistricts() >= 3:
				housingFromDistricts += 2.0

		return housingFromDistricts

	def _housingFromWonders(self, simulation) -> float:
		housingFromWonders: float = 0.0

		# city has templeOfArtemis: +3 Housing
		if self.hasWonder(WonderType.templeOfArtemis):
			housingFromWonders += 3.0

		# city has hangingGardens: +2 Housing
		if self.hasWonder(WonderType.hangingGardens):
			housingFromWonders += 2.0

		# player has angkorWat: +1 Housing in all cities.
		if self.player.hasWonder(WonderType.angkorWat, simulation):
			housingFromWonders += 2.0

		return housingFromWonders

	def _housingFromImprovements(self, simulation) -> float:
		# Each Farm, Pasture, Plantation, or Camp supports a small amount of Population — 1 Housing for every 2
		# such improvements.
		farms: int = 0
		pastures: int = 0
		plantations: int = 0
		camps: int = 0

		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				adjacentTile = simulation.tileAt(point)

				# farms
				if adjacentTile.hasImprovement(ImprovementType.farm):
					farms += 1

				# pastures
				if adjacentTile.hasImprovement(ImprovementType.pasture):
					pastures += 1

				# plantations
				if adjacentTile.hasImprovement(ImprovementType.plantation):
					plantations += 1

				# camps
				if adjacentTile.hasImprovement(ImprovementType.camp):
					camps += 1

		housingValue: float = 0.0

		housingValue += float((farms / 2))
		housingValue += float((pastures / 2))
		housingValue += float((plantations / 2))
		housingValue += float((camps / 2))

		return housingValue

	def _housingFromGovernment(self) -> float:
		housingFromGovernment: float = 0.0

		# All cities with a district receive +1 Housing and +1 Amenity.
		if self.player.government.currentGovernment() == GovernmentType.classicalRepublic:
			if self.districts.hasAny():
				housingFromGovernment += 1.0

		# ..and +1 Housing per District.
		if self.player.government.currentGovernment() == GovernmentType.democracy:
			housingFromGovernment += float(self.districts.numberOfBuiltDistricts())

		# +1 Housing in all cities with at least 2 specialty districts.
		if self.player.government.hasCard(PolicyCardType.insulae):
			if self.districts.numberOfBuiltDistricts() >= 2:
				housingFromGovernment += 1.0

		# medievalWalls: +2 Housing under the Monarchy Government.
		if self.player.government.currentGovernment() == GovernmentType.monarchy:
			if self.buildings.hasBuilding(BuildingType.medievalWalls):
				housingFromGovernment += 2.0

		# newDeal - +4 Housing and +2 Amenities to all cities with at least 3 specialty districts.
		if self.player.government.hasCard(PolicyCardType.newDeal):
			if self.districts.numberOfBuiltDistricts() >= 3:
				housingFromGovernment += 4.0

		# collectivism - Farms + 1 Food.
		# All cities + 2 Housing. +100 % Industrial Zone adjacency bonuses.
		# BUT: Great People Points earned 50 % slower.
		if self.player.government.hasCard(PolicyCardType.collectivism):
			housingFromGovernment += 2.0

		return housingFromGovernment

	def _housingFromGovernors(self) -> float:
		housingValue: float = 0.0

		# Established Governors with at least 2 Promotions provide +1 Amenity and +2 Housing.
		if self.player.government.hasCard(PolicyCardType.civilPrestige) and self.numberOfGovernorTitles() >= 2:
			housingValue += 2.0

		if self.governor() is not None:
			# Liang - waterWorks - +2 Housing for every Neighborhood and Aqueduct district in this city.
			if self.governor().type == GovernorType.liang and self.governor().hasTitle(GovernorTitle.waterWorks):
				numberOfNeighborhoods = 1.0 if self.hasDistrict(DistrictType.neighborhood) else 0.0
				numberOfAqueducts = 1.0 if self.hasDistrict(DistrictType.aqueduct) else 0.0
				housingValue += 2.0 * (numberOfNeighborhoods + numberOfAqueducts)

		# civilPrestige - Established Governors with at least 2 Promotions provide +1 Amenity and +2 Housing.
		if self.player.government.hasCard(PolicyCardType.civilPrestige) and self.governor().titleCount() >= 2:
			housingValue += 2.0

		return housingValue

	def hasDistrict(self, district: DistrictType) -> bool:
		if district == DistrictType.cityCenter:
			return True

		return self.districts.hasDistrict(district)

	def hasWonder(self, wonder: WonderType) -> bool:
		return self.wonders.hasWonder(wonder)

	def amenitiesNeeded(self) -> float:
		# first two people don't need amenities
		return max(0.0, float(self._populationValue) - 2.0) + float(self.amenitiesForWarWearinessValue)

	def amenitiesState(self, simulation) -> AmenitiesState:
		amenities = self.amenitiesPerTurn(simulation)
		amenitiesDiff = amenities - self.amenitiesNeeded()

		if amenitiesDiff >= 3.0:
			return AmenitiesState.ecstatic
		elif amenitiesDiff == 1.0 or amenitiesDiff == 2.0:
			return AmenitiesState.happy
		elif amenitiesDiff == 0.0:
			return AmenitiesState.content
		elif amenitiesDiff == -1.0 or amenitiesDiff == -2.0:
			return AmenitiesState.displeased
		elif amenitiesDiff == -3.0 or amenitiesDiff == -4.0:
			return AmenitiesState.unhappy
		elif amenitiesDiff == -5.0 or amenitiesDiff == -6.0:
			return AmenitiesState.unrest
		else:
			return AmenitiesState.revolt

	def _amenitiesGrowthModifier(self, simulation):
		# https://civilization.fandom.com/wiki/Amenities_(Civ6)
		amenitiesStateValue = self.amenitiesState(simulation)

		if amenitiesStateValue == AmenitiesState.ecstatic:
			return 1.2
		elif amenitiesStateValue == AmenitiesState.happy:
			return 1.1
		elif amenitiesStateValue == AmenitiesState.content:
			return 1.0
		elif amenitiesStateValue == AmenitiesState.displeased:
			return 0.85
		elif amenitiesStateValue == AmenitiesState.unhappy:
			return 0.70
		elif amenitiesStateValue == AmenitiesState.unrest:
			return 0.0
		elif amenitiesStateValue == AmenitiesState.revolt:
			return 0.0

		raise Exception(f'Unhandled AmenitiesState: {amenitiesStateValue}')

	def amenitiesPerTurn(self, simulation):
		amenitiesPerTurn: float = 0.0

		amenitiesPerTurn += self._amenitiesFromTiles(simulation)
		amenitiesPerTurn += self._amenitiesFromLuxuries()
		amenitiesPerTurn += self._amenitiesFromDistrict(simulation)
		amenitiesPerTurn += self._amenitiesFromBuildings()
		amenitiesPerTurn += self._amenitiesFromWonders(simulation)
		amenitiesPerTurn += self._amenitiesFromCivics(simulation)

		return amenitiesPerTurn

	def _amenitiesFromTiles(self, simulation):
		amenitiesFromTiles: float = 0.0

		hueyTeocalliLocation: HexPoint = HexPoint(-1, -1)
		if self.player.hasWonder(WonderType.hueyTeocalli, simulation):
			for point in self.cityCitizens.workingTileLocations():
				if self.cityCitizens.isWorkedAt(point):
					adjacentTile = simulation.tileAt(point)
					if adjacentTile.hasWonder(WonderType.hueyTeocalli):
						hueyTeocalliLocation = point

		# +1 Amenity from entertainment for each Lake tile within one tile of Huey Teocalli.
		# (This includes the Lake tile where the wonder is placed.)
		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				if point == hueyTeocalliLocation or point.isNeighborOf(hueyTeocalliLocation):
					amenitiesFromTiles += 1

		return amenitiesFromTiles

	def _amenitiesFromLuxuries(self):
		return float(len(self._luxuries))

	def _amenitiesFromDistrict(self, simulation):
		amenitiesFromDistrict: float = 0.0

		# "All cities with a district receive +1 Housing and +1 Amenity."
		if self.player.government.currentGovernment() == GovernmentType.classicalRepublic:
			if self.districts.hasAny():
				amenitiesFromDistrict += 1.0

		if self.hasDistrict(DistrictType.holySite):
			# riverGoddess - +2 Amenities and +2 Housing to cities if they have a Holy Site district adjacent to a River.
			holySiteLocation = self.locationOf(DistrictType.holySite)
			isHolySiteAdjacentToRiver = False

			for neighbor in holySiteLocation.neighbors():
				if simulation.riverAt(neighbor):
					isHolySiteAdjacentToRiver = True
					break

			if isHolySiteAdjacentToRiver:
				amenitiesFromDistrict += 2.0

		return amenitiesFromDistrict

	def _amenitiesFromBuildings(self):
		amenitiesFromBuildings: float = 0.0

		# gather amenities from buildings
		for building in list(BuildingType):
			if self.buildings.hasBuilding(building):
				amenitiesFromBuildings += float(building.amenities())

		# audienceChamber - +2 Amenities and +4 Housing in Cities with Governors.
		if self.buildings.hasBuilding(BuildingType.audienceChamber) and self.governor() is not None:
			amenitiesFromBuildings += 2

		return amenitiesFromBuildings

	def _amenitiesFromWonders(self, simulation):
		locationOfColosseum: HexPoint = HexPoint(-1, -1)

		for cityRef in simulation.citiesOf(self.player):
			if cityRef.hasWonder(WonderType.colosseum):
				# this is a hack
				locationOfColosseum = cityRef.location

		amenitiesFromWonders: float = 0.0

	    # gather amenities from buildingss
		for wonder in list(WonderType):
			if self.hasWonder(wonder):
				amenitiesFromWonders += float(wonder.amenities())

		# temple of artemis
		if self.hasWonder(WonderType.templeOfArtemis):
			for loopPoint in self.location.areaWithRadius(radius=3):
				loopTile = simulation.tileAt(loopPoint)
				if loopTile.hasImprovement(ImprovementType.camp) or \
					loopTile.hasImprovement(ImprovementType.pasture) or \
					loopTile.hasImprovement(ImprovementType.plantation):

					# Each Camp, Pasture, and Plantation improvement within 4 tiles of this wonder provides +1 Amenity.
					amenitiesFromWonders += 1.0

		# colosseum - +2 Culture, +2 Loyalty, +2 Amenities from entertainment
		# to each City Center within 6 tiles.
		if self.hasWonder(WonderType.colosseum) or locationOfColosseum.distance(self.location) <= 6:
			amenitiesFromWonders += 2.0

		return amenitiesFromWonders

	def _amenitiesFromCivics(self, simulation) -> float:
		amenitiesFromCivics: float = 0.0

		# Retainers - +1 Amenity in cities with a garrisoned unit.
		if self.player.government.hasCard(PolicyCardType.retainers):
			if self._garrisonedUnitValue is not None:
				amenitiesFromCivics += 1

		# Civil Prestige - +1 Amenity and +2 Housing in cities with established Governors with 2+ promotions.
		if self.player.government.hasCard(PolicyCardType.retainers):
			if self.governor() is not None:
				if self.governor().titlesCount() >= 2:
					amenitiesFromCivics += 1

		# Liberalism - +1 Amenity in cities with 2 + specialty districts.
		if self.player.government.hasCard(PolicyCardType.liberalism):
			if self.districts.numberOfBuiltDistricts() >= 2:
				amenitiesFromCivics += 1

		# Police State - -2 Spy operation level in your lands. - 1 Amenity in all cities.
		if self.player.government.hasCard(PolicyCardType.policeState):
			amenitiesFromCivics -= 1

		# New Deal - +2 Amenities and +4 Housing in all cities with 3 + specialty districts.
		if self.player.government.hasCard(PolicyCardType.newDeal):
			if self.districts.numberOfBuiltDistricts() >= 3:
				amenitiesFromCivics += 2

		# civilPrestige - Established Governors with at least 2 Promotions provide +1 Amenity and +2 Housing.
		if self.player.government.hasCard(PolicyCardType.civilPrestige):
			if self.governor() is not None:
				if self.governor().titlesCount() >= 2:
					amenitiesFromCivics += 1.0

		# Sports Media + 100 % Theater Square adjacency bonuses, and Stadiums generate + 1 Amenity.
		# Music Censorship Other civs  Rock Bands cannot enter your territory. -1 Amenities Amenity in all cities.

		# robberBarons - +50 % Gold in cities with a Stock Exchange. +25% Production in cities with a Factory.
		# BUT: -2 Amenities in all cities.
		if self.player.government.hasCard(PolicyCardType.robberBarons):
			amenitiesFromCivics -= 2

		# - Automated Workforce +20% Production towards city projects.
		# BUT: -1 Amenities and -5 Loyalty in all cities.
		if self.player.government.hasCard(PolicyCardType.automatedWorkforce):
			amenitiesFromCivics -= 1

		return amenitiesFromCivics

	def wonderGrowthModifier(self, simulation) -> float:
		wonderModifier: float = 0.0

		# hangingGardens - Increases growth by 15 % in all cities.
		if self.player.hasWonder(WonderType.hangingGardens, simulation):
			wonderModifier += 0.15

		return wonderModifier

	def religionGrowthModifier(self) -> float:
		religionModifier: float = 0.0

		# fertilityRites - City growth rate is 10 % higher.
		if self.player.religion.pantheon() == PantheonType.fertilityRites:
			religionModifier += 0.10

		return religionModifier

	def governmentGrowthModifier(self) -> float:
		governmentModifier: float = 0.0

		# colonialOffices - +15 % faster growth and 3 Loyalty per turn
		# for cities not on your original Capital's continent.
		if self.player.government.hasCard(PolicyCardType.colonialOffices):
			# @fixme not continent check
			governmentModifier += 0.15

		return governmentModifier
	