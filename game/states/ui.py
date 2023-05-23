from utils.base import ExtendedEnum


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


class ScreenType(ExtendedEnum):
	diplomatic = 'diplomatic'
