from enum import Enum
from typing import Optional

from game.civilizations import CivilizationType
from game.flavors import Flavor
from game.types import EraType, TechType, CivicType
from map.types import UnitMovementType, RouteType, FeatureType, ResourceType, UnitDomainType, Yields
from utils.base import ExtendedEnum
from utils.base import InvalidEnumError
# from utils.translation import gettext_lazy as _


class ImprovementTypeData:
	def __init__(self, name: str, effects: [str], requiredTech: Optional[TechType],
				 civilization: Optional[CivilizationType], flavors: [Flavor]):
		self.name = name
		self.effects = effects
		self.requiredTech = requiredTech
		self.civilization = civilization
		self.flavors = flavors


class ImprovementType(Enum):
	none = 'none'

	mine = 'mine'
	plantation = 'plantation'
	farm = 'farm'
	quarry = 'quarry'
	camp = 'camp'
	fishingBoats = 'fishingBoats'
	pasture = 'pasture'

	def name(self):
		return self._data().name

	def _data(self) -> ImprovementTypeData:
		if self == ImprovementType.none:
			return ImprovementTypeData(
				name="",
				effects=[],
				requiredTech=None,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.mine:
			# https://civilization.fandom.com/wiki/Mine_(Civ6)
			return ImprovementTypeData(
				name="Mine",
				effects=[
					"-1 Appeal",
					"+1 [Production] Production",
					"+1 [Production] Production (Apprenticeship)",
					"+1 [Production] Production (Industrialization)",
					"+1 [Production] Production (Smart Materials)"
				],
				requiredTech=TechType.mining,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			return ImprovementTypeData(
				name="Plantation",
				effects=[
					"+2 [Gold] Gold",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Scientific Theory)",
					"+2 [Gold] Gold (Globalization)"
				],
				requiredTech=TechType.irrigation,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.farm:
			# https://civilization.fandom.com/wiki/Farm_(Civ6)
			return ImprovementTypeData(
				name="Farm",
				effects=[
					"+1 [Food] Food",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food with two adjacent Farms (Feudalism)",
					"+1 [Food] Food for each adjacent Farm (Replaceable Parts)"
				],
				requiredTech=None,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.quarry:
			# https://civilization.fandom.com/wiki/Quarry_(Civ6)
			return ImprovementTypeData(
				name="Quarry",
				effects=[
					"-1 Appeal",
					"+1 [Production] Production",
					"+2 [Gold] Gold (Banking)",
					"+1 [Production] Production (Rocketry)",
					"+1 [Production] Production (Gunpowder)",
					"+1 [Production] Production (Predictive Systems)"
				],
				requiredTech=TechType.mining,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.camp:
			# https://civilization.fandom.com/wiki/Camp_(Civ6)
			return ImprovementTypeData(
				name="Camp",
				effects=[
					"+2 [Gold] Gold",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Mercantilism)",
					"+1 [Production] (Mercantilism)",
					"+1 [Gold] Gold (Synthetic Materials)"
				],
				requiredTech=TechType.animalHusbandry,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.fishingBoats:
			# https://civilization.fandom.com/wiki/Fishing_Boats_(Civ6)
			return ImprovementTypeData(
				name="Fishing Boats",
				effects=[
					"+1 [Food] Food",
					"+0.5 [Housing] Housing",
					"+2 [Gold] Gold (Cartography)",
					"+1 [Food] Food (Plastics)"
				],
				requiredTech=TechType.sailing,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			return ImprovementTypeData(
				name="Pasture",
				effects=[
					"+1 [Production] Production",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Stirrups)",
					"+1 [Production] Production (Robotics)"
				],
				requiredTech=TechType.animalHusbandry,
				civilization=None,
				flavors=[]
			)

		raise InvalidEnumError(self)

	def yieldsFor(self, player, visibleResource):
		if self == ImprovementType.none:
			return Yields(food=0, production=0, gold=0, science=0)
		elif self == ImprovementType.mine:
			# https://civilization.fandom.com/wiki/Mine_(Civ6)
			yieldValue =  Yields(food=0, production=1, gold=0, science=0, appeal=-1.0)

			# +1 additional Production (requires Apprenticeship)
			if player.techs.hasTech(TechType.apprenticeship):
				yieldValue.production += 1

			# +1 additional Production (requires Industrialization)
			if player.techs.hasTech(TechType.industrialization):
				yieldValue.production += 1

			# Provides adjacency bonus for Industrial Zones (+1 Production, ½ in GS-Only.png).

			# +1 additional Production (requires Smart Materials)
			#  /*if techs.has(tech: .smartMaterials) {
			#   yieldValue.production += 2

			return yieldValue
		elif self == ImprovementType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			yieldValue = Yields(food=0, production=0, gold=2, science=0, housing=0.5)

			if player.civics.hasCivic(CivicType.feudalism):
				yieldValue.food += 1

			# +1 Food (Scientific Theory)
			if player.techs.hasTech(TechType.scientificTheory):
				yieldValue.food += 1

			# +2 Gold (Globalization)
			if player.civics.hasCivic(CivicType.globalization):
				yieldValue.gold += 2

			return yieldValue
		elif self == ImprovementType.farm:
			# https//civilization.fandom.com/wiki/Farm_(Civ6)
			yieldValue = Yields(food=1, production=0, gold=0, science=0, housing=0.5)

			# +1 additional Food with two adjacent Farms (requires Feudalism)
			if player.civics.hasCivic(CivicType.feudalism):
				yieldValue.food += 1

			# +1 additional Food for each adjacent Farm (requires Replaceable Parts)
			if player.techs.hasTech(TechType.replaceableParts):
				yieldValue.food += 1

			return yieldValue
		elif self == ImprovementType.quarry:
			yieldValue = Yields(food=0, production=1, gold=0, science=0, appeal=-1.0)

			# +2 Gold (Banking)
			if player.techs.hasTech(TechType.banking):
				yieldValue.gold += 2

			# +1 Production (Rocketry)
			if player.techs.hasTech(TechType.rocketry):
				yieldValue.production += 1

			# +1 Production (Gunpowder)
			if player.techs.hasTech(TechType.gunpowder):
				yieldValue.production += 1

			# +1 Production (Predictive Systems)
			#  /*if techs.has(tech: .pred) {
			# yieldValue.production += 1

			return yieldValue
		elif self == ImprovementType.camp:
			yieldValue = Yields(food=0, production=0, gold=1, science=0)

			# +1 Food and +1 Production (requires Mercantilism)
			if player.civics.hasCivic(CivicType.mercantilism):
				yieldValue.food += 1
				yieldValue.production += 1

			# +2 additional Gold (requires Synthetic Materials)
			if player.techs.hasTech(TechType.syntheticMaterials):
				yieldValue.gold += 2

			return yieldValue
		elif self == ImprovementType.fishingBoats:
			# https://civilization.fandom.com/wiki/Fishing_Boats_(Civ6)
			yieldValue = Yields(food=1, production=0, gold=0, science=0, housing=0.5)

			if player.techs.hasTech(TechType.cartography):
				yieldValue.gold += 2

			if player.civics.hasCivic(CivicType.colonialism):
				yieldValue.production += 1

			if player.techs.hasTech(TechType.plastics):
				yieldValue.food += 1

			return yieldValue
		elif self == ImprovementType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			yieldValue = Yields(food=0, production=1, gold=0, science=0, housing=0.5)

			# +1 Food (requires Stirrups)
			if player.techs.hasTech(TechType.stirrups):
				yieldValue.food += 1

			# +1 additional Production and +1 additional Food (requires Robotics)
			if player.techs.hasTech(TechType.robotics):
				yieldValue.production += 1
				yieldValue.food += 1

			# +1 Production from every adjacent Outback Station (requires Steam Power)

			# +1 additional Production (requires Replaceable Parts)
			if player.techs.hasTech(TechType.replaceableParts):
				yieldValue.production += 1

			return yieldValue

		raise InvalidEnumError(self)


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
	none = 0

	removeRainforest = 1
	removeMarsh = 2
	removeForest = 3
	repair = 4
	mine = 5
	ancientRoad = 6
	classicalRoad = 7
	removeRoad = 8
	fishingBoats = 9
	camp = 10
	farm = 11
	quarry = 12
	plantation = 13
	pasture = 14

	def canRemove(self, feature: FeatureType) -> bool:
		featureBuild = next((build for build in self._data().featureBuilds if build.featureType == feature), None)

		if featureBuild is not None:
			return featureBuild.isRemove

		return False

	def _data(self) -> BuildTypeData:
		if self == BuildType.none:
			return BuildTypeData(
				name="None",
				duration=0
			)
		elif self == BuildType.repair:
			return BuildTypeData(
				name="Repair",
				repair=True,
				duration=300
			)

		elif self == BuildType.ancientRoad:
			return BuildTypeData(
				name="Road",
				era=EraType.ancient,
				route=RouteType.ancientRoad,
				duration=300
			)

		elif self == BuildType.classicalRoad:
			return BuildTypeData(
				name="Road",
				era=EraType.classical,
				route=RouteType.classicalRoad,
				duration=300
			)
		elif self == BuildType.removeRoad:
			return BuildTypeData(
				name="Remove Road",
				required=TechType.wheel,
				removeRoad=True,
				duration=300
			)
		elif self == BuildType.farm:
			farmBuild = BuildTypeData(
				name="Farm",
				improvement=ImprovementType.farm,
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
		elif self == BuildType.mine:
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
		elif self == BuildType.quarry:
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

		elif self == BuildType.removeForest:
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

		elif self == BuildType.removeRainforest:
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

		elif self == BuildType.removeMarsh:
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


class UnitTaskType(ExtendedEnum):
	none = 'none'

	work = 'work'
	ranged = 'ranged'
	attack = 'attack'
	explore_sea = 'explore_sea'
	explore = 'explore'
	settle = 'settle'


class UnitAbilityType(ExtendedEnum):
	pass


class OperationType(ExtendedEnum):
	not_so_quick_colonize = 2
	colonize = 1
	found_city = 0


class UnitClassType(ExtendedEnum):
	civilian = 'civilian'


class BitArray:
	pass


class UnitType:
	pass


class UnitTypeData:
	def __init__(self, name: str, baseType: Optional[UnitType], domain: UnitDomainType, effects: [str],
				 abilities: [UnitAbilityType], era: EraType, requiredResource: Optional[ResourceType],
				 civilization: Optional[CivilizationType], unitTasks: [UnitTaskType],
				 defaultTask: UnitTaskType, movementType: UnitMovementType, productionCost: int,
				 purchaseCost: int, faithCost: int, maintenanceCost: int, sight: int, range: int,
				 supportDistance: int, strength: int, targetType: UnitClassType, flags: Optional[BitArray],
				 meleeAttack: int, rangedAttack: int, moves: int, requiredTech: Optional[TechType],
				 obsoleteTech: Optional[TechType], requiredCivic: Optional[CivicType],
				 upgradesFrom: [UnitType], flavours: [Flavor]):
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
		#
		self.requiredCivic = requiredCivic
		self.flavours = flavours


class UnitType(ExtendedEnum):
	# default ------------------------------
	none = 'none'

	# civilians ------------------------------
	settler = 'settler'
	builder = 'builder'
	trader = 'trader'

	# recon ------------------------------
	scout = 'scout'  # ancient
	skirmisher = 'skirmisher'  # medieval

	# melee ------------------------------
	warrior = 'warrior'  # ancient
	swordman = 'swordman'  # classical
	manAtArms = 'manAtArms'  # medieval

	# ranged ------------------------------
	slinger = 'slinger'  # ancient
	archer = 'archer'  # ancient
	crossbowman = 'crossbowman'  # medieval

	# anti-cavalry ------------------------------
	spearman = 'spearman'  # ancient
	pikeman = 'pikeman'  # medieval
	# pikeAndShot  # renaissance

	# light cavalry ------------------------------
	horseman = 'horseman'  # classical
	courser = 'courser'  # medieval
	# cavalry  # industrial

	# heavy cavalry ------------------------------
	heavyChariot = 'heavyChariot'  # ancient
	knight = 'knight'  # medieval
	# cuirassier  # industrial

	# siege ------------------------------
	catapult = 'catapult'  # classical
	trebuchet = 'trebuchet'  # medieval
	# bombard  # renaissance

	# naval melee ------------------------------
	galley = 'galley'  # ancient
	# caravel  # renaissance
	# ironclad  # industrial

	# naval ranged ------------------------------
	quadrireme = 'quadrireme'  # classical

	def name(self):
		return self._data().name

	def defaultTask(self) -> UnitTaskType:
		return self._data().defaultTask

	def unitTasks(self) -> [UnitTaskType]:
		return self._data().unitTasks

	def civilization(self) -> Optional[CivilizationType]:
		return self._data().civilization

	def requiredCivic(self):
		return self._data().requiredCivic

	def _data(self) -> UnitTypeData:
		# default ------------------------------
		if self == UnitType.none:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)

		# civilians ------------------------------
		elif self == UnitType.settler:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.builder:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.trader:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)

		# recon ------------------------------
		elif self == UnitType.scout:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.skirmisher:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)

		# melee ------------------------------
		elif self == UnitType.warrior:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.swordman:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.manAtArms:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)

		# ranged ------------------------------
		elif self == UnitType.slinger:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.archer:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.crossbowman:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)

		# anti-cavalry ------------------------------
		elif self == UnitType.spearman:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.pikeman:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		# pikeAndShot  # renaissance

		# light cavalry ------------------------------
		elif self == UnitType.horseman:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.courser:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		# cavalry  # industrial

		# heavy cavalry ------------------------------
		elif self == UnitType.heavyChariot:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.knight:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		# cuirassier  # industrial

		# siege ------------------------------
		elif self == UnitType.catapult:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		elif self == UnitType.trebuchet:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		# bombard  # renaissance

		# naval melee ------------------------------
		elif self == UnitType.galley:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)
		# caravel  # renaissance
		# ironclad  # industrial
		#
		# naval ranged ------------------------------
		elif self == UnitType.quadrireme:
			return UnitTypeData(
				name='...',
				baseType=None,
				domain=UnitDomainType.land,
				effects=[],
				abilities=[],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[],
				defaultTask=UnitTaskType.none,
				movementType=UnitMovementType.walk,
				productionCost=0,
				purchaseCost=0,
				faithCost=0,
				maintenanceCost=0,
				sight=0,
				range=0,
				supportDistance=0,
				strength=0,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=0,
				requiredTech=None,
				requiredCivic=None,
				obsoleteTech=None,
				upgradesFrom=None,
				flavours=[]
			)

		raise AttributeError(f'cant get data for unit {self}')


class MoveOptions(Enum):
	NONE = 0


class UnitMissionType(Enum):
	NONE = 0

	rangedAttack = 1
