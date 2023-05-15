from typing import Optional

from game.types import TechType, CivicType
from utils.base import WeightedBaseList


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


class WeightedCivicList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for civic in list(CivicType):
			self.setWeight(0.0, civic)


class CivicInspirations:
	pass


class Civics:
	def __init__(self, player):
		self.player = player

		self._civics: [CivicType] = []
		self._currentCivicValue: Optional[CivicType] = None
		self._lastCultureEarnedValue: float = 1.0
		self._progresses = WeightedCivicList()
		self._inspirations = CivicInspirations()

	def hasCivic(self, civic: CivicType) -> bool:
		return False

	def discoverCivic(self, civic: CivicType):
		pass

	def needToChooseCivic(self):
		pass

	def currentCultureProgress(self) -> float:
		if self._currentCivicValue is None:
			return 0.0

		return self._progresses.weight(self._currentCivicValue)


class BuilderTaskingAI:
	def __init__(self, player):
		self.player = player

	def update(self, simulation):
		pass


class TacticalAI:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass


class DiplomacyAI:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass

	def hasMetWith(self, player) -> bool:
		return False

	def update(self, simulation):
		pass


class HomelandAI:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass


class DiplomacyRequests:
	def __init__(self, player):
		self.player = player

	def endTurn(self):
		pass
