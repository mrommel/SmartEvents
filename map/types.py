from builtins import float
from enum import Enum
from typing import Optional

from game.types import TechType, CivicType
from map.base import ExtendedEnum, Size
from utils.base import InvalidEnumError, WeightedBaseList
from utils.translation import gettext_lazy as _


class UnitDomainType(ExtendedEnum):
	none = 'none'

	sea = 'sea'
	land = 'land'
	air = 'air'
	immobile = 'immobile'


class MapAge(Enum):
	young = 'young'
	normal = 'normal'
	old = 'old'


class MapSizeData:
	def __init__(self, name: str, size: Size, numPlayers: int, numberOfCityStates: int):
		self.name = name
		self.size = size
		self.numPlayers = numPlayers
		self.numberOfCityStates = numberOfCityStates


class MapSize(Enum):
	duel = 'duel'
	tiny = 'tiny'
	small = 'small'
	standard = 'standard'

	def name(self) -> str:
		return self._data().name

	def size(self) -> Size:
		return self._data().size

	def numberOfPlayers(self):
		return self._data().numPlayers

	def numberOfCityStates(self):
		return self._data().numberOfCityStates

	def _data(self):
		if self == MapSize.duel:
			return MapSizeData(
				name=_('TXT_KEY_MAP_SIZE_DUEL_NAME'),
				size=Size(32, 22),
				numPlayers=2,
				numberOfCityStates=3
			)
		elif self == MapSize.tiny:
			return MapSizeData(
				name=_('TXT_KEY_MAP_SIZE_TINY_NAME'),
				size=Size(42, 32),
				numPlayers=3,
				numberOfCityStates=6
			)
		elif self == MapSize.small:
			return MapSizeData(
				name=_('TXT_KEY_MAP_SIZE_SMALL_NAME'),
				size=Size(52, 42),
				numPlayers=4,
				numberOfCityStates=9
			)
		elif self == MapSize.standard:
			return MapSizeData(
				name=_('TXT_KEY_MAP_SIZE_STANDARD_NAME'),
				size=Size(62, 52),
				numPlayers=6,
				numberOfCityStates=12
			)

		raise ValueError(f'Not handled enum: {self}')


class MapTypeData:
	def __init__(self, name: str):
		self.name = name


class MapType(Enum):
	empty = 'empty'
	earth = 'earth'
	pangaea = 'pangaea'
	continents = 'continents'
	archipelago = 'archipelago'

	def name(self) -> str:
		return self._data().name

	def _data(self) -> MapTypeData:
		if self == MapType.empty:
			return MapTypeData(
				name=_('TXT_KEY_MAP_TYPE_EMPTY_NAME')
			)
		elif self == MapType.earth:
			return MapTypeData(
				name=_('TXT_KEY_MAP_TYPE_EARTH_NAME')
			)
		elif self == MapType.pangaea:
			return MapTypeData(
				name=_('TXT_KEY_MAP_TYPE_PANGAEA_NAME')
			)
		elif self == MapType.continents:
			return MapTypeData(
				name=_('TXT_KEY_MAP_TYPE_CONTINENTS_NAME')
			)
		elif self == MapType.archipelago:
			return MapTypeData(
				name=_('TXT_KEY_MAP_TYPE_ARCHIPELAGO_NAME')
			)


class Yields:
	def __init__(self, food: float, production: float, gold: float, science: float = 0.0, culture: float = 0.0,
	             faith: float = 0.0, housing: float = 0.0, appeal: float = 0.0):
		self.food = food
		self.production = production
		self.gold = gold
		self.science = science
		self.culture = culture
		self.faith = faith
		self.housing = housing
		self.appeal = appeal

	def __iadd__(self, other):
		if isinstance(other, Yields):
			self.food += other.food
			self.production += other.production
			self.gold += other.gold
			self.science += other.science
			self.culture += other.culture
			self.faith += other.faith
			self.housing += other.housing
			self.appeal += other.appeal

			return self
		else:
			raise Exception(f'type is not accepted {type(other)}')


class YieldType(ExtendedEnum):
	none = 'none'

	food = 'food'
	production = 'production'
	gold = 'gold'
	science = 'science'
	culture = 'culture'
	faith = 'faith'


class YieldList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for yieldType in list(YieldType):
			self[yieldType] = 0


class TerrainData:
	def __init__(self, name: str, yields: Yields, isWater: bool, domain: UnitDomainType, antiquityPriority: int):
		self.name = name
		self.yields = yields
		self.isWater = isWater
		self.domain = domain
		self.antiquityPriority = antiquityPriority


