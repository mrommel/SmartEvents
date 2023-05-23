import sys
from typing import Optional

from game.policyCards import PolicyCardType
from game.states.ages import AgeType
from game.states.builds import BuildType
from game.states.dedications import DedicationType
from game.types import EraType
from game.unitTypes import UnitTaskType, UnitType, PromotionType, MoveOptions, UnitMissionType
from map.base import HexPoint, HexArea
from map.types import UnitDomainType
from utils.base import ExtendedEnum


class UnitActivityType(ExtendedEnum):
	heal = 'heal'
	sleep = 'sleep'
	none = 'none'
	awake = 'awake'
	mission = 'mission'
	hold = 'hold'


class UnitAutomationType(ExtendedEnum):
	build = 'build'
	explore = 'explore'
	none = 'none'


class HexPath:
	pass


class UnitMission:
	def __init__(self, missionType: UnitMissionType, buildType: Optional[BuildType] = None,
				 target: Optional[HexPoint] = None, path: Optional[HexPath] = None,
				 options: Optional[MoveOptions] = None):
		self.missionType = missionType
		self.buildType = buildType
		self.target = target
		self.path = path
		self.options = options
		self.unit = None

		self.startedInTurn: int = -1

		if missionType.needsTarget() and (target is None and path is None):
			raise Exception("need target")

	def start(self, simulation):
		"""Initiate a mission"""
		self.startedInTurn = simulation.currentTurn

		delete = False
		notify = False
		action = False

		if self.unit.canMove():
			self.unit.setActivityType(UnitActivityType.mission, simulation)
		else:
			self.unit.setActivityType(UnitActivityType.hold, simulation)

		if not self.unit.canStartMission(self, simulation):
			delete = True
		else:
			if self.missionType == UnitMissionType.skip:
				self.unit.setActivityType(UnitActivityType.hold, simulation)
				delete = True
			elif self.missionType == UnitMissionType.sleep:
				self.unit.setActivityType(UnitActivityType.sleep, simulation)
				delete = True
				notify = True
			elif self.missionType == UnitMissionType.fortify:
				self.unit.setActivityType(UnitActivityType.sleep, simulation)
				delete = True
				notify = True
			elif self.missionType == UnitMissionType.heal:
				self.unit.setActivityType(UnitActivityType.heal, simulation)
				delete = True
				notify = True

			if self.unit.canMove():

				if self.missionType == UnitMissionType.fortify or self.missionType == UnitMissionType.heal or \
					self.missionType == UnitMissionType.alert or self.missionType == UnitMissionType.skip:

					self.unit.setFortifiedThisTurnTo(True, simulation)

					# start the animation right now to give feedback to the player
					if not self.unit.isFortified() and not self.unit.hasMoved(simulation) and \
						self.unit.canFortifyAt(self.unit.location, simulation):
						simulation.userInterface.refreshUnit(self.unit)
				elif self.unit.isFortified():
					# unfortify for any other mission
					simulation.userInterface.refreshUnit(self.unit)

				# ---------- now the real missions with action -----------------------

				if self.missionType == UnitMissionType.embark or self.missionType == UnitMissionType.disembark:
					action = True

				# FIXME nuke, paradrop, airlift
				elif self.missionType == UnitMissionType.rebase:
					if self.unit.doRebaseTo(self.target):
						action = True
				elif self.missionType == UnitMissionType.rangedAttack:
					if not self.unit.canRangeStrikeAt(self.target, needWar=False, noncombatAllowed=False, simulation=simulation):
						# Invalid, delete the mission
						delete = True
				elif self.missionType == UnitMissionType.pillage:
					if self.unit.doPillage(simulation):
						action = True
				elif self.missionType == UnitMissionType.found:
					if self.unit.doFoundWith(None, simulation):
						action = True

		if action and self.unit.player.isHuman():
			timer = self.calculateMissionTimerFor(self.unit)
			self.unit.setMissionTimerTo(timer)

		if delete:
			self.unit.popMission()
		elif self.unit.activityType() == UnitActivityType.mission:
			self.continueMissionSteps(0, simulation)

		return


class Army:
	pass


