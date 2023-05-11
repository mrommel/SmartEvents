from typing import Optional

from game.policy_cards import PolicyCardType
from game.types import CivicType
from utils.base import ExtendedEnum


class GovernmentTypeData:
	def __init__(self, name: str, requiredCivic: Optional[CivicType]):
		self.name = name
		self.requiredCivic = requiredCivic


class GovernmentType(ExtendedEnum):
	none = 'none'

	chiefdom = 'chiefdom'
	autocracy = 'chiefdom'
	monarchy = 'autocracy'

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def _data(self) -> GovernmentTypeData:
		if self == GovernmentType.none:
			return GovernmentTypeData(
				name='KEY_NONE',
				requiredCivic=None
			)
		elif self == GovernmentType.chiefdom:
			return GovernmentTypeData(
				name='KEY_CHIEF',
				requiredCivic=None
			)
		elif self == GovernmentType.monarchy:
			return GovernmentTypeData(
				name='KEY_MONARCHY',
				requiredCivic=None
			)
		raise AttributeError(f'cant get data for government {self}')


class PlayerGovernment:
	def __init__(self, player):
		self.player = player
		self._currentGovernmentValue = GovernmentType.chiefdom

	def setGovernment(self, governmentType: GovernmentType, simulation):
		self._currentGovernmentValue = governmentType

	def currentGovernment(self) -> GovernmentType:
		return self._currentGovernmentValue

	def hasCard(self, policyCard: PolicyCardType) -> bool:
		return False