class TerrainType(ExtendedEnum):
	desert = 'desert'
	grass = 'grass'
	ocean = 'ocean'
	plains = 'plains'
	shore = 'shore'
	snow = 'snow'
	tundra = 'tundra'

	land = 'land'
	sea = 'sea'

	def name(self) -> str:
		return self._data().name

	def isWater(self):
		return self == TerrainType.sea or self == TerrainType.ocean or self == TerrainType.shore

	def isLand(self):
		return not self.isWater()

	def domain(self) -> UnitDomainType:
		return self._data().domain

	def _data(self) -> TerrainData:
		if self == TerrainType.desert:
			return TerrainData(
				name='Desert',
				yields=Yields(food=0, production=0, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=5
			)
		elif self == TerrainType.grass:
			return TerrainData(
				name='Grassland',
				yields=Yields(food=2, production=0, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=2
			)
		elif self == TerrainType.ocean:
			return TerrainData(
				name='Ocean',
				yields=Yields(food=1, production=0, gold=0, science=0),
				isWater=True,
				domain=UnitDomainType.sea,
				antiquityPriority=0
			)
		elif self == TerrainType.plains:
			return TerrainData(
				name='Plains',
				yields=Yields(food=1, production=1, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=2
			)
		elif self == TerrainType.shore:
			return TerrainData(
				name='Shore',
				yields=Yields(food=1, production=0, gold=1, science=0),
				isWater=True,
				domain=UnitDomainType.sea,
				antiquityPriority=2
			)
		elif self == TerrainType.snow:
			return TerrainData(
				name='Snow',
				yields=Yields(food=0, production=0, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=1
			)
		elif self == TerrainType.tundra:
			return TerrainData(
				name='Tundra',
				yields=Yields(food=1, production=0, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=3
			)

		elif self == TerrainType.land:
			return TerrainData(
				name='',
				yields=Yields(food=0, production=0, gold=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=0
			)
		elif self == TerrainType.sea:
			return TerrainData(
				name='',
				yields=Yields(food=0, production=0, gold=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=0
			)

		raise InvalidEnumError(self)

	def movementCost(self, movement_type):
		if movement_type == UnitMovementType.immobile:
			return UnitMovementType.max

		if movement_type == UnitMovementType.swim:
			if self == TerrainType.ocean:
				return 1.5

			if self == TerrainType.shore:
				return 1.0

			return UnitMovementType.max

		if movement_type == UnitMovementType.swimShallow:
			if self == TerrainType.shore:
				return 1.0

			return UnitMovementType.max

		if movement_type == UnitMovementType.walk:
			if self == TerrainType.plains:
				return 1.0

			if self == TerrainType.grass:
				return 1.0

			if self == TerrainType.desert:
				return 1.0

			if self == TerrainType.tundra:
				return 1.0

			if self == TerrainType.snow:
				return 1.0

			return UnitMovementType.max

	def textures(self):
		if self == TerrainType.desert:
			return ['terrain_desert@3x.png']

		if self == TerrainType.grass:
			return ['terrain_grass@3x.png']

		if self == TerrainType.ocean:
			return ['terrain_ocean@3x.png']

		if self == TerrainType.plains:
			return ['terrain_plains@3x.png']

		if self == TerrainType.shore:
			return ['terrain_shore@3x.png']

		if self == TerrainType.snow:
			return ['terrain_snow@3x.png']

		if self == TerrainType.tundra:
			return ['terrain_tundra@3x.png', 'terrain_tundra2@3x.png', 'terrain_tundra3@3x.png']

		return []

	def yields(self) -> Yields:
		return self._data().yields


class FeatureData:
	def __init__(self, name, yields, is_wonder):
		self.name = name
		self.yields = yields
		self.is_wonder = is_wonder


class FeatureType(ExtendedEnum):
	none = 'none'
	atoll = 'atoll'
	fallout = 'fallout'
	floodplains = 'floodplains'
	forest = 'forest'
	ice = 'ice'
	marsh = 'marsh'
	mountains = 'mountains'
	oasis = 'oasis'
	pine = 'pine'  # special case for pine forest
	rainforest = 'rainforest'
	reef = 'reef'
	lake = 'lake'
	volcano = 'volcano'

	# natural wonder
	mountEverest = 'mountEverest'
	mountKilimanjaro = 'mountEverest'
	greatBarrierReef = 'greatBarrierReef'
	cliffsOfDover = 'cliffsOfDover'
	uluru = 'uluru'

	def name(self) -> str:
		return self._data().name

	def _data(self):
		if self == FeatureType.none:
			return FeatureData('None', Yields(food=0, production=0, gold=0), False)
		if self == FeatureType.forest or self == FeatureType.pine:
			return FeatureData('Forest', Yields(0, 1, gold=0), False)
		elif self == FeatureType.rainforest:
			return FeatureData('Rainforest', Yields(1, 0, gold=0), False)
		elif self == FeatureType.floodplains:
			return FeatureData('Floodplains', Yields(3, 0, gold=0), False)
		elif self == FeatureType.marsh:
			return FeatureData('Marsh', Yields(3, 0, gold=0), False)
		elif self == FeatureType.oasis:
			return FeatureData("Oasis", Yields(1, 0, gold=0), False)
		elif self == FeatureType.reef:
			return FeatureData("Reef", Yields(1, 0, gold=0), False)
		elif self == FeatureType.ice:
			return FeatureData("Ice", Yields(0, 0, gold=0), False)
		elif self == FeatureType.atoll:
			return FeatureData("Atoll", Yields(1, 0, gold=0), False)
		elif self == FeatureType.volcano:
			return FeatureData("Volcano", Yields(0, 0, gold=0), False)
		elif self == FeatureType.mountains:
			return FeatureData("Mountains", Yields(0, 0, gold=0), False)
		elif self == FeatureType.lake:
			return FeatureData("Lake", Yields(0, 0, gold=0), False)
		elif self == FeatureType.fallout:
			return FeatureData("Fallout", Yields(-3, -3, gold=-3), False)

		# wonders
		elif self == FeatureType.mountEverest:
			return FeatureData(
				name="Mount Everest",
				yields=Yields(food=2, production=0, gold=0, science=0, faith=1),
				is_wonder=True
			)
		elif self == FeatureType.greatBarrierReef:
			return FeatureData(
				name="Great Barrier Reef",
				yields=Yields(food=3, production=0, gold=0, science=2),
				is_wonder=True
			)
		elif self == FeatureType.cliffsOfDover:
			return FeatureData(
				name="Cliffs of Dover",
				yields=Yields(food=0, production=0, gold=0, science=0, culture=0, faith=0),  #
				is_wonder=True
			)
		elif self == FeatureType.uluru:
			return FeatureData(
				name="Uluru",
				yields=Yields(food=0, production=0, gold=0, science=0, culture=2, faith=2),
				is_wonder=True
			)

		raise AttributeError(f'FeatureType.data: {self} not handled!')

	# return FeatureData('None', Yields(0, 0, 0), False)

	def movementCost(self, movement_type):
		if movement_type == UnitMovementType.immobile:
			return UnitMovementType.max

		if movement_type == UnitMovementType.swim:
			return UnitMovementType.max  # this means that no unit can enter water features

		if movement_type == UnitMovementType.swimShallow:
			return self.movementCosts()

		if movement_type == UnitMovementType.walk:
			return self.movementCosts()

	def movementCosts(self):
		if self == FeatureType.forest:
			return 2
		elif self == FeatureType.rainforest:
			return 2
		elif self == FeatureType.floodplains:
			return 0
		elif self == FeatureType.marsh:
			return 2
		elif self == FeatureType.oasis:
			return 0
		elif self == FeatureType.reef:
			return 2
		elif self == FeatureType.ice:
			return UnitMovementType.max
		elif self == FeatureType.atoll:
			return 2
		elif self == FeatureType.volcano:
			return UnitMovementType.max
		elif self == FeatureType.mountains:
			return 2  # ???
		elif self == FeatureType.lake:
			return UnitMovementType.max
		elif self == FeatureType.fallout:
			return 2

		return UnitMovementType.max

	def isPossibleOn(self, tile):
		if self == FeatureType.forest:
			return self._isForestPossibleOn(tile)
		elif self == FeatureType.rainforest:
			return self._isRainforestPossibleOn(tile)
		elif self == FeatureType.floodplains:
			return self._isFloodplainsPossibleOn(tile)
		elif self == FeatureType.marsh:
			return self._isMarshPossibleOn(tile)
		elif self == FeatureType.oasis:
			return self._isOasisPossibleOn(tile)
		elif self == FeatureType.reef:
			return self._isReefPossibleOn(tile)
		elif self == FeatureType.ice:
			return self._isIcePossibleOn(tile)
		elif self == FeatureType.atoll:
			return self._isAtollPossibleOn(tile)
		elif self == FeatureType.volcano:
			return self._isVolcanoPossibleOn(tile)
		#
		elif self == FeatureType.mountains:
			return self._isMountainPossibleOn(tile)
		elif self == FeatureType.lake:
			return self._isLakePossibleOn(tile)
		elif self == FeatureType.fallout:
			return self._isFalloutPossibleOn(tile)

		return False

	def _isForestPossibleOn(self, tile):
		"""Grassland, Grassland (Hills), Plains, Plains (Hills), Tundra and Tundra (Hills)."""
		if tile.terrain() == TerrainType.tundra or tile.terrain() == TerrainType.grass or tile.terrain() == TerrainType.plains:
			return True

		return False

	def _isRainforestPossibleOn(self, tile):
		"""Modifies Plains and Plains (Hills)."""
		if tile.terrain() == TerrainType.plains:
			return True

		return False

	def _isFloodplainsPossibleOn(self, tile):
		"""Floodplains modifies Deserts and also Plains and Grassland."""
		if tile.isHills():
			return False

		if tile.terrain() in [TerrainType.desert, TerrainType.grass, TerrainType.plains]:
			return True

		return False

	def _isMarshPossibleOn(self, tile):
		"""Marsh modifies Grassland"""
		if tile.isHills():
			return False

		if tile.terrain() == TerrainType.grass:
			return True

		return False

	def _isOasisPossibleOn(self, tile):
		"""Oasis modifies Desert"""
		if tile.isHills():
			return False

		if tile.terrain() == TerrainType.desert:
			return True

		return False

	def _isReefPossibleOn(self, tile):
		"""
			checks if feature reef is possible on tile
			https://civilization.fandom.com/wiki/Reef_(Civ6)

			@param tile: tile to check
			@return: True, if feature reef is possible on tile
		"""
		if not tile.isWater():
			return False

		if tile.terrain() != TerrainType.shore:
			return False

		return True

	def _isIcePossibleOn(self, tile):
		"""Ice modifies Ocean and Shore"""
		if tile.isWater():
			return True

		return False

	def _isAtollPossibleOn(self, tile):
		"""Atoll modifies Ocean and Shore"""
		if tile.isWater():
			return True

		return False

	def _isVolcanoPossibleOn(self, tile):
		"""Volcano modifies Mountains"""
		if tile.hasFeature(FeatureType.mountains):
			return True

		return False

	def _isMountainPossibleOn(self, tile):
		"""Mountain modifies hilly Desert, Grassland, Plains, Tundra and Snow"""
		if tile.isHills():
			return False

		if tile.terrain() in [TerrainType.desert, TerrainType.grass, TerrainType.plains, TerrainType.tundra,
		                      TerrainType.snow]:
			return True

		return False

	def _isLakePossibleOn(self, tile):
		"""Lake modifies all non-hilly terrain"""
		if tile.isHills():
			return False

		if tile.isWater():
			return False

		return True

	def _isFalloutPossibleOn(self, tile):
		"""Fallout modifies all land tiles"""
		if tile.isWater():
			return False

		return True

	def isNaturalWonder(self):
		return self._data().is_wonder

	def textures(self):
		if self == FeatureType.none:
			return ['feature_none@3x.png']

		if self == FeatureType.atoll:
			return ['feature_atoll@3x.png']

		if self == FeatureType.fallout:
			return ['feature_fallout@3x.png']

		if self == FeatureType.floodplains:
			return ['feature_floodplains@3x.png']

		if self == FeatureType.forest:
			return ['feature_forest1@3x.png', 'feature_forest2@3x.png']

		if self == FeatureType.ice:
			return ['feature_ice1@3x.png', 'feature_ice2@3x.png', 'feature_ice3@3x.png', 'feature_ice4@3x.png',
			        'feature_ice5@3x.png', 'feature_ice6@3x.png']

		if self == FeatureType.marsh:
			return ['feature_marsh1@3x.png', 'feature_marsh2@3x.png']

		if self == FeatureType.mountains:
			return ['feature_mountains1@3x.png', 'feature_mountains2@3x.png', 'feature_mountains3@3x.png']

		if self == FeatureType.oasis:
			return ['feature_oasis@3x.png']

		if self == FeatureType.pine:
			return ['feature_pine1@3x.png', 'feature_pine2@3x.png']

		if self == FeatureType.rainforest:
			return ['feature_rainforest1@3x.png', 'feature_rainforest2@3x.png', 'feature_rainforest3@3x.png',
			        'feature_rainforest4@3x.png', 'feature_rainforest5@3x.png', 'feature_rainforest6@3x.png',
			        'feature_rainforest7@3x.png', 'feature_rainforest8@3x.png', 'feature_rainforest9@3x.png']

		if self == FeatureType.reef:
			return ['feature_reef1@3x.png', 'feature_reef2@3x.png', 'feature_reef3@3x.png']

		if self == FeatureType.lake:
			return []

		if self == FeatureType.volcano:
			return []

		# natural wonders

		if self == FeatureType.mountEverest:
			return []

		if self == FeatureType.mountKilimanjaro:
			return []

		return []

	def yields(self) -> Yields:
		return self._data().yields


class ResourceUsage(ExtendedEnum):
	bonus = 'bonus'
	strategic = 'strategic'
	luxury = 'luxury'
	artifacts = 'artifacts'

	def amenities(self) -> int:
		if self == ResourceUsage.luxury:
			return 4

		return 0


class ResourceTypeData:
	def __init__(self, name: str, usage: ResourceUsage, revealTech: Optional[TechType],
	             revealCivic: Optional[CivicType], placementOrder: int, baseAmount: int, placeOnHills: bool,
	             placeOnRiverSide: bool, placeOnFlatlands: bool, placeOnFeatures: [FeatureType],
	             placeOnFeatureTerrains: [TerrainType], placeOnTerrains: [TerrainType], yields: Yields):
		self.name = name
		self.usage = usage
		self.revealTech = revealTech
		self.revealCivic = revealCivic
		self.placementOrder = placementOrder
		self.baseAmount = baseAmount

		self.placeOnHills = placeOnHills
		self.placeOnRiverSide = placeOnRiverSide
		self.placeOnFlatlands = placeOnFlatlands
		self.placeOnFeatures = placeOnFeatures
		self.placeOnFeatureTerrains = placeOnFeatureTerrains
		self.placeOnTerrains = placeOnTerrains

		self.yields = yields


class ResourceType(ExtendedEnum):
	# default
	none = 'none'

	# bonus
	wheat = 'wheat'
	rice = 'rice'
	deer = 'deer'
	sheep = 'sheep'
	copper = 'copper'
	stone = 'stone'  # https://civilization.fandom.com/wiki/Stone_(Civ6)
	banana = 'banana'
	cattle = 'cattle'
	fish = 'fish'

	# luxury
	citrus = 'citrus'
	whales = 'whales'

	# strategic
	horses = 'horses'
	iron = 'iron'  # https://civilization.fandom.com/wiki/Iron_(Civ6)
	coal = 'coal'  # https://civilization.fandom.com/wiki/Coal_(Civ6)
	oil = 'oil'  # https://civilization.fandom.com/wiki/Oil_(Civ6)
	aluminum = 'aluminum'  # https://civilization.fandom.com/wiki/Aluminum_(Civ6)
	uranium = 'uranium'  # https://civilization.fandom.com/wiki/Uranium_(Civ6)
	niter = 'niter'  # https://civilization.fandom.com/wiki/Niter_(Civ6)

	# artifacts
	antiquitySite = 'antiquitySite'  # https://civilization.fandom.com/wiki/Antiquity_Site_(Civ6)
	shipwreck = 'shipwreck'  # https://civilization.fandom.com/wiki/Shipwreck_(Civ6)

	def name(self) -> str:
		return self._data().name

	def usage(self) -> ResourceUsage:
		return self._data().usage

	def placementOrder(self) -> int:
		return self._data().placementOrder

	def _data(self) -> ResourceTypeData:
		# default
		if self == ResourceType.none:
			return ResourceTypeData(
				name='none',
				usage=ResourceUsage.bonus,
				revealTech=None,
				revealCivic=None,
				placementOrder=-1,
				baseAmount=0,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[],
				yields=Yields(food=0, production=0, gold=0)
			)

		# bonus
		if self == ResourceType.wheat:
			return ResourceTypeData(
				name='Wheat',
				usage=ResourceUsage.bonus,
				revealTech=TechType.pottery,
				revealCivic=None,
				placementOrder=4,
				baseAmount=18,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.floodplains],
				placeOnFeatureTerrains=[TerrainType.desert],
				placeOnTerrains=[TerrainType.plains],
				yields=Yields(food=1, production=0, gold=0)
			)
		elif self == ResourceType.rice:
			return ResourceTypeData(
				name='Rice',
				usage=ResourceUsage.bonus,
				revealTech=TechType.pottery,
				revealCivic=None,
				placementOrder=4,
				baseAmount=14,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.marsh],
				placeOnFeatureTerrains=[TerrainType.grass],
				placeOnTerrains=[TerrainType.grass],
				yields=Yields(food=1, production=0, gold=0)
			)
		elif self == ResourceType.deer:
			return ResourceTypeData(
				name='Deer',
				usage=ResourceUsage.bonus,
				revealTech=TechType.animalHusbandry,
				revealCivic=None,
				placementOrder=4,
				baseAmount=16,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.forest],
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.snow],
				placeOnTerrains=[TerrainType.tundra],
				yields=Yields(food=0, production=1, gold=0)
			)
		elif self == ResourceType.sheep:
			return ResourceTypeData(
				name='Sheep',
				usage=ResourceUsage.bonus,
				revealTech=None,
				revealCivic=None,
				placementOrder=4,
				baseAmount=20,
				placeOnHills=True,
				placeOnRiverSide=True,
				placeOnFlatlands=False,
				placeOnFeatures=[FeatureType.forest],
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.snow],
				placeOnTerrains=[TerrainType.tundra],
				yields=Yields(food=1, production=0, gold=0)
			)
		elif self == ResourceType.copper:
			return ResourceTypeData(
				name='Copper',
				usage=ResourceUsage.bonus,
				revealTech=None,
				revealCivic=None,
				placementOrder=4,
				baseAmount=6,
				placeOnHills=True,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra],
				yields=Yields(food=0, production=1, gold=0)
			)
		elif self == ResourceType.stone:
			return ResourceTypeData(
				name='Stone',
				usage=ResourceUsage.bonus,
				revealTech=None,
				revealCivic=None,
				placementOrder=4,
				baseAmount=12,
				placeOnHills=True,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass],
				yields=Yields(food=0, production=1, gold=0)
			)
		elif self == ResourceType.banana:
			return ResourceTypeData(
				name='Banana',
				usage=ResourceUsage.bonus,
				revealTech=None,
				revealCivic=None,
				placementOrder=4,
				baseAmount=2,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.rainforest],
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains],
				placeOnTerrains=[],
				yields=Yields(food=1, production=0, gold=0)
			)
		elif self == ResourceType.cattle:
			return ResourceTypeData(
				name='Cattle',
				usage=ResourceUsage.bonus,
				revealTech=None,
				revealCivic=None,
				placementOrder=4,
				baseAmount=22,
				placeOnHills=False,
				placeOnRiverSide=True,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass],
				yields=Yields(food=1, production=0, gold=0)
			)
		elif self == ResourceType.fish:
			return ResourceTypeData(
				name='Fish',
				usage=ResourceUsage.bonus,
				revealTech=None,
				revealCivic=None,
				placementOrder=4,
				baseAmount=36,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[FeatureType.lake],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.shore],
				yields=Yields(food=1, production=0, gold=0)
			)

		# luxury
		elif self == ResourceType.citrus:
			return ResourceTypeData(
				name='Citrus',
				usage=ResourceUsage.luxury,
				revealTech=None,
				revealCivic=None,
				placementOrder=3,
				baseAmount=2,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=2, production=0, gold=0)
			)
		elif self == ResourceType.whales:
			return ResourceTypeData(
				name='Whales',
				usage=ResourceUsage.luxury,
				revealTech=None,
				revealCivic=None,
				placementOrder=3,
				baseAmount=6,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.shore],
				yields=Yields(food=0, production=1, gold=1)
			)

		# strategic
		elif self == ResourceType.horses:
			return ResourceTypeData(
				name='Horses',
				usage=ResourceUsage.strategic,
				revealTech=None,
				revealCivic=None,
				placementOrder=1,
				baseAmount=14,
				placeOnHills=False,
				placeOnRiverSide=True,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra],
				yields=Yields(food=1, production=1, gold=0)
			)
		elif self == ResourceType.iron:
			return ResourceTypeData(
				name='Iron',
				usage=ResourceUsage.strategic,
				revealTech=TechType.bronzeWorking,
				revealCivic=None,
				placementOrder=0,
				baseAmount=12,
				placeOnHills=False,
				placeOnRiverSide=True,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.desert,
				                 TerrainType.snow],
				yields=Yields(food=0, production=0, gold=0, science=1)
			)
		elif self == ResourceType.coal:
			return ResourceTypeData(
				name='Coal',
				usage=ResourceUsage.strategic,
				revealTech=TechType.industrialization,
				revealCivic=None,
				placementOrder=2,
				baseAmount=10,
				placeOnHills=True,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.plains, TerrainType.grass],
				yields=Yields(food=0, production=2, gold=0)
			)
		elif self == ResourceType.oil:
			return ResourceTypeData(
				name='Oil',
				usage=ResourceUsage.strategic,
				revealTech=TechType.refining,
				revealCivic=None,
				placementOrder=2,
				baseAmount=8,
				placeOnHills=False,
				placeOnRiverSide=True,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.rainforest, FeatureType.marsh],
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains],
				placeOnTerrains=[TerrainType.desert, TerrainType.tundra, TerrainType.snow, TerrainType.shore],
				yields=Yields(food=0, production=3, gold=0)
			)
		elif self == ResourceType.aluminum:
			return ResourceTypeData(
				name='Aluminum',
				usage=ResourceUsage.strategic,
				revealTech=None,
				revealCivic=None,
				placementOrder=2,
				baseAmount=8,
				placeOnHills=True,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[TerrainType.plains],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=0, production=0, gold=0, science=1)
			)
		elif self == ResourceType.uranium:
			return ResourceTypeData(
				name='Uranium',
				usage=ResourceUsage.strategic,
				revealTech=None,
				revealCivic=None,
				placementOrder=2,
				baseAmount=4,
				placeOnHills=False,
				placeOnRiverSide=True,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.rainforest, FeatureType.marsh, FeatureType.forest],
				placeOnFeatureTerrains=[
					TerrainType.grass, TerrainType.plains, TerrainType.desert,
					TerrainType.tundra, TerrainType.snow
				],
				placeOnTerrains=[
					TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra,
					TerrainType.snow
				],
				yields=Yields(food=0, production=2, gold=0)
			)
		elif self == ResourceType.niter:
			return ResourceTypeData(
				name='Niter',
				usage=ResourceUsage.strategic,
				revealTech=None,
				revealCivic=None,
				placementOrder=2,
				baseAmount=8,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra],
				yields=Yields(food=1, production=1, gold=0)
			)

		# artifacts
		elif self == ResourceType.antiquitySite:
			#
			return ResourceTypeData(
				name='Antiquity Site',
				usage=ResourceUsage.artifacts,
				revealTech=None,
				revealCivic=CivicType.naturalHistory,
				placementOrder=-1,
				baseAmount=0,
				placeOnHills=True,
				placeOnRiverSide=True,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[
					TerrainType.grass, TerrainType.plains, TerrainType.desert, TerrainType.tundra, TerrainType.snow
				],
				yields=Yields(food=0.0, production=0.0, gold=0.0)
			)
		elif self == ResourceType.shipwreck:
			return ResourceTypeData(
				name='Shipwreck',
				usage=ResourceUsage.artifacts,
				revealTech=None,
				revealCivic=CivicType.culturalHeritage,
				placementOrder=-1,
				baseAmount=0,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.shore, TerrainType.ocean],
				yields=Yields(food=0.0, production=0.0, gold=0.0)
			)

		raise AttributeError(f'cant determine data of {self}')

	def canBePlacedOnFeature(self, feature: FeatureType) -> bool:
		return feature in self._data().placeOnFeatures

	def canBePlacedOnFeatureTerrain(self, terrain: TerrainType) -> bool:
		return terrain in self._data().placeOnFeatureTerrains

	def canBePlacedOnTerrain(self, terrain: TerrainType) -> bool:
		return terrain in self._data().placeOnTerrains

	def canBePlacedOnHills(self) -> bool:
		return self._data().placeOnHills

	def canBePlacedOnFlatlands(self):
		return self._data().placeOnFlatlands

	def baseAmount(self):
		return self._data().baseAmount

	def absoluteVarPercent(self):
		if self == ResourceType.fish:
			return 10

		return 25

	def revealTech(self):
		"""
			returns the tech that reveals the resource
			:return: tech that is needed to reveal the resource
		"""
		return self._data().revealTech

	def revealCivic(self):
		"""
			returns the civic that reveals the resource
			:return: civic that is needed to reveal the resource
		"""
		return self._data().revealCivic

	def texture(self) -> str:
		# default
		if self == ResourceType.none:
			return 'resource_none@3x.png'

		# bonus
		if self == ResourceType.wheat:
			return 'resource_wheat@3x.png'
		if self == ResourceType.rice:
			return 'resource_rice@3x.png'
		if self == ResourceType.deer:
			return 'resource_deer@3x.png'
		if self == ResourceType.sheep:
			return 'resource_sheep@3x.png'
		if self == ResourceType.copper:
			return 'resource_copper@3x.png'
		if self == ResourceType.stone:
			return 'resource_stone@3x.png'
		if self == ResourceType.banana:
			return 'resource_banana@3x.png'
		if self == ResourceType.cattle:
			return 'resource_cattle@3x.png'
		if self == ResourceType.fish:
			return 'resource_fish@3x.png'

		# luxury
		if self == ResourceType.citrus:
			return 'resource_citrus@3x.png'
		if self == ResourceType.whales:
			return 'resource_whales@3x.png'

		# strategic
		if self == ResourceType.horses:
			return 'resource_horses@3x.png'
		if self == ResourceType.iron:
			return 'resource_iron@3x.png'
		if self == ResourceType.coal:
			return 'resource_coal@3x.png'
		if self == ResourceType.oil:
			return 'resource_oil@3x.png'
		if self == ResourceType.aluminum:
			return 'resource_aluminum@3x.png'
		if self == ResourceType.uranium:
			return 'resource_uranium@3x.png'
		if self == ResourceType.niter:
			return 'resource_niter@3x.png'

		# artifacts
		if self == ResourceType.antiquitySite:
			return 'resource_antiquitySite@3x.png'
		if self == ResourceType.shipwreck:
			return 'resource_shipwreck@3x.png'

		raise ValueError(f'cannot get texture for {self}')

	def __str__(self):
		return self.value

	def yields(self):
		return self._data().yields


