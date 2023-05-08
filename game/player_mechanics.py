from game.types import TechType, CivicType


class Techs:
	def __init__(self, player):
		self.player = player

	def eurekaTriggeredForTech(self, tech: TechType) -> bool:
		return False

	def needToChooseTech(self):
		pass

	def discover(self, tech: TechType, simulation):
		pass

	def hasTech(self, tech: TechType) -> bool:
		return False


class Civics:
	def __init__(self, player):
		self.player = player

	def needToChooseCivic(self):
		pass

	def hasCivic(self, civic: CivicType) -> bool:
		return False
