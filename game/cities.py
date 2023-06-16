import random
import sys
from typing import Optional

from game.ai.cities import CityStrategyAI, CitySpecializationType, BuildableItem, BuildableType
from game.ai.economicStrategies import EconomicStrategyType
from game.ai.grandStrategies import GrandStrategyAIType
from game.amenities import AmenitiesState
from game.buildings import BuildingType, BuildingCategoryType
from game.cityStates import CityStateType, CityStateCategory
from game.civilizations import LeaderWeightList, CivilizationAbility, LeaderAbility, LeaderType, \
	WeightedCivilizationList, CivilizationType
from game.districts import DistrictType
from game.envoys import EnvoyEffectLevel
from game.governments import GovernmentType
from game.governors import GovernorType, GovernorTitle, Governor
from game.greatPersons import GreatPersonType
from game.greatworks import GreatWorkSlotType
from game.loyalties import LoyaltyState
from game.moments import MomentType
from game.notifications import NotificationType
from game.policyCards import PolicyCardType
from game.projects import ProjectType
from game.religions import PantheonType
from game.specialists import SpecialistType
from game.states.ages import AgeType
from game.states.dedications import DedicationType
from game.states.gossips import GossipType
from game.types import EraType, TechType, CivicType
from game.unitTypes import UnitType, UnitClassType
from game.units import Unit
from game.wonders import WonderType
from map import constants
from map.base import HexPoint
from map.improvements import ImprovementType
from map.types import YieldList, FeatureType, TerrainType, ResourceUsage, ResourceType, YieldType, Yields, RouteType, \
	UnitDomainType, Tutorials
from core.base import ExtendedEnum, WeightedBaseList


class CityDistrictItem:
	def __init__(self, district: DistrictType, location: HexPoint):
		self.district = district
		self.location = location


class CityDistricts:
	def __init__(self, city):
		self.city = city
		self._items: [CityDistrictItem] = []
		self._housingVal = 0.0

	def build(self, district: DistrictType, location: HexPoint):
		newItem = CityDistrictItem(district=district, location=location)

		if len(list(filter(lambda item: item.district == district and item.location == location, self._items))) > 0:
			raise Exception(f'District {district} already built at {location}')

		self._items.append(newItem)

	def hasAny(self) -> bool:
		# cityCenter does not count
		return len(list(filter(lambda item: item.district != DistrictType.cityCenter, self._items))) > 0

	def hasAnySpecialtyDistrict(self) -> bool:
		return len(list(filter(lambda item: item.district.isSpecialty(), self._items))) > 0

	def hasDistrict(self, district: DistrictType) -> bool:
		return len(list(filter(lambda item: item.district == district, self._items))) > 0

	def housing(self) -> float:
		return self._housingVal

	def updateHousing(self):
		housingVal = 0.0
		for district in list(DistrictType):
			if self.hasDistrict(district):
				housingVal += district.yields().housing

		self._housingVal = housingVal
		return

	def numberOfSpecialtyDistricts(self) -> int:
		return sum(map(lambda item: 1 if item.district.isSpecialty() else 0, self._items))

	def locationOfDistrict(self, district: DistrictType) -> Optional[HexPoint]:
		districtItem = next(filter(lambda item: item.district == district, self._items), None)

		if districtItem is not None:
			return districtItem.location

		return None

	def domesticTradeYields(self) -> Yields:

		yields = Yields(food=0.0, production=0.0, gold=0.0)

		for district in list(DistrictType):
			if self.hasDistrict(district):
				yields += district.domesticTradeYields()

		return yields

	def foreignTradeYields(self) -> Yields:

		yields = Yields(food=0.0, production=0.0, gold=0.0)

		for district in list(DistrictType):
			if self.hasDistrict(district):
				yields += district.foreignTradeYields()

		return yields


class CityBuildings:
	def __init__(self, city):
		self.city = city
		self._buildings = []

		self._defenseValue = 0
		self._housingValue = 0.0

	def build(self, building: BuildingType):
		if building in self._buildings:
			raise Exception(f'Error: {building} already build in {self.city.name}')

		self._buildings.append(building)

		self._updateDefense()
		self.updateHousing()

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

	def __repr__(self):
		return f'WorkingPlot({self.location}, {self.worked} / {self.workedForced})'


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


class SpecialistCountList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for specialist in list(SpecialistType):
			self.setWeight(0.0, specialist)

	def increaseNumberOf(self, specialistType: SpecialistType):
		self.addWeight(1, specialistType)


class GreatPersonProgressList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for greatPerson in list(GreatPersonType):
			self.setWeight(0.0, greatPerson)


