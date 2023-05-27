""" unittest module """
import unittest

from game.civilizations import LeaderType
from game.game import Game
from game.players import Player
from game.types import TechType
from map.base import Array2D, HexPoint, HexCube, HexDirection, Size, BoundingBox, HexArea
from map.generation import MapOptions, MapGenerator, HeightMap
from map.improvements import ImprovementType
from map.map import Tile, Map
from map.path_finding.finder import MoveTypeIgnoreUnitsOptions, AStarPathfinder, MoveTypeIgnoreUnitsPathfinderDataSource
from map.types import FeatureType, TerrainType, UnitMovementType, MapSize, MapType, AppealLevel, ResourceType
from tests.testBasics import UserInterfaceMock, MapMock


class TestMapAssets(unittest.TestCase):
	def test_mapSize_data(self):
		for mapSize in list(MapSize):
			_ = mapSize.name()

	def test_mapType_data(self):
		for mapType in list(MapType):
			_ = mapType.name()

	def test_terrain_data(self):
		for terrain in list(TerrainType):
			_ = terrain.name()
			_ = terrain.textures()

	def test_feature_data(self):
		for feature in list(FeatureType):
			_ = feature.name()
			_ = feature.textures()

	def test_resource_data(self):
		for resource in list(ResourceType):
			_ = resource.name()
			_ = resource.texture()


class TestArray2D(unittest.TestCase):
	def test_constructor(self):
		"""Test the Array2D constructor"""
		arr1 = Array2D(3, 4)
		self.assertEqual(arr1.width, 3)
		self.assertEqual(arr1.height, 4)


class TestHexPoint(unittest.TestCase):
	def test_constructor(self):
		"""Test the HexPoint constructor"""
		hex1 = HexPoint(27, 5)
		self.assertEqual(hex1.x, 27)
		self.assertEqual(hex1.y, 5)

		hex2 = HexPoint(HexCube(2, 1, 3))
		self.assertEqual(hex2.x, 4)
		self.assertEqual(hex2.y, 3)

		with self.assertRaises(AttributeError):
			_ = HexPoint(1, None)

	def test_neighbor_n_s(self):
		"""Test the HexPoint neighbor"""
		# north
		hex1 = HexPoint(27, 5)
		neighbor_n = hex1.neighbor(HexDirection.north, 1)

		self.assertEqual(neighbor_n, HexPoint(26, 4))
		self.assertEqual(neighbor_n.neighbor(HexDirection.south, 1), hex1)

	def test_neighbor_ne_sw(self):
		"""Test the HexPoint neighbor in north-east and south-west"""
		# north
		hex1 = HexPoint(27, 5)
		neighbor_ne = hex1.neighbor(HexDirection.northEast, 1)

		self.assertEqual(neighbor_ne, HexPoint(27, 4))
		self.assertEqual(neighbor_ne.neighbor(HexDirection.southWest, 1), hex1)

	def test_neighbors(self):
		"""Test the HexPoint neighbors"""
		expected = [
			HexPoint(26, 4),
			HexPoint(27, 4),
			HexPoint(28, 5),
			HexPoint(27, 6),
			HexPoint(26, 6),
			HexPoint(26, 5)
		]
		hex1 = HexPoint(27, 5)
		neighbors = hex1.neighbors()

		self.assertEqual(len(neighbors), 6)
		for index in range(6):
			self.assertEqual(neighbors[index], expected[index])

	def test_directionTowards(self):
		"""Test the HexPoint neighbors"""
		hex1 = HexPoint(27, 5)
		far_direction = hex1.directionTowards(HexPoint(10, 5))
		near_direction = hex1.directionTowards(HexPoint(28, 5))

		self.assertEqual(far_direction, HexDirection.northWest)
		self.assertEqual(near_direction, HexDirection.southEast)

	def test_distance(self):
		"""Test the HexPoint distance"""
		hex1 = HexPoint(3, 2)
		hex2 = HexPoint(5, 4)
		hex3 = HexPoint(17, 5)

		self.assertEqual(hex1.distance(hex1), 0)
		self.assertEqual(hex1.distance(hex2), 3)
		self.assertEqual(hex2.distance(hex1), 3)
		self.assertEqual(hex1.distance(hex3), 15)
		self.assertEqual(hex3.distance(hex1), 15)
		self.assertEqual(hex2.distance(hex3), 12)
		self.assertEqual(hex3.distance(hex2), 12)

	def test_areaWith(self):
		"""Test the HexPoint areaWith"""
		hex1 = HexPoint(3, 2)

		area1 = hex1.areaWithRadius(1)
		area2 = hex1.areaWithRadius(2)

		self.assertEqual(len(area1.points), 7)  # 1 + 6
		self.assertEqual(len(area2.points), 19)  # 1 + 6 + 12


class TestImprovementType(unittest.TestCase):
	def test_farm_yields(self):
		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		farmYields = ImprovementType.farm.yieldsFor(player)
		self.assertEqual(farmYields.food, 1)
		self.assertEqual(farmYields.production, 0)
		self.assertEqual(farmYields.gold, 0)

	def test_mine_yields(self):
		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		mineYields = ImprovementType.mine.yieldsFor(player)
		self.assertEqual(mineYields.food, 0)
		self.assertEqual(mineYields.production, 1)
		self.assertEqual(mineYields.gold, 0)

	def test_pasture_yields(self):
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel)

		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 0)
		self.assertEqual(pastureYields.production, 1)
		self.assertEqual(pastureYields.gold, 0)

		player.techs.discover(TechType.stirrups, simulation)
		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 1)
		self.assertEqual(pastureYields.production, 1)
		self.assertEqual(pastureYields.gold, 0)

		player.techs.discover(TechType.robotics, simulation)
		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 2)
		self.assertEqual(pastureYields.production, 2)
		self.assertEqual(pastureYields.gold, 0)

		player.techs.discover(TechType.replaceableParts, simulation)
		pastureYields = ImprovementType.pasture.yieldsFor(player)
		self.assertEqual(pastureYields.food, 2)
		self.assertEqual(pastureYields.production, 3)
		self.assertEqual(pastureYields.gold, 0)

	def test_plantation_yields(self):
		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		plantationYields = ImprovementType.plantation.yieldsFor(player)
		self.assertEqual(plantationYields.food, 0)
		self.assertEqual(plantationYields.production, 0)
		self.assertEqual(plantationYields.gold, 2)

	def test_fishingBoats_yields(self):
		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		fishingBoatsYields = ImprovementType.fishingBoats.yieldsFor(player)
		self.assertEqual(fishingBoatsYields.food, 1)
		self.assertEqual(fishingBoatsYields.production, 0)
		self.assertEqual(fishingBoatsYields.gold, 0)

	def test_camp_yields(self):
		player = Player(LeaderType.trajan, human=False)
		player.initialize()

		campYields = ImprovementType.camp.yieldsFor(player)
		self.assertEqual(campYields.food, 0)
		self.assertEqual(campYields.production, 0)
		self.assertEqual(campYields.gold, 1)


class TestFeatureType(unittest.TestCase):
	def test_isPossibleOn(self):
		"""Test isPossibleOn"""
		tile = Tile(HexPoint(0, 0), TerrainType.grass)
		feature = FeatureType.none

		# cannot place FeatureType.none on any tile
		self.assertEqual(feature.isPossibleOn(tile), False)

		# forest
		feature = FeatureType.forest
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.snow)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# rainforest
		feature = FeatureType.rainforest
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# floodplains
		feature = FeatureType.floodplains
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# marsh
		feature = FeatureType.marsh
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# oasis
		feature = FeatureType.oasis
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# reef
		feature = FeatureType.reef
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.shore)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# ice
		feature = FeatureType.ice
		tile.setTerrain(TerrainType.snow)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.shore)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# atoll
		feature = FeatureType.atoll
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.shore)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# volcano
		feature = FeatureType.volcano
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.tundra)
		self.assertEqual(feature.isPossibleOn(tile), False)

		# mountains
		feature = FeatureType.mountains
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# lake
		feature = FeatureType.lake
		tile.setTerrain(TerrainType.grass)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)

		# fallout
		feature = FeatureType.fallout
		tile.setTerrain(TerrainType.ocean)
		self.assertEqual(feature.isPossibleOn(tile), False)
		tile.setTerrain(TerrainType.desert)
		self.assertEqual(feature.isPossibleOn(tile), True)
		tile.setTerrain(TerrainType.plains)
		self.assertEqual(feature.isPossibleOn(tile), True)


class TestHeightMap(unittest.TestCase):
	def test_constructor(self):
		"""Test the HeightMap constructor"""
		height_map1 = HeightMap(3, 4)
		self.assertEqual(height_map1.width, 3)
		self.assertEqual(height_map1.height, 4)

	def test_findThresholdAbove(self):
		"""Test the HeightMap findThresholdAbove method"""
		height_map1 = HeightMap(3, 3)
		height_map1.values[0][0] = 0.1
		height_map1.values[0][1] = 0.2
		height_map1.values[0][2] = 0.3
		height_map1.values[1][0] = 0.4
		height_map1.values[1][1] = 0.5
		height_map1.values[1][2] = 0.6
		height_map1.values[2][0] = 0.7
		height_map1.values[2][1] = 0.8
		height_map1.values[2][2] = 0.9
		self.assertEqual(height_map1.findThresholdAbove(0.5), 0.5)


class TestTile(unittest.TestCase):
	def test_constructor(self):
		"""Test that the tile constructor versions work"""
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.point, HexPoint(3, 2))
		self.assertEqual(tile.point.x, 3)
		self.assertEqual(tile.point.y, 2)
		self.assertEqual(tile.terrain(), TerrainType.tundra)

	def test_river_n(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		tile._riverValue = 1

		self.assertEqual(tile.isRiverInNorth(), True)
		self.assertEqual(tile.isRiverInNorthEast(), False)
		self.assertEqual(tile.isRiverInSouthEast(), False)

	def test_river_ne(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)
		tile._riverValue = 4

		self.assertEqual(tile.isRiverInNorth(), False)
		self.assertEqual(tile.isRiverInNorthEast(), True)
		self.assertEqual(tile.isRiverInSouthEast(), False)

	def test_isWater(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.isWater(), False)

	def test_isLand(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.isLand(), True)

	def test_movementCost(self):
		tundra_tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		grass_tile = Tile(HexPoint(3, 1), TerrainType.grass)
		mountains_tile = Tile(HexPoint(3, 1), TerrainType.grass)
		mountains_tile.setFeature(FeatureType.mountains)
		ocean_tile = Tile(HexPoint(3, 1), TerrainType.shore)

		self.assertEqual(grass_tile.movementCost(UnitMovementType.walk, tundra_tile), 1)
		self.assertEqual(mountains_tile.movementCost(UnitMovementType.walk, tundra_tile), 3)
		self.assertEqual(ocean_tile.movementCost(UnitMovementType.walk, tundra_tile), UnitMovementType.max.value)

	def test_improvement_getset(self):
		tile = Tile(HexPoint(3, 2), TerrainType.grass)

		self.assertEqual(tile.improvement(), ImprovementType.none)  # initial

		tile.setImprovement(ImprovementType.farm)
		self.assertEqual(tile.improvement(), ImprovementType.farm)

		tile.setImprovement(ImprovementType.none)
		self.assertEqual(tile.improvement(), ImprovementType.none)

	def test_improvement_pillage(self):
		tile = Tile(HexPoint(3, 2), TerrainType.tundra)

		self.assertEqual(tile.isImprovementPillaged(), False)  # initial

		tile.setImprovementPillaged(True)
		self.assertEqual(tile.isImprovementPillaged(), True)

		tile.setImprovementPillaged(False)
		self.assertEqual(tile.isImprovementPillaged(), False)


class TestBoundingBox(unittest.TestCase):
	def test_constructor(self):
		boundingBox = BoundingBox([HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])
		self.assertEqual(boundingBox.width(), 2)
		self.assertEqual(boundingBox.height(), 2)


class TestHexArea(unittest.TestCase):
	def test_constructor(self):
		area0 = HexArea([HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])
		self.assertEqual(area0.points, [HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])

		area1 = HexArea(HexPoint(1, 1))
		self.assertEqual(area1.points, [HexPoint(1, 1)])

		area2 = HexArea(HexPoint(1, 1), radius=1)
		self.assertEqual(area2.points, [HexPoint(0, 0), HexPoint(0, 1), HexPoint(0, 2), HexPoint(2, 1), HexPoint(1, 0), HexPoint(1, 1), HexPoint(1, 2)])

	def test_center(self):
		area = HexArea([HexPoint(1, 1), HexPoint(2, 2), HexPoint(3, 3)])
		self.assertEqual(area.center(), HexPoint(2, 2))

	def test_boundingBox(self):
		area0 = HexArea([HexPoint(1, 1), HexPoint(1, 2)])
		boundingBox0 = area0.boundingBox()
		expectedBoundingBox = BoundingBox()
		expectedBoundingBox.min_x = 1
		expectedBoundingBox.min_y = 1
		expectedBoundingBox.max_x = 1
		expectedBoundingBox.max_y = 2
		self.assertEqual(boundingBox0, expectedBoundingBox)


class TestMap(unittest.TestCase):
	def test_constructor(self):
		"""Test that the map constructor versions work"""
		map1 = Map(3, 4)
		self.assertEqual(map1.width, 3)
		self.assertEqual(map1.height, 4)

		map2 = Map(Size(5, 2))
		self.assertEqual(map2.width, 5)
		self.assertEqual(map2.height, 2)

		with self.assertRaises(AttributeError):
			_ = Map(5.2, 1)

	def test_valid(self):
		"""Test that a point is on the map (or not)"""
		map1 = Map(3, 4)

		self.assertEqual(map1.valid(2, 3), True)
		self.assertEqual(map1.valid(HexPoint(2, 3)), True)

		self.assertEqual(map1.valid(-1, 3), False)
		self.assertEqual(map1.valid(HexPoint(-1, 3)), False)

	def test_points(self):
		"""Test that points returns all map points"""
		expected = [
			HexPoint(0, 0),
			HexPoint(0, 1),
			HexPoint(1, 0),
			HexPoint(1, 1),
		]
		map1 = Map(2, 2)
		map_points = map1.points()

		self.assertEqual(len(map_points), 4)
		for index in range(4):
			self.assertEqual(map_points[index], expected[index])

	def test_average_tile_appeal(self):
		# GIVEN
		mapModel = MapMock(10, 10, TerrainType.ocean)

		simulation = Game(mapModel)
		simulation.userInterface = UserInterfaceMock()

		tile = mapModel.tileAt(HexPoint(3, 3))

		# WHEN
		appeal = tile.appeal(simulation)
		appealLevel = tile.appealLevel(simulation)

		# GIVEN
		self.assertEqual(appeal, 0)
		self.assertEqual(appealLevel, AppealLevel.average)

	def test_discovery(self):
		# GIVEN
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()

		tile = mapModel.tileAt(HexPoint(3, 1))

		# WHEN
		discoveredBefore = tile.isDiscoveredBy(player)
		tile.discoverBy(player, simulation)
		discoveredAfter = tile.isDiscoveredBy(player)
		# tile.sightBy(player)

		# THEN
		self.assertEqual(discoveredBefore, False)
		self.assertEqual(discoveredAfter, True)

	def test_sight(self):
		# GIVEN
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()

		tile = mapModel.tileAt(HexPoint(3, 1))

		# WHEN
		discoveredBefore = tile.isVisibleTo(player)
		tile.sightBy(player)
		discoveredAfter = tile.isVisibleTo(player)

		# THEN
		self.assertEqual(discoveredBefore, False)
		self.assertEqual(discoveredAfter, True)


class TestMapGenerator(unittest.TestCase):

	def setUp(self):
		self.last_state_value = 0.0

	def test_constructor(self):
		"""Test the MapGenerator constructor"""

		def _callback(state):
			print(f'Progress: {state.value} - {state.message} ', flush=True)
			self.last_state_value = state.value

		options = MapOptions(mapSize=MapSize.duel, mapType=MapType.continents, leader=LeaderType.trajan)
		generator = MapGenerator(options)

		grid = generator.generate(_callback)

		self.assertEqual(grid.width, 32)
		self.assertEqual(grid.height, 22)
		self.assertEqual(self.last_state_value, 1.0)


class TestPathfinding(unittest.TestCase):
	def test_generation_request(self):
		"""Test astar"""
		grid = Map(10, 10)
		for pt in grid.points():
			grid.modifyTerrainAt(pt, TerrainType.grass)

		player = Player(leader=LeaderType.trajan, human=True)

		grid.modifyFeatureAt(HexPoint(1, 2), FeatureType.mountains)  # put a mountain into the path

		datasource_options = MoveTypeIgnoreUnitsOptions(ignore_sight=True, can_embark=False, can_enter_ocean=False)
		datasource = MoveTypeIgnoreUnitsPathfinderDataSource(grid, UnitMovementType.walk, player, datasource_options)
		finder = AStarPathfinder(datasource)

		path = finder.shortestPath(HexPoint(0, 0), HexPoint(2, 3))

		# print(path)
		target_path = [HexPoint(0, 0), HexPoint(1, 1), HexPoint(2, 1), HexPoint(2, 2), HexPoint(2, 3), ]
		self.assertEqual(len(path.points()), 5)
		for i, n in enumerate(target_path):
			self.assertEqual(n, path.points()[i])


if __name__ == '__main__':
	unittest.main()
