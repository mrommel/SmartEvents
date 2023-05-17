import sys
from enum import Enum
from typing import Optional

from game.civilizations import CivilizationType
from game.flavors import Flavor, FlavorType
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

	barbarianCamp = 'barbarianCamp'

	mine = 'mine'
	plantation = 'plantation'
	farm = 'farm'
	quarry = 'quarry'
	camp = 'camp'
	fishingBoats = 'fishingBoats'
	pasture = 'pasture'
	oilWell = 'oilWell'
	fort = 'fort'

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
		elif self == ImprovementType.barbarianCamp:
			#
			return ImprovementTypeData(
				name="Barbarian camp",
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
		elif self == ImprovementType.oilWell:
			# https://civilization.fandom.com/wiki/Oil_Well_(Civ6)
			return ImprovementTypeData(
				name="Oil well",
				effects=[
					"-1 Appeal",
					"+2 [Production] Production"
				],
				requiredTech=TechType.steel,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.fort:
			# https://civilization.fandom.com/wiki/Fort_(Civ6)
			return ImprovementTypeData(
				name="Fort",
				effects=[
					"Occupying unit receives +4 Defense Strength and 2 turns of fortification.",
					"Built by a Military Engineer."
				],
				requiredTech=TechType.siegeTactics,
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
	def __init__(self, name: str, repair: bool=False, requiredTech: Optional[TechType]=None, era: EraType=None,
	             improvement: Optional[ImprovementType]=None, route: RouteType=None, removeRoad: bool = False,
	             duration: int = 0, isWater: bool = True):
		"""

		:type requiredTech: object
		"""
		self.name = name
		self.repair = repair
		self.requiredTech = requiredTech
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

	def name(self) -> str:
		return self._data().name

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

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
				requiredTech=TechType.wheel,
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
				requiredTech=TechType.mining,
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
				requiredTech=TechType.mining,
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
				requiredTech=TechType.irrigation,
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
				requiredTech=TechType.animalHusbandry,
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
				requiredTech=TechType.animalHusbandry,
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
				requiredTech=TechType.sailing,
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

	def buildTimeOn(self, tile) -> int:
		time = self._data().duration

		for feature in list(FeatureType):
			if feature == FeatureType.none:
				continue

			if tile.hasFeature(feature) and not self.keepsFeature(feature):
				featureBuild = next((fb for fb in self._data().featureBuilds if fb.featureType == feature), None)

				if featureBuild is not None:
					time += featureBuild.duration
				else:
					# build cant handle feature
					return sys.maxsize

		return time

	def keepsFeature(self, feature: FeatureType) -> bool:
		if feature in self._data().featuresKept:
			return True

		return False

	def improvement(self) -> ImprovementType:
		return self._data().improvement

	def route(self):
		return self._data().route

	def willRepair(self) -> bool:
		return self._data().repair

	def willRemoveRoute(self) -> bool:
		return self._data().removeRoad


class UnitTaskType(ExtendedEnum):
	reserveSea = 'reserveSea'
	escortSea = 'escortSea'
	exploreSea = 'exploreSea'
	cityBombard = 'cityBombard'
	attackSea = 'attackSea'
	cityAttack = 'cityAttack'
	trade = 'trade'
	explore = 'explore'
	ranged = 'ranged'
	defense = 'defense'
	attack = 'attack'
	work = 'work'
	settle = 'settle'
	none = 'none'


class UnitAbilityType(ExtendedEnum):
	ignoreZoneOfControl = 'ignoreZoneOfControl'
	oceanImpassable = 'oceanImpassable'
	experienceFromTribal = 'experienceFromTribal'
	canMoveInRivalTerritory = 'canMoveInRivalTerritory'
	canEstablishTradeRoute = 'canEstablishTradeRoute'
	canImprove = 'canImprove'
	canFound = 'canFound'
	canCapture = 'canCapture'


class OperationType(ExtendedEnum):
	not_so_quick_colonize = 2
	colonize = 1
	found_city = 0


class UnitClassType(ExtendedEnum):
	civilian = 'civilian'
	recon = 'recon'
	melee = 'melee'
	antiCavalry = 'antiCavalry'
	lightCavalry = 'lightCavalry'
	heavyCavalry = 'heavyCavalry'
	ranged = 'ranged'
	siege = 'siege'
	navalMelee = 'navalMelee'
	navalRanged = 'navalRanged'


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
		self.faithCost = faithCost
		self.maintenanceCost = maintenanceCost
		self.sight = sight
		self.range = range
		self.supportDistance = supportDistance
		self.strength = strength
		self.targetType = targetType
		self.flags = flags
		self.meleeAttack = meleeAttack
		self.rangedAttack = rangedAttack
		self.moves = moves
		self.requiredTech = requiredTech
		self.obsoleteTech = obsoleteTech
		self.requiredCivic = requiredCivic
		self.upgradesFrom = upgradesFrom
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
	# courser = 'courser'  # medieval
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

	def civilization(self):
		return self._data().civilization

	def requiredCivic(self) -> CivicType:
		return self._data().requiredCivic

	def requiredTech(self) -> TechType:
		return self._data().requiredTech

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
				name="TXT_KEY_UNIT_SETTLER_NAME",
				baseType=UnitType.settler,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SETTLER_EFFECT1",
					"TXT_KEY_UNIT_SETTLER_EFFECT2"
				],
				abilities=[UnitAbilityType.canFound],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.settle],
				defaultTask=UnitTaskType.settle,
				movementType=UnitMovementType.walk,
				productionCost=80,
				purchaseCost=320,
				faithCost=-1,
				maintenanceCost=0,
				sight=3,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.expansion, value=9)
				]
			)
		elif self == UnitType.builder:
			return UnitTypeData(
				name="TXT_KEY_UNIT_BUILDER_NAME",
				baseType=UnitType.builder,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_BUILDER_EFFECT1",
					"TXT_KEY_UNIT_BUILDER_EFFECT2"
				],
				abilities=[UnitAbilityType.canImprove],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.work],
				defaultTask=UnitTaskType.work,
				movementType=UnitMovementType.walk,
				productionCost=50,
				purchaseCost=200,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.tileImprovement, value=10),
					Flavor(FlavorType.amenities, value=7),
					Flavor(FlavorType.expansion, value=4),
					Flavor(FlavorType.growth, value=4),
					Flavor(FlavorType.gold, value=4),
					Flavor(FlavorType.production, value=4),
					Flavor(FlavorType.science, value=2),
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=1)
				]
			)
		elif self == UnitType.trader:
			return UnitTypeData(
				name="TXT_KEY_UNIT_TRADER_NAME",
				baseType=UnitType.trader,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_TRADER_EFFECT1",
					"TXT_KEY_UNIT_TRADER_EFFECT2"
				],
				abilities=[
					UnitAbilityType.canEstablishTradeRoute,
					UnitAbilityType.canMoveInRivalTerritory
				],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.trade],
				defaultTask=UnitTaskType.trade,
				movementType=UnitMovementType.walk,
				productionCost=40,
				purchaseCost=160,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.civilian,
				flags=None,
				meleeAttack=0,
				rangedAttack=0,
				moves=1,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=CivicType.foreignTrade,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.gold, value=10)
				]
			)

		# recon ------------------------------
		elif self == UnitType.scout:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SCOUT_NAME",
				baseType=UnitType.scout,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SCOUT_EFFECT1"
				],
				abilities=[UnitAbilityType.experienceFromTribal],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.explore],
				defaultTask=UnitTaskType.explore,
				movementType=UnitMovementType.walk,
				productionCost=30,
				purchaseCost=120,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.recon,
				flags=None,
				meleeAttack=10,
				rangedAttack=0,
				moves=3,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.recon, value=8),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitType.skirmisher:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SKIRMISHER_NAME",
				baseType=UnitType.skirmisher,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SKIRMISHER_EFFECT1",
					"TXT_KEY_UNIT_SKIRMISHER_EFFECT2"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=150,
				purchaseCost=600,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=1,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.recon,
				flags=None,
				meleeAttack=20,
				rangedAttack=30,
				moves=3,
				requiredTech=TechType.machinery,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.scout],
				flavours=[
					Flavor(FlavorType.recon, value=8),
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=1)
				]
			)

		# melee ------------------------------
		elif self == UnitType.warrior:
			return UnitTypeData(
				name="TXT_KEY_UNIT_WARRIOR_NAME",
				baseType=UnitType.warrior,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_WARRIOR_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=40,
				purchaseCost=160,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.melee,
				flags=None,
				meleeAttack=20,
				rangedAttack=0,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.recon, value=3),
					Flavor(FlavorType.defense, value=3)
				]
			)
		elif self == UnitType.swordman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SWORDMAN_NAME",
				baseType=UnitType.swordman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SWORDMAN_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.classical,
				requiredResource=ResourceType.iron,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=90,
				purchaseCost=360,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.melee,
				flags=None,
				meleeAttack=35,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.ironWorking,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.warrior],
				flavours=[]
			)
		elif self == UnitType.manAtArms:
			return UnitTypeData(
				name="TXT_KEY_UNIT_MAN_AT_ARMS_NAME",
				baseType=UnitType.manAtArms,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_MAN_AT_ARMS_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=ResourceType.iron,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=160,
				purchaseCost=640,
				faithCost=-1,
				maintenanceCost=3,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.melee,
				flags=None,
				meleeAttack=45,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.apprenticeship,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.swordman],
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=8),
					Flavor(FlavorType.defense, value=1)
				]
			)

		# ranged ------------------------------
		elif self == UnitType.slinger:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SLINGER_NAME",
				baseType=UnitType.slinger,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SLINGER_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.ranged],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=35,
				purchaseCost=140,
				faithCost=-1,
				maintenanceCost=0,
				sight=2,
				range=1,
				supportDistance=1,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=5,
				rangedAttack=15,
				moves=2,
				requiredTech=None,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.recon, value=10),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=4)
				]
			)
		elif self == UnitType.archer:
			return UnitTypeData(
				name="TXT_KEY_UNIT_ARCHER_NAME",
				baseType=UnitType.archer,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_ARCHER_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.ranged],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=60,
				purchaseCost=240,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=2,
				supportDistance=2,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=15,
				rangedAttack=25,
				moves=2,
				requiredTech=TechType.archery,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.slinger],
				flavours=[
					Flavor(FlavorType.ranged, value=6),
					Flavor(FlavorType.recon, value=3),
					Flavor(FlavorType.offense, value=1),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == UnitType.crossbowman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_CROSSBOWMAN_NAME",
				baseType=UnitType.crossbowman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_CROSSBOWMAN_EFFECT1",
					"TXT_KEY_UNIT_CROSSBOWMAN_EFFECT2"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.ranged],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=180,
				purchaseCost=720,
				faithCost=-1,
				maintenanceCost=3,
				sight=2,
				range=2,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=30,
				rangedAttack=40,
				moves=2,
				requiredTech=TechType.machinery,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.archer],
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=7),
					Flavor(FlavorType.defense, value=2)
				]
			)

		# anti-cavalry ------------------------------
		elif self == UnitType.spearman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_SPEARMAN_NAME",
				baseType=UnitType.spearman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_SPEARMAN_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense],
				defaultTask=UnitTaskType.defense,
				movementType=UnitMovementType.walk,
				productionCost=65,
				purchaseCost=260,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.antiCavalry,
				flags=None,
				meleeAttack=25,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.bronzeWorking,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.recon, value=2),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitType.pikeman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_PIKEMAN_NAME",
				baseType=UnitType.pikeman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_PIKEMAN_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=180,
				purchaseCost=720,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.antiCavalry,
				flags=None,
				meleeAttack=45,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.militaryTactics,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.spearman],
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=6)
				]
			)
		# pikeAndShot  # renaissance

		# light cavalry ------------------------------
		elif self == UnitType.horseman:
			return UnitTypeData(
				name="TXT_KEY_UNIT_HORSEMAN_NAME",
				baseType=UnitType.horseman,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_HORSEMAN_EFFECT1",
					"TXT_KEY_UNIT_HORSEMAN_EFFECT2"
				],
				abilities=[
					UnitAbilityType.canCapture,
					UnitAbilityType.ignoreZoneOfControl
				],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=80,
				purchaseCost=320,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.lightCavalry,
				flags=None,
				meleeAttack=36,
				rangedAttack=0,
				moves=4,
				requiredTech=TechType.horsebackRiding,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[]
			)
		# elif self == UnitType.courser:
		# 	return UnitTypeData(
		# 		name='...',
		# 		baseType=None,
		# 		domain=UnitDomainType.land,
		# 		effects=[],
		# 		abilities=[],
		# 		era=EraType.ancient,
		# 		requiredResource=None,
		# 		civilization=None,
		# 		unitTasks=[],
		# 		defaultTask=UnitTaskType.none,
		# 		movementType=UnitMovementType.walk,
		# 		productionCost=0,
		# 		purchaseCost=0,
		# 		faithCost=0,
		# 		maintenanceCost=0,
		# 		sight=0,
		# 		range=0,
		# 		supportDistance=0,
		# 		strength=0,
		# 		targetType=UnitClassType.civilian,
		# 		flags=None,
		# 		meleeAttack=0,
		# 		rangedAttack=0,
		# 		moves=0,
		# 		requiredTech=None,
		# 		requiredCivic=None,
		# 		obsoleteTech=None,
		# 		upgradesFrom=None,
		# 		flavours=[]
		# 	)
		# cavalry  # industrial

		# heavy cavalry ------------------------------
		elif self == UnitType.heavyChariot:
			return UnitTypeData(
				name="TXT_KEY_UNIT_HEAVY_CHARIOT_NAME",
				baseType=UnitType.heavyChariot,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_HEAVY_CHARIOT_EFFECT1",
					"TXT_KEY_UNIT_HEAVY_CHARIOT_EFFECT2"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=65,
				purchaseCost=260,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.lightCavalry,
				flags=None,
				meleeAttack=28,
				rangedAttack=0,
				moves=2,
				requiredTech=TechType.wheel,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.recon, value=9),
					Flavor(FlavorType.ranged, value=5),
					Flavor(FlavorType.mobile, value=10),
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=6)
				]
			)
		elif self == UnitType.knight:
			return UnitTypeData(
				name="TXT_KEY_UNIT_KNIGHT_NAME",
				baseType=UnitType.knight,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_KNIGHT_EFFECT1"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.medieval,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.defense, UnitTaskType.explore],
				defaultTask=UnitTaskType.attack,
				movementType=UnitMovementType.walk,
				productionCost=220,
				purchaseCost=880,
				faithCost=-1,
				maintenanceCost=4,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.heavyCavalry,
				flags=None,
				meleeAttack=50,
				rangedAttack=0,
				moves=4,
				requiredTech=TechType.stirrups,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.heavyChariot],
				flavours=[
					Flavor(FlavorType.recon, value=1),
					Flavor(FlavorType.offense, value=9)
				]
			)
		# cuirassier  # industrial

		# siege ------------------------------
		elif self == UnitType.catapult:
			return UnitTypeData(
				name="TXT_KEY_UNIT_CATAPULT_NAME",
				baseType=UnitType.catapult,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_CATAPULT_EFFECT1",
					"TXT_KEY_UNIT_CATAPULT_EFFECT2",
					"TXT_KEY_UNIT_CATAPULT_EFFECT3"
				],
				abilities=[UnitAbilityType.canCapture],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attack, UnitTaskType.ranged, UnitTaskType.cityBombard],
				defaultTask=UnitTaskType.ranged,
				movementType=UnitMovementType.walk,
				productionCost=120,
				purchaseCost=480,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=2,
				supportDistance=2,
				strength=10,
				targetType=UnitClassType.ranged,
				flags=None,
				meleeAttack=25,
				rangedAttack=35,
				moves=2,
				requiredTech=TechType.engineering,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.offense, value=2)
				]
			)
		elif self == UnitType.trebuchet:
			return UnitTypeData(
				name="TXT_KEY_UNIT_TREBUCHET_NAME",
				baseType=UnitType.trebuchet,
				domain=UnitDomainType.land,
				effects=[
					"TXT_KEY_UNIT_TREBUCHET_EFFECT1",
					"TXT_KEY_UNIT_TREBUCHET_EFFECT2",
					"TXT_KEY_UNIT_TREBUCHET_EFFECT3"
				],
				abilities=[],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.cityAttack],
				defaultTask=UnitTaskType.cityAttack,
				movementType=UnitMovementType.walk,
				productionCost=200,
				purchaseCost=800,
				faithCost=-1,
				maintenanceCost=3,
				sight=2,
				range=2,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.siege,
				flags=None,
				meleeAttack=35,
				rangedAttack=45,
				moves=2,
				requiredTech=TechType.militaryEngineering,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[UnitType.catapult],
				flavours=[
					Flavor(FlavorType.ranged, value=8),
					Flavor(FlavorType.offense, value=2)
				]
			)
		# bombard  # renaissance

		# naval melee ------------------------------
		elif self == UnitType.galley:
			return UnitTypeData(
				name="TXT_KEY_UNIT_GALLEY_NAME",
				baseType=UnitType.galley,
				domain=UnitDomainType.sea,
				effects=[
					"TXT_KEY_UNIT_GALLEY_EFFECT1",
					"TXT_KEY_UNIT_GALLEY_EFFECT2"
				],
				abilities=[
					UnitAbilityType.oceanImpassable,
					UnitAbilityType.canCapture
				],
				era=EraType.ancient,
				requiredResource=None,
				civilization=None,
				unitTasks=[
					UnitTaskType.exploreSea,
					UnitTaskType.attackSea,
					UnitTaskType.escortSea,
					UnitTaskType.reserveSea
				],
				defaultTask=UnitTaskType.attackSea,
				movementType=UnitMovementType.swimShallow,
				productionCost=65,
				purchaseCost=260,
				faithCost=-1,
				maintenanceCost=1,
				sight=2,
				range=0,
				supportDistance=0,
				strength=10,
				targetType=UnitClassType.navalMelee,
				flags=None,
				meleeAttack=30,
				rangedAttack=0,
				moves=3,
				requiredTech=TechType.sailing,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[]
			)
		# caravel  # renaissance
		# ironclad  # industrial
		#
		# naval ranged ------------------------------
		elif self == UnitType.quadrireme:
			return UnitTypeData(
				name="TXT_KEY_UNIT_QUADRIREME_NAME",
				baseType=UnitType.quadrireme,
				domain=UnitDomainType.sea,
				effects=[
					"TXT_KEY_UNIT_QUADRIREME_EFFECT1",
					"TXT_KEY_UNIT_QUADRIREME_EFFECT2"
				],
				abilities=[UnitAbilityType.oceanImpassable],
				era=EraType.classical,
				requiredResource=None,
				civilization=None,
				unitTasks=[UnitTaskType.attackSea, UnitTaskType.escortSea, UnitTaskType.reserveSea],
				defaultTask=UnitTaskType.attackSea,
				movementType=UnitMovementType.swimShallow,
				productionCost=120,
				purchaseCost=480,
				faithCost=-1,
				maintenanceCost=2,
				sight=2,
				range=1,
				supportDistance=1,
				strength=10,
				targetType=UnitClassType.navalRanged,
				flags=None,
				meleeAttack=20,
				rangedAttack=25,
				moves=3,
				requiredTech=TechType.shipBuilding,
				obsoleteTech=None,
				requiredCivic=None,
				upgradesFrom=[],
				flavours=[]
			)

		raise AttributeError(f'cant get data for unit {self}')


class MoveOptions(Enum):
	NONE = 0


class UnitMissionType(Enum):
	NONE = 0

	rangedAttack = 1
