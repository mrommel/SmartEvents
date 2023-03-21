from game.types import TechType


class Techs:
	def __init__(self, player):
		self.player = player

	def eurekaTriggeredForTech(self, tech: TechType) -> bool:
		return False

	def needToChooseTech(self):
		pass


class Civics:
	def __init__(self, player):
		self.player = player

	def needToChooseCivic(self):
		pass
