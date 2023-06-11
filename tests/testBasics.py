from typing import Optional, Union

from game.states.ui import Interface, PopupType
from game.types import TechType
from map.map import MapModel
from map.types import TerrainType, MapSize


class MapModelMock(MapModel):
	def __init__(self, width_or_size: Union[int, MapSize], height_or_terrain: Union[int, TerrainType], terrain: Optional[TerrainType] = None):
		if isinstance(width_or_size, int) and isinstance(height_or_terrain, int) and isinstance(terrain, TerrainType):
			width = width_or_size
			height = height_or_terrain
			super().__init__(width, height)

			for point in self.points():
				self.modifyTerrainAt(point, terrain)
		elif isinstance(width_or_size, MapSize) and isinstance(height_or_terrain, TerrainType):
			width = width_or_size.size().width()
			height = width_or_size.size().height()
			terrain = height_or_terrain
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

	def showPopup(self, popup: PopupType, tech: Optional[TechType]):
		pass
