import sys
from typing import Union

from map.base import HexPoint, HexArea
from map.map import Map
from utils.base import ExtendedEnum


class BaseSiteEvaluator:
	def __init__(self):
		pass

	def valueOfPoint(self, point: HexPoint, player) -> float:
		raise Exception('must be overloaded by sub class')

	def valueOfArea(self, area: HexArea, player) -> float:
		sumValue = 0.0

		for point in area:
			sumValue += self.valueOfPoint(point, player)

		return sumValue

	def bestPointOfArea(self, area: HexArea, player) -> (HexPoint, float):
		bestValue = sys.float_info.min
		bestPoint: HexPoint = area.first()

		for point in area:
			value = self.valueOfPoint(point, player)

			if value > bestValue:
				bestValue = value
				bestPoint = point

		return bestPoint, bestValue


class CitySiteEvaluationType(ExtendedEnum):
	freshWater = 'freshWater'
	coastalWater = 'coastalWater'
	noWater = 'noWater'
	tooCloseToAnotherCity = 'tooCloseToAnotherCity'
	invalidTerrain = 'invalidTerrain'


class TileFertilityEvaluator(BaseSiteEvaluator):
	def __init__(self, map: Map):
		super().__init__()
		self.map = map


class CitySiteEvaluator(BaseSiteEvaluator):

	minCityDistance = 2

	def __init__(self, map: Map):
		super().__init__()
		self.map = map
		self.tileFertilityEvaluator = TileFertilityEvaluator(map)

	def canCityBeFoundOn(self, tile, player) -> bool:
		# check if tile is owned by another player
		if tile.owner() is not None:
			if not tile.owner().isEqualTo(player):
				return False

		# check if already found a city here
		if self.map.cityAt(tile.point) is not None:
			return False

		# can't found on water
		if tile.terrain().isWater():
			return False

		# check for distance (cities inside the area)
		area = tile.point.areaWithRadius(self.minCityDistance)

		for areaPoint in area:
			if self.map.cityAt(areaPoint) is not None:
				return False

		return True
