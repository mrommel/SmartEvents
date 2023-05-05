from game.ai.cities import CityStrategyAI
from game.civilizations import LeaderWeightList
from map.base import HexPoint
from map.types import YieldList


class City:
	def __init__(self, name: str, location: HexPoint, isCapital: bool, player):
		self.name = name
		self.location = location
		self.capitalValue = isCapital
		self.everCapitalValue = isCapital
		self.populationValue = 0
		self.gameTurnFoundedValue = 0
		self.foodBasketValue = 1.0

		self.player = player
		self.leader = player.leader
		self.originalLeaderValue = player.leader
		self.previousLeaderValue = None

		self.isFeatureSurroundedValue = False
		self.threatVal = 0

		self.healthPointsValue = 200
		self.amenitiesForWarWearinessValue = 0

		self.productionAutomatedValue = False
		self.baseYieldRateFromSpecialists = YieldList()
		self.extraSpecialistYield = YieldList()
		self.numPlotsAcquiredList = LeaderWeightList()

		self.featureProductionValue = 0.0

		# ai
		self.cityStrategyAI = CityStrategyAI(self)

	def __str__(self):
		return f'City "{self.name}" at {self.location}'

	def doFoundMessage(self):
		pass

	def initialize(self, simulation):
		pass

	def featureProduction(self) -> float:
		return self.featureProductionValue

	def changeFeatureProduction(self, change: float):
		self.featureProductionValue += change

	def setFeatureProduction(self, value: float):
		self.featureProductionValue = value
