from map.map import Map
from map.types import TerrainType


class MapMock(Map):
	def __init__(self, width: int, height: int, terrain: TerrainType):
		super().__init__(width, height)

		for point in self.points():
			self.modifyTerrainAt(point, terrain)


class UserInterfaceMock:
	def updateCity(self, city):
		pass

	def updatePlayer(self, player):
		pass

	def isShown(self, screenType) -> bool:
		return False