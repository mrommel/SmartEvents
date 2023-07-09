from core.base import ExtendedEnum
from utils.translation import gettext_lazy as _


class EraTypeData:
	def __init__(self, name: str, next, formalWarWeariness: int, surpriseWarWeariness: int):
		self.name = name
		self.next = next
		self.formalWarWeariness = formalWarWeariness
		self.surpriseWarWeariness = surpriseWarWeariness


class EraType(ExtendedEnum):
	# default
	ancient = 0, 'ancient'
	classical = 1, 'classical'
	medieval = 2, 'medieval'
	renaissance = 3, 'renaissance'
	industrial = 4, 'industrial'
	modern = 5, 'modern'
	atomic = 6, 'atomic'
	information = 7, 'information'
	future = 8, 'future'

	def __new__(cls, value, name):
		member = object.__new__(cls)
		member._value = value
		member._name = name
		return member

	def name(self) -> str:
		return self._data().name

	# def __eq__(self, other):
	# 	if self.ft == other.ft and self.inch == other.inch:
	# 		return "both objects are equal"
	# 	else:
	# 		return "both objects are not equal"

	def __le__(self, other):
		return self._value <= other._value

	def __lt__(self, other):
		return self._value < other._value

	def warWearinessValue(self, formal: bool):
		return self._data().formalWarWeariness if formal else self._data().surpriseWarWeariness

	def _data(self) -> EraTypeData:
		if self == EraType.ancient:
			return EraTypeData(
				name=_('TXT_KEY_ERA_ANCIENT'),
				next=EraType.classical,
				formalWarWeariness=16,
				surpriseWarWeariness=16
			)
		elif self == EraType.classical:
			return EraTypeData(
				name=_('TXT_KEY_ERA_CLASSICAL'),
				next=EraType.medieval,
				formalWarWeariness=22,
				surpriseWarWeariness=25
			)
		elif self == EraType.medieval:
			return EraTypeData(
				name=_('TXT_KEY_ERA_MEDIEVAL'),
				next=EraType.renaissance,
				formalWarWeariness=28,
				surpriseWarWeariness=34
			)
		elif self == EraType.renaissance:
			return EraTypeData(
				name=_('TXT_KEY_ERA_RENAISSANCE'),
				next=EraType.industrial,
				formalWarWeariness=34,
				surpriseWarWeariness=43
			)
		elif self == EraType.industrial:
			return EraTypeData(
				name=_('TXT_KEY_ERA_INDUSTRIAL'),
				next=EraType.modern,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.modern:
			return EraTypeData(
				name=_('TXT_KEY_ERA_MODERN'),
				next=EraType.atomic,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.atomic:
			return EraTypeData(
				name=_('TXT_KEY_ERA_ATOMIC'),
				next=EraType.information,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.information:
			return EraTypeData(
				name=_('TXT_KEY_ERA_INFORMATION'),
				next=EraType.future,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)
		elif self == EraType.future:
			return EraTypeData(
				name=_('TXT_KEY_ERA_FUTURE'),
				next=EraType.none,
				formalWarWeariness=40,
				surpriseWarWeariness=52
			)

		raise AttributeError(f'cant get name of {self}')
