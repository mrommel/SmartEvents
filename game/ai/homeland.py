import sys
from typing import Optional

from game.cities import City
from game.flavors import FlavorType
from game.states.builds import BuildType
from game.unitTypes import UnitTaskType, UnitMapType, UnitMissionType
from game.units import Unit, UnitAutomationType, UnitMission
from map.base import HexPoint
from map.improvements import ImprovementType
from map.types import UnitDomainType
from utils.base import ExtendedEnum, InvalidEnumError


class HomelandMoveTypeData:
	def __init__(self, name: str, priority: int):
		self.name = name
		self.priority = priority


class HomelandMoveType(ExtendedEnum):
	none = 'none'  # AI_HOMELAND_MOVE_NONE = -1,
	unassigned = 'unassigned'  # AI_HOMELAND_MOVE_UNASSIGNED,
	explore = 'explore'  # AI_HOMELAND_MOVE_EXPLORE,
	exploreSea = 'exploreSea'  # AI_HOMELAND_MOVE_EXPLORE_SEA,
	settle = 'settle'  # AI_HOMELAND_MOVE_SETTLE,
	garrison = 'garrison'  # AI_HOMELAND_MOVE_GARRISON,
	heal = 'heal'  # AI_HOMELAND_MOVE_HEAL,
	toSafety = 'toSafety'  # AI_HOMELAND_MOVE_TO_SAFETY,
	mobileReserve = 'mobileReserve'  # AI_HOMELAND_MOVE_MOBILE_RESERVE,
	sentry = 'sentry'  # AI_HOMELAND_MOVE_SENTRY,
	worker = 'worker'  # AI_HOMELAND_MOVE_WORKER,
	workerSea = 'workerSea'  # AI_HOMELAND_MOVE_WORKER_SEA,
	patrol = 'patrol'  # AI_HOMELAND_MOVE_PATROL,
	upgrade = 'upgrade'  # AI_HOMELAND_MOVE_UPGRADE,
	ancientRuins = 'ancientRuins'  # AI_HOMELAND_MOVE_ANCIENT_RUINS,
	# garrisonCityState = ''  # AI_HOMELAND_MOVE_GARRISON_CITY_STATE,
	# writer = ''  # AI_HOMELAND_MOVE_WRITER,
	# artistGoldenAge = ''  # AI_HOMELAND_MOVE_ARTIST_GOLDEN_AGE,
	# musician = ''  # AI_HOMELAND_MOVE_MUSICIAN,
	# scientiestFreeTech = ''  # AI_HOMELAND_MOVE_SCIENTIST_FREE_TECH,
	# none = ''  # AI_HOMELAND_MOVE_MERCHANT_TRADE,
	# none = ''  # AI_HOMELAND_MOVE_ENGINEER_HURRY,
	# none = ''  # AI_HOMELAND_MOVE_GENERAL_GARRISON,
	# none = ''  # AI_HOMELAND_MOVE_ADMIRAL_GARRISON,
	# none = ''  # AI_HOMELAND_MOVE_SPACESHIP_PART,
	aircraftToTheFront = 'aircraftToTheFront'  # AI_HOMELAND_MOVE_AIRCRAFT_TO_THE_FRONT,
	# none = ''  # AI_HOMELAND_MOVE_PROPHET_RELIGION,
	# missionary = ''  # AI_HOMELAND_MOVE_MISSIONARY,
	# inquisitor = ''  # AI_HOMELAND_MOVE_INQUISITOR,
	tradeUnit = 'tradeUnit'  # AI_HOMELAND_MOVE_TRADE_UNIT,

	# archaeologist = ''  # AI_HOMELAND_MOVE_ARCHAEOLOGIST,
	# addSpaceshipPart = ''  # AI_HOMELAND_MOVE_ADD_SPACESHIP_PART,
	# airlift = ''  # AI_HOMELAND_MOVE_AIRLIFT

	def name(self) -> str:
		return self._data().name

	def priority(self) -> int:
		return self._data().priority

	def _data(self) -> HomelandMoveTypeData:
		if self == HomelandMoveType.none:
			return HomelandMoveTypeData(name="none", priority=0)
		elif self == HomelandMoveType.unassigned:
			return HomelandMoveTypeData(name="unassigned", priority=0)

		elif self == HomelandMoveType.explore:
			return HomelandMoveTypeData(name="explore", priority=35)
		elif self == HomelandMoveType.exploreSea:
			return HomelandMoveTypeData(name="exploreSea", priority=35)
		elif self == HomelandMoveType.settle:
			return HomelandMoveTypeData(name="settle", priority=50)
		elif self == HomelandMoveType.garrison:
			return HomelandMoveTypeData(name="garrison", priority=10)
		elif self == HomelandMoveType.heal:
			return HomelandMoveTypeData(name="heal", priority=30)
		elif self == HomelandMoveType.toSafety:
			return HomelandMoveTypeData(name="toSafety", priority=30)
		elif self == HomelandMoveType.mobileReserve:
			return HomelandMoveTypeData(name="mobileReserve", priority=15)
		elif self == HomelandMoveType.sentry:
			return HomelandMoveTypeData(name="sentry", priority=20)
		elif self == HomelandMoveType.worker:
			return HomelandMoveTypeData(name="worker", priority=30)
		elif self == HomelandMoveType.workerSea:
			return HomelandMoveTypeData(name="workerSea", priority=30)
		elif self == HomelandMoveType.patrol:
			return HomelandMoveTypeData(name="patrol", priority=0)
		elif self == HomelandMoveType.upgrade:
			return HomelandMoveTypeData(name="upgrade", priority=25)
		elif self == HomelandMoveType.ancientRuins:
			return HomelandMoveTypeData(name="ancientRuins", priority=40)
		elif self == HomelandMoveType.aircraftToTheFront:
			return HomelandMoveTypeData(name="aircraftToTheFront", priority=50)

		elif self == HomelandMoveType.tradeUnit:
			return HomelandMoveTypeData(name="tradeUnit", priority=100)

		raise InvalidEnumError(self)


