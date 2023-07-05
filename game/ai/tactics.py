import random
from typing import Optional

from core.base import ExtendedEnum
from game.civilizations import LeaderType
from game.unitTypes import BitArray, UnitTaskType, UnitMapType
from map.base import Array2D, Size, HexArea, HexPoint
from map.improvements import ImprovementType
from map.types import UnitDomainType, ResourceUsage, ResourceType


class TacticalMoveTypeData:
	def __init__(self, operationsCanRecruit: bool, dominanceZoneMove: bool, offenseFlavorWeight: int,
				 defenseFlavorWeight: int, priority: int):
		self.operationsCanRecruit: bool = operationsCanRecruit
		self.dominanceZoneMove: bool = dominanceZoneMove
		self.offenseFlavorWeight: int = offenseFlavorWeight
		self.defenseFlavorWeight: int = defenseFlavorWeight
		self.priority: int = priority


class TacticalMoveType:
	pass


class TacticalMoveType(ExtendedEnum):
	none = 'none'

	unassigned = 'unassigned'  # TACTICAL_UNASSIGNED
	moveNoncombatantsToSafety = 'moveNoncombatantsToSafety'  # TACTICAL_MOVE_NONCOMBATANTS_TO_SAFETY
	captureCity = 'captureCity'  # TACTICAL_CAPTURE_CITY
	damageCity = 'damageCity'  # TACTICAL_DAMAGE_CITY
	destroyHighUnit = 'destroyHighUnit'  # TACTICAL_DESTROY_HIGH_UNIT
	destroyMediumUnit = 'destroyMediumUnit'  # TACTICAL_DESTROY_MEDIUM_UNIT
	destroyLowUnit = 'destroyLowUnit'  # TACTICAL_DESTROY_LOW_UNIT
	toSafety = 'toSafety'  # TACTICAL_TO_SAFETY
	attritHighUnit = 'attritHighUnit'  # TACTICAL_ATTRIT_HIGH_UNIT
	attritMediumUnit = 'attritMediumUnit'  # TACTICAL_ATTRIT_MEDIUM_UNIT
	attritLowUnit = 'attritLowUnit'  # TACTICAL_ATTRIT_LOW_UNIT
	reposition = 'reposition'  # TACTICAL_REPOSITION
	barbarianCamp = 'barbarianCamp'  # TACTICAL_BARBARIAN_CAMP
	pillage = 'pillage'  # TACTICAL_PILLAGE
	civilianAttack = 'civilianAttack'  # TACTICAL_CIVILIAN_ATTACK
	safeBombards = 'safeBombards'  # TACTICAL_SAFE_BOMBARDS
	heal = 'heal'  # TACTICAL_HEAL
	ancientRuins = 'ancientRuins'  # TACTICAL_ANCIENT_RUINS
	garrisonToAllowBombards = 'garrisonToAllowBombards' # TACTICAL_GARRISON_TO_ALLOW_BOMBARD
	bastionAlreadyThere = 'bastionAlreadyThere'  # TACTICAL_BASTION_ALREADY_THERE
	garrisonAlreadyThere = 'garrisonAlreadyThere'  # TACTICAL_GARRISON_ALREADY_THERE
	guardImprovementAlreadyThere = 'guardImprovementAlreadyThere'  # TACTICAL_GUARD_IMPROVEMENT_ALREADY_THERE
	bastionOneTurn = 'bastionOneTurn'  # TACTICAL_BASTION_1_TURN
	garrisonOneTurn = 'garrisonOneTurn'  # TACTICAL_GARRISON_1_TURN
	guardImprovementOneTurn = 'guardImprovementOneTurn'  # TACTICAL_GUARD_IMPROVEMENT_1_TURN
	airSweep = 'airSweep'  # TACTICAL_AIR_SWEEP
	airIntercept = 'airIntercept'  # TACTICAL_AIR_INTERCEPT
	airRebase = 'airRebase'  # TACTICAL_AIR_REBASE
	closeOnTarget = 'closeOnTarget'  # TACTICAL_CLOSE_ON_TARGET
	moveOperation = 'moveOperation'  # TACTICAL_MOVE_OPERATIONS
	emergencyPurchases = 'emergencyPurchases'  # TACTICAL_EMERGENCY_PURCHASES

	# postures
	postureWithdraw = 'postureWithdraw'  # TACTICAL_POSTURE_WITHDRAW
	postureSitAndBombard = 'postureSitAndBombard'  # TACTICAL_POSTURE_SIT_AND_BOMBARD
	postureAttritFromRange = 'postureAttritFromRange'  # TACTICAL_POSTURE_ATTRIT_FROM_RANGE
	postureExploitFlanks = 'postureExploitFlanks'  # TACTICAL_POSTURE_EXPLOIT_FLANKS
	postureSteamroll = 'postureSteamroll'  # TACTICAL_POSTURE_STEAMROLL
	postureSurgicalCityStrike = 'postureSurgicalCityStrike'  # TACTICAL_POSTURE_SURGICAL_CITY_STRIKE
	postureHedgehog = 'postureHedgehog'  # TACTICAL_POSTURE_HEDGEHOG
	postureCounterAttack = 'postureCounterAttack'  # TACTICAL_POSTURE_COUNTERATTACK
	postureShoreBombardment = 'postureShoreBombardment'  # TACTICAL_POSTURE_SHORE_BOMBARDMENT

	# barbarian
	barbarianCaptureCity = 'barbarianCaptureCity'  # AI_TACTICAL_BARBARIAN_CAPTURE_CITY,
	barbarianDamageCity = 'barbarianDamageCity'  # AI_TACTICAL_BARBARIAN_DAMAGE_CITY,
	barbarianDestroyHighPriorityUnit = 'barbarianDestroyHighPriorityUnit'  # AI_TACTICAL_BARBARIAN_DESTROY_HIGH_PRIORITY_UNIT,
	barbarianDestroyMediumPriorityUnit = 'barbarianDestroyMediumPriorityUnit'  # AI_TACTICAL_BARBARIAN_DESTROY_MEDIUM_PRIORITY_UNIT,
	barbarianDestroyLowPriorityUnit = 'barbarianDestroyLowPriorityUnit'  # AI_TACTICAL_BARBARIAN_DESTROY_LOW_PRIORITY_UNIT,
	barbarianMoveToSafety = 'barbarianMoveToSafety'  # AI_TACTICAL_BARBARIAN_MOVE_TO_SAFETY,
	barbarianAttritHighPriorityUnit = 'barbarianAttritHighPriorityUnit'  # AI_TACTICAL_BARBARIAN_ATTRIT_HIGH_PRIORITY_UNIT,
	barbarianAttritMediumPriorityUnit = 'barbarianAttritMediumPriorityUnit'  # AI_TACTICAL_BARBARIAN_ATTRIT_MEDIUM_PRIORITY_UNIT,
	barbarianAttritLowPriorityUnit = 'barbarianAttritLowPriorityUnit'  # AI_TACTICAL_BARBARIAN_ATTRIT_LOW_PRIORITY_UNIT,
	barbarianPillage = 'barbarianPillage'  # AI_TACTICAL_BARBARIAN_PILLAGE,
	barbarianBlockadeResource = 'barbarianBlockadeResource'  # AI_TACTICAL_BARBARIAN_PRIORITY_BLOCKADE_RESOURCE,
	barbarianCivilianAttack = 'barbarianCivilianAttack'  # AI_TACTICAL_BARBARIAN_CIVILIAN_ATTACK,
	barbarianAggressiveMove = 'barbarianAggressiveMove'  # AI_TACTICAL_BARBARIAN_AGGRESSIVE_MOVE,
	barbarianPassiveMove = 'barbarianPassiveMove'  # AI_TACTICAL_BARBARIAN_PASSIVE_MOVE,
	barbarianCampDefense = 'barbarianCampDefense'  # AI_TACTICAL_BARBARIAN_CAMP_DEFENSE,
	barbarianGuardCamp = 'barbarianGuardCamp'
	barbarianDesperateAttack = 'barbarianDesperateAttack'  # AI_TACTICAL_BARBARIAN_DESPERATE_ATTACK,
	barbarianEscortCivilian = 'barbarianEscortCivilian'  # AI_TACTICAL_BARBARIAN_ESCORT_CIVILIAN,
	barbarianPlunderTradeUnit = 'barbarianPlunderTradeUnit'  # AI_TACTICAL_BARBARIAN_PLUNDER_TRADE_UNIT,
	barbarianPillageCitadel = 'barbarianPillageCitadel'  # AI_TACTICAL_BARBARIAN_PILLAGE_CITADEL,
	barbarianPillageNextTurn = 'barbarianPillageNextTurn'  # AI_TACTICAL_BARBARIAN_PILLAGE_NEXT_TURN

	@staticmethod
	def allBarbarianMoves() -> [TacticalMoveType]:
		return [
			TacticalMoveType.barbarianCaptureCity,
			TacticalMoveType.barbarianDamageCity,
			TacticalMoveType.barbarianDestroyHighPriorityUnit,
			TacticalMoveType.barbarianDestroyMediumPriorityUnit,
			TacticalMoveType.barbarianDestroyLowPriorityUnit,
			TacticalMoveType.barbarianMoveToSafety,
			TacticalMoveType.barbarianAttritHighPriorityUnit,
			TacticalMoveType.barbarianAttritMediumPriorityUnit,
			TacticalMoveType.barbarianAttritLowPriorityUnit,
			TacticalMoveType.barbarianPillage,
			TacticalMoveType.barbarianBlockadeResource,
			TacticalMoveType.barbarianCivilianAttack,
			TacticalMoveType.barbarianAggressiveMove,
			TacticalMoveType.barbarianPassiveMove,
			TacticalMoveType.barbarianCampDefense,
			TacticalMoveType.barbarianGuardCamp,
			TacticalMoveType.barbarianDesperateAttack,
			TacticalMoveType.barbarianEscortCivilian,
			TacticalMoveType.barbarianPlunderTradeUnit,
			TacticalMoveType.barbarianPillageCitadel,
			TacticalMoveType.barbarianPillageNextTurn
		]

	def priority(self) -> int:
		return self._data().priority

	def dominanceZoneMove(self) -> bool:
		return self._data().dominanceZoneMove

	def canRecruitForOperations(self) -> bool:
		return self._data().operationsCanRecruit

	def _data(self) -> TacticalMoveTypeData:
		if self == TacticalMoveType.none:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=-1
			)
		elif self == TacticalMoveType.barbarianGuardCamp:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=200
			)
		elif self == TacticalMoveType.unassigned:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=-1)
		elif self == TacticalMoveType.moveNoncombatantsToSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=0
			)
		elif self == TacticalMoveType.captureCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0, priority=150
			)
		elif self == TacticalMoveType.damageCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0, priority=15
			)
		elif self == TacticalMoveType.destroyHighUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=140
			)
		elif self == TacticalMoveType.destroyMediumUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=120
			)
		elif self == TacticalMoveType.destroyLowUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=110
			)
		elif self == TacticalMoveType.closeOnTarget:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=45
			)
		elif self == TacticalMoveType.toSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=11
			)
		elif self == TacticalMoveType.attritHighUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=17
			)
		elif self == TacticalMoveType.attritMediumUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=15
			)
		elif self == TacticalMoveType.attritLowUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=12
			)
		elif self == TacticalMoveType.reposition:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=50, defenseFlavorWeight=50, priority=1
			)
		elif self == TacticalMoveType.barbarianCamp:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0, priority=10
			)
		elif self == TacticalMoveType.pillage:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0, priority=40
			)
		elif self == TacticalMoveType.civilianAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0, priority=65
			)
		elif self == TacticalMoveType.safeBombards:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0, priority=60
			)
		elif self == TacticalMoveType.heal:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=8
			)
		elif self == TacticalMoveType.ancientRuins:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=50, defenseFlavorWeight=50, priority=25
			)
		elif self == TacticalMoveType.garrisonToAllowBombards:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=20
			)
		elif self == TacticalMoveType.bastionAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=7
			)
		elif self == TacticalMoveType.garrisonAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=6
			)
		elif self == TacticalMoveType.guardImprovementAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=5
			)
		elif self == TacticalMoveType.bastionOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=4
			)
		elif self == TacticalMoveType.garrisonOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=3
			)
		elif self == TacticalMoveType.guardImprovementOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=2
			)
		elif self == TacticalMoveType.airSweep:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0, priority=10
			)
		elif self == TacticalMoveType.airIntercept:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=20
			)
		elif self == TacticalMoveType.airRebase:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100, priority=1
			)
		elif self == TacticalMoveType.postureWithdraw:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=101
			)
		elif self == TacticalMoveType.postureSitAndBombard:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=105
			)
		elif self == TacticalMoveType.postureAttritFromRange:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=104
			)
		elif self == TacticalMoveType.postureExploitFlanks:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=107
			)
		elif self == TacticalMoveType.postureSteamroll:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=108
			)
		elif self == TacticalMoveType.postureSurgicalCityStrike:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=106
			)
		elif self == TacticalMoveType.postureHedgehog:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=50
			)
		elif self == TacticalMoveType.postureCounterAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=103
			)
		elif self == TacticalMoveType.postureShoreBombardment:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=100
			)
		elif self == TacticalMoveType.moveOperation:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=80
			)
		elif self == TacticalMoveType.emergencyPurchases:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=200
			)

		# https://github.com/chvrsi/BarbariansEvolved/blob/00a6feec72fa7d95ef026d821f008bdbbf3ee3ab/xml/BarbarianDefines.xml
		elif self == TacticalMoveType.barbarianCaptureCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=9
			)
		elif self == TacticalMoveType.barbarianDamageCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=5
			)
		elif self == TacticalMoveType.barbarianDestroyHighPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=16
			)
		elif self == TacticalMoveType.barbarianDestroyMediumPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=15
			)
		elif self == TacticalMoveType.barbarianDestroyLowPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=14
			)
		elif self == TacticalMoveType.barbarianMoveToSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=10
			)
		elif self == TacticalMoveType.barbarianAttritHighPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=10
			)
		elif self == TacticalMoveType.barbarianAttritMediumPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=7
			)
		elif self == TacticalMoveType.barbarianAttritLowPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=6
			)
		elif self == TacticalMoveType.barbarianPillage:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=12
			)
		elif self == TacticalMoveType.barbarianBlockadeResource:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=10
			)
		elif self == TacticalMoveType.barbarianCivilianAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=13
			)
		elif self == TacticalMoveType.barbarianAggressiveMove:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=3
			)
		elif self == TacticalMoveType.barbarianPassiveMove:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=-1
			)
		elif self == TacticalMoveType.barbarianCampDefense:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=13
			)
		elif self == TacticalMoveType.barbarianDesperateAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=0
			)
		elif self == TacticalMoveType.barbarianEscortCivilian:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=30
			)
		elif self == TacticalMoveType.barbarianPlunderTradeUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=20
			)
		elif self == TacticalMoveType.barbarianPillageCitadel:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=14
			)
		elif self == TacticalMoveType.barbarianPillageNextTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0, priority=4
			)


class TacticalTargetType(ExtendedEnum):
	none = 'none'  # AI_TACTICAL_TARGET_NONE

	city = 'city'  # AI_TACTICAL_TARGET_CITY
	barbarianCamp = 'barbarianCamp'  # AI_TACTICAL_TARGET_BARBARIAN_CAMP
	improvement = 'improvement'  # AI_TACTICAL_TARGET_IMPROVEMENT
	blockadeResourcePoint = 'blockadeResourcePoint'  # AI_TACTICAL_TARGET_BLOCKADE_RESOURCE_POINT
	lowPriorityUnit = 'lowPriorityUnit'  # AI_TACTICAL_TARGET_LOW_PRIORITY_UNIT # Can't attack one of our cities
	mediumPriorityUnit = 'mediumPriorityUnit'  # AI_TACTICAL_TARGET_MEDIUM_PRIORITY_UNIT - Can damage one of our cities
	highPriorityUnit = 'highPriorityUnit'  # AI_TACTICAL_TARGET_HIGH_PRIORITY_UNIT
		# Can contribute to capturing one of our cities
	cityToDefend = 'cityToDefend'  # AI_TACTICAL_TARGET_CITY_TO_DEFEND
	improvementToDefend = 'improvementToDefend'  # AI_TACTICAL_TARGET_IMPROVEMENT_TO_DEFEND
	defensiveBastion = 'defensiveBastion'  # AI_TACTICAL_TARGET_DEFENSIVE_BASTION
	ancientRuins = 'ancientRuins'  # AI_TACTICAL_TARGET_ANCIENT_RUINS
	bombardmentZone = 'bombardmentZone'  # AI_TACTICAL_TARGET_BOMBARDMENT_ZONE - Used for naval bombardment operation
	embarkedMilitaryUnit = 'embarkedMilitaryUnit'  # AI_TACTICAL_TARGET_EMBARKED_MILITARY_UNIT
	embarkedCivilian = 'embarkedCivilian'  # AI_TACTICAL_TARGET_EMBARKED_CIVILIAN
	lowPriorityCivilian = 'lowPriorityCivilian'  # AI_TACTICAL_TARGET_LOW_PRIORITY_CIVILIAN
	mediumPriorityCivilian = 'mediumPriorityCivilian'  # AI_TACTICAL_TARGET_MEDIUM_PRIORITY_CIVILIAN
	highPriorityCivilian = 'highPriorityCivilian'  # AI_TACTICAL_TARGET_HIGH_PRIORITY_CIVILIAN
	veryHighPriorityCivilian = 'veryHighPriorityCivilian'  # AI_TACTICAL_TARGET_VERY_HIGH_PRIORITY_CIVILIAN

	tradeUnitSea = 'tradeUnitSea'  # AI_TACTICAL_TARGET_TRADE_UNIT_SEA,
	tradeUnitLand = 'tradeUnitLand'  # AI_TACTICAL_TARGET_TRADE_UNIT_LAND,
	tradeUnitSeaPlot = 'tradeUnitSeaPlot'  # AI_TACTICAL_TARGET_TRADE_UNIT_SEA_PLOT - Used for idle unit moves to
		# plunder trade routes that go through our territory
	tradeUnitLandPlot = 'tradeUnitLandPlot'  # AI_TACTICAL_TARGET_TRADE_UNIT_LAND_PLOT,
	citadel = 'citadel'  # AI_TACTICAL_TARGET_CITADEL
	improvementResource = 'improvementResource'  # AI_TACTICAL_TARGET_IMPROVEMENT_RESOURCE


class TacticalPostureType(ExtendedEnum):
	"""
		// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
		//  CLASS:      CvTacticalPosture
		// !  \brief        The posture an AI has adopted for fighting in a specific dominance zone
		//
		// !  Key Attributes:
		// !  - Used to keep consistency in approach from turn-to-turn
		// !  - Reevaluated by tactical AI each turn before units are moved for this zone
		// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	"""
	none = 'none'
	withdraw = 'withdraw'
	sitAndBombard = 'sitAndBombard'
	attritFromRange = 'attritFromRange'
	exploitFlanks = 'exploitFlanks'
	steamRoll = 'steamRoll'
	surgicalCityStrike = 'surgicalCityStrike'
	hedgehog = 'hedgehog'
	counterAttack = 'counterAttack'
	shoreBombardment = 'shoreBombardment'
	emergencyPurchases = 'emergencyPurchases'


class TacticalDominanceTerritoryType(ExtendedEnum):
	tempZone = 'tempZone'
	enemy = 'enemy'
	friendly = 'friendly'
	neutral = 'neutral'
	noOwner = 'noOwner'


class TacticalDominanceType(ExtendedEnum):
	none = 'none'

	noUnitsPresent = 'noUnitsPresent'
	notVisible = 'notVisible'
	friendly = 'friendly'  # TACTICAL_DOMINANCE_FRIENDLY
	enemy = 'enemy'
	even = 'even'


class TacticalDominanceTerritoryType(ExtendedEnum):
	tempZone = 'tempZone'


class TacticalDominanceType(ExtendedEnum):
	noUnitsPresent = 'noUnitsPresent'


class TacticalAnalysisCell:
	def __init__(self):
		self.bits = BitArray(24)

		self.enemyMilitaryUnit = None
		self.enemyCivilianUnit = None
		self.neutralMilitaryUnit = None
		self.neutralCivilianUnit = None
		self.friendlyMilitaryUnit = None
		self.friendlyCivilianUnit = None

		self.defenseModifier = 0
		self.deploymentScore = 0
		self.targetType = TacticalTargetType.none

		self.dominanceZone: Optional[TacticalDominanceZone] = None

	def reset(self):
		self.bits.fill(False)

		self.enemyMilitaryUnit = None
		self.enemyCivilianUnit = None
		self.neutralMilitaryUnit = None
		self.neutralCivilianUnit = None
		self.friendlyMilitaryUnit = None
		self.friendlyCivilianUnit = None

		self.defenseModifier = 0
		self.deploymentScore = 0
		self.targetType = TacticalTargetType.none

		self.dominanceZone = None

	def setRevealed(self, value: bool):
		self.bits[0] = value

	def isRevealed(self) -> bool:
		return self.bits[0] > 0


class TacticalDominanceZone:
	def __init__(self, territoryType: TacticalDominanceTerritoryType, dominanceFlag: TacticalDominanceType, owner,
				 area: Optional[HexArea], isWater: bool, center, navalInvasion: bool, friendlyStrength: int,
				 friendlyRangedStrength: int, friendlyUnitCount: int, friendlyRangedUnitCount: int,
				 enemyStrength: int, enemyRangedStrength: int, enemyUnitCount: int, enemyRangedUnitCount: int,
				 enemyNavalUnitCount: int, rangeClosestEnemyUnit: int, dominanceValue: int):
		self.territoryType = territoryType
		self.dominanceFlag = dominanceFlag
		self.owner = owner
		self.area = area
		self.isWater = isWater
		self._center = center  # Tile
		self.navalInvasion = navalInvasion
		self.friendlyStrength = friendlyStrength
		self.friendlyRangedStrength = friendlyRangedStrength
		self.friendlyUnitCount = friendlyUnitCount
		self.friendlyRangedUnitCount = friendlyRangedUnitCount
		self.enemyStrength = enemyStrength
		self.enemyRangedStrength = enemyRangedStrength
		self.enemyUnitCount = enemyUnitCount
		self.enemyRangedUnitCount = enemyRangedUnitCount
		self.enemyNavalUnitCount = enemyNavalUnitCount
		self.rangeClosestEnemyUnit = rangeClosestEnemyUnit
		self.dominanceValue = dominanceValue

		self.closestCity = None  # City

	@property
	def center(self):
		return self._center

	def __eq__(self, other):
		if isinstance(other, TacticalDominanceZone):
			return self._center.point == other._center.point

		return False

	def __hash__(self):
		return hash(self._center.point)


class TacticalTarget:
	def __init__(self, targetType: TacticalTargetType, target: HexPoint, targetLeader: LeaderType = LeaderType.none,
				 dominanceZone: TacticalDominanceZone = None):
		self.targetType = targetType
		self.target = target
		self.targetLeader = targetLeader
		self.dominanceZone = dominanceZone

	def isTargetValidIn(self, domain: UnitDomainType) -> bool:
		"""This target make sense for this domain of unit/zone?"""
		if self.targetType == TacticalTargetType.none:
			return False

		elif self.targetType == TacticalTargetType.city or \
			self.targetType == TacticalTargetType.cityToDefend or \
			self.targetType == TacticalTargetType.lowPriorityCivilian or \
			self.targetType == TacticalTargetType.mediumPriorityCivilian or \
			self.targetType == TacticalTargetType.highPriorityCivilian or \
			self.targetType == TacticalTargetType.veryHighPriorityCivilian or \
			self.targetType == TacticalTargetType.lowPriorityUnit or \
			self.targetType == TacticalTargetType.mediumPriorityUnit or \
			self.targetType == TacticalTargetType.highPriorityUnit:

			return True  # always valid

		elif self.targetType == TacticalTargetType.barbarianCamp or \
			self.targetType == TacticalTargetType.improvement or \
			self.targetType == TacticalTargetType.improvementToDefend or \
			self.targetType == TacticalTargetType.defensiveBastion or \
			self.targetType == TacticalTargetType.ancientRuins or \
			self.targetType == TacticalTargetType.tradeUnitLand or \
			self.targetType == TacticalTargetType.tradeUnitLandPlot or \
			self.targetType == TacticalTargetType.citadel or \
			self.targetType == TacticalTargetType.improvementResource:

			return domain == UnitDomainType.land  # land targets

		elif self.targetType == TacticalTargetType.blockadeResourcePoint or \
			self.targetType == TacticalTargetType.bombardmentZone or \
			self.targetType == TacticalTargetType.embarkedMilitaryUnit or \
			self.targetType == TacticalTargetType.embarkedCivilian or \
			self.targetType == TacticalTargetType.tradeUnitSea or \
			self.targetType == TacticalTargetType.tradeUnitSeaPlot:

			return domain == UnitDomainType.sea  # sea targets

		return False


class TacticalAnalysisMap:
	dominancePercentage = 25  # AI_TACTICAL_MAP_DOMINANCE_PERCENTAGE
	tacticalRange = 10  # AI_TACTICAL_RECRUIT_RANGE
	tempZoneRadius = 5  # AI_TACTICAL_MAP_TEMP_ZONE_RADIUS

	def __init__(self, size: Size):
		self.unitStrengthMultiplier = 10 * self.tacticalRange  # AI_TACTICAL_MAP_UNIT_STRENGTH_MULTIPLIER

		self.plots = Array2D(size.width(), size.height())
		self.plots.fill(TacticalAnalysisCell())

		self.turnBuild = -1
		self.isBuild = False
		self.enemyUnits = []
		self.dominanceZones = []
		self.ignoreLineOfSight = False

		self.playerBuild = None

		# reserve capacity
		# self.dominanceZones.reserveCapacity(mapSize.width() * mapSize.height())

	def refreshFor(self, player, simulation):
		"""Fill the map with data for this AI player's turn"""
		# skip for barbarian player
		if player.isBarbarian():
			return

		if self.turnBuild < simulation.currentTurn or player.leader != self.playerBuild.leader:
			self.isBuild = False
			self.playerBuild = player
			self.turnBuild = simulation.currentTurn

			self.dominanceZones = []
			self.addTemporaryZones(simulation)

			for x in range(self.plots.width):
				for y in range(self.plots.height):
					tile = simulation.tileAt(x, y)

					if self.populateCellAt(x, y, tile, simulation):
						zone = self.dominanceZone(self.plots.values[y][x], tile, simulation)
						if zone is not None:
							# Set zone for this cell
							self.dominanceZones.append(zone)
							self.plots.values[y][x].dominanceZone = zone

					else:
						# Erase this cell
						self.plots.values[y][x].reset()

			self.calculateMilitaryStrengths(simulation)
			self.prioritizeZones(simulation)
			self.buildEnemyUnitList(simulation)
			self.markCellsNearEnemy(simulation)

			self.isBuild = True

		return

	def addTemporaryZones(self, simulation):
		"""Add in any temporary dominance zones from tactical AI"""
		tacticalAI = self.playerBuild.tacticalAI

		tacticalAI.dropObsoleteZones(simulation)

		# Can't be a city zone (which is just used to boost priority but not establish a new zone)
		for temporaryZone in tacticalAI.temporaryZones:
			if temporaryZone.targetType == TacticalTargetType.city:
				continue

			tile = simulation.tileAt(temporaryZone.location)

			if tile is not None:
				newZone = TacticalDominanceZone(
					territoryType=TacticalDominanceTerritoryType.tempZone,
					dominanceFlag=TacticalDominanceType.noUnitsPresent,
					owner=None,
					area=tile.area,
					isWater=tile.terrain().isWater(),
					center=tile,
					navalInvasion=temporaryZone.navalMission,
					friendlyStrength=0,
					friendlyRangedStrength=0,
					friendlyUnitCount=0,
					friendlyRangedUnitCount=0,
					enemyStrength=0,
					enemyRangedStrength=0,
					enemyUnitCount=0,
					enemyRangedUnitCount=0,
					enemyNavalUnitCount=0,
					rangeClosestEnemyUnit=0,
					dominanceValue=0
				)

				self.dominanceZones.append(newZone)

		return


class TemporaryZone:
	pass


class QueuedAttack:
	pass


class TacticalMove:
	def __init__(self):
		self.moveType: TacticalMoveType = TacticalMoveType.unassigned
		self.priority: int = TacticalMoveType.unassigned.priority()

	def __eq__(self, other):
		if isinstance(other, TacticalMove):
			return self.priority == other.priority and self.moveType == other.moveType

		return False

	def __lt__(self, other):
		# this will sort the highest priority to the beginning
		if isinstance(other, TacticalMove):
			return self.priority > other.priority

		return False

	def __repr__(self):
		return f'TacticalMove({self.moveType}, {self.priority})'


class TacticalPosture:
	pass


class TacticalCity:
	"""Object stored in the list of current move cities (currentMoveCities)"""
	def __init__(self, attackStrength: int = 0, expectedTargetDamage: int = 0, city = None):
		self.attackStrength = attackStrength
		self.expectedTargetDamage = expectedTargetDamage
		self.city = city

	def __lt__(self, other):
		if isinstance(other, TacticalCity):
			return self.attackStrength > other.attackStrength

		return False

	def __eq__(self, other):
		if isinstance(other, TacticalCity):
			return False

		return False


class TacticalUnit:
	def __init__(self, unit, attackStrength: int = 0, healthPercent: int = 0):
		self.attackStrength = attackStrength
		self.healthPercent = healthPercent
		self.movesToTarget = 0
		self.expectedTargetDamage = 0
		self.expectedSelfDamage = 0
		self.unit = unit

	def attackPriority(self) -> int:
		return self.attackStrength * self.healthPercent

	def __lt__(self, other):
		if isinstance(other, TacticalUnit):
			return self.attackStrength > other.attackStrength

		return False

	def __eq__(self, other):
		if isinstance(other, TacticalUnit):
			return False

		return False


