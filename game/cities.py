import random

from game.ai.cities import CityStrategyAI
from game.buildings import BuildingType
from game.civilizations import LeaderWeightList, CivilizationAbility, LeaderAbility, LeaderType
from game.districts import DistrictType
from map.base import HexPoint
from map.types import YieldList
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
		return 0.0

	def goldPerTurn(self, simulation) -> float:
		return 0.0
