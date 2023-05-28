import math
from typing import Optional

from game.ai.homeland import HomelandAI
from game.baseTypes import GameState
from game.ai.economics import EconomicAI
from game.ai.grandStrategies import GrandStrategyAI
from game.ai.militaries import MilitaryAI
from game.buildings import BuildingType
from game.cities import City, CityStateType, YieldValues
from game.cityConnections import CityConnections
from game.civilizations import LeaderType, CivilizationType, CivilizationAbility
from game.flavors import Flavors, FlavorType
from game.governments import PlayerGovernment
from game.greatPersons import GreatPersonType
from game.moments import MomentType
from game.notifications import Notifications, NotificationType, Notification
from game.playerMechanics import PlayerTechs, PlayerCivics, BuilderTaskingAI, TacticalAI, DiplomacyAI, \
	DiplomacyRequests, PlayerMoments
from game.policyCards import PolicyCardType
from game.religions import PantheonType
from game.states.ages import AgeType
from game.states.dedications import DedicationType
from game.states.gossips import GossipType
from game.states.ui import ScreenType
from game.tradeRoutes import TradeRoutes
from game.types import EraType, TechType, CivicType
from game.unitTypes import UnitMissionType, UnitTaskType, UnitMapType
from game.wonders import WonderType
from map.base import HexPoint
from map.types import Tutorials, Yields, TerrainType, FeatureType, UnitMovementType


class Player:
	pass


class DiplomaticAI:
	def __init__(self, player):
		self.player = player

	def update(self, simulation):
		pass

	def hasMetWith(self, player):
		return False


class TradeRoute:
	pass


class PlayerTradeRoutes:
	def __init__(self, player):
		self.player = player

	def tradeRoutesStartingAt(self, city) -> [TradeRoute]:
		return []

	def yields(self, simulation) -> Yields:
		return Yields(0, 0, 0)


class PlayerGreatPeople:
	def __init__(self, player):
		self.player = player

	def hasRetired(self, greatPerson: GreatPersonType) -> bool:
		return False


class PlayerTreasury:
	def __init__(self, player):
		self.player = player

		# internal
		self._gold = 0.0
		self._goldChangeForTurn = []

	def value(self) -> float:
		return self._gold

	def changeGoldBy(self, amount: float):
		self._gold += amount

	def doTurn(self, simulation):
		goldChange = self.calculateGrossGold(simulation)

		self._goldChangeForTurn.append(goldChange)

		# predict treasury
		goldAfterThisTurn = self._gold + goldChange

		# check if we are running low
		if goldAfterThisTurn < 0:
			self._gold = 0

			if goldAfterThisTurn <= -5: # DEFICIT_UNIT_DISBANDING_THRESHOLD
				# player.doDeficit()
				pass
		else:
			self.changeGoldBy(goldChange)

	def averageIncome(self, numberOfTurns: int) -> float:
		"""Average change in gold balance over N turns"""
		if numberOfTurns <= 0:
			raise Exception(f'Number of turn to check must be positive and not {numberOfTurns}')

		if len(self._goldChangeForTurn) == 0:
			return 0.0

		numberOfElements = min(numberOfTurns, len(self._goldChangeForTurn))
		total = sum(self._goldChangeForTurn[-numberOfElements:])

		return float(total) / float(numberOfElements)

	def calculateGrossGold(self, simulation):
		netGold = 0.0

		# Income
		# //////////////////

		# Gold from Cities
		netGold += self.goldFromCities(simulation)

		# Gold per Turn from Diplomacy
		netGold += self.goldPerTurnFromDiplomacy(simulation)

		# City connection bonuses
		netGold += self.goldFromTradeRoutes(simulation)

		# Costs
		# //////////////////

		# Gold for Unit Maintenance
		netGold -= self.goldForUnitMaintenance(simulation)

		# Gold for Building Maintenance
		netGold -= self.goldForBuildingMaintenance(simulation)

		# Gold per Turn for Diplomacy
		netGold += self.goldPerTurnForDiplomacy(simulation)

		return netGold

	def goldFromCities(self, simulation) -> float:
		"""Gold from Cities"""
		goldValue = 0.0

		for city in simulation.citiesOf(self.player):
			goldValue += city.goldPerTurn(simulation)

		return goldValue

	def goldPerTurnFromDiplomacy(self, simulation) -> float:
		return 0.0

	def goldFromTradeRoutes(self, simulation) -> float:
		return self.player.tradeRoutes.yields(simulation).gold

	def goldForUnitMaintenance(self, simulation) -> float:
		maintenanceCost = 0.0

		for unit in simulation.unitsOf(self.player):
			unitMaintenanceCost: float = float(unit.unitType.maintenanceCost())

			# conscription - Unit maintenance reduced by 1 Gold per turn, per unit.
			if self.player.government.hasCard(PolicyCardType.conscription):
				unitMaintenanceCost = max(0.0, unitMaintenanceCost - 1.0)

			# leveeEnMasse - Unit maintenance cost reduced by 2 Gold per unit.
			if self.player.government.hasCard(PolicyCardType.leveeEnMasse):
				unitMaintenanceCost = max(0.0, unitMaintenanceCost - 2.0)

			# eliteForces - +100 % combat experience for all units.
			# BUT: +2 Gold to maintain each military unit.
			if unit.unitType.maintenanceCost() > 0 and self.player.government.hasCard(PolicyCardType.eliteForces):
				unitMaintenanceCost += 2.0

			maintenanceCost += unitMaintenanceCost

		return maintenanceCost

	def goldForBuildingMaintenance(self, simulation) -> float:
		maintenanceCost = 0.0

		for city in simulation.citiesOf(self.player):
			maintenanceCost += city.maintenanceCostsPerTurn()

		return maintenanceCost

	def goldPerTurnForDiplomacy(self, simulation) -> float:
		return 0.0