class HomelandMove:
	"""Object stored in the list of move priorities (movePriorityList)"""

	def __init__(self, moveType: HomelandMoveType, priority: int = 0):
		self.moveType = moveType
		self.priority = priority

	def __lt__(self, other):
		if isinstance(other, HomelandMove):
			return self.priority > other.priority

		raise Exception('wrong type: HomelandMove expected')

	def __eq__(self, other) -> bool:
		if isinstance(other, HomelandMove):
			return self.moveType == other.moveType and self.priority == other.priority

		raise Exception('wrong type: HomelandMove expected')


class HomelandUnit:
	"""Object stored in the list of current move units (m_CurrentMoveUnits)"""

	def __init__(self, unit):
		self.unit = unit
		self.movesToTarget: int = 0
		self.target: Optional[HexPoint] = None

	def __lt__(self, other):
		if isinstance(other, HomelandUnit):
			return self.movesToTarget < other.movesToTarget

		raise Exception('wrong type: HomelandUnit expected')

	def __eq__(self, other) -> bool:
		if isinstance(other, HomelandUnit):
			return self.movesToTarget == other.movesToTarget

		raise Exception('wrong type: HomelandUnit expected')


class HomelandTargetType(ExtendedEnum):
	city = 'city'  # AI_HOMELAND_TARGET_CITY
	sentryPoint = 'sentryPoint'  # AI_HOMELAND_TARGET_SENTRY_POINT
	fort = 'fort'  # AI_HOMELAND_TARGET_FORT
	navalResource = 'navalResource'  # AI_HOMELAND_TARGET_NAVAL_RESOURCE
	homeRoad = 'homeRoad'  # AI_HOMELAND_TARGET_HOME_ROAD
	ancientRuin = 'ancientRuin'  # AI_HOMELAND_TARGET_ANCIENT_RUIN


