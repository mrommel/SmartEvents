import sys
from typing import Optional

from game.buildings import BuildingType
from game.combat import Combat
from game.moments import MomentType
from game.notifications import NotificationType
from game.policyCards import PolicyCardType
from game.religions import PantheonType
from game.states.ages import AgeType
from game.states.dedications import DedicationType
from game.types import EraType, TechType
from game.unitMissions import UnitMission
from game.unitTypes import UnitTaskType, UnitType, UnitPromotionType, MoveOptions, UnitMissionType, UnitActivityType, \
	UnitMapType
from map.base import HexPoint, HexArea
from map.improvements import ImprovementType
from map.path_finding.path import HexPath
from map.types import UnitDomainType, YieldType
from utils.base import ExtendedEnum


class UnitAutomationType(ExtendedEnum):
	none = 'none'

	build = 'build'
	explore = 'explore'


class Army:
	pass


class UnitAnimationType:
	fortify = 'fortify'
	unfortify = 'unfortify'


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
		self._missionTimerValue = 0
		self._fortifyTurnsValue = 0
		self._fortifiedThisTurnValue = False

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
		if self.hasPromotion(UnitPromotionType.commando):
			moveVal += 1

		# pursuit - +1 Movement.
		if self.hasPromotion(UnitPromotionType.pursuit):
			moveVal += 1

		# redeploy - +1 Movement.
		if self.hasPromotion(UnitPromotionType.redeploy):
			moveVal += 1

		# helmsman - +1 Movement.
		if self.hasPromotion(UnitPromotionType.helmsman):
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

	def hasPromotion(self, promotion: UnitPromotionType) -> bool:
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
		if self._activityTypeValue == UnitActivityType.mission:
			if len(self._missions) > 0:
				self._missions[-1].continueMission(steps=0, simulation=simulation)

		return

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
		if len(self._missions) > 0:
			return self._missions[-1]  # return last element

	def setMissionTimerTo(self, timer: int):
		self._missionTimerValue = timer

	def missionTimer(self) -> int:
		return self._missionTimerValue

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

	def setHealthPoints(self, newValue):
		self._healthPointsValue = newValue

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
			self._activityTypeValue = activityType

			# If we're waking up a Unit then remove it's fortification bonus
			if activityType == UnitActivityType.awake:
				self.setFortifyTurns(0, simulation)


			simulation.userInterface.refreshUnit(self)

		return

	def isHuman(self) -> bool:
		return self.player.isHuman()

	def isFortified(self) -> bool:
		return self._fortifyTurnsValue > 0

	def isFortifiedThisTurn(self) -> bool:
		return self._fortifiedThisTurnValue

	def fortifyTurns(self) -> int:
		return self._fortifyTurnsValue

	def setFortifyTurns(self, newValue: int, simulation):
		# range(iNewValue, 0, GC.getMAX_FORTIFY_TURNS());

		if newValue != self._fortifyTurnsValue:
			# Unit subtly slipped into Fortification state by remaining stationary for a turn
			if self.fortifyTurns() == 0 and newValue > 0:
				simulation.userInterface.animateUnit(self, UnitAnimationType.fortify)

			self._fortifyTurnsValue = newValue
			# setInfoBarDirty(true);

			# Fortification turned off, send an event noting this
			if newValue == 0:
				self.setFortifiedThisTurn(False, simulation)

		return

	def setFortifiedThisTurn(self, fortifiedThisTurn: bool, simulation):
		if not self.isEverFortifyable() and fortifiedThisTurn:
			return

		if self.isFortifiedThisTurn() != fortifiedThisTurn:
			self._fortifiedThisTurnValue = fortifiedThisTurn

			if fortifiedThisTurn:
				turnsToFortify = 1
				if not self.isFortifyable(canWaitForNextTurn=False, simulation=simulation):
					turnsToFortify = 0

				# Manually set us to being fortified for the first turn (so we get the Fort bonus immediately)
				self.setFortifyTurns(turnsToFortify, simulation)

				if turnsToFortify > 0:
					# auto_ptr < ICvUnit1 > pDllUnit(new CvDllUnit(this));
					# gDLL->GameplayUnitFortify(pDllUnit.get(), true);
					simulation.userInterface.animateUnit(self, UnitAnimationType.fortify)
			else:
				simulation.userInterface.animateUnit(self, UnitAnimationType.unfortify)

		return

	def isEverFortifyable(self):
		"""Can this Unit EVER fortify? (maybe redundant with some other stuff)"""
		# /*|| noDefensiveBonus()*/
		if not self.isCombatUnit() or (self.domain() != UnitDomainType.land and self.domain() != UnitDomainType.immobile):
			return False

		return True

	def isFortifyable(self, canWaitForNextTurn: bool, simulation):
		# Can't fortify if you've already used any moves this turn
		if not canWaitForNextTurn:
			if self.hasMoved(simulation):
				return False

		if not self.isEverFortifyable():
			return False

		return True

	def isCombatUnit(self) -> bool:
		"""Combat eligibility routines"""
		return self.unitType.meleeStrength() > 0

	def doFoundWith(self, name: str, simulation):
		if not self.canFoundAt(self.location, simulation):
			return False

		for neighbor in self.location.neighbors():
			newPlot = simulation.tileAt(neighbor)

			if newPlot.hasImprovement(ImprovementType.barbarianCamp):
				self.player.doClearBarbarianCampAt(newPlot, simulation)

				# initiationRites - +50 Faith for each Barbarian Outpost cleared.The unit that cleared the Barbarian Outpost heals +100 HP.
				if self.player.religion.pantheon() == PantheonType.initiationRites:
					self.setHealthPoints(self.maxHealthPoints())

			elif newPlot.hasImprovement(ImprovementType.goodyHut):
				self.player.doGoodyHutAt(newPlot, self, simulation)

		self.player.foundAt(self.location, name=name, simulation=simulation)

		# ancestralHall - New cities receive a free Builder
		if self.player.hasBuilding(BuildingType.ancestralHall, simulation):
			newCity = simulation.cityAt(self.location)

			# hack - add fake money - it will be removed once the builder is purchased
			purchaseCost = newCity.goldPurchaseCostOf(UnitType.builder, simulation)
			self.player.treasury.changeGoldBy(purchaseCost)

			# now purchase the builder
			newCity.purchaseUnit(UnitType.builder, YieldType.gold, simulation)

		self.doKillDelayed(False, None, simulation)

		return True

	def doKillDelayed(self, delayed: bool, otherPlayer, simulation):
		if self.player.isBarbarian():
			# Bronze Working eureka: Kill 3 Barbarians
			otherPlayer.techs.changeEurekaValueFor(TechType.bronzeWorking, change=1)

			if otherPlayer.tech.changeEurekaValueFor(TechType.bronzeWorking) >= 3:
				otherPlayer.tech.triggerEurekaFor(TechType.bronzeWorking, simulation)

		if delayed:
			self.startDelayedDeath()
			return

		if otherPlayer is not None:
			# FIXME - add die visualization
			pass

		simulation.concealAt(self.location, sight=self.sight(), unit=self, player=self.player)

		simulation.userInterface.hideUnit(self, self.location)
		simulation.removeUnit(self)

	def canHoldAt(self, location, simulation):
		# fixme
		return False

	def popMission(self):
		if len(self._missions) > 0:
			self._missions.pop()

		if len(self._missions) == 0:
			if self._activityTypeValue == UnitActivityType.mission:
				self._activityTypeValue = UnitActivityType.none

		return

	def sight(self):
		sightValue = self.unitType.sight()

		# spyglass - +1 sight range.
		if self.hasPromotion(UnitPromotionType.spyglass):
			sightValue += 1

		# rutter - +1 sight range.
		if self.hasPromotion(UnitPromotionType.rutter):
			sightValue += 1

		return sightValue

	def doAttackInto(self, destination: HexPoint, steps: int, simulation) -> bool:
		"""Returns true if attack was made...
			UnitAttack in civ5"""
		destPlot = simulation.tileAt(destination)

		attack = False
		# wrapX: Int = gameModel.wrappedX() ? gameModel.mapSize().width(): -1
		adjacent = self.location.isNeighborOf(destination)

		if adjacent:
			if self.isOutOfAttacks(simulation):
				return False

			# Air mission
			if self.domain() == UnitDomainType.air and self.baseCombatStrength() == 0:
				if self.canRangeStrikeAt(destination, needWar=False, noncombatAllowed=True, simulation=simulation):
					attack = True
					Combat.doAirAttack(self, destPlot, simulation=simulation)

			elif destPlot.isCity():  # City combat
				city = simulation.cityAt(destination)
				if city is not None:
					if self.player.diplomacyAI.isAtWarWith(city.player):
						if self.domain() == UnitDomainType.land:
							# Ranged units that are embarked can't do a move-attack
							if self.isRanged() and self.isEmbarked():
								return False

							attack = True
							Combat.doMeleeAttack(self, city, simulation)

			else: # Normal unit combat
				# if there are no defenders, do not attack
				defenderUnit = simulation.unitAt(destination, UnitMapType.combat)
				if defenderUnit is None:
					return False

				# Ranged units that are embarked can't do a move-attack
				if self.isRanged() and self.isEmbarked():
					return False

				if not self.player.diplomacyAI.isAtWarWith(defenderUnit.player) or not defenderUnit.isBarbarian():
					return False

				attack = True
				Combat.doMeleeAttack(self, defenderUnit, simulation)

				self.player.addMoment(MomentType.battleFought, simulation)

			# Barb camp here that was attacked?
			if destPlot.improvement() == ImprovementType.barbarianCamp:
				simulation.doCampAttackedAt(destPlot.point)

		return attack

	def isTrading(self) -> bool:
		return False

	def doMoveOnPathTowards(self, target: HexPoint, previousETA: int, buildingRoute: bool, simulation):
		"""
		// UnitPathTo
		// Returns the number of turns it will take to reach the target.
		// If no move was made it will return 0.
		// If it can reach the target in one turn or less than one turn (i.e. not use up all its movement points) it will return 1
		"""
		if self.location == target:
			print("Already at location")
			return 0

		pathPlot = None

		targetPlot = simulation.tileAt(target)
		if targetPlot is None:
			print("Destination is not a valid plot location")
			return 0

		path = self.pathTowards(target, options=None, simulation=simulation)
		if path is None:
			print("Unable to generate path with BuildRouteFinder")
			if self.unitType == UnitType.trader:
				self.finishMoves()  # skip one turn
			else:
				self.doCancelOrder(simulation)

			return 0

		if self.domain() == UnitDomainType.air:

			if not self.canMoveInto(target, options=None, simulation=simulation):
				return 0

			pathPlot = targetPlot
		else:
			if len(path) > 1:
				pathPlot = simulation.tileAt(path[1])

			if buildingRoute:
				if pathPlot is None or not self.canMoveInto(target, options=None, simulation=simulation):
					# add route interrupted
					simulation.humanPlayer().notifications().addNotification(NotificationType.generic)
					return 0

		rejectMove = False

		# handle empty path
		if len(path.points()) > 0:
			firstCost = path.costs()[0]

			if previousETA >= 0 and int(firstCost) > previousETA + 2:
				# LOG_UNIT_MOVES_MESSAGE_OSTR(std::string("Rejecting move iPrevETA=") << iPrevETA << std::string(", m_iData2=") << kNode.m_iData2);
				rejectMove = True

			# if we should end our turn there this turn, but can't move into that tile
			if int(firstCost) == 1 and not self.canMoveInto(target, options=None, simulation=simulation):
				if self.peekMission() is not None:
					if self.peekMission().startedInTurn != simulation.currentTurn:
						# LOG_UNIT_MOVES_MESSAGE_OSTR(std::
						#	string("Rejecting move pkMissionData->iPushTurn=") << pkMissionData->iPushTurn << std::string(
						#	", GC.getGame().getGameTurn()=") << GC.getGame().getGameTurn());
						rejectMove = True

			if rejectMove:
				# m_kLastPath.clear();
				# slewis - perform its queued moves?
				self.publishQueuedVisualizationMoves(simulation)
				return 0

		usedPathCost = 0.0

		# this is wrong - unsure where it gets broken
		path.cropPointsUntil(self.location)

		print(f"unit {self.location} => doMoveOnPath({path})")
		for (index, point) in enumerate(path):
			# skip if already at point
			if point == self.location:
				continue

			if self.doMoveOnto(point, simulation):
				if self.isTrading():
					tile = simulation.tileAt(point)
					if tile is not None:
						tile.setRoute(self.player.bestRouteAt(tile))
						simulation.userInterface.refreshTile(tile)

				usedPathCost += path[index].cost

		self.publishQueuedVisualizationMoves(simulation)

		if len(path.points()) > 0:
			tmp = (path.cost() - usedPathCost) / float(self.maxMoves(simulation))
			if 0.0 < tmp < 1.0:
				return 1
			return int(tmp)

		return 1

	def pathTowards(self, target: HexPoint, options, simulation) -> Optional[HexPath]:
		return None

	def doCancelOrder(self, simulation):
		pass
