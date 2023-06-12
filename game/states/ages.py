from core.base import ExtendedEnum, InvalidEnumError


class AgeTypeData:
	def __init__(self, name: str):
		self.name = name


class AgeType(ExtendedEnum):
	normal = 'normal'
	golden = 'golden'
	dark = 'dark'

	def name(self) -> str:
		return self._data().name

	def _data(self) -> AgeTypeData:
		if self == AgeType.normal:
			return AgeTypeData(
				name='Normal'
			)
		elif self == AgeType.golden:
			return AgeTypeData(
				name='Golden'
			)
		elif self == AgeType.dark:
			return AgeTypeData(
				name='Dark'
			)

		raise InvalidEnumError(self)
	