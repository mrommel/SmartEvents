import sys
from typing import Optional

from game.buildings import BuildingType
from game.combat import Combat
from game.governors import GovernorTitle
from game.moments import MomentType
from game.notifications import NotificationType
from game.policyCards import PolicyCardType
from game.religions import PantheonType
from game.states.ages import AgeType
from game.states.builds import BuildType
from game.states.dedications import DedicationType
from game.types import EraType, TechType
from game.unitMissions import UnitMission
from game.unitTypes import UnitTaskType, UnitType, UnitPromotionType, MoveOptions, UnitMissionType, UnitActivityType, \
	UnitMapType
from map.base import HexPoint, HexArea
from map.improvements import ImprovementType
from map.path_finding.path import HexPath
from map.types import UnitDomainType, YieldType, ResourceType, RouteType
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
		self._buildTypeValue = None
		self._buildChargesValue = unitType.buildCharges()

		self._fortifyTurnsValue = 0
		self._fortifiedThisTurnValue = False
		self._fortifyValue = 0

		self._garrisonedValue: bool = False

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
			if self.canBuild(buildType=mission.buildType, location=mission.unit.location, simulation=simulation):
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

	def isGarrisoned(self) -> bool:
		return self._garrisonedValue

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

	def doHeal(self, simulation):
		# no heal for barbarians
		if self.isBarbarian():
			return

		healRate = self.healRateAt(self.location, simulation)

		# governor effect guard
		unitTile = simulation.tileAt(self.location)

		city = unitTile.workingCity()
		if city is not None:
			governor = city.governor()
			if governor is not None:
				# layingOnOfHands - All Governor's units heal fully in one turn in tiles of this city.
				if governor.hasTitle(GovernorTitle.layingOnOfHands):
					healRate = int(Unit.maxHealth) - self._healthPointsValue

		self._healthPointsValue += healRate

		if self._healthPointsValue > int(Unit.maxHealth):
			self._healthPointsValue = int(Unit.maxHealth)

		return

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
			if len(path.points()) > 1:
				pathPlot = simulation.tileAt(path.points()[1])

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

		# fixme this is wrong - unsure where it gets broken
		# path.cropPointsUntil(self.location)

		print(f"unit {self.location} => doMoveOnPath({path})")
		for (index, point) in enumerate(path.points()):
			# skip if already at point
			if point == self.location:
				continue

			if self.doMoveOnto(point, simulation):
				if self.isTrading():
					tile = simulation.tileAt(point)
					if tile is not None:
						tile.setRoute(self.player.bestRouteAt(tile))
						simulation.userInterface.refreshTile(tile)

				usedPathCost += path.costs()[index]

		self.publishQueuedVisualizationMoves(simulation)

		if len(path.points()) > 0:
			tmp = (path.cost() - usedPathCost) / float(self.maxMoves(simulation))
			if 0.0 < tmp < 1.0:
				return 1
			return int(tmp)

		return 1

	def pathTowards(self, target: HexPoint, options, simulation) -> Optional[HexPath]:
		return simulation.pathTowards(target, options, self)

	def doCancelOrder(self, simulation):
		pass

	def movementType(self):
		return self.unitType.movementType()

	def doMoveOnto(self, target: HexPoint, simulation) -> bool:
		targetPlot = simulation.tileAt(target)
		oldPlot = simulation.tileAt(self.location)

		costDataSource = simulation.unitAwarePathfinderDataSource(self)

		if not self.canMove():
			return False

		shouldDeductCost: bool = True
		moveCost = costDataSource.costToMove(self.location, target)

		# we need to get our dis / embarking on
		if self.canEverEmbark() and targetPlot.terrain().isWater() != oldPlot.terrain().isWater():
			if oldPlot.terrain().isWater():
				if self.isEmbarked():
					# moving from water to the land
					#/ * if self.moveLocations.count > 0 {
					# If we have some queued moves, execute them now, so that the disembark is done at the proper location visually
					#self.publishQueuedVisualizationMoves( in: gameModel)
					#} * /

					self.doDisembark(simulation)

			else:
				if not self.isEmbarked() and self.canEmbarkInto(target, simulation):
					# moving from land to the water
					# if self.moveLocations.count > 0
					# If we have some queued moves, execute them now, so that the disembark is done at the proper location visually
					# self.publishQueuedVisualizationMoves( in: gameModel)

					self.doEmbark(simulation)
					self.finishMoves()
					shouldDeductCost = False

		if shouldDeductCost:
			self._movesValue -= int(moveCost)

			if self._movesValue < 0:
				self._movesValue = 0

		self.setLocation(target, simulation=simulation)

		return True

	def canEverEmbark(self) -> bool:
		# https://civilization.fandom.com/wiki/Movement_(Civ6)?so=search#Embarking
		# only land units can embark
		if self.domain() != UnitDomainType.land:
			return False

		if self.unitType == UnitType.builder and self.player.hasTech(TechType.sailing):
			return True

		if self.player.canEmbark():
			return True

		return False

	def isBusy(self) -> bool:
		if self.missionTimer() > 0:
			return True

		# if self.isInCombat():
		# 	return True

		return False

	def canFortifyAt(self, point, simulation):
		if self.player.isHuman() and self._fortifyValue == 0:
			# num friendly units
			pass

		# a unit can either fortify or garrison. Never both.
		if self.canGarrisonAt(point, simulation):
			return False

		if not self.isFortifyable(canWaitForNextTurn=True, simulation=simulation):
			return False

		if self.isWaiting():
			return False

		return True

	def setFortifiedThisTurnTo(self, fortifiedThisTurn: bool, simulation):
		if not self.isEverFortifyable() and fortifiedThisTurn:
			return

		if self.isFortifiedThisTurn() != fortifiedThisTurn:
			self._fortifiedThisTurnValue = fortifiedThisTurn

			if fortifiedThisTurn:
				turnsToFortify = 1
				if not self.isFortifyableCanWaitForNextTurn(False, simulation):
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

	def canGarrisonAt(self, point, simulation) -> bool:
		# garrison only in cities
		if simulation.cityAt(point) is None:
			return False

		# only one unit per tile, or we are the units?
		if simulation.unitAt(point, self.unitMapType()) is not None and self.location != point:
			return False

		return True

	def doGarrison(self, simulation) -> bool:
		# garrison only in cities guard
		city = simulation.cityAt(self.location)
		if city is None:
			return False

		if not self.canGarrisonAt(self.location, simulation):
			return False

		city.setGarrison(unit=self)
		self._garrisonedValue = True

		return True

	def unitMapType(self) -> UnitMapType:
		if self.unitType.unitClass() == UnitMapType.civilian:
			return UnitMapType.civilian
		else:
			return UnitMapType.combat

	def isWaiting(self):
		return self._activityTypeValue == UnitActivityType.hold or self._activityTypeValue == UnitActivityType.sleep or \
			self._activityTypeValue == UnitActivityType.heal or self._activityTypeValue == UnitActivityType.sentry or \
			self._activityTypeValue == UnitActivityType.intercept

	def isFortifyableCanWaitForNextTurn(self, canWaitForNextTurn: bool, simulation):
		# Can't fortify if you've already used any moves this turn
		if not canWaitForNextTurn:
			if self.hasMoved(simulation):
				return False

		if not self.isEverFortifyable():
			return False

		return True

	def isBarbarian(self) -> bool:
		return self.player.isBarbarian()

	def isHuman(self) -> bool:
		return self.player.isHuman()

	def canBuild(self, buildType: BuildType, location: HexPoint, testVisible: Optional[bool] = False,
	             testGold: Optional[bool] = True, simulation = None):
		if simulation is None:
			raise Exception('Simulation must not be None')

		tile = simulation.tileAt(location)

		# don't build twice
		if buildType.improvement() is not None:
			if tile.hasImprovement(buildType.improvement()):
				return False

		# no improvements in cities
		if buildType.improvement() != ImprovementType.none:
			if tile.isCity():
				return False

		if not self.unitType.canBuild(buildType):
			return False

		if not self.player.canBuild(buildType, location, testGold=testGold, simulation=simulation):
			return False

		validBuildPlot = self.domain() == tile.terrain().domain()  # self.isNativeDomain(at: point, in: gameModel)
		validBuildPlot = validBuildPlot or (buildType.isWater() and self.domain() == UnitDomainType.land and
		                                    tile.isWater() and (self.canEmbark(simulation) or self.isEmbarked()))

		if not validBuildPlot:
			return False

		if testVisible:
			# check for any other units working in this plot
			for loopUnit in simulation.unitsAt(location):
				if loopUnit.isEqualTo(self):
					continue

				loopMission = loopUnit.peekMission()
				if loopMission is not None:
					if loopMission.buildType is not None:
						return False

		return True

	def continueBuilding(self, buildType: BuildType, simulation) -> bool:
		"""Returns true if build should continue..."""
		canContinue = False

		tile = simulation.tileAt(self.location)
		if tile is None:
			return False

		if self.isAutomated():
			if tile.improvement() != ImprovementType.none and tile.improvement() != ImprovementType.ruins:
				resource = tile.resourceFor(self.player)
				if resource == ResourceType.none or resource.techCityTrade():
					if tile.improvement().pillageImprovement() != ImprovementType.none:
						return False

		# Don't check for Gold cost here (2nd false) because this function is called from continueMission... we spend the Gold then check to see if we can Build
		if self.canBuild(buildType, self.location, testVisible=False, testGold=False, simulation=simulation):
			canContinue = True

			if self.doBuild(buildType, simulation):
				canContinue = False

		return canContinue

	def doBuild(self, buildType: BuildType, simulation) -> bool:
		"""
		Returns true if build finished...
        bool CvUnit::build(BuildTypes eBuild)

		@param buildType:
		@param simulation:
		@return:
		"""
		tile = simulation.tileAt(self.location)

		self._buildTypeValue = buildType

		if tile is not None:
			resource = tile.resourceFor(self.player)
			if resource != ResourceType.none:
				player = tile.owner()
				if player is not None:
					resourceQuantity = tile.resourceQuantity()
					player.changeNumberOfAvailableResource(resource, float(resourceQuantity))

		finished: bool = False

		# Don't test Gold
		if not self.canBuild(buildType, self.location, testVisible=False, testGold=False, simulation=simulation):
			return False

		startedYet = tile.buildProgressOf(buildType)

		# if we are starting something new, wipe out the old thing immediately
		if startedYet == 0:
			if buildType.improvement() is not None:
				if tile.improvement() != ImprovementType.none:
					tile.setImprovement(ImprovementType.none)

				# FIXME wipe out all build progress also

		rate = self.unitType.workRate()
		finished = tile.changeBuildProgressOf(buildType, change=rate, player=self.player, simulation=simulation)

		# needs to be at bottom because movesLeft() can affect workRate()...
		self.finishMoves()

		if finished:
			if buildType.isKill():
				if self.isGreatPerson():
					raise Exception("niy")
					# player.doGreatPersonExpended(of: self.type)

				self.doKill(delayed=True, player=None, simulation=simulation)

			if self.unitType == UnitType.builder:
				self.changeBuildChargesBy(-1)

				# handle builder expended
				if not self.hasBuildCharges():
					self.doKill(delayed=True, player=None, simulation=simulation)

			# Add to player's Improvement count, which will increase cost of future Improvements
			if buildType.improvement() is not None or buildType.route() is not None:
				# Prevents chopping Forest or Jungle from counting
				self.player.changeTotalImprovementsBuiltBy(1)

			simulation.userInterface.refreshTile(tile)
		else:
			# we are not done doing this
			if startedYet == 0:
				if tile.isVisibleTo(self.player):
					if buildType.improvement() is not None:
						simulation.userInterface.refreshTile(tile)
					elif buildType.route() is not None:
						simulation.userInterface.refreshTile(tile)

		return finished

	def changeBuildChargesBy(self, change: int):
		if self._buildChargesValue + change < 0:
			print("buildCharges cant be negative")
			return

		self._buildChargesValue += change
		return

	def buildCharges(self) -> int:
		return self._buildChargesValue

	def hasBuildCharges(self) -> bool:
		return self._buildChargesValue > 0

	def canHeal(self, simulation):
		# No barb healing
		if self.isBarbarian():
			return False

		# only damaged units can heal
		if self.damage() == 0:
			return False

		# Embarked Units can't heal
		if self.isEmbarked():
			return False

		if self.healRateAt(self.location, simulation) == 0:
			return False

		# twilightValor - All units +5 Combat Strength for all melee attack units.
		# BUT: Cannot heal outside your territory.
		if self.player.government.hasCard(PolicyCardType.twilightValor):
			unitTile = simulation.tileAt(self.location)
			return unitTile.isFriendlyTerritoryFor(self.player, simulation)

		return True

	def healRateAt(self, location: HexPoint, simulation):
		if self.player.isBarbarian():
			return 0

		totalHeal = 0

		if simulation.cityAt(location) is not None:
			totalHeal += 10 # CITY_HEAL_RATE

		# Heal from religion
		# next to a city or in the city - check for beliefs

		# Heal from units - medic/supply convoy
		extraHealFromUnits: int = 0
		for neighbor in location.neighbors():
			unit = simulation.unitAt(neighbor, UnitMapType.civilian)
			if unit is not None:
				# friends or us
				if self.player.isEqualTo(unit.player) or self.player.diplomacyAI.isAllianceActiveWith(unit.player):
					extraHealFromUnits += unit.unitType.healingAdjacentUnits()

		# Heal from territory ownership (friendly, enemy, etc.)
		tile = simulation.tileAt(location)
		if tile is not None:
			if tile.isFriendlyTerritoryFor(self.player, simulation):
				totalHeal += 20
			elif tile.isEnemyTerritoryFor(self.player, simulation):
				totalHeal += 5
			else:
				totalHeal += 10

		return totalHeal + extraHealFromUnits

	def canPillageAt(self, location, simulation):
		tile = simulation.tileAt(location)

		if self.isEmbarked():
			return False

		if not self.unitType.canPillage():
			return False

		# Barbarian boats not allowed to pillage, as they're too annoying :)
		if self.isBarbarian() and self.domain() == UnitDomainType.sea:
			return False

		if tile.isCity():
			return False

		improvementType = tile.improvement()
		if improvementType == ImprovementType.none:
			if tile.hasRoute(RouteType.none):
				return False
		elif improvementType == ImprovementType.ruins:
			return False
		elif improvementType == ImprovementType.goodyHut:
			return False

		# Either nothing to pillage or everything is pillaged to its max
		if (improvementType == ImprovementType.none or tile.isImprovementPillaged()) and \
			(tile.hasRoute(RouteType.none) or tile.isRoutePillaged()):
			return False

		# if tile.hasOwner():
		# 	if (!potentialWarAction(pPlot)):
		# 		if ((eImprovementType == NO_IMPROVEMENT and !pPlot->isRoute()) or (pPlot->getOwner() != getOwner())):
		# 			return False

		# can no longer pillage our tiles
		if self.player.isEqualTo(tile.owner()):
			return False

		return True

	def doPillage(self, simulation) -> bool:
		if not self.canPillageAt(self.location, simulation):
			return False

		tile = simulation.tileAt(self.location)
		if tile is not None:
			improvement = tile.improvement()
			if not improvement.canBePillaged():
				return False
			else:
				movesCost: int = 2

				# depredation - Pillaging costs only 1 Movement point.
				if self.hasPromotion(UnitPromotionType.depredation):
					movesCost = 1

				self._movesValue -= movesCost

				if self._movesValue < 0:
					self._movesValue = 0

				tile.setImprovementPillaged(True)

				resource = tile.resourceFor(self.player)
				if resource != ResourceType.none:
					player = tile.owner()
					if player is not None:
						resourceQuantity = tile.resourceQuantity()
						player.changeNumberOfAvailableResource(resource, change=-float(resourceQuantity))

				return True

		return False

