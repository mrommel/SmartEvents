from core.base import ExtendedEnum


class EraType(ExtendedEnum):
	# default
	ancient = 'ancient'
	classical = 'classical'
	medieval = 'medieval'
	renaissance = 'renaissance'
	industrial = 'industrial'
	modern = 'modern'
	atomic = 'atomic'
	information = 'information'
	future = 'future'

	def name(self) -> str:
		if self == EraType.ancient:
			return _('TXT_KEY_ERA_ANCIENT')
		elif self == EraType.classical:
			return _('TXT_KEY_ERA_CLASSICAL')
		elif self == EraType.medieval:
			return _('TXT_KEY_ERA_MEDIEVAL')
		elif self == EraType.renaissance:
			return _('TXT_KEY_ERA_RENAISSANCE')
		elif self == EraType.industrial:
			return _('TXT_KEY_ERA_INDUSTRIAL')
		elif self == EraType.modern:
			return _('TXT_KEY_ERA_MODERN')
		elif self == EraType.atomic:
			return _('TXT_KEY_ERA_ATOMIC')
		elif self == EraType.information:
			return _('TXT_KEY_ERA_INFORMATION')
		elif self == EraType.future:
			return _('TXT_KEY_ERA_FUTURE')

		raise AttributeError(f'cant get name of {self}')

	def value(self) -> int:
		if self == EraType.ancient:
			return 0
		elif self == EraType.classical:
			return 1
		elif self == EraType.medieval:
			return 2
		elif self == EraType.renaissance:
			return 3
		elif self == EraType.industrial:
			return 4
		elif self == EraType.modern:
			return 5
		elif self == EraType.atomic:
			return 6
		elif self == EraType.information:
			return 7
		elif self == EraType.future:
			return 8

		raise AttributeError(f'cant get value of {self}')

	# def __eq__(self, other):
	# 	if self.ft == other.ft and self.inch == other.inch:
	# 		return "both objects are equal"
	# 	else:
	# 		return "both objects are not equal"

	def __le__(self, other):
		return self.value() <= other.value()