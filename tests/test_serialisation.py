import unittest

from map.base import HexPoint
from map.map import Tile
from map.types import TerrainType, MapSize
from serialisation.map import MapModelSchema, TileSchema
from tests.testBasics import MapModelMock


class TestSerialisation(unittest.TestCase):
	def test_tile_dump(self):
		pass
		# tile = Tile(HexPoint(1, 13), TerrainType.desert)
		# json_str = TileSchema().dumps(tile)
		#
		# self.assertGreater(len(json_str), 0)
		#
		# obj_dict = TileSchema().loads(json_str)
		# obj = Tile(obj_dict)
		#
		# self.assertEqual(obj.point.x, tile.point.x)
		# self.assertEqual(obj.point.y, tile.point.y)
		# self.assertEqual(obj.terrain(), tile.terrain())

	def test_map_dump(self):
		pass
		# mapModel = MapModelMock(MapSize.duel, TerrainType.ocean)
		# json_data = MapModelSchema().dump(mapModel)
		#
		# self.assertGreater(len(json_data), 0)
		#
		# obj = MapModelSchema().load(json_data)
		#
		# self.assertEqual(obj.width, mapModel.width)
