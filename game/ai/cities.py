import random
from typing import Union, Optional

from game.buildings import BuildingType
from game.districts import DistrictType
from game.flavors import Flavors, FlavorType
from game.projects import ProjectType
from game.unitTypes import UnitTaskType, UnitType
from game.wonders import WonderType
from map.base import HexPoint
from map.types import YieldType
from utils.base import ExtendedEnum, InvalidEnumError, WeightedBaseList


class CitySpecializationType(ExtendedEnum):
	none = 'none'

	productionWonder = 'productionWonder'
	generalEconomic = 'generalEconomic'


class CityStrategyType(ExtendedEnum):
	pass


class WeightedFlavorList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for flavorType in list(FlavorType):
			if flavorType == FlavorType.none:
				continue

			self.setWeight(0.0, flavorType)


class WeightedYieldList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for yieldType in list(YieldType):
			if yieldType == YieldType.none:
				continue

			self.setWeight(0.0, yieldType)


class CityStrategyAdoptionItem:
	def __init__(self, cityStrategyType: CityStrategyType, adopted: bool, turnOfAdoption: int):
		self.cityStrategyType = cityStrategyType
		self.adopted = adopted
		self.turnOfAdoption = turnOfAdoption


class CityStrategyAdoptions:
	def __init__(self):
		self.adoptions = []

		for cityStrategyType in list(CityStrategyType):
			self.adoptions.append(CityStrategyAdoptionItem(cityStrategyType, False, -1))

	def adopted(self, cityStrategyType: CityStrategyType) -> bool:
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			return item.adopted

		raise InvalidEnumError(cityStrategyType)

	def turnOfAdoption(self, cityStrategyType: CityStrategyType) -> int:
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			return item.turnOfAdoption

		raise InvalidEnumError(cityStrategyType)

	def adopt(self, cityStrategyType: CityStrategyType, turnOfAdoption: int):
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			item.adopted = True
			item.turnOfAdoption = turnOfAdoption
			return

		raise InvalidEnumError(cityStrategyType)

	def abandon(self, cityStrategyType: CityStrategyType):
		item = next((adoptionItem for adoptionItem in self.adoptions if
					 adoptionItem.cityStrategyType == cityStrategyType), None)

		if item is not None:
			item.adopted = False
			item.turnOfAdoption = -1
			return

		raise InvalidEnumError(cityStrategyType)


class BuildingWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for buildingType in list(BuildingType):
			self.addWeight(0.0, buildingType)


class DistrictWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for districtType in list(DistrictType):
			self.addWeight(0.0, districtType)


class BuildingProductionAI:
	def __init__(self, player):
		self.player = player

		self.buildingWeights = BuildingWeights()
		self.districtWeights = DistrictWeights()

		self.initWeights()

	def weight(self, itemType: Union[DistrictType, BuildingType]) -> float:
		if isinstance(itemType, DistrictType):
			return self.districtWeights.weight(itemType)
		elif isinstance(itemType, BuildingType):
			return self.buildingWeights.weight(itemType)

		raise InvalidEnumError(itemType)

	def initWeights(self):
		for flavorType in list(FlavorType):
			if flavorType == FlavorType.none:
				continue

			leaderFlavor = self.player.personalAndGrandStrategyFlavor(flavorType)

			for buildingType in list(BuildingType):
				buildingFlavor = buildingType.flavor(flavorType)
				self.buildingWeights.addWeight(buildingFlavor * leaderFlavor, buildingType)

			for districtType in list(DistrictType):
				districtFlavor = districtType.flavor(flavorType)
				self.districtWeights.addWeight(districtFlavor * leaderFlavor, districtType)

		return

	def reset(self):
		self.buildingWeights.reset()
		self.districtWeights.reset()


class UnitWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for unitType in list(UnitType):
			self.addWeight(0.0, unitType)

	def reset(self):
		self.removeAll()
		for unitType in list(UnitType):
			self.addWeight(0.0, unitType)


class UnitProductionAI:
	def __init__(self):
		self.unitWeights = UnitWeights()

	def addWeight(self, weight: int, flavorType: FlavorType):
		for unitType in list(UnitType):
			unitWeight = self.unitWeights.weight(unitType)

			flavor = next(filter(lambda flavorIterator: flavorIterator.flavorType == flavorType, unitType.flavors()), None)
			if flavor is not None:
				self.unitWeights.setWeight(flavor.value * weight, unitType)

		return

	def weight(self, unitType: UnitType) -> float:
		return self.unitWeights.weight(unitType)


