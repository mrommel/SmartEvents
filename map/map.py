from typing import Optional

from game.cities import City
from game.districts import DistrictType
from game.governors import GovernorType, GovernorTitle
from game.players import Player
from game.states.builds import BuildType
from game.types import TechType, CivicType
from game.unitTypes import UnitMapType
from game.units import Unit
from game.wonders import WonderType
from map.base import HexPoint, HexDirection, Size, Array2D
from map.improvements import ImprovementType
from map.types import TerrainType, FeatureType, ResourceType, ClimateZone, RouteType, UnitMovementType, MapSize, \
	Tutorials, Yields, AppealLevel
from utils.base import WeightedBaseList, ExtendedEnum


class Tile:
	pass


class WeightedBuildList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for build in list(BuildType):
			self.setWeight(0.0, build)


# noinspection PyRedeclaration
class Tile:
	"""
		class that holds a single tile of a Map

		it has a TerrainType, FeatureType, ResourceType and a boolean value for being hilly (or not)
	"""

	def __init__(self, point: HexPoint, terrain: TerrainType):
		"""
			constructs a Tile from a TerrainType

			@param point: location of the tile
			@param terrain: TerrainType
		"""
		self.point = point
		self._terrainValue = terrain
		self._isHills = False
		self._featureValue = FeatureType.none
		self._resourceValue = ResourceType.none  # property is hidden
		self._resourceQuantity = 0
		self._riverValue = 0
		self._climateZone = ClimateZone.temperate
		self._route = RouteType.none
		self._improvementValue = ImprovementType.none
		self._improvementPillagedValue: bool = False
		self.continentIdentifier = None
		self.discovered = dict()
		self.visible = dict()
		self._cityValue = None
		self._districtValue = None
		self._wonderValue = WonderType.none
		self._owner = None
		self._workingCity = None
		self._buildProgressList = WeightedBuildList()

	def owner(self) -> Player:
		return self._owner

	def hasOwner(self) -> bool:
		return self._owner is not None

	def isWater(self):
		"""
			returns if this is a water tile
			:return: True, if this tile is a water tile, False otherwise
		"""
		return self._terrainValue.isWater()

	def isLand(self):
		"""
			returns if this is a land tile
			:return: True, if this tile is a land tile, False otherwise
		"""
		return self._terrainValue.isLand()

	def seeThroughLevel(self) -> int:
		# https://civilization.fandom.com/wiki/Sight_(Civ6)
		level = 0

		if self.isHills():
			level += 1

		if self.hasFeature(FeatureType.mountains):
			level += 3

		if self.hasFeature(FeatureType.forest) or self.hasFeature(FeatureType.rainforest):
			level += 1

		return level

	def resourceFor(self, player) -> ResourceType:
		"""
			returns the resource of this tile for player
			if no player is provided, no check for tech
			:return: resource of this if visible to player (if provided)
		"""
		if self._resourceValue != ResourceType.none:
			valid = True

			# check if already visible to player
			reveal_tech = self._resourceValue.revealTech()
			if reveal_tech is not None:
				if player is not None:
					if not player.has(reveal_tech):
						valid = False

			reveal_civic = self._resourceValue.revealCivic()
			if reveal_civic is not None:
				if player is not None:
					if not player.has(reveal_civic):
						valid = False

			if valid:
				return self._resourceValue

		return ResourceType.none

	def hasAnyResourceFor(self, player) -> bool:
		return self.resourceFor(player) != ResourceType.none

	def isImpassable(self, movement_ype):
		# start with terrain cost
		terrain_cost = self._terrainValue.movementCost(movement_ype)

		if terrain_cost == UnitMovementType.max:
			return True

		if self._featureValue != FeatureType.none:
			feature_cost = self._featureValue.movementCost(movement_ype)

			if feature_cost == UnitMovementType.max:
				return True

		return False

	def movementCost(self, movement_type: UnitMovementType, from_tile: Tile) -> int:
		"""
			cost to enter a terrain given the specified movement_type

			@param movement_type: type of movement
			@param from_tile: tile the unit comes from
			@return: movement cost to go from {from_tile} to this tile
		"""
		# start with terrain cost
		terrain_cost = self._terrainValue.movementCost(movement_type)

		if terrain_cost == UnitMovementType.max:
			return UnitMovementType.max.value

		# hills
		hill_costs = 1.0 if self.isHills() else 0.0

		# add feature costs
		feature_costs = 0.0
		if self.hasAnyFeature():
			feature_cost = self._featureValue.movementCost(movement_type)

			if feature_cost == UnitMovementType.max:
				return UnitMovementType.max.value

			feature_costs = feature_cost

		# add river crossing cost
		river_cost = 0.0
		if from_tile.isRiverToCrossTowards(self):
			river_cost = 3.0  # FIXME - river cost per movementType

		# https://civilization.fandom.com/wiki/Roads_(Civ6)
		if self.hasAnyRoute():
			terrain_cost = self._route.movementCost()

			if self._route != RouteType.ancientRoad:
				river_cost = 0.0

			hill_costs = 0.0
			feature_costs = 0.0

		return terrain_cost + hill_costs + feature_costs + river_cost

	def isRiverToCrossTowards(self, target: Tile) -> bool:
		if not self.isNeighborTo(target.point):
			return False

		direction = self.point.directionTowards(target.point)

		if direction == HexDirection.north:
			return self.isRiverInNorth()
		elif direction == HexDirection.northEast:
			return self.isRiverInNorthEast()
		elif direction == HexDirection.southEast:
			return self.isRiverInSouthEast()
		elif direction == HexDirection.south:
			return target.isRiverInNorth()
		elif direction == HexDirection.southWest:
			return target.isRiverInNorthEast()
		elif direction == HexDirection.northWest:
			return target.isRiverInSouthEast()

	def to_dict(self):
		return {
			'terrain': self._terrainValue.value,
			'isHills': self._isHills,
			'feature': self._featureValue.value,
			'resource': self._resourceValue.value,
			'resource_quantity': self._resourceQuantity
		}

	def isNeighborTo(self, candidate: HexPoint) -> bool:
		return self.point.distance(candidate) == 1

	def isRiverInNorth(self):
		"""river in north can flow from east or west direction"""
		# 0x01 => east
		# 0x02 => west
		return self._riverValue & 0x01 > 0 or self._riverValue & 0x02 > 0

	def isRiverInNorthEast(self):
		"""river in north-east can flow to northwest or southeast direction"""
		# 0x04 => northWest
		# 0x08 => southEast
		return self._riverValue & 0x04 > 0 or self._riverValue & 0x08 > 0

	def isRiverInSouthEast(self):
		"""river in south-east can flow to northeast or southwest direction"""
		# 0x16 => northWest
		# 0x32 => southEast
		return self._riverValue & 0x10 > 0 or self._riverValue & 0x20 > 0

	def hasAnyRoute(self):
		return self._route != RouteType.none

	def canHaveResource(self, grid, resource: ResourceType, ignore_latitude: bool = False) -> bool:

		if resource == ResourceType.none:
			return True

		# only one resource per tile
		if self._resourceValue != ResourceType.none:
			return False

		# no resources on natural wonders
		if self._featureValue.isNaturalWonder():
			return False

		# no resources on mountains
		if self._featureValue == FeatureType.mountains:
			return False

		if self._featureValue != FeatureType.none:
			if not resource.canBePlacedOnFeature(self._featureValue):
				return False

			if not resource.canBePlacedOnFeatureTerrain(self._terrainValue):
				return False
		else:
			# only checked if no feature
			if not resource.canBePlacedOnTerrain(self._terrainValue):
				return False

		if self._isHills:
			if not resource.canBePlacedOnHills():
				return False
		elif self.isFlatlands():
			if not resource.canBePlacedOnFlatlands():
				return False

		if grid.riverAt(self.point):
			if not resource.canBePlacedOnRiverSide():
				return False

		return True

	def isFlatlands(self):
		if not self._terrainValue.isLand():
			return False

		if self._featureValue == FeatureType.mountains or self._featureValue == FeatureType.mountEverest or self._featureValue == FeatureType.mountKilimanjaro:
			return False

		return True

	def isDiscoveredBy(self, player) -> bool:
		return self.discovered.get(str(player.leader), False)

	def discoverBy(self, player, simulation):
		if not self.discovered:
			self.discovered[str(player.leader)] = True

			# tutorial
			if simulation.tutorial() == Tutorials.movementAndExploration and player.isHuman():
				numberOfDiscoveredPlots = player.numberOfDiscoveredPlots(simulation)
				if numberOfDiscoveredPlots >= Tutorials.tilesToDiscover():
					print(f'tutorial finished: MOVEMENT_AND_EXPLORATION')
	#                     gameModel?.userInterface?.finish(tutorial: .movementAndExploration)
	#                     gameModel?.enable(tutorial: .none)

	def isVisibleTo(self, player) -> bool:
		return self.visible.get(str(player.leader), False)

	def isVisibleToAny(self):
		for visibleToPlayer in self.visible.values():
			if visibleToPlayer:
				return True

		return False

	def sightBy(self, player):
		self.visible[str(player.leader)] = True

	def canSeeTile(self, otherTile, player, range: int, hasSentry: bool, simulation) -> bool:
		if otherTile.point == self.point:
			return True

		# wrappedX: Int = gameModel.wrappedX() ? gameModel.mapSize().width(): -1
		if self.point.isNeighborOf(otherTile.point):
			return True

		seeThruLevel = 2 if hasSentry else 1

		distance = self.point.distance(otherTile.point)
		if distance <= range:
			tmpPoint = self.point

			while not tmpPoint.isNeighborOf(otherTile.point):
				direction = tmpPoint.directionTowards(otherTile.point)
				tmpPoint = tmpPoint.neighbor(direction)
				# tmpPoint = gameModel.wrap(point: tmpPoint)

				tmpTile = simulation.tileAt(tmpPoint)
				if tmpTile.seeThroughLevel() > seeThruLevel:
					return False

			return True

		return False

	def concealTo(self, player):
		self.visible[str(player.leader)] = False

	def isCity(self) -> bool:
		return self._cityValue is not None

	def setCity(self, city):
		self._cityValue = city

	def productionFromFeatureRemoval(self, buildType: BuildType) -> int:
		if not self.hasAnyFeature():
			return 0

		production = 0

		for feature in list(FeatureType):
			if self.hasFeature(feature):
				if not buildType.canRemove(feature):
					return 0

				production += buildType.productionFromRemovalOf(feature)

		return 0

	def terrain(self):
		return self._terrainValue

	def setTerrain(self, terrain: TerrainType):
		self._terrainValue = terrain

	def hasAnyFeature(self) -> bool:
		return self._featureValue != FeatureType.none

	def hasFeature(self, feature: FeatureType) -> bool:
		return self._featureValue == feature

	def feature(self):
		return self._featureValue

	def setFeature(self, feature: FeatureType):
		self._featureValue = feature

	def isHills(self):
		return self._isHills

	def setHills(self, hills: bool):
		self._isHills = hills

	def hasAnyImprovement(self) -> bool:
		return self._improvementValue != ImprovementType.none

	def hasImprovement(self, improvement: ImprovementType) -> bool:
		return self._improvementValue == improvement

	def route(self) -> RouteType:
		return self._route

	def setRoute(self, route: RouteType):
		self._route = route

	def improvement(self):
		return self._improvementValue

	def setImprovement(self, improvement: ImprovementType):
		self._improvementValue = improvement

	def hasAnyWonder(self) -> bool:
		return self._wonderValue != WonderType.none

	def hasDistrict(self, district: DistrictType) -> bool:
		return self._districtValue == district

	def buildDistrict(self, district: DistrictType):
		self._districtValue = district

	def setOwner(self, player):
		self._owner = player

	def setWorkingCity(self, city):
		self._workingCity = city

	def yields(self, player, ignoreFeature: bool):
		returnYields = Yields(food=0, production=0, gold=0, science=0)

		baseYields = self._terrainValue.yields()
		returnYields += baseYields

		if self._isHills and self._terrainValue.isLand():
			returnYields += Yields(food=0, production=1, gold=0, science=0)

		if ignoreFeature == False and self._featureValue != FeatureType.none:
			returnYields += self._featureValue.yields()

		visibleResource = self.resourceFor(player)
		returnYields += visibleResource.yields()

		if self._improvementValue is not None and self._improvementValue != ImprovementType.none and \
			not self.isImprovementPillaged():
			returnYields += self._improvementValue.yieldsFor(player)

		return returnYields

	def isImprovementPillaged(self) -> bool:
		return self._improvementPillagedValue

	def setImprovementPillaged(self, value: bool):
		self._improvementPillagedValue = value

	def changeBuildProgressOf(self, build: BuildType, change: int, player: Player, simulation) -> bool:
		"""Returns true if build finished ..."""
		finished = False

		if change < 0:
			raise Exception(f'change must be bigger than zero but is {change}')

		if change > 0:
			self._buildProgressList.addWeight(change, build)

			if self.buildProgressFor(build) >= build.buildTimeOn(self):
				self._buildProgressList.setWeight(0, build)

				# Constructed Improvement
				if build.improvement() is not None and build.improvement() != ImprovementType.none:
					# eurekas
					self.updateEurekas(build.improvement(), player, simulation)

					self.setImprovement(build.improvement())

				# Constructed Route
				if build.route() is not None:
					self.setRoute(build.route())

				# Remove Feature
				if self.hasAnyFeature():
					if not build.keepsFeature(self.feature()) and build.canRemoveFeature(self.feature()):

						production, city = self.featureProductionBy(build, player)

						if production > 0:
							if city is None:
								raise Exception("no city found")

							city.changeFeatureProduction(float(production))

							if city.player.isHuman():
								# simulation.userInterface.showTooltip(at: self.point,
								# 	type:.clearedFeature(feature: self.feature(), production: production, cityName: city.name),
								# 	delay: 3)
								pass

						self.setFeature(FeatureType.none)

				# Repairing a Pillaged Tile
				if build.willRepair():
					if self.isImprovementPillaged():
						self.setImprovementPillaged(False)
					elif self.isRoutePillaged():
						self.setRoutePillaged(False)

				if build.willRemoveRoute():
					self.setRoute(RouteType.none)

				finished = True

		return finished

	def buildProgressFor(self, build: BuildType) -> int:
		return int(self._buildProgressList.weight(build))

	def updateEurekas(self, improvement: ImprovementType, player, simulation):
		# Techs
		# -----------------------------------------------------

		# Masonry - To Boost: Build a quarry
		if not player.techs.eurekaTriggeredFor(TechType.masonry):
			if improvement == ImprovementType.quarry:
				player.techs.triggerEurekaFor(TechType.masonry, simulation)

		# Wheel - To Boost: Mine a resource
		if not player.techs.eurekaTriggeredFor(TechType.wheel):
			if improvement == ImprovementType.mine and self.hasAnyResourceFor(player):
				player.techs.triggerEurekaFor(TechType.wheel, simulation)

		# Irrigation - To Boost: Farm a resource
		if not player.techs.eurekaTriggeredFor(TechType.irrigation):
			if improvement == ImprovementType.farm and self.hasAnyResourceFor(player):
				player.techs.triggerEureka(TechType.irrigation, simulation)

		# Horseback Riding - To Boost: Build a pasture
		if not player.techs.eurekaTriggeredFor(TechType.horsebackRiding):
			if improvement == ImprovementType.pasture:
				player.techs.triggerEureka(TechType.horsebackRiding, simulation)

		# Iron Working - To Boost: Build an Iron Mine
		if not player.techs.eurekaTriggeredFor(TechType.ironWorking):
			if improvement == ImprovementType.mine and self._resourceValue == ResourceType.iron:
				player.techs.triggerEurekaFor(TechType.ironWorking, simulation)

		# Apprenticeship - To Boost: Build 3 mines
		if not player.techs.eurekaTriggeredFor(TechType.apprenticeship):
			if improvement == ImprovementType.mine:
				player.techs.changeEurekaValue(TechType.apprenticeship, change=1)

				if player.techs.eurekaValue(TechType.apprenticeship) >= 3:
					player.techs.triggerEurekaFor(TechType.apprenticeship, simulation)

		# Ballistics - To Boost: Build 2 Forts
		if not player.techs.eurekaTriggeredFor(TechType.ballistics):
			if improvement == ImprovementType.fort:
				player.techs.changeEurekaValue(TechType.ballistics, change=1)

				if player.techs.eurekaValue(TechType.ballistics) >= 2:
					player.techs.triggerEurekaFor(TechType.ballistics)

		# Rifling - To Boost: Build a Niter Mine
		if not player.techs.eurekaTriggeredFor(TechType.rifling):
			if improvement == ImprovementType.mine and self._resourceValue == ResourceType.niter:
				player.techs.triggerEurekaFor(TechType.rifling)

		# Civics
		# -----------------------------------------------------

		# Craftsmanship - To Boost: Improve 3 tiles
		if not player.civics.inspirationTriggeredFor(CivicType.craftsmanship):
			# increase for any improvement
			player.civics.changeInspirationValueFor(CivicType.craftsmanship, change=1)

			if player.civics.inspirationValueOf(CivicType.craftsmanship) >= 3:
				player.civics.triggerInspirationFor(CivicType.craftsmanship, simulation)

		return

	def appeal(self, simulation) -> int:
		# Mountain tiles have a base Appeal of Breathtaking (4),
		# which is unaffected by surrounding features.
		if self._featureValue == FeatureType.mountains:
			return 4

		# Natural wonder tiles have a base Appeal of Breathtaking (5),
		# which is also unaffected by surrounding features.
		if self._featureValue.isNaturalWonder():
			return 5

		appealValue: int = 0
		nextRiverOrLake: bool = simulation.riverAt(self.point)
		neighborCliffsOfDoverOrUluru: bool = False
		neighborPillagedCount: int = 0
		neighborBadFeaturesCount: int = 0
		neighborBadImprovementsCount: int = 0
		neighborBadDistrictsCount: int = 0
		neighborGoodTerrainsCount: int = 0
		neighborGoodDistrictsCount: int = 0
		neighborWondersCount: int = 0
		neighborNaturalWondersCount: int = 0

		for neighbor in self.point.neighbors():

			neighborTile = simulation.tileAt(neighbor)

			if neighborTile.hasFeature(FeatureType.lake):
				nextRiverOrLake = True

			if neighborTile.hasFeature(FeatureType.rainforest) or \
				neighborTile.hasFeature(FeatureType.marsh) or \
				neighborTile.hasFeature(FeatureType.floodplains):
				neighborBadFeaturesCount += 1

			if neighborTile.hasFeature(FeatureType.cliffsOfDover) or neighborTile.hasFeature(FeatureType.uluru):
				neighborCliffsOfDoverOrUluru = True

			if neighborTile.feature().isNaturalWonder() and \
				not (neighborTile.hasFeature(FeatureType.cliffsOfDover) or neighborTile.hasFeature(FeatureType.uluru)):
				neighborNaturalWondersCount += 1

			if neighborTile.isImprovementPillaged():
				neighborPillagedCount += 1

			if neighborTile.hasImprovement(ImprovementType.barbarianCamp) or \
				neighborTile.hasImprovement(ImprovementType.mine) or \
				neighborTile.hasImprovement(ImprovementType.quarry) or \
				neighborTile.hasImprovement(ImprovementType.oilWell):

				neighborBadImprovementsCount += 1

			if neighborTile.hasDistrict(DistrictType.industrialZone) or \
				neighborTile.hasDistrict(DistrictType.encampment) or \
				neighborTile.hasDistrict(DistrictType.spaceport):  # neighborTile.hasDistrict(DistrictType.aerodrome) or

				neighborBadDistrictsCount += 1

			if simulation.isCoastalAt(neighbor) or \
				neighborTile.hasFeature(FeatureType.mountains) or \
				neighborTile.hasFeature(FeatureType.forest) or \
				neighborTile.hasFeature(FeatureType.oasis):

				neighborGoodTerrainsCount += 1

			if neighborTile.hasAnyFeature() and not neighborTile.hasAnyImprovement():
				# check for governor effects of reyna
				city = neighborTile.workingCity()
				if city is not None and city.governor() is not None:
					if city.governor().type == GovernorType.reyna:
						# forestryManagement - Tiles adjacent to unimproved features receive +1 Appeal in this city.
						if city.governor().hasTitle(GovernorTitle.forestryManagement):
							neighborGoodTerrainsCount += 1

			if neighborTile.hasAnyWonder():
				neighborWondersCount += 1

			if neighborTile.hasDistrict(DistrictType.holySite) or \
				neighborTile.hasDistrict(DistrictType.theaterSquare) or \
				neighborTile.hasDistrict(DistrictType.entertainmentComplex) or \
				neighborTile.hasDistrict(DistrictType.waterPark) or \
				neighborTile.hasDistrict(DistrictType.preserve):  # dam canal

				neighborGoodDistrictsCount += 1

		# +2 for each adjacent Sphinx (in Gathering Storm), Ice Hockey Rink, City Park, or natural wonder (except the
		# ones that provide a larger bonus).
		appealValue += neighborNaturalWondersCount * 2

		# +1 for each adjacent Holy Site, Theater Square, Entertainment Complex, Water Park, Dam, Canal, Preserve,
		# or wonder.
		appealValue += neighborGoodDistrictsCount
		appealValue += neighborWondersCount

		# +1 for each adjacent Sphinx (in vanilla Civilization VI and Rise and Fall), Château, Pairidaeza, Golf Course,
		# Nazca Line, or Rock-Hewn Church.
		#

		# +1 for each adjacent Mountain, Coast, Woods, or Oasis.
		appealValue += neighborGoodTerrainsCount

		# -1 for each adjacent barbarian outpost, Mine, Quarry, Oil Well, Offshore Oil Rig, Airstrip, Industrial Zone,
		# Encampment, Aerodrome, or Spaceport.
		appealValue -= neighborBadImprovementsCount
		appealValue -= neighborBadDistrictsCount

		# -1 for each adjacent Rainforest, Marsh, or Floodplain.
		appealValue -= neighborBadFeaturesCount

		# -1 for each adjacent pillaged tile.
		appealValue -= neighborPillagedCount

		# +1 if the tile is next to a River or Lake.
		if nextRiverOrLake:
			appealValue += 1

		# +4 if adjacent to the Cliffs of Dover (in Gathering Storm) or Uluru.
		if neighborCliffsOfDoverOrUluru:
			appealValue += 4

		return appealValue

	def appealLevel(self, simulation) -> AppealLevel:
		return AppealLevel.fromAppeal(self.appeal(simulation))


class TileStatistics:
	def __init__(self):
		self.ocean = 0.0
		self.shore = 0.0
		self.plains = 0.0
		self.grass = 0.0
		self.desert = 0.0
		self.tundra = 0.0
		self.snow = 0.0

	def normalize(self, factor):
		self.ocean /= factor
		self.shore /= factor
		self.plains /= factor
		self.grass /= factor
		self.desert /= factor
		self.tundra /= factor
		self.snow /= factor


class Continent:
	def __init__(self, identifier: int, name: str, grid):
		self.identifier = identifier
		self.name = name
		self.grid = grid
		self.points = []
		self.continentType = ContinentType.none

	def add(self, point):
		self.points.append(point)

	def __str__(self):
		return f'Content: {self.identifier} {self.name}'


class ContinentType(ExtendedEnum):
	none = 'none'

	africa = 'africa'
	AMASIA = 2
	AMERICA = 3
	ANTARCTICA = 4
	ARCTICA = 5
	ASIA = 6
	ASIAMERICA = 7
	ATLANTICA = 8
	ATLANTIS = 9
	AUSTRALIA = 10
	AVALONIA = 11
	AZANIA = 12
	BALTICA = 13
	CIMMERIA = 14
	COLUMBIA = 15
	CONGOCRATON = 16
	EURAMERICA = 17
	EUROPE = 18
	GONDWANA = 19
	KALAHARIA = 20
	KAZAKHSTANIA = 21
	KERNORLAND = 22
	KUMARIKANDAM = 23
	LAURASIA = 24
	LAURENTIA = 25
	LEMURIA = 26
	MU = 27
	NENA = 28
	NORTH_AMERICA = 29
	NOVO_PANGAEA = 30
	NUNA = 31
	PANGAEA = 32
	PANGAEA_ULTIMA = 33
	PANNOTIA = 34
	RODINIA = 35
	SIBERIA = 36
	SOUTH_AMERICA = 37
	TERRA_AUSTRALIS = 38
	UR = 39
	VAALBARA = 40
	VENDIAN = 41
	ZEALANDIA = 42


class Map:
	def __init__(self, width, height=None):
		if isinstance(width, Size) and height is None:
			size = width
			self.width = size.width
			self.height = size.height
		elif isinstance(width, int) and isinstance(height, int):
			self.width = width
			self.height = height
		else:
			raise AttributeError(f'Map with wrong attributes: {width} / {height}')

		self.tiles = Array2D(self.width, self.height)

		# create a unique Tile per place
		for y in range(self.height):
			for x in range(self.width):
				self.tiles.values[y][x] = Tile(HexPoint(x, y), TerrainType.ocean)

		self._cities = []
		self._units = []
		self.startLocations = []
		self.continents = []

	def valid(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return 0 <= hex_point.x < self.width and 0 <= hex_point.y < self.height
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return 0 <= x < self.width and 0 <= y < self.height
		else:
			raise AttributeError(f'Map.valid with wrong attributes: {x_or_hex} / {y}')

	def points(self):
		point_arr = []

		for x in range(self.width):
			for y in range(self.height):
				point_arr.append(HexPoint(x, y))

		return point_arr

	def tileAt(self, x_or_hex, y=None) -> Optional[Tile]:
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex

			if not self.valid(hex_point.x, hex_point.y):
				return None

			return self.tiles.values[hex_point.y][hex_point.x]
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex

			if not self.valid(x, y):
				return None

			return self.tiles.values[y][x]
		else:
			raise AttributeError(f'Map.tileAt with wrong attributes: {x_or_hex} / {y}')

	def terrainAt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex

			if not self.valid(hex_point.x, hex_point.y):
				return None

			return self.tiles.values[hex_point.y][hex_point.x].terrain()
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex

			if not self.valid(x, y):
				return None

			return self.tiles.values[y][x].terrain()
		else:
			raise AttributeError(f'Map.terrainAt with wrong attributes: {x_or_hex} / {y}')

	def modifyTerrainAt(self, x_or_hex, y_or_terrain, terrain=None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_terrain, TerrainType) and terrain is None:
			hex_point = x_or_hex
			terrain_type = y_or_terrain
			self.tiles.values[hex_point.y][hex_point.x].setTerrain(terrain_type)
		elif isinstance(x_or_hex, int) and isinstance(y_or_terrain, int) and isinstance(terrain, TerrainType):
			x = x_or_hex
			y = y_or_terrain
			terrain_type = terrain
			self.tiles.values[y][x].setTerrain(terrain_type)
		else:
			raise AttributeError(f'Map.modifyTerrainAt with wrong attributes: {x_or_hex} / {y_or_terrain} / {terrain}')

	def isHillsAtt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].ishills()
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].ishills()
		else:
			raise AttributeError(f'Map.isHillsAtt with wrong attributes: {x_or_hex} / {y}')

	def modifyIsHillsAt(self, x_or_hex, y_or_is_hills, is_hills=None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_is_hills, bool) and is_hills is None:
			hex_point = x_or_hex
			is_hills = y_or_is_hills
			self.tiles.values[hex_point.y][hex_point.x].setHills(is_hills)
		elif isinstance(x_or_hex, int) and isinstance(y_or_is_hills, int) and isinstance(is_hills, bool):
			x = x_or_hex
			y = y_or_is_hills
			self.tiles.values[y][x].setHills(is_hills)
		else:
			raise AttributeError(
				f'Map.modifyIsHillsAt with wrong attributes: {x_or_hex} / {y_or_is_hills} / {is_hills}')

	def featureAt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x].feature()
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x].feature()
		else:
			raise AttributeError(f'Map.featureAt with wrong attributes: {x_or_hex} / {y}')

	def modifyFeatureAt(self, x_or_hex, y_or_terrain, feature=None):
		if isinstance(x_or_hex, HexPoint) and isinstance(y_or_terrain, FeatureType) and feature is None:
			hex_point = x_or_hex
			feature_type = y_or_terrain
			self.tiles.values[hex_point.y][hex_point.x].setFeature(feature_type)
		elif isinstance(x_or_hex, int) and isinstance(y_or_terrain, int) and isinstance(feature, TerrainType):
			x = x_or_hex
			y = y_or_terrain
			feature_type = feature
			self.tiles.values[y][x].setFeature(feature_type)
		else:
			raise AttributeError(f'Map.modifyTerrainAt with wrong attributes: {x_or_hex} / {y_or_terrain} / {feature}')

	def riverAt(self, x_or_hex, y=None) -> bool:
		"""@return True, if this tile has a river - False otherwise"""
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self.tiles.values[hex_point.y][hex_point.x]._riverValue > 0
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self.tiles.values[y][x]._riverValue > 0
		else:
			raise AttributeError(f'Map.riverAt with wrong attributes: {x_or_hex} / {y}')

	def isFreshWaterAt(self, x_or_hex, y=None):
		if isinstance(x_or_hex, HexPoint) and y is None:
			hex_point = x_or_hex
			return self._isFreshWaterAt(hex_point.x, hex_point.y)
		elif isinstance(x_or_hex, int) and isinstance(y, int):
			x = x_or_hex
			return self._isFreshWaterAt(x, y)
		else:
			raise AttributeError(f'Map.riverAt with wrong attributes: {x_or_hex} / {y}')

	def _isFreshWaterAt(self, x, y):
		tile = self.tileAt(x, y)

		if tile.terrain().isWater() or tile.isImpassable(UnitMovementType.walk):
			return False

		if self.riverAt(x, y):
			return True

		for neighbors in HexPoint(x, y).neighbors():
			loopTile = self.tileAt(neighbors)

			if loopTile is None:
				continue

			if loopTile._featureValue == FeatureType.lake:
				return True

			if loopTile._featureValue == FeatureType.oasis:
				return True

		return False

	def capitalOf(self, player: Player) -> City:
		item = next((city for city in self._cities if city.player.leader == player.leader and city.capitalValue), None)
		return item

	def unitsOf(self, player: Player) -> [Unit]:
		return list(filter(lambda unit: unit.player.leader == player.leader, self._units))

	def unitsAt(self, location) -> [Unit]:
		return list(filter(lambda unit: unit.location == location, self._units))

	def unitAt(self, location, unitMapType: UnitMapType) -> Optional[Unit]:
		return next(filter(lambda unit: unit.location == location and unit.unitMapType() == unitMapType, self._units), None)

	def addUnit(self, unit):
		self._units.append(unit)

	def removeUnit(self, unit):
		self._units = list(filter(lambda loopUnit: unit.location == loopUnit.location and unit.unitType == loopUnit.unitType, self._units))

	def cityAt(self, location: HexPoint) -> Optional[City]:
		return next(filter(lambda city: city.location == location, self._cities), None)

	def citiesOf(self, player) -> [City]:
		return list(filter(lambda city: city.player.leader == player.leader, self._cities))

	def addCity(self, city: City, simulation):
		self._cities.append(city)

		tile = self.tileAt(city.location)
		tile.setCity(city)

		self._sightCity(city, simulation)

	def _sightCity(self, city, simulation):
		for pt in city.location.areaWithRadius(3):
			tile = self.tileAt(pt)
			tile.discoverBy(city.player, simulation)
			tile.sightBy(city.player)

	def tileStatistics(self, grid_point: HexPoint, radius: int):

		valid_tiles = 0.0
		stats = TileStatistics()

		for pt in grid_point.areaWithRadius(radius):
			if not self.valid(pt):
				continue

			tile = self.tileAt(pt)

			if tile.terrain == TerrainType.ocean:
				stats.ocean += 1
			elif tile.terrain == TerrainType.shore:
				stats.shore += 1
			elif tile.terrain == TerrainType.plains:
				stats.plains += 1
			elif tile.terrain == TerrainType.grass:
				stats.grass += 1
			elif tile.terrain == TerrainType.desert:
				stats.desert += 1
			elif tile.terrain == TerrainType.tundra:
				stats.tundra += 1
			elif tile.terrain == TerrainType.snow:
				stats.snow += 1

			valid_tiles += 1.0

		# normalize
		stats.normalize(valid_tiles)

		return stats

	def canHaveFeature(self, grid_point: HexPoint, feature_type: FeatureType):
		tile = self.tileAt(grid_point)

		# check tile itself (no surroundings)
		if feature_type.isPossibleOn(tile):
			# additional check for flood plains
			if feature_type == FeatureType.floodplains:
				return self.riverAt(grid_point)

			#  no natural wonders on resources
			if feature_type.isNaturalWonder() and tile.hasAnyResourceFor(None):
				return False

			return True

		return False

	def bestMatchingSize(self) -> MapSize:
		bestDelta = 100000
		bestMapSize = MapSize.tiny

		for mapSize in list(MapSize):
			delta = abs((mapSize.size().width * mapSize.size().height) - (self.width * self.height))
			if delta < bestDelta:
				bestDelta = delta
				bestMapSize = mapSize

		return bestMapSize

	def to_dict(self):
		return {
			'width': self.width,
			'height': self.height,
			'tiles': self.tiles.to_dict()
		}

	def isCoastalAt(self, point: HexPoint):
		terrain = self.tileAt(point).terrain()
		# we are only coastal, if we are on land
		if terrain.isWater():
			return False

		for neighborPoint in point.neighbors():
			neighborTile = self.tileAt(neighborPoint)

			if neighborTile is None:
				continue

			neighborTerrain = neighborTile.terrain()
			if neighborTerrain.isWater():
				return True

		return False

	def continent(self, identifier: int) -> Continent:
		return next((continent for continent in self.continents if continent.identifier == identifier), None)

	#def continentAt(self, location: HexPoint) -> Continent:
	#	tile = self.tileAt(location)

	def setContinent(self, continent: Continent, location: HexPoint):
		tile = self.tileAt(location)
		tile.continentIdentifier = continent.identifier

