from typing import Optional

from map.base import HexPoint
from map.map import MapModel
from map.path_finding.base import AStar
from map.path_finding.path import HexPath
from map.types import UnitMovementType, TerrainType


class AStarDataSource:
	def __init__(self, grid: MapModel, movement_type: UnitMovementType):
		self.grid = grid
		self.movement_type = movement_type

	def walkableAdjacentTilesCoords(self, tile_coord: HexPoint) -> [HexPoint]:
		pass

	def costToMove(self, from_tile_coord: HexPoint, to_adjacent_tile_coord: HexPoint) -> float:
		pass


class MoveTypeIgnoreUnitsOptions:
	def __init__(self, ignore_sight, can_embark, can_enter_ocean):
		self.ignore_sight = ignore_sight
		self.can_embark = can_embark
		self.can_enter_ocean = can_enter_ocean
	# self.wrapX = wrapX


class MoveTypeIgnoreUnitsPathfinderDataSource(AStarDataSource):

	def __init__(self, grid: MapModel, movement_type: UnitMovementType, player, options: MoveTypeIgnoreUnitsOptions):
		super().__init__(grid, movement_type)
		self.player = player
		self.options = options

	def walkableAdjacentTilesCoords(self, tile_coord: HexPoint) -> [HexPoint]:
		walkable_coords = []

		for neighbor in tile_coord.neighbors():
			if not self.grid.valid(neighbor):
				continue

			to_tile = self.grid.tileAt(neighbor)

			if self.movement_type == UnitMovementType.walk:
				if to_tile.terrain() == TerrainType.ocean and not self.options.can_enter_ocean:
					continue
				if to_tile.isWater() and self.options.can_embark and to_tile.isImpassable(UnitMovementType.swim):
					continue

				if to_tile.isLand() and to_tile.isImpassable(UnitMovementType.walk):
					continue
			else:
				if to_tile.terrain() == TerrainType.ocean and not self.options.can_enter_ocean:
					continue

				if to_tile.isWater() and to_tile.isImpassable(UnitMovementType.swim):
					continue

			# use sight?
			if not self.options.ignore_sight:
				# skip if not in sight or discovered
				if not to_tile.isDiscoveredBy(self.player):
					continue

				if not to_tile.isVisibleTo(self.player):
					continue

			from_tile = self.grid.tileAt(tile_coord)

			if to_tile.movementCost(self.movement_type, from_tile) < UnitMovementType.max.value:
				walkable_coords.append(neighbor)

		return walkable_coords

	def costToMove(self, from_tile_coord: HexPoint, to_adjacent_tile_coord: HexPoint) -> float:
		from_tile = self.grid.tileAt(from_tile_coord)
		to_tile = self.grid.tileAt(to_adjacent_tile_coord)

		return to_tile.movementCost(self.movement_type, from_tile)


class AStarPathfinder(AStar):

	def __init__(self, data_source):
		self.data_source = data_source

	def heuristic_cost_estimate(self, current: HexPoint, goal: HexPoint):
		return current.distance(goal)

	def distance_between(self, n1, n2):
		return self.data_source.costToMove(n1, n2)

	def neighbors(self, node):
		return self.data_source.walkableAdjacentTilesCoords(node)

	def is_goal_reached(self, current, goal):
		return current == goal

	def shortestPath(self, from_point, to_point) -> Optional[HexPath]:
		if self.data_source is None:
			print('no datasource')

		pts_or_none = self.astar(from_point, to_point, False)

		if pts_or_none is not None:
			return HexPath(list(pts_or_none))

		return None
