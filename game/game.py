from typing import Optional

from game.ai.barbarians import BarbarianAI
from game.ai.religions import Religions
from game.baseTypes import HandicapType, GameState
from game.buildings import BuildingType
from game.cities import City
from game.civilizations import LeaderType, CivilizationType
from game.greatPersons import GreatPersonType
from game.moments import MomentType
from game.notifications import NotificationType
from game.players import Player
from game.promotions import UnitPromotionType
from game.states.builds import BuildType
from game.states.gossips import GossipType
from game.states.ui import ScreenType
from game.states.victories import VictoryType
from game.types import TechType, EraType, CivicType
from game.unitTypes import UnitMapType, UnitAbilityType, MoveOption
from game.units import Unit
from game.wonders import WonderType
from map import constants
from map.base import HexPoint, Size
from map.evaluators import CitySiteEvaluator, MapAnalyzer
from map.improvements import ImprovementType
from map.map import MapModel, Tile, ContinentType, Continent
from map.path_finding.finder import AStarPathfinder, MoveTypeIgnoreUnitsOptions, \
	MoveTypeIgnoreUnitsPathfinderDataSource, InfluencePathfinderDataSource
from map.path_finding.path import HexPath
from map.types import FeatureType, Tutorials, MapSize, UnitMovementType


class GameModel:
	def __init__(self, victoryTypes: [VictoryType], handicap: HandicapType, turnsElapsed: int, players, map: MapModel):
		self.turnSliceValue = 0
		self.waitDiploPlayer = None
		self.players = players
		self.currentTurn = turnsElapsed
		self.victoryTypes = victoryTypes
		self.handicap = handicap
		self._map = map
		self.userInterface = None
		self._gameStateValue = GameState.on

		# game ai
		self.barbarianAI = BarbarianAI()
		self.religions = Religions()

		# analyze map
		analyzer = MapAnalyzer(self._map)
		analyzer.analyze()

		# stats
		self.discoveredContinents = []

	def initialize(self, humanLeader: LeaderType):
		# init human player and units
		humanPlayer = Player(humanLeader, human=True)
		humanStartLocation = next(
			(startLocation for startLocation in self._map.startLocations if startLocation.leader == humanLeader), None)

		if humanStartLocation is None:
			raise Exception(f'no start location for {humanLeader} provided')

		for unitType in self.handicap.freeHumanStartingUnitTypes():
			unit = Unit(humanStartLocation.location, unitType, humanPlayer)
			self._map.addUnit(unit)

			if len(self.unitsAt(humanStartLocation)) > 1:
				unit.jumpToNearestValidPlotWithin(2, self)

		self.players.append(humanPlayer)

	# add ai players
	# for aiLeader in selectedLeaders:
	#	aiPlayer = Player(aiLeader, human=False, barbarian=False)
	#	self.players.append(aiPlayer)

	# def doTurn(self):
	# 	print(f'start turn {self.currentTurn}')
	# 	for player in self.players:
	# 		player.doTurn(self)
	#
	# 	self.currentTurn += 1

	def update(self):
		if self.userInterface is None:
			raise Exception("no UI")

		if self.isWaitingForBlockingInput():
			if not self.userInterface.isShown(ScreenType.diplomatic):
				# when diplomatic screen is visible - we can't update
				self.waitDiploPlayer.doTurnPostDiplomacy(self)
				self.setWaitingForBlockingInput(None)
			else:
				return

		# if the game is single player, it's ok to block all processing until
		# the user selects an extended match or quits.
		if self.gameState() == GameState.over:
			# self.testExtendedGame()
			return

		# self.sendPlayerOptions()

		if self.turnSlice() == 0 and not self.isPaused():
			# gDLL->AutoSave(true);
			pass

		# If there are no active players, move on to the AI
		if self.numGameTurnActive() == 0:
			self.doTurn()

		# Check for paused again, the doTurn call might have called something that paused the game and we don't want an update to sneak through
		if not self.isPaused():
			# self.updateWar()
			self.updateMoves()

		# And again, the player can change after the automoves and that can pause the game
		if not self.isPaused():
			self.updateTimers()

			self.updatePlayers(self)  # slewis added!

			# self.testAlive()

			if not self.humanPlayer().isAlive():
				self.setGameStateTo(GameState.over)

			# next player ???
			self.checkPlayerTurnDeactivate()

			self.changeTurnSliceBy(1)

	def capitalOf(self, player: Player) -> City:
		return self._map.capitalOf(player)

	def points(self) -> [HexPoint]:
		return self._map.points()

	def unitsOf(self, player: Player) -> [Unit]:
		return self._map.unitsOf(player)

	def unitsAt(self, location: HexPoint) -> [Unit]:
		return self._map.unitsAt(location)

	def unitAt(self, location: HexPoint, unitMapType: UnitMapType) -> Optional[Unit]:
		return self._map.unitAt(location, unitMapType)

	def addUnit(self, unit):
		self._map.addUnit(unit)

	def removeUnit(self, unit):
		self._map.removeUnit(unit)

	def cityAt(self, location: HexPoint) -> Optional[City]:
		return self._map.cityAt(location)

	def citiesOf(self, player) -> [City]:
		return self._map.citiesOf(player)

	def addCity(self, city):
		tile = self.tileAt(city.location)

		# check feature removal
		featureRemovalSurplus = 0
		featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeForest)
		featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeRainforest)
		featureRemovalSurplus += tile.productionFromFeatureRemoval(BuildType.removeMarsh)

		city.changeFeatureProduction(featureRemovalSurplus)

		tile.setFeature(FeatureType.none)

		self._map.addCity(city, simulation=self)
		# self.userInterface?.show(city: city)

		# update area around the city
		for pt in city.location.areaWithRadius(3):
			if not self._map.valid(pt):
				continue

			neighborTile = self.tileAt(pt)
			self.userInterface.refreshTile(neighborTile)

		# update eureka
		if not city.player.techs.eurekaTriggeredFor(TechType.sailing):
			if self._map.isCoastalAt(city.location):
				city.player.techs.triggerEurekaFor(TechType.sailing, self)

		return

	def tileAt(self, location) -> Tile:
		return self._map.tileAt(location)

	def riverAt(self, location) -> bool:
		return self._map.riverAt(location)

	def valid(self, point: HexPoint) -> bool:
		return self._map.valid(point)

	def isCoastalAt(self, location) -> bool:
		return self._map.isCoastalAt(location)

	def tutorial(self) -> Tutorials:
		return Tutorials.none

	def showTutorialInfos(self) -> bool:
		return False

	def isWaitingForBlockingInput(self) -> bool:
		return self.waitDiploPlayer is not None

	def gameState(self) -> GameState:
		return self._gameStateValue

	def setGameStateTo(self, gameState: GameState):
		print(f'ooo Game has be set to {gameState} in turn {self.currentTurn} ooo')
		self._gameStateValue = gameState

	def turnSlice(self) -> int:
		return self.turnSliceValue

	def setTurnSliceTo(self, value: int):
		self.turnSliceValue = value

	def changeTurnSliceBy(self, delta: int):
		self.turnSliceValue += delta

	def isPaused(self):
		return False

	def numGameTurnActive(self):
		numActive = 0
		for player in self.players:
			if player.isAlive() and player.isActive():
				numActive += 1

		return numActive

	def doTurn(self):
		print('', flush=True)
		print(f"::: TURN {self.currentTurn + 1} starts now :::", flush=True)
		print('', flush=True)

		self.humanPlayer().resetFinishTurnButtonPressed()

		self.barbarianAI.doTurn(self)
		self.religions.doTurn(self)

		# doUpdateCacheOnTurn();
		# DoUpdateCachedWorldReligionTechProgress();

		self.updateScore()

		# m_kGameDeals.DoTurn();

		for player in self.players:
			player.prepareTurn(self)

		# map.doTurn()

		# GC.GetEngineUserInterface()->doTurn();

		self.barbarianAI.doCamps(self)
		self.barbarianAI.doUnits(self)

		# incrementGameTurn();
		self.currentTurn += 1

		# Sequential turns.
		# Activate the << FIRST >> player we find from the start, human or AI, who wants a sequential turn.
		for player in self.players:
			if player.isAlive():
				player.startTurn(self)

				# show stacked messages
				# if player.isHuman():
				#    self.showMessages()

				break

		# self.doUnitedNationsCountdown();

		self.doWorldEra()

		# Victory stuff
		self.doTestVictory()

		# Who's Winning every 25 turns (to be un-hardcoded later)
		human = self.humanPlayer()
		if human.isAlive():
			if self.currentTurn % 25 == 0:
				# This popup is the sync rand, so beware
				# self.userInterface.showScreen(screenType: .interimRanking, city: nil, other: nil, data: nil)
				pass

	def humanPlayer(self) -> Player:
		return next((player for player in self.players if player.isHuman()), None)

	def updateScore(self):
		pass

	def doWorldEra(self):
		pass

	def doTestVictory(self):
		pass

	def updateMoves(self):
		playersToProcess = []
		processPlayerAutoMoves = False

		for player in self.players:

			if player.isAlive() and player.isActive() and not player.isHuman():
				playersToProcess.append(player)
				processPlayerAutoMoves = False

				# Notice the break. Even if there is more than one AI with an active turn, we do them sequentially.
				break

		# If no AI with an active turn, check humans.
		if len(playersToProcess) == 0:
			processPlayerAutoMoves = True

			for player in self.players:
				# player.checkInitialTurnAIProcessed()
				if player.isActive() and player.isHuman():
					playersToProcess.append(player)

		if len(playersToProcess) > 0:
			player = playersToProcess[0]

			readyUnitsBeforeMoves = player.countReadyUnits(self)

			if player.isAlive():
				needsAIUpdate = player.hasUnitsThatNeedAIUpdate(self)
				if player.isActive() or needsAIUpdate:
					if not player.isAutoMoves() or needsAIUpdate:
						if needsAIUpdate or not player.isHuman():
							# ------- this is where the important stuff happens! --------------
							player.unitUpdate(self)
						# print("updateMoves() : player.unitUpdate() called for player \(player.leader.name())")

						readyUnitsNow = player.countReadyUnits(self)

						# Was a move completed, if so save off which turn slice this was
						if readyUnitsNow < readyUnitsBeforeMoves:
							player.setLastSliceMoved(self.turnSlice())

						if not player.isHuman() and not player.hasBusyUnitOrCity():

							if readyUnitsNow == 0:
								player.setAutoMovesTo(True)
							else:
								if player.hasReadyUnit(self):
									waitTime = 5

									if self.turnSlice() - player.lastSliceMoved() > waitTime:
										print(
											"GAME HANG - Please show and send save. Stuck units will have their turn ended so game can advance.")
										# debug
										for unit in self.unitsOf(player):
											if not unit.readyToMove():
												continue

											print(
												f"GAME HANG - unit of {player.leader.name()} has no orders: {unit.name()} at {unit.location}")

										# debug
										player.endTurnsForReadyUnits(self)

						if player.isAutoMoves() and (not player.isHuman() or processPlayerAutoMoves):
							repeatAutomoves = False
							repeatPassCount = 2  # Prevent getting stuck in a loop

							while True:
								for loopUnit in self.unitsOf(player):
									loopUnit.autoMission(self)

									# Does the unit still have movement points left over?
									if player.isHuman() and loopUnit.hasCompletedMoveMission(
										self) and loopUnit.canMove() and not loopUnit.isAutomated():

										if player.turnFinished():
											repeatAutomoves = True  # Do another pass.

								# This is a short - term solution to a problem where a unit
								# with an auto-mission (a queued, multi-turn) move order cannot reach its destination, but
								# does not re-enter the "need order" list because this code is processed at the end of turns.The result is that the player could easily "miss" moving
								# the unit this turn because it displays "next turn" rather than "skip unit turn" and the unit is not added to the "needs orders" list.
								# To correctly fix this problem, we would need some way to determine if any of the auto-missions are invalid before the player can end the turn and
								# activate the units that have a problem.
								# The problem with evaluating this is that, with one unit per tile, we don't know what is a valid move until other units have moved.
								# (For example, if one unit was to follow another, we would want the unit in the lead to move first and then have the following unit move, in order
								# to prevent the following unit from constantly waking up because it can't move into the next tile. This is currently not supported.)

								# This short-term solution will reactivate a unit after the player clicks "next turn".It will appear strange, because the player will be asked to move
								# a unit after they clicked "next turn", but it is to give the player a chance to move all of their units.

								# jrandall sez: In MP matches, let's not OOS or stall the game.

								repeatPassCount -= 1

								if not (repeatAutomoves and repeatPassCount > 0):
									break

							# check if the(for now human) player is overstacked and move the units
							# if (player.isHuman())

							# slewis - I changed this to only be the AI because human players should have the tools to deal with this now
							if not player.isHuman():
								for loopUnit in self.unitsOf(player):
									loopUnit.doDelayedDeath(self)

						# If we completed the processing of the auto - moves, flag it.
						if player.turnFinished() or not player.isHuman():
							player.setProcessedAutoMovesTo(True)

					# KWG: This code should go into CheckPlayerTurnDeactivate
					if not player.turnFinished() and player.isHuman():
						if not player.hasBusyUnitOrCity():
							player.setEndTurn(True, self)

							if player.isEndTurn():
								# If the player's turn ended, indicate it in the log.  We only do so when the end turn state has changed to prevent useless log spamming in multiplayer.
								# NET_MESSAGE_DEBUG_OSTR_ALWAYS("UpdateMoves() : player.setEndTurn(true) called for player " << player.GetID() << " " << player.getName())
								pass
						else:
							# if !player.hasBusyUnitUpdatesRemaining() {
							# NET_MESSAGE_DEBUG_OSTR_ALWAYS("Received turn complete for player " << player.GetID() << " " << player.getName() << " but there is a busy unit. Forcing the turn to advance")
							player.setEndTurn(True, self)

	def updateTimers(self):
		activePlayer = self.activePlayer()
		if activePlayer is None or not activePlayer.isHuman():
			return

		for player in self.players:
			if player.isAlive():
				player.updateTimers(self)

	def updatePlayers(self, simulation):
		for player in self.players:
			if player.isAlive() and player.isActive():
				player.updateNotifications(simulation)

	def checkPlayerTurnDeactivate(self):
		""" Check to see if the player's turn should be deactivated.
			This occurs when the player has set its EndTurn and its AutoMoves to true
			and all activity has been completed."""
		if self.userInterface is None:
			raise Exception("no UI")

		for player in self.players:
			if player.isAlive() and player.isActive():
				# For some reason, AI players don't set EndTurn, why not?
				if player.turnFinished() or (not player.isHuman() and not player.hasActiveDiplomacyRequests()):
					if player.hasProcessedAutoMoves():
						autoMovesComplete = False
						if not player.hasBusyUnitOrCity():
							autoMovesComplete = True
							# print("+++ GameModel - CheckPlayerTurnDeactivate() : auto-moves complete for \(player.leader.name())")

						if autoMovesComplete:
							# Activate the next player
							# In that case, the local human is (should be) the player we just deactivated the turn for
							# and the AI players will be activated all at once in CvGame::doTurn, once we have received
							# all the moves from the other human players
							if not self.userInterface.isShown(ScreenType.diplomatic):
								player.endTurn(self)

								# If it is a hot seat game and the player is human and is dead, don't advance the player,
								# we want them to get the defeat screen
								if player.isAlive() or not player.isHuman():
									hasReachedCurrentPlayer = False
									for nextPlayer in self.players:

										if nextPlayer.leader == player.leader:
											hasReachedCurrentPlayer = True
											continue

										if not hasReachedCurrentPlayer:
											continue

										if nextPlayer.isAlive():
											# the player is alive and also running sequential turns.they're up!
											nextPlayer.startTurn(self)
											# self.resetTurnTimer(false)
											break
							else:
								# KWG: This doesn't actually do anything other than print to the debug log
								print(f"Because the diplomatic screen is blocking, I am bumping this up for player "
								      f"{player.leader}")
							# changeNumGameTurnActive(1, std::string("Because the diplo screen is blocking I am
							# bumping this up for player ") + getName());

	def setWaitingForBlockingInput(self, player):
		self.waitDiploPlayer = player

	def activePlayer(self):
		return next((player for player in self.players if player.isAlive() and player.isActive()), None)

	def updateTacticalAnalysisMap(self, player):
		# fixme
		pass

	def sightAt(self, location: HexPoint, sight: int, unit=None, player=None):
		if player is None:
			raise Exception("cant get player")

		currentTile = self.tileAt(location)
		hasSentry: bool = unit.hasPromotion(UnitPromotionType.sentry) if unit is not None else False

		for areaPoint in location.areaWithRadius(sight):
			tile = self.tileAt(areaPoint)

			if tile is None:
				continue

			if not tile.canSeeTile(currentTile, player, sight, hasSentry, self):
				continue

			# inform the player about a goody hut
			if tile.hasImprovement(ImprovementType.goodyHut) and not tile.isDiscoveredBy(player):
				player.notifications().addNotification(NotificationType.goodyHutDiscovered, location=areaPoint)

			# inform the player about a barbarian camp
			if tile.hasImprovement(ImprovementType.barbarianCamp) and not player.isBarbarianCampDiscoveredAt(areaPoint):
				player.discoverBarbarianCampAt(areaPoint)

			# check if tile is on another continent than the(original) capital
			continent = self.continentAt(areaPoint)
			if continent is not None:
				tileContinent: ContinentType = continent.continentType
				capitalLocation = player.originalCapitalLocation()
				if capitalLocation != constants.invalidHexPoint:
					capitalContinent = self.continentAt(capitalLocation)
					if capitalContinent is not None:
						if tileContinent != capitalContinent.continentType and \
							capitalContinent.continentType != ContinentType.none and \
							tileContinent != ContinentType.none:
							if not player.civics.inspirationTriggeredFor(CivicType.foreignTrade):
								player.civics.triggerInspirationFor(CivicType.foreignTrade, simulation=self)

			# found Natural wonder
			feature = tile.feature()
			if feature.isNaturalWonder():
				# check if wonder is discovered by player already
				if not player.hasDiscoveredNaturalWonder(feature):
					player.doDiscoverNaturalWonder(feature)
					player.addMoment(MomentType.discoveryOfANaturalWonder, naturalWonder=feature, simulation=self)

					if unit.hasAbility(UnitAbilityType.experienceFromTribal):
						# Gains XP when activating Tribal Villages(+5 XP) and discovering Natural Wonders(+10 XP)
						unit.changeExperienceBy(10, self)

					if player.isHuman():
						player.notifications().addNotification(NotificationType.naturalWonderDiscovered,
						                                       location=areaPoint)

				if not player.techs.eurekaTriggeredFor(TechType.astrology):
					player.techs.triggerEurekaFor(TechType.astrology, self)

			tile.discoverBy(player, self)
			tile.sightBy(player)
			player.checkWorldCircumnavigated(self)
			if continent is not None:
				self.checkDiscoveredContinent(continent, areaPoint, player)

			self.userInterface.refreshTile(tile)

		return

	def concealAt(self, location: HexPoint, sight: int, unit=None, player=None):
		currentTile = self.tileAt(location)

		hasSentry: bool = unit.hasPromotion(UnitPromotionType.sentry) if unit is not None else False

		for loopPoint in location.areaWithRadius(sight):
			loopTile = self.tileAt(loopPoint)

			if loopTile is None:
				continue

			if not loopTile.canSeeTile(currentTile, player, sight, hasSentry=hasSentry, simulation=self):
				continue

			loopTile.concealTo(player)
			self.userInterface.refreshTile(loopTile)

		return

	def continentAt(self, location) -> Optional[Continent]:
		if not self.valid(location):
			return None

		tile = self.tileAt(location)
		identifier = tile.continentIdentifier

		if identifier is not None:
			return self._map.continent(identifier)

		return None

	def citySiteEvaluator(self) -> CitySiteEvaluator:
		return CitySiteEvaluator(self._map)

	def isLargestPlayer(self, player) -> bool:
		"""
			check if moment worldsLargestCivilization should trigger

			- Parameter civilization: civilization to check
			- Returns:  has the civilization at least 3 more cities than the next biggest civilization
		"""
		numPlayerCities = len(self.citiesOf(player))
		numAllOtherCities = map(lambda p: len(self.citiesOf(p)), self.players)
		numNextBestPlayersCities = max(numAllOtherCities)

		return numPlayerCities >= (numNextBestPlayersCities + 3)

	def sendGossip(self, gossipType: GossipType, cityName: Optional[str] = None, tech: Optional[TechType] = None,
	               player=None, leader: Optional[LeaderType] = None, building: Optional[BuildingType] = None):
		print('send gossip is not implemented')  # fixme
		pass

	def visibleEnemyAt(self, location: HexPoint, player, unitMapType: UnitMapType = UnitMapType.combat) -> Optional[
		Unit]:
		tile = self.tileAt(location)

		if tile.isVisibleTo(player):
			enemyUnit = self.unitAt(location, unitMapType)

			if enemyUnit is not None and player.diplomacyAI.isAtWarWith(enemyUnit.player):
				return enemyUnit

		return None

	def unitAwarePathfinderDataSource(self, unit) -> MoveTypeIgnoreUnitsPathfinderDataSource:
		datasourceOptions = MoveTypeIgnoreUnitsOptions(
			ignore_sight=True,
			can_embark=unit.player.canEmbark(),
			can_enter_ocean=unit.player.canEnterOcean()
		)
		return MoveTypeIgnoreUnitsPathfinderDataSource(self._map, unit.movementType(), unit.player, datasourceOptions)

	def ignoreUnitsPathfinderDataSource(self, movementType: UnitMovementType, player, unitMapType: UnitMapType,
	                                    canEmbark: bool, canEnterOcean: bool) -> MoveTypeIgnoreUnitsPathfinderDataSource:
		datasourceOptions = MoveTypeIgnoreUnitsOptions(
			ignore_sight=True,
			can_embark=canEmbark,
			can_enter_ocean=canEnterOcean
		)
		return MoveTypeIgnoreUnitsPathfinderDataSource(self._map, movementType, player, datasourceOptions)

	def pathTowards(self, target: HexPoint, options: [MoveOption], unit) -> HexPath:
		datasource = self.unitAwarePathfinderDataSource(unit)
		pathFinder = AStarPathfinder(datasource)

		path = pathFinder.shortestPath(unit.location, target)

		# add costs
		path.addCost(0.0)  # first location

		lastPoint = None
		for index, point in enumerate(path.points()):
			if index == 0:
				lastPoint = point
				continue

			cost = datasource.costToMove(lastPoint, point)
			path.addCost(cost)
			lastPoint = point

		return path

	def anyHasMoment(self, momentType: MomentType, civilization: Optional[CivilizationType] = None,
	                 eraType: Optional[EraType] = None) -> bool:
		for player in self.players:
			if player.hasMoment(momentType, civilization=civilization, eraType=eraType):
				return True

		return False

	def alreadyBuiltWonder(self, wonderType: WonderType) -> bool:
		for player in self.players:
			if player.hasWonder(wonderType, self):
				return True

		return False

	def checkArchaeologySites(self):
		pass

	def isEnemyVisibleAt(self, location: HexPoint, player, unitMapType: UnitMapType = UnitMapType.combat) -> bool:
		return self.visibleEnemyAt(location, player, unitMapType) is not None

	def mapSize(self) -> Size:
		return self._map.bestMatchingSize().size()

	def checkDiscoveredContinent(self, continentType: ContinentType, location: HexPoint, player):
		"""
		/// method to trigger the firstDiscoveryOfANewContinent moment, when player has discovered a new continent before everybody else
	    ///
	    /// - Parameters:
	    ///   - continent: continent to check
	    ///   - player: player to check and trigger the moment for

		@param continentType:
		@param location:
		@param player:
		@return:
		"""
		if player is None:
			raise Exception('player must not be None')

		if not self.hasDiscoveredContinent(continentType):
			self.markContinentDiscovered(continentType)

			continent = self._map.continentBy(continentType)
			if continent is not None:
				# only trigger discovery of new continent, if player has at least one city
				# this prevents first city triggering this
				if continent.points.count > 8 and len(self.citiesOf(player)) > 0:
					player.addMoment(MomentType.firstDiscoveryOfANewContinent, self)

					if player.isHuman():
						player.notifications().addNotification(
							NotificationType.continentDiscovered,
							location=location,
							continentName=continentType.name()
						)
		return

	def hasDiscoveredContinent(self, continentType: ContinentType) -> bool:
		return continentType in self.discoveredContinents

	def markContinentDiscovered(self, continentType: ContinentType):
		self.discoveredContinents.append(continentType)

	def calculateInfluenceDistance  (self, cityLocation: HexPoint, targetDestination: HexPoint, limit: int) -> int:
		if cityLocation == targetDestination:
			return 0

		influencePathfinderDataSource = InfluencePathfinderDataSource(self._map, cityLocation)
		influencePathfinder = AStarPathfinder(influencePathfinderDataSource)

		path = influencePathfinder.shortestPath(cityLocation, targetDestination)
		if path is not None:
			return int(path.cost())

		return 0

	def isAdjacentDiscovered(self, point: HexPoint, player) -> bool:
		for neighbor in point.neighbors():
			tile = self._map.tileAt(neighbor)

			if tile is None:
				continue

			if tile.isDiscoveredBy(player):
				return True

		return False

	def isWithinCityRadius(self, tile, player) -> bool:
		playerCities = self.citiesOf(player)

		for city in playerCities:
			if tile.point.distance(city.location) < City.workRadius:
				return True

		return False

	def areas(self):
		return self._map.areas

	def isGreatGeneral(self, greatPerson: GreatPersonType, player, location: HexPoint, range: int) -> bool:
		for unit in self.unitsOf(player):
			if unit.location.distance(location) <= range:
				if unit.greatPerson == greatPerson:
					return True

		return False