class HomelandTarget:
	"""
	A target of opportunity for the Homeland AI this turn

	Key Attributes:
	- Arises during processing of CvHomelandAI::FindHomelandTargets()
	- Targets are reexamined each turn (so shouldn't need to be serialized)
	"""

	def __init__(self, targetType: HomelandTargetType):
		self.targetType = targetType
		self.target: Optional[HexPoint] = None
		self.city: Optional[City] = None
		self.threatValue: int = 0
		self.improvement: ImprovementType = ImprovementType.none

	def __lt__(self, other):
		if isinstance(other, HomelandTarget):
			return self.threatValue < other.threatValue

		raise Exception('wrong type: HomelandTarget expected')

	def __eq__(self, other) -> bool:
		if isinstance(other, HomelandTarget):
			return self.threatValue == other.threatValue

		raise Exception('wrong type: HomelandTarget expected')


class HomelandAI:
	flavorDampening = 0.3  # AI_TACTICAL_FLAVOR_DAMPENING_FOR_MOVE_PRIORITIZATION
	defensiveMoveTurns = 4  # AI_HOMELAND_MAX_DEFENSIVE_MOVE_TURNS
	maxDangerLevel = 100000.0  # MAX_DANGER_VALUE

	def __init__(self, player):
		self.player = player
		self.currentTurnUnits: [Unit] = []
		self.currentMoveUnits: [HomelandUnit] = []
		self.currentMoveHighPriorityUnits: [HomelandUnit] = []

		self.movePriorityList: [HomelandMove] = []
		self.movePriorityTurn: int = 0

		self.currentBestMoveUnit: Optional[Unit] = None
		self.currentBestMoveUnitTurns: int = sys.maxsize
		self.currentBestMoveHighPriorityUnit: Optional[Unit]
		self.currentBestMoveHighPriorityUnitTurns: int = sys.maxsize

		self.targetedCities: [HomelandTarget] = []
		self.targetedSentryPoints: [HomelandTarget] = []
		self.targetedForts: [HomelandTarget] = []
		self.targetedNavalResources: [HomelandTarget] = []
		self.targetedHomelandRoads: [HomelandTarget] = []
		self.targetedAncientRuins: [HomelandTarget] = []

	def doTurn(self, simulation):
		"""Update the AI for units"""
		# no homeland for barbarians
		if self.player.isBarbarian():
			for loopUnit in simulation.unitsOf(self.player):
				if not loopUnit.processedInTurn():
					loopUnit.setTurnProcessedTo(True)

			return

		if self.player.isHuman():
			self.findAutomatedUnits(simulation)
		else:
			self.recruitUnits(simulation)

		# Make sure we have a unit to handle
		if len(self.currentTurnUnits) > 0:
			# Make sure the economic plots are up - to - date, it has a caching system in it.
			self.player.economicAI.updatePlots(simulation)

			# Start by establishing the priority order for moves this turn
			self.establishHomelandPriorities(simulation)

			# Put together lists of places we may want to move toward
			self.findHomelandTargets(simulation)

			# Loop through each move assigning units when available
			self.assignHomelandMoves(simulation)

		return

	def recruitUnits(self, simulation):
		"""Mark all the units that will be under homeland AI control this turn"""
		self.currentTurnUnits = []

		# Loop through our units
		for unit in simulation.unitsOf(self.player):
			# Never want immobile / dead units or ones that have already moved
			if not unit.processedInTurn() and not unit.isDelayedDeath() and unit.task() != UnitTaskType.unknown and unit.canMove():
				self.currentTurnUnits.append(unit)

		return

	def establishHomelandPriorities(self, simulation):
		"""Choose which moves to emphasize this turn"""
		flavorDefense = int(
			float(self.player.valueOfPersonalityFlavor(FlavorType.defense)) * HomelandAI.flavorDampening)
		# flavorOffense = Int(Double(player.valueOfPersonalityFlavor(of:.offense)) *self.flavorDampening)
		flavorExpand = self.player.valueOfPersonalityFlavor(FlavorType.expansion)
		flavorImprove = 0
		flavorNavalImprove = 0
		flavorExplore = int(float(self.player.valueOfPersonalityFlavor(FlavorType.recon)) * HomelandAI.flavorDampening)
		flavorGold = self.player.valueOfPersonalityFlavor(FlavorType.gold)
		# flavorScience = player.valueOfPersonalityFlavor(of:.science)
		# flavorWonder = player.valueOfPersonalityFlavor(of:.wonder)
		flavorMilitaryTraining = self.player.valueOfPersonalityFlavor(FlavorType.militaryTraining)

		self.movePriorityList = []
		self.movePriorityTurn = simulation.currentTurn

		# Loop through each possible homeland move(other than "none" or "unassigned")
		for homelandMoveType in list(HomelandMoveType):
			priority = homelandMoveType.priority()

			# Garrisons must beat out sentries if policies encourage garrisoning
			if homelandMoveType == HomelandMoveType.garrison:
				# FIXME ??
				pass

			# Make sure base priority is not negative
			if priority >= 0:

				# Defensive moves
				if homelandMoveType in [
					HomelandMoveType.garrison, HomelandMoveType.heal, HomelandMoveType.toSafety,
					HomelandMoveType.mobileReserve, HomelandMoveType.sentry, HomelandMoveType.aircraftToTheFront]:
					priority += flavorDefense

				# Other miscellaneous types
				if homelandMoveType in [HomelandMoveType.explore, HomelandMoveType.exploreSea]:
					priority += flavorExplore

				if homelandMoveType == HomelandMoveType.settle:
					priority += flavorExpand

				if homelandMoveType == HomelandMoveType.worker:
					priority += flavorImprove

				if homelandMoveType == HomelandMoveType.workerSea:
					priority += flavorNavalImprove

				if homelandMoveType == HomelandMoveType.upgrade:
					priority += flavorMilitaryTraining

				if homelandMoveType == HomelandMoveType.ancientRuins:
					priority += flavorExplore

				if homelandMoveType == HomelandMoveType.tradeUnit:
					priority += flavorGold

				# Store off this move and priority
				self.movePriorityList.append(HomelandMove(homelandMoveType, priority))

		# Now sort the moves in priority order
		self.movePriorityList.sort()

	def findHomelandTargets(self, simulation):
		"""Make lists of everything we might want to target with the homeland AI this turn"""
		# Clear out target lists since we rebuild them each turn
		self.targetedCities = []
		self.targetedSentryPoints = []
		self.targetedForts = []
		self.targetedNavalResources = []
		self.targetedHomelandRoads = []
		self.targetedAncientRuins = []

		# Look at every tile on map
		for point in simulation.points():
			tile = simulation.tileAt(point)

			if tile.isVisibleTo(self.player):
				# get some values
				civilianUnit = simulation.unitAt(point, UnitMapType.civilian)
				combatUnit = simulation.unitAt(point, UnitMapType.combat)

				# Have a...
				# ... friendly city?
				city = simulation.cityAt(point)
				if city is not None and city.player.leader == self.player.leader:
					# Don't send another unit, if the tactical AI already sent a garrison here
					addTarget = False

					unit = simulation.unitAt(point, UnitMapType.combat)
					if unit is not None:
						if unit.isUnderTacticalControl():
							addTarget = True
					else:
						addTarget = True

					if addTarget:
						newTarget = HomelandTarget(HomelandTargetType.city)
						newTarget.target = point
						newTarget.city = city
						newTarget.threatValue = city.threatValue()
						self.targetedCities.append(newTarget)

				elif tile.terrain().isWater() and not tile.hasAnyImprovement():
					# ... naval resource?
					if tile.hasAnyResourceFor(self.player):
						workingCity = tile.workingCity()
						if workingCity is not None and workingCity.player.leader == self.player.leader:
							# Find proper improvement
							improvement = next(iter(tile.possibleImprovements()), None)
							if improvement is not None:
								newTarget = HomelandTarget(HomelandTargetType.navalResource)
								newTarget.target = point
								newTarget.improvement = improvement
								self.targetedNavalResources.append(newTarget)

				elif tile.hasImprovement(ImprovementType.goodyHut):
					# ... un-popped goody hut?
					newTarget = HomelandTarget(HomelandTargetType.ancientRuin)
					newTarget.target = point
					self.targetedAncientRuins.append(newTarget)

				elif civilianUnit is not None:
					# ... enemy civilian(or embarked) unit?
					if self.player.diplomacyAI.isAtWarWith(civilianUnit.player) and not civilianUnit.canDefend():
						newTarget = HomelandTarget(HomelandTargetType.ancientRuin)
						newTarget.target = point
						self.targetedAncientRuins.append(newTarget)

				elif tile.terrain().isLand() and combatUnit is None:
					# ... possible sentry point? (must be empty or only have friendly units)

					# Must be at least adjacent to our land
					if tile.owner().leader == self.player.leader or tile.owner() is None:
						# FIXME
						pass

				elif tile.owner().leader == self.player.leader and tile.hasAnyRoute():
					# ...road segment in friendly territory?
					newTarget = HomelandTarget(HomelandTargetType.homeRoad)
					newTarget.target = point
					self.targetedHomelandRoads.append(newTarget)

		# Post - processing on targets
		# FIXME self.eliminateAdjacentSentryPoints();
		# FIXME self.eliminateAdjacentHomelandRoads();
		self.targetedCities.sort()

	def assignHomelandMoves(self, simulation):
		"""Choose which moves to run and assign units to it"""
		# Proceed in priority order
		for movePriorityItem in self.movePriorityList:
			if movePriorityItem.moveType == HomelandMoveType.explore:  # AI_HOMELAND_MOVE_EXPLORE
				self.plotExplorerMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.exploreSea:  # AI_HOMELAND_MOVE_EXPLORE_SEA
				self.plotExplorerSeaMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.settle:  # AI_HOMELAND_MOVE_SETTLE:
				self.plotFirstTurnSettlerMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.garrison:  # AI_HOMELAND_MOVE_GARRISON
				self.plotGarrisonMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.heal:  # AI_HOMELAND_MOVE_HEAL
				self.plotHealMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.toSafety:  # AI_HOMELAND_MOVE_TO_SAFETY
				self.plotMovesToSafety(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.mobileReserve:  # AI_HOMELAND_MOVE_MOBILE_RESERVE
				self.plotMobileReserveMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.sentry:  # AI_HOMELAND_MOVE_SENTRY
				self.plotSentryMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.worker:  # AI_HOMELAND_MOVE_WORKER
				self.plotWorkerMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.workerSea:  # AI_HOMELAND_MOVE_WORKER_SEA
				self.plotWorkerSeaMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.patrol:  # AI_HOMELAND_MOVE_PATROL
				self.plotPatrolMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.upgrade:  # AI_HOMELAND_MOVE_UPGRADE
				self.plotUpgradeMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.ancientRuins:  # AI_HOMELAND_MOVE_ANCIENT_RUINS
				self.plotAncientRuinMoves(simulation)
			elif movePriorityItem.moveType == HomelandMoveType.aircraftToTheFront:  # AI_HOMELAND_MOVE_AIRCRAFT_TO_THE_FRONT
				# FIXME self.plotAircraftMoves()
				pass
			elif movePriorityItem.moveType == HomelandMoveType.tradeUnit:  # AI_HOMELAND_MOVE_TRADE_UNIT
				self.plotTradeUnitMoves(simulation)
		#
		# TODO
		#             /*case .writer:
		#                  # AI_HOMELAND_MOVE_WRITER:
		#	self.plotWriterMoves()*/
		#             /*case AI_HOMELAND_MOVE_ARTIST_GOLDEN_AGE:
		#                 PlotArtistMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_MUSICIAN:
		#                 PlotMusicianMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_SCIENTIST_FREE_TECH:
		#                 PlotScientistMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_ENGINEER_HURRY:
		#                 PlotEngineerMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_MERCHANT_TRADE:
		#                 PlotMerchantMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_GENERAL_GARRISON:
		#                 PlotGeneralMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_ADMIRAL_GARRISON:
		#                 PlotAdmiralMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_PROPHET_RELIGION:
		#                 PlotProphetMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_MISSIONARY:
		#                 PlotMissionaryMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_INQUISITOR:
		#                 PlotInquisitorMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_AIRCRAFT_TO_THE_FRONT:
		#                 PlotAircraftMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_ADD_SPACESHIP_PART:
		#                 PlotSSPartAdds();
		#                 break;
		#             case AI_HOMELAND_MOVE_SPACESHIP_PART:
		#                 PlotSSPartMoves();
		#                 break;*/
		#             /*case AI_HOMELAND_MOVE_ARCHAEOLOGIST:
		#                 PlotArchaeologistMoves();
		#                 break;
		#             case AI_HOMELAND_MOVE_AIRLIFT:
		#                 PlotAirliftMoves();
		#                 break;*/
		#
		#             default:
		#                 print(f"not implemented: HomelandAI - {movePriorityItem.type}")

		self.reviewUnassignedUnits(simulation)
		return

	def plotExplorerMoves(self, simulation):
		"""Get units with explore AI and plan their moves"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.explore or \
				(currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.land and
				 currentTurnUnit.automateType() == UnitAutomationType.explore):
				homelandUnit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(homelandUnit)

		if len(self.currentMoveUnits) > 0:
			# Execute twice so explorers who can reach the end of their sight can move again
			self.executeExplorerMoves(land=True, simulation=simulation)
			self.executeExplorerMoves(land=True, simulation=simulation)

		return

	def plotTradeUnitMoves(self, simulation):
		"""Send trade units on their way"""
		self.clearCurrentMoveUnits()

		# Loop through all remaining units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.trade:
				unit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(unit)

		if len(self.currentMoveUnits) > 0:
			self.executeTradeUnitMoves(simulation)

		return

	def clearCurrentMoveUnits(self):
		self.currentMoveUnits = []
		self.currentBestMoveUnit = None
		self.currentBestMoveUnitTurns = sys.maxsize

	def plotExplorerSeaMoves(self, simulation):
		"""Get units with explore AI and plan their moves"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.exploreSea or \
				(currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.sea and
				 currentTurnUnit.automateType() == UnitTaskType.explore):

				self.currentMoveUnits.append(HomelandUnit(currentTurnUnit))

		if len(self.currentMoveUnits) > 0:
			# Execute twice so explorers who can reach the end of their sight can move again
			self.executeExplorerMoves(land=False, simulation=simulation)
			self.executeExplorerMoves(land=False, simulation=simulation)

		return

	def plotFirstTurnSettlerMoves(self, simulation):
		"""Get our first city built"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			goingToSettle = False

			if not currentTurnUnit.player.isHuman():
				if len(simulation.citiesOf(self.player)) == 0 and len(self.currentMoveUnits) == 0:
					if currentTurnUnit.canFoundAt(currentTurnUnit.location, simulation):
						homelandUnit = HomelandUnit(currentTurnUnit)
						self.currentMoveUnits.append(homelandUnit)
						goingToSettle = True

			# If we find a settler that isn't in an operation, let's keep him in place
			if not goingToSettle and currentTurnUnit.isFound() and currentTurnUnit.army() is None:
				currentTurnUnit.pushMission(UnitMission(UnitMissionType.skip), simulation)
				currentTurnUnit.finishMoves()

		if len(self.currentMoveUnits) > 0:
			self.executeFirstTurnSettlerMoves(simulation)

		return

	def executeFirstTurnSettlerMoves(self, simulation):
		"""Creates cities for AI civs on first turn"""
		for currentMoveUnit in self.currentMoveUnits:
			if currentMoveUnit.unit is not None:
				currentMoveUnit.unit.pushMission(UnitMission(UnitMissionType.found), simulation)
				self.unitProcessed(currentMoveUnit.unit)

				print(f"Founded city at {currentMoveUnit.unit.location}")

		return

	def unitProcessed(self, unit):
		"""Remove a unit that we've allocated from list of units to move this turn"""
		self.currentTurnUnits = list(filter(lambda loopUnit: loopUnit.location != unit.location, self.currentTurnUnits))
		unit.setTurnProcessedTo(True)

	def plotAncientRuinMoves(self, simulation):
		"""Pop goody huts nearby"""
		# Do we have any targets of this type?
		if len(self.targetedAncientRuins) > 0:
			# Prioritize them (LATER)

			# See how many moves of this type we can execute
			for (index, homelandTarget) in enumerate(self.targetedAncientRuins):
				targetTile = simulation.tileAt(homelandTarget.target)

				self.findUnitsForMove(HomelandMoveType.ancientRuins, firstTime=(index == 0), simulation=simulation)

				if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:

					if self.bestUnitToReachTarget(targetTile, HomelandAI.defensiveMoveTurns, simulation):

						self.executeMoveToTarget(targetTile, garrisonIfPossible=False, simulation=simulation)

						if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
							print("Moving to goody hut (non-explorer), \(targetTile.point)")
							# LogHomelandMessage(strLogString);
		return

	def plotUpgradeMoves(self, simulation):
		pass

	def plotHealMoves(self, simulation):
		"""Find out which units would like to heal"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			tile = simulation.tileAt(currentTurnUnit.location)

			if not currentTurnUnit.isHuman():

				# Am I under 100 % health and not at sea or already in a city?
				if currentTurnUnit.healthPoints() < currentTurnUnit.maxHealthPoints() and \
					not currentTurnUnit.isEmbarked() and simulation.cityAt(currentTurnUnit.location) is None:

					# If I'm a naval unit I need to be in friendly territory
					if currentTurnUnit.domain() != UnitDomainType.sea or tile.isFriendlyTerritoryFor(self.player, simulation):

						if not currentTurnUnit.isUnderEnemyRangedAttack():
							self.currentMoveUnits.append(HomelandUnit(currentTurnUnit))

							if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
								print(f"{currentTurnUnit.unitType} healing at {currentTurnUnit.location}")
								# LogHomelandMessage(strLogString);

			if len(self.currentMoveUnits) > 0:
				self.executeHeals(simulation)

	def plotMovesToSafety(self, simulation):
		"""Moved endangered units to safe hexes"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			tile = simulation.tileAt(currentTurnUnit.location)
			dangerLevel = self.player.dangerPlotsAI.dangerAt(currentTurnUnit.location)

			# Danger value of plot must be greater than 0
			if dangerLevel > 0:
				addUnit = False

				# If civilian( or embarked unit) always ready to flee
				# slewis - 4.18.2013 - Problem here is that a combat unit that is a boat can get stuck in a city
				# hiding from barbarians on the land
				if not currentTurnUnit.canDefend():
					if currentTurnUnit.isAutomated() and currentTurnUnit.baseCombatStrength(ignoreEmbarked=True) > 0:
						# then this is our special case
						pass
					else:
						addUnit = True
				elif currentTurnUnit.healthPoints() < currentTurnUnit.maxHealthPoints():
					# Also may be true if a damaged combat unit
					if currentTurnUnit.isBarbarian():
						# Barbarian combat units - only naval units flee (but they flee if have taken ANY damage)
						if currentTurnUnit.domain() == UnitDomainType.sea:
							addUnit = True
					elif currentTurnUnit.isUnderEnemyRangedAttack() or \
						currentTurnUnit.attackStrengthAgainst(unit=None, city=None, tile=tile, simulation=simulation) * 2 <= \
						currentTurnUnit.baseCombatStrength(ignoreEmbarked=False):
						# Everyone else flees at less than or equal to 50% combat strength
						addUnit = True
				elif not currentTurnUnit.isBarbarian():
					# Also flee if danger is really high in current plot (but not if we're barbarian)
					acceptableDanger = currentTurnUnit.attackStrengthAgainst(unit=None, city=None, tile=tile, simulation=simulation) * 100
					if int(dangerLevel) > acceptableDanger:
						addUnit = True

				if addUnit:
					# Just one unit involved in this move to execute
					self.currentMoveUnits.append(HomelandUnit(currentTurnUnit))

		if len(self.currentMoveUnits) > 0:
			self.executeMovesToSafestPlot(simulation)

		return

	def plotWorkerMoves(self, simulation):
		"""Find something for all workers to do"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.work or (currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.land and currentTurnUnit.automateType() == UnitAutomationType.build):
				homelandUnit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(homelandUnit)

		if len(self.currentMoveUnits) > 0:
			self.executeWorkerMoves(simulation)

		return

	def plotWorkerSeaMoves(self, simulation):
		"""Send out work boats to harvest resources"""
		self.clearCurrentMoveUnits()

		# Loop through all recruited units
		for currentTurnUnit in self.currentTurnUnits:
			if currentTurnUnit.task() == UnitTaskType.workerSea or \
			(currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.sea and
			 currentTurnUnit.automateType() == UnitAutomationType.build):

				homelandUnit = HomelandUnit(currentTurnUnit)
				self.currentMoveUnits.append(homelandUnit)

		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit
			targetIndex: Optional[HomelandTarget] = None
			targetMoves: int = sys.maxsize

			pathFinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
				unit.movementType(), unit.player, UnitMapType.combat,
				canEmbark=unit.player.canEmbark(), canEnterOcean=unit.player.canEnterOcean())
			pathFinder = AStarPathfinder(pathFinderDataSource)

			# See how many moves of this type we can execute
			for target in self.targetedNavalResources:
				build = target.improvement.buildType()
				targetLocation = target.target

				if not currentMoveUnit.canBuild(build, targetLocation, testVisible=True, testGold=True, simulation=simulation):
					continue

				moves = pathFinder.turnsToReachTarget(unit, targetLocation, simulation)
				if moves < targetMoves:
					targetMoves = moves
					targetIndex = target

			if targetIndex is not None:
				# Queue best one up to capture it
				targetLocation = targetIndex.target

				result = False
				path = unit.pathTowards(targetLocation, options=None, simulation=simulation)
				if path is not None:
					unit.pushMission(UnitMission(UnitMissionType.moveTo, targetLocation), simulation)
					if unit.location == targetLocation:
						mission = UnitMission(
							UnitMissionType.build,
							buildType=targetIndex.improvement.buildType(),
							target=targetLocation,
							path=path,
							options=None
						)
						unit.pushMission(mission, simulation)
						result = True
					else:
						unit.finishMoves()

					# Delete this unit from those we have to move
					self.unitProcessed(unit)
				else:
					if unit.location == targetLocation:
						mission = UnitMission(
							UnitMissionType.build,
							buildType=BuildType.fromImprovement(targetIndex.improvement),
							location=targetLocation,
							path=None,
							options=None
						)
						unit.pushMission(mission, simulation)
						result = True

				if result:
					print(f"Harvesting naval resource at: {targetLocation}")
				else:
					print(f"Moving toward naval resource at: {targetLocation}")

	def plotSentryMoves(self, simulation):
		"""Send units to sentry points around borders"""
		# Do we have any targets of this type?
		if len(self.targetedSentryPoints) > 0:
			# Prioritize them (LATER)

			# See how many moves of this type we can execute
			for (index, targetedSentryPoint) in enumerate(self.targetedSentryPoints):
				# AI_PERF_FORMAT("Homeland-perf.csv", ("PlotSentryMoves, Turn %03d, %s", GC.getGame().getElapsedGameTurns(), m_pPlayer->getCivilizationShortDescription()) );

				# CvPlot * pTarget = GC.getMap().plot(m_TargetedSentryPoints[iI].GetTargetX(), m_TargetedSentryPoints[iI].GetTargetY());
				targetTile = simulation.tileAt(targetedSentryPoint.target)

				self.findUnitsForMove(HomelandMoveType.sentry, firstTime=(index == 0), simulation=simulation)

				if (len(self.currentMoveHighPriorityUnits) + len(self.currentMoveUnits)) > 0:
					if self.bestUnitToReachTarget(targetTile, maxTurns=sys.maxsize, simulation=simulation):
						self.executeMoveToTarget(targetTile, garrisonIfPossible=False, simulation=simulation)

						if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
							print("Moving to sentry point, \(targetedSentryPoint.target ?? HexPoint.invalid), " +
								"Priority: \(targetedSentryPoint.threatValue)")
							# LogHomelandMessage(strLogString);

		return

	def plotMobileReserveMoves(self, simulation):
		pass  # fixme

	def plotGarrisonMoves(self, simulation):
		pass  # fixme

	def plotPatrolMoves(self, simulation):
		pass  # fixme

	def reviewUnassignedUnits(self, simulation):
		"""Log that we couldn't find assignments for some units"""
		# Loop through all remaining units
		for currentTurnUnit in self.currentTurnUnits:
			currentTurnUnit.pushMission(UnitMission(UnitMissionType.skip), simulation)
			currentTurnUnit.setTurnProcessedTo(True)

			print(f"<< HomelandAI ### Unassigned {currentTurnUnit.name()} at {currentTurnUnit.location} ### >>")

	def findAutomatedUnits(self, simulation):
		pass