class SpecialistBuilding:
	def __init__(self, building: BuildingType, amount: int):
		self.building = building
		self.amount = amount


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
		self._noAutoAssignSpecialistsValue = False

		self.numberOfSpecialists = SpecialistCountList()
		self.numberOfSpecialistsInBuilding = []
		self.numberOfForcedSpecialistsInBuilding = []

		#
		self.specialistGreatPersonProgress = GreatPersonProgressList()
		self.numberOfForcedSpecialistsValue = 0
		self.numberOfDefaultSpecialistsValue = 0

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
		if not sum <= self.city.population():
			raise Exception("Gameplay: More workers than population in the city.")

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

	def canWorkAt(self, location: HexPoint, simulation) -> bool:
		"""Can our City work a particular CvPlot?"""
		tile = simulation.tileAt(location)

		if tile.workingCity() is not None and tile.workingCity().location != self.city.location:
			return False

		yields = tile.yields(self.city.player, ignoreFeature=False)
		if yields.food <= 0 and yields.production <= 0 and yields.gold <= 0 and yields.science <= 0 and yields.culture <= 0:
			return False

		if self.isBlockaded(tile, simulation):
			return False

		return True

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

	def forceWorkingPlotAt(self, location: HexPoint, force: bool, simulation):
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
		"""Is our City working a CvPlot?"""
		# city center is always worked
		if location == self.city.location:
			return True

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
		"""How many Citizens are working Plots?"""
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
			self.doRemoveWorstCitizen(removeForcedStatus=False, dontChangeSpecialist=SpecialistType.none,
			                          simulation=simulation)

		# Remove Non-Forced Specialists in Buildings
		for buildingType in list(BuildingType):
			# Have this Building in the City?
			if self.city.buildings.hasBuilding(building=buildingType):
				# Don't include Forced guys
				numSpecialistsToRemove = self.numberOfSpecialistsIn(buildingType) - self.numberOfForcedSpecialistsIn(
					buildingType)
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
		yields = tile.yields(self.city.player, ignoreFeature=False)

		# Yield Values
		foodYieldValue = 12 * yields.value(YieldType.food)
		productionYieldValue = 8 * yields.value(YieldType.production)
		goldYieldValue = 10 * yields.value(YieldType.gold)
		scienceYieldValue = 6 * yields.value(YieldType.science)
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

	def doVerifyWorkingPlots(self, simulation):
		"""Check all Plots by this City to see if we can actually be working them (if we are)"""
		for workingPlot in self._workingPlots:
			self.doVerifyWorkingPlot(workingPlot, simulation)

		return

	def doVerifyWorkingPlot(self, workingPlot, simulation):
		"""If we're working this plot make sure we're allowed, and if we're not then correct the situation"""
		if workingPlot is None:
			return

		if workingPlot.worked:
			if not self.canWorkAt(workingPlot.location, simulation):
				self.setWorkedAt(workingPlot.location, worked=False)
				self.doAddBestCitizenFromUnassigned(simulation)

		return

	def setNoAutoAssignSpecialists(self, param, simulation):
		pass

	def totalSpecialistCount(self) -> int:
		return 0

	def doRemoveWorstCitizen(self,
	                         removeForcedStatus: bool = False,
	                         dontChangeSpecialist: SpecialistType = SpecialistType.none,
	                         simulation=None) -> bool:
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
		return self.numberOfDefaultSpecialistsValue

	def doRemoveWorstSpecialist(self, dontChangeSpecialist: SpecialistType = SpecialistType.none,
	                            dontRemoveFromBuilding: BuildingType = BuildingType.none, simulation=None) -> bool:
		"""Find the worst Specialist and remove him from duty"""
		if simulation is None:
			raise Exception('simulation must not be None')

		for buildingType in list(BuildingType):
			if buildingType == dontRemoveFromBuilding:
				continue

			# We might not be allowed to change this Building's Specialists
			if dontChangeSpecialist == buildingType.specialistType():
				continue

			if self.numberOfSpecialistsIn(buildingType) > 0:
				self.doRemoveSpecialistFrom(buildingType, forced=True, simulation=simulation)
				return True

		return False

	def numberOfForcedDefaultSpecialists(self) -> int:
		return self.numberOfForcedSpecialistsValue

	def changeNumberOfDefaultSpecialistsBy(self, delta: int):
		"""Changes how many Default Specialists are assigned in this City"""
		self.numberOfDefaultSpecialistsValue += delta

		specialistType: SpecialistType = SpecialistType.citizen
		self.numberOfSpecialists.addWeight(delta, specialistType)
		self.city.processSpecialist(specialistType, delta)

		self.changeNumberOfUnassignedCitizensBy(-delta)

	def changeNumberOfForcedDefaultSpecialists(self, delta: int):
		"""How many Default Specialists have been forced assigned in this City?"""
		self.numberOfDefaultSpecialistsValue += delta

	def bestCityPlotWithValue(self, wantBest: bool, wantWorked: bool, simulation) -> (Optional[HexPoint], int):
		"""Find a Plot the City is either working or not, and the best/worst value for it - this function does
		"double duty" depending on what the user wants to find"""
		bestPlotValue: int = -1
		bestPlotID: [HexPoint] = None

		# Look at all workable Plots
		for workableTile in self.workableTiles(simulation):
			# skip home plot
			if workableTile.point == self.city.location:
				continue

			# Is this a Plot this City controls?
			if not self.city.player.isEqualTo(workableTile.owner()):
				continue

			# Working the Plot and wanting to work it, or Not working it and wanting to find one to work?
			if (self.isWorkedAt(workableTile.point) and wantWorked) or (
				not self.isWorkedAt(workableTile.point) and not wantWorked):

				# Working the Plot or CAN work the Plot?
				if wantWorked or self.canWorkAt(workableTile.point, simulation):

					value = self.plotValueOf(workableTile.point, useAllowGrowthFlag=wantBest, simulation=simulation)
					slotForceWorked = self.isForcedWorkedAt(workableTile.point)

					if slotForceWorked:
						# Looking for best, unworked Plot: Forced plots are FIRST to be picked
						if wantBest and not wantWorked:
							value += 10000

						# Looking for worst, worked Plot: Forced plots are LAST to be picked, so make it's value incredibly high
						if not wantBest and wantWorked:
							value += 10000

					# First Plot? or Best Plot so far? or Worst Plot so far?
					if bestPlotValue == -1 or (wantBest and value > bestPlotValue) or (
						not wantBest and value < bestPlotValue):
						bestPlotValue = value
						bestPlotID = workableTile.point

		return bestPlotID, bestPlotValue

	def numberOfSpecialistsIn(self, buildingType: BuildingType) -> int:
		specialistsEntry = next(
			filter(lambda entry: entry.buildingType == buildingType, self.numberOfSpecialistsInBuilding), None)
		if specialistsEntry is not None:
			return specialistsEntry.specialists

		return 0

	def numberOfForcedSpecialistsIn(self, buildingType: BuildingType) -> int:
		specialistsEntry = next(
			filter(lambda entry: entry.buildingType == buildingType, self.numberOfForcedSpecialistsInBuilding), None)
		if specialistsEntry is not None:
			return specialistsEntry.specialists

		return 0

	def doAddBestCitizenFromUnassigned(self, simulation):
		"""Pick the best Plot to work from one of our unassigned pool"""
		# We only assign the unassigned here, folks
		if self.numberOfUnassignedCitizens() == 0:
			return False

		# Maybe we want to add a Specialist?
		if not self.isNoAutoAssignSpecialists():

			# Have to want it right now: look at Food situation, mainly
			if self.isAIWantSpecialistRightNow(simulation):
				bestBuilding = self.bestSpecialistBuilding(simulation)

				# Is there a Specialist we can assign?
				if bestBuilding != BuildingType.none:
					self.doAddSpecialistToBuilding(bestBuilding, forced=False, simulation=simulation)
					return True

		(bestPlot, _) = self.bestCityPlotWithValue(wantBest=True, wantWorked=False, simulation=simulation)

		# Found a Valid Plot to place a guy?
		if bestPlot is not None:
			# Now assign the guy to the best possible Plot
			self.setWorkedAt(bestPlot, worked=True, useUnassignedPool=True)
			return True
		else:
			# No valid Plot - change this guy into a default Specialist
			self.changeNumberOfDefaultSpecialistsBy(1)

		return False

	def doRemoveSpecialistFrom(self, buildingType, forced, simulation):
		# We only assign the unassigned here, folks
		if self.numberOfUnassignedCitizens() == 0:
			return False

		# Maybe we want to add a Specialist?
		if not self.isNoAutoAssignSpecialists():

			# Have to want it right now: look at Food situation, mainly
			if self.isAIWantSpecialistRightNow(simulation):

				bestBuilding = self.bestSpecialistBuilding(simulation)

				# Is there a Specialist we can assign?
				if bestBuilding != BuildingType.none:
					self.doAddSpecialistToBuilding(bestBuilding, forced=False, simulation=simulation)
					return True

		(bestPlot, _) = self.bestCityPlotWithValue(wantBest=True, wantWorked=False, simulation=simulation)

		# Found a Valid Plot to place a guy?
		if bestPlot is not None:
			# Now assign the guy to the best possible Plot
			self.setWorkedAt(bestPlot, worked=True, useUnassignedPool=True)
			return True
		else:
			# No valid Plot - change this guy into a default Specialist
			self.changeNumberOfDefaultSpecialistsBy(1)

		return False

	def workableTiles(self, simulation):
		area = self.city.location.areaWithRadius(radius=City.workRadius)
		result = []

		for neighbor in area:
			if not simulation.valid(neighbor):
				continue

			tile = simulation.tileAt(neighbor)
			result.append(tile)

		return result

	def isBlockaded(self, tile, simulation):
		"""Is there a naval blockade on this water tile?"""
		# See if there are any enemy boats near us that are blockading this plot
		blockadeDistance = 2  # NAVAL_PLOT_BLOCKADE_RANGE

		# Might be a better way to do this that'd be slightly less CPU-intensive
		for nearbyPoint in tile.point.areaWithRadius(blockadeDistance):
			nearbyTile = simulation.tileAt(nearbyPoint)

			# Must be water in the same Area
			if nearbyTile is not None and nearbyTile.terrain().isWater() and nearbyTile.area() == tile.area():
				# Enemy boat within range to blockade our plot?
				if simulation.isEnemyVisibleAt(nearbyTile.point, self.city.player):
					return True

		return False

	def isNoAutoAssignSpecialists(self) -> bool:
		"""Are this City's Specialists under automation?"""
		return self._noAutoAssignSpecialistsValue

	def setNoAutoAssignSpecialists(self, noAutoAssignSpecialists: bool, simulation):
		"""Sets this City's Specialists to be under automation"""
		if self._noAutoAssignSpecialistsValue != noAutoAssignSpecialists:
			self._noAutoAssignSpecialistsValue = noAutoAssignSpecialists

			# If we're giving the AI control clear all manually assigned Specialists
			if not noAutoAssignSpecialists:
				self.doClearForcedSpecialists()

			self.doReallocateCitizens(simulation)

		return

	def isAIWantSpecialistRightNow(self, simulation):
		"""Does the AI want a Specialist?"""
		weight = 100

		# If the City is Size 1 or 2 then we probably don't want Specialists
		if self.city.population() < 3:
			weight /= 2

		foodPerTurn = self.city.foodPerTurn(simulation)
		foodEatenPerTurn = self.city.foodConsumption()
		surplusFood = foodPerTurn - foodEatenPerTurn

		focusTypeValue = self.focusType()

		# If we don't yet have enough Food to feed our City, we dont want no Specialists!
		if surplusFood <= 0:
			weight /= 3
		elif self.isAvoidGrowth() and (
			focusTypeValue == CityFocusType.none or focusTypeValue == CityFocusType.greatPeople):
			weight *= 2
		elif surplusFood <= 2:
			weight /= 2
		elif surplusFood > 2:
			if focusTypeValue == CityFocusType.none or focusTypeValue == CityFocusType.greatPeople or focusTypeValue == CityFocusType.productionGrowth:
				weight *= 100 + (20 * (int(surplusFood) - 4))
				weight /= 100

		# If we're deficient in Production then we're less likely to want Specialists
		if self.city.cityStrategy.isDeficientFor(YieldType.production, simulation):
			weight *= 50
			weight /= 100

		# if we've got some slackers in town (since they provide Production)
		elif self.numberOfDefaultSpecialists() > 0 and focusTypeValue != CityFocusType.production and focusTypeValue != CityFocusType.productionGrowth:
			weight *= 150
			weight /= 100

		# Someone told this AI it should be focused on something that is usually gotten from specialists
		if focusTypeValue == CityFocusType.greatPeople:

			# Loop through all Buildings
			for buildingType in list(BuildingType):

				# Have this Building in the City?
				if self.city.hasBuilding(buildingType):
					# Can't add more than the max
					if self.canAddSpecialistToBuilding(buildingType):
						weight *= 3
						break

		elif focusTypeValue == CityFocusType.culture:

			# Loop through all Buildings
			for buildingType in list(BuildingType):

				# Have this Building in the City?
				if self.city.hasBuilding(buildingType):

					# Can't add more than the max
					if self.canAddSpecialistToBuilding(buildingType):

						if buildingType.specialistType().yields().value(YieldType.culture) > 0:
							weight *= 3
							break

		elif focusTypeValue == CityFocusType.science:

			# Loop through all Buildings
			for buildingType in list(BuildingType):

				# Have this Building in the City?
				if self.city.hasBuilding(buildingType):

					#  Can't add more than the max
					if self.canAddSpecialistToBuilding(buildingType):

						if buildingType.specialistType().yields().value(YieldType.science) > 0:
							weight *= 3

			# FIXME
			# if (GetPlayer()->getSpecialistExtraYield(YIELD_SCIENCE) > 0)
			# iWeight *= 3;

			# FIXME
			# if (GetPlayer()->GetPlayerTraits()->GetSpecialistYieldChange(eSpecialist, YIELD_SCIENCE) > 0)
			# iWeight *= 3;

		elif focusTypeValue == CityFocusType.production:
			# Loop through all Buildings
			for buildingType in list(BuildingType):

				# Have this Building in the City?
				if self.city.hasBuilding(buildingType):

					# Can't add more than the max
					if self.canAddSpecialistToBuilding(buildingType):

						if buildingType.specialistType().yields().value(YieldType.production) > 0:
							weight *= 150
							weight /= 100

			# FIXME
			# if (GetPlayer()->getSpecialistExtraYield(YIELD_PRODUCTION) > 0)
			# iWeight *= 2;

			# FIXME
			# if (GetPlayer()->GetPlayerTraits()->GetSpecialistYieldChange(eSpecialist, YIELD_PRODUCTION) > 0)
			#   iWeight *= 2;

		elif focusTypeValue == CityFocusType.gold:

			# Loop through all Buildings
			for buildingType in list(BuildingType):

				# Have this Building in the City?
				if self.city.hasBuilding(buildingType):

					# Can't add more than the max
					if self.canAddSpecialistToBuilding(buildingType):

						if buildingType.specialistType().yields().value(YieldType.gold) > 0:
							weight *= 150
							weight /= 100
							break

		elif focusTypeValue == CityFocusType.food:
			weight *= 50
			weight /= 100

		elif focusTypeValue == CityFocusType.productionGrowth:

			# Loop through all Buildings
			for buildingType in list(BuildingType):

				# Have this Building in the City?
				if self.city.hasBuilding(buildingType):

					# Can't add more than the max
					if self.canAddSpecialistToBuilding(buildingType):

						if buildingType.specialistType().yields().value(YieldType.production) > 0:
							weight *= 150
							weight /= 100
							break

		elif focusTypeValue == CityFocusType.goldGrowth:

			# Loop through all Buildings
			for buildingType in list(BuildingType):

				# Have this Building in the City?
				if self.city.hasBuilding(buildingType):

					# Can't add more than the max
					if self.canAddSpecialistToBuilding(buildingType):
						if buildingType.specialistType().yields().value(YieldType.gold) > 0:
							weight *= 150
							weight /= 100

			# FIXME
			# if (GetPlayer()->getSpecialistExtraYield(YIELD_GOLD) > 0):
			# iWeight *= 2;

			# FIXME
			# if (GetPlayer()->GetPlayerTraits()->GetSpecialistYieldChange(eSpecialist, YIELD_GOLD) > 0):
			#  iWeight *= 2;

		# Does the AI want it enough?
		if weight >= 150:
			return True

		return False

	def canAddSpecialistToBuilding(self, buildingType: BuildingType) -> bool:
		"""Are we in the position to add another Specialist to eBuilding?"""
		numSpecialistsAssigned = self.numberOfSpecialistsIn(buildingType)

		# Limit based on Pop of City
		# Limit for this particular Building
		if numSpecialistsAssigned < self.city.population() and \
			numSpecialistsAssigned < buildingType.specialistCount() and \
			numSpecialistsAssigned < 5:  # MAX_SPECIALISTS_FROM_BUILDING - Overall Limit

			return True

		return False

	def doClearForcedSpecialists(self):
		"""Remove forced status from all Specialists"""
		# Loop through all Buildings
		self.numberOfForcedSpecialistsInBuilding = []

	def bestSpecialistBuilding(self, simulation) -> BuildingType:
		"""What is the Building Type the AI likes the Specialist of most right now?"""
		bestBuilding: BuildingType = BuildingType.none
		bestSpecialistValue = -1

		# Loop through all Buildings
		for buildingType in list(BuildingType):

			# Have this Building in the City?
			if self.city.buildings.hasBuilding(buildingType):

				# Can't add more than the max
				if buildingType.canAddSpecialist():
					specialistType = buildingType.specialistType()
					value = self.specialistValueFor(specialistType, simulation)

					# Add a bit more weight to a Building if it has more slots(10 % per).
					# This will bias the AI to fill a single building over spreading Specialists out
					temp = ((buildingType.specialistCount() - 1) * value * 10)
					temp /= 100
					value += temp

					if value > bestSpecialistValue:
						bestBuilding = buildingType
						bestSpecialistValue = value

		return bestBuilding

	def specialistValueFor(self, specialistType, simulation) -> int:
		"""How valuable is eSpecialist?"""
		value = 20

		deficientYield = self.city.cityStrategy.deficientYield(simulation)

		# Does this Specialist help us with a Deficient Yield?
		focusTypeValue = self.focusType()

		if focusTypeValue == CityFocusType.science:
			value += int(specialistType.yields().science) * 3
		elif focusTypeValue == CityFocusType.culture:
			value += int(specialistType.yields().culture) * 3
		elif focusTypeValue == CityFocusType.gold:
			value += int(specialistType.yields().gold) * 3
		elif focusTypeValue == CityFocusType.production:
			if deficientYield == YieldType.production:
				value += (value * int(specialistType.yields().value(deficientYield)))

			value += int(specialistType.yields().production) * 2
		elif focusTypeValue == CityFocusType.greatPeople:
			# FIXME value += (GetSpecialistGreatPersonProgress(eSpecialist) / 5);
			if deficientYield != YieldType.none:
				value += (value * int(specialistType.yields().value(deficientYield)))
		elif focusTypeValue == CityFocusType.food:
			value += int(specialistType.yields().food) * 3
		elif focusTypeValue == CityFocusType.productionGrowth:
			if deficientYield == YieldType.production:
				value += (value * int(specialistType.yields().value(deficientYield)))

			value += int(specialistType.yields().production) * 2
		elif focusTypeValue == CityFocusType.goldGrowth:
			value += int(specialistType.yields().gold) * 2
		else:
			if deficientYield != YieldType.none:
				value += (value * int(specialistType.yields().value(deficientYield)))

			# if we are nearing completion of a GP
			value += (self.specialistGreatPersonProgressFor(specialistType) / 10)

		# GPPs are always good
		value += specialistType.greatPeopleRateChange()

		return value

	def doAddSpecialistToBuilding(self, buildingType: BuildingType, forced: bool, simulation):
		"""Adds and initializes a Specialist for this building"""
		specialistType = buildingType.specialistType()

		# Can't add more than the max
		if self.canAddSpecialistToBuilding(buildingType):
			# If we're force-assigning a specialist, then we can reduce the count on forced default specialists
			if forced:
				if self.numberOfForcedDefaultSpecialists() > 0:
					self.changeNumberOfForcedDefaultSpecialists(-1)

			# If we don't already have an Unassigned Citizen to turn into a Specialist, find one from somewhere
			if self.numberOfUnassignedCitizens() == 0:
				self.doRemoveWorstCitizen(removeForcedStatus=True, dontChangeSpecialist=specialistType,
				                          simulation=simulation)

				if self.numberOfUnassignedCitizens() == 0:
					# Still nobody, all the citizens may be assigned to the eSpecialist we are looking for, try again
					if not self.doRemoveWorstSpecialist(dontRemoveFromBuilding=buildingType, simulation=simulation):
						return  # For some reason we can't do this, we must exit, else we will be going over the population count

			# Increase count for the whole city
			self.numberOfSpecialists.increaseNumberOf(specialistType)
			self.increaseNumberOfSpecialists(buildingType)

			if forced:
				self.increaseNumberOfForcedSpecialistsIn(buildingType)

			self.city.processSpecialist(specialistType, 1)

			self.changeNumberOfUnassignedCitizensBy(-1)

	def specialistGreatPersonProgressFor(self, specialistType) -> int:
		return int(self.specialistGreatPersonProgress.weight(specialistType))

	def increaseNumberOfSpecialists(self, buildingType: BuildingType):
		# update
		specialistsTuple = next(
			filter(lambda spec: spec.buildingType == buildingType, self.numberOfSpecialistsInBuilding), None)
		if specialistsTuple is not None:
			specialistsTuple.specialists += 1
			return

		# create new entry
		self.numberOfSpecialistsInBuilding.append(SpecialistBuilding(buildingType, 1))

	def increaseNumberOfForcedSpecialistsIn(self, buildingType):
		# update
		specialistsTuple = next(
			filter(lambda spec: spec.buildingType == buildingType, self.numberOfForcedSpecialistsInBuilding), None)
		if specialistsTuple is not None:
			specialistsTuple.specialists += 1
			return

		# create new entry
		self.numberOfForcedSpecialistsInBuilding.append(SpecialistBuilding(buildingType, 1))


