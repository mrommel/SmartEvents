from builtins import float
from enum import Enum
from typing import Optional

from core.types import EraType
from game.types import TechType, CivicType
from map.base import ExtendedEnum, Size
from core.base import InvalidEnumError, WeightedBaseList
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


class YieldType(ExtendedEnum):
	none = 'none'

	food = 'food'
	production = 'production'
	gold = 'gold'
	science = 'science'
	culture = 'culture'
	faith = 'faith'


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

	def value(self, yieldType: YieldType) -> float:
		if yieldType == YieldType.food:
			return self.food
		if yieldType == YieldType.production:
			return self.production
		if yieldType == YieldType.gold:
			return self.gold
		if yieldType == YieldType.science:
			return self.science
		if yieldType == YieldType.culture:
			return self.culture
		if yieldType == YieldType.faith:
			return self.faith
		# if yieldType == YieldType.housing:
		#	return self.housing
		# if yieldType == YieldType.appeal:
		#	return self.appeal
		if yieldType == YieldType.none:
			return 0.0

		raise InvalidEnumError(yieldType)


class YieldList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for yieldType in list(YieldType):
			self[yieldType] = 0


class TerrainData:
	def __init__(self, name: str, yields: Yields, isWater: bool, domain: UnitDomainType, antiquityPriority: int,
	             defenseModifier: int):
		self.name = name
		self.yields = yields
		self.isWater = isWater
		self.domain = domain
		self.antiquityPriority = antiquityPriority
		self.defenseModifier = defenseModifier


