class CitySpecializationType:
	none = 'none'
	productionWonder = 'productionWonder'


class CityStrategyAI:
	def __init__(self, city):
		self.city = city

	def doTurn(self, simulation):
		pass

	def specialization(self) -> CitySpecializationType:
		return CitySpecializationType.none
