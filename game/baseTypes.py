from enum import Enum

from game.types import TechType, CivicType
from game.units import UnitType
from core.base import InvalidEnumError
from utils.translation import gettext_lazy as _


class HandicapTypeData:
	def __init__(self, name: str, value: int, barbarianCampGold: int, barbarianSpawnMod: int,
	             earliestBarbarianReleaseTurn: int, freeHumanTechs: [TechType], freeHumanCivics: [CivicType],
	             freeHumanStartingUnitTypes: [UnitType], freeHumanCombatBonus: int,
	             freeAIStartingUnitTypes: [UnitType], freeAICombatBonus: int):
		self.name = name
		self.value = value
		self.barbarianCampGold = barbarianCampGold
		self.barbarianSpawnMod = barbarianSpawnMod
		self.earliestBarbarianReleaseTurn = earliestBarbarianReleaseTurn
		# human
		self.freeHumanTechs = freeHumanTechs
		self.freeHumanCivics = freeHumanCivics
		self.freeHumanStartingUnitTypes = freeHumanStartingUnitTypes
		self.freeHumanCombatBonus = freeHumanCombatBonus
		# ai
		self.freeAIStartingUnitTypes = freeAIStartingUnitTypes
		self.freeAICombatBonus = freeAICombatBonus


class HandicapType(Enum):
	# https://civ6.gamepedia.com/Game_difficulty

	settler = 'settler'
	chieftain = 'chieftain'
	warlord = 'warlord'
	prince = 'prince'
	king = 'king'
	emperor = 'emperor'
	immortal = 'immortal'
	deity = 'deity'

	def name(self) -> str:
		return self._data().name

	def value(self) -> int:
		return self._data().value

	def freeHumanStartingUnitTypes(self) -> [UnitType]:
		return self._data().freeHumanStartingUnitTypes

	def freeHumanCombatBonus(self) -> int:
		return self._data().freeHumanCombatBonus

	def freeAICombatBonus(self) -> int:
		return self._data().freeAICombatBonus

	def earliestBarbarianReleaseTurn(self) -> int:
		return self._data().earliestBarbarianReleaseTurn

	def _data(self) -> HandicapTypeData:
		if self == HandicapType.settler:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_SETTLER"),
				value=0,
				barbarianCampGold=50,
				barbarianSpawnMod=8,
				earliestBarbarianReleaseTurn=50,
				# human
				freeHumanTechs=[TechType.pottery, TechType.animalHusbandry, TechType.mining],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder],
				freeHumanCombatBonus=3,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=-1
			)
		elif self == HandicapType.chieftain:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_CHIEFTAIN"),
				value=1,
				barbarianCampGold=40,
				barbarianSpawnMod=5,
				earliestBarbarianReleaseTurn=40,
				# human
				freeHumanTechs=[TechType.pottery, TechType.animalHusbandry],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior, UnitType.builder],
				freeHumanCombatBonus=2,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=-1
			)
		elif self == HandicapType.warlord:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_WARLORD"),
				value=2,
				barbarianCampGold=30,
				barbarianSpawnMod=3,
				earliestBarbarianReleaseTurn=35,
				# human
				freeHumanTechs=[TechType.pottery],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[
					UnitType.settler, UnitType.warrior, UnitType.builder
				],
				freeHumanCombatBonus=1,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=-1
			)
		elif self == HandicapType.prince:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_PRINCE"),
				value=3,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=35,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeAICombatBonus=0
			)
		elif self == HandicapType.king:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_KING"),
				value=4,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=30,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder],
				freeAICombatBonus=1
			)
		elif self == HandicapType.emperor:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_EMPEROR"),
				value=5,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=20,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.warrior,
			        UnitType.builder],
				freeAICombatBonus=2
			)
		elif self == HandicapType.immortal:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_IMMORTAL"),
				value=6,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=10,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.warrior,
			        UnitType.warrior, UnitType.builder, UnitType.builder],
				freeAICombatBonus=3
			)
		elif self == HandicapType.deity:
			#
			return HandicapTypeData(
				name=_("TXT_KEY_HANDICAP_DEITY"),
				value=7,
				barbarianCampGold=25,
				barbarianSpawnMod=0,
				earliestBarbarianReleaseTurn=0,
				# human
				freeHumanTechs=[],
				freeHumanCivics=[],
				freeHumanStartingUnitTypes=[UnitType.settler, UnitType.warrior],
				freeHumanCombatBonus=0,
				# ai
				freeAIStartingUnitTypes=[UnitType.settler, UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior,
			        UnitType.warrior, UnitType.warrior, UnitType.warrior, UnitType.builder, UnitType.builder],
				freeAICombatBonus=4
			)

	def freeAIStartingUnitTypes(self) -> [UnitType]:
		return self._data().freeAIStartingUnitTypes

	def firstImpressionBaseValue(self):
		# // -3 - +3
		# Deity -2 to -8
		# Immortal -1 to -7
		# Emperor 0 a -6
		# King1 to -5
		# Prince 2 to -4
		# https://forums.civfanatics.com/threads/first-impression-of-you.613161/ */
		if self == HandicapType.settler:
			return 2
		elif self == HandicapType.chieftain:
			return 1
		elif self == HandicapType.warlord:
			return 0
		elif self == HandicapType.prince:
			return -1
		elif self == HandicapType.king:
			return -2
		elif self == HandicapType.emperor:
			return -3
		elif self == HandicapType.immortal:
			return -4
		elif self == HandicapType.deity:
			return -5

		raise InvalidEnumError(self)

	def freeHumanTechs(self) -> [TechType]:
		return self._data().freeHumanTechs

	def freeHumanCivics(self) -> [CivicType]:
		return self._data().freeHumanCivics

	def freeAITechs(self) -> [TechType]:
		return []

	def freeAICivics(self) -> [CivicType]:
		return []


class GameState(Enum):
	on = 'on'
	over = 'over'
	extended = 'extended'
