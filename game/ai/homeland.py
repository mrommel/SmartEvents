import sys
from typing import Optional

from game.cities import City
from game.flavors import FlavorType
from game.unitTypes import UnitTaskType
from game.units import Unit
from map.base import HexPoint
from map.improvements import ImprovementType
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

		self.currentBestMoveUnit: Optional[Unit]
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
		flavorDefense = int(float(self.player.valueOfPersonalityFlavor(FlavorType.defense)) * HomelandAI.flavorDampening)
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
				if homelandMoveType in [HomelandMoveType.garrison, HomelandMoveType.heal, HomelandMoveType.toSafety,
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
		self.targetedCities.removeAll()
		self.targetedSentryPoints.removeAll()
		self.targetedForts.removeAll()
		self.targetedNavalResources.removeAll()
		self.targetedHomelandRoads.removeAll()
		self.targetedAncientRuins.removeAll()

		# Look at every tile on map
		# CvMap & theMap = GC.getMap();
		mapSize = simulation.mapSize()
		for x in 0.. < mapSize.width() {
		for y in 0..< mapSize.height() {

		let point = HexPoint(x, y)
		guard
		let
		tile = simulation.tileAt(point) else {
		continue
		}

		if tile.isVisible(to: player) {

		# Have a...
		# ... friendly city?
		if let city = simulation.cityAt(point) {

		if city.player?.leader == player.leader
		{

		# Don't send another unit, if the tactical AI already sent a garrison here
		addTarget = False
		if let
		unit = simulation.unitAt(point, .combat) {

		if unit.isUnderTacticalControl()
		{
			addTarget = true
		}
		} else {
			addTarget = true
		}

		if addTarget {

		let newTarget = HomelandTarget(targetType: .city)
		newTarget.target = point
		newTarget.city = city
		newTarget.threatValue = city.threatValue()
		self.targetedCities.append(newTarget)
		}
		}
		} elif tile.terrain().isWater() and tile.has(improvement: .
			none) {
			      # ... naval resource?
		if tile.hasAnyResource(for: player) {

		if let
		workingCity = tile.workingCity(), workingCity.player?.leader == player.leader
		{

		# Find proper improvement
		if let
		improvement = tile.possibleImprovements().first
		{

			let
		newTarget = HomelandTarget(targetType:.navalResource)
		newTarget.target = point
		newTarget.improvement = improvement
		self.targetedNavalResources.append(newTarget)
		}
		}
		}
		} elif tile.hasImprovement(ImprovementType.goodyHut) {

			          # ... unpopped goody hut?
		newTarget = HomelandTarget(targetType:.ancientRuin)
		newTarget.target = point
		self.targetedAncientRuins.append(newTarget)

		} elif let targetUnit = simulation.unitAt(point, of:.civilian) {

		# ... enemy civilian( or embarked) unit?
		if diplomacyAI.isAtWar(with: targetUnit.player) and not targetUnit.canDefend()
		{

			newTarget = HomelandTarget(targetType:.ancientRuin)
		newTarget.target = point
		self.targetedAncientRuins.append(newTarget)
		}
		} else if tile.terrain().isLand() and gameModel.unitAt(point, .combat) is None
		{

		# ... possible sentry point? (must be empty or only have friendly units)

		       # Must be at least adjacent to our land
		if tile.owner().leader == player.leader or tile.owner() is None:
			# FIXME

		}
		} else if tile.owner().leader == player.leader and tile.hasAnyRoute():

		# ...road segment in friendly territory?

		let newTarget = HomelandTarget(targetType: .homeRoad)
		newTarget.target = point
		self.targetedHomelandRoads.append(newTarget)
		}
		}
		}
		}

		# Post - processing on targets
		# FIXME self.eliminateAdjacentSentryPoints();
		# FIXME self.eliminateAdjacentHomelandRoads();
		self.targetedCities.sort()
