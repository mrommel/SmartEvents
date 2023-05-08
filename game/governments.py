from typing import Optional

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
		raise AttributeError(f'cant get data for government {self}')


class PlayerGovernment:
	def __init__(self, player):
		self.player = player

	def setGovernment(self, governmentType: GovernmentType, simulation):
		pass
