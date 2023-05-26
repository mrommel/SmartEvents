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
		cropIndex = -1

		for (index, point) in enumerate(self._points):
			if point == location:
				cropIndex = index

		if cropIndex != -1:
			self._points = self._points[0:cropIndex]
			self._costs = self._costs[0:cropIndex]
