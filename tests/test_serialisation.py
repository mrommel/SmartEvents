import os
import unittest

from game.civilizations import LeaderType
from map.base import HexPoint
from map.generation import MapOptions, MapGenerator
from map.map import Tile, MapModel
from map.types import TerrainType, MapSize, FeatureType, MapType
from serialisation.map import MapModelSchema, TileSchema
from tests.testBasics import MapModelMock


class TestSerialisation(unittest.TestCase):
	def setUp(self):
		self.last_state_value = 0.0

	def test_tile_serialization(self):
		tile = Tile(HexPoint(1, 13), TerrainType.desert)
		json_str = TileSchema().dumps(tile)

		self.assertGreater(len(json_str), 0)

		obj_dict = TileSchema().loads(json_str)
		obj = Tile(obj_dict)

		self.assertEqual(obj.point.x, tile.point.x)
		self.assertEqual(obj.point.y, tile.point.y)
		self.assertEqual(obj.terrain(), tile.terrain())
		self.assertEqual(obj.feature(), tile.feature())

	def test_map_serialization(self):
		mapModel = MapModelMock(MapSize.duel, TerrainType.ocean)
		mapModel.modifyTerrainAt(HexPoint(2, 3), TerrainType.desert)
		mapModel.modifyFeatureAt(HexPoint(2, 3), FeatureType.oasis)

		json_str = MapModelSchema().dumps(mapModel)

		self.assertGreater(len(json_str), 0)

		obj_dict = MapModelSchema().loads(json_str)
		obj = MapModel(obj_dict)

		self.assertEqual(obj.width, mapModel.width)
		self.assertEqual(obj.height, mapModel.height)
		self.assertEqual(obj.tileAt(HexPoint(0, 0)).terrain(), mapModel.tileAt(HexPoint(0, 0)).terrain())

		self.assertEqual(obj.tileAt(HexPoint(2, 3)).terrain(), mapModel.tileAt(HexPoint(2, 3)).terrain())
		self.assertEqual(obj.tileAt(HexPoint(2, 3)).feature(), mapModel.tileAt(HexPoint(2, 3)).feature())

	def test_map_deserialization_from_file(self):
		path = './tests/files/duel.map'
		if os.path.exists('./files/duel.map'):
			path = './files/duel.map'

		with open(path, "r") as file:
			fileContent = file.read()

			obj_dict = MapModelSchema().loads(fileContent)
			obj = MapModel(obj_dict)

			self.assertEqual(obj.width, 32)
			self.assertEqual(obj.height, 22)

			self.assertGreater(len(obj.startLocations), 0)
			self.assertGreater(len(obj.cityStateStartLocations), 0)

			self.assertGreater(len(obj.continents), 0)
			self.assertGreater(len(obj.oceans), 0)

	def _test_generate_testfile(self):
		def _callback(state):
			# print(f'Progress: {state.value} - {state.message} ', flush=True)
			self.last_state_value = state.value

		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.trajan)
		generator = MapGenerator(options)

		mapModel = generator.generate(_callback)

		json_str = MapModelSchema().dumps(mapModel)

		with open('duel.map', "w") as file:
			file.write(json_str)
