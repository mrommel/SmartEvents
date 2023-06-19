from typing import Optional

from map.base import HexPoint


class HexPath:
	pass


class HexPath:
	def __init__(self, points: [HexPoint], costs=None):
		if costs is None:
			costs = []

		self._points = points
		self._costs = costs

	def __repr__(self):
		strValue = 'HexPath('

		for pt in self._points:
			strValue += f'({pt.x}, {pt.y}), '

		strValue += ')'
		return strValue

	def __str__(self):
		strValue = 'HexPath('

		for pt in self._points:
			strValue += f'({pt.x}, {pt.y}), '

		strValue += ')'
		return strValue

	def points(self) -> [HexPoint]:
		return self._points

	def addCost(self, cost: float):
		self._costs.append(cost)

	def costs(self) -> [float]:
		return self._costs

	def cost(self) -> float:
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

	def prepend(self, point: HexPoint, cost: float):
		self._points.insert(0, point)
		self._costs.insert(0, cost)

		return

	def append(self, point: HexPoint, cost: float):
		self._points.append(point)
		self._costs.append(cost)

		return

	def pathWithoutFirst(self):
		return HexPath(self._points[1:], self._costs[1:])

	def reversed(self) -> HexPath:
		return HexPath(list(reversed(self._points)), list(reversed(self._costs)))
