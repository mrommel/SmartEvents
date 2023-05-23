from game.states.ui import Interface
from map.map import Map
from map.types import TerrainType


class MapMock(Map):
	def __init__(self, width: int, height: int, terrain: TerrainType):
		super().__init__(width, height)

		for point in self.points():
			self.modifyTerrainAt(point, terrain)

	def discover(self, player, simulation):
		for point in self.points():
			tile = self.tileAt(point)
			tile.discoverBy(player, simulation)


class UserInterfaceMock(Interface):
	def updateCity(self, city):
		pass

	def updatePlayer(self, player):
		pass

	def isShown(self, screenType) -> bool:
		return False

	def refreshTile(self, tile):
		pass