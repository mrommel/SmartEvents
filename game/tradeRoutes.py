from game.cityStates import CityStateType
from game.civilizations import CivilizationAbility
from game.governors import GovernorTitle, GovernorType
from game.greatPersons import GreatPersonType
from game.policyCards import PolicyCardType
from game.wonders import WonderType
from map.base import HexPoint
# from map.path_finding.finder import AStarDataSource
from map.types import UnitMovementType, Yields


class TradeRoutes:
	landRange = 15


class TradeRoute:
	def __init__(self, path):
		self._path = path

	def start(self) -> HexPoint:
		return self._path.points()[0]

	def last(self) -> HexPoint:
		return self._path.points()[-1]

	def path(self):
		return self._path

	def startCity(self, simulation):
		firstPoint: HexPoint = self._path.points()[0]
		return simulation.cityAt(firstPoint)

	def endCity(self, simulation):
		lastPoint: HexPoint = self._path.points()[-1]
		return simulation.cityAt(lastPoint)

	def yields(self, simulation) -> Yields:
		"""
		get the yields per turn of a specific trade route
		https://civilization.fandom.com/wiki/Trade_Route_(Civ6)#Trade_Yields_Based_on_Districts
		@param simulation: game
		@return: `Yields` of this trade rotue
		"""
		yields: Yields = Yields(food=0.0, production=0.0, gold=0.0)

		startCity = self.startCity(simulation)
		startPlayer = startCity.player
		startPlayerGovernment = startPlayer.government
		startCityDistricts = startCity.districts
		endCity = self.endCity(simulation)
		endDistricts = endCity.districts
		endCityGovernor = endCity.governor()

		if self.isDomestic(simulation):
			yields += endDistricts.domesticTradeYields()

			# satrapies - Domestic Trade Routes provide +2 Gold and +1 Culture.
			if startPlayer.leader.civilization().ability() == CivilizationAbility.satrapies:
				yields.gold += 2.0
				yields.culture += 1.0

			# collectivization - +2 Production and +4 Food from domestic Trade Routes.
			if startPlayerGovernment.hasCard(PolicyCardType.collectivization):
				yields.production += 2.0
				yields.food += 4.0

			# universityOfSankore - Domestic Trade Routes give an additional +1 Faith to this city
			if endCity.hasWonder(WonderType.universityOfSankore):
				yields.faith += 1.0

			# isolationism - Domestic routes provide + 2 Food, +2 Production.
			# BUT: Can't train or buy Settlers nor settle new cities.
			if startPlayerGovernment.hasCard(PolicyCardType.isolationism):
				yields.food += 2
				yields.production += 2

		else:
			yields += endDistricts.foreignTradeYields()

			if startPlayer.hasRetired(GreatPersonType.zhangQian):
				# Foreign Trade Routes to this city provide +2 Gold to both cities.
				yields.gold += 2.0

			# amsterdam or antioch suzerain bonus
			# Your Trade Routes to foreign cities earn + 1 Gold for each luxury resource.
			if startPlayer.isSuzerain(CityStateType.amsterdam, simulation) or \
				startPlayer.isSuzerain(CityStateType.antioch, simulation):

				amountOfLuxuryResources = startCity.numLocalLuxuryResources(simulation)
				yields.gold += 1.0 * float(amountOfLuxuryResources)

			# kumasi suzerain bonus
			# Your Trade Routes to any city - state provide + 2 Culture and +1 Gold for every
			# specialty district in the origin city.
			if startPlayer.isSuzerain(CityStateType.kumasi, simulation) and \
				endCity.player.isCityState() == True:

				numberOfSpecialtyDistricts: float = float(startCityDistricts.numberOfSpecialtyDistricts())
				yields.culture += 2.0 * numberOfSpecialtyDistricts
				yields.gold += 1.0 * numberOfSpecialtyDistricts

			# universityOfSankore - Other civilizations' Trade Routes to this city provide +1 Science and +1 Gold for them
			if endCity.hasWonder(WonderType.universityOfSankore):
				yields.science += 1.0
				yields.gold += 1.0

		# caravansaries - +2 Gold from all Trade Routes.
		if startPlayerGovernment.hasCard(PolicyCardType.caravansaries):
			yields.gold += 2.0

		# tradeConfederation - +1 Culture and +1 Science from international Trade Routes.
		if startPlayerGovernment.hasCard(PolicyCardType.tradeConfederation):
			yields.culture += 1.0
			yields.science += 1.0

		# triangularTrade - +4 Gold and +1 Faith from all Trade Routes.
		if startPlayerGovernment.hasCard(PolicyCardType.triangularTrade):
			yields.gold += 4.0
			yields.faith += 1.0

		# ecommerce - +2 Production and +5 Gold from all Trade Routes.
		if startPlayerGovernment.hasCard(PolicyCardType.ecommerce):
			yields.production += 2.0
			yields.gold += 5.0

		# universityOfSankore - +2 Science for every Trade Route to this city
		if endCity.hasWonder(WonderType.universityOfSankore):
			yields.science += 2.0

		if endCityGovernor is not None:
			# Your Trade Routes ending here provide +2[Food] Food to their starting city.
			if endCityGovernor.type == GovernorType.magnus and endCityGovernor.hasTitle(GovernorTitle.surplusLogistics):
				yields.food += 2.0

		# # posts - currently no implemented
		# yields.gold += float(self.posts.count)
		#
		# if startPlayer.leader.civilization().ability() == .allRoadsLeadToRome:
		# 	# Trade Routes generate +1 additional Gold from Roman Trading Posts they pass through.
		# 	yields.gold += Double(self.posts.count)

		return yields

	def isDomestic(self, simulation) -> bool:
		startLeader = self.startCity(simulation).player.leader
		endLeader = self.endCity(simulation).player.leader
		return startLeader == endLeader

	def isInternational(self, simulation) -> bool:
		return not self.isDomestic(simulation)