class PlayerReligion:
	def __init__(self, player):
		self.player = player

	def pantheon(self) -> PantheonType:
		return PantheonType.none


class PlayerTourism:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass


class PlayerGovernors:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass


class CitySpecializationAI:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass

	def setSpecializationsDirty(self):
		pass


class DangerPlotsAI:
	def __init__(self, player):
		self.player = player

	def dangerAt(self, location: HexPoint) -> float:
		return 0.0


class Player:
	def __init__(self, leader: LeaderType, cityState: Optional[CityStateType]=None, human: bool=False):
		self.leader = leader
		self.cityState = cityState
		self.human = human

		# ais
		self.grandStrategyAI = GrandStrategyAI(player=self)
		self.economicAI = EconomicAI(player=self)
		self.militaryAI = MilitaryAI(player=self)
		self.tacticalAI = TacticalAI(player=self)
		self.diplomacyAI = DiplomacyAI(player=self)
		self.homelandAI = HomelandAI(player=self)
		self.builderTaskingAI = BuilderTaskingAI(player=self)
		self.citySpecializationAI = CitySpecializationAI(player=self)
		self.dangerPlotsAI = DangerPlotsAI(player=self)

		self.notifications = Notifications(self)
		self.diplomacyRequests = DiplomacyRequests(player=self)

		# special
		self.techs = PlayerTechs(self)
		self.civics = PlayerCivics(self)
		self.moments = PlayerMoments(self)

		self.personalityFlavors = Flavors()
		# state values
		self.isAliveVal = True
		self.turnActive = False
		self.finishTurnButtonPressedValue = False
		self.processedAutoMovesValue = False
		self.autoMovesValue = False
		self.endTurnValue = False
		self.lastSliceMovedValue = 0
		# cities stats values
		self.citiesFoundValue = 0
		self.citiesLostValue = 0
		self.builtCityNames = []
		self.originalCapitalLocationValue = HexPoint(-1, -1)
		self.lostCapitalValue = False
		self.conquerorValue = None

		self.government = PlayerGovernment(player=self)
		self.religion = PlayerReligion(player=self)
		self.tradeRoutes = PlayerTradeRoutes(player=self)
		self.cityConnections = CityConnections(player=self)
		self.greatPeople = PlayerGreatPeople(player=self)
		self.treasury = PlayerTreasury(player=self)
		self.tourism = PlayerTourism(player=self)
		self.governors = PlayerGovernors(player=self)

		self.currentEraVal: EraType = EraType.ancient
		self.currentAgeVal: AgeType = AgeType.normal
		self.currentDedicationsVal: [DedicationType] = []
		self.numberOfDarkAgesVal: int = 0
		self.numberOfGoldenAgesVal: int = 0
		self._citiesFoundValue: int = 0

	def initialize(self):
		pass

	def doTurn(self, simulation):
		self.doEurekas(simulation)
		self.doResourceStockpile(simulation)
		self.doSpaceRace(simulation)
		self.tourism.doTurn(simulation)

		# inform ui about new notifications
		self.notifications.update(simulation)

		hasActiveDiploRequest = False
		if self.isAlive():
			if not self.isBarbarian() and not self.isFreeCity() and not self.isCityState():

				# self.doUnitDiversity()
				self.doUpdateCramped(simulation)
				# DoUpdateUprisings();
				# DoUpdateCityRevolts();
				# CalculateNetHappiness();
				# SetBestWonderCities();
				self.doUpdateTradeRouteCapacity(simulation)

				self.grandStrategyAI.doTurn(simulation)

				# Do diplomacy for toward everyone
				self.diplomacyAI.doTurn(simulation)
				self.governors.doTurn(simulation)

				if self.isHuman():
					hasActiveDiploRequest = self.hasActiveDiploRequestWithHuman()

			if self.isCityState():
				self.doQuests(simulation)

		if (hasActiveDiploRequest or simulation.userInterface.isShown(ScreenType.diplomatic)) and not self.isHuman():
			simulation.setWaitingForBlockingInputOf(self)
		else:
			self.doTurnPostDiplomacy(simulation)

	def doTurnPostDiplomacy(self, simulation):
		if self.isAlive():
			if not self.isBarbarian() and not self.isFreeCity():
				self.economicAI.doTurn(simulation)
				self.militaryAI.doTurn(simulation)
				self.citySpecializationAI.doTurn(simulation)

		# Golden Age
		self.doProcessAge(simulation)

		self.doUpdateWarWeariness(simulation)

		# balance amenities
		self.doCityAmenities(simulation)

		# Do turn for all Cities
		for city in simulation.citiesOf(self):
			city.doTurn(simulation)

		# Gold GetTreasury()->DoGold();
		self.treasury.doTurn(simulation)

		# Culture / Civics
		self.doCivics(simulation)

		# Science / Techs
		self.doTechs(simulation)  # doResearch

		# government
		self.doGovernment(simulation)

		# faith / religion
		self.doFaith(simulation)

		# great people
		self.doGreatPeople(simulation)

		self.doTurnPost()

		return

	def isFreeCity(self) -> bool:
		return False

	def doTurnUnits(self, simulation):
		pass

	def name(self) -> str:
		return self.leader.name

	def isEqualTo(self, otherPlayer) -> bool:
		if otherPlayer is None:
			return False

		return self.leader == otherPlayer.leader

	def foundCity(self, location: HexPoint, name: str, simulation):
		tile = simulation.tileAt(location)

		cityName = name if name is not None else self.newCityName(simulation)

		# moments
		# ...

		isCapital = len(simulation.citiesOf(self)) == 0
		city = City(cityName, location, isCapital, self)
		city.initialize(simulation)

		simulation.addCity(city)

		if self.isHuman():
			# Human player is prompted to choose production BEFORE the AI runs for the turn.
			# So we'll force the AI strategies on the city now, just after it is founded.
			# And if the very first turn, we haven't even run player strategies once yet, so do that too.
			if simulation.currentTurn == 0:
				self.economicAI.doTurn(simulation)
				self.militaryAI.doTurn(simulation)

				city.cityStrategyAI.doTurn(simulation)

				if self.isActive():
					self.notifications.add(Notification(NotificationType.productionNeeded, city=city))

				city.doFoundMessage()

				# If this is the first city (or we still aren't getting tech for some other reason) notify the player
				if self.techs.needToChooseTech() and self.science(simulation) > 0.0:
					self.notifications.add(Notification(NotificationType.techNeeded))

				# If this is the first city (or ..) notify the player
				if self.civics.needToChooseCivic() and self.culture(simulation, consume=False) > 0.0:
					self.notifications.add(Notification(NotificationType.civicNeeded))

				if isCapital:
					self.notifications.add(Notification(NotificationType.policyNeeded))
			else:
				city.doFoundMessage()

				# AI civ, may need to redo city specializations
				self.citySpecializationAI.setSpecializationsDirty()

		# roman roads
		# if self.leader.civilization().ability() == .allRoadsLeadToRome {
		#
		#             if !isCapital {
		#                 guard let capital = gameModel.capital(of: self) else {
		#                     fatalError("cant get capital")
		#                 }
		#
		#                 let pathFinderDataSource = gameModel.ignoreUnitsPathfinderDataSource(
		#                     for: .walk,
		#                     for: self,
		#                     unitMapType: .combat,
		#                     canEmbark: false,
		#                     canEnterOcean: self.canEnterOcean()
		#                 )
		#                 let pathFinder = AStarPathfinder(with: pathFinderDataSource)
		#
		#                 if let path = pathFinder.shortestPath(fromTileCoord: location, toTileCoord: capital.location) {
		#                     // If within TradeRoute6 Trade Route range of the Capital6 Capital, a road to it.
		#                     if path.count <= TradeRoutes.landRange {
		#
		#                         for pathLocation in path {
		#
		#                             if let pathTile = gameModel.tile(at: pathLocation) {
		#                                 pathTile.set(route: self.bestRoute())

		# send gossip
		simulation.sendGossip(GossipType.cityFounded, cityName=cityName, player=self)

		self.citiesFoundValue += 1

		if simulation.tutorial() == Tutorials.foundFirstCity and self.isHuman():
			if self.citiesFoundValue >= Tutorials.citiesToFound():
				simulation.userInterface.finishTutorial(Tutorials.foundFirstCity)
				simulation.enableTutorial(Tutorials.none)

	def isAtWar(self) -> bool:
		return False

	def valueOfStrategyAndPersonalityFlavor(self, flavorType: FlavorType) -> int:
		activeStrategy = self.grandStrategyAI.activeStrategy

		if activeStrategy is None:
			return self.personalityFlavors.value(flavorType)

		return self.personalityFlavors.value(flavorType) + activeStrategy.flavor(flavorType)

	def valueOfPersonalityFlavor(self, flavor: FlavorType) -> int:
		return self.leader.flavor(flavor)

	def valueOfPersonalityIndividualFlavor(self, flavorType: FlavorType) -> int:
		return self.personalityFlavors.value(flavorType)

	def isHuman(self) -> bool:
		return self.human

	def isBarbarian(self) -> bool:
		return self.leader == LeaderType.barbar

	def hasMetWith(self, otherPlayer: Player) -> bool:
		if self.isBarbarian() or otherPlayer.isBarbarian():
			return False

		return self.diplomacyAI.hasMetWith(otherPlayer)

	def canFinishTurn(self) -> bool:
		if not self.isHuman():
			return False

		if not self.isAlive():
			return False

		if not self.isActive():
			return False

		if not self.hasProcessedAutoMoves():
			return False

		if self.blockingNotification() is not None:
			return False

		return True

	def turnFinished(self) -> bool:
		return self.finishTurnButtonPressedValue

	def finishTurn(self):
		self.finishTurnButtonPressedValue = True

	def resetFinishTurnButtonPressed(self):
		self.finishTurnButtonPressedValue = False

	def lastSliceMoved(self) -> int:
		return self.lastSliceMovedValue

	def setLastSliceMoved(self, value: int):
		self.lastSliceMovedValue = value

	def isTurnActive(self) -> bool:
		return self.turnActive

	def __eq__(self, other):
		return self.leader == other.leader

	def __str__(self):
		return f'Player {self.leader}'

	def isActive(self) -> bool:
		return self.turnActive

	def numberOfCitiesFounded(self) -> int:
		return self.citiesFoundValue

	def science(self, simulation) -> float:
		value: YieldValues = YieldValues(value=0.0, percentage=1.0)

		# Science from our Cities
		value += self.scienceFromCities(simulation)
		value += self.scienceFromCityStates(simulation)

		return max(value.calc(), 0)

	def scienceFromCities(self, simulation) -> YieldValues:
		scienceVal: YieldValues = YieldValues(value=0.0, percentage=0.0)

		for city in simulation.citiesOf(player=self):
			scienceVal += city.sciencePerTurn(simulation)

		return scienceVal

	def scienceFromCityStates(self, simulation) -> YieldValues:
		scienceVal = 0.0
		scienceModifier = 0.0

		# internationalSpaceAgency - 5% Science per City-State you are the Suzerain of.
		if self.government.hasCard(PolicyCardType.internationalSpaceAgency):
			numberOfCityStatesMet: int = 0
			for cityState in self.metCityStates(simulation):
				if self.isSuzerainOf(cityState, simulation):
					numberOfCityStatesMet += 1

			scienceModifier += 0.05 * float(numberOfCityStatesMet)

		return YieldValues(value=scienceVal, percentage=scienceModifier)

	def culture(self, simulation, consume: bool) -> float:
		pass

	def isAlive(self) -> bool:
		return self.isAliveVal

	def prepareTurn(self, simulation):
		# Barbarians get all Techs that 3 / 4 of alive players get
		if self.isBarbarian():
			# self.doBarbarianTech()
			pass

		# / * for (iI = 0; iI < GC.getNumTechInfos();
		# iI + +)  {
		#     GetTeamTechs()->SetNoTradeTech(((TechTypes)iI), false);
		# }
		#
		# DoTestWarmongerReminder();
		#
		# DoTestSmallAwards(); * /
		self.checkWorldCircumnavigated(simulation)

	def startTurn(self, simulation):
		if self.isTurnActive():
			print("try to start already active turn")
			return

		if self.isHuman():
			print(f'--- start turn for HUMAN player {self.leader} ---')
		elif self.isBarbarian():
			print("--- start turn for barbarian player ---")
		elif self.leader == LeaderType.cityState:
			print(f'--- start turn for city state {self.cityState.name()} ---')
		elif self.isMajorAI():
			print(f'--- start turn for AI player {self.leader} ---')

		simulation.userInterface.updatePlayer(self)

		self.turnActive = True
		self.setEndTurnTo(False, simulation)
		self.setAutoMovesTo(False)

		# ##################################################################
		# TURN IS BEGINNING
		# ##################################################################

		# self.doUnitAttrition()
		self.verifyAlive(simulation)

		self.setAllUnitsUnprocessed(simulation)

		simulation.updateTacticalAnalysisMap(self)

		self.updateTimers(simulation)

		# This block all has things which might change based on city connections changing
		self.cityConnections.doTurn(simulation)
		self.builderTaskingAI.update(simulation)

		if simulation.currentTurn > 0:
			if self.isAlive():
				self.doTurn(simulation)
				self.doTurnUnits(simulation)

		if simulation.currentTurn == 1 and simulation.showTutorialInfos():
			if self.isHuman():
				# simulation.userInterface.showPopup(popupType: .tutorialStart(tutorial: gameModel.tutorialInfos()))
				pass

	def endTurn(self, simulation):
		if not self.isTurnActive():
			raise Exception("try to end an inactive turn")

		# print("--- unit animation running: \(gameModel?.userInterface?.animationsAreRunning(for: self.leader)) ---")
		playerType = 'HUMAN' if self.isHuman() else 'AI'
		print(f'--- end turn for {playerType} player {self.leader} ---')

		self.turnActive = False

		# /////////////////////////////////////////////
		# // TURN IS ENDING
		# /////////////////////////////////////////////

		self.doUnitReset(simulation)
		self.setCanChangeGovernmentTo(False)

		self.notifications.cleanUp(simulation)

		self.diplomacyRequests.endTurn()

	def hasProcessedAutoMoves(self) -> bool:
		return self.processedAutoMovesValue

	def setProcessedAutoMovesTo(self, value: bool):
		self.processedAutoMovesValue = value

	def doUnitReset(self, simulation):
		"""Units heal and then get their movement back"""
		for loopUnit in simulation.unitsOf(self):
			# HEAL UNIT?
			if not loopUnit.isEmbarked():
				if not loopUnit.hasMoved(simulation):
					if loopUnit.isHurt():
						loopUnit.doHeal(simulation)

			# Finally(now that healing is done), restore movement points
			loopUnit.resetMoves(simulation)
			# pLoopUnit->SetIgnoreDangerWakeup(false);
			loopUnit.setMadeAttackTo(False)
			# pLoopUnit->setMadeInterception(false);

			if not self.isHuman():
				mission = loopUnit.peekMission()
				if mission is not None:
					if mission.type == UnitMissionType.rangedAttack:
						# CvAssertMsg(0, "An AI unit has a combat mission queued at the end of its turn.");
						loopUnit.clearMissions() # Clear the whole thing, the AI will re-evaluate next turn.

	def setCanChangeGovernmentTo(self, param):
		pass

	def checkWorldCircumnavigated(self, game):
		pass

	def updatePlots(self, simulation):
		pass

	def setCapitalCity(self, city, simulation):
		pass

	def currentAge(self) -> AgeType:
		return self.currentAgeVal

	def hasDedication(self, dedication: DedicationType) -> bool:
		return dedication in self.currentDedicationsVal

	def hasWonder(self, wonder: WonderType, simulation) -> bool:
		return False

	def isSuzerainOf(self, cityState: CityStateType, simulation) -> bool:
		return False

	def isMajorAI(self) -> bool:
		# return not self.isHuman() and not self.isFreeCity() and not self.isBarbarian() and not self.isCityState()
		return not self.isHuman() and not self.isBarbarian() and not self.isCityState()

	def isCityState(self) -> bool:
		return self.leader == LeaderType.cityState

	def setEndTurnTo(self, value: bool, simulation):
		if not self.isEndTurn() and self.isHuman() and simulation.activePlayer().leader != self.leader:
			if self.hasBusyUnitOrCity() or self.hasReadyUnit(simulation):
				return
		elif not self.isHuman():
			if self.hasBusyUnitOrCity():
				return

		if self.isEndTurn() != value:
			if not self.isTurnActive():
				raise Exception("isTurnActive is expected to be true")

			self.endTurnValue = value

			if self.isEndTurn():
				self.setAutoMovesTo(True)
			else:
				self.setAutoMovesTo(False)
		else:
			# This check is here for the AI.
			# Currently, the setEndTurn(true) never seems to get called for AI players, the auto moves are just
			# set directly
			# Why is this?  It would be great if all players were processed the same.
			if not value and self.isAutoMoves():
				self.setAutoMovesTo(False)

	def isEndTurn(self) -> bool:
		return self.endTurnValue

	def hasBusyUnitOrCity(self) -> bool:
		# @fixme
		return False

	def isAutoMoves(self) -> bool:
		return self.autoMovesValue

	def setAutoMovesTo(self, value: bool):
		if self.autoMovesValue != value:
			self.autoMovesValue = value
			self.processedAutoMovesValue = False

	def hasReadyUnit(self, simulation) -> bool:
		activePlayer = simulation.activePlayer()

		for loopUnit in simulation.unitsOf(activePlayer):
			if loopUnit.readyToMove() and not loopUnit.isDelayedDeath():
				return True

		return False

	def countReadyUnits(self, simulation) -> int:
		rtnValue = 0
		activePlayer = simulation.activePlayer()

		for loopUnit in simulation.unitsOf(activePlayer):
			if loopUnit.readyToMove() and not loopUnit.isDelayedDeath():
				rtnValue += 1

		return rtnValue

	def hasUnitsThatNeedAIUpdate(self, simulation) -> bool:
		for loopUnit in simulation.unitsOf(self):
			if not loopUnit.processedInTurn() and (loopUnit.isAutomated() and loopUnit.task() != UnitTaskType.none and loopUnit.canMove()):
				return True

		return False

	def unitUpdate(self, simulation):
		# CvPlayerAI::AI_unitUpdate()
		# Now it's the homeland AI's turn.
		if self.isHuman():
			self.homelandAI.doTurn(simulation)
		else:
			# Now let the tactical AI run.  Putting it after the operations update allows units who have
			# just been handed off to the tactical AI to get a move in the same turn they switch between
			self.tacticalAI.doTurn(simulation)
			self.homelandAI.doTurn(simulation)

	def verifyAlive(self, simulation):
		if self.isAlive():
			if not self.isBarbarian(): # and not self.isFreeCity():
				if self.numberOfCities(simulation) == 0 and self.numberOfUnits(simulation) == 0:
					self.setAliveTo(False, simulation)
		else:
			# if dead but has received units / cities - revive
			if self.numberOfUnits(simulation) > 0 or self.numberOfCities(simulation) > 0:
				self.setAliveTo(True, simulation)

	def numberOfCities(self, simulation) -> int:
		return simulation.citiesOf(player=self)

	def numberOfUnits(self, simulation) -> int:
		return simulation.unitsOf(player=self)

	def setAliveTo(self, alive, simulation):
		if self.isAliveVal != alive:
			self.isAliveVal = alive

			if not alive:
				# cleanup
				# killUnits();
				# killCities();
				# GC.getGame().GetGameDeals()->DoCancelAllDealsWithPlayer(GetID());

				if self.isHuman():
					simulation.setGameStateTo(GameState.over)

				self.endTurn(simulation)

	def setAllUnitsUnprocessed(self, simulation):
		for unit in simulation.unitsOf(player=self):
			unit.setTurnProcessedTo(False)

	def updateTimers(self, simulation):
		for unit in simulation.unitsOf(player=self):
			unit.updateMission(simulation)
			unit.doDelayedDeath(simulation)

		self.diplomacyAI.update(simulation)

	def updateNotifications(self, simulation):
		pass

	def hasActiveDiplomacyRequests(self) -> bool:
		return False

	def doUpdateTradeRouteCapacity(self, simulation):
		pass

	def envoyEffects(self, simulation):
		return []

	def doFirstContactWith(self, otherPlayer, simulation):
		self.diplomacyAI.doFirstContactWith(otherPlayer, simulation)
		otherPlayer.diplomacyAI.doFirstContactWith(self, simulation)

		if otherPlayer.isMajorAI() or otherPlayer.isHuman():
			# moment
			self.addMoment(MomentType.metNewCivilization, civilization=otherPlayer.leader.civilization(), simulation=simulation)

		# update eurekas
		if not self.techs.eurekaTriggeredFor(TechType.writing):
			self.techs.triggerEurekaFor(TechType.writing, simulation)

		if self.isCityState():
			self.doQuests(simulation)

		if otherPlayer.isCityState():
			otherPlayer.doQuests(simulation)

		return

	def addMoment(self, momentType: MomentType, civilization: Optional[CivilizationType] = None,
				  cityName: Optional[str] = None, continentName: Optional[str] = None,
				  eraType: Optional[EraType] = None, naturalWonder: Optional[FeatureType] = None,
	              dedication: Optional[DedicationType] = None,
				  simulation = None):
		if simulation is None:
			raise Exception('simulation not provided')

		if not momentType.minEra() <= self.currentEraVal <= momentType.maxEra():
			return

		self.moments.addMomentOf(momentType, simulation.currentTurn, civilization=civilization,
								 cityName=cityName, continentName=continentName, eraType=eraType,
								 naturalWonder=naturalWonder, dedication=dedication)

		# also show a notification, when the moment brings era score
		if momentType.eraScore() > 0:
			if self.isHuman():
				self.notifications.addNotification(NotificationType.momentAdded, momentType=momentType)

	def hasMoment(self, momentType: MomentType, civilization: Optional[CivilizationType] = None,
	              eraType: Optional[EraType] = None, cityName: Optional[str] = None,
	              continentName: Optional[str] = None, naturalWonder: Optional[FeatureType] = None,
	              dedication: Optional[DedicationType] = None) -> bool:
		return self.moments.hasMoment(momentType=momentType, civilization=civilization, eraType=eraType,
		                              cityName=cityName, continentName=continentName, naturalWonder=naturalWonder,
		                              dedication=dedication)

	def militaryMight(self, simulation) -> int:
		might = 0.0

		# Current combat strength
		for unit in simulation.unitsOf(player=self):
			might += float(unit.power())

		# Simplistic increase based on player's gold
		# 500 gold will increase might by 22%, 2000 by 45%, 8000 gold by 90%
		treasureValue = max(0.0, self.treasury.value())
		goldMultiplier = 1.0 + math.sqrt(treasureValue) / 100.0
		if goldMultiplier > 2.0:
			goldMultiplier = 2.0

		might *= goldMultiplier

		return int(might)

	def doEurekas(self, simulation):
		if not self.civics.inspirationTriggeredFor(CivicType.earlyEmpire):
			if self.population(simulation) >= 6:
				self.civics.triggerInspirationFor(CivicType.earlyEmpire, simulation)

	def population(self, simulation) -> int:
		populationVal = 0

		for city in simulation.citiesOf(self):
			populationVal += city.population()

		return populationVal

	def doResourceStockpile(self, simulation):
		pass

	def doSpaceRace(self, simulation):
		pass

	def doUpdateCramped(self, simulation):
		pass

	def hasActiveDiploRequestWithHuman(self) -> bool:
		return False

	def doProcessAge(self, simulation):
		pass

	def doUpdateWarWeariness(self, simulation):
		pass

	def doCityAmenities(self, simulation):
		pass

	def doCivics(self, simulation):
		pass

	def doTechs(self, simulation):
		pass

	def doGovernment(self, simulation):
		pass

	def doFaith(self, simulation):
		pass

	def doGreatPeople(self, simulation):
		pass

	def doTurnPost(self):
		pass

	def canFoundAt(self, location: HexPoint, simulation) -> bool:
		# FIXME check deals
		# Has the AI agreed to not settle here?

		# FIXME Settlers cannot found cities while empire is very unhappy

		tile = simulation.tileAt(location)
		if simulation.citySiteEvaluator().canCityBeFoundOn(tile, self):
			return True

		return False

	def canEnterOcean(self) -> bool:
		return False

	def foundAt(self, location: HexPoint, name: Optional[str], simulation):
		tile = simulation.tileAt(location)
		cityName = name if name is not None else self.newCityName(simulation)

		# moments
		# check if tile is on a continent that the player has not settler yet
		tileContinent = simulation.continentAt(location)
		if tileContinent is not None:
			if not self.hasSettledOnContinent(tileContinent):
				self.markSettledOnContinent(tileContinent)

				# only from second city (capital == first city is also founded on a 'new' continent)
				if len(simulation.cities(self)) > 0:
					self.addMoment(MomentType.cityOnNewContinent, cityName=cityName, continentName=tileContinent.name(), simulation=simulation)

		if tile.terrain() == TerrainType.tundra:
			self.addMoment(MomentType.tundraCity, cityName=cityName, simulation=simulation)
		elif tile.terrain() == TerrainType.desert:
			self.addMoment(MomentType.desertCity, cityName=cityName, simulation=simulation)
		elif tile.terrain() == TerrainType.snow:
			self.addMoment(MomentType.snowCity, cityName=cityName, simulation=simulation)

		if simulation.isLargestPlayer(self) and not self.hasMoment(MomentType.worldsLargestCivilization):
			self.addMoment(MomentType.worldsLargestCivilization, simulation)

		nearVolcano: bool = False
		nearNaturalWonder: bool = False
		for neighbor in location.areaWithRadius(2):
			neighborTile = simulation.tileAt(neighbor)

			if neighborTile.hasFeature(FeatureType.volcano):
				nearVolcano = True

			if neighborTile.feature().isNaturalWonder():
				nearNaturalWonder = True

		if nearVolcano and not self.hasMoment(MomentType.cityNearVolcano):
			self.addMoment(MomentType.cityNearVolcano, cityName=cityName, simulation=simulation)

		if nearNaturalWonder and not self.hasMoment(MomentType.cityOfAwe):
			self.addMoment(MomentType.cityOfAwe, cityName=cityName, simulation=simulation)

		isCapital = len(simulation.citiesOf(self)) == 0

		city = City(cityName, location, isCapital, self)
		city.initialize(simulation)

		simulation.addCity(city)

		if self.isHuman():
			# Human player is prompted to choose production BEFORE the AI runs for the turn.
			# So we'll force the AI strategies on the city now, just after it is founded.
			# And if the very first turn, we haven't even run player strategies once yet, so do that too.
			if simulation.currentTurn == 0:
				self.economicAI.doTurn(simulation)
				self.militaryAI.doTurn(simulation)

			city.cityStrategy.turn(simulation)

			if self.isActive():
				self.notifications.addNotification(NotificationType.productionNeeded, city=city.name, location=city.location)

			city.doFoundMessage()

			# If this is the first city(or we still aren't getting tech for some other reason) notify the player
			if self.techs.needToChooseTech() and self.science(simulation) > 0.0:
				self.notifications.addNotification(NotificationType.techNeeded)

			# If this is the first city( or..) notify the player
			if self.civics.needToChooseCivic() and self.culture(simulation, consume=False) > 0.0:
				self.notifications.addNotification(NotificationType.civicNeeded)

			if isCapital:
				self.notifications().addNotification(NotificationType.policyNeeded)
		else:
			city.doFoundMessage()

			# AI civ, may need to redo city specializations
			self.citySpecializationAI.setSpecializationsDirty()

		# roman roads
		if self.leader.civilization().ability() == CivilizationAbility.allRoadsLeadToRome:
			if not isCapital:
				capital = simulation.capitalOf(self)

				path = simulation.shortestPathFrom(
					location,
					capital.location,
					UnitMovementType.walk,
					self,
					UnitMapType.combat,
					canEmbark=False,
					canEnterOcean=self.canEnterOcean()
				)

				# If within Trade Route range of the Capital, a road to it.
				if path is not None and path.count <= TradeRoutes.landRange:

					for pathLocation in path:
						pathTile = simulation.tileAt(pathLocation)
						pathTile.setRoute(self.bestRoute())

		# send gossip
		simulation.sendGossip(GossipType.cityFounded, cityName=cityName, player=self)

		self._citiesFoundValue += 1

		if simulation.tutorial() == Tutorials.foundFirstCity and self.isHuman():
			if self._citiesFoundValue >= Tutorials.foundFirstCityTutorialCitiesToFound:
				simulation.userInterface.finishTutorial(Tutorials.foundFirstCity)
				simulation.enableTutorial(Tutorials.none)

	def newCityName(self, simulation):
		possibleNames = self.leader.civilization().cityNames()

		if self.isCityState() and len(possibleNames) == 0:
			possibleNames.append(self.cityState.name())

		for builtCityName in self.builtCityNames:
			possibleNames = list(filter(lambda name: name != builtCityName, possibleNames))

		for city in simulation.citiesOf(self):
			possibleNames = list(filter(lambda name: name != city.name, possibleNames))

		if len(possibleNames) > 0:
			return possibleNames[0]

		return "TXT_KEY_CITY_NAME_GENERIC"

	def hasBuilding(self, buildingType: BuildingType, simulation) -> bool:
		for city in simulation.citiesOf(self):
			if city.hasBuilding(buildingType):
				return True

		return False

	def canEmbark(self) -> bool:
		return self.hasTech(TechType.shipBuilding)

	def hasTech(self, techType: TechType) -> bool:
		return self.techs.hasTech(techType)
