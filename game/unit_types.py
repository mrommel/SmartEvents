from enum import Enum

from game.types import EraType, TechType
from map.types import MovementType, RouteType, FeatureType
from utils.base import ExtendedEnum, InvalidEnumError
from utils.translation import gettext_lazy as _


class ImprovementType(Enum):
	NONE = 0

	MINE = 1
	plantation = 2
	FARM = 3
	mine = 4
	quarry = 5
	camp = 6
	fishingBoats = 7
	pasture = 8


class BuildTypeData:
	# noinspection PyShadowingNames
	def __init__(self, name: str, repair: bool=False, required: TechType=None, era: EraType=None, improvement: ImprovementType=None, route: RouteType=None, removeRoad: bool = False, duration: int = 0, isWater: bool = True):
		"""

		:type required: object
		"""
		self.name = name
		self.repair = repair
		self.required = required
		self.era = era
		self.improvement = improvement
		self.route = route
		self.removeRoad = removeRoad
		self.duration = duration
		self.isWater = isWater
		self.featureBuilds = []
		self.featuresKept = []


class FeatureBuild:
	def __init__(self, featureType: FeatureType, required: TechType, production: int, duration: int, isRemove: bool):
		self.featureType = featureType
		self.required = required
		self.production = production
		self.duration = duration
		self.isRemove = isRemove


class BuildType(ExtendedEnum):
	NONE = 0

	REMOVE_RAINFOREST = 1
	REMOVE_MARSH = 2
	REMOVE_FOREST = 3
	REPAIR = 4
	MINE = 5
	ANCIENT_ROAD = 6
	CLASSICAL_ROAD = 7
	REMOVE_ROAD = 8
	fishingBoats = 9
	camp = 10
	FARM = 11
	QUARRY = 12
	plantation = 13
	pasture = 14

	def canRemove(self, feature: FeatureType) -> bool:
		featureBuild = next((build for build in self._data().featureBuilds if build.featureType == feature), None)

		if featureBuild is not None:
			return featureBuild.isRemove

		return False

	def _data(self) -> BuildTypeData:
		if self == BuildType.NONE:
			return BuildTypeData(
				name="None",
				duration=0
			)
		elif self == BuildType.REPAIR:
			return BuildTypeData(
				name="Repair",
				repair=True,
				duration=300
			)

		elif self == BuildType.ANCIENT_ROAD:
			return BuildTypeData(
				name="Road",
				era=EraType.ANCIENT,
				route=RouteType.ancientRoad,
				duration=300
			)

		elif self == BuildType.CLASSICAL_ROAD:
			return BuildTypeData(
				name="Road",
				era=EraType.CLASSICAL,
				route=RouteType.classicalRoad,
				duration=300
			)
		elif self == BuildType.REMOVE_ROAD:
			return BuildTypeData(
				name="Remove Road",
				required=TechType.wheel,
				removeRoad=True,
				duration=300
			)
		elif self == BuildType.FARM:
			farmBuild = BuildTypeData(
				name="Farm",
				improvement=ImprovementType.FARM,
				duration=600
			)

			farmBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.rainforest,
					required=TechType.bronzeWorking,
					production=0,
					duration=600,
					isRemove=True
				)
			)
			farmBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.forest,
					required=TechType.mining,
					production=20,
					duration=300,
					isRemove=True
				)
			)
			farmBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.marsh,
					required=TechType.masonry,
					production=0,
					duration=500,
					isRemove=True
				)
			)

			farmBuild.featuresKept.append(FeatureType.floodplains)

			return farmBuild
		elif self == BuildType.MINE:
			mineBuild = BuildTypeData(
				name="Mine",
				required=TechType.mining,
				improvement=ImprovementType.mine,
				duration=600
			)

			mineBuild.featuresKept.append(FeatureType.forest)
			mineBuild.featuresKept.append(FeatureType.rainforest)
			mineBuild.featuresKept.append(FeatureType.marsh)
			mineBuild.featuresKept.append(FeatureType.oasis)

			return mineBuild
		elif self == BuildType.QUARRY:
			quarryBuild = BuildTypeData(
				name="Quarry",
				required=TechType.mining,
				improvement=ImprovementType.quarry,
				duration=700
			)

			quarryBuild.featuresKept.append(FeatureType.forest)
			quarryBuild.featuresKept.append(FeatureType.rainforest)
			quarryBuild.featuresKept.append(FeatureType.marsh)

			return quarryBuild
		elif self == BuildType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			plantationBuild = BuildTypeData(
				name="Plantation",
				required=TechType.irrigation,
				improvement=ImprovementType.plantation,
				duration=500
			)

			plantationBuild.featuresKept.append(FeatureType.forest)
			plantationBuild.featuresKept.append(FeatureType.rainforest)
			plantationBuild.featuresKept.append(FeatureType.marsh)

			return plantationBuild
		elif self == BuildType.camp:
			campBuild = BuildTypeData(
				name="Camp",
				required=TechType.animalHusbandry,
				improvement=ImprovementType.camp,
				duration=600
			)

			campBuild.featuresKept.append(FeatureType.forest)
			campBuild.featuresKept.append(FeatureType.rainforest)

			return campBuild

		elif self == BuildType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			pastureBuild = BuildTypeData(
				name="Pasture",
				required=TechType.animalHusbandry,
				improvement=ImprovementType.pasture,
				duration=700
			)

			pastureBuild.featuresKept.append(FeatureType.forest)
			pastureBuild.featuresKept.append(FeatureType.rainforest)
			pastureBuild.featuresKept.append(FeatureType.marsh)

			return pastureBuild

		elif self == BuildType.fishingBoats:
			fishingBoatsBuild = BuildTypeData(
				name="Fishing Boats",
				required=TechType.sailing,
				improvement=ImprovementType.fishingBoats,
				duration=700,
				isWater=True
			)

			return fishingBoatsBuild

		elif self == BuildType.REMOVE_FOREST:
			removeForestBuild = BuildTypeData(
				name="Remove Forest",
				duration=300
			)

			removeForestBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.forest,
					required=TechType.mining,
					production=20,
					duration=300,
					isRemove=True
				)
			)

			return removeForestBuild

		elif self == BuildType.REMOVE_RAINFOREST:
			removeRainforestBuild = BuildTypeData(name="Remove Rainforest", duration=600)

			removeRainforestBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.rainforest,
					required=TechType.bronzeWorking,
					production=0,
					duration=600,
					isRemove=True
				)
			)

			return removeRainforestBuild

		elif self == BuildType.REMOVE_MARSH:
			removeMarshBuild = BuildTypeData(name="Remove Marsh", duration=500)

			removeMarshBuild.featureBuilds.append(
				FeatureBuild(
					featureType=FeatureType.marsh,
					required=TechType.masonry,
					production=0,
					duration=500,
					isRemove=True
				)
			)

			return removeMarshBuild


class UnitTask(ExtendedEnum):
	WORK = 5
	RANGED = 4
	ATTACK = 3
	EXPLORE_SEA = 2
	EXPLORE = 1
	SETTLE = 0


class UnitDomain(ExtendedEnum):
	SEA = 1
	LAND = 0


class OperationType(ExtendedEnum):
	NOT_SO_QUICK_COLONIZE = 2
	COLONIZE = 1
	FOUND_CITY = 0


class UnitTypeData:
	def __init__(self, name: str, baseType, domain: UnitDomain, effects, abilities, era: EraType,
	             requiredResource, civilization, unitTasks: [UnitTask],
	             defaultTask: UnitTask, movementType: MovementType, productionCost: int, purchaseCost: int):
		self.name = name
		self.baseType = baseType
		self.domain = domain
		self.effects = effects
		self.abilities = abilities
		self.era = era
		self.requiredResource = requiredResource
		self.civilization = civilization
		self.unitTasks = unitTasks
		self.defaultTask = defaultTask
		self.movementType = movementType
		self.productionCost = productionCost
		self.purchaseCost = purchaseCost


class UnitType(Enum):
	SETTLER = 0
	BUILDER = 1
	WARRIOR = 1

	def defaultTask(self) -> UnitTask:
		return self._data().defaultTask

	def unitTasks(self) -> [UnitTask]:
		return self._data().unitTasks

	def _data(self) -> UnitTypeData:
		if self == UnitType.SETTLER:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_SETTLER_NAME"),
				baseType=UnitType.SETTLER,
				domain=UnitDomain.LAND,
				effects=[
					_("TXT_KEY_UNIT_SETTLER_EFFECT1"),
					_("TXT_KEY_UNIT_SETTLER_EFFECT2")
				],
				abilities=[""".canFound"""],
				era=EraType.ANCIENT,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTask.SETTLE],
				defaultTask=UnitTask.SETTLE,
				movementType=MovementType.WALK,
				productionCost=80,
				purchaseCost=320,
			)
		elif self == UnitType.BUILDER:
			return UnitTypeData(
				name=_("TXT_KEY_UNIT_BUILDER_NAME"),
				baseType=UnitType.BUILDER,
				domain=UnitDomain.LAND,
				effects=[
					_("TXT_KEY_UNIT_BUILDER_EFFECT1"),
					_("TXT_KEY_UNIT_BUILDER_EFFECT2")
				],
				abilities=[""".canImprove"""],
				era=EraType.ANCIENT,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTask.WORK],
				defaultTask=UnitTask.WORK,
				movementType=MovementType.WALK,
				productionCost=50,
				purchaseCost=200,
			)
		else:
			raise InvalidEnumError(self)


class MoveOptions(Enum):
	NONE = 0


class UnitMissionType(Enum):
	NONE = 0

	rangedAttack = 1
