import sys

from game.policyCards import PolicyCardType
from game.types import EraType
from game.unitTypes import UnitTaskType, UnitType, PromotionType
from map.base import HexPoint, HexArea
from map.types import UnitDomainType


class Unit:
	def __init__(self, location: HexPoint, unitType: UnitType, player):
		self.location = location
		self.unitType = unitType
		self.player = player
		self.taskValue = unitType.defaultTask()

		self._movesValue = 0

	def hasTask(self, task: UnitTaskType) -> bool:
		return task in self.unitType.unitTasks()

	def task(self) -> UnitTaskType:
		return self.taskValue

	def domain(self) -> UnitDomainType:
		return self.unitType.domain()

	def jumpToNearestValidPlotWithin(self, radius, simulation):
		currentTile = simulation.tileAt(self.location)
		bestValue = sys.maxsize
		bestTile = None

		area = HexArea(self.location, radius)
		for loopPoint in area.points:
			loopTile = simulation.tileAt(loopPoint)

			if loopTile.isValidDomainFor(self):
				if self.canMoveInto(loopPoint, MoveOptions.none, simulation):
					if simulation.unitAt(loopPoint, self.unitMapType()) is None:
						if not loopTile.hasOwner() or self.player == loopTile.owner():
							if loopTile.isDiscoveredBy(self.player):
								value = loopPoint.distanceTo(self.location)

								if loopTile.continentIdentifier() != currentTile.continentIdentifier():
									value *= 3

								if value < bestValue:
									bestValue = value
									bestTile = loopTile

		if bestTile is not None:
			fromString = f'(x: {self.location.x}, y: {self.location.y})'
			toString = f'(x: {bestTile.location.x}, y: {bestTile.location.y})'
			print(f'Jump to nearest valid plot within range by {self.unitType}, from: {fromString} to: {toString}')
			self.setLocation(bestTile.location, simulation)
			self.publishQueuedVisualizationMoves(simulation)
		else:
			print(f'Can\'t find a valid plot within range. for {self.unitType}, at X: {self.location.x}, Y: {self.location.y}')
			return False

		return True

	def moves(self) -> int:
		return self._movesValue

	def finishMoves(self):
		self._movesValue = 0

	def resetMoves(self, simulation):
		self._movesValue = self.maxMoves(simulation)

	def maxMoves(self, simulation) -> int:
		moveVal = self.baseMoves(simulation)

		if (self.unitType.era() == EraType.classical or self.unitType.era() == EraType.medieval) and \
			self.domain() == UnitDomainType.land:

			boudicaNear = False  # @fixme gameModel.isGreatGeneral(type: .boudica, of: self.player, at: self.location, inRange: 2)
			hannibalBarcaNear = False  # @fixme gameModel.isGreatGeneral(type:.hannibalBarca, of: self.player, at: self.location, inRange: 2)
			sunTzuNear = False  # @fixme gameModel.isGreatGeneral(type:.sunTzu, of: self.player, at: self.location, inRange: 2)

			if boudicaNear or hannibalBarcaNear or sunTzuNear:
				# +1 Movement to Classical and Medieval era land units within 2 tiles.
				moveVal += 1

		# monumentality + golden - +2 Movement for Builders.
		if self.player.currentAge() == AgeType.golden and self.player.hasDedication(DedicationType.monumentality):
			if self.unitType == UnitType.builder:
				moveVal += 2

		# exodusOfTheEvangelists + golden - +2 Movement for Missionaries, Apostles and Inquisitors
		# /* if player.currentAge() ==.golden and player.has(dedication: .
		# 	exodusOfTheEvangelists) {
		# if self.type ==.missionary or self.type ==.apostle or self.type ==.inquisitor
		# {
		# 	moveVal += 2
		# }
		# } * /

		# commando - +1 Movement.
		if self.hasPromotion(PromotionType.commando):
			moveVal += 1

		# pursuit - +1 Movement.
		if self.hasPromotion(PromotionType.pursuit):
			moveVal += 1

		# redeploy - +1 Movement.
		if self.hasPromotion(PromotionType.redeploy):
			moveVal += 1

		# helmsman - +1 Movement.
		if self.hasPromotion(PromotionType.helmsman):
			moveVal += 1

		# militaryOrganization - +2 Great General points for every Armory and +4 Great General points for every Military Academy.
		# Great Generals receive +2 Movement.
		if self.player.government.hasCard(PolicyCardType.militaryOrganization):
			if self.unitType == UnitType.general:
				moveVal += 2

		# logistics - +1 Movement if starting turn in friendly territory.
		if self.player.government.hasCard(PolicyCardType.logistics):
			unitTile = simulation.tileAt(self.location)

			if unitTile.isFriendlyTerritoryFor(self.player, simulation):
				moveVal += 1

		return moveVal


	def hasMoved(self, simulation) -> bool:
		return self.moves() < self.maxMoves(simulation)

	def movesLeft(self) -> int:
		return max(0, self.moves())

	def hasPromotion(self, promotion: PromotionType) -> bool:
		return False

	def canMoveInto(self, point, options, simulation):
		return True

	def setLocation(self, location, simulation):
		self.location = location

	def publishQueuedVisualizationMoves(self, simulation):
		pass
