from core.base import ExtendedEnum


class TooltipType(ExtendedEnum):
	unitDestroyedEnemyUnit = 'unitDestroyedEnemyUnit'


class Interface:
	def __init__(self):
		pass

	def updateCity(self, city):
		pass

	def updatePlayer(self, player):
		pass

	def isShown(self, screenType) -> bool:
		return False

	def refreshTile(self, tile):
		pass

	def refreshUnit(self, unit):
		pass

	def hideUnit(self, unit, location):
		pass

	def showUnit(self, unit, location):
		pass

	def animateUnit(self, unit, animation):
		pass

	def selectTech(self, tech):
		pass

	def selectCivic(self, civic):
		pass

	def enterCity(self, unit, point):
		pass

	def leaveCity(self, unit, point):
		pass


class ScreenType(ExtendedEnum):
	diplomatic = 'diplomatic'


class PopupType(ExtendedEnum):
	tutorialBadUnitAttack = 'tutorialBadUnitAttack'
	tutorialCityAttack = 'tutorialCityAttack'
	inspirationTriggered = 'inspirationTriggered'
	eurekaTriggered = 'eurekaTriggered'
