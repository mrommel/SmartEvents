from enum import Enum


class ExtendedEnum(Enum):

	@classmethod
	def values(cls):
		return list(map(lambda c: c.value, cls))


class InvalidEnumError(Exception):
	def __init__(self, type_value):
		super().__init__(f'enum value {type_value} not handled')


class WeightedBaseList(dict):
	def addWeight(self, value, identifier):
		self[identifier] = self.get(identifier, 0) + value

	def setWeight(self, value, identifier):
		self[identifier] = value

	def weight(self, identifier):
		return self[identifier]

	def removeAll(self):
		self.clear()

	def top3(self):
		top3Dict = dict()

		for key, value in self.items():
			# if not populated, fill it up
			if len(top3Dict) < 3:
				top3Dict[key] = value
				continue

			smallestTop3Key = None

			# find the smallest in top3
			for top3Key, top3Value in top3Dict.items():
				if smallestTop3Key is None:
					smallestTop3Key = top3Key
					continue

				if self[smallestTop3Key] > top3Value:
					smallestTop3Key = top3Key

			# if current value is bigger than smallest in top3, replace it
			if self[smallestTop3Key] < value:
				del top3Dict[smallestTop3Key]
				top3Dict[key] = value

		tmp = WeightedBaseList()

		for top3Key, top3Value in top3Dict.items():
			tmp[top3Key] = top3Value

		return tmp

	def distributeByWeight(self):
		"""distributes the keys based on the weight - it will return 100 items"""
		if len(self.keys()) == 0:
			raise Exception(f'Cannot distribute weighted array - dict is empty')

		sumValue = sum(self.values())
		output = []

		for key, value in self.items():
			amount = int(value * 100.0 / sumValue)
			for _ in range(amount):
				output.append(key)

		additional = 100 - len(output)
		for _ in range(additional):
			output.append(list(self.keys())[-1])

		assert len(output) == 100

		return output



class WeightedStringList(WeightedBaseList):
	pass
