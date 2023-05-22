from game.flavors import FlavorType, Flavor
from utils.base import ExtendedEnum, InvalidEnumError, WeightedBaseList


class TraitType(ExtendedEnum):
	boldness = 'boldness'


class Trait:
	def __init__(self, traitType: TraitType, value: int):
		self.traitType = traitType
		self.value = value


class CivilizationAbility(ExtendedEnum):
	none = 'none'
	motherRussia = 'motherRussia'
	allRoadsLeadToRome = 'allRoadsLeadToRome'


class CivilizationData:
	def __init__(self, name: str, ability: CivilizationAbility):
		self.name = name
		self.ability = ability


class CivilizationType(ExtendedEnum):
	none = 'none'
	barbarian = 'barbarian'
	free = 'free'
	cityState = 'cityState'

	greek = 'greek'
	roman = 'roman'
	english = 'english'

	def name(self) -> str:
		return self._data().name

	def ability(self) -> CivilizationAbility:
		return self._data().ability

	def startingBias(self, tile, grid) -> int:
		# https://civilization.fandom.com/wiki/Starting_bias_(Civ5)
		if self == CivilizationType.greek:
			return 0  # no special bias
		elif self == CivilizationType.roman:
			return 0  # no special bias
		elif self == CivilizationType.english:
			return 2 if grid.isCoastalAt(tile.point) else 0

		return 0  # rest

	def _data(self) -> CivilizationData:
		if self == CivilizationType.none:
			return CivilizationData(
				name='None',
				ability=CivilizationAbility.none
			)
		elif self == CivilizationType.barbarian:
			return CivilizationData(
				name='Barbarian',
				ability=CivilizationAbility.none
			)
		elif self == CivilizationType.free:
			return CivilizationData(
				name='Free',
				ability=CivilizationAbility.none
			)
		elif self == CivilizationType.cityState:
			return CivilizationData(
				name='CityState',
				ability=CivilizationAbility.none
			)

		elif self == CivilizationType.greek:
			return CivilizationData(
				name='Greek',
				ability=CivilizationAbility.none
			)
		elif self == CivilizationType.roman:
			return CivilizationData(
				name='Roman',
				ability=CivilizationAbility.allRoadsLeadToRome
			)
		elif self == CivilizationType.english:
			return CivilizationData(
				name='English',
				ability=CivilizationAbility.none
			)

		raise InvalidEnumError(self)


class WeightedCivilizationList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for civilization in list(CivilizationType):
			self.setWeight(0.0, civilization)


class LeaderAbility(ExtendedEnum):
	none = 'none'
	trajansColumn = 'trajansColumn'


class LeaderTypeData:
	def __init__(self, name: str, civilization: CivilizationType, ability: LeaderAbility, flavors: [Flavor],
	             traits: [Trait]):
		self.name = name
		self.civilization = civilization
		self.ability = ability
		self.flavors = flavors
		self.traits = traits


