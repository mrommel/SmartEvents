import copy
import random
import sys
from typing import Optional

from game.ai.builderTasking import BuilderDirectiveType
from game.ai.militaryStrategies import ReconStateType
from game.cities import City
from game.flavors import FlavorType
from game.states.builds import BuildType
from game.tradeRoutes import TradeRoute
from game.unitTypes import UnitTaskType, UnitMapType, UnitMissionType
from game.units import Unit, UnitAutomationType, UnitMission
from map import constants
from map.base import HexPoint
from map.improvements import ImprovementType
from map.path_finding.finder import AStarPathfinder
from map.types import UnitDomainType, UnitMovementType, Yields
from core.base import ExtendedEnum, InvalidEnumError, contains


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
	# scientistFreeTech = ''  # AI_HOMELAND_MOVE_SCIENTIST_FREE_TECH,
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

	def __repr__(self):
		return f'HomelandMove(moveType={self.moveType}, priority={self.priority})'


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
		self.currentBestMoveHighPriorityUnit: Optional[Unit] = None
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
					if tile.owner() is None or tile.owner().leader == self.player.leader:
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
		"""Creates cities for AI civilizations on first turn"""
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
							print(f"Moving to goody hut (non-explorer), {targetTile.point}")
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
					if currentTurnUnit.domain() != UnitDomainType.sea or tile.isFriendlyTerritoryFor(self.player,
					                                                                                 simulation):

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
						# Barbarian combat units - only naval units flee (but they flee if they have taken ANY damage)
						if currentTurnUnit.domain() == UnitDomainType.sea:
							addUnit = True
					elif currentTurnUnit.isUnderEnemyRangedAttack() or \
						currentTurnUnit.attackStrengthAgainst(unit=None, city=None, tile=tile,
						                                      simulation=simulation) * 2 <= \
						currentTurnUnit.baseCombatStrength(ignoreEmbarked=False):
						# Everyone else flees at less than or equal to 50% combat strength
						addUnit = True
				elif not currentTurnUnit.isBarbarian():
					# Also flee if danger is really high in current plot (but not if we're barbarian)
					acceptableDanger = currentTurnUnit.attackStrengthAgainst(unit=None, city=None, tile=tile,
					                                                         simulation=simulation) * 100
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
			if currentTurnUnit.task() == UnitTaskType.work or (
				currentTurnUnit.isAutomated() and currentTurnUnit.domain() == UnitDomainType.land and currentTurnUnit.automateType() == UnitAutomationType.build):
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

				if not currentMoveUnit.canBuild(build, targetLocation, testVisible=True, testGold=True,
				                                simulation=simulation):
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
							target=targetLocation,
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
							print(
								f"Moving to sentry point, {targetedSentryPoint.target or constants.invalidHexPoint}), " +
								f"Priority: {targetedSentryPoint.threatValue}")
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
		"""Mark all the units that will be under tactical AI control this turn"""
		self.currentTurnUnits = []

		# Loop through our units
		for loopUnit in simulation.unitsOf(self.player):
			if loopUnit.isAutomated() and not loopUnit.processedInTurn() and loopUnit.task() != UnitTaskType.unknown \
				and loopUnit.canMove():
				self.currentTurnUnits.append(loopUnit)

	def executeWorkerMoves(self, simulation):
		"""Moves units to explore the map"""
		dangerPlotsAI = self.player.dangerPlotsAI

		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit

			if unit is not None:
				danger = dangerPlotsAI.dangerAt(unit.location)
				if danger > 0.0:
					if self.moveCivilianToSafety(unit, simulation):
						print(
							f"{self.player.leader} moves {unit.name()} in turn {simulation.currentTurn} to 1st Safety,")
						unit.finishMoves()
						self.unitProcessed(unit)
						continue

				actionPerformed = self.executeWorkerMove(unit, simulation)
				if actionPerformed:
					continue

				# if there's nothing else to do, move to the safest spot nearby
				if self.moveCivilianToSafety(unit, ignoreUnits=True, simulation=simulation):
					print(f"{self.player.leader} moves {unit.name()} in turn {simulation.currentTurn} to 2nd Safety,")

					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)

					if not self.player.isHuman():
						unit.finishMoves()

					self.unitProcessed(unit)
					continue

				# slewis - this was removed because a unit would eat all its moves.
				# So if it didn't do anything this turn, it wouldn't be able to work
				unit.pushMission(UnitMission(UnitMissionType.skip), simulation)

				if not self.player.isHuman():
					unit.finishMoves()

				self.unitProcessed(unit)
		return

	def executeWorkerMove(self, unit, simulation) -> bool:
		# evaluator
		directive = self.player.builderTaskingAI.evaluateBuilder(unit, simulation=simulation)

		if directive is not None:
			if directive.buildType == BuilderDirectiveType.buildImprovementOnResource or \
				directive.buildType == BuilderDirectiveType.buildImprovement or \
				directive.buildType == BuilderDirectiveType.repair or \
				directive.buildType == BuilderDirectiveType.buildRoute or \
				directive.buildType == BuilderDirectiveType.chop or \
				directive.buildType == BuilderDirectiveType.removeRoad:

				# are we already there?
				if directive.target == unit.location:
					# check to see if we already have this mission as the unit's head mission
					pushMission = True
					missionData: UnitMission = unit.peekMission()
					if missionData is not None:
						if missionData.missionType == UnitMissionType.build and missionData.buildType == directive.build:
							pushMission = False

					if pushMission:
						unitMission = UnitMission(UnitMissionType.build)
						unitMission.buildType = directive.build
						unit.pushMission(unitMission, simulation)

					if unit.readyToMove():
						unit.finishMoves()

					self.unitProcessed(unit)

				else:
					unit.pushMission(UnitMission(UnitMissionType.moveTo, directive.target), simulation)
					unit.finishMoves()
					self.unitProcessed(unit)

				return True
		else:
			print("builder has no directive")
			unit.doCancelOrder(simulation)

		return False

	def executeExplorerMoves(self, land: bool, simulation):
		"""Moves units to explore the map"""
		self.player.economicAI.updatePlots(simulation)
		foundNearbyExplorePlot = False

		pathfinderDataSource = simulation.ignoreUnitsPathfinderDataSource(
			UnitMovementType.walk if land else UnitMovementType.swimShallow,
			self.player,
			UnitMapType.combat,
			self.player.canEmbark(),
			canEnterOcean=self.player.canEnterOcean()
		)
		pathfinder = AStarPathfinder(pathfinderDataSource)

		for homelandUnit in self.currentMoveUnits:
			if homelandUnit.unit is None:
				continue

			unit = homelandUnit.unit
			if unit.processedInTurn():
				continue

			unitPlayer = unit.player
			if unitPlayer is None:
				continue

			goodyPlot = self.player.economicAI.unitTargetGoodyPlot(unit, simulation)
			if goodyPlot is not None:
				print(f"Unit {unit.name()} at {unit.location} has goody target at {goodyPlot.point}")

				if (goodyPlot.hasImprovement(ImprovementType.goodyHut) or
				    goodyPlot.hasImprovement(ImprovementType.barbarianCamp)) and \
					simulation.visibleEnemy(goodyPlot.point, self.player) is None:

					path = pathfinder.shortestPath(unit.location, goodyPlot.point)
					if path is not None:
						firstStep = path.firstSegmentFor(unit.moves())
						if firstStep is not None:
							stepPoint = firstStep.points()[-1]
							print(f"Unit {unit.name()} Moving to goody hut, from {unit.location}")

							unit.pushMission(UnitMission(UnitMissionType.moveTo, stepPoint), simulation)
							unit.finishMoves()
							self.unitProcessed(unit)
						else:
							print(f"Unit {unit.name()} no end turn plot to goody from {unit.location}")

						continue
					else:
						print(f"Unit {unit.name()} can't find path to goody from {unit.location}")

			bestPlot = None
			bestPlotScore = 0

			sightRange = unit.sight()
			movementRange = unit.movesLeft()  # / GC.getMOVE_DENOMINATOR();
			for evalPoint in unit.location.areaWithRadius(movementRange):
				evalPlot = simulation.tileAt(evalPoint)

				if evalPlot is None:
					continue

				if not self.isValidExplorerEndTurnPlot(unit, evalPlot, simulation):
					continue

				path = pathfinder.shortestPath(unit.location, evalPoint)

				if path is None:
					continue

				distance = len(path.points())
				if distance > 1:
					continue

				domain = unit.domain()
				score = self.player.economicAI.scoreExplore(evalPoint, self.player, sightRange, domain, simulation)
				if score > 0:
					if domain == UnitDomainType.land and evalPlot.hasHills():
						score += 50
					elif domain == UnitDomainType.sea and simulation.adjacentToLand(evalPoint):
						score += 200
					elif domain == UnitDomainType.land and unit.isEmbarkAllWater() and not evalPlot.isShallowWater():
						score += 200

				if score > bestPlotScore:
					bestPlot = evalPlot
					bestPlotScore = score
					foundNearbyExplorePlot = True

			if bestPlot is not None and movementRange > 0:
				explorationPlots = self.player.economicAI.explorationPlots()
				if len(explorationPlots) > 0:
					bestPlotScore = 0

					for explorationPlot in explorationPlots:
						evalPlot = simulation.tileAt(explorationPlot.location)
						if evalPlot is None:
							continue

						plotScore = 0

						if not self.isValidExplorerEndTurnPlot(unit, evalPlot, simulation):
							continue

						rating = explorationPlot.rating

						# hitting the pathfinder, may not be the best idea...
						path = pathfinder.shortestPath(unit.location, explorationPlot.location)
						if path is None:
							continue

						distance = path.cost() + random.uniform(0.0, 5.0)
						if distance == 0:
							plotScore = 1000 * rating
						else:
							plotScore = (1000 * rating) / int(distance)

						if plotScore > bestPlotScore:
							endTurnPoint = path.points()[-1]
							endTurnPlot = simulation.tileAt(endTurnPoint)

							if endTurnPoint == unit.location:
								bestPlot = None
								bestPlotScore = plotScore
							elif self.isValidExplorerEndTurnPlot(unit, endTurnPlot, simulation):
								bestPlot = endTurnPlot
								bestPlotScore = plotScore
							else:
								# not a valid destination
								continue

			if bestPlot is not None:
				unitMission = UnitMission(UnitMissionType.moveTo, buildType=None, target=bestPlot.point, options=[])
				unit.pushMission(unitMission, simulation)

				# Only mark as done if out of movement
				if unit.moves() <= 0:
					self.unitProcessed(unit)
			else:
				if unitPlayer.isHuman():
					unit.automate(UnitAutomationType.none, simulation)
					self.unitProcessed(unit)
				else:
					# If this is a land explorer and there is no ignore unit path to a friendly city, then disband him
					if unit.task() == UnitTaskType.explore:
						foundPath = False

						for city in simulation.citiesOf(self.player):
							if pathfinder.doesPathExist(unit.location, city.location):
								foundPath = True
								break

							if not foundPath:
								self.unitProcessed(unit)
								unit.doKill(delayed=False, otherPlayer=None, simulation=simulation)
								self.player.economicAI.incrementExplorersDisbanded()
					elif unit.task() == UnitTaskType.exploreSea:
						# NOOP
						pass

		return

	def executeTradeUnitMoves(self, simulation):
		"""Get a trade unit and send it to a city!"""
		goldFlavor: float = float(self.player.leader.flavor(FlavorType.gold))
		foodFlavor: float = float(self.player.leader.flavor(FlavorType.growth))
		scienceFlavor: float = float(self.player.leader.flavor(FlavorType.science))

		for currentMoveUnit in self.currentMoveUnits:
			unit = currentMoveUnit.unit

			originCity = simulation.cityAt(unit.origin)
			if originCity is not None:

				bestTradeRoute: Optional[TradeRoute] = None
				bestTradeRouteValue: float = -1.0

				possibleTradeRoutes: [TradeRoute] = self.player.possibleTradeRoutes(originCity, simulation)

				for possibleTradeRoute in possibleTradeRoutes:
					# skip, if already has trade route between these cities
					if self.player.hasTradeRoute(originCity.location, possibleTradeRoute.end()):
						continue

					tradeRouteYields: Yields = possibleTradeRoute.yields(simulation)
					value: float = 0.0
					value += tradeRouteYields.gold * goldFlavor
					value += tradeRouteYields.food * foodFlavor
					value += tradeRouteYields.science * scienceFlavor

					if value > bestTradeRouteValue:
						bestTradeRoute = possibleTradeRoute
						bestTradeRouteValue = value

				if bestTradeRoute is not None:
					targetCity = simulation.cityAt(bestTradeRoute.end())

					unit.doEstablishTradeRouteTo(targetCity, simulation)
					self.unitProcessed(unit)
					# unit.finishMoves()
					if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
						print(f"Trade unit founded trade route between {originCity.name} and {targetCity.name}")
				else:
					if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
						print("Trade unit idling")

					self.unitProcessed(unit)

					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
					unit.finishMoves()
			else:
				# try to relocate trader to random city
				randomCity = random.choice(simulation.citiesOf(self.player))
				if randomCity is not None:
					unit.doRebaseTo(randomCity.location)

					if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
						print(f"Trade unit rebased to {randomCity.name}")
				else:
					if simulation.loggingEnabled() and simulation.aiLoggingEnabled():
						print("Trade unit idling")

					self.unitProcessed(unit)

					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
					unit.finishMoves()

		return

	def findUnitsForMove(self, moveType: HomelandMoveType, firstTime: bool, simulation) -> bool:
		"""Finds both high and normal priority units we can use for this homeland move
		(returns true if at least 1 unit found)"""
		rtnValue: bool = False

		if firstTime:
			self.currentMoveUnits = []
			self.currentMoveHighPriorityUnits = []

			# Loop through all units available to homeland AI this turn
			for loopUnit in self.currentTurnUnits:
				loopUnitPlayer = loopUnit.player
				economicAI = self.player.economicAI

				if not loopUnitPlayer.isHuman():
					# Civilians aren't useful for any of these moves
					if not loopUnit.isCombatUnit():
						continue

					# Scouts aren't useful unless recon is entirely shut off
					if loopUnit.task() == UnitTaskType.explore and economicAI.reconState() != ReconStateType.enough:
						continue

					suitableUnit = False
					highPriority = False

					if moveType == HomelandMoveType.garrison:
						# Want to put ranged units in cities to give them a ranged attack
						if loopUnit.isRanged() and not loopUnit.hasTask(UnitTaskType.cityBombard):
							suitableUnit = True
							highPriority = True

						elif loopUnit.canAttack():  # Don't use non-combatants
							# Don't put units with a combat strength boosted from promotions in cities, these boosts are ignored
							if loopUnit.defenseModifierAgainst(unit=None, city=None, tile=None, ranged=False,
							                                   simulation=simulation) == 0 \
								and loopUnit.attackModifierAgainst(unit=None, city=None, tile=None,
								                                   simulation=simulation) == 0:
								suitableUnit = True

					elif moveType == HomelandMoveType.sentry:
						# No ranged units as sentries
						if not loopUnit.isRanged():  # and !loopUnit->noDefensiveBonus()
							suitableUnit = True

							# Units with extra sight are especially valuable
							if loopUnit.sight() > 2:
								highPriority = True

						elif loopUnit.sight() > 2:  # and loopUnit->noDefensiveBonus()
							suitableUnit = True
							highPriority = True

					elif moveType == HomelandMoveType.mobileReserve:
						# Ranged units are excellent in the mobile reserve as are fast movers
						if loopUnit.isRanged() or loopUnit.hasTask(UnitTaskType.fastAttack):
							suitableUnit = True
							highPriority = True
						elif loopUnit.canAttack():
							suitableUnit = True

					elif moveType == HomelandMoveType.ancientRuins:
						# Fast movers are top priority
						if loopUnit.hasTask(UnitTaskType.fastAttack):
							suitableUnit = True
							highPriority = True
						elif loopUnit.canAttack():
							suitableUnit = True

					else:
						# NOOP
						pass

					# If unit was suitable, add it to the proper list
					if suitableUnit:
						unit = HomelandUnit(loopUnit)
						if highPriority:
							self.currentMoveHighPriorityUnits.append(unit)
						else:
							self.currentMoveUnits.append(unit)
						rtnValue = True

		else:  # not first time
			# Normal priority units
			tempList = copy.deepcopy(self.currentMoveUnits)
			self.currentMoveUnits = []

			for it in tempList:
				if contains(lambda u: u.location == it.unit.location, self.currentTurnUnits):
					self.currentMoveUnits.append(it)
					rtnValue = True

			# High priority units
			tempList = copy.deepcopy(self.currentMoveHighPriorityUnits)
			self.currentMoveHighPriorityUnits = []

			for it in tempList:
				if contains(lambda u: u.location == it.unit.location, self.currentTurnUnits):
					self.currentMoveHighPriorityUnits.append(it)
					rtnValue = True

		return rtnValue

	def isValidExplorerEndTurnPlot(self, unit, plot, simulation):
		if unit.location == plot.point:
			return False

		if not plot.isDiscoveredBy(unit.player):
			return False

		# domain = unit.domain()
		# if plot.sameContinent( as: <  # T##AbstractTile#>) (pPlot->area() != pUnit->area())
		# 	if (!pUnit->CanEverEmbark())
		# 		if (!(eDomain == DOMAIN_SEA & & pPlot->isWater()))
		# 			return false;

		# don't let the auto-explore end it's turn in a city
		if plot.isCity():
			return False

		if not unit.canMoveInto(plot.point, options=[], simulation=simulation):
			return False

		return True

	def moveCivilianToSafety(self, unit, ignoreUnits: bool, simulation) -> bool:
		"""Fleeing to safety for civilian units"""
		dangerPlotsAI = self.player.dangerPlotsAI
		searchRange = unit.searchRange(1, simulation)

		bestValue = -999999
		bestPlot = None

		for point in unit.location.areaWithRadius(searchRange):
			tile = simulation.tileAt(point)

			if tile is None:
				continue

			if not unit.validTarget(point, simulation):
				continue

			if simulation.isEnemyVisibleAt(point, self.player):
				continue

			# if we can't get there this turn, skip it
			turns = unit.turnsToReach(point, simulation)
			if turns == sys.maxsize or turns > 1:
				continue

			value = 0
			if tile.owner() is not None and tile.owner().leader == self.player.leader:
				# if this is within our territory, provide a minor benefit
				value += 1

			city = simulation.cityAt(point)

			if city is not None and city.player.leader == self.player.leader:
				value += city.defensiveStrengthAgainst(unit=None, tile=tile, ranged=False, simulation=simulation)

			elif not ignoreUnits:
				otherUnit = simulation.unitAt(point, UnitMapType.combat)
				if otherUnit is not None:
					if otherUnit.player.leader == unit.player.leader:
						if otherUnit.canDefend() and otherUnit.location != unit.location:
							if otherUnit.isWaiting() or not otherUnit.canMove():
								value += otherUnit.defensiveStrengthAgainst(unit=None, city=None, tile=tile, ranged=False, simulation=simulation)

			value -= int(dangerPlotsAI.dangerAt(point))

			if value > bestValue:
				bestValue = value
				bestPlot = tile

		if bestPlot is not None:
			if unit.location == bestPlot.point:
				# print("\(unit.name()) tried to move to safety, but is already at the best spot, \(bestPlot.point)")
				if unit.canHoldAt(bestPlot.point, simulation):
					print(f"{unit.name()} tried to move to safety, but is already at the best spot, {bestPlot.point}")
					unit.pushMission(UnitMission(UnitMissionType.skip), simulation)
					return True
				else:
					print(f"{unit.name()} tried to move to safety, but cannot hold in current location, {bestPlot.point}")
					unit.automate(UnitAutomationType.none, simulation)
			else:
				print(f"{unit.name()} moving to safety, {bestPlot.point}")
				unit.pushMission(UnitMission(UnitMissionType.moveTo, target=bestPlot.point), simulation)
				return True
		else:
			print(f"{unit.name()} tried to move to a safe point but couldn't find a good place to go")

		return False