class TerrainType:
	pass


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

	@staticmethod
	def fromName(terrainName: str) -> TerrainType:
		if terrainName == 'TerrainType.desert' or terrainName == 'desert':
			return TerrainType.desert
		elif terrainName == 'TerrainType.grass' or terrainName == 'grass':
			return TerrainType.grass
		elif terrainName == 'TerrainType.ocean' or terrainName == 'ocean':
			return TerrainType.ocean
		elif terrainName == 'TerrainType.plains' or terrainName == 'plains':
			return TerrainType.plains
		elif terrainName == 'TerrainType.shore' or terrainName == 'shore':
			return TerrainType.shore
		elif terrainName == 'TerrainType.snow' or terrainName == 'snow':
			return TerrainType.snow
		elif terrainName == 'TerrainType.tundra' or terrainName == 'tundra':
			return TerrainType.tundra

		raise Exception(f'No matching case for terrainName: "{terrainName}"')

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
				antiquityPriority=5,
				defenseModifier=0
			)
		elif self == TerrainType.grass:
			return TerrainData(
				name='Grassland',
				yields=Yields(food=2, production=0, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=2,
				defenseModifier=0
			)
		elif self == TerrainType.ocean:
			return TerrainData(
				name='Ocean',
				yields=Yields(food=1, production=0, gold=0, science=0),
				isWater=True,
				domain=UnitDomainType.sea,
				antiquityPriority=0,
				defenseModifier=0
			)
		elif self == TerrainType.plains:
			return TerrainData(
				name='Plains',
				yields=Yields(food=1, production=1, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=2,
				defenseModifier=0
			)
		elif self == TerrainType.shore:
			return TerrainData(
				name='Shore',
				yields=Yields(food=1, production=0, gold=1, science=0),
				isWater=True,
				domain=UnitDomainType.sea,
				antiquityPriority=2,
				defenseModifier=0
			)
		elif self == TerrainType.snow:
			return TerrainData(
				name='Snow',
				yields=Yields(food=0, production=0, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=1,
				defenseModifier=0
			)
		elif self == TerrainType.tundra:
			return TerrainData(
				name='Tundra',
				yields=Yields(food=1, production=0, gold=0, science=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=3,
				defenseModifier=0
			)

		elif self == TerrainType.land:
			return TerrainData(
				name='',
				yields=Yields(food=0, production=0, gold=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=0,
				defenseModifier=0
			)
		elif self == TerrainType.sea:
			return TerrainData(
				name='',
				yields=Yields(food=0, production=0, gold=0),
				isWater=False,
				domain=UnitDomainType.land,
				antiquityPriority=0,
				defenseModifier=0
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

	def defenseModifier(self):
		return self._data().defenseModifier


class FeatureData:
	def __init__(self, name, yields, isWonder: bool, isRemovable: bool, defenseModifier: int):
		self.name = name
		self.yields = yields
		self.isWonder = isWonder
		self.isRemovable = isRemovable
		self.defenseModifier = defenseModifier


class FeatureType:
	pass


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

	@staticmethod
	def fromName(featureName: str) -> FeatureType:
		if featureName == 'FeatureType.none' or featureName == 'none':
			return FeatureType.none
		elif featureName == 'FeatureType.atoll' or featureName == 'atoll':
			return FeatureType.atoll
		elif featureName == 'FeatureType.fallout' or featureName == 'fallout':
			return FeatureType.fallout
		elif featureName == 'FeatureType.floodplains' or featureName == 'floodplains':
			return FeatureType.floodplains
		elif featureName == 'FeatureType.forest' or featureName == 'forest':
			return FeatureType.forest
		elif featureName == 'FeatureType.ice' or featureName == 'ice':
			return FeatureType.ice
		elif featureName == 'FeatureType.marsh' or featureName == 'marsh':
			return FeatureType.marsh
		elif featureName == 'FeatureType.mountains' or featureName == 'mountains':
			return FeatureType.mountains
		elif featureName == 'FeatureType.oasis' or featureName == 'oasis':
			return FeatureType.oasis
		elif featureName == 'FeatureType.pine' or featureName == 'pine':
			return FeatureType.pine
		elif featureName == 'FeatureType.rainforest' or featureName == 'rainforest':
			return FeatureType.rainforest
		elif featureName == 'FeatureType.reef' or featureName == 'reef':
			return FeatureType.reef
		elif featureName == 'FeatureType.lake' or featureName == 'lake':
			return FeatureType.lake
		elif featureName == 'FeatureType.volcano' or featureName == 'volcano':
			return FeatureType.volcano

		# natural wonder
		elif featureName == 'FeatureType.mountEverest' or featureName == 'mountEverest':
			return FeatureType.mountEverest
		elif featureName == 'FeatureType.mountKilimanjaro' or featureName == 'mountKilimanjaro':
			return FeatureType.mountKilimanjaro
		elif featureName == 'FeatureType.greatBarrierReef' or featureName == 'greatBarrierReef':
			return FeatureType.greatBarrierReef
		elif featureName == 'FeatureType.cliffsOfDover' or featureName == 'cliffsOfDover':
			return FeatureType.cliffsOfDover
		elif featureName == 'FeatureType.uluru' or featureName == 'uluru':
			return FeatureType.uluru

		raise Exception(f'No matching case for featureName: "{featureName}"')

	def name(self) -> str:
		return self._data().name

	def isRemovable(self) -> bool:#
		return self._data().isRemovable

	def _data(self):
		if self == FeatureType.none:
			return FeatureData(
				name='None',
				yields=Yields(food=0, production=0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		if self == FeatureType.forest or self == FeatureType.pine:
			return FeatureData(
				name='Forest',
				yields=Yields(0, 1, gold=0),
				isWonder=False,
				isRemovable=True,
				defenseModifier=3
			)
		elif self == FeatureType.rainforest:
			return FeatureData(
				name='Rainforest',
				yields=Yields(1, 0, gold=0),
				isWonder=False,
				isRemovable=True,
				defenseModifier=3
			)
		elif self == FeatureType.floodplains:
			return FeatureData(
				name='Floodplains',
				yields=Yields(3, 0, gold=0),
				isWonder=False,
				isRemovable=True,
				defenseModifier=-2
			)
		elif self == FeatureType.marsh:
			return FeatureData(
				name='Marsh',
				yields=Yields(3, 0, gold=0),
				isWonder=False,
				isRemovable=True,
				defenseModifier=-2
			)
		elif self == FeatureType.oasis:
			return FeatureData(
				name="Oasis",
				yields=Yields(1, 0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.reef:
			return FeatureData(
				name="Reef",
				yields=Yields(1, 0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.ice:
			return FeatureData(
				name="Ice",
				yields=Yields(0, 0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.atoll:
			return FeatureData(
				name="Atoll",
				yields=Yields(1, 0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.volcano:
			return FeatureData(
				name="Volcano",
				yields=Yields(0, 0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.mountains:
			return FeatureData(
				name="Mountains",
				yields=Yields(0, 0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.lake:
			return FeatureData(
				name="Lake",
				yields=Yields(0, 0, gold=0),
				isWonder=False,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.fallout:
			return FeatureData(
				name="Fallout",
				yields=Yields(-3, -3, gold=-3),
				isWonder=True,
				isRemovable=True,
				defenseModifier=0
			)

		# wonders
		elif self == FeatureType.mountEverest:
			return FeatureData(
				name="Mount Everest",
				yields=Yields(food=2, production=0, gold=0, science=0, faith=1),
				isWonder=True,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.greatBarrierReef:
			return FeatureData(
				name="Great Barrier Reef",
				yields=Yields(food=3, production=0, gold=0, science=2),
				isWonder=True,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.cliffsOfDover:
			return FeatureData(
				name="Cliffs of Dover",
				yields=Yields(food=0, production=0, gold=0, science=0, culture=0, faith=0),  #
				isWonder=True,
				isRemovable=False,
				defenseModifier=0
			)
		elif self == FeatureType.uluru:
			return FeatureData(
				name="Uluru",
				yields=Yields(food=0, production=0, gold=0, science=0, culture=2, faith=2),
				isWonder=True,
				isRemovable=False,
				defenseModifier=0
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
		return self._data().isWonder

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

	def defenseModifier(self):
		return self._data().defenseModifier


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


class ResourceType:
	pass


class ResourceType(ExtendedEnum):
	# default
	none = 'none'

	# bonus
	banana = 'banana'
	cattle = 'cattle'
	copper = 'copper'
	crab = 'crab'
	deer = 'deer'
	fish = 'fish'
	rice = 'rice'
	sheep = 'sheep'
	stone = 'stone'
	wheat = 'wheat'

	# luxury
	citrus = 'citrus'
	cocoa = 'cocoa'
	cotton = 'cotton'
	dyes = 'dyes'
	furs = 'furs'
	incense = 'incense'
	ivory = 'ivory'
	pearls = 'pearls'
	salt = 'salt'
	silk = 'silk'
	silver = 'silver'
	spices = 'spices'
	sugar = 'sugar'
	tea = 'tea'
	whales = 'whales'
	wine = 'wine'
	# marble

	# strategic
	horses = 'horses'
	iron = 'iron'
	coal = 'coal'
	oil = 'oil'
	aluminum = 'aluminum'
	uranium = 'uranium'
	niter = 'niter'

	# artifacts
	antiquitySite = 'antiquitySite'  # https://civilization.fandom.com/wiki/Antiquity_Site_(Civ6)
	shipwreck = 'shipwreck'  # https://civilization.fandom.com/wiki/Shipwreck_(Civ6)

	@staticmethod
	def fromName(resourceName: str) -> ResourceType:
		if resourceName == 'ResourceType.none' or resourceName == 'none':
			return ResourceType.none

		# bonus
		elif resourceName == 'ResourceType.banana' or resourceName == 'banana':
			return ResourceType.banana
		elif resourceName == 'ResourceType.cattle' or resourceName == 'cattle':
			return ResourceType.cattle
		elif resourceName == 'ResourceType.copper' or resourceName == 'copper':
			return ResourceType.copper
		elif resourceName == 'ResourceType.crab' or resourceName == 'crab':
			return ResourceType.crab
		elif resourceName == 'ResourceType.deer' or resourceName == 'deer':
			return ResourceType.deer
		elif resourceName == 'ResourceType.fish' or resourceName == 'fish':
			return ResourceType.fish
		elif resourceName == 'ResourceType.rice' or resourceName == 'rice':
			return ResourceType.rice
		elif resourceName == 'ResourceType.sheep' or resourceName == 'sheep':
			return ResourceType.sheep
		elif resourceName == 'ResourceType.stone' or resourceName == 'stone':
			return ResourceType.stone
		elif resourceName == 'ResourceType.wheat' or resourceName == 'wheat':
			return ResourceType.wheat

		# luxury
		elif resourceName == 'ResourceType.citrus' or resourceName == 'citrus':
			return ResourceType.citrus
		elif resourceName == 'ResourceType.cocoa' or resourceName == 'cocoa':
			return ResourceType.cocoa
		elif resourceName == 'ResourceType.cotton' or resourceName == 'cotton':
			return ResourceType.cotton
		elif resourceName == 'ResourceType.dyes' or resourceName == 'dyes':
			return ResourceType.dyes
		elif resourceName == 'ResourceType.furs' or resourceName == 'furs':
			return ResourceType.furs
		elif resourceName == 'ResourceType.incense' or resourceName == 'incense':
			return ResourceType.incense
		elif resourceName == 'ResourceType.ivory' or resourceName == 'ivory':
			return ResourceType.ivory
		elif resourceName == 'ResourceType.pearls' or resourceName == 'pearls':
			return ResourceType.pearls
		elif resourceName == 'ResourceType.salt' or resourceName == 'salt':
			return ResourceType.salt
		elif resourceName == 'ResourceType.silk' or resourceName == 'silk':
			return ResourceType.silk
		elif resourceName == 'ResourceType.silver' or resourceName == 'silver':
			return ResourceType.silver
		elif resourceName == 'ResourceType.spices' or resourceName == 'spices':
			return ResourceType.spices
		elif resourceName == 'ResourceType.sugar' or resourceName == 'sugar':
			return ResourceType.sugar
		elif resourceName == 'ResourceType.tea' or resourceName == 'tea':
			return ResourceType.tea
		elif resourceName == 'ResourceType.whales' or resourceName == 'whales':
			return ResourceType.whales
		elif resourceName == 'ResourceType.wine' or resourceName == 'wine':
			return ResourceType.wine
		# marble

			# strategic
		elif resourceName == 'ResourceType.horses' or resourceName == 'horses':
			return ResourceType.horses
		elif resourceName == 'ResourceType.iron' or resourceName == 'iron':
			return ResourceType.iron
		elif resourceName == 'ResourceType.coal' or resourceName == 'coal':
			return ResourceType.coal
		elif resourceName == 'ResourceType.oil' or resourceName == 'oil':
			return ResourceType.oil
		elif resourceName == 'ResourceType.aluminum' or resourceName == 'aluminum':
			return ResourceType.aluminum
		elif resourceName == 'ResourceType.uranium' or resourceName == 'uranium':
			return ResourceType.uranium
		elif resourceName == 'ResourceType.niter' or resourceName == 'niter':
			return ResourceType.niter

			# artifacts
		elif resourceName == 'ResourceType.antiquitySite' or resourceName == 'antiquitySite':
			return ResourceType.antiquitySite
		elif resourceName == 'ResourceType.shipwreck' or resourceName == 'shipwreck':
			return ResourceType.shipwreck

		raise Exception(f'No matching case for resourceName: "{resourceName}"')

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
		if self == ResourceType.crab:
			# https://civilization.fandom.com/wiki/Crabs_(Civ6)
			return ResourceTypeData(
				name="Crab",
				usage=ResourceUsage.bonus,
				revealTech=TechType.sailing,
				revealCivic=None,
				placementOrder=4,
				baseAmount=8,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.shore],
				yields=Yields(food=0, production=0, gold=2)
			)
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
			# https://civilization.fandom.com/wiki/Citrus_(Civ6)
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
		elif self == ResourceType.cocoa:
			# https://civilization.fandom.com/wiki/Cocoa_(Civ6)
			return ResourceTypeData(
				name="Cocoa",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=2,
				placeOnHills=True,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.rainforest],  # only on rainforest
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=1, production=0, gold=1)
			)
		elif self == ResourceType.cotton:
			# https://civilization.fandom.com/wiki/Cotton_(Civ6)
			return ResourceTypeData(
				name="Cotton",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=1,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=0, production=0, gold=3)
			)
		elif self == ResourceType.dyes:
			# https://civilization.fandom.com/wiki/Dyes_(Civ6)
			return ResourceTypeData(
				name="Dyes",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=2,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.rainforest, FeatureType.forest],  # only on rainforest
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=0, production=0, gold=0, faith=1)
			)
		elif self == ResourceType.furs:
			# https://civilization.fandom.com/wiki/Furs_(Civ6)
			return ResourceTypeData(
				name="Furs",
				usage=ResourceUsage.luxury,
				revealTech=TechType.animalHusbandry,
				revealCivic=None,
				placementOrder=3,
				baseAmount=12,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.forest],
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.tundra, TerrainType.snow],
				placeOnTerrains=[TerrainType.tundra],
				yields=Yields(food=1, production=0, gold=1)
			)
		elif self == ResourceType.incense:
			# https://civilization.fandom.com/wiki/Incense_(Civ6)
			return ResourceTypeData(
				name="Incense",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=4,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.plains, TerrainType.desert],
				yields=Yields(food=0, production=0, gold=0, faith=1)
			)
		elif self == ResourceType.ivory:
			# https://civilization.fandom.com/wiki/Ivory_(Civ6)
			return ResourceTypeData(
				name="Ivory",
				usage=ResourceUsage.luxury,
				revealTech=TechType.animalHusbandry,
				revealCivic=None,
				placementOrder=3,
				baseAmount=4,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.plains, TerrainType.desert],
				yields=Yields(food=0, production=1, gold=1)
			)
		elif self == ResourceType.pearls:
			# https://civilization.fandom.com/wiki/Pearls_(Civ6)
			return ResourceTypeData(
				name="Pearls",
				usage=ResourceUsage.luxury,
				revealTech=TechType.sailing,
				revealCivic=None,
				placementOrder=3,
				baseAmount=6,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.shore],
				yields=Yields(food=0, production=0, gold=0, faith=1)
			)
		elif self == ResourceType.salt:
			# https://civilization.fandom.com/wiki/Salt_(Civ6)
			return ResourceTypeData(
				name="Salt",
				usage=ResourceUsage.luxury,
				revealTech=TechType.mining,
				revealCivic=None,
				placementOrder=3,
				baseAmount=2,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.plains, TerrainType.desert, TerrainType.tundra],
				yields=Yields(food=1, production=0, gold=1)
			)
		elif self == ResourceType.silk:
			# https://civilization.fandom.com/wiki/Silk_(Civ6)
			return ResourceTypeData(
				name="Silk",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=1,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.forest],  # only on forest
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=0, production=0, gold=0, faith=1)
			)
		elif self == ResourceType.silver:
			# https://civilization.fandom.com/wiki/Silver_(Civ6)
			return ResourceTypeData(
				name="Silver",
				usage=ResourceUsage.luxury,
				revealTech=TechType.mining,
				revealCivic=None,
				placementOrder=3,
				baseAmount=10,
				placeOnHills=True,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.desert, TerrainType.tundra],
				yields=Yields(food=0, production=0, gold=3)
			)
		elif self == ResourceType.spices:
			# https://civilization.fandom.com/wiki/Spices_(Civ6)
			return ResourceTypeData(
				name="Spices",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=4,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.rainforest],  # only on rainforest
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=2, production=0, gold=0)
			)
		elif self == ResourceType.sugar:
			# https://civilization.fandom.com/wiki/Sugar_(Civ6)
			return ResourceTypeData(
				name="Sugar",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=1,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[FeatureType.floodplains, FeatureType.marsh],  # only on rainforest feature
				placeOnFeatureTerrains=[TerrainType.grass, TerrainType.plains, TerrainType.desert],
				placeOnTerrains=[],
				yields=Yields(food=2, production=0, gold=0)
			)
		elif self == ResourceType.tea:
			# https://civilization.fandom.com/wiki/Tea_(Civ6)
			return ResourceTypeData(
				name="Tea",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=2,
				placeOnHills=True,
				placeOnRiverSide=False,
				placeOnFlatlands=False,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass],
				yields=Yields(food=0, production=0, gold=0, culture=1)
			)
		elif self == ResourceType.whales:
			# https://civilization.fandom.com/wiki/Whales_(Civ6)
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
		elif self == ResourceType.wine:
			# https://civilization.fandom.com/wiki/Wine_(Civ6)
			return ResourceTypeData(
				name="Wine",
				usage=ResourceUsage.luxury,
				revealTech=TechType.irrigation,
				revealCivic=None,
				placementOrder=3,
				baseAmount=12,
				placeOnHills=False,
				placeOnRiverSide=False,
				placeOnFlatlands=True,
				placeOnFeatures=[],
				placeOnFeatureTerrains=[],
				placeOnTerrains=[TerrainType.grass, TerrainType.plains],
				yields=Yields(food=1, production=0, gold=1)
			)

		# strategic
		elif self == ResourceType.horses:
			# https://civilization.fandom.com/wiki/Horses_(Civ6)
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
			# https://civilization.fandom.com/wiki/Iron_(Civ6)
			return ResourceTypeData(
				name='Iron',
				usage=ResourceUsage.strategic,
				revealTech=TechType.mining,
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
			# https://civilization.fandom.com/wiki/Coal_(Civ6)
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
			# https://civilization.fandom.com/wiki/Oil_(Civ6)
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
			# https://civilization.fandom.com/wiki/Aluminum_(Civ6)
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
			# https://civilization.fandom.com/wiki/Uranium_(Civ6)
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
			# https://civilization.fandom.com/wiki/Niter_(Civ6)
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
		if self == ResourceType.cocoa:
			return 'resource_cocoa@3x.png'
		if self == ResourceType.cotton:
			return 'resource_cotton@3x.png'
		if self == ResourceType.crab:
			return 'resource_crab@3x.png'
		if self == ResourceType.dyes:
			return 'resource_dyes@3x.png'
		if self == ResourceType.furs:
			return 'resource_furs@3x.png'
		if self == ResourceType.incense:
			return 'resource_incense@3x.png'
		if self == ResourceType.ivory:
			return 'resource_ivory@3x.png'
		if self == ResourceType.pearls:
			return 'resource_pearls@3x.png'
		if self == ResourceType.salt:
			return 'resource_salt@3x.png'
		if self == ResourceType.silk:
			return 'resource_silk@3x.png'
		if self == ResourceType.silver:
			return 'resource_silver@3x.png'
		if self == ResourceType.spices:
			return 'resource_spices@3x.png'
		if self == ResourceType.sugar:
			return 'resource_sugar@3x.png'
		if self == ResourceType.tea:
			return 'resource_tea@3x.png'
		if self == ResourceType.whales:
			return 'resource_whales@3x.png'
		if self == ResourceType.wine:
			return 'resource_wine@3x.png'

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


class ClimateZone:
	pass


class ClimateZone(ExtendedEnum):
	polar = 'polar'
	sub_polar = 'sub_polar'
	temperate = 'temperate'
	sub_tropic = 'sub_tropic'
	tropic = 'tropic'

	@staticmethod
	def fromName(climateName: str) -> ClimateZone:
		if climateName == 'ClimateZone.polar' or climateName == 'polar':
			return ClimateZone.polar
		elif climateName == 'ClimateZone.sub_polar' or climateName == 'sub_polar':
			return ClimateZone.sub_polar
		elif climateName == 'ClimateZone.temperate' or climateName == 'temperate':
			return ClimateZone.temperate
		elif climateName == 'ClimateZone.sub_tropic' or climateName == 'sub_tropic':
			return ClimateZone.sub_tropic
		elif climateName == 'ClimateZone.tropic' or climateName == 'tropic':
			return ClimateZone.tropic

		raise Exception(f'No matching case for climateName: "{climateName}"')

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


class RouteTypeData:
	def __init__(self, name: str, era: EraType, movementCost: float):
		self.name = name
		self.era = era
		self.movementCost = movementCost


class RouteType:
	pass


class RouteType(ExtendedEnum):
	none = 'none'
	ancientRoad = 'ancientRoad'
	classicalRoad = 'classicalRoad'
	industrialRoad = 'industrialRoad'
	modernRoad = 'modernRoad'

	@staticmethod
	def fromName(routeName: str) -> RouteType:
		if routeName == 'RouteType.none' or routeName == 'none':
			return RouteType.none
		elif routeName == 'RouteType.ancientRoad' or routeName == 'ancientRoad':
			return RouteType.ancientRoad
		elif routeName == 'RouteType.classicalRoad' or routeName == 'classicalRoad':
			return RouteType.classicalRoad
		elif routeName == 'RouteType.industrialRoad' or routeName == 'industrialRoad':
			return RouteType.industrialRoad
		elif routeName == 'RouteType.modernRoad' or routeName == 'modernRoad':
			return RouteType.modernRoad

		raise Exception(f'No matching case for routeName: "{routeName}"')


	def name(self) -> str:
		return self._data().name

	def movementCost(self) -> float:
		return self._data().movementCost

	def era(self) -> EraType:
		return self._data().era

	def _data(self):
		if self == RouteType.none:
			return RouteTypeData(
				name='KEY_TXT_ROUTE_NONE_NAME',
				era=EraType.none,
				movementCost=200
			)
		elif self == RouteType.ancientRoad:
			# Starting road, well-packed dirt. Most terrain costs 1 MP; crossing rivers still costs 3 MP.
			return RouteTypeData(
				name='KEY_TXT_ROUTE_ANCIENT_NAME',
				era=EraType.ancient,
				movementCost=1
			)
		elif self == RouteType.classicalRoad:
			# Adds bridges over rivers; crossing costs reduced to only 1 MP.
			return RouteTypeData(
				name='KEY_TXT_ROUTE_CLASSICAL_NAME',
				era=EraType.classical,
				movementCost=1
			)
		elif self == RouteType.industrialRoad:
			# Paved roads are developed; 0.75 MP per tile.
			return RouteTypeData(
				name='KEY_TXT_ROUTE_INDUSTRIAL_NAME',
				era=EraType.industrial,
				movementCost=0.75
			)
		elif self == RouteType.modernRoad:
			# Asphalted roads are developed; 0.50 MP per tile.
			return RouteTypeData(
				name='KEY_TXT_ROUTE_MODERN_NAME',
				era=EraType.modern,
				movementCost=0.5
			)


class Tutorials(Enum):
	none = 'none'
	foundFirstCity = 'foundFirstCity'
	movementAndExploration = 'movementAndExploration'
	improvingCity = 'improvingCity'

	@classmethod
	def tilesToDiscover(cls) -> int:
		return 60  # ???

	@classmethod
	def citiesToFound(cls) -> int:
		return 2  # ???

	@classmethod
	def citizenInCityNeeded(cls) -> int:
		return 2  # ???
