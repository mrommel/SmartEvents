from enum import Enum


class ExtendedEnum(Enum):

	@classmethod
	def values(cls):
		return list(map(lambda c: c.value, cls))


class InvalidEnumError(Exception):
	def __init__(self, type_value):
		super().__init__(f'enum value {type_value} not handled')


class WeightedStringList(dict):
	def addWeight(self, value, identifier):
		self[identifier] = self.get(identifier, 0) + value

	def setWeight(self, value, identifier):
		self[identifier] = value

	def weight(self, identifier):
		return self[identifier]