class TradeRoutePathfinderDataSource: # (AStarDataSource):
	def __init__(self, player, startLocation: HexPoint, targetLocation: HexPoint, simulation):
		#super().__init__(grid, UnitMovementType.walk)
		self.player = player

		self.startLocation = startLocation
		self.targetLocation = targetLocation

		self.simulation = simulation

		self.tradingPostLocations: [HexPoint] = []  # fixme

	def walkableAdjacentTilesCoords(self, tile_coord: HexPoint) -> [HexPoint]:
		startCity = self.simulation.cityAt(self.startLocation)
		walkableCoords: [HexPoint] = []

		for neighbor in tile_coord.neighbors():
			# if mapModel.wrapX
			# 	neighbor = mapModel.wrap(point: neighbor)

			if not self.simulation.valid(neighbor):
				continue

			isReachable: bool = False

			if neighbor.distance(self.startLocation) < TradeRoutes.landRange:
				isReachable = True

			for tradingPostLocation in self.tradingPostLocations:
				if neighbor.distance(tradingPostLocation) < TradeRoutes.landRange:
					isReachable = True

			if not isReachable:
				continue

			toTile = self.simulation.tileAt(neighbor)

			# walkable ?
			if toTile.isWater():
				continue

			# use possible trading post
			city = self.simulation.cityAt(neighbor)
			if city is not None:
				cityTradingPosts = city.cityTradingPosts
				if cityTradingPosts.hasTradingPostOf(self.player.leader) and \
					self.canEstablishDirectTradeRoute(startCity, city, self.simulation):

					self.tradingPostLocations.append(neighbor)

			walkableCoords.append(neighbor)

		return walkableCoords

	def costToMove(self, from_tile_coord: HexPoint, to_adjacent_tile_coord: HexPoint) -> float:
		return 1

	def canEstablishDirectTradeRoute(self, startCity, city, simulation):
		return False  # fixme