class Unit:
	maxHealth = 100.0

	def __init__(self, location: HexPoint, unitType: UnitType, player):
		self._name = unitType.name()
		self.location = location
		self.unitType = unitType
		self.player = player
		self.taskValue = unitType.defaultTask()

		self._movesValue = unitType.moves()
		self._healthPointsValue = Unit.maxHealth
		self._activityTypeValue = UnitActivityType.none
		self._automationType = UnitAutomationType.none
		self._processedInTurnValue = False
		self._missions = []

	def name(self) -> str:
		return self._name

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
		moveVal = self.baseMovesInto(UnitDomainType.none, simulation)

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

	def baseMovesInto(self, domain: UnitDomainType, simulation) -> int:
		if (domain == UnitDomainType.sea and self.canEmbark(simulation)) or \
			(domain == UnitDomainType.none and self.isEmbarked()):
			return 2  # EMBARKED_UNIT_MOVEMENT

		extraNavalMoves = 0
		if domain == UnitDomainType.sea:
			extraNavalMoves = self.extraNavalMoves(simulation)

		extraGoldenAgeMoves = 0

		extraUnitCombatTypeMoves = 0  # ???
		return self.unitType.moves() + extraNavalMoves + extraGoldenAgeMoves + extraUnitCombatTypeMoves

	def power(self) -> int:
		"""Current power of unit (raw unit type power adjusted for health)"""
		powerVal: float = float(self.unitType.power())

		# Take promotions into account: unit with 4 promotions worth ~50% more
		powerVal = powerVal * pow(float(self.experienceLevel()), 0.3)

		ratio = float(self._healthPointsValue) / (2.0 * Unit.maxHealth) + 0.5
		return int(powerVal * ratio)

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

	def experienceLevel(self) -> int:
		return 1

	def activityType(self) -> UnitActivityType:
		return self._activityTypeValue

	def setTurnProcessedTo(self, turnProcessed: bool):
		self._processedInTurnValue = turnProcessed

	def processedInTurn(self) -> bool:
		return self._processedInTurnValue

	def updateMission(self, simulation):
		pass

	def pushMission(self, mission, simulation):
		self._missions.append(mission)

		print(f">>> pushed mission: {mission.missionType} {mission.target} for {self.unitType}")

		mission.unit = self
		mission.start(simulation)

	def doDelayedDeath(self, simulation):
		pass

	def isDelayedDeath(self) -> bool:
		return False

	def readyToMove(self) -> bool:
		if not self.canMove():
			return False

		if self.isGarrisoned():
			return False

		if len(self._missions) > 0:
			return False

		if self._activityTypeValue != UnitActivityType.none and self._activityTypeValue != UnitActivityType.awake:
			return False

		if self._automationType != UnitActivityType.none:
			return False

		# / * if self.isbusy()
		# {
		# return False
		# } * /

		return True

	def canMove(self) -> bool:
		return self.moves() > 0

	def isAutomated(self) -> bool:
		return self._automationType != UnitAutomationType.none

	def autoMission(self, simulation):
		pass

	def peekMission(self) -> Optional[UnitMission]:
		return None

	def canStartMission(self, mission: UnitMission, simulation):
		"""Eligible to start a new mission?"""
		if mission.missionType == UnitMissionType.found:
			if self.canFoundAt(mission.unit.location, simulation):
				return True
		elif mission.missionType == UnitMissionType.moveTo:
			if simulation.valid(mission.target):
				return True
		elif mission.missionType == UnitMissionType.garrison:
			if self.canGarrisonAt(mission.target, simulation):
				return True
			elif self.canGarrisonAt(self.location, simulation):
				return True
		elif mission.missionType == UnitMissionType.pillage:
			if self.canPillageAt(self.location, simulation):
				return True
		elif mission.missionType == UnitMissionType.skip:
			if self.canHoldAt(mission.unit.location, simulation):
				return True
		elif mission.missionType == UnitMissionType.rangedAttack:
			if self.canRangeStrikeAt(mission.target, needWar=False, noncombatAllowed=False, simulation=simulation):
				return True
		elif mission.missionType == UnitMissionType.sleep:
			pass
			# FIXME
			# if self.canSleep()
			# return True
		elif mission.missionType == UnitMissionType.fortify:
			if self.canFortifyAt(self.location, simulation):
				return True
		elif mission.missionType == UnitMissionType.alert:
			if self.canSentry(simulation):
				return True
		elif mission.missionType == UnitMissionType.airPatrol:
			pass
			# FIXME
		elif mission.missionType == UnitMissionType.heal:
			if self.canHeal(simulation):
				return True
		elif mission.missionType == UnitMissionType.embark:
			if self.canEmbarkInto(mission.target, simulation):
				return True
		elif mission.missionType == UnitMissionType.disembark:
			if self.canDisembarkInto(mission.target, simulation):
				return True
		elif mission.missionType == UnitMissionType.rebase:
			if mission.target is not None:
				return self.canTransferToAnotherCity()
		elif mission.missionType == UnitMissionType.build:
			if self.canBuild(mission.buildType, mission.unit.location, simulation):
				return True
		elif mission.missionType == UnitMissionType.routeTo:
			if simulation.valid(mission.target) and mission.unit.pathTowards(mission.target, options=None, simulation=simulation) is not None:
				return True
		elif mission.missionType == UnitMissionType.followPath:
			if mission.path is not None:
				return True
		# elif mission.missionType == UnitMissionType.swapUnits:
		# elif mission.missionType == UnitMissionType.moveToUnit:

		return False

	def isEmbarked(self) -> bool:
		return False

	def setMadeAttackTo(self, value):
		pass

	def army(self) -> Optional[Army]:
		return None

	def isGarrisoned(self):
		return False

	def damage(self) -> int:
		return max(0, int(Unit.maxHealth) - int(self._healthPointsValue))

	def healthPoints(self) -> int:
		return int(self._healthPointsValue)

	def maxHealthPoints(self) -> int:
		return int(Unit.maxHealth)

	def isHurt(self) -> bool:
		return self.damage() > 0

	def isFound(self) -> bool:
		return self.unitType.canFound()

	def canFoundAt(self, location, simulation) -> bool:
		if not self.unitType.canFound():
			return False

		if not self.player.canFoundAt(location, simulation):
			return False

		# isolationism - Domestic routes provide +2 Food, +2 Production.
		# BUT: Can't train or buy Settlers nor settle new cities.
		if self.player.government.hasCard(PolicyCardType.isolationism):
			return False

		return True

	def setActivityType(self, activityType: UnitActivityType, simulation):
		oldActivity = self._activityTypeValue

		if oldActivity != activityType:
			self.activityTypeValue = activityType

			# If we're waking up a Unit then remove it's fortification bonus
			if activityType == UnitActivityType.awake:
				self.setFortifyTurns(0, simulation)


			simulation.userInterface.refreshUnit(self)

		return

	def isHuman(self) -> bool:
		return self.player.isHuman()