class ClimateZone(ExtendedEnum):
	polar = 'polar'
	sub_polar = 'sub_polar'
	temperate = 'temperate'
	sub_tropic = 'sub_tropic'
	tropic = 'tropic'

	def moderate(self):
		if self == ClimateZone.polar:
			return ClimateZone.sub_polar
		elif self == ClimateZone.sub_polar:
			return ClimateZone.temperate
		elif self == ClimateZone.temperate:
			return ClimateZone.sub_tropic
		elif self == ClimateZone.sub_tropic:
			return ClimateZone.tropic
		else:
			return ClimateZone.tropic


class UnitMovementType(ExtendedEnum):
	immobile = 'immobile'
	walk = 'walk'
	swim = 'swim'
	swimShallow = 'swimShallow'

	max = 1000

class AppealLevel:
	pass


class AppealLevel(ExtendedEnum):
	breathtaking = 'breathtaking'
	charming = 'charming'
	average = 'average'
	uninviting = 'uninviting'
	disgusting = 'disgusting'

	@classmethod
	def fromAppeal(cls, appeal: int) -> AppealLevel:
		if appeal >= 4:
			return AppealLevel.breathtaking
		elif appeal >= 2:
			return AppealLevel.charming
		elif appeal >= -1:
			return AppealLevel.average
		elif appeal >= -3:
			return AppealLevel.uninviting
		else:
			return AppealLevel.disgusting


class RouteType(ExtendedEnum):
	none = 'none'
	ancientRoad = 'ancientRoad'
	classicalRoad = 'classicalRoad'
	industrialRoad = 'industrialRoad'
	modernRoad = 'modernRoad'

	def movementCost(self):
		if self == RouteType.none:
			return 200
		elif self == RouteType.ancientRoad:
			# Starting road, well-packed dirt. Most terrain costs 1 MP; crossing rivers still costs 3 MP.
			return 1
		elif self == RouteType.classicalRoad:
			# Adds bridges over rivers; crossing costs reduced to only 1 MP.
			return 1
		elif self == RouteType.industrialRoad:
			# Paved roads are developed; 0.75 MP per tile.
			return 0.75
		elif self == RouteType.modernRoad:
			# Asphalted roads are developed; 0.50 MP per tile.
			return 0.5


class Tutorials(Enum):
	none = 'none'
	foundFirstCity = 'foundFirstCity'
	movementAndExploration = 'movementAndExploration'

	@classmethod
	def tilesToDiscover(cls):
		return 60  # ???

	@classmethod
	def citiesToFound(cls):
		return 2  # ???