class LeaderType(ExtendedEnum):
	barbar = 'barbar'
	cityState = 'cityState'
	none = 'none'

	alexander = 'alexander'
	trajan = 'trajan'
	victoria = 'victoria'

	def name(self) -> str:
		return self._data().name

	def civilization(self) -> CivilizationType:
		return self._data().civilization

	def ability(self) -> LeaderAbility:
		return self._data().ability

	def flavor(self, flavorType: FlavorType) -> int:
		item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

		if item is not None:
			return item.value

		return 0

	def _flavors(self) -> [Flavor]:
		return self._data().flavors

	def traitValue(self, traitType: TraitType) -> int:
		item = next((trait for trait in self._traits() if trait.traitType == traitType), None)

		if item is not None:
			return item.value

		return 0

	def _traits(self) -> [Trait]:
		return self._data().traits

	def _data(self) -> LeaderTypeData:
		if self == LeaderType.alexander:
			return LeaderTypeData(
				name='Alexander',
				civilization=CivilizationType.greek,
				ability=LeaderAbility.none,
				flavors=[
					Flavor(FlavorType.cityDefense, 5),
					Flavor(FlavorType.culture, 7),
					Flavor(FlavorType.defense, 5),
					Flavor(FlavorType.diplomacy, 9),
					Flavor(FlavorType.expansion, 8),
					Flavor(FlavorType.gold, 3),
					Flavor(FlavorType.growth, 4),
					Flavor(FlavorType.amenities, 5),
					Flavor(FlavorType.infrastructure, 4),
					Flavor(FlavorType.militaryTraining, 5),
					Flavor(FlavorType.mobile, 8),
					Flavor(FlavorType.naval, 5),
					Flavor(FlavorType.navalGrowth, 6),
					Flavor(FlavorType.navalRecon, 5),
					Flavor(FlavorType.navalTileImprovement, 6),
					Flavor(FlavorType.offense, 8),
					Flavor(FlavorType.production, 5),
					Flavor(FlavorType.recon, 5),
					Flavor(FlavorType.science, 6),
					Flavor(FlavorType.tileImprovement, 4),
					Flavor(FlavorType.wonder, 6)
				],
				traits=[Trait(TraitType.boldness, 8)]
			)
		elif self == LeaderType.trajan:
			return LeaderTypeData(
				name='Trajan',
				civilization=CivilizationType.roman,
				ability=LeaderAbility.trajansColumn,
				flavors=[
					Flavor(FlavorType.cityDefense, 5),
					Flavor(FlavorType.culture, 5),
					Flavor(FlavorType.defense, 6),
					Flavor(FlavorType.diplomacy, 5),
					Flavor(FlavorType.expansion, 8),
					Flavor(FlavorType.gold, 6),
					Flavor(FlavorType.growth, 5),
					Flavor(FlavorType.amenities, 8),
					Flavor(FlavorType.infrastructure, 8),
					Flavor(FlavorType.militaryTraining, 7),
					Flavor(FlavorType.mobile, 4),
					Flavor(FlavorType.naval, 5),
					Flavor(FlavorType.navalGrowth, 4),
					Flavor(FlavorType.navalRecon, 5),
					Flavor(FlavorType.navalTileImprovement, 4),
					Flavor(FlavorType.offense, 5),
					Flavor(FlavorType.production, 6),
					Flavor(FlavorType.recon, 3),
					Flavor(FlavorType.science, 5),
					Flavor(FlavorType.tileImprovement, 7),
					Flavor(FlavorType.wonder, 6)
				],
				traits=[Trait(TraitType.boldness, 6)]
			)
		elif self == LeaderType.victoria:
			return LeaderTypeData(
				name='Alexander',
				civilization=CivilizationType.english,
				ability=LeaderAbility.none,
				flavors=[
					Flavor(FlavorType.cityDefense, 6),
					Flavor(FlavorType.culture, 6),
					Flavor(FlavorType.defense, 6),
					Flavor(FlavorType.diplomacy, 6),
					Flavor(FlavorType.expansion, 6),
					Flavor(FlavorType.gold, 8),
					Flavor(FlavorType.growth, 4),
					Flavor(FlavorType.amenities, 5),
					Flavor(FlavorType.infrastructure, 5),
					Flavor(FlavorType.militaryTraining, 5),
					Flavor(FlavorType.mobile, 3),
					Flavor(FlavorType.naval, 8),
					Flavor(FlavorType.navalGrowth, 7),
					Flavor(FlavorType.navalRecon, 8),
					Flavor(FlavorType.navalTileImprovement, 7),
					Flavor(FlavorType.offense, 3),
					Flavor(FlavorType.production, 6),
					Flavor(FlavorType.recon, 6),
					Flavor(FlavorType.science, 6),
					Flavor(FlavorType.tileImprovement, 6),
					Flavor(FlavorType.wonder, 5)
				],
				traits=[Trait(TraitType.boldness, 4)]
			)

		elif self == LeaderType.none:
			return LeaderTypeData(
				name='None',
				civilization=CivilizationType.none,
				ability=LeaderAbility.none,
				flavors=[],
				traits=[]
			)
		elif self == LeaderType.cityState:
			return LeaderTypeData(
				name='CityState',
				civilization=CivilizationType.cityState,
				ability=LeaderAbility.none,
				flavors=[],
				traits=[]
			)
		elif self == LeaderType.barbar:
			return LeaderTypeData(
				name='Barbar',
				civilization=CivilizationType.barbarian,
				ability=LeaderAbility.none,
				flavors=[],
				traits=[]
			)

		raise InvalidEnumError(self)


class LeaderWeightList(dict):
	def __init__(self):
		super().__init__()
		for leaderType in list(LeaderType):
			self[leaderType.name] = 0