import random
import sys
from typing import Optional

from core.base import ExtendedEnum
from game.ai.baseTypes import PlayerStateAllWars
from game.civilizations import LeaderType
from game.unitMissions import UnitMission
from game.unitTypes import BitArray, UnitTaskType, UnitMapType, UnitMissionType
from map.base import Array2D, Size, HexArea, HexPoint, HexDirection
from map.improvements import ImprovementType
from map.path_finding.finder import AStarPathfinder
from map.types import UnitDomainType, ResourceUsage, ResourceType, TerrainType, UnitMovementType


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
	garrisonToAllowBombards = 'garrisonToAllowBombards'  # TACTICAL_GARRISON_TO_ALLOW_BOMBARD
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

	@staticmethod
	def allPlayerMoves() -> [TacticalMoveType]:
		return [
			TacticalMoveType.moveNoncombatantsToSafety,
			TacticalMoveType.captureCity,
			TacticalMoveType.damageCity,
			TacticalMoveType.destroyHighUnit,
			TacticalMoveType.destroyMediumUnit,
			TacticalMoveType.destroyLowUnit,
			TacticalMoveType.toSafety,
			TacticalMoveType.attritHighUnit,
			TacticalMoveType.attritMediumUnit,
			TacticalMoveType.attritLowUnit,
			TacticalMoveType.reposition,
			TacticalMoveType.barbarianCamp,
			TacticalMoveType.pillage,
			TacticalMoveType.civilianAttack,
			TacticalMoveType.safeBombards,
			TacticalMoveType.heal,
			TacticalMoveType.ancientRuins,
			TacticalMoveType.garrisonToAllowBombards,
			TacticalMoveType.bastionAlreadyThere,
			TacticalMoveType.garrisonAlreadyThere,
			TacticalMoveType.guardImprovementAlreadyThere,
			TacticalMoveType.bastionOneTurn,
			TacticalMoveType.garrisonOneTurn,
			TacticalMoveType.guardImprovementOneTurn,
			TacticalMoveType.airSweep,
			TacticalMoveType.airIntercept,
			TacticalMoveType.airRebase,
			TacticalMoveType.closeOnTarget,
			TacticalMoveType.moveOperation,
			TacticalMoveType.emergencyPurchases
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
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=-1
			)
		elif self == TacticalMoveType.barbarianGuardCamp:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=200
			)
		elif self == TacticalMoveType.unassigned:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=-1)
		elif self == TacticalMoveType.moveNoncombatantsToSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=0
			)
		elif self == TacticalMoveType.captureCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0,
				priority=150
			)
		elif self == TacticalMoveType.damageCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0,
				priority=15
			)
		elif self == TacticalMoveType.destroyHighUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=140
			)
		elif self == TacticalMoveType.destroyMediumUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=120
			)
		elif self == TacticalMoveType.destroyLowUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=110
			)
		elif self == TacticalMoveType.closeOnTarget:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=45
			)
		elif self == TacticalMoveType.toSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=11
			)
		elif self == TacticalMoveType.attritHighUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=17
			)
		elif self == TacticalMoveType.attritMediumUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=15
			)
		elif self == TacticalMoveType.attritLowUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=12
			)
		elif self == TacticalMoveType.reposition:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=50, defenseFlavorWeight=50,
				priority=1
			)
		elif self == TacticalMoveType.barbarianCamp:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.pillage:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0,
				priority=40
			)
		elif self == TacticalMoveType.civilianAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0,
				priority=65
			)
		elif self == TacticalMoveType.safeBombards:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0,
				priority=60
			)
		elif self == TacticalMoveType.heal:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=8
			)
		elif self == TacticalMoveType.ancientRuins:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=50, defenseFlavorWeight=50,
				priority=25
			)
		elif self == TacticalMoveType.garrisonToAllowBombards:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=20
			)
		elif self == TacticalMoveType.bastionAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=7
			)
		elif self == TacticalMoveType.garrisonAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=6
			)
		elif self == TacticalMoveType.guardImprovementAlreadyThere:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=5
			)
		elif self == TacticalMoveType.bastionOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=4
			)
		elif self == TacticalMoveType.garrisonOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=3
			)
		elif self == TacticalMoveType.guardImprovementOneTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=True, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=2
			)
		elif self == TacticalMoveType.airSweep:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=100, defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.airIntercept:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=20
			)
		elif self == TacticalMoveType.airRebase:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=100,
				priority=1
			)
		elif self == TacticalMoveType.postureWithdraw:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=101
			)
		elif self == TacticalMoveType.postureSitAndBombard:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=105
			)
		elif self == TacticalMoveType.postureAttritFromRange:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=104
			)
		elif self == TacticalMoveType.postureExploitFlanks:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=107
			)
		elif self == TacticalMoveType.postureSteamroll:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=108
			)
		elif self == TacticalMoveType.postureSurgicalCityStrike:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=106
			)
		elif self == TacticalMoveType.postureHedgehog:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=50
			)
		elif self == TacticalMoveType.postureCounterAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=103
			)
		elif self == TacticalMoveType.postureShoreBombardment:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=100
			)
		elif self == TacticalMoveType.moveOperation:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=80
			)
		elif self == TacticalMoveType.emergencyPurchases:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=True, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=200
			)

		# https://github.com/chvrsi/BarbariansEvolved/blob/00a6feec72fa7d95ef026d821f008bdbbf3ee3ab/xml/BarbarianDefines.xml
		elif self == TacticalMoveType.barbarianCaptureCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=9
			)
		elif self == TacticalMoveType.barbarianDamageCity:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=5
			)
		elif self == TacticalMoveType.barbarianDestroyHighPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=16
			)
		elif self == TacticalMoveType.barbarianDestroyMediumPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=15
			)
		elif self == TacticalMoveType.barbarianDestroyLowPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=14
			)
		elif self == TacticalMoveType.barbarianMoveToSafety:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.barbarianAttritHighPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.barbarianAttritMediumPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=7
			)
		elif self == TacticalMoveType.barbarianAttritLowPriorityUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=6
			)
		elif self == TacticalMoveType.barbarianPillage:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=12
			)
		elif self == TacticalMoveType.barbarianBlockadeResource:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=10
			)
		elif self == TacticalMoveType.barbarianCivilianAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=13
			)
		elif self == TacticalMoveType.barbarianAggressiveMove:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=3
			)
		elif self == TacticalMoveType.barbarianPassiveMove:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=-1
			)
		elif self == TacticalMoveType.barbarianCampDefense:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=13
			)
		elif self == TacticalMoveType.barbarianDesperateAttack:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=0
			)
		elif self == TacticalMoveType.barbarianEscortCivilian:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=30
			)
		elif self == TacticalMoveType.barbarianPlunderTradeUnit:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=20
			)
		elif self == TacticalMoveType.barbarianPillageCitadel:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=14
			)
		elif self == TacticalMoveType.barbarianPillageNextTurn:
			return TacticalMoveTypeData(
				operationsCanRecruit=False, dominanceZoneMove=False, offenseFlavorWeight=0, defenseFlavorWeight=0,
				priority=4
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
		// !  brief        The posture an AI has adopted for fighting in a specific dominance zone
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
					tile = simulation.tileAt(HexPoint(x, y))

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

	def populateCellAt(self, x: int, y: int, tile, simulation) -> bool:
		"""Update data for a cell: returns whether to add to dominance zones"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		cell = self.plots.values[y][x]

		if tile is not None:
			cell.reset()

			cell.revealed = tile.isDiscoveredBy(self.playerBuild)
			cell.visible = tile.isVisibleTo(self.playerBuild)
			cell.impassableTerrain = tile.isImpassable(UnitMovementType.walk) or tile.isImpassable(
				UnitMovementType.swim)
			cell.water = tile.terrain().isWater()
			cell.ocean = tile.terrain() == TerrainType.ocean

			impassableTerritory = False
			if tile.hasOwner():
				city = simulation.cityAt(HexPoint(x, y))
				if tile.owner().leader != player.leader and diplomacyAI.isAtWarWith(tile.owner()) and \
					not diplomacyAI.isOpenBorderAgreementActiveWith(tile.owner()):
					impassableTerritory = True

				elif city is not None:
					if city.player.leader == player.leader:
						cell.friendlyCity = True
					elif diplomacyAI.isAtWarWith(city.player) or player.isBarbarian():
						cell.enemyCity = True
					else:
						cell.neutralCity = True

				if tile.owner().leader != player.leader:
					cell.ownTerritory = True

				if tile.isFriendlyTerritoryFor(player, simulation):
					cell.friendlyTerritory = True

				if diplomacyAI.isAtWarWith(tile.owner()):
					cell.enemyTerritory = True

				if player.isBarbarian():
					cell.enemyTerritory = True

			else:
				cell.unclaimedTerritory = True

			cell.impassableTerritory = impassableTerritory
			cell.defenseModifier = tile.defenseModifierFor(player)

			unit = simulation.unitAt(HexPoint(x, y), UnitMapType.combat)
			if unit is not None:
				if unit.player.leader == player.leader:
					if unit.isCombatUnit():
						cell.friendlyMilitaryUnit = unit
					else:
						cell.friendlyCivilianUnit = unit
				elif diplomacyAI.isAtWarWith(unit.player) or player.isBarbarian():
					if unit.isCombatUnit():
						cell.enemyMilitaryUnit = unit
					else:
						cell.enemyCivilianUnit = unit
				else:
					if unit.isCombatUnit():
						cell.neutralMilitaryUnit = unit
					else:
						cell.neutralCivilianUnit = unit

			# Figure out whether to add this to a dominance zone
			if cell.impassableTerrain or cell.impassableTerritory or (
				not cell.isRevealed() and not player.isBarbarian()):
				return False

		return True

	def calculateMilitaryStrengths(self, simulation):
		"""Calculate military presences in each owned dominance zone"""
		player = self.playerBuild

		# Loop through the dominance zones
		for dominanceZone in self.dominanceZones:
			if dominanceZone.territoryType == TacticalDominanceTerritoryType.noOwner:
				continue

			closestCity = dominanceZone.closestCity
			if closestCity is not None:
				# Start with strength of the city itself
				strength = closestCity.rangedCombatStrength(None, None) * self.tacticalRange

				if dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
					dominanceZone.friendlyStrength += strength
					dominanceZone.friendlyRangedStrength += closestCity.rangedCombatStrength(None, None)
				else:
					dominanceZone.enemyStrength += strength
					dominanceZone.enemyRangedStrength += closestCity.rangedCombatStrength(None, None)

				# Loop through all of OUR units first
				for unit in simulation.unitsOf(player):
					if unit.isCombatUnit():
						if unit.domain() == UnitDomainType.air or \
							unit.domain() == UnitDomainType.land and not dominanceZone.isWater or \
							unit.domain() == UnitDomainType.sea and dominanceZone.isWater:

							distance = closestCity.location.distance(unit.location)
							multiplier = self.tacticalRange + 1 - distance

							if multiplier > 0:
								unitStrength = unit.attackStrength(None, None, None, simulation)

								if unitStrength == 0 and unit.isEmbarked() and not dominanceZone.isWater:
									unitStrength = unit.baseCombatStrength(ignoreEmbarked=True)

								dominanceZone.friendlyStrength += unitStrength * multiplier * self.unitStrengthMultiplier
								dominanceZone.friendlyRangedStrength += unit.rangedCombatStrength(None, None, None,
																								  attacking=True,
																								  simulation=simulation)

								if unit.range() > self.bestFriendlyRangeValue:
									self.bestFriendlyRangeValue = unit.range()

								dominanceZone.friendlyUnitCount += 1

				# Repeat for all visible enemy units ( or adjacent to visible)
				for otherPlayer in simulation.players:
					if player.isAtWarWith(otherPlayer):
						for loopUnit in simulation.unitsOf(otherPlayer):
							if loopUnit.isCombatUnit():

								if loopUnit.domain() == UnitDomainType.air or \
									(loopUnit.domain() == UnitDomainType.land and not dominanceZone.isWater) or \
									(loopUnit.domain() == UnitDomainType.sea and dominanceZone.isWater):

									plot = simulation.tileAt(loopUnit.location)

									if plot is not None:
										visible = True
										distance = loopUnit.location.distance(closestCity.location)

										if distance <= self.tacticalRange:
											# "4" so unit strength isn't totally dominated by proximity to city
											multiplier = (self.tacticalRange + 4 - distance)
											if not plot.isVisibleTo(player) and \
												not simulation.isAdjacentDiscovered(loopUnit.location, player):
												visible = False

											if multiplier > 0:
												unitStrength = loopUnit.attackStrength(None, None, None, simulation)
												if unitStrength == 0 and loopUnit.isEmbarked() and not dominanceZone.isWater:
													unitStrength = loopUnit.baseCombatStrength(ignoreEmbarked=True)

												if not visible:
													unitStrength /= 2

												dominanceZone.enemyStrength += unitStrength * multiplier * self.unitStrengthMultiplier

												rangedStrength = loopUnit.rangedCombatStrength(None, None, None,
																							   attacking=True,
																							   simulation=simulation)
												if not visible:
													rangedStrength /= 2

												dominanceZone.enemyRangedStrength = rangedStrength

												if visible:
													dominanceZone.enemyUnitCount += 1
													if distance < dominanceZone.rangeClosestEnemyUnit:
														dominanceZone.rangeClosestEnemyUnit = distance

													if loopUnit.isRanged():
														dominanceZone.enemyRangedUnitCount += 1

													if loopUnit.domain() == UnitDomainType.sea:
														dominanceZone.enemyNavalUnitCount += 1

		return

	def prioritizeZones(self, simulation):
		"""Establish order of zone processing for the turn"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		# Loop through the dominance zones
		for dominanceZone in self.dominanceZones:
			# Find the zone and compute dominance here
			dominance = self.calculateDominanceOf(dominanceZone, simulation)
			dominanceZone.dominanceFlag = dominance

			# Establish a base value for the region
			baseValue = 1
			multiplier = 1

			# Temporary zone?
			if dominanceZone.territoryType == TacticalDominanceTerritoryType.tempZone:
				multiplier = 200
			else:
				closestCity = dominanceZone.closestCity

				if closestCity is not None:
					baseValue += closestCity.population()

					if closestCity.isCapital():
						baseValue *= 2

					# How damaged is this city?
					damage = closestCity.damage()
					if damage > 0:
						baseValue *= (damage + 2) / 2

					if player.tacticalAI.isTemporaryZone(closestCity):
						baseValue *= 3

				if not dominanceZone.isWater:
					baseValue *= 8

				# Now compute a multiplier based on current conditions here
				if dominance == TacticalDominanceType.noUnitsPresent or dominance == TacticalDominanceType.notVisible:
					pass  # NOOP
				elif dominance == TacticalDominanceType.friendly:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier = 4
					elif dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier = 1
				elif dominance == TacticalDominanceType.even:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier = 3
					elif dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier = 3
				elif dominance == TacticalDominanceType.enemy:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier = 2
					elif dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier = 4

				if diplomacyAI.stateOfAllWars == PlayerStateAllWars.winning:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.enemy:
						multiplier *= 2
				elif diplomacyAI.stateOfAllWars == PlayerStateAllWars.losing:
					if dominanceZone.territoryType == TacticalDominanceTerritoryType.friendly:
						multiplier *= 2

			if baseValue * multiplier <= 0:
				raise Exception("Invalid Dominance Zone Value")

			dominanceZone.dominanceValue = baseValue * multiplier

		self.dominanceZones.sort(key=lambda zone: zone.dominanceValue, reverse=True)

	def buildEnemyUnitList(self, simulation):
		"""Find all our enemies (combat units)"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		self.enemyUnits = []

		for otherPlayer in simulation.players:
			# for each opposing civ
			if player.isAlive() and diplomacyAI.isAtWarWith(otherPlayer):
				for unit in simulation.unitsOf(otherPlayer):
					if unit.canAttack():
						self.enemyUnits.append(unit)

		return

	def markCellsNearEnemy(self, simulation):
		"""Indicate the plots we might want to move to that the enemy can attack"""
		player = self.playerBuild
		diplomacyAI = player.diplomacyAI

		# Look at every cell on the map
		for x in range(self.plots.width):
			for y in range(self.plots.height):
				marked = False
				pt = HexPoint(x, y)
				plot = self.plots.values[y][x]
				tile = simulation.tileAt(pt)

				if tile is not None:
					if tile.isDiscoveredBy(self.playerBuild) and not tile.isImpassable(UnitMovementType.walk):
						if not tile.isVisibleToEnemy(player, simulation):
							plot.notVisibleToEnemy = True

						else:
							# loop all enemy units
							for enemyUnit in self.enemyUnits:
								if marked:
									break

								pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
									enemyUnit.movementType(),
									enemyUnit.player,
									unitMapType=UnitMapType.combat,
									canEmbark=enemyUnit.player.canEmbark(),
									canEnterOcean=enemyUnit.player.canEnterOcean()
								)

								pathFinder = AStarPathfinder(pathFinderDataSource)
								unitArea = simulation.areaOf(enemyUnit.location)
								if tile.area == unitArea:
									# Distance check before hitting pathfinder
									distance = enemyUnit.location.distance(tile.point)
									if distance == 0:
										plot.subjectToAttack = True
										plot.enemyCanMovePast = True
										marked = True

									# TEMPORARY OPTIMIZATION: Assumes can't use roads or RR
									elif distance <= enemyUnit.baseMoves(UnitDomainType.none, simulation):
										path = pathFinder.shortestPath(enemyUnit.location, tile.point)

										if path is not None:
											turnsToReach = len(path.points()) / enemyUnit.moves()

											if turnsToReach <= 1:
												plot.subjectToAttack = True

											if turnsToReach == 0:
												plot.enemyCanMovePast = True
												marked = True

							# Check adjacent plots for enemy citadels
							if not plot.subjectToAttack:
								for dir in list(HexDirection):
									adjacent = tile.point.neighbor(dir)
									adjacentTile = simulation.tileAt(adjacent)

									if adjacentTile is not None:
										if adjacentTile.hasOwner():
											if diplomacyAI.isAtWarWith(adjacentTile.owner()):
												if adjacentTile.hasImprovement(ImprovementType.citadelle):
													plot.subjectToAttack = True
													break

		return

	def isInEnemyDominatedZone(self, point: HexPoint) -> bool:
		"""Is this plot in dangerous territory?"""
		cell = self.plots.values[point.y][point.x]

		for dominanceZone in self.dominanceZones:
			if cell.dominanceZone == dominanceZone:
				return dominanceZone.dominanceFlag == TacticalDominanceType.enemy or \
					dominanceZone.dominanceFlag == TacticalDominanceType.notVisible

		return False


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

	def __init__(self, attackStrength: int = 0, expectedTargetDamage: int = 0, city=None):
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

			elif not unit.isCombatUnit() and not unit.isGreatPerson():
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

						elif tile.owner() is not None and diplomacyAI.isAtWarWith(tile.owner()) and \
							not tile.hasImprovement(ImprovementType.none) and \
							not tile.canBePillaged() and not tile.hasResource(ResourceType.none, self.player) and \
							not enemyDominatedPlot:
							# ... enemy resource improvement?

							# On land, civilizations only target improvements built on resources
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
						elif tile.owner() is not None and diplomacyAI.isAtWarWith(tile.owner()) and \
							(tile.hasImprovement(ImprovementType.fort) and tile.hasImprovement(ImprovementType.citadelle)):
							newTarget.targetType = TacticalTargetType.improvement
							newTarget.targetLeader = tile.owner().leader
							newTarget.tile = tile
							self.allTargets.append(newTarget)

						# ... enemy trade route?
						# elif if tile.owner() is not None and diplomacyAI.isAtWarWith(tile.owner()) and \
						#	tile.route
						# else if (atWar (m_pPlayer->getTeam(), pLoopPlot->getTeam()) &&
						# 					pLoopPlot->getRouteType() != NO_ROUTE && !pLoopPlot->IsRoutePillaged() && pLoopPlot->IsTradeRoute() && !bEnemyDominatedPlot)
						# 				{
						# 					newTarget.SetTargetType(AI_TACTICAL_TARGET_IMPROVEMENT);
						# 					newTarget.SetTargetPlayer(pLoopPlot->getOwner());
						# 					newTarget.SetAuxData((void *)pLoopPlot);
						# 					m_AllTargets.push_back(newTarget);
						# 				}

						# ... enemy civilian (or embarked) unit?
						elif unit is not None and unit.player.leader != self.player.leader:
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
		#                     bFoundAdjacent = True;
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
							if len(
								self.zoneTargets) == 0 and dominanceZone.territoryType != TacticalDominanceTerritoryType.tempZone and \
								(
									dominanceZone.territoryType != TacticalDominanceTerritoryType.enemy or dominanceZone.isWater):
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
				self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=True,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyMediumPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_MEDIUM_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=True,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianDestroyLowPriorityUnit:
				# AI_TACTICAL_BARBARIAN_DESTROY_LOW_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=True,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianMoveToSafety:
				# AI_TACTICAL_BARBARIAN_MOVE_TO_SAFETY
				self.plotMovesToSafety(combatUnits=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritHighPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_HIGH_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritMediumPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_MEDIUM_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=False, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianAttritLowPriorityUnit:
				# AI_TACTICAL_BARBARIAN_ATTRIT_LOW_PRIORITY_UNIT
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=False, simulation=simulation)
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
				self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False,
										  attackAtPoorOdds=True, simulation=simulation)
			elif move.moveType == TacticalMoveType.barbarianEscortCivilian:
				# AI_TACTICAL_BARBARIAN_ESCORT_CIVILIAN
				self.plotBarbarianCivilianEscortMove(simulation)
			elif move.moveType == TacticalMoveType.barbarianPlunderTradeUnit:
				# AI_TACTICAL_BARBARIAN_PLUNDER_TRADE_UNIT
				self.plotBarbarianPlunderTradeUnitMove(UnitDomainType.land, simulation)
				self.plotBarbarianPlunderTradeUnitMove(UnitDomainType.sea, simulation)
			elif move.moveType == TacticalMoveType.barbarianGuardCamp:
				self.plotGuardBarbarianCamp(simulation)
			else:
				print(f"not implemented: TacticalAI - {move.moveType}")

		self.reviewUnassignedBarbarianUnits(simulation)

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
			if self.findUnitsWithinStrikingDistanceTowards(target.target, numTurnsAway=0, noRangedUnits=False,
														   navalOnly=navalOnly, simulation=simulation):
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

	def plotDestroyUnitMoves(self, targetType: TacticalTargetType, mustBeAbleToKill: bool, attackAtPoorOdds: bool,
							 simulation):
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
					unitCanAttack = self.findUnitsWithinStrikingDistanceTowards(tile.point, numTurnsAway=1,
																				noRangedUnits=False,
																				simulation=simulation)
					cityCanAttack = self.findCitiesWithinStrikingDistanceOf(targetLocation, simulation)

					if unitCanAttack or cityCanAttack:
						expectedDamage = self.computeTotalExpectedDamage(target, tile, simulation)
						expectedDamage += self.computeTotalExpectedBombardDamageAgainst(defender, simulation)
						requiredDamage = defender.healthPoints()

						target.damage = requiredDamage

						if not mustBeAbleToKill:
							# Attack no matter what
							if attackAtPoorOdds:
								self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=False,
												   simulation=simulation)
							else:
								# If we can at least knock the defender to 40 % strength with our combined efforts, go ahead even if each individual attack isn't favorable
								mustInflictWhatWeTake = True
								if expectedDamage >= (requiredDamage * 40) / 100:
									mustInflictWhatWeTake = False

								self.executeAttack(target, tile, inflictWhatWeTake=mustInflictWhatWeTake,
												   mustSurviveAttack=True, simulation=simulation)
						else:
							# Do we have enough firepower to destroy it?
							if expectedDamage > requiredDamage:
								self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=(
										targetType != TacticalTargetType.highPriorityUnit), simulation=simulation)

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
			if firstPass and self.findUnitsWithinStrikingDistance(target.target, numTurnsAway=0, noRangedUnits=False,
																  navalOnly=False, mustMoveThrough=True,
																  includeBlockedUnits=False, willPillage=True,
																  simulation=simulation):
				# Queue best one up to capture it
				self.executePillageAt(target.target, simulation)

			elif not firstPass and self.findUnitsWithinStrikingDistance(target.target, numTurnsAway=2,
																		noRangedUnits=False, navalOnly=False,
																		mustMoveThrough=False,
																		includeBlockedUnits=False, willPillage=True,
																		simulation=simulation):
				# No one can reach it this turn, what about next turn?
				self.executeMoveToTarget(target.target, garrisonIfPossible=False, simulation=simulation)

		return

	def plotCivilianAttackMoves(self, targetType: TacticalTargetType, simulation):
		"""Assigns units to capture undefended civilians"""
		for target in self.zoneTargetsFor(targetType):
			# See what units we have who can reach target this turn
			if self.findUnitsWithinStrikingDistance(target.target, numTurnsAway=1, noRangedUnits=False, navalOnly=False,
													mustMoveThrough=False, includeBlockedUnits=False, willPillage=False,
													targetUndefended=True, simulation=simulation):
				# Queue best one up to capture it
				self.executeCivilianCapture(target.target, simulation)

		return

	def plotCampDefenseMoves(self, simulation):
		"""Assigns a barbarian to go protect an undefended camp"""
		for target in self.zoneTargetsFor(TacticalTargetType.barbarianCamp):
			if self.findUnitsWithinStrikingDistance(target.target, numTurnsAway=1, noRangedUnits=True, navalOnly=False,
													mustMoveThrough=False, includeBlockedUnits=False, willPillage=False,
													targetUndefended=True, simulation=simulation):
				self.executeMoveToPlot(target.target, saveMoves=False, simulation=simulation)

		return

	def plotMovesToSafety(self, combatUnits: bool, simulation):
		"""Moved endangered units to safe hexes"""
		dangerPlotsAI = self.player.dangerPlotsAI

		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentUnit in self.currentTurnUnits:

			if currentUnit is not None:
				dangerLevel = dangerPlotsAI.dangerAt(currentUnit.location)

				# Danger value of plot must be greater than 0
				if dangerLevel > 0:
					addUnit = False
					if combatUnits:
						# If under 100% health, might flee to safety
						if currentUnit.damage() > 0:
							if currentUnit.player.leader == LeaderType.barbar:
								# Barbarian combat units - only naval units flee (but they flee if they have taken ANY damage)
								if currentUnit.domain() == UnitDomainType.sea:
									addUnit = True

							# Everyone else flees at less than or equal to 50 %combat strength
							elif currentUnit.damage() > 50:
								addUnit = True

						# Also flee if danger is really high in current plot (but not if we're barbarian)
						elif currentUnit.player.leader != LeaderType.barbar:
							acceptableDanger = currentUnit.baseCombatStrength(ignoreEmbarked=True) * 100
							if int(dangerLevel) > acceptableDanger:
								addUnit = True

					else:
						# Civilian( or embarked) units always flee from danger
						if not currentUnit.canFortifyAt(currentUnit.location, simulation):
							addUnit = True

					if addUnit:
						# Just one unit involved in this move to execute
						tacticalUnit: TacticalUnit = TacticalUnit(currentUnit)
						self.currentMoveUnits.append(tacticalUnit)

		if len(self.currentMoveUnits) > 0:
			self.executeMovesToSafestPlot(simulation)

		return

	def plotCaptureCityMoves(self, simulation) -> bool:
		"""Assign a group of units to take down each city we can capture"""
		attackMade = False

		# See how many moves of this type we can execute
		for target in self.zoneTargetsFor(TacticalTargetType.city):
			# See what units we have who can reach target this turn
			tile = target.tile
			if tile is None:
				continue

			if self.findUnitsWithinStrikingDistance(tile.point, numTurnsAway=1, simulation=simulation):
				# Do we have enough firepower to destroy it?
				city = simulation.cityAt(tile.point)
				if city is not None:
					requiredDamage = 200 - city.damage()
					target.damage = requiredDamage

					if self.computeTotalExpectedDamage(target, tile, simulation) >= requiredDamage:
						print(f"### Attacking city of {city.name} to capture {city.location} by {self.player.leader}")
						# If so, execute enough moves to take it
						self.executeAttack(target, tile, inflictWhatWeTake := False, mustSurviveAttack=False,
										   simulation=simulation)
						attackMade = True

						# Did it work?  If so, don't need a temporary dominance zone if had one here
						if tile.owner().leader == self.player.leader:
							self.deleteTemporaryZoneAt(tile.point)

		return attackMade

	def plotDamageCityMoves(self, simulation) -> bool:
		"""Assign a group of units to take down each city we can capture"""
		attackMade = False

		# See how many moves of this type we can execute
		for target in self.zoneTargetsFor(TacticalTargetType.city):
			# See what units we have who can reach target this turn
			tile = target.tile
			if tile is None:
				continue

			self.currentMoveCities = []

			if self.findUnitsWithinStrikingDistance(tile.point, numTurnsAway=1, noRangedUnits=False, navalOnly=False,
													mustMoveThrough=False, includeBlockedUnits=True,
													simulation=simulation):
				city = simulation.cityAt(tile.point)
				if city is not None:
					requiredDamage = city.maxHealthPoints() - city.damage()
					target.damage = requiredDamage

					# Don't want to hammer away to try and take down a city for more than 8 turns
					if self.computeTotalExpectedDamage(target, tile, simulation) > (requiredDamage / 8):
						# If so, execute enough moves to take it
						self.executeAttack(target, tile, inflictWhatWeTake=False, mustSurviveAttack=True,
										   simulation=simulation)
						attackMade = True

		return attackMade

	def plotBarbarianMove(self, aggressive: bool, simulation):
		"""Move barbarians across the map"""
		if not self.player.isBarbarian():
			return

		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			unit = TacticalUnit(currentTurnUnit)
			self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeBarbarianMoves(aggressive=aggressive, simulation=simulation)

		return

	def reviewUnassignedBarbarianUnits(self, simulation):
		"""Log that we couldn't find assignments for some units"""
		# Loop through all remaining units
		for currentTurnUnit in self.currentTurnUnits:
			# Barbarians and air units aren't handled by the operational or homeland AIs
			if currentTurnUnit.player.leader == LeaderType.barbar or currentTurnUnit.domain() == UnitDomainType.air:
				currentTurnUnit.pushMission(UnitMission(UnitMissionType.skip), simulation)
				currentTurnUnit.setTurnProcessed(True)

				print(
					f"<< TacticalAI - barbarian ### Unassigned {currentTurnUnit.name()} at {currentTurnUnit.location}")

		return

	def isAlreadyTargeted(self, point: HexPoint) -> Optional[QueuedAttack]:
		"""Do we already have a queued attack running on this plot? Return series ID if yes, nil if no."""
		if len(self.queuedAttacks) == 0:
			return None

		for queuedAttack in self.queuedAttacks:
			target = queuedAttack.target
			if target is not None:
				if target.target == point:
					return queuedAttack

		return None

	def identifyPriorityTargets(self, simulation):
		"""Mark units that we'd like to make opportunity attacks on because of their unit type (e.g. catapults)"""
		# Look through all the enemies we can see
		for target in self.allTargets:
			# Don't consider units that are already medium priority
			if target.targetType == TacticalTargetType.highPriorityUnit or \
				target.targetType == TacticalTargetType.lowPriorityUnit:
				# Ranged units will always be medium priority targets
				unit = target.unit
				if unit is not None:
					if unit.canAttackRanged():
						target.targetType = TacticalTargetType.mediumPriorityUnit

			# Don't consider units that are already high priority
			if target.targetType == TacticalTargetType.mediumPriorityUnit or \
				target.targetType == TacticalTargetType.lowPriorityUnit:

				unit = target.unit
				if unit is not None:
					tile = simulation.tileAt(unit.location)

					# Units defending citadels will always be high priority targets
					if tile.hasImprovement(ImprovementType.fort) or tile.hasImprovement(ImprovementType.citadelle):
						target.targetType = TacticalTargetType.highPriorityUnit

		return

	def establishTacticalPriorities(self):
		"""Choose which tactics to emphasize this turn"""
		self.movePriorityList = []

		for tacticalMove in TacticalMoveType.allPlayerMoves():
			priority = tacticalMove.priority()

			# Make sure base priority is not negative
			if priority >= 0:

				# Finally, add a random die roll to each priority
				priority += random.randint(-2, 2)  # AI_TACTICAL_MOVE_PRIORITY_RANDOMNESS

				# Store off this move and priority
				move = TacticalMove()
				move.moveType = tacticalMove
				move.priority = priority
				self.movePriorityList.append(move)

		# Loop through each possible tactical move
		self.movePriorityList.sort()

	def updatePostures(self, simulation):
		"""Establish postures for each dominance zone (taking into account last posture)"""
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		newPostures: [TacticalPosture] = []

		for dominanceZone in tacticalAnalysisMap.dominanceZones:

			# Check to make sure we want to use this zone
			if self.useThisDominanceZone(dominanceZone):

				lastPostureType = self.findPostureTypeFor(dominanceZone)
				newPostureType = self.selectPostureTypeFor(dominanceZone, lastPostureType, tacticalAnalysisMap.dominancePercentage)

				posture = TacticalPosture(
					newPostureType,
					dominanceZone.owner,
					dominanceZone.closestCity,
					dominanceZone.isWater
				)
				newPostures.append(posture)

		self.postures = newPostures

	def assignTacticalMove(self, tacticalMove: TacticalMove, simulation):
		"""Choose which tactics to run and assign units to it"""
		if tacticalMove.moveType == TacticalMoveType.moveNoncombatantsToSafety:
			# TACTICAL_MOVE_NONCOMBATANTS_TO_SAFETY
			self.plotMovesToSafety(combatUnits=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.reposition:
			# TACTICAL_REPOSITION
			self.plotRepositionMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.garrisonAlreadyThere:
			# TACTICAL_GARRISON_ALREADY_THERE
			self.plotGarrisonMoves(numTurnsAway=0, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.garrisonToAllowBombards:
			# TACTICAL_GARRISON_TO_ALLOW_BOMBARD
			self.plotGarrisonMoves(numTurnsAway=1, mustAllowRangedAttack=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.captureCity:
			# TACTICAL_CAPTURE_CITY
			self.plotCaptureCityMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.damageCity:
			# TACTICAL_DAMAGE_CITY
			self.plotDamageCityMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.destroyHighUnit:
			# TACTICAL_DESTROY_HIGH_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.destroyMediumUnit:
			# TACTICAL_DESTROY_MEDIUM_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.destroyLowUnit:
			# TACTICAL_DESTROY_LOW_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=True, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.toSafety:
			# TACTICAL_TO_SAFETY
			self.plotMovesToSafety(combatUnits=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.attritHighUnit:
			# TACTICAL_ATTRIT_HIGH_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.highPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.attritMediumUnit:
			# TACTICAL_ATTRIT_MEDIUM_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.mediumPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.attritLowUnit:
			# TACTICAL_ATTRIT_LOW_UNIT
			self.plotDestroyUnitMoves(TacticalTargetType.lowPriorityUnit, mustBeAbleToKill=False, attackAtPoorOdds=False, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.barbarianCamp:
			# TACTICAL_BARBARIAN_CAMP
			self.plotBarbarianCampMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.pillage:
			# TACTICAL_PILLAGE
			self.plotPillageMoves(TacticalTargetType.improvement, firstPass=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.civilianAttack:
			# fatalError("not implemented yet")
			# NOOP
			pass
		elif tacticalMove.moveType == TacticalMoveType.safeBombards:
			# TACTICAL_SAFE_BOMBARDS
			self.plotSafeBombardMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.heal:
			# TACTICAL_HEAL
			self.plotHealMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.ancientRuins:
			# TACTICAL_ANCIENT_RUINS
			self.plotAncientRuinMoves(turnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.bastionAlreadyThere:
			# TACTICAL_BASTION_ALREADY_THERE
			self.plotBastionMoves(numTurnsAway=0, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.guardImprovementAlreadyThere:
			# TACTICAL_GUARD_IMPROVEMENT_ALREADY_THERE
			self.plotGuardImprovementMoves(numTurnsAway=0, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.bastionOneTurn:
			# TACTICAL_BASTION_1_TURN
			self.plotBastionMoves(numTurnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.garrisonOneTurn:
			# TACTICAL_GARRISON_1_TURN
			self.plotGarrisonMoves(numTurnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.guardImprovementOneTurn:
			# TACTICAL_GUARD_IMPROVEMENT_1_TURN
			self.plotGuardImprovementMoves(numTurnsAway=1, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.airSweep:
			# TACTICAL_AIR_SWEEP
			self.plotAirSweepMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.airIntercept:
			# TACTICAL_AIR_INTERCEPT
			self.plotAirInterceptMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.airRebase:
			# fatalError("not implemented yet")
			# NOOP
			pass
		elif tacticalMove.moveType == TacticalMoveType.closeOnTarget:
			# TACTICAL_CLOSE_ON_TARGET
			self.plotCloseOnTarget(checkDominance=True, simulation=simulation)
		elif tacticalMove.moveType == TacticalMoveType.moveOperation:
			# TACTICAL_MOVE_OPERATIONS
			self.plotOperationalArmyMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.emergencyPurchases:
			# TACTICAL_EMERGENCY_PURCHASES
			self.plotEmergencyPurchases(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureWithdraw:
			# TACTICAL_POSTURE_WITHDRAW
			self.plotWithdrawMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureSitAndBombard:
			# TACTICAL_POSTURE_SIT_AND_BOMBARD
			self.plotSitAndBombardMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureAttritFromRange:
			# TACTICAL_POSTURE_ATTRIT_FROM_RANGE
			self.plotAttritFromRangeMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureExploitFlanks:
			# TACTICAL_POSTURE_EXPLOIT_FLANKS
			self.plotExploitFlanksMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureSteamroll:
			# TACTICAL_POSTURE_STEAMROLL
			self.plotSteamrollMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureSurgicalCityStrike:
			# TACTICAL_POSTURE_SURGICAL_CITY_STRIKE
			self.plotSurgicalCityStrikeMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureHedgehog:
			# TACTICAL_POSTURE_HEDGEHOG
			self.plotHedgehogMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureCounterAttack:
			# TACTICAL_POSTURE_COUNTERATTACK
			self.plotCounterAttackMoves(simulation)
		elif tacticalMove.moveType == TacticalMoveType.postureShoreBombardment:
			# TACTICAL_POSTURE_SHORE_BOMBARDMENT
			self.plotShoreBombardmentMoves(simulation)
		else:
			# NOOP
			print(f"not implemented: TacticalAI - {tacticalMove.moveType}")

	def plotOperationalArmyMoves(self, simulation):
		"""Process units that we recruited out of operational moves.
		Haven't used them, so let them go ahead with those moves"""
		operations = self.player.operations

		# Update all operations(moved down - previously was in the PlayerAI object)
		for operation in operations:
			if operation.lastTurnMoved() < simulation.currentTurn:

				if operation.moveType == TacticalMoveType.singleHex:
					self.plotSingleHexOperationMoves(operation, simulation)  # EscortedOperation
				elif operation.moveType == TacticalMoveType.enemyTerritory:
					self.plotEnemyTerritoryOperationMoves(operation, simulation)  # EnemyTerritoryOperation
				elif operation.moveType == TacticalMoveType.navalEscort:
					self.plotNavalEscortOperationMoves(operation, simulation)  # NavalEscortedOperation
				elif operation.moveType == TacticalMoveType.freeformNaval:
					self.plotFreeformNavalOperationMoves(operation, simulation)  # NavalOperation
				elif operation.moveType == TacticalMoveType.rebase:
					# NOOP
					pass

				operation.setLastTurnMoved(simulation.currentTurn)
				operation.checkOnTarget(simulation)

		killedSomething: bool = True

		while killedSomething:
			killedSomething = False

			for operation in operations:
				if operation.doDelayedDeath(simulation):
					killedSomething = True
					break

		return

	def plotSafeBombardMoves(self, simulation):
		"""Find all targets that we can bombard easily"""
		tacticalAnalysisMap = simulation.tacticalAnalysisMap()

		for target in self.zoneTargetsFor(TacticalTargetType.highPriorityUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				bestFriendlyRange = tacticalAnalysisMap.bestFriendlyRange()
				canIgnoreLightOfSight = tacticalAnalysisMap.canIgnoreLightOfSight()

				tacticalAnalysisMap.clearDynamicFlags()
				tacticalAnalysisMap.setTargetBombardCells(
					target.target,
					bestFriendlyRange=bestFriendlyRange,
					canIgnoreLightOfSight=canIgnoreLightOfSight,
					simulation=simulation
				)

				self.executeSafeBombardsOn(target, simulation)

		for target in self.zoneTargetsFor(TacticalTargetType.mediumPriorityUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				# m_pMap->ClearDynamicFlags();
				# m_pMap->SetTargetBombardCells(pTargetPlot, m_pMap->GetBestFriendlyRange(), m_pMap->CanIgnoreLOS());
				self.executeSafeBombardsOn(target, simulation)

		for target in self.zoneTargetsFor(TacticalTargetType.lowPriorityUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				# m_pMap->ClearDynamicFlags();
				# m_pMap->SetTargetBombardCells(pTargetPlot, m_pMap->GetBestFriendlyRange(), m_pMap->CanIgnoreLOS());
				self.executeSafeBombardsOn(target, simulation)

		for target in self.zoneTargetsFor(TacticalTargetType.embarkedMilitaryUnit):
			if target.isTargetStillAliveFor(self.player, simulation):
				# m_pMap->ClearDynamicFlags();
				# m_pMap->SetTargetBombardCells(pTargetPlot, m_pMap->GetBestFriendlyRange(), m_pMap->CanIgnoreLOS());
				self.executeSafeBombardsOn(target, simulation)

		return

	def plotAncientRuinMoves(self, turnsAway, simulation):
		"""Pop goody huts nearby"""
		for zoneTarget in self.zoneTargetsFor(TacticalTargetType.ancientRuins):
			# Grab units that make sense for this move type
			plot = simulation.tileAt(zoneTarget.target)

			self.findUnitsFor(TacticalMoveType.ancientRuins, plot, rangedOnly=False, simulation=simulation)

			if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
				self.executeMoveToTarget(plot.point, garrisonIfPossible=False, simulation=simulation)

				if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
					print(f"Moving to goody hut, {zoneTarget.target}, Turns Away: {turnsAway}")
					# LogTacticalMessage(strLogString);

		return

	def plotAirInterceptMoves(self, simulation):
		"""Set fighters to intercept"""
		pass

	def plotGarrisonMoves(self, numTurnsAway: int, mustAllowRangedAttack: bool=False, simulation=None):
		"""Make a defensive move to garrison a city"""
		if simulation is None:
			raise Exception('simulation must not be None')

		for target in self.zoneTargetsFor(TacticalTargetType.cityToDefend):
			tile = simulation.tileAt(target.target)

			if tile is None:
				continue

			city = simulation.cityAt(target.target)

			if city is None:
				continue

			if city.lastTurnGarrisonAssigned() < simulation.currentTurn:
				# Grab units that make sense for this move type
				self.findUnitsFor(TacticalMoveType.garrisonAlreadyThere, tile, turnsAway=numTurnsAway, rangedOnly=mustAllowRangedAttack, simulation=simulation)

				if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:

					self.executeMoveToTarget(target.target, garrisonIfPossible=True, simulation=simulation)
					city.setLastTurnGarrisonAssigned(simulation.currentTurn)

		return

	def findUnitsFor(self, move: TacticalMoveType, targetTile, turnsAway: int, rangedOnly: bool, simulation) -> bool:
		"""Finds both high and normal priority units we can use for this move (returns true if at least 1 unit found)"""
		rtnValue = False

		self.currentMoveUnits = []
		self.currentMoveHighPriorityUnits = []

		# Loop through all units available to tactical AI this turn
		for loopUnit in self.currentTurnUnits:
			if loopUnit.domain() != UnitDomainType.air and loopUnit.isCombatUnit():

				# Make sure domain matches
				if loopUnit.domain() == UnitDomainType.sea and not targetTile.terrain().isWater() or \
					loopUnit.domain() == UnitDomainType.land and targetTile.terrain().isWater():
					continue

				suitableUnit = False
				highPriority = False

				if move == TacticalMoveType.garrisonAlreadyThere or move == TacticalMoveType.garrisonOneTurn:
					# Want to put ranged units in cities to give them a ranged attack
					if loopUnit.isRanged():
						suitableUnit = True
						highPriority = True
					elif rangedOnly:
						continue

					# Don't put units with a combat strength boosted from promotions in cities, these boosts are ignored
					if loopUnit.defenseModifier(None, None, None, ranged=False, simulation=simulation) == 0 and \
						loopUnit.attackModifier(None, None, None, simulation) == 0:
						suitableUnit = True
				elif move == TacticalMoveType.guardImprovementAlreadyThere or \
					move == TacticalMoveType.guardImprovementOneTurn or \
					move == TacticalMoveType.bastionAlreadyThere or move == TacticalMoveType.bastionOneTurn:

					# No ranged units or units without defensive bonuses as plot defenders
					if not loopUnit.isRanged(): # and !loopUnit->noDefensiveBonus()*/ {
						suitableUnit = True

						# Units with defensive promotions are especially valuable
						if loopUnit.defenseModifier(None, None, None, ranged=False, simulation=simulation) > 0: # or pLoopUnit->getExtraCombatPercent() > 0*/ {
							highPriority = True
				elif move == TacticalMoveType.ancientRuins:

					# Fast movers are top priority
					if loopUnit.hasTask(UnitTaskType.fastAttack):
						suitableUnit = True
						highPriority = True
					elif loopUnit.canAttack():
						suitableUnit = True

				if suitableUnit:
					# Is it even possible for the unit to reach in the number of requested turns (ignoring roads and RR)
					distance = targetTile.point.distance(loopUnit.location)
					if loopUnit.maxMoves(simulation) > 0:
						movesPerTurn = loopUnit.maxMoves(simulation) # / GC.getMOVE_DENOMINATOR();
						leastTurns = (distance + movesPerTurn - 1) / movesPerTurn

						if turnsAway == -1 or leastTurns <= turnsAway:

							# If unit was suitable, and close enough, add it to the proper list
							pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
								loopUnit.movementType(),
								loopUnit.player,
								UnitMapType.combat,
								canEmbark=loopUnit.player.canEmbark(),
								canEnterOcean=self.player.canEnterOcean()
							)
							pathFinder = AStarPathfinder(pathFinderDataSource)
							moves = pathFinder.turnsToReachTarget(loopUnit, targetTile.point, simulation)

							if moves != sys.maxsize and (turnsAway == -1 or (turnsAway == 0 and loopUnit.location == targetTile.point) or moves <= turnsAway):

								unit = TacticalUnit(loopUnit)
								unit.healthPercent = loopUnit.healthPoints() * 100 / loopUnit.maxHealthPoints()
								unit.movesToTarget = moves

								if highPriority:
									self.currentMoveHighPriorityUnits.append(unit)
								else:
									self.currentMoveUnits.append(unit)

								rtnValue = True

		return rtnValue

	def plotBarbarianCampMoves(self, simulation):
		"""Assign a unit to capture an undefended barbarian camp"""
		for target in self.zoneTargetsFor(TacticalTargetType.barbarianCamp):
			targetPoint = target.target

			if targetPoint is None:
				continue

			if self.findUnitsWithinStrikingDistance(
				targetPoint,
				numTurnsAway=1,
				noRangedUnits=False,
				navalOnly=False,
				mustMoveThrough=False,
				includeBlockedUnits=False, willPillage=False, targetUndefended=True, simulation=simulation):

				# Queue best one up to capture it
				self.executeBarbarianCampMove(targetPoint, simulation)

				if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
					print(f"Removing barbarian camp, {targetPoint}")
					# LogTacticalMessage(strLogString);

				self.deleteTemporaryZone(targetPoint)

		return

	def plotAirSweepMoves(self, simulation):
		"""Set fighters to air sweep"""
		pass

	def plotHealMoves(self, simulation):
		"""Assigns units to heal"""
		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			unit = currentTurnUnit

			if unit is None:
				continue

			# Am I under 100% health and not embarked or already in a city?
			if unit.healthPoints() < unit.maxHealthPoints() and not unit.isEmbarked() and simulation.cityAt(unit.location) is None:
				# If I'm a naval unit I need to be in friendly territory
				if unit.domain() != UnitDomainType.sea or simulation.tileAt(unit.location).isFriendlyTerritory(self.player, simulation):
					if not unit.isUnderEnemyRangedAttack():
						self.currentMoveUnits.append(TacticalUnit(unit))

						if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
							print(f"Healing at, {unit.location}")
							# LogTacticalMessage(strLogString);

		if len(self.currentMoveUnits) > 0:
			self.executeHeals(simulation)

		return

	def plotBastionMoves(self, numTurnsAway: int, simulation):
		"""Establish a defensive bastion adjacent to a city"""
		for zoneTarget in self.zoneTargetsFor(TacticalTargetType.defensiveBastion):
			plot = simulation.tileAt(zoneTarget.target)

			# Grab units that make sense for this move type
			if plot is None:
				continue

			self.findUnitsFor(TacticalMoveType.bastionAlreadyThere, plot, turnsAway=numTurnsAway, rangedOnly=False, simulation=simulation)

			if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
				self.executeMoveToTarget(zoneTarget.target, garrisonIfPossible=False, simulation=simulation)

				if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
					print(f"Bastion, {zoneTarget.target}, Priority: {zoneTarget.threatValue}, Turns Away: {numTurnsAway}")
					# LogTacticalMessage(strLogString)

		return

	def plotGuardImprovementMoves(self, numTurnsAway, simulation):
		"""Make a defensive move to guard an improvement"""
		for zoneTarget in self.zoneTargetsFor(TacticalTargetType.improvementToDefend):
			plot = simulation.tileAt(zoneTarget.target)

			# Grab units that make sense for this move type
			if plot is None:
				continue

			self.findUnitsFor(TacticalMoveType.bastionAlreadyThere, plot, turnsAway=numTurnsAway, rangedOnly=False, simulation=simulation)

			if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
				self.executeMoveToTarget(zoneTarget.target, garrisonIfPossible=False, simulation=simulation)

				if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
					print(f"Guard Improvement, {target.target}, Turns Away: {numTurnsAway}")
					# LogTacticalMessage(strLogString)

		return

	def plotRepositionMoves(self, simulation):
		"""Move units to a better location"""
		self.currentMoveUnits = []

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			self.currentMoveUnits.append(TacticalUnit(currentTurnUnit))

		if len(self.currentMoveUnits) > 0:
			self.executeRepositionMoves(simulation)

		return

	def executeBarbarianMoves(self, aggressive: bool, simulation):
		"""Move barbarian to a new location"""
		for currentMoveUnitRef in self.currentMoveUnits:
			unit = currentMoveUnitRef.unit
			if unit.isBarbarian():
				# LAND MOVES
				if unit.domain() == UnitDomainType.land:
					bestPlot: Optional[HexPoint] = None
					if aggressive:
						bestPlot = self.findBestBarbarianLandMoveFor(unit, simulation)
					else:
						bestPlot = self.findPassiveBarbarianLandMoveFor(unit, simulation)

					if bestPlot is not None:
						self.moveToEmptySpaceNearTarget(unit, bestPlot, land=True, simulation=simulation)
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)
					else:
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)

				else:  # NAVAL MOVES
					bestPlot: Optional[HexPoint] = None

					# Do I still have a destination from a previous turn?
					currentDestination = unit.tacticalTarget()

					# Compute a new destination if I don't have one or am already there
					if currentDestination is None or currentDestination == unit.location:
						bestPlot = self.findBestBarbarianSeaMove(unit, simulation)
					else:  # Otherwise just keep moving there (assuming a path is available)
						if unit.turnsToReach(currentDestination, simulation) != sys.maxsize:
							bestPlot = currentDestination
						else:
							bestPlot = self.findBestBarbarianSeaMove(unit, simulation)

					if bestPlot is not None:
						unit.setTacticalTarget(bestPlot)
						unit.pushMission(UnitMission(UnitMissionType.moveTo, bestPlot), simulation)
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)
					else:
						unit.resetTacticalTarget()
						unit.finishMoves()
						self.unitProcessed(unit, simulation=simulation)
		
		return

	def findBestBarbarianLandMoveFor(self, unit, simulation):
		"""Find a multi-turn target for a land barbarian to wander towards"""
		landBarbarianRange = simulation.handicap.barbarbianLandTargetRange()
		bestMovePlot = self.findNearbyTargetFor(unit, landBarbarianRange, TacticalTargetType.none, None, simulation=simulation)

		# move toward trade routes
		if bestMovePlot is None:
			bestMovePlot = self.findBarbarianGankTradeRouteTargetFor(unit, simulation)

		# explore wander
		if bestMovePlot is None:
			bestMovePlot = self.findBarbarianExploreTargetFor(unit, simulation)

		return bestMovePlot

	def findNearbyTargetFor(self, unit, range: int, targetType: TacticalTargetType, noLikeUnit=None, simulation=None):
		if simulation is None:
			raise Exception('simulation must not be None')

		bestMovePlot: Optional[HexPoint] = None
		bestValue: int = sys.maxsize

		# Loop through all appropriate targets to find the closest
		for zoneTarget in self.zoneTargets:
			# Is the target of an appropriate type?
			typeMatch = False

			if targetType == TacticalTargetType.none:
				if zoneTarget.targetType == TacticalTargetType.highPriorityUnit or \
					zoneTarget.targetType == TacticalTargetType.mediumPriorityUnit or \
					zoneTarget.targetType == TacticalTargetType.lowPriorityUnit or \
					zoneTarget.targetType == TacticalTargetType.city or \
					zoneTarget.targetType == TacticalTargetType.improvement:

					typeMatch = True
			elif zoneTarget.targetType == targetType:
				typeMatch = True

			# Is this unit near enough?
			if typeMatch:
				tile = simulation.tileAt(zoneTarget.target)
				unitTile = simulation.tileAt(unit.location)

				if tile is not None and unitTile is not None:
					distance = tile.point.distance(unit.location)

					if distance == 0:
						return tile.point
					elif distance < range:
						if unitTile.area == tile.area:
							unitAtTile = simulation.unitAt(tile.point, UnitMapType.combat)
							if noLikeUnit is not None or (unitAtTile is not None and unitAtTile.hasSameType(noLikeUnit)):
								value = unit.turnsToReach(tile.point, simulation)

								if value < bestValue:
									bestMovePlot = tile.point
									bestValue = value

		return bestMovePlot

	def findBarbarianGankTradeRouteTargetFor(self, unit, simulation):
		"""Scan nearby tiles for a trade route to sit and gank from"""
		bestMovePlot: Optional[HexPoint] = None

		# Now looking for BEST score
		bestValue = 0
		movementRange = unit.movesLeft()

		for plot in unit.location.areaWithRadius(movementRange):
			if plot == unit.location:
				continue

			tile = simulation.tileAt(plot)
			if tile is not None:
				continue

			if not tile.isDiscoveredBy(self.player):
				continue

			if not unit.canReach(plot, movementRange, simulation):
				continue

			value = simulation.numTradeRoutesAt(plot)

			if value > bestValue:
				bestMovePlot = plot
				bestValue = value

		return bestMovePlot

	def findBarbarianExploreTargetFor(self, unit, simulation):
		"""Scan nearby tiles for the best choice, borrowing code from the explore AI"""
		economicAI = self.player.economicAI

		bestValue = 0
		bestMovePlot: Optional[HexPoint] = None
		movementRange = unit.movesLeft()

		# Now looking for BEST score
		for plot in unit.location.areaWithRadius(movementRange):
			if plot == unit.location:
				continue

			tile = simulation.tileAt(plot)
			if tile is not None:
				continue

			if not tile.isDiscoveredBy(self.player):
				continue

			if not unit.canReach(plot, movementRange, simulation):
				continue

			# Value them based on their explore value
			value = economicAI.scoreExplore(plot, self.player, unit.sight(), unit.domain(), simulation)

			# Add special value for popping up on hills or near enemy lands
			#if (pPlot->isAdjacentOwned())
			#	iValue += 100;
			if tile.hasOwner():
				value += 200

			# If still have no value, score equal to distance from my current plot
			if value == 0:
				value = unit.location.distance(plot)

			if value > bestValue:
				bestMovePlot = plot
				bestValue = value

		return bestMovePlot

	def unitProcessed(self, unit, markTacticalMap: bool = True, simulation=None):
		"""Remove a unit that we've allocated from list of units to move this turn"""
		if simulation is None:
			raise Exception('simulation must not be None')

		self.currentTurnUnits = list(filter(lambda u: not u == unit, self.currentTurnUnits))

		unit.setTurnProcessedTo(True)

		if markTacticalMap:
			map = simulation.tacticalAnalysisMap()

			if map.isBuild:
				cell = map.plots.values[unit.location.y][unit.location.x]
				cell.friendlyTurnEndTile = True

		return