class GreatWorkPlaceInBuilding:
	def __init__(self, building: BuildingType, slot: GreatWorkSlotType, used: bool = False):
		self.building = building
		self.slot = slot
		self.used = used


class CityGreatWorks:
	def __init__(self, city):
		self.city = city

		self._placesInBuildings = []

	def addPlacesFor(self, building: BuildingType):
		for slot in building.slotsForGreatWork():
			self._placesInBuildings.append(GreatWorkPlaceInBuilding(building, slot))


class CityReligion:
	def __init__(self, city):
		self.city = city


class CityTradingPosts:
	def __init__(self, city):
		self.city = city

	def buildTradingPost(self, leader: LeaderType):
		pass

	def hasTradingPostOf(self, leader: LeaderType) -> bool:
		return False


class CityTourism:
	def __init__(self, city):
		self.city = city


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


class BuildQueue:
	def __init__(self):
		self._items: [BuildableItem] = []

	def __iter__(self):
		return self._items.__iter__()

	def append(self, buildableItem: BuildableItem):
		self._items.append(buildableItem)

	def peek(self) -> Optional[BuildableItem]:
		if len(self._items) == 0:
			return None

		return self._items[0]

	def buildingOf(self, buildingType: BuildingType) -> Optional[BuildableItem]:
		item = next(filter(lambda
			                   itemIterator: itemIterator.buildableType == BuildableType.building and itemIterator.buildingType == buildingType,
		                   self._items), None)
		if item is not None:
			return item

		return None

	def unitOf(self, unitType: UnitType) -> Optional[BuildableItem]:
		item = next(filter(
			lambda itemIterator: itemIterator.buildableType == BuildableType.unit and itemIterator.unitType == unitType,
			self._items), None)
		if item is not None:
			return item

		return None

	def pop(self):
		self._items.pop()

	def isCurrentlyBuildingDistrict(self, district: Optional[DistrictType] = None) -> bool:
		if district is None:
			return len(list(filter(lambda it: it.buildableType == BuildableType.district, self._items))) > 0
		else:
			return len(list(filter(lambda it: it.buildableType == BuildableType.district and it.district == district,
			                       self._items))) > 0

	def isCurrentlyBuildingBuilding(self, building: Optional[BuildingType] = None) -> bool:
		if building is None:
			return len(list(filter(lambda it: it.buildableType == BuildableType.building, self._items))) > 0
		else:
			return len(list(filter(lambda it: it.buildableType == BuildableType.building and it.building == building,
			                       self._items))) > 0

	def isCurrentlyBuildingWonder(self, wonder: Optional[WonderType] = None) -> bool:
		if wonder is None:
			return len(list(filter(lambda it: it.buildableType == BuildableType.wonder, self._items))) > 0
		else:
			return len(list(
				filter(lambda it: it.buildableType == BuildableType.wonder and it.wonder == wonder, self._items))) > 0

	def isCurrentlyTrainingUnit(self, unit: Optional[UnitType] = None) -> bool:
		if unit is None:
			return len(list(filter(lambda it: it.buildableType == BuildableType.unit, self._items))) > 0
		else:
			return len(
				list(filter(lambda it: it.buildableType == BuildableType.unit and it.unit == unit, self._items))) > 0


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
		self._lastTurnFoodEarnedValue = 0.0
		self._lastTurnFoodHarvestedValue = 0.0

		self.player = player
		self.leader = player.leader
		self.originalLeaderValue = player.leader
		self.previousLeaderValue = None

		self._isFeatureSurroundedValue = False
		self._cheapestPlotInfluenceValue = 0

		self.threatVal = 0
		self._garrisonedUnitValue = None
		self._numberOfAttacksMade = 0

		self.healthPointsValue = 200
		self.amenitiesForWarWearinessValue = 0

		self._luxuries = []

		self.productionAutomatedValue: bool = False
		self.baseYieldRateFromSpecialists = YieldList()
		self.extraSpecialistYield = YieldList()
		self.numPlotsAcquiredList = LeaderWeightList()

		self._featureProductionValue = 0.0
		self._productionLastTurnValue = 0.0
		self._buildQueue = BuildQueue()
		self._routeToCapitalConnectedLastTurn: bool = False
		self._routeToCapitalConnectedThisTurn: bool = False

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
				if otherPlayer.isAlive() and self.player.diplomacyAI.hasMetWith(otherPlayer):
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
			tiles = self.location.areaWithRadius(radius=2).points()
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

	def addHealthPoints(self, healthPoints):
		self.healthPointsValue += healthPoints

	def featureProduction(self) -> float:
		return self._featureProductionValue

	def changeFeatureProduction(self, change: float):
		self._featureProductionValue += change

	def setFeatureProduction(self, value: float):
		self._featureProductionValue = value

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
			# 			cityStatePlayer?.fulfillQuest(by: player.leader,simulation)

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

	def power(self, simulation) -> int:
		return int(
			pow(float(self.defensiveStrengthAgainst(unit=None, tile=None, ranged=False, simulation=simulation)) / 100.0,
			    1.5))

	def doUpdateCheapestPlotInfluence(self, simulation):
		"""What is the cheapest plot we can get"""
		lowestCost = sys.maxsize

		for loopPoint in self.location.areaWithRadius(City.workRadius):
			loopPlot = simulation.tileAt(loopPoint)

			if loopPlot is None:
				continue

			# If the plot's not owned by us, it doesn't matter
			if loopPlot.hasOwner():
				continue

			# we can use the faster, but slightly inaccurate pathfinder here -
			# after all we are using a rand in the equation
			influenceCost = simulation.calculateInfluenceDistance(self.location, loopPoint, limit=City.workRadius)

			if influenceCost > 0:
				# Are we the cheapest yet?
				if influenceCost < lowestCost:
					lowestCost = influenceCost

		self.setCheapestPlotInfluence(lowestCost)

	def setCheapestPlotInfluence(self, value: int):
		self._cheapestPlotInfluenceValue = value

	def cheapestPlotInfluence(self) -> int:
		return self._cheapestPlotInfluenceValue

	def doAcquirePlot(self, point: HexPoint, simulation):
		"""Acquire the plot and set its owner to us"""
		tile = simulation.tileAt(point)

		tile.setOwner(self.player)
		tile.setWorkingCity(self)

		self.player.addPlotAt(point)

		self.doUpdateCheapestPlotInfluence(simulation)

		# clear barbarian camps / goody huts
		if tile.hasImprovement(ImprovementType.barbarianCamp):
			self.player.doClearBarbarianCampAt(tile, simulation)
		elif tile.hasImprovement(ImprovementType.goodyHut):
			self.player.doGoodyHutAt(tile, None, simulation)

		# repaint newly acquired tile...
		simulation.userInterface.refreshTile(tile)

		# ... and neighbors
		for neighbor in point.neighbors():
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile is None:
				continue

			simulation.userInterface.refreshTile(neighborTile)

		return

	def updateEurekas(self, simulation):
		# militaryTraining - Build any district.
		if not self.player.civics.inspirationTriggeredFor(CivicType.stateWorkforce):
			if self.districts.hasAny():
				# city center is taken into account
				self.player.civics.triggerInspirationFor(CivicType.stateWorkforce, simulation)

		# militaryTraining - Build an Encampment.
		if not self.player.civics.inspirationTriggeredFor(CivicType.militaryTraining):
			if self.districts.hasDistrict(DistrictType.encampment):
				self.player.civics.triggerInspirationFor(CivicType.militaryTraining, simulation)

		# recordedHistory - Build 2 Campus Districts.
		if not self.player.civics.inspirationTriggeredFor(CivicType.recordedHistory):
			if self.player.numberOfDistricts(DistrictType.campus, simulation) >= 2:
				self.player.civics.triggerInspirationFor(CivicType.recordedHistory, simulation)

		# construction - Build water mill.
		if not self.player.techs.eurekaTriggeredFor(TechType.construction):
			if self.buildings.hasBuilding(BuildingType.waterMill):
				self.player.techs.triggerEurekaFor(TechType.construction, simulation)

		# engineering - Build ancient walls
		if not self.player.techs.eurekaTriggeredFor(TechType.engineering):
			if self.buildings.hasBuilding(BuildingType.ancientWalls):
				self.player.techs.triggerEurekaFor(TechType.engineering, simulation)

		# shipBuilding - Own 2 Galleys
		if not self.player.techs.eurekaTriggeredFor(TechType.shipBuilding):
			if len(list(filter(lambda unit: unit.unitType == UnitType.galley, simulation.unitsOf(self.player)))) >= 2:
				self.player.techs.triggerEurekaFor(TechType.shipBuilding, simulation)

		# economics - build 2 banks
		if not self.player.techs.eurekaTriggeredFor(TechType.economics):
			if self.player.numberBuildings(BuildingType.bank, simulation) >= 2:
				self.player.techs.triggerEurekaFor(TechType.economics, simulation)

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
				if workedTile.hasFeature(FeatureType.marsh) and self.player.hasWonder(WonderType.etemenanki,
				                                                                      simulation):
					productionValue += 1.0

				# etemenanki - +1 Science and +1 Production on all Floodplains tiles in this city.
				if workedTile.hasFeature(FeatureType.floodplains) and self.hasWonder(WonderType.etemenanki):
					productionValue += 1.0

				# godOfTheSea - 1 Production from Fishing Boats.
				if workedTile.improvement() == ImprovementType.fishingBoats and \
					self.player.religion.pantheon() == PantheonType.godOfTheSea:
					productionValue += 1.0

				# ladyOfTheReedsAndMarshes - +2 Production from Marsh, Oasis, and Desert Floodplains.
				if (workedTile.hasFeature(FeatureType.marsh) or workedTile.hasFeature(FeatureType.oasis) or
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
				if self.player.isSuzerainOf(CityStateType.auckland, simulation):
					if workedTile.terrain() == TerrainType.shore:
						productionValue += 1.0

					if self.player.currentEra() == EraType.industrial:
						productionValue += 1.0

				# johannesburg suzerain bonus
				# Cities receive + 1 Production for every improved resource type.
				# After researching Industrialization it becomes +2[Production] Production.
				if self.player.isSuzerainOf(CityStateType.johannesburg, simulation):
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
			industrialLocation = self.locationOfDistrict(DistrictType.industrialZone)

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
				if neighborTile.hasImprovement(
					ImprovementType.mine):  # /*|| neighborTile.has(improvement: .lumberMill)*/ {
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
		if self.player.isSuzerainOf(CityStateType.singapore, simulation):
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
						if self.governor().type() == GovernorType.reyna and self.governor().hasTitle(
							GovernorTitle.forestryManagement):
							goldValue = 2.0

		return goldValue

	def _goldFromGovernmentType(self) -> YieldValues:
		goldFromGovernmentValue: YieldValues = YieldValues(value=0.0, percentage=0.0)

		# yields from government
		government = self.player.government

		# https://civilization.fandom.com/wiki/Autocracy_(Civ6)
		# +1 to all yields for each government building and Palace in a city.
		if government.currentGovernment() == GovernmentType.autocracy:
			goldFromGovernmentValue += float(self.buildings.numberOfBuildingsOf(BuildingCategoryType.government))

		# godKing
		if government.hasCard(PolicyCardType.godKing) and self.capitalValue == True:
			goldFromGovernmentValue += 1.0

		# thirdAlternative - +2 Culture and +4 Gold from each Research Lab, Military Academy, Coal Power Plant,
		# Oil Power Plant, and Nuclear Power Plant.
		if government.hasCard(PolicyCardType.thirdAlternative):
			if self.buildings.hasBuilding(BuildingType.researchLab):
				goldFromGovernmentValue += 4

			if self.buildings.hasBuilding(BuildingType.militaryAcademy):
				goldFromGovernmentValue += 4

			if self.buildings.hasBuilding(BuildingType.coalPowerPlant):
				goldFromGovernmentValue += 4

			if self.buildings.hasBuilding(BuildingType.oilPowerPlant):
				goldFromGovernmentValue += 4

			if self.buildings.hasBuilding(BuildingType.nuclearPowerPlant):
				goldFromGovernmentValue += 4

		# - Decentralization Cities with 6 or less population receive +4 Loyalty per turn.
		# BUT: Cities with more than 6 Citizen population receive -15 % Gold.
		if government.hasCard(PolicyCardType.decentralization) and self.population() > 6:
			goldFromGovernmentValue += YieldValues(value=0.0, percentage=-0.15)

		# yields from governors
		if self.governor() is not None:
			# Reyna + taxCollector - +2 Gold per turn for each Citizen in the city.
			if self.governor().type() == GovernorType.reyna and self.governor().hasTitle(GovernorTitle.taxCollector):
				goldFromGovernmentValue += 2.0 * float(self.population())

		return goldFromGovernmentValue

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

		return

	def isCapital(self) -> bool:
		return self.capitalValue

	def hasOnlySmallFoodSurplus(self) -> bool:
		exceedFood = self._lastTurnFoodEarnedValue - float(self.foodConsumption())
		return 0.0 < exceedFood < 2.0

	def hasFoodSurplus(self) -> bool:
		exceedFood = self._lastTurnFoodEarnedValue - float(self.foodConsumption())
		return 0.0 < exceedFood < 4.0

	def hasEnoughFood(self) -> bool:
		exceedFood = self._lastTurnFoodEarnedValue - float(self.foodConsumption())
		return exceedFood > 0.0

	def damage(self) -> int:
		return max(0, self.maxHealthPoints() - self.healthPointsValue)

	def maxHealthPoints(self) -> int:
		healthPointsVal = 200

		if self.buildings.hasBuilding(BuildingType.ancientWalls):
			healthPointsVal += 100

		if self.buildings.hasBuilding(BuildingType.medievalWalls):
			healthPointsVal += 100

		if self.buildings.hasBuilding(BuildingType.renaissanceWalls):
			healthPointsVal += 100

		return healthPointsVal

	def setDamage(self, damage: int):
		self.healthPointsValue = self.maxHealthPoints() - damage

		self.healthPointsValue = max(self.healthPointsValue, self.maxHealthPoints())
		self.healthPointsValue = min(0, self.healthPointsValue)

	def setMadeAttackTo(self, madeAttack: bool):
		if madeAttack:
			self._numberOfAttacksMade += 1
		else:
			self._numberOfAttacksMade = 0

	def doCheckProduction(self, simulation):
		okay = True

		# ...

		if not self.isProduction() and self.player.isHuman() and not self.isProductionAutomated():
			self.player.notifications.addNotification(NotificationType.productionNeeded, cityName=self.name,
			                                          location=self.location)
			return okay

		# ...

		okay = self.cleanUpQueue(simulation)

		return okay

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
		# 			player.addMoment(of:.firstBustlingCity(cityName: self.name),simulation)
		# 		else:
		# 			player.addMoment(of:.worldsFirstBustlingCity(cityName: self.name),simulation)

		# if self._populationValue > 15:
		# 	if not player.hasMoment(of: .firstLargeCity(cityName: self.name)) and
		# 		not player.hasMoment(of:.worldsFirstLargeCity(cityName: self.name)):
		#
		#         #  check if someone else already had a bustling city
		# 		if gameModel.anyHasMoment(of: .worldsFirstLargeCity(cityName: self.name)):
		# 			player.addMoment(of:.firstLargeCity(cityName: self.name),simulation)
		# 		else:
		# 			player.addMoment(of:.worldsFirstLargeCity(cityName: self.name),simulation)

		# if self.populationValue > 20:
		# 	if not self.player.hasMoment(of: .firstEnormousCity(cityName: self.name)) and
		# 		not self.player.hasMoment(of:.worldsFirstEnormousCity(cityName: self.name)):
		#
		#         # check if someone else already had a bustling city
		# 		if simulation.anyHasMoment(of: .worldsFirstEnormousCity(cityName: self.name)) {
		# 			player.addMoment(of:.firstEnormousCity(cityName: self.name),simulation)
		# 		else:
		# 			player.addMoment(of:.worldsFirstEnormousCity(cityName: self.name),simulation)

		# if self._populationValue > 25:
		# 	if not self.player.hasMoment(of: .firstGiganticCity(cityName: self.name)) and
		# 		not player.hasMoment(of:.worldsFirstGiganticCity(cityName: self.name)):
		#
		#         # check if someone else already had a bustling city
		# 		if gameModel.anyHasMoment(of: .worldsFirstGiganticCity(cityName: self.name)):
		# 			player.addMoment(of:.firstGiganticCity(cityName: self.name),simulation)
		# 		else:
		# 			player.addMoment(of:.worldsFirstGiganticCity(cityName: self.name),simulation)

		elif self.foodBasket() < 0:
			self.setFoodBasket(0)

			if self.population() > 1:
				self.setPopulation(self.population() - 1, reassignCitizen=False, simulation=simulation)

	def doProduction(self, allowNoProduction, simulation):
		if not self.player.isHuman() or self.isProductionAutomated():
			if not self.isProduction():  # or self.isProductionProcess() or AI_isChooseProductionDirty()
				self.AI_chooseProduction(interruptWonders=False, simulation=simulation)

		if not allowNoProduction and not self.isProduction():
			return

		# processes are wealth or science
		# if self.isProductionProcess()
		# return

		if self.isProduction():
			production: float = self.productionPerTurn(simulation)
			modifierPercentage = 0.0

			effects = self.player.envoyEffects(simulation)

			for effect in effects:
				# Industrial: +2 Production in the Capital when producing wonders, buildings, and districts.
				if effect.isEqualCategory(CityStateCategory.industrial, EnvoyEffectLevel.first) and self.capitalValue:

					if self._buildQueue.isCurrentlyBuildingBuilding() or \
						self._buildQueue.isCurrentlyBuildingDistrict() or \
						self._buildQueue.isCurrentlyBuildingWonder():
						production += 2.0

				# Industrial: +2 Production in every city with a Workshop building when producing wonders, buildings, and districts.
				if effect.isEqualCategory(CityStateCategory.industrial, EnvoyEffectLevel.third) and self.hasBuilding(
					BuildingType.workshop):
					if self._buildQueue.isCurrentlyBuildingBuilding() or \
						self._buildQueue.isCurrentlyBuildingDistrict() or \
						self._buildQueue.isCurrentlyBuildingWonder():
						production += 2.0

				# Industrial: +2 Production in every city with a Factory building when producing wonders, buildings, and districts.
				if effect.isEqualCategory(CityStateCategory.industrial, EnvoyEffectLevel.sixth) and self.hasBuilding(
					BuildingType.factory):
					if self._buildQueue.isCurrentlyBuildingBuilding() or \
						self._buildQueue.isCurrentlyBuildingDistrict() or \
						self._buildQueue.isCurrentlyBuildingWonder():
						production += 2.0

				# Militaristic: +2 Production in the Capital when producing units.
				if effect.isEqualCategory(CityStateCategory.militaristic, EnvoyEffectLevel.first) and self.capitalValue:
					if self._buildQueue.isCurrentlyTrainingUnit():
						production += 2.0

				# Militaristic: +2 Production in every city with a Barracks or Stable building when producing units.
				if effect.isEqualCategory(CityStateCategory.militaristic, EnvoyEffectLevel.third) and \
					(self.hasBuilding(BuildingType.barracks) or self.hasBuilding(BuildingType.stable)):
					if self._buildQueue.isCurrentlyTrainingUnit():
						production += 2.0

				# Militaristic: +2 Production in every city with an Armory building when producing units.
				if effect.isEqualCategory(CityStateCategory.militaristic, EnvoyEffectLevel.sixth) and self.hasBuilding(
					BuildingType.armory):
					if self._buildQueue.isCurrentlyTrainingUnit():
						production += 2.0

				# brussels suzerain bonus
				# Your cities get +15% Production towards wonders.
				if effect.cityState == CityStateType.brussels and effect.level == EnvoyEffectLevel.suzerain:
					if self.productionWonderType() is not None:
						modifierPercentage += 0.15

			# +1 Production in all cities.
			if self.player.government.hasCard(PolicyCardType.urbanPlanning):
				production += 1.0

			# city state production bonus is 50%
			if self.player.isCityState():
				modifierPercentage += 0.5

			# https://civilization.fandom.com/wiki/Autocracy_(Civ6)
			# +10% Production toward Wonders.
			if self.player.government.currentGovernment() == GovernmentType.autocracy:
				if self.productionWonderType() is not None:
					modifierPercentage += 0.1

			# +15% Production toward Districts.
			if self.player.government.currentGovernment() == GovernmentType.merchantRepublic:
				if self._buildQueue.isCurrentlyBuildingDistrict():
					modifierPercentage += 0.15

			# +50% Production toward Units.
			if self.player.government.currentGovernment() == GovernmentType.fascism:
				if self._buildQueue.isCurrentlyTrainingUnit():
					modifierPercentage += 0.50

			# +15 % Production.
			if self.player.government.currentGovernment() == GovernmentType.communism:
				modifierPercentage += 0.15

			# +1 Production ... per District.
			if self.player.government.currentGovernment() == GovernmentType.democracy:
				production += float(self.districts.numberOfBuiltDistricts())

			# +20 % Production towards Medieval, Renaissance, and Industrial Wonders.
			if self.player.leader.civilization().ability() == CivilizationAbility.grandTour:
				if self.productionWonderType() is not None:
					if self.productionWonderType().era() == EraType.ancient or \
						self.productionWonderType().era() == EraType.classical:
						modifierPercentage += 0.20

			# +15 % Production towards Districts and wonders built next to a river.
			if self.player.leader.civilization().ability() == CivilizationAbility.iteru:
				if simulation.riverAt(self.location):
					if self.productionWonderType() is not None or self.productionDistrictType() is not None:
						modifierPercentage += 0.15

			# corvee - +15 % Production toward Ancient and Classical wonders.
			if self.player.government.hasCard(PolicyCardType.corvee):
				if self.productionWonderType() is not None:
					if self.productionWonderType().era() == EraType.ancient or \
						self.productionWonderType().era() == EraType.classical:
						modifierPercentage += 0.15

			# ilkum - +30 % Production toward Builders.
			if self.player.government.hasCard(PolicyCardType.ilkum):
				if self._buildQueue.isCurrentlyTrainingUnit(UnitType.builder):
					modifierPercentage += 0.30

			# colonization - +50 % Production toward Settlers.
			if self.player.government.hasCard(PolicyCardType.colonization):
				if self._buildQueue.isCurrentlyTrainingUnit(UnitType.settler):
					modifierPercentage += 0.50

			# maneuver - +50 % Production toward Ancient and Classical era heavy and light cavalry units.
			if self.player.government.hasCard(PolicyCardType.maneuver):
				if self._buildQueue.isCurrentlyTrainingUnit(UnitClassType.heavyCavalry) or \
					self._buildQueue.isCurrentlyTrainingUnit(UnitClassType.lightCavalry):
					modifierPercentage += 0.50

			# maritimeIndustries - +100 % Production toward Ancient and Classical era naval units.
			if self.player.government.hasCard(PolicyCardType.maritimeIndustries):
				unitType = self.productionUnitType()
				if unitType is not None:
					if unitType.unitClass() == UnitClassType.navalMelee and \
						(unitType.era() == EraType.ancient or unitType.era() == EraType.classical):
						modifierPercentage += 1.0

			# limes - +100% Production toward defensive buildings.
			if self.player.government.hasCard(PolicyCardType.limes):
				buildingType = self.productionBuildingType()
				if buildingType is not None:
					if buildingType.defense() > 0:
						modifierPercentage += 1.0

			# agoge - +50 % Production toward Ancient and Classical era melee, ranged units and anti - cavalry units.
			if self.player.government.hasCard(PolicyCardType.agoge):
				unitType = self.productionUnitType()
				if unitType is not None:
					if (unitType.unitClass() == UnitClassType.melee or unitType.unitClass() == UnitClassType.ranged or \
					    unitType.unitClass() == UnitClassType.antiCavalry) and (unitType.era() == EraType.ancient or \
					                                                            unitType.era() == EraType.classical):
						modifierPercentage += 0.50

			# veterancy - +30 % Production toward Encampment and Harbor districts and buildings for those districts.
			if self.player.government.hasCard(PolicyCardType.veterancy):
				districtType = self.productionDistrictType()
				if districtType is not None:
					if districtType == DistrictType.encampment or districtType == DistrictType.harbor:
						modifierPercentage += 0.30

				buildingType = self.productionBuildingType()
				if buildingType is not None:
					if buildingType.district() == DistrictType.encampment or buildingType.district() == DistrictType.harbor:
						modifierPercentage += 0.30

			# feudalContract - +50 % Production toward Ancient, Classical, Medieval and Renaissance era melee, ranged and anti - cavalry units.
			if self.player.government.hasCard(PolicyCardType.feudalContract):
				unitType = self.productionUnitType()
				if unitType is not None:
					if (unitType.unitClass() == UnitClassType.melee or unitType.unitClass() == UnitClassType.ranged or
					    unitType.unitClass() == UnitClassType.antiCavalry) and (unitType.era() == EraType.ancient or
					                                                            unitType.era() == EraType.classical or unitType.era() == EraType.medieval or
					                                                            unitType.era() == EraType.renaissance):
						modifierPercentage += 0.50

			# chivalry - +50%  Production toward Industrial era and earlier heavy and light cavalry units.
			if self.player.government.hasCard(PolicyCardType.chivalry):
				unitType = self.productionUnitType()
				if unitType is not None:
					if (
						unitType.unitClass() == UnitClassType.lightCavalry or unitType.unitClass() == UnitClassType.heavyCavalry) and \
						(unitType.era() == EraType.ancient or unitType.era() == EraType.classical or
						 unitType.era() == EraType.medieval or unitType.era() == EraType.renaissance or
						 unitType.era() == EraType.industrial):
						modifierPercentage += 0.50

			# gothicArchitecture - +15%  Production toward Ancient, Classical, Medieval and Renaissance wonders.
			if self.player.government.hasCard(PolicyCardType.gothicArchitecture):
				wonderType = self.productionWonderType()
				if wonderType is not None:
					if wonderType.era() == EraType.ancient or wonderType.era() == EraType.classical or \
						wonderType.era() == EraType.medieval or wonderType.era() == EraType.renaissance:
						modifierPercentage += 0.15

			# militaryFirst - +50% Production toward all melee, anti - cavalry and ranged units.
			if self.player.government.hasCard(PolicyCardType.militaryFirst):
				unitType = self.productionUnitType()
				if unitType is not None:
					if unitType.unitClass() == UnitClassType.melee or \
						unitType.unitClass() == UnitClassType.antiCavalry or \
						unitType.unitClass() == UnitClassType.ranged:
						modifierPercentage += 0.50

			# lightningWarfare - +50% Production for all heavy and light cavalry units.
			if self.player.government.hasCard(PolicyCardType.lightningWarfare):
				unitType = self.productionUnitType()
				if unitType is not None:
					if unitType.unitClass() == UnitClassType.heavyCavalry or \
						unitType.unitClass() == UnitClassType.lightCavalry:
						modifierPercentage += 0.5

			# internationalWaters - +100% Production towards all naval units, excluding Carriers.
			if self.player.government.hasCard(PolicyCardType.internationalWaters):
				unitType = self.productionUnitType()
				if unitType is not None:
					if unitType.unitClass() == UnitClassType.navalMelee or \
						unitType.unitClass() == UnitClassType.navalRaider or \
						unitType.unitClass() == UnitClassType.navalRanged:
						modifierPercentage += 1.0

			# - Automated Workforce +20% Production towards city projects.
			# BUT: -1 Amenities and -5 Loyalty in all cities.
			if self.player.government.hasCard(PolicyCardType.automatedWorkforce):
				projectType = self.productionProjectType()
				if projectType is not None:
					if projectType.unique():
						modifierPercentage += 0.20

			# cityPatronGoddess - +25% Production toward districts in cities without a specialty district.
			if self.player.religion.pantheon() == PantheonType.cityPatronGoddess:
				if not self.districts.hasAnySpecialtyDistrict():
					if self._buildQueue.isCurrentlyBuildingDistrict():
						modifierPercentage += 0.25

			# godOfTheForge - +25% Production toward Ancient and Classical military units.
			if self.player.religion.pantheon() == PantheonType.godOfTheForge:
				unitType = self.productionUnitType()
				if unitType is not None:
					if (unitType.unitClass() == UnitClassType.melee or unitType.unitClass() == UnitClassType.ranged) and \
						(unitType.era() == EraType.ancient or unitType.era() == EraType.classical):
						modifierPercentage += 0.25

			# monumentToTheGods - +15%  Production to Ancient and Classical era Wonders.
			if self.player.religion.pantheon() == PantheonType.monumentToTheGods:
				wonderType = self.productionWonderType()
				if wonderType is not None:
					if wonderType.era() == EraType.ancient or wonderType.era() == EraType.classical:
						modifierPercentage += 0.15

			# governor effects
			if self.governor() is not None:
				# Liang - zoningCommissioner - +20 %Production towards constructing Districts in the city.
				if self.hasGovernorTitle(GovernorTitle.zoningCommissioner):
					if self._buildQueue.isCurrentlyBuildingDistrict():
						modifierPercentage += 0.20

			# Themistocles - +20 % Production towards Naval Ranged promotion class .
			if self.player.hasRetired(GreatPersonType.themistocles):
				unitType = self.productionUnitType()
				if unitType is not None:
					if unitType.unitClass() == UnitClassType.navalRanged:
						modifierPercentage += 0.20

			# statueOfZeus - +50 % Production towards anti - cavalry units.
			if self.hasWonder(WonderType.statueOfZeus):
				unitType = self.productionUnitType()
				if unitType is not None:
					if unitType.unitClass() == UnitClassType.antiCavalry:
						modifierPercentage += 0.50

			# ancestralHall - 50 % increased Production toward Settlers in this city
			if self.hasBuilding(BuildingType.ancestralHall):
				unitType = self.productionUnitType()
				if unitType is not None and unitType == UnitType.settler:
					modifierPercentage += 0.5

			production *= (1.0 + modifierPercentage)

			self.updateProduction(production, simulation)
			self.setFeatureProductionTo(0.0)
		else:
			self.setFeatureProductionTo(0.0)

		return

	def culturePerTurn(self, simulation) -> float:
		culturePerTurn: YieldValues = YieldValues(value=0.0, percentage=1.0)

		culturePerTurn += YieldValues(value=self._cultureFromTiles(simulation))
		culturePerTurn += self._cultureFromGovernmentType()
		culturePerTurn += YieldValues(value=self._cultureFromDistricts(simulation))
		culturePerTurn += YieldValues(value=self._cultureFromBuildings())
		culturePerTurn += YieldValues(value=self._cultureFromWonders(simulation))
		culturePerTurn += YieldValues(value=self._cultureFromPopulation())
		culturePerTurn += YieldValues(value=self._cultureFromTradeRoutes(simulation))
		culturePerTurn += self._cultureFromGovernors()
		culturePerTurn += YieldValues(value=self.baseYieldRateFromSpecialists.weight(YieldType.culture))
		culturePerTurn += YieldValues(value=self._cultureFromEnvoys(simulation))

		# cap yields based on loyalty
		culturePerTurn += YieldValues(value=0.0, percentage=self.loyaltyState().yieldPercentage())

		return culturePerTurn.calc()

	def cultureStored(self) -> float:
		return 0.0

	def updateCultureStoredTo(self, value: float):
		pass

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

	def lastTurnFoodEarned(self) -> float:
		return self._lastTurnFoodEarnedValue

	def setLastTurnFoodEarned(self, foodEarned):
		self._lastTurnFoodEarnedValue = foodEarned

	def setLastTurnFoodHarvested(self, foodHarvested):
		self._lastTurnFoodHarvestedValue = foodHarvested

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

		# for now there can only be one
		if self.hasDistrict(DistrictType.neighborhood):
			# A district in your city that provides Housing based on the Appeal of the tile.
			neighborhoodLocation = self.locationOfDistrict(DistrictType.neighborhood)
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
			holySiteLocation = self.locationOfDistrict(DistrictType.holySite)
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

	def hasBuilding(self, building: BuildingType) -> bool:
		return self.buildings.hasBuilding(building)

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

	def sciencePerTurn(self, simulation) -> float:
		sciencePerTurn: YieldValues = YieldValues(value=0.0, percentage=1.0)

		sciencePerTurn += YieldValues(value=self._scienceFromTiles(simulation))
		sciencePerTurn += self._scienceFromGovernmentType()
		sciencePerTurn += YieldValues(value=self._scienceFromBuildings())
		sciencePerTurn += self._scienceFromDistricts(simulation)
		sciencePerTurn += YieldValues(value=self._scienceFromWonders())
		sciencePerTurn += YieldValues(value=self._scienceFromPopulation())
		sciencePerTurn += YieldValues(value=self._scienceFromTradeRoutes(simulation))
		sciencePerTurn += self._scienceFromGovernors()
		# this is broken - not sure why
		# sciencePerTurn += YieldValues(value=self.baseYieldRateFromSpecialists.weight(of:.science))
		sciencePerTurn += self._scienceFromEnvoys(simulation)

		# cap yields based on loyalty
		sciencePerTurn += YieldValues(value=0.0, percentage=self.loyaltyState().yieldPercentage())

		return sciencePerTurn.calc()

	def _scienceFromTiles(self, simulation) -> float:
		scienceFromTiles: float = 0.0

		centerTile = simulation.tileAt(self.location)
		scienceFromTiles += centerTile.yields(self.player, ignoreFeature=False).science

		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				adjacentTile = simulation.tileAt(point)
				scienceFromTiles += adjacentTile.yields(self.player, ignoreFeature=False).science

				# mausoleumAtHalicarnassus
				if adjacentTile.terrain() == TerrainType.shore and self.hasWonder(WonderType.mausoleumAtHalicarnassus):
					# +1 Science, +1 Faith, and +1 Culture to all Coast tiles in this city.
					scienceFromTiles += 1.0

				# etemenanki - +2 Science and +1 Production to all Marsh tiles in your empire.
				if adjacentTile.hasFeature(FeatureType.marsh) and self.player.hasWonder(WonderType.etemenanki,
				                                                                        simulation):
					scienceFromTiles += 2.0

				# etemenanki - +1 Science and +1 Production on all Floodplains tiles in this city.
				if adjacentTile.hasFeature(FeatureType.floodplains) and self.hasWonder(WonderType.etemenanki):
					scienceFromTiles += 1.0

		return scienceFromTiles

	def _scienceFromGovernmentType(self):
		scienceFromGovernmentValue: YieldValues = YieldValues(value=0.0, percentage=0.0)

		# yields from government
		# https://civilization.fandom.com/wiki/Autocracy_(Civ6)
		# +1 to all yields for each government building and Palace in a city.
		if self.player.government.currentGovernment() == GovernmentType.autocracy:
			scienceFromGovernmentValue += float(self.buildings.numberOfBuildingsOf(BuildingCategoryType.government))

		# militaryResearch - Military Academies, Seaports, and Renaissance Walls generate +2 Science.
		if self.player.government.hasCard(PolicyCardType.militaryResearch):
			if self.buildings.hasBuilding(BuildingType.militaryAcademy):
				scienceFromGovernmentValue += 2.0

			if self.buildings.hasBuilding(BuildingType.seaport):
				scienceFromGovernmentValue += 2.0

			if self.buildings.hasBuilding(BuildingType.renaissanceWalls):
				scienceFromGovernmentValue += 2.0

		# despoticPaternalism - +4 Loyalty per turn in cities with Governors.
		# BUT: -15% Science and -15% Culture in all cities without an established Governor.
		if self.player.government.hasCard(PolicyCardType.despoticPaternalism):
			if self.governor() is None:
				scienceFromGovernmentValue.percentage += -0.15

		return scienceFromGovernmentValue

	def _scienceFromBuildings(self) -> float:
		scienceFromBuildings: float = 0.0

		# gather yields from builds
		for building in list(BuildingType):
			if self.buildings.hasBuilding(building):
				scienceFromBuildings += building.yields().science

			# Libraries provide + 1 Science.
			# https://civilization.fandom.com/wiki/Hypatia_(Civ6)
			if building == BuildingType.library and self.player.greatPeople.hasRetired(GreatPersonType.hypatia):
				scienceFromBuildings += 1

		return scienceFromBuildings

	def _scienceFromDistricts(self, simulation):
		scienceFromDistricts: YieldValues = YieldValues(value=0.0, percentage=0.0)
		policyCardModifier: float = 1.0

		# yields from cards
		# naturalPhilosophy - +100% Campus district adjacency bonuses.
		if self.player.government.hasCard(PolicyCardType.naturalPhilosophy):
			policyCardModifier += 1.0

		# fiveYearPlan - +100 % Campus and Industrial Zone district adjacency bonuses.
		if self.player.government.hasCard(PolicyCardType.fiveYearPlan):
			policyCardModifier += 1.0

		# district
		if self.districts.hasDistrict(DistrictType.campus):
			campusLocation = self.locationOf(DistrictType.campus)

			for neighbor in campusLocation.neighbors():
				neighborTile = simulation.tileAt(neighbor)

				# Major bonus(+2 Science) for each adjacent Geothermal Fissure and Reef tile.
				if neighborTile.hasFeature(FeatureType.geyser) or neighborTile.hasFeature(FeatureType.reef):
					scienceFromDistricts += 2.0 * policyCardModifier

				# Major bonus(+2 Science) for each adjacent Great Barrier Reef tile.
				if neighborTile.hasFeature(FeatureType.greatBarrierReef):
					scienceFromDistricts += 2.0 * policyCardModifier

				# Standard bonus(+1 Science) for each adjacent Mountain tile.
				if neighborTile.hasFeature(FeatureType.mountains):
					scienceFromDistricts += 1.0 * policyCardModifier

				# Minor bonus(+½ Science) for each adjacent Rainforest and district tile.
				if neighborTile.hasFeature(FeatureType.rainforest) or neighborTile.district() != DistrictType.none:
					scienceFromDistricts += 0.5 * policyCardModifier

		# freeInquiry + golden - Commercial Hubs and Harbors provide Science equal to their Gold bonus.
		if self.player.currentAge() == AgeType.golden and self.player.hasDedication(DedicationType.freeInquiry):
			if self.districts.hasDistrict(DistrictType.commercialHub):
				scienceFromDistricts += 2.0  # not exactly what the bonus says

			if self.districts.hasDistrict(DistrictType.harbor):
				scienceFromDistricts += 2.0  # not exactly what the bonus says

		# monasticism - +75% Science in cities with a Holy Site.
		# BUT: -25% Culture in all cities.
		if self.player.government.hasCard(PolicyCardType.monasticism) and self.districts.hasDistrict(
			DistrictType.holySite):
			scienceFromDistricts.percentage += 0.75

		return scienceFromDistricts

	def _scienceFromWonders(self) -> float:
		scienceFromWonders: float = 0.0

		# greatLibrary - +2 Science
		if self.wonders.hasWonder(WonderType.greatLibrary):
			scienceFromWonders += 2.0

		return scienceFromWonders

	def _scienceFromPopulation(self) -> float:
		# science & culture from population
		return self._populationValue * 0.5

	def _scienceFromTradeRoutes(self, simulation) -> float:
		scienceFromTradeRoutes: float = 0.0

		for tradeRoute in self.player.tradeRoutes.tradeRoutesStartingAt(city=self):
			scienceFromTradeRoutes += tradeRoute.yields(simulation).science

		return scienceFromTradeRoutes

	def _scienceFromGovernors(self) -> float:
		scienceFromGovernors: YieldValues = YieldValues(value=0.0, percentage=0.0)

		# +1 Science per turn for each Citizen in the city.
		if self.hasGovernorTitle(GovernorTitle.researcher):
			scienceFromGovernors += YieldValues(value=float(self.population()))

		# 15 % increase in Science and Culture generated by the city.
		if self.hasGovernorTitle(GovernorTitle.librarian):
			scienceFromGovernors += YieldValues(value=0.0, percentage=0.15)

		return scienceFromGovernors

	def _scienceFromEnvoys(self, simulation) -> YieldValues:
		scienceFromEnvoys: YieldValues = YieldValues(value=0.0, percentage=0.0)
		effects = self.player.envoyEffects(simulation)

		for effect in effects:
			# +2 Science in the Capital.
			if effect.isEqualCategory(CityStateCategory.scientific, EnvoyEffectLevel.first) and self.capitalValue:
				scienceFromEnvoys += YieldValues(value=2.0)

			# +2 Science in every Library building.
			if effect.isEqualCategory(CityStateCategory.scientific, EnvoyEffectLevel.third) and self.hasBuilding(
				BuildingType.library):
				scienceFromEnvoys += YieldValues(value=2.0)

			# +2 Science in every University building.
			if effect.isEqualCategory(CityStateCategory.scientific, EnvoyEffectLevel.sixth) and self.hasBuilding(
				BuildingType.university):
				scienceFromEnvoys += YieldValues(value=2.0)
			# taruga suzerain effect
			# Your cities receive +5% Science for each different Strategic Resource they have.
			if effect.cityState == CityStateType.taruga and effect.level == EnvoyEffectLevel.suzerain:
				differentResources = float(self.numberOfDifferentStrategicResources(simulation))
				scienceFromEnvoys += YieldValues(percentage=5.0 * differentResources)

			# geneva suzerain effect
			# Your cities earn +15% Science whenever you are not at war with any civilization.
			if effect.cityState == CityStateType.geneva and effect.level == EnvoyEffectLevel.suzerain:
				if self.player.atWarCount() == 0:
					scienceFromEnvoys += YieldValues(value=0.0, percentage=0.15)

		return scienceFromEnvoys

	def hasGovernorTitle(self, title: GovernorTitle) -> bool:
		if self.governor() is not None:
			if self.governor().defaultTitle() == title:
				return True

			return self.governor().hasTitle(title)

		return False

	def _cultureFromTiles(self, simulation) -> float:
		cultureFromTiles: float = 0.0
		hasStBasilsCathedral = self.player.hasWonder(WonderType.stBasilsCathedral, simulation)

		centerTile = simulation.tileAt(self.location)
		cultureFromTiles += centerTile.yields(self.player, ignoreFeature=False).culture

		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				adjacentTile = simulation.tileAt(point)
				cultureFromTiles += adjacentTile.yields(self.player, ignoreFeature=False).culture

				# city has mausoleumAtHalicarnassus: +1 Science, +1 Faith,
				# and +1 Culture to all Coast tiles in this city.
				if adjacentTile.terrain() == TerrainType.shore and self.hasWonder(WonderType.mausoleumAtHalicarnassus):
					cultureFromTiles += 1.0

				# city has chichenItza: +2 Culture and +1 Production to all Rainforest tiles for this city.
				if adjacentTile.hasFeature(FeatureType.rainforest) and self.hasWonder(WonderType.chichenItza):
					cultureFromTiles += 2.0

				# stBasilsCathedral
				if adjacentTile.terrain() == TerrainType.tundra and hasStBasilsCathedral:
					# +1 Food, +1 Production, and +1 Culture on all Tundra tiles for this city.
					cultureFromTiles += 1.0

				# godOfTheOpenSky - +1 Culture from Pastures.
				if adjacentTile.improvement() == ImprovementType.pasture and \
					self.player.religion.pantheon() == PantheonType.godOfTheOpenSky:
					cultureFromTiles += 1.0

				# goddessOfFestivals - +1 Culture from Plantations.
				if adjacentTile.improvement() == ImprovementType.plantation and \
					self.player.religion.pantheon() == PantheonType.goddessOfFestivals:
					cultureFromTiles += 1.0

		return cultureFromTiles

	def _cultureFromGovernmentType(self) -> YieldValues:
		"""yields from government"""
		cultureFromGovernmentValue: YieldValues = YieldValues(value=0.0, percentage=0.0)

		# https://civilization.fandom.com/wiki/Autocracy_(Civ6)
		# +1 to all yields for each government building and Palace in a city.
		if self.player.government.currentGovernment() == GovernmentType.autocracy:
			cultureFromGovernmentValue += float(self.buildings.numberOfBuildingsOf(BuildingCategoryType.government))

		# thirdAlternative - +2 Culture and +4 Gold from each Research Lab, Military Academy, Coal Power Plant, 
		# Oil Power Plant, and Nuclear Power Plant.
		if self.player.government.hasCard(PolicyCardType.thirdAlternative):
			if self.buildings.hasBuilding(BuildingType.researchLab):
				cultureFromGovernmentValue += 2

			if self.buildings.hasBuilding(BuildingType.militaryAcademy):
				cultureFromGovernmentValue += 2

			if self.buildings.hasBuilding(BuildingType.coalPowerPlant):
				cultureFromGovernmentValue += 2

			if self.buildings.hasBuilding(BuildingType.oilPowerPlant):
				cultureFromGovernmentValue += 2

			if self.buildings.hasBuilding(BuildingType.nuclearPowerPlant):
				cultureFromGovernmentValue += 2

		# despoticPaternalism - +4 Loyalty per turn in cities with Governors.
		# BUT: -15% Science and -15% Culture in all cities without an established Governor.
		if self.player.government.hasCard(PolicyCardType.despoticPaternalism):
			if self.governor() is None:
				cultureFromGovernmentValue.percentage -= 0.15

		# monasticism - +75% Science in cities with a Holy Site.
		# BUT: -25% Culture in all cities.
		if self.player.government.hasCard(PolicyCardType.monasticism):
			cultureFromGovernmentValue.percentage -= 0.25

		return cultureFromGovernmentValue

	def _cultureFromDistricts(self, simulation):
		cultureFromDistricts: float = 0.0
		policyCardModifier: float = 1.0

		# yields from cards
		# aesthetics - +100 % Theater Square district adjacency bonuses.
		if self.player.government.hasCard(PolicyCardType.aesthetics):
			policyCardModifier += 1.0

		# meritocracy - Each city receives +1 Culture for each specialty District it constructs.
		if self.player.government.hasCard(PolicyCardType.meritocracy):
			cultureFromDistricts += 1.0 * float(self.districts.numberOfSpecialtyDistricts())

		# district
		if self.districts.hasDistrict(DistrictType.theaterSquare):
			theaterSquareLocation = self.locationOf(DistrictType.theaterSquare)

			for neighbor in theaterSquareLocation.neighbors():
				neighborTile = simulation.tileAt(neighbor)

				# Major bonus(+2 Culture) for each adjacent Wonder
				if neighborTile.feature().isNaturalWonder():
					cultureFromDistricts += 2.0 * policyCardModifier

				# Major bonus(+2 Culture) for each adjacent Water Park or Entertainment Complex district tile
				if neighborTile.district() == DistrictType.entertainmentComplex:
					cultureFromDistricts += 2.0 * policyCardModifier

				# Major bonus(+2 Culture) for each adjacent Pamukkale tile

				# Minor bonus (+½ Culture) for each adjacent district tile
				if neighborTile.district() != DistrictType.none:
					cultureFromDistricts += 0.5 * policyCardModifier

		# penBrushAndVoice + golden - +1 Culture per Specialty District for each city.
		if self.player.currentAge() == AgeType.golden and self.player.hasDedication(DedicationType.penBrushAndVoice):
			for districtType in list(DistrictType):
				if self.districts.hasDistrict(districtType):
					if districtType.isSpecialty():
						cultureFromDistricts += 1.0

		return cultureFromDistricts

	def _cultureFromBuildings(self):
		cultureFromBuildings: float = 0.0

		# gather yields from buildings
		for building in list(BuildingType):
			if self.buildings.hasBuilding(building):
				cultureFromBuildings += building.yields().culture

		# Monument: +1 additional Culture if city is at maximum Loyalty.
		if self.buildings.hasBuilding(BuildingType.monument) and self.loyaltyState() == LoyaltyState.loyal:
			cultureFromBuildings += 1

		return cultureFromBuildings

	def _cultureFromWonders(self, simulation):
		cultureFromWonders: float = 0.0
		locationOfColosseum: HexPoint = constants.invalidHexPoint

		for city in simulation.citiesOf(self.player):
			if city.hasWonder(WonderType.colosseum):
				locationOfColosseum = city.location

		# pyramids
		if self.hasWonder(WonderType.pyramids):
			# +2 Culture
			cultureFromWonders += 2.0

		# oracle
		if self.hasWonder(WonderType.oracle):
			# +1 Culture
			cultureFromWonders += 1.0

		# colosseum - +2 Culture for every city in 6 tiles
		if self.hasWonder(WonderType.colosseum) or locationOfColosseum.distance(self.location) <= 6:
			cultureFromWonders += 2.0

		return cultureFromWonders

	def _cultureFromPopulation(self) -> float:
		# science & culture from population
		return self._populationValue * 0.3

	def _cultureFromTradeRoutes(self, simulation):
		cultureFromTradeRoutes: float = 0.0

		tradeRoutes = self.player.tradeRoutes.tradeRoutesStartingAt(self)

		for tradeRoute in tradeRoutes:
			cultureFromTradeRoutes += tradeRoute.yields(simulation).culture

		return cultureFromTradeRoutes

	def _cultureFromGovernors(self):
		cultureFromGovernors: YieldValues = YieldValues(value=0.0, percentage=0.0)

		# connoisseur - +1 Culture per turn for each Citizen in the city.
		if self.hasGovernorTitle(GovernorTitle.connoisseur):
			cultureFromGovernors += YieldValues(value=float(self.population()))

		# 15% increase in Science and Culture generated by the city.
		if self.hasGovernorTitle(GovernorTitle.librarian):
			cultureFromGovernors += YieldValues(value=0.0, percentage=0.15)

		return cultureFromGovernors

	def _cultureFromEnvoys(self, simulation):
		cultureFromEnvoys: float = 0.0
		effects = self.player.envoyEffects(simulation)

		for effect in effects:
			# +2 Culture in the Capital.
			if effect.isEqual(category=CityStateCategory.cultural, at=EnvoyEffectLevel.first) and self.capitalValue:
				cultureFromEnvoys += 2.0

			# +2 Culture in every Amphitheater building.
			if effect.isEqual(category=CityStateCategory.cultural, at=EnvoyEffectLevel.third) and \
				self.buildings.hasBuilding(BuildingType.amphitheater):
				cultureFromEnvoys += 2.0

			# +2 Culture in every Art Museum and Archaeological Museum building.
			if effect.isEqual(category=CityStateCategory.cultural, at=EnvoyEffectLevel.sixth):
				raise Exception("not handled")
		# if self.has(building: .museum)
		# 	cultureFromEnvoys += 2.0
		#
		# if self.has(building: .arch)
		# 	cultureFromEnvoys += 2.0

		return cultureFromEnvoys

	def defensiveStrengthAgainst(self, unit, tile, ranged, simulation):
		strengthValue = 0

		# Base strength, equal to that of the strongest melee unit your civilization
		# currently possesses minus 10, or to the unit which is garrisoned inside
		# the city(whichever is greater). Note also that
		# Corps or Army units are capable of pushing this number higher than otherwise possible
		# for this Era, so when you station such a unit in a city, its CS will increase accordingly;
		if self.garrisonedUnit() is not None:
			unitStrength = self.garrisonedUnit().attackStrengthAgainst(unit=None, city=None, tile=None,
			                                                           simulation=simulation)
			warriorStrength = UnitType.warrior.meleeStrength() - 10
			strengthValue = max(warriorStrength, unitStrength)
		else:
			strengthValue = UnitType.warrior.meleeStrength() - 10

		# Building Defense
		# Wall defenses add + 3 CS per each level of Walls(up to + 9 for Renaissance Walls);
		# this bonus is lost if /when the walls are brought down.Note that this bonus is only valid for
		# 'ancient defenses' (i.e.pre-Urban Defenses Walls).If a city never built any walls and then got Urban Defenses,
		# it will never get this bonus, despite actually having modern defensive capabilities.

		# The Capital gains an additional boost of 3 CS thanks to its Palace; this is called "Palace Guard" in the
		# strength breakdown. This can increase to + 8 when Victor has moved to the city(takes 3 turns).
		buildingDefense = self.buildings.defense()
		strengthValue += buildingDefense

		# Terrain mod
		# Bonus if the city is built on a Hill; this is the normal + 3 bonus which is native to Hills.
		if tile is not None:
			if tile.isHills():
				strengthValue += 3  # CITY_STRENGTH_HILL_MOD

		# +6 City Defense Strength.
		if self.player.government.hasCard(PolicyCardType.bastions):
			strengthValue += 6

		# Increases city garrison Strength Combat Strength by + 5
		if self.hasGovernorTitle(GovernorTitle.redoubt):
			strengthValue += 5

		return strengthValue

	def garrisonedUnit(self) -> Optional[Unit]:
		return self._garrisonedUnitValue

	def setGarrison(self, unit):
		self._garrisonedUnitValue = unit

	def hasGarrison(self) -> bool:
		return self._garrisonedUnitValue is not None

	def maintenanceCostsPerTurn(self) -> float:
		costs = 0.0

		# gather costs from districts
		for district in list(DistrictType):
			if self.districts.hasDistrict(district):
				costs += float(district.maintenanceCost())

		# gather costs from buildings
		for building in list(BuildingType):
			if self.buildings.hasBuilding(building):
				costs += float(building.maintenanceCost())

		return costs

	def currentBuildableItem(self) -> Optional[BuildableItem]:
		return self._buildQueue.peek()

	def isProduction(self):
		if self._buildQueue.peek() is not None:
			return True

		return False

	def AI_chooseProduction(self, interruptWonders: bool, simulation):
		buildWonder = False

		# See if this is the one AI city that is supposed to be building wonders
		wonderBuildCity = self.player.citySpecializationAI.wonderBuildCity()
		if wonderBuildCity is not None and wonderBuildCity.location == self.location:
			# Is it still working on that wonder, and we don't want to interrupt it?
			if not interruptWonders:
				if self.productionWonderType() is not None:
					# Stay the course
					return

			# So we're the wonder building city but it is not underway yet...

			# Has the designated wonder been poached by another civ?
			(nextWonderType, nextWonderLocation) = self.player.citySpecializationAI.nextWonderDesired()
			if not self.canBuildWonder(nextWonderType, nextWonderLocation, simulation):
				# Reset city specialization
				# citySpecializationAI.->SetSpecializationsDirty(SPECIALIZATION_UPDATE_WONDER_BUILT_BY_RIVAL);
				raise Exception("need to trigger the selection of new wonder")
			else:
				buildWonder = True

		if buildWonder:
			(nextWonderType, nextWonderLocation) = self.player.citySpecializationAI.nextWonderDesired()
			self.startBuildingWonder(nextWonderType, nextWonderLocation, simulation)

			if simulation.getLogging() and simulation.getAILogging():
				print('bla bla bla')
		# CvString playerName;
		# FILogFile * pLog;
		# CvString strBaseString;
		# CvString strOutBuf;
		# m_pCityStrategyAI->LogCityProduction(buildable, false);
		# playerName = kOwner.getCivilizationShortDescription();
		# pLog = LOGFILEMGR.GetLog(kOwner.GetCitySpecializationAI()->GetLogFileName(playerName), FILogFile::kDontTimeStamp);
		# strBaseString.Format("%03d, ", GC.getGame().getElapsedGameTurns());
		# strBaseString += playerName + ", ";
		# strOutBuf.Format("%s, WONDER - Started %s, Turns: %d", getName().GetCString(),
		# GC.getBuildingInfo((BuildingTypes)buildable.m_iIndex)->GetDescription(), buildable.m_iTurnsToConstruct);
		# strBaseString += strOutBuf;
		# pLog->Msg(strBaseString);
		else:
			self.cityStrategy.chooseProduction(simulation)
			simulation.userInterface.updateCity(self)

		return

	def setFeatureProductionTo(self, value: float):
		self._featureProductionValue = value

	def isProductionAutomated(self) -> bool:
		return False

	def canBuildDistrict(self, districtType: DistrictType, location: Optional[HexPoint] = None, simulation=None):
		if districtType == DistrictType.none:
			return False

		if simulation is None:
			raise Exception('simulation cannot be None')

		if location is not None:
			tile = simulation.tileAt(location)

			# can't build districts in cities, wonders or other districts
			if tile.isCity() or tile.district() != DistrictType.none or tile.wonder() != WonderType.none:
				return False

			if tile.workingCity() is not None and tile.workingCity().location != self.location:
				return False

		requiredTech = districtType.requiredTech()
		if requiredTech is not None:
			if not self.player.hasTech(requiredTech):
				return False

		requiredCivic = districtType.requiredCivic()
		if requiredCivic is not None:
			if not self.player.hasCivic(requiredCivic):
				return False

		if districtType.isSpecialty():
			# specialty districts are limited by population
			if self.districts.numberOfSpecialtyDistricts() >= self.numberOfBuildableSpecialtyDistricts():
				return False

			# they can only be built once per city
			if self.districts.hasDistrict(districtType):
				return False

		if districtType.oncePerCivilization():
			for city in simulation.citiesOf(self.player):
				if city.districts.hasDistrict(districtType):
					return False

		if location is not None and not districtType.canBuildOn(location, simulation):
			return False

		return True

	def bestLocationForDistrict(self, districtType: DistrictType, simulation) -> Optional[HexPoint]:
		weightedLocations = WeightedBaseList()

		for loopLocation in self.cityCitizens.workingTileLocations():
			loopTile = simulation.tileAt(loopLocation)
			if loopTile.workingCity() is not None:
				if loopTile.workingCity().location != self.location:
					continue

			if districtType.canBuildOn(loopLocation, simulation):
				distance = loopLocation.distance(self.location)
				weightedLocations.addWeight(5.0 - distance, loopLocation)

		if len(weightedLocations.items()) == 0:
			return None

		# select one
		selectedIndex = random.randrange(100)

		weightedLocations = weightedLocations.top3()
		weightedLocationsArray = weightedLocations.distributeByWeight()
		selectedLocation = weightedLocationsArray[selectedIndex]

		return selectedLocation

	def numberOfBuildableSpecialtyDistricts(self) -> int:
		"""For example a city of 6 pop can only build 2 districts but 7 can build 3."""
		return int((int(self._populationValue) + 2) / 3)

	def canBuildBuilding(self, buildingType: BuildingType, simulation) -> bool:
		if buildingType == BuildingType.none:
			return False

		# at least one required building is needed( if there is one)
		hasOneRequiredBuilding = False
		for requiredBuilding in buildingType.requiredBuildings():
			if self.buildings.hasBuilding(requiredBuilding):
				hasOneRequiredBuilding = True

		if not len(buildingType.requiredBuildings()) == 0 and not hasOneRequiredBuilding:
			return False

		# if an obsolete building exists - this cant be built
		for obsoleteBuilding in buildingType.obsoleteBuildings():
			if self.buildings.hasBuilding(obsoleteBuilding):
				return False

		if not buildingType.canBuildIn(self, simulation):
			return False

		if self.buildings.hasBuilding(buildingType):
			return False

		requiredTech = buildingType.requiredTech()
		if requiredTech is not None:
			if not self.player.hasTech(requiredTech):
				return False

		requiredCivic = buildingType.requiredCivic()
		if requiredCivic is not None:
			if not self.player.hasCivic(requiredCivic):
				return False

		if not self.hasDistrict(buildingType.district()):
			return False

		# special handling of the palace
		# can only be built once
		if buildingType == BuildingType.palace and simulation.capitalOf(self.player) is not None:
			return False

		return True

	def canBuildWonder(self, wonderType: WonderType, location: Optional[HexPoint] = None, simulation=None) -> bool:
		if wonderType == WonderType.none:
			return False

		if simulation is None:
			raise Exception('simulation cannot be None')

		if location is not None:
			tile = simulation.tileAt(location)

			# can't build wonders in cities, districts or other wonders
			if tile.isCity() or tile.district() != DistrictType.none or tile.wonder() != WonderType.none:
				return False

			if tile.workingCity() is not None and tile.workingCity().location != self.location:
				return False

			# check tile
			if not wonderType.canBuildOn(location, simulation):
				return False

		# only major player can build wonders
		if not self.player.isHuman() and not self.player.isMajorAI():
			return False

		if self.wonders.hasWonder(wonderType):
			return False

		requiredTech = wonderType.requiredTech()
		if requiredTech is not None:
			if not self.player.hasTech(requiredTech):
				return False

		requiredCivic = wonderType.requiredCivic()
		if requiredCivic is not None:
			if not self.player.hasCivic(requiredCivic):
				return False

		# check other cities of user (if they are currently building)
		cities = simulation.citiesOf(self.player)

		# loop thru all cities but skip this city
		for loopCity in cities:
			if loopCity.location == self.location:
				continue

			if loopCity.buildQueue.isBuildingWonder(wonderType):
				return False

		# has another player built this wonder already?
		if simulation.alreadyBuiltWonder(wonderType):
			return False

		return True

	def buildingProductionTurnsLeftFor(self, buildingType: BuildingType) -> int:
		buildingTypeItem = self._buildQueue.buildingOf(buildingType)
		if buildingTypeItem is not None:
			return int(buildingTypeItem.productionLeftFor(self.player) / self.productionLastTurnValue)

		return 100

	def canTrainUnit(self, unitType: UnitType, simulation) -> bool:
		if unitType == UnitType.none:
			return False

		# city states cant build settlers or prophets
		if self.player.isCityState() and (unitType == UnitType.settler or unitType == UnitType.prophet):
			return False

		# filter great people
		if unitType.productionCost() < 0:
			return False

		requiredTech = unitType.requiredTech()
		if requiredTech is not None:
			if not self.player.hasTech(requiredTech):
				return False

		if unitType == UnitType.settler:
			if self.population() <= 1:
				return False

			# isolationism - Domestic routes provide +2 Food, +2 Production.
			# BUT: Can't train or buy Settlers nor settle new cities.
			if self.player.government.hasCard(PolicyCardType.isolationism):
				return False

		if unitType == UnitType.trader:
			if self.player.isCityState() or self.player.isBarbarian() or self.player.isFreeCity():
				return False

			if (self.player.numberOfTradeRoutes() + self.player.numberOfUnassignedTraders(
				simulation)) >= self.player.tradingCapacity():
				return False

		requiredCivilization = unitType.civilization()
		if requiredCivilization is not None:
			if self.player.leader.civilization() != requiredCivilization:
				return False

		# only coastal cities( or cities with harbors) can build ships
		if unitType.unitClass() == UnitClassType.navalMelee or unitType.unitClass() == UnitClassType.navalRanged or \
			unitType.unitClass() == UnitClassType.navalRaider or unitType.unitClass() == UnitClassType.navalCarrier:
			if not self.isCoastal(simulation) and not self.districts.hasDistrict(DistrictType.harbor):
				return False

		# check that enough resources are there
		resource = unitType.requiredResource()
		if resource is not None:
			if self.player.numberOfItemsInStockpile(resource) < 1:
				return False

		return True

	def unitProductionTurnsLeftFor(self, unitType: UnitType) -> int:
		unitTypeItem = self._buildQueue.unitOf(unitType)
		if unitTypeItem is not None:
			return int(unitTypeItem.productionLeftFor(self.player) / self.productionLastTurnValue)

		return 100

	def bestLocationForWonder(self, wonderType: WonderType, simulation) -> Optional[HexPoint]:
		for loopLocation in self.cityCitizens.workingTileLocations():
			if wonderType.canBuildOn(loopLocation, simulation):
				return loopLocation

		return None

	def startTrainingUnit(self, unitType: UnitType):
		self._buildQueue.append(BuildableItem(unitType))

	def startBuildingBuilding(self, buildingType: BuildingType):
		self._buildQueue.append(BuildableItem(buildingType))

	def startBuildingWonder(self, wonderType: WonderType, location: HexPoint, simulation):
		tile = simulation.tileAt(location)

		tile.startBuildingWonder(wonderType)
		simulation.userInterface.refreshTile(tile)

		self._buildQueue.append(BuildableItem(wonderType, location))

		# send gossip
		simulation.sendGossip(GossipType.wonderStarted, wonder=wonderType, cityName=self.name, player=self.player)

	def startBuildingDistrict(self, districtType: DistrictType, location: HexPoint, simulation):
		tile = simulation.tileAt(location)

		tile.startBuildingDistrict(districtType)
		simulation.userInterface.refreshTile(tile)

		self._buildQueue.append(BuildableItem(districtType, location))

	def startBuildingProject(self, projectType: ProjectType, location: HexPoint, simulation):
		self._buildQueue.append(BuildableItem(projectType, location))

	def updateProduction(self, productionPerTurn: float, simulation):
		currentBuilding = self.currentBuildableItem()
		if currentBuilding is not None:
			currentBuilding.addProduction(productionPerTurn)

			if currentBuilding.ready(self.player):
				self._buildQueue.pop()

				if currentBuilding.buildableType == BuildableType.unit:
					unitType: UnitType = currentBuilding.unitType
					self.trainUnit(unitType, simulation)

				elif currentBuilding.buildableType == BuildableType.building:
					buildingType: BuildingType = currentBuilding.buildingType
					self.buildBuilding(buildingType, simulation)

				elif currentBuilding.buildableType == BuildableType.wonder:
					wonderType: WonderType = currentBuilding.wonderType,
					wonderLocation = currentBuilding.location
					self.buildWonder(wonderType, wonderLocation, simulation)

				elif currentBuilding.buildableType == BuildableType.district:
					districtType: DistrictType = currentBuilding.districtType,
					districtLocation = currentBuilding.location
					self.buildDistrict(districtType, districtLocation, simulation)

				elif currentBuilding.buildableType == BuildableType.project:
					# NOOP - FIXME
					pass

				self.player.doUpdateTradeRouteCapacity(simulation)

				if self.player.isHuman():
					self.player.notifications.addNotification(NotificationType.productionNeeded, cityName=self.name, location=self.location)
				else:
					self.cityStrategy.chooseProduction(simulation)

		else:
			if self.player.isHuman():
				self.player.notifications.addNotification(NotificationType.productionNeeded, cityName=self.name, location=self.location)
			else:
				self.cityStrategy.chooseProduction(simulation)

		self._productionLastTurnValue = productionPerTurn

	def productionWonderType(self) -> Optional[WonderType]:
		currentProduction = self._buildQueue.peek()
		if currentProduction is not None:
			if currentProduction.buildableType == BuildableType.wonder:
				return currentProduction.wonderType

		return None

	def canBuildProject(self, projectType: ProjectType) -> bool:
		return False

	def isFeatureSurrounded(self) -> bool:
		return self._isFeatureSurroundedValue

	def updateFeatureSurrounded(self, simulation):
		totalPlots = 0
		featuredPlots = 0

		# Look two tiles around this city in every direction to see if at least half the plots are covered in a
		# removable feature
		range = City.workRadius

		surroundingArea = self.location.areaWithRadius(range)

		for pt in surroundingArea:

			if not simulation.valid(pt):
				continue

			# Increase total plot count
			totalPlots += 1

			tile = simulation.tileAt(pt)
			if tile is not None:
				hasRemovableFeature = False
				for feature in list(FeatureType):
					if tile.hasFeature(feature) and feature.isRemovable():
						hasRemovableFeature = True

				if hasRemovableFeature:
					featuredPlots += 1

		# At least half have coverage?
		if featuredPlots >= totalPlots / 2:
			self._isFeatureSurroundedValue = True
		else:
			self._isFeatureSurroundedValue = False

		return

	def cleanUpQueue(self, simulation) -> bool:
		"""remove items in the queue that are no longer valid"""
		okay = True

		for buildItem in self._buildQueue:
			if not self.canContinueProductionItem(buildItem, simulation):
				self.buildQueue.removeItem(buildItem)
				okay = False

		return okay

	def locationOfDistrict(self, district: DistrictType) -> Optional[HexPoint]:
		if district == DistrictType.cityCenter:
			return self.location

		return self.districts.locationOfDistrict(district)

	def setEverCapitalTo(self, value):
		self.everCapitalValue = value

	def canContinueProductionItem(self, buildItem: BuildableItem, simulation) -> bool:
		if buildItem.buildableType == BuildableType.unit:
			return self.canTrainUnit(buildItem.unitType, simulation)
		elif buildItem.buildableType == BuildableType.building:
			return self.canBuildBuilding(buildItem.buildingType, simulation)
		elif buildItem.buildableType == BuildableType.wonder:
			return self.canBuildWonder(buildItem.wonderType, buildItem.location, simulation)
		elif buildItem.buildableType == BuildableType.district:
			return self.canBuildDistrict(buildItem.districtType, buildItem.location, simulation)
		elif buildItem.buildableType == BuildableType.project:
			return self.canBuildProject(buildItem.projectType)

		return False

	def trainUnit(self, unitType: UnitType, simulation):
		unitLocation = self.location

		if unitType.domain() == UnitDomainType.sea:
			if not self.isCoastal(simulation) and self.districts.hasDistrict(DistrictType.harbor):
				harborLocation = self.districts.locationOfDistrict(DistrictType.harbor)
				unitLocation = harborLocation

		unit = Unit(unitLocation, unitType, self.player)
		secondUnit: Optional[Unit] = None

		if self.hasWonder(WonderType.venetianArsenal) and unitType.domain() == UnitDomainType.sea:
			# Receive a second naval unit each time you train a naval unit.
			secondUnit = Unit(unitLocation, unitType, self.player)

		if unitType == UnitType.settler:
			self.player.changeTrainedSettlersBy(1)

			if self.population() <= 1:
				print("cannot train settler if only 1 people left")
				return

			settlerWillReducePopulation: bool = True

			governor = self.governor()
			if governor is not None:
				# magnus - provision - Settlers trained in the city do not consume a Citizen Population.
				if governor.type == GovernorType.magnus and governor.hasTitle(GovernorTitle.provision):
					settlerWillReducePopulation = False

			if settlerWillReducePopulation:
				self.setPopulation(self.population() - 1, True, simulation)

		elif unitType == UnitType.builder:
			governor = self.governor()
			if governor is not None:
				# Guildmaster - All Builders trained in city get +1 build charge.
				if governor.hasTitle(GovernorTitle.guildmaster):
					unit.changeBuildChargesBy(1)

			# serfdom - Newly trained Builders gain 2 extra build actions.
			if self.player.government.hasCard(PolicyCardType.serfdom):
				unit.changeBuildChargesBy(2)

		experienceModifier: float = 0.0

		# +25 % combat experience for all melee, ranged and anti - cavalry land units trained in this city.
		if self.buildings.hasBuilding(BuildingType.barracks) and \
			(unitType.unitClass() == UnitClassType.melee or unitType.unitClass() == UnitClassType.ranged or
			 unitType.unitClass() == UnitClassType.antiCavalry):
			experienceModifier += 0.25

		# +25 % combat experience for all cavalry and siege class units trained in this city.
		if self.buildings.hasBuilding(BuildingType.stable) and \
			(unitType.unitClass() == UnitClassType.lightCavalry or unitType.unitClass() == UnitClassType.heavyCavalry or
			 unitType.unitClass() == UnitClassType.siege):
			experienceModifier += 0.25

		# +25% combat experience for all naval units trained in this city.
		if self.buildings.hasBuilding(BuildingType.barracks) and \
			(unitType.unitClass() == UnitClassType.navalMelee or unitType.unitClass() == UnitClassType.navalRaider or
			 unitType.unitClass() == UnitClassType.navalRaider or unitType.unitClass() == UnitClassType.navalCarrier):
			experienceModifier += 0.25

		# +25 % combat experience for all military land units trained in this city
		if self.buildings.hasBuilding(BuildingType.armory):
			experienceModifier += 0.25

		# +25 % combat experience for all naval units trained in this city.
		if self.buildings.hasBuilding(BuildingType.shipyard):
			experienceModifier += 0.25

		# consume strategic resource
		resource = unitType.requiredResource()
		if resource is not None:
			cost = 1.0

			governor: Governor = self.governor()
			if governor is not None:
				# blackMarketeer - Strategic resources for units are discounted 80%.
				if governor.hasTitle(GovernorTitle.blackMarketeer):
					cost -= 0.8

			self.player.changeNumberOfItemsInStockpileOf(resource, -cost)

		unit.setExperienceModifier(experienceModifier)
		if secondUnit is not None:
			secondUnit.setExperienceModifier(experienceModifier)

		# Victor - embrasure - Military units trained in this city start with a free promotion that do not already
		# start with a free promotion.
		governor = self.governor()
		if governor is not None:
			if governor.type == GovernorType.victor and governor.hasTitle(GovernorTitle.embrasure):
				if len(unit.gainedPromotions()) == 0:
					unit.changeExperienceUntilPromotion(simulation)

				if secondUnit is not None:
					if len(secondUnit.gainedPromotions()) == 0:
						secondUnit.changeExperienceUntilPromotion(simulation)

		simulation.addUnit(unit)
		simulation.userInterface.showUnit(unit, unitLocation)

		if secondUnit is not None:
			simulation.addUnit(secondUnit)
			simulation.userInterface.showUnit(secondUnit, unitLocation)

		# send gossip
		if unitType == UnitType.settler:
			simulation.sendGossip(GossipType.settlerTrained, cityName=self.name, player=self.player)

		self.updateEurekas(simulation)

		# check quests
		# for quest in self.player.ownQuests(simulation):
		# 	if quest.type == QuestType.trainUnit(type: unitType) & & quest.leader == player.leader
		# 	cityStatePlayer = gameModel?.cityStatePlayer(for: quest.cityState)
		# 	cityStatePlayer?.fulfillQuest(by: player.leader, in: gameModel)

		return

	def buildBuilding(self, buildingType: BuildingType, simulation):
		self.buildings.build(buildingType)
		self.updateEurekas(simulation)

		# penBrushAndVoice + normal - construct a building with a Great Work slot.
		if self.player.currentAge() == AgeType.normal and self.player.hasDedication(DedicationType.penBrushAndVoice):
			if len(buildingType.slotsForGreatWork()) != 0:
				self.player.addMoment(MomentType.dedicationTriggered, dedication=DedicationType.penBrushAndVoice,
				                      simulation=simulation)

		# freeInquiry + normal - constructing a building which provides Science
		if self.player.currentAge() == AgeType.normal and self.player.hasDedication(DedicationType.freeInquiry):
			if buildingType.yields().science > 0:
				self.player.addMoment(MomentType.dedicationTriggered, dedication=DedicationType.freeInquiry,
				                      simulation=simulation)

		if buildingType == BuildingType.warlordsThrone or buildingType == BuildingType.audienceChamber or \
			buildingType == BuildingType.ancestralHall or buildingType == BuildingType.foreignMinistry or \
			buildingType == BuildingType.grandMastersChapel or buildingType == BuildingType.intelligenceAgency:
			# Awards + 1 Governor Title.
			self.player.addGovernorTitle()

		self.greatWorks.addPlacesFor(buildingType)

		# send gossip
		simulation.sendGossip(GossipType.buildingConstructed, building=buildingType, player=self.player)

		# update district tile
		cityCitizens = self.cityCitizens

		for loopPoint in cityCitizens._workingPlots:
			loopTile = simulation.tileAt(loopPoint.location)

			if loopTile.district() == buildingType.district():
				simulation.userInterface.refreshTile(loopTile)

		# update city tile
		if buildingType.district() == DistrictType.cityCenter:
			cityTile = simulation.tileAt(self.location)
			simulation.userInterface.refreshTile(cityTile)

		# check for improving city tutorial
		if simulation.tutorial() == Tutorials.improvingCity and self.player.isHuman():
			if int(self._populationValue) >= Tutorials.citizenInCityNeeded() and \
				self.buildings.hasBuilding(BuildingType.granary) and self.buildings.hasBuilding(BuildingType.monument):
				simulation.userInterface.finishTutorial(Tutorials.improvingCity)
				simulation.enableTutorial(Tutorials.none)

		return

	def isCoastal(self, simulation) -> bool:
		return simulation.isCoastalAt(self.location)
