from typing import Optional

from map.base import HexPoint


class HexPath:
	def __init__(self, points: [HexPoint]):
		self._points = points
		self._costs = []

	def points(self) -> [HexPoint]:
		return self._points

	def addCost(self, cost: float):
		self._costs.append(cost)

	def costs(self) -> [float]:
		return self._costs

	def cost(self) -> int:
		return sum(self._costs)

	def cropPointsUntil(self, location):
		cropIndex = self.firstIndexOf(location)

		if cropIndex is not None:
			self._points = self._points[0:cropIndex]
			self._costs = self._costs[0:cropIndex]

	def firstIndexOf(self, location) -> Optional[int]:
		cropIndex = None

		for (index, point) in enumerate(self._points):
			if point == location:
				cropIndex = index

		return cropIndex