class WonderWeights(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for wonderType in list(WonderType):
			self.addWeight(0.0, wonderType)


class WonderProductionAI:
	def __init__(self, player):
		self.player = player
		self.wonderWeights = WonderWeights()

	def weight(self, wonderType: WonderType) -> float:
		return self.wonderWeights.weight(wonderType)


class BuildableItemWeights(WeightedBaseList):
	pass


class BuildableType(ExtendedEnum):
	district = 'district'
	building = 'building'
	wonder = 'wonder'
	project = 'project'
	unit = 'unit'


class BuildableItem:
	def __init__(self, item: Union[DistrictType, BuildingType, WonderType, UnitType, ProjectType],
				 location: Optional[HexPoint] = None):
		if isinstance(item, DistrictType):
			self.buildableType = BuildableType.district
			self.districtType = item
			self.buildingType = None
			self.unitType = None
			self.wonderType = None
			self.projectType = None
			self.location = location
			self.production = 0.0
		elif isinstance(item, BuildingType):
			self.buildableType = BuildableType.building
			self.districtType = None
			self.buildingType = item
			self.unitType = None
			self.wonderType = None
			self.projectType = None
			self.location = None  # buildings don't need a location
			self.production = 0.0
		elif isinstance(item, UnitType):
			self.buildableType = BuildableType.unit
			self.districtType = None
			self.buildingType = None
			self.unitType = item
			self.wonderType = None
			self.projectType = None
			self.location = None  # units don't need a location
			self.production = 0.0
		elif isinstance(item, WonderType):
			self.buildableType = BuildableType.wonder
			self.districtType = None
			self.buildingType = None
			self.unitType = None
			self.wonderType = item
			self.projectType = None
			self.location = location
			self.production = 0.0
		elif isinstance(item, ProjectType):
			self.buildableType = BuildableType.project
			self.districtType = None
			self.buildingType = None
			self.unitType = None
			self.wonderType = None
			self.projectType = item
			self.location = location
			self.production = 0.0
		else:
			raise Exception(f'unsupported buildable type: {type(item)}')

	def __repr__(self):
		if self.buildableType == BuildableType.district:
			return f'BuildableItem(BuildableType.district, {self.districtType}, {self.location})'
		elif self.buildableType == BuildableType.building:
			return f'BuildableItem(BuildableType.building, {self.buildingType})'
		elif self.buildableType == BuildableType.unit:
			return f'BuildableItem(BuildableType.unit, {self.unitType})'
		elif self.buildableType == BuildableType.wonder:
			return f'BuildableItem(BuildableType.wonder, {self.wonderType}, {self.location})'
		elif self.buildableType == BuildableType.project:
			return f'BuildableItem(BuildableType.project, {self.projectType})'

		raise Exception(f'unsupported buildable type: {self.buildableType}')

	def addProduction(self, productionDelta: float):
		self.production += productionDelta

	def productionLeft(self, player) -> float:

		if self.buildableType == BuildableType.unit:
			unitType = self.unitType
			return float(player.productionCostOfUnit(unitType)) - self.production

		elif self.buildableType == BuildableType.building:
			buildingType = self.buildingType
			return float(buildingType.productionCost()) - self.production

		elif self.buildableType == BuildableType.wonder:
			wonderType = self.wonderType
			return float(wonderType.productionCost()) - self.production

		elif self.buildableType == BuildableType.district:
			districtType = self.districtType
			return float(districtType.productionCost()) - self.production

		elif self.buildableType == BuildableType.project:
			projectType = self.projectType
			return float(projectType.productionCost()) - self.production

	def ready(self, player) -> bool:
		return self.productionLeft(player) <= 0


class CityStrategyAI:
	"""
		++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
		CLASS:      CvCityStrategyAI
		!  brief        Manages operations for a single city in the game world

		!  Key Attributes:
		!  - One instance for each city
		!  - Receives instructions from other AI components (usually as flavor changes) to
		!    specialize, switch production, etc.
		!  - Oversees both the city governor AI and the AI managing what the city is building
		++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	"""

	def __init__(self, city):
		self.city = city

		self.cityStrategyAdoption = CityStrategyAdoptions()
		self.flavors = Flavors()
		self.focusYield = YieldType.none

		self.buildingProductionAI = BuildingProductionAI(city.player)
		self.unitProductionAI = UnitProductionAI()
		self.wonderProductionAI = WonderProductionAI(city.player)

		self.specializationValue = CitySpecializationType.generalEconomic
		self.defaultSpecializationValue = CitySpecializationType.generalEconomic
		self.flavorWeights = WeightedFlavorList()
		self.bestYieldAverage = WeightedYieldList()
		self.yieldDeltaValue = WeightedYieldList()

	def doTurn(self, simulation):
		for cityStrategyType in list(CityStrategyType):
			# Minor Civs can't run some Strategies
			# if self.city.player.isCityState():
			#	cont

			# check tech
			requiredTech = cityStrategyType.required()
			isTechGiven = True if requiredTech is None else self.city.player.hasTech(requiredTech)
			obsoleteTech = cityStrategyType.obsolete()
			isTechObsolete = False if obsoleteTech is None else self.city.player.hasTech(obsoleteTech)

			# Do we already have this CityStrategy adopted?
			shouldCityStrategyStart = True
			if self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType):
				shouldCityStrategyStart = False
			elif not isTechGiven:
				shouldCityStrategyStart = False

			shouldCityStrategyEnd = False
			if self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType):
				# If Strategy is Permanent we can't ever turn it off
				if not cityStrategyType.permanent():
					if cityStrategyType.checkEachTurns() > 0:
						# Is it a turn where we want to check to see if this Strategy is maintained?
						if simulation.currentTurn - self.cityStrategyAdoption.turnOfAdoption(cityStrategyType) % cityStrategyType.checkEachTurns() == 0:
							shouldCityStrategyEnd = True

					if shouldCityStrategyEnd and cityStrategyType.minimumAdoptionTurns() > 0:
						# Has the minimum  # of turns passed for this Strategy?
						if simulation.currentTurn < self.cityStrategyAdoption.turnOfAdoption(cityStrategyType) + cityStrategyType.minimumAdoptionTurns():
							shouldCityStrategyEnd = False

			# Check CityStrategy Triggers
			# Functionality and existence of specific CityStrategies is hardcoded here, but data is stored in XML so it's easier to modify
			if shouldCityStrategyStart or shouldCityStrategyEnd:
				# Has the Tech which obsoletes this Strategy? If so, Strategy should be deactivated regardless of other factors
				strategyShouldBeActive = False

				# Strategy isn't obsolete, so test triggers as normal
				if not isTechObsolete:
					strategyShouldBeActive = cityStrategyType.shouldBeActiveFor(self.city, simulation)

				# This variable keeps track of whether or not we should be doing something(i.e.Strategy is active now but should be turned off, OR Strategy is inactive and should be enabled)
				bAdoptOrEndStrategy = False

				# Strategy should be on, and if it's not, turn it on
				if strategyShouldBeActive:
					if shouldCityStrategyStart:
						bAdoptOrEndStrategy = True
					elif shouldCityStrategyEnd:
						bAdoptOrEndStrategy = False

				# Strategy should be off, and if it's not, turn it off
				else:
					if shouldCityStrategyStart:
						bAdoptOrEndStrategy = False
					elif shouldCityStrategyEnd:
						bAdoptOrEndStrategy = True

				if bAdoptOrEndStrategy:
					if shouldCityStrategyStart:
						self.cityStrategyAdoption.adopt(cityStrategyType=cityStrategyType, turnOfAdoption=simulation.currentTurn)
					elif shouldCityStrategyEnd:
						self.cityStrategyAdoption.abandon(cityStrategyType=cityStrategyType)

		self.updateFlavors()

	def adopted(self, cityStrategyType: CityStrategyType) -> bool:
		return self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType)

	def specialization(self) -> CitySpecializationType:
		return self.specializationValue

	def updateFlavors(self):
		self.flavors.reset()

		for cityStrategyType in list(CityStrategyType):
			if self.cityStrategyAdoption.adopted(cityStrategyType=cityStrategyType):
				for cityStrategyTypeFlavor in cityStrategyType.flavorModifiers():
					self.flavors += cityStrategyTypeFlavor

		# FIXME: inform sub AI
		for flavorType in list(FlavorType):
			flavorValue = self.flavors.value(flavorType)

			# limit
			if flavorValue < 0:
				flavorValue = 0

			self.unitProductionAI.addWeight(flavorValue, flavorType)

	def chooseProduction(self, simulation):
		if simulation is None:
			raise Exception('simulation must not be None')
		unitsOfPlayer = simulation.unitsOf(self.city.player)
		buildables = BuildableItemWeights()
		settlersOnMap = sum(map(lambda unit: 1 if unit.task() == UnitTaskType.settle else 0, unitsOfPlayer))

		# Check units for operations first
		# FIXME

		# Loop through adding the available districts
		for districtType in list(DistrictType):
			if districtType == DistrictType.none or districtType == DistrictType.cityCenter:
				continue

			if self.city.canBuildDistrict(districtType, simulation=simulation):
				weight: float = float(self.buildingProductionAI.weight(districtType))
				bestDistrictLocation = self.city.bestLocationForDistrict(districtType, simulation)

				if bestDistrictLocation is None:
					raise Exception(f'District {districtType} need a location')

				if self.city.canBuildDistrict(districtType, bestDistrictLocation, simulation):
					buildableItem = BuildableItem(districtType, bestDistrictLocation)
					# re-weight ?
					buildables.addWeight(weight, buildableItem)

		# Loop through adding the available buildings
		for buildingType in list(BuildingType):
			if self.city.canBuildBuilding(buildingType, simulation):
				weight: float = float(self.buildingProductionAI.weight(buildingType))
				buildableItem = BuildableItem(buildingType)

				# re-weight
				turnsLeft = self.city.buildingProductionTurnsLeftFor(buildingType)
				totalCostFactor = 0.15 + 0.004 * float(turnsLeft)  # AI_PRODUCTION_WEIGHT_BASE_MOD / AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
				weightDivisor = pow(float(turnsLeft), totalCostFactor)
				weight /= weightDivisor

				buildables.addWeight(weight, buildableItem)

		# Loop through adding the available units
		for unitType in list(UnitType):
			if self.city.canTrainUnit(unitType, simulation):
				weight = float(self.unitProductionAI.weight(unitType))
				buildableItem = BuildableItem(unitType)

				# re-weight
				turnsLeft = self.city.unitProductionTurnsLeftFor(unitType)
				totalCostFactor = 0.15 + 0.004 * float(turnsLeft)  # AI_PRODUCTION_WEIGHT_BASE_MOD / AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
				weightDivisor = pow(float(turnsLeft), totalCostFactor)
				weight = float(weight) / weightDivisor

				if unitType.defaultTask() == UnitTaskType.settle:
					if settlersOnMap >= 2:
						weight = 0.0
					else:
						# FIXME: check settle areas
						pass


				buildables.addWeight(weight, buildableItem)

		# Loop through adding the available wonders
		for wonderType in list(WonderType):
			if self.city.canBuildWonder(wonderType, location=None, simulation=simulation):
				weight: float = float(self.wonderProductionAI.weight(wonderType))
				bestWonderLocation = self.city.bestLocationForWonder(wonderType, simulation)

				if bestWonderLocation is None:
					raise Exception("cant get valid wonder location")

				if self.city.canBuildWonder(wonderType, bestWonderLocation, simulation):
					buildableItem = BuildableItem(wonderType, bestWonderLocation)

					# re-weight
					turnsLeft = self.city.wonderProductionTurnsLeftFor(wonderType)
					totalCostFactor = 0.15 + 0.004 * float(turnsLeft)  # AI_PRODUCTION_WEIGHT_BASE_MOD / AI_PRODUCTION_WEIGHT_MOD_PER_TURN_LEFT
					weightDivisor = pow(float(turnsLeft), totalCostFactor)
					weight /= weightDivisor

					buildables.addWeight(weight, buildableItem)

		# Loop through adding the available projects
		for projectType in list(ProjectType):
			if self.city.canBuildProject(projectType):
				# FIXME
				pass

		# select one
		selectedIndex = random.randrange(100)

		weightedBuildable = buildables.top3()
		weightedBuildableArray = weightedBuildable.distributeByWeight()
		selectedBuildable = weightedBuildableArray[selectedIndex]

		if selectedBuildable is not None:
			if selectedBuildable.buildableType == BuildableType.unit:
				unitType = selectedBuildable.unitType
				if unitType is not None:
					self.city.startTrainingUnit(unitType)

			elif selectedBuildable.buildableType == BuildableType.building:
				buildingType = selectedBuildable.buildingType
				if buildingType is not None:
					self.city.startBuildingBuilding(buildingType)

			elif selectedBuildable.buildableType == BuildableType.wonder:
				wonderType = selectedBuildable.wonderType
				wonderLocation = selectedBuildable.location
				if wonderType is not None and wonderLocation is not None:
					self.city.startBuildingWonder(wonderType, wonderLocation, simulation)

			elif selectedBuildable.buildableType == BuildableType.district:
				districtType = selectedBuildable.districtType
				districtLocation = selectedBuildable.location
				if districtType is not None and districtLocation is not None:
					self.city.startBuildingDistrict(districtType, districtLocation, simulation)

			elif selectedBuildable.buildableType == BuildableType.project:
				projectType = selectedBuildable.projectType
				projectLocation = selectedBuildable.location
				if projectType is not None and projectLocation is not None:
					self.city.startBuildingProject(projectType, projectLocation, simulation)

		return
