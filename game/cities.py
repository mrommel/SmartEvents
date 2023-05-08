import random

from game.ai.cities import CityStrategyAI
from game.buildings import BuildingType
from game.civilizations import LeaderWeightList, CivilizationAbility, LeaderAbility, LeaderType
from game.districts import DistrictType
from game.religions import PantheonType
from game.types import EraType, TechType
from game.unit_types import ImprovementType
from game.wonders import WonderType
from map.base import HexPoint
from map.types import YieldList, FeatureType, TerrainType, ResourceUsage, ResourceType
from utils.base import ExtendedEnum


class CityDistricts:
	def __init__(self, city):
		self.city = city

	def build(self, district: DistrictType, location: HexPoint):
		pass


class CityBuildings:
	def __init__(self, city):
		self.city = city

	def build(self, building: BuildingType):
		pass


class CityWonders:
	def __init__(self, city):
		self.city = city


class CityProjects:
	def __init__(self, city):
		self.city = city
		

class CityCitizens:
	def __init__(self, city):
		self.city = city

	def initialize(self, simulation):
		pass

	def doFound(self, simulation):
		pass


class CityGreatWorks:
	def __init__(self, city):
		self.city = city


class CityReligion:
	def __init__(self, city):
		self.city = city


class CityTradingPosts:
	def __init__(self, city):
		self.city = city

	def buildTradingPost(self, leader: LeaderType):
		pass


class CityTourism:
	def __init__(self, city):
		self.city = city


class AgeType(ExtendedEnum):
	normal = 'normal'


class RouteType(ExtendedEnum):
	ancientRoad = 'ancientRoad'


class GossipType(ExtendedEnum):
	districtConstructed = 'districtConstructed'


class MomentType(ExtendedEnum):
	dedicationTriggered = 'dedicationTriggered'
	worldsFirstNeighborhood = 'worldsFirstNeighborhood'
	firstNeighborhoodCompleted = 'firstNeighborhoodCompleted'


class DedicationType(ExtendedEnum):
	monumentality = 'monumentality'


class YieldValues:
	pass

class YieldValues:
	def __init__(self, value: float, percentage: float = 0.0):
		self.value = value
		self.percentage = percentage

	def calc(self) -> float:
		return self.value * self.percentage

	def __add__(self, other):
		if isinstance(other, float):
			return YieldValues(self.value + other, self.percentage)
		elif isinstance(other, YieldValues):
			return YieldValues(self.value + other.value, self.percentage + other.percentage)
		else:
			raise Exception(f'invalid parameter: {other}')


class CityState(ExtendedEnum):
	johannesburg = 'johannesburg'
	auckland = 'auckland'


class City:
	def __init__(self, name: str, location: HexPoint, isCapital: bool, player):
		self.name = name
		self.location = location
		self.capitalValue = isCapital
		self.everCapitalValue = isCapital
		self.populationValue = 0
		self.gameTurnFoundedValue = 0
		self.foodBasketValue = 1.0

		self.player = player
		self.leader = player.leader
		self.originalLeaderValue = player.leader
		self.previousLeaderValue = None

		self.isFeatureSurroundedValue = False
		self.threatVal = 0

		self.healthPointsValue = 200
		self.amenitiesForWarWearinessValue = 0

		self.productionAutomatedValue = False
		self.baseYieldRateFromSpecialists = YieldList()
		self.extraSpecialistYield = YieldList()
		self.numPlotsAcquiredList = LeaderWeightList()

		self.featureProductionValue = 0.0

		# ai
		self.cityStrategyAI = CityStrategyAI(self)

		# init later via 'initialize' method
		self.districts = None
		self.buildings = None
		self.wonders = None
		self.projects = None

		self.cityStrategy = None
		self.cityCitizens = None
		self.greatWorks = None
		self.cityReligion = None
		self.cityTradingPosts = None
		self.cityTourism = None

	def __str__(self):
		return f'City "{self.name}" at {self.location}'

	def doFoundMessage(self):
		pass

	def initialize(self, simulation):
		self.gameTurnFoundedValue = simulation.currentTurn

		self.districts = CityDistricts(city=self)
		self.buildings = CityBuildings(city=self)
		self.wonders = CityWonders(city=self)
		self.projects = CityProjects(city=self)

		self.buildDistrict(district=DistrictType.cityCenter, location=self.location, simulation=simulation)

		if self.capitalValue:
			try:
				self.buildings.build(building=BuildingType.palace)
			except:
				print("cant build palace")

		self.cityStrategy = CityStrategyAI(city=self)
		self.cityCitizens = CityCitizens(city=self)
		self.greatWorks = CityGreatWorks(city=self)
		self.cityReligion = CityReligion(city=self)
		self.cityTradingPosts = CityTradingPosts(city=self)
		self.cityTourism = CityTourism(city=self)

		self.cityCitizens.initialize(simulation=simulation)

		if self.player.leader.civilization().ability() == CivilizationAbility.allRoadsLeadToRome:
			self.cityTradingPosts.buildTradingPost(leader=self.player.leader)

		if self.player.leader.ability() == LeaderAbility.trajansColumn:
			# All founded cities start with a free monument in the City Center.
			try:
				self.buildings.build(building=BuildingType.monument)
			except:
				pass

		# Update Proximity between this Player and all others
		for otherPlayer in simulation.players:
			if otherPlayer.leader != self.player.leader:
				if otherPlayer.isAlive() and self.player.diplomacyAI.hasMetWith(player=otherPlayer):
					# Fixme
					# Players do NOT have to know one another in order to calculate proximity.
					# Having this info available(even when they haven't met) can be useful
					self.player.doUpdateProximityTowards(otherPlayer, simulation)
					otherPlayer.doUpdateProximityTowards(self.player, simulation)

		self.doUpdateCheapestPlotInfluence(simulation=simulation)

		# discover the surrounding area
		for pointToDiscover in self.location.areaWithRadius(radius=2):
			if not simulation.valid(pointToDiscover):
				continue

			tile = simulation.tileAt(pointToDiscover)
			tile.discoverBy(self.player, simulation)

		# Every city automatically creates a road on its tile, which remains even 
		# if the feature is pillaged or the city is razed.
		tile = simulation.tileAt(self.location)
		tile.setRoute(RouteType.ancientRoad)

		# claim ownership for direct neighbors( if not taken)
		for pointToClaim in self.location.areaWithRadius(radius=1):
			tile = simulation.tileAt(pointToClaim)
			try:
				# FIXME
				tile.setOwner(player=self.player)
				tile.setWorkingCity(city=self)
			except Exception as e:
				raise Exception(f'cant set owner: {e}')

		# Founded cities start with eight additional tiles.
		if self.player.leader.civilization().ability() == CivilizationAbility.motherRussia:
			tiles = self.location.areaWithRadius(radius=2).points
			random.shuffle(tiles)
			additional = 0

			for pointToClaim in tiles:
				tile = simulation.tileAt(pointToClaim)

				if not tile.hasOwner() and additional < 8:
					try:           
						tile.setOwner(player=self.player)
						tile.setWorkingCity(city=self)

						additional += 1
					except:
						raise Exception('cant set owner')

		self.cityCitizens.doFound(simulation=simulation)

		self.player.updatePlots(simulation=simulation)

		if self.capitalValue:
			self.player.setCapitalCity(city=self, simulation=simulation)

		self.setPopulation(value=1, simulation=simulation)

	def featureProduction(self) -> float:
		return self.featureProductionValue

	def changeFeatureProduction(self, change: float):
		self.featureProductionValue += change

	def setFeatureProduction(self, value: float):
		self.featureProductionValue = value

	def buildDistrict(self, district: DistrictType, location: HexPoint, simulation):
		tile = simulation.tileAt(location)

		try:
			self.districts.build(district=district, location=location)
			self.updateEurekas(simulation)

			# moments
			if self.player.currentAge() == AgeType.normal and self.player.hasDedication(DedicationType.monumentality):
				if district.isSpecialty():
					self.player.addMoment(MomentType.dedicationTriggered, DedicationType.monumentality, simulation)

			# check quests
			# for quest in self.player.ownQuests(simulation):
			# 	if case .constructDistrict(type: let district) = quest.type {
			# 		if district == districtType && player.leader == quest.leader {
			# 			let cityStatePlayer = gameModel.cityStatePlayer(for: quest.cityState)
			# 			cityStatePlayer?.fulfillQuest(by: player.leader, in: gameModel)

			if district == DistrictType.preserve:
				# Initiate a Culture Bomb on adjacent unowned tiles
				for neighborPoint in location.neighbors():

					neighborTile = simulation.tileAt(neighborPoint)

					if not neighborTile.hasOwner() and not neighborTile.isWorked():
						self.doAcquirePlot(neighborPoint, simulation)

			if district == DistrictType.neighborhood:
				if not self.player.hasMoment(MomentType.firstNeighborhoodCompleted) and \
					not self.player.hasMoment(MomentType.worldsFirstNeighborhood):

					# check if someone else already had a built a neighborhood district
					if simulation.anyHasMoment(MomentType.worldsFirstNeighborhood):
						self.player.addMoment(MomentType.firstNeighborhoodCompleted, simulation)
					else:
						self.player.addMoment(MomentType.worldsFirstNeighborhood, simulation)

			if district == DistrictType.governmentPlaza:
				# governmentPlaza - Awards +1 Governor Title.
				self.player.addGovernorTitle()

			# send gossip
			if district.isSpecialty():
				simulation.sendGossip(type=GossipType.districtConstructed, meta=district, player=self.player)

			tile.buildDistrict(district)
			if district != DistrictType.cityCenter:
				# the city does not exist yet - so no update
				simulation.userInterface.refreshTile(tile)
		except Exception as e:
			raise Exception(f'cant build district: already build => {e}')

	def setPopulation(self, value, simulation):
		pass

	def doUpdateCheapestPlotInfluence(self, simulation):
		pass

	def doAcquirePlot(self, neighborPoint, simulation):
		pass

	def updateEurekas(self, simulation):
		pass

	def foodPerTurn(self, simulation) -> float:
		return 0.0

	def productionPerTurn(self, simulation) -> float:
		productionPerTurnValue: YieldValues = YieldValues(value=0.0, percentage=1.0)

		productionPerTurnValue += YieldValues(value=self._productionFromTiles(simulation))
		productionPerTurnValue += YieldValues(value=self._productionFromGovernmentType())
		productionPerTurnValue += YieldValues(value=self._productionFromDistricts(simulation))
		productionPerTurnValue += YieldValues(value=self._productionFromBuildings())
		productionPerTurnValue += YieldValues(value=self._productionFromTradeRoutes(simulation))
		productionPerTurnValue += YieldValues(value=self.featureProduction())

		# cap yields based on loyalty
		productionPerTurnValue += YieldValues(value=0.0, percentage=self.loyaltyState().yieldPercentage())

		return productionPerTurnValue.calc()

	def goldPerTurn(self, simulation) -> float:
		return 0.0

	def _productionFromTiles(self, simulation) -> float:
		hasHueyTeocalli = self.player.hasWonder(WonderType.hueyTeocalli, simulation)
		hasStBasilsCathedral = self.player.hasWonder(WonderType.stBasilsCathedral, simulation)
		productionValue: float = 0.0

		centerTile = simulation.tileAt(self.location)
		if centerTile is not None:

			productionValue += centerTile.yields(self.player, ignoreFeature=False).production

			# The yield of the tile occupied by the city center will be increased to 2 Food and 1 production, if either
			# was previously lower (before any bonus yields are applied).
			if productionValue < 1.0:
				productionValue = 1.0

		for point in self.cityCitizens.workingTileLocations():
			if self.cityCitizens.isWorkedAt(point):
				workedTile = simulation.tileAt(point)
				productionValue += workedTile.yields(self.player, ignoreFeature=False).production

				# city has petra: +2 Food, +2 Gold, and +1 Production
				# on all Desert tiles for this city(non - Floodplains).
				if workedTile.terrain() == TerrainType.desert and \
					not workedTile.hasFeature(FeatureType.floodplains) and \
					self.wonders.hasWonder(WonderType.petra):
					productionValue += 1.0

				# motherRussia
				if workedTile.terrain() == TerrainType.tundra and \
					self.player.leader.civilization().ability() == CivilizationAbility.motherRussia:
					# Tundra tiles provide + 1 Faith and +1 Production, in addition to their usual yields.
					productionValue += 1.0

				# stBasilsCathedral
				if workedTile.terrain() == TerrainType.tundra and hasStBasilsCathedral:
					# +1 Food, +1 Production, and +1 Culture on all Tundra tiles for this city.
					productionValue += 1.0

				# player has hueyTeocalli: +1 Food and +1 Production for each Lake tile in your empire.
				if workedTile.hasFeature(FeatureType.lake) and hasHueyTeocalli:
					productionValue += 1.0

				# city has chichenItza: +2 Culture and +1 Production to all Rainforest tiles for this city.
				if workedTile.hasFeature(FeatureType.rainforest) and self.hasWonder(WonderType.chichenItza):
					productionValue += 1.0

				# etemenanki - +2 Science and +1 Production to all Marsh tiles in your empire.
				if workedTile.hasFeature(FeatureType.marsh) and self.player.hasWonder(WonderType.etemenanki, simulation):
					productionValue += 1.0

				# etemenanki - +1 Science and +1 Production on all Floodplains tiles in this city.
				if workedTile.hasFeature(FeatureType.floodplains) and self.hasWonder(WonderType.etemenanki):
					productionValue += 1.0

				# godOfTheSea - 1 Production from Fishing Boats.
				if workedTile.improvement() == ImprovementType.fishingBoats and \
					self.player.religion.pantheon() == PantheonType.godOfTheSea:
					productionValue += 1.0

				# ladyOfTheReedsAndMarshes - +2 Production from Marsh, Oasis, and Desert Floodplains.
				if (workedTile.hasFeature(FeatureType.marsh) or workedTile.hasFeature(FeatureType.oasis) or \
				    workedTile.hasFeature(FeatureType.floodplains)) and \
					self.player.religion.pantheon() == PantheonType.ladyOfTheReedsAndMarshes:
					productionValue += 1.0

				# godOfCraftsmen - +1 Production and +1 Faith from improved Strategic resources.
				if self.player.religion.pantheon() == PantheonType.godOfCraftsmen:
					if workedTile.resourceFor(self.player).usage() == ResourceUsage.strategic and \
						workedTile.hasAnyImprovement():
						productionValue += 1.0

				# goddessOfTheHunt - +1 Food and +1 Production from Camps.
				if workedTile.improvement() == ImprovementType.camp and \
					self.player.religion.pantheon() == PantheonType.goddessOfTheHunt:
					productionValue += 1.0

				# auckland suzerain bonus
				# Shallow water tiles worked by Citizens provide +1 Production.
				# Additional +1 when you reach the Industrial Era
				if self.player.isSuzerainOf(CityState.auckland, simulation):
					if workedTile.terrain() == TerrainType.shore:
						productionValue += 1.0

					if self.player.currentEra() == EraType.industrial:
						productionValue += 1.0

				# johannesburg suzerain bonus
				# Cities receive + 1 Production for every improved resource type.
				# After researching Industrialization it becomes +2[Production] Production.
				if self.player.isSuzerainOf(CityState.johannesburg, simulation):
					if workedTile.hasAnyImprovement() and workedTile.resourceFor(self.player) != ResourceType.none:
						productionValue += 1.0

						if self.player.hasTech(TechType.industrialization):
							productionValue += 1.0

		return productionValue