class BlockingUnit:
	pass


class OperationUnit:
	pass


class TacticalAI:
	recruitRange = 10  # AI_TACTICAL_RECRUIT_RANGE
	repositionRange = 10  # AI_TACTICAL_REPOSITION_RANGE
	deployRadius = 4  # AI_OPERATIONAL_CITY_ATTACK_DEPLOY_RANGE

	def __init__(self, player):

		self.player = player

		self.temporaryZones: [TemporaryZone] = []
		self.allTargets: [TacticalTarget] = []

		self.queuedAttacks: [QueuedAttack] = []
		self.movePriorityList: [TacticalMove] = []
		self.postures: [TacticalPosture] = []
		self.zoneTargets: [TacticalTarget] = []
		self.tempTargets: [TacticalTarget] = []

		self.currentTurnUnits = []
		self.currentMoveCities: [TacticalCity] = []
		self.currentMoveUnits: [TacticalUnit] = []
		self.currentMoveHighPriorityUnits: [TacticalUnit] = []

		# Blocking (and flanking) position data
		self.potentialBlocks: [BlockingUnit] = []
		self.temporaryBlocks: [BlockingUnit] = []
		self.chosenBlocks: [BlockingUnit] = []
		self.newlyChosen: [BlockingUnit] = []

		# Operational AI support data
		self.operationUnits: [OperationUnit] = []
		self.generalsToMove: [OperationUnit] = []
		self.paratroopersToMove: [OperationUnit] = []

		self.movePriorityTurn: int = 0
		self.currentSeriesId: int = -1

	def doTurn(self, simulation):
		"""Update the AI for units"""
		# DropOldFocusAreas();
		self.findTacticalTargets(simulation)

		# do this after updating the target list!
		self.recruitUnits(simulation)

		# Loop through each dominance zone assigning moves
		self.processDominanceZones(simulation)

	def dropObsoleteZones(self, simulation):
		"""Remove temporary zones that have expired"""
		self.temporaryZones = list(filter(lambda zone: zone.lastTurn >= simulation.currentTurn, self.temporaryZones))
		return

	def recruitUnits(self, simulation):
		"""Mark all the units that will be under tactical AI control this turn"""
		dangerPlotsAI = self.player.dangerPlotsAI
		self.currentTurnUnits = []

		for unit in simulation.unitsOf(self.player):
			# Never want immobile / dead units, explorers, ones that have already moved
			if unit.task() == UnitTaskType.explore or not unit.canMove():
				continue

			elif self.player.leader == LeaderType.barbar:
				# We want ALL the barbarians that are not guarding a camp
				unit.setTacticalMove(TacticalMoveType.unassigned)
				self.currentTurnUnits.append(unit)

			elif unit.domain() == UnitDomainType.air:
				# and air units
				unit.setTacticalMove(TacticalMoveType.unassigned)
				self.currentTurnUnits.append(unit)

			elif not unit.isCombatUnit() and not unit.isGreatGeneral():
				# Now down to land and sea units... in these groups our unit must have a base combat strength...
				# or be a great general
				continue

			else:
				# Is this one in an operation we can't interrupt?
				if unit.army() is not None:
					if unit.army().canTacticalAIInterrupt():
						unit.setTacticalMove(TacticalMoveType.none)
				else:
					# Non - zero danger value, near enemy, or deploying out of an operation?
					danger = dangerPlotsAI.dangerAt(unit.location)
					if danger > 0 or self.isNearVisibleEnemy(unit, 10, simulation):
						unit.setTacticalMove(TacticalMoveType.unassigned)
						self.currentTurnUnits.append(unit)
		return

	def isNearVisibleEnemy(self, unitToTest, distance: int, simulation) -> bool:
		"""Am I within range of an enemy?"""
		diplomacyAI = self.player.diplomacyAI

		# Loop through enemies
		for otherPlayer in simulation.players:
			if otherPlayer.isAlive() and otherPlayer.leader != self.player.leader and diplomacyAI.isAtWarWith(
				otherPlayer):
				# Loop through their units
				for unit in simulation.unitsOf(otherPlayer):
					# Make sure this tile is visible to us
					tile = simulation.tileAt(unit.location)

					if tile is not None:
						if tile.isVisibleTo(self.player) and unitToTest.location.distanceTo(unit.location) < distance:
							return True

				# Loop through their cities
				for city in simulation.citiesOf(otherPlayer):
					# Make sure this tile is visible to us
					tile = simulation.tileAt(city.location)
					if tile.isVisibleTo(self.player) and unitToTest.location.distanceTo(city.location) < distance:
						return True

		return False

	def findTacticalTargets(self, simulation):
		"""Make lists of everything we might want to target with the tactical AI this turn"""
		diplomacyAI = self.player.diplomacyAI
		dangerPlotsAI = self.player.dangerPlotsAI

		# Clear out target list since we rebuild it each turn
		self.allTargets = []

		barbsAllowedYet = simulation.currentTurn >= 20
		mapSize = simulation.mapSize()

		# Look at every tile on map
		for x in range(mapSize.width()):
			for y in range(mapSize.height()):
				point = HexPoint(x, y)
				validPlot = False
				tile = simulation.tileAt(point)

				if tile.isVisibleTo(self.player):
					# Make sure player is not a barbarian who can not move into owned territory this early in the game
					if self.player.isBarbarian():
						if barbsAllowedYet or not tile.hasOwner():
							validPlot = True
					else:
						validPlot = True

				if validPlot:
					if self.isAlreadyTargeted(point) is not None:
						validPlot = False

				if validPlot:
					dominanceZone = simulation.tacticalAnalysisMap().plots.values[point.y][point.x].dominanceZone
					newTarget = TacticalTarget(
						targetType=TacticalTargetType.none,
						target=point,
						targetLeader=LeaderType.none,
						dominanceZone=dominanceZone
					)

					enemyDominatedPlot = simulation.tacticalAnalysisMap().isInEnemyDominatedZone(point)

					# Have a...
					city = simulation.cityAt(tile.point)

					if city is not None:
						if self.player.leader == city.player.leader:
							# ...friendly city?
							newTarget.targetType = TacticalTargetType.cityToDefend
							newTarget.city = city
							newTarget.threatValue = city.threatValue()
							self.allTargets.append(newTarget)
						elif diplomacyAI.isAtWarWith(city.player):
							# ... enemy city
							newTarget.targetType = TacticalTargetType.city
							newTarget.city = city
							newTarget.threatValue = city.threatValue()
							self.allTargets.append(newTarget)
					else:
						unit = simulation.unitAt(tile.point, UnitMapType.combat)
						if unit is not None:
							if diplomacyAI.isAtWarWith(unit.player):
								# ... enemy unit?
								newTarget.targetType = TacticalTargetType.lowPriorityUnit
								newTarget.targetLeader = unit.player.leader
								newTarget.unit = unit
								newTarget.damage = unit.damage()
								self.allTargets.append(newTarget)
								continue

						if tile.hasImprovement(ImprovementType.barbarianCamp):
							# ... undefended camp?
							newTarget.targetType = TacticalTargetType.barbarianCamp
							newTarget.targetLeader = LeaderType.barbar
							newTarget.tile = tile
							self.allTargets.append(newTarget)

						elif tile.hasImprovement(ImprovementType.goodyHut):
							# ... goody hut?
							newTarget.targetType = TacticalTargetType.ancientRuins
							newTarget.tile = tile
							self.allTargets.append(newTarget)

						elif diplomacyAI.isAtWarWith(tile.owner()) and not tile.hasImprovement(ImprovementType.none) and \
							not tile.canBePillaged() and not tile.hasResource(ResourceType.none, self.player) and \
							not enemyDominatedPlot:
							# ... enemy resource improvement?

							# On land, civs only target improvements built on resources
							if tile.hasResource(ResourceUsage.strategic, self.player) or \
								tile.hasResource(ResourceUsage.luxury, self.player) or tile.terrain().isWater() or \
								self.player.leader == LeaderType.barbar:

								if tile.terrain().isWater() and self.player.leader == LeaderType.barbar:
									continue
								else:
									newTarget.targetType = TacticalTargetType.improvement
									newTarget.targetLeader = tile.owner().leader
									newTarget.tile = tile
									self.allTargets.append(newTarget)

						# Or forts / citadels!
						elif diplomacyAI.isAtWarWith(tile.owner()) and (tile.hasImprovement(ImprovementType.fort) and
																		tile.hasImprovement(ImprovementType.citadelle)):
							newTarget.targetType = TacticalTargetType.improvement
							newTarget.targetLeader = tile.owner().leader
							newTarget.tile = tile
							self.allTargets.append(newTarget)

						# ... enemy civilian( or embarked) unit?
						elif unit.player.leader != self.player.leader:
							if unit is not None:
								if diplomacyAI.isAtWarWith(unit.player) and not unit.canDefend():
									newTarget.targetType = TacticalTargetType.lowPriorityUnit
									newTarget.targetLeader = unit.player.leader
									newTarget.unit = unit

									if unit.isEmbarked():
										if unit.isCombatUnit():
											newTarget.targetType = TacticalTargetType.embarkedMilitaryUnit
										else:
											newTarget.targetType = TacticalTargetType.embarkedCivilian
									else:
										numberOfCities = len(simulation.citiesOf(self.player))
										if self.isVeryHighPriorityCivilianTarget(newTarget):
											# AI_TACTICAL_TARGET_VERY_HIGH_PRIORITY_CIVILIAN
											newTarget.targetType = TacticalTargetType.veryHighPriorityCivilian
										elif self.isHighPriorityCivilianTarget(newTarget, simulation.currentTurn,
																			   numberOfCities):
											newTarget.targetType = TacticalTargetType.highPriorityCivilian
										elif self.isMediumPriorityCivilianTarget(newTarget, simulation.currentTurn):
											newTarget.targetType = TacticalTargetType.mediumPriorityCivilian

									self.allTargets.append(newTarget)

							elif self.player.leader == tile.owner().leader and tile.defenseModifierFor(
								self.player) > 0 and \
								dangerPlotsAI.dangerAt(point) > 0.0:
								# ... defensive bastion?
								defenseCity = simulation.friendlyCityAdjacentTo(point, self.player)
								if defenseCity is not None:
									newTarget.targetType = TacticalTargetType.defensiveBastion
									newTarget.tile = tile
									newTarget.threatValue = defenseCity.threatValue() + int(
										dangerPlotsAI.dangerAt(point))
									self.allTargets.append(newTarget)

							elif self.player.leader == tile.owner().leader and \
								not tile.hasImprovement(ImprovementType.none) and \
								not tile.hasImprovement(ImprovementType.goodyHut) and tile.canBePillaged():
								# ... friendly improvement?
								newTarget.targetType = TacticalTargetType.improvementToDefend
								newTarget.tile = tile
								self.allTargets.append(newTarget)

		# POST - PROCESSING ON TARGETS

		# Mark enemy units threatening our cities( or camps) as priority targets
		if self.player.leader == LeaderType.barbar:
			self.identifyPriorityBarbarianTargets(simulation)
		else:
			self.identifyPriorityTargets(simulation)

		# Also add some priority targets that we'd like to hit just because of their unit type (e.g. catapults)
		self.identifyPriorityTargetsByType(simulation)

		# Remove extra targets
		self.eliminateNearbyBlockadePoints()

		# Sort remaining targets by aux data( if used for that target type)
		self.allTargets.sort(key=lambda target: target.threatValue)

	def identifyPriorityBarbarianTargets(self, simulation):
		"""Mark units that can damage our barbarian camps as priority targets"""
		mapSize = simulation.mapSize()

		for x in range(mapSize.width()):
			for y in range(mapSize.height()):
				point = HexPoint(x, y)
				tile = simulation.tileAt(point)

				if tile.hasImprovement(ImprovementType.barbarianCamp):
					for unitTarget in self.unitTargets():
						priorityTarget = False
						if unitTarget.targetType != TacticalTargetType.highPriorityUnit:
							enemyUnit = simulation.visibleEnemyAt(unitTarget.target, self.player)
							if enemyUnit is not None:
								if enemyUnit.canAttackRanged() and \
									enemyUnit.rangedCombatStrengthAgainst(None, None, tile, attacking=True,
																		  simulation=simulation) > \
									enemyUnit.attackStrengthAgainst(None, None, tile, simulation=simulation):

									if enemyUnit.location.distance(point) <= enemyUnit.range():
										priorityTarget = True
								elif enemyUnit.canReachAt(point, turns=1, simulation=simulation):
									priorityTarget = True

								if priorityTarget:
									unitTarget.targetType = TacticalTargetType.highPriorityUnit

		return

	def identifyPriorityTargetsByType(self, simulation):
		"""Mark units that we'd like to make opportunity attacks on because of their unit type (e.g. catapults)"""
		# Look through all the enemies we can see
		for target in self.allTargets:
			# Don't consider units that are already medium priority
			if target.targetType == TacticalTargetType.highPriorityUnit or target.targetType == TacticalTargetType.lowPriorityUnit:
				# Ranged units will always be medium priority targets
				if target.unit is not None:
					if target.unit.canAttackRanged():
						target.targetType = TacticalTargetType.mediumPriorityUnit

			# Don't consider units that are already high priority
			if target.targetType == TacticalTargetType.mediumPriorityUnit or target.targetType == TacticalTargetType.lowPriorityUnit:
				if target.unit is not None:
					tile = simulation.tileAt(target.unit.location)
					if tile is not None:
						# Units defending citadels will always be high priority targets
						if tile.hasImprovement(ImprovementType.fort) or tile.hasImprovement(ImprovementType.citadelle):
							target.targetType = TacticalTargetType.highPriorityUnit

		return

	def eliminateNearbyBlockadePoints(self):
		"""Don't allow tiles within 2 to both be blockade points"""
		# // fatalError("not implemented yet")
		#
		#         /*// First, sort the sentry points by priority
		#         self.naval
		#         std::stable_sort(m_NavalResourceBlockadePoints.begin(), m_NavalResourceBlockadePoints.end());
		#
		#         // Create temporary copy of list
		#         TacticalList tempPoints;
		#         tempPoints = m_NavalResourceBlockadePoints;
		#
		#         // Clear out main list
		#         m_NavalResourceBlockadePoints.clear();
		#
		#         // Loop through all points in copy
		#         TacticalList::iterator it, it2;
		#         for (it = tempPoints.begin(); it != tempPoints.end(); ++it)
		#         {
		#             bool bFoundAdjacent = false;
		#
		#             // Is it adjacent to a point in the main list?
		#             for (it2 = m_NavalResourceBlockadePoints.begin(); it2 != m_NavalResourceBlockadePoints.end(); ++it2)
		#             {
		#                 if (plotDistance(it->GetTargetX(), it->GetTargetY(), it2->GetTargetX(), it2->GetTargetY()) <= 2)
		#                 {
		#                     bFoundAdjacent = true;
		#                     break;
		#                 }
		#             }
		#
		#             if (!bFoundAdjacent)
		#             {
		#                 m_NavalResourceBlockadePoints.push_back(*it);
		#             }
		#         }
		#
		#         // Now copy all points into main target list
		#         for (it = m_NavalResourceBlockadePoints.begin(); it != m_NavalResourceBlockadePoints.end(); ++it)
		#         {
		#             m_AllTargets.push_back(*it);
		#         } */
		pass

	def processDominanceZones(self, simulation):
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		# Barbarian processing is straightforward - - just one big list of priorities and everything is considered at once
		if self.player.leader == LeaderType.barbar:
			self.establishBarbarianPriorities(simulation.currentTurn)
			self.extractTargets()
			self.assignBarbarianMoves(simulation)
		else:
			self.establishTacticalPriorities()
			self.updatePostures(simulation)

			# Proceed in priority order
			for move in self.movePriorityList:
				if move.priority < 0:
					continue

				if move.moveType.dominanceZoneMove():
					for dominanceZone in tacticalAnalysisMap.dominanceZones:
						self.currentDominanceZone = dominanceZone
						postureType = self.findPostureTypeFor(dominanceZone)

						# Is this move of the right type for this zone?
						match = False
						if move.moveType == TacticalMoveType.closeOnTarget:  # This one is okay for all zones
							match = True
						elif postureType == TacticalPostureType.withdraw and \
							move.moveType == TacticalMoveType.postureWithdraw:
							match = True
						elif postureType == TacticalPostureType.sitAndBombard and \
							move.moveType == TacticalMoveType.postureSitAndBombard:
							match = True
						elif postureType == TacticalPostureType.attritFromRange and \
							move.moveType == TacticalMoveType.postureAttritFromRange:
							match = True
						elif postureType == TacticalPostureType.exploitFlanks and \
							move.moveType == TacticalMoveType.postureExploitFlanks:
							match = True
						elif postureType == TacticalPostureType.steamRoll and \
							move.moveType == TacticalMoveType.postureSteamroll:
							match = True
						elif postureType == TacticalPostureType.surgicalCityStrike and \
							move.moveType == TacticalMoveType.postureSurgicalCityStrike:
							match = True
						elif postureType == TacticalPostureType.hedgehog and \
							move.moveType == TacticalMoveType.postureHedgehog:
							match = True
						elif postureType == TacticalPostureType.counterAttack and \
							move.moveType == TacticalMoveType.postureCounterAttack:
							match = True
						elif postureType == TacticalPostureType.shoreBombardment and \
							move.moveType == TacticalMoveType.postureShoreBombardment:
							match = True
						elif dominanceZone.dominanceFlag == TacticalDominanceType.enemy and \
							dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly and \
							move.moveType == TacticalMoveType.emergencyPurchases:
							match = True

						if match:
							if not self.useThisDominanceZone(dominanceZone):
								continue

							self.extractTargetsFor(dominanceZone)

							# Must have some moves to continue or it must be land around an enemy city (which we always want to process because
							# we might have an operation targeting it)
							if len(self.zoneTargets) == 0 and dominanceZone.territoryType != TacticalDominanceTerritoryType.tempZone and \
								(dominanceZone.territoryType != TacticalDominanceTerritoryType.enemy or dominanceZone.isWater):
								continue

							self.assignTacticalMove(move, simulation)
				else:
					self.extractTargets()
					self.assignTacticalMove(move, simulation)

		return

	def establishBarbarianPriorities(self, turn: int):
		"""Choose which tactics the barbarians should emphasize this turn"""
		# Only establish priorities once per turn
		if turn <= self.movePriorityTurn:
			return

		self.movePriorityList = []
		self.movePriorityTurn = turn

		# Loop through each possible tactical move(other than "none" or "unassigned")
		for barbarianTacticalMove in TacticalMoveType.allBarbarianMoves():
			priority = barbarianTacticalMove.priority()

			# Make sure base priority is not negative
			if priority >= 0:

				# Finally, add a random die roll to each priority
				priority += random.randint(-2, 2)  # AI_TACTICAL_MOVE_PRIORITY_RANDOMNESS

				# Store off this move and priority
				move = TacticalMove()
				move.moveType = barbarianTacticalMove
				move.priority = priority
				self.movePriorityList.append(move)

		self.movePriorityList.sort()
		return

	def extractTargets(self, dominanceZone: Optional[TacticalDominanceZone] = None):
		"""Sift through the target list and find just those that apply to the dominance zone we are currently looking at"""
		self.zoneTargets = []

		for target in self.allTargets:
			valid = False

			if dominanceZone is not None:
				domain: UnitDomainType = UnitDomainType.sea if dominanceZone.isWater else UnitDomainType.land
				valid = target.isTargetValidIn(domain)
			else:
				valid = True

			if valid:
				if dominanceZone is None or dominanceZone == target.dominanceZone:
					self.zoneTargets.append(target)
				else:
					# Not obviously in this zone, but if within 2 of city we want them anyway
					city = dominanceZone.closestCity
					if city is not None:
						if target.target.distanceTo(city.location) <= 2:
							self.zoneTargets.append(target)

		print(f"targets extracted: {len(self.zoneTargets)}")
		return

	def assignBarbarianMoves(self, simulation):
		"""Choose which tactics to run and assign units to it (barbarian version)"""
		for move in self.movePriorityList:
			if move.moveType == TacticalMoveType.barbarianCaptureCity:
				# AI_TACTICAL_BARBARIAN_CAPTURE_CITY
				self.plotCaptureCityMoves(simulation)
			elif move.moveType == TacticalMoveType.barbarianDamageCity:
				# AI_TACTICAL_BARBARIAN_DAMAGE_CITY
				self.plotDamageCityMoves(simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyHighPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_HIGH_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyMediumPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_MEDIUM_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyLowPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_LOW_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianMoveToSafety:
				# AI_TACTICAL_BARBARIAN_MOVE_TO_SAFETY
				self.plotMovesToSafety(combatUnits=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritHighPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_HIGH_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritMediumPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_MEDIUM_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritLowPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_LOW_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPillage:
				# AI_TACTICAL_BARBARIAN_PILLAGE
				self.plotPillageMoves(TacticalTargetType.improvementResource, firstPass=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPillageCitadel:
				# AI_TACTICAL_BARBARIAN_PILLAGE_CITADEL
				self.plotPillageMoves(TacticalTargetType.citadel, firstPass=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPillageNextTurn:
				# AI_TACTICAL_BARBARIAN_PILLAGE_NEXT_TURN
				self.plotPillageMoves(TacticalTargetType.citadel, firstPass=False, simulation=simulation)
				self.plotPillageMoves(TacticalTargetType.improvementResource, firstPass=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianBlockadeResource:
				# AI_TACTICAL_BARBARIAN_PRIORITY_BLOCKADE_RESOURCE \
				# PlotBlockadeImprovementMoves();
				pass
			elif move.moveType == TacticalMoveType.barbarianCivilianAttack:
				# AI_TACTICAL_BARBARIAN_CIVILIAN_ATTACK
				self.plotCivilianAttackMoves(TacticalTargetType.veryHighPriorityCivilian, simulation)
				self.plotCivilianAttackMoves(TacticalTargetType.highPriorityCivilian, simulation)
				self.plotCivilianAttackMoves(TacticalTargetType.mediumPriorityCivilian, simulation)
				self.plotCivilianAttackMoves(TacticalTargetType.lowPriorityCivilian, simulation)
			elif move.moveType == TacticalMoveType.barbarianCampDefense:
				# AI_TACTICAL_BARBARIAN_CAMP_DEFENSE
				self.plotCampDefenseMoves(simulation)
			elif move.moveType == TacticalMoveType.barbarianAggressiveMove:
				# AI_TACTICAL_BARBARIAN_AGGRESSIVE_MOVE
				self.plotBarbarianMove(aggressive=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianPassiveMove:
				# AI_TACTICAL_BARBARIAN_PASSIVE_MOVE
				self.plotBarbarianMove(aggressive=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDesperateAttack:
				# AI_TACTICAL_BARBARIAN_DESPERATE_ATTACK
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianEscortCivilian:
				# AI_TACTICAL_BARBARIAN_ESCORT_CIVILIAN
				self.plotBarbarianCivilianEscortMove(simulation)
			elif move.moveType == TacticalMoveType.barbarianPlunderTradeUnit:
				# AI_TACTICAL_BARBARIAN_PLUNDER_TRADE_UNIT
				self.plotBarbarianPlunderTradeUnitMove(UnitDomainType.land, simulation)
				self.plotBarbarianPlunderTradeUnitMove(UnitDomainType.sea, simulation)
			elif move.moveType == TacticalMoveType.barbarianGuardCamp:
				self.plotGuardBarbarianCamp( simulation)
			else:
				print(f"not implemented: TacticalAI - {move.moveType}")

		self.reviewUnassignedBarbarianUnits( simulation)

	def plotGuardBarbarianCamp(self, simulation):
		"""Assigns a barbarian to go protect an undefended camp"""
		if not self.player.isBarbarian():
			return

		self.currentMoveUnits = []

		for loopUnit in self.currentTurnUnits:
			# is unit already at a camp?
			tile = simulation.tileAt(loopUnit.location)
			if tile is not None:
				if tile.hasImprovement(ImprovementType.barbarianCamp):
					unit = TacticalUnit(loopUnit)
					self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeGuardBarbarianCamp(simulation)

		return

	def plotBarbarianCivilianEscortMove(self, simulation):
		"""Escort captured civilians back to barbarian camps"""
		if not self.player.isBarbarian():
			return

		self.currentMoveUnits = []

		for currentTurnUnit in self.currentTurnUnits:
			# Find any civilians we may have "acquired" from the civilizations
			if not currentTurnUnit.canAttack():
				unit = TacticalUnit(currentTurnUnit)
				self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeBarbarianCivilianEscortMove(simulation)

		return

	def plotBarbarianPlunderTradeUnitMove(self, domain: UnitDomainType, simulation):
		"""Plunder trade routes"""
		targetType: TacticalTargetType = TacticalTargetType.none
		navalOnly = False

		if domain == UnitDomainType.land:
			targetType = TacticalTargetType.tradeUnitLand
		elif domain == UnitDomainType.sea:
			targetType = TacticalTargetType.tradeUnitSea
			navalOnly = True

		if targetType == TacticalTargetType.none:
			return

		for target in self.zoneTargetsFor(targetType):
			# See what units we have who can reach target this turn
			if self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=0, noRangedUnits=False, navalOnly=navalOnly, simulation=simulation):
				# Queue best one up to capture it
				self.executePlunderTradeUnitAt(target.target, simulation)

		return

	def zoneTargetsFor(self, targetType: TacticalTargetType) -> [TacticalTarget]:
		"""Find the first target of a requested type in current dominance zone (call after ExtractTargetsForZone())"""
		tempTargets: [TacticalTarget] = []
		for zoneTarget in self.zoneTargets:
			if targetType == TacticalTargetType.none or zoneTarget.targetType == targetType:
				tempTargets.append(zoneTarget)

		return tempTargets

	def plotDestroyUnitMoves(self, targetType: TacticalTargetType, mustBeAbleToKill: bool, attackAtPoorOdds: bool, simulation):
		"""Assign a group of units to attack each unit we think we can destroy"""
		requiredDamage: int = 0
		expectedDamage: int = 0

		# See how many moves of this type we can execute
		for target in self.zoneTargetsFor(targetType):
			unitCanAttack = False
			cityCanAttack = False

			if target.target is not None:
				targetLocation = target.target
				tile = simulation.tileAt(targetLocation)

				if tile is None:
					continue

				defender = simulation.unitAt(targetLocation, UnitMapType.combat)

				if defender is not None:
					unitCanAttack = self.findUnitsWithinStrikingDistanceTowards(tile.point, numTurnsAway=1, noRangedUnits=False, simulation=simulation)
					cityCanAttack = self.findCitiesWithinStrikingDistanceOf(targetLocation, simulation)

					if unitCanAttack or cityCanAttack:
						expectedDamage = self.computeTotalExpectedDamage(target, tile, simulation)
						expectedDamage += self.computeTotalExpectedBombardDamageAgainst(defender, simulation)
						requiredDamage = defender.healthPoints()

						target.damage = requiredDamage

						if not mustBeAbleToKill:
							# Attack no matter what
							if attackAtPoorOdds:
								self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=False, simulation=simulation)
							else:
								# If we can at least knock the defender to 40 % strength with our combined efforts, go ahead even if each individual attack isn't favorable
								mustInflictWhatWeTake = True
								if expectedDamage >= (requiredDamage * 40) / 100:
									mustInflictWhatWeTake = False

								self.executeAttack(target, tile, inflictWhatWeTake=mustInflictWhatWeTake, mustSurviveAttack=True, simulation=simulation)
						else:
							# Do we have enough firepower to destroy it?
							if expectedDamage > requiredDamage:
								self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=(targetType != TacticalTargetType.highPriorityUnit), simulation=simulation)

			return

	def plotPillageMoves(self, targetType: TacticalTargetType, firstPass: bool, simulation):
		"""Assigns units to pillage enemy improvements"""
		for target in self.zoneTargetsFor(targetType):
			# // try paratroopers first, not because they are more effective, just because it looks cooler...
			# / * if (bFirstPass & & FindParatroopersWithinStrikingDistance(pPlot))
			# {
			# # Queue best one up to capture it
			# ExecuteParadropPillage(pPlot);
			# } else * /
			if firstPass and self.findUnitsWithinStrikingDistance(target.target, numTurnsAway=0, noRangedUnits=False, navalOnly=False, mustMoveThrough=True, includeBlockedUnits=False, willPillage=True, simulation=simulation):
				# Queue best one up to capture it
				self.executePillageAt(target.target, simulation)

			elif not firstPass and self.findUnitsWithinStrikingDistance(target.target, numTurnsAway=2, noRangedUnits=False, navalOnly=False, mustMoveThrough=False, includeBlockedUnits=False, willPillage=True, simulation=simulation):
				# No one can reach it this turn, what about next turn?
				self.executeMoveToTarget(target.target, garrisonIfPossible=False, simulation=simulation)

		return

	def plotCivilianAttackMoves(self, targetType: TacticalTargetType, simulation):
		"""Assigns units to capture undefended civilians"""
		for target in self.zoneTargetsFor(targetType):
			# See what units we have who can reach target this turn
			if self.findUnitsWithinStrikingDistance(target.target, numTurnsAway=1, noRangedUnits=False, navalOnly=False, mustMoveThrough=False, includeBlockedUnits=False, willPillage=False, targetUndefended=True, simulation=simulation):
				# Queue best one up to capture it
				self.executeCivilianCapture(target.target, simulation)

		return
