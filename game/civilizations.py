from game.flavors import FlavorType, Flavor
from core.base import ExtendedEnum, InvalidEnumError, WeightedBaseList


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
	workshopOfTheWorld = 'workshopOfTheWorld'
	platosRepublic = 'platosRepublic'
	grandTour = 'grandTour'
	iteru = 'iteru'
	satrapies = 'satrapies'

	def name(self) -> str:
		return 'ability'


class CivilizationData:
	def __init__(self, name: str, ability: CivilizationAbility, cityNames: [str]):
		self.name = name
		self.ability = ability
		self.cityNames = cityNames


class CivilizationType(ExtendedEnum):
	none = 'none'
	unmet = 'unmet'
	barbarian = 'barbarian'
	free = 'free'
	cityState = 'cityState'

	greek = 'greek'
	roman = 'roman'
	english = 'english'
	russian = 'russian'

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
				ability=CivilizationAbility.none,
				cityNames=[]
			)
		elif self == CivilizationType.barbarian:
			return CivilizationData(
				name='Barbarian',
				ability=CivilizationAbility.none,
				cityNames=[]
			)
		elif self == CivilizationType.free:
			return CivilizationData(
				name='Free',
				ability=CivilizationAbility.none,
				cityNames=[]
			)
		elif self == CivilizationType.unmet:
			return CivilizationData(
				name='Unmet',
				ability=CivilizationAbility.none,
				cityNames=[]
			)
		elif self == CivilizationType.cityState:
			return CivilizationData(
				name='CityState',
				ability=CivilizationAbility.none,
				cityNames=[]
			)

		elif self == CivilizationType.greek:
			# https://civilization.fandom.com/wiki/Greek_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Greek_cities_(Civ6)
			return CivilizationData(
				name='TXT_KEY_CIVILIZATION_GREEK',
				ability=CivilizationAbility.platosRepublic,
				cityNames=[
					"TXT_KEY_CITY_NAME_ATHENS",
					"TXT_KEY_CITY_NAME_SPARTA",
					"TXT_KEY_CITY_NAME_CORINTH",
					"TXT_KEY_CITY_NAME_EPHESUS",
					"TXT_KEY_CITY_NAME_ARGOS",
					"TXT_KEY_CITY_NAME_KNOSSOS",
					"TXT_KEY_CITY_NAME_MYCENAE",
					"TXT_KEY_CITY_NAME_PHARSALOS",
					"TXT_KEY_CITY_NAME_RHODES",
					"TXT_KEY_CITY_NAME_OLYMPIA",
					"TXT_KEY_CITY_NAME_ERETRIA",
					"TXT_KEY_CITY_NAME_PERGAMON",
					"TXT_KEY_CITY_NAME_MILETOS",
					"TXT_KEY_CITY_NAME_MEGARA",
					"TXT_KEY_CITY_NAME_PHOCAEA",
					"TXT_KEY_CITY_NAME_DELPHI",
					"TXT_KEY_CITY_NAME_MARATHON",
					"TXT_KEY_CITY_NAME_PATRAS"
				]
			)
		elif self == CivilizationType.roman:
			# https://civilization.fandom.com/wiki/Roman_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Roman_cities_(Civ6)
			return CivilizationData(
				name="TXT_KEY_CIVILIZATION_ROMAN",
				ability=CivilizationAbility.allRoadsLeadToRome,
				cityNames=[
					"TXT_KEY_CITY_NAME_ROME",
					"TXT_KEY_CITY_NAME_OSTIA",
					"TXT_KEY_CITY_NAME_ANTIUM",
					"TXT_KEY_CITY_NAME_CUMAE",
					"TXT_KEY_CITY_NAME_AQUILEIA",
					"TXT_KEY_CITY_NAME_RAVENNA",
					"TXT_KEY_CITY_NAME_PUTEOLI",
					"TXT_KEY_CITY_NAME_ARRETIUM",
					"TXT_KEY_CITY_NAME_MEDIOLANUM",
					"TXT_KEY_CITY_NAME_LUGDUNUM",
					"TXT_KEY_CITY_NAME_ARPINUM",
					"TXT_KEY_CITY_NAME_SETIA",
					"TXT_KEY_CITY_NAME_VELITRAE",
					"TXT_KEY_CITY_NAME_DUROCORTORUM",
					"TXT_KEY_CITY_NAME_BRUNDISIUM",
					"TXT_KEY_CITY_NAME_CAESARAUGUSTA",
					"TXT_KEY_CITY_NAME_PALMYRA",
					"TXT_KEY_CITY_NAME_HISPALIS",
					"TXT_KEY_CITY_NAME_CAESAREA",
					"TXT_KEY_CITY_NAME_ARTAXATA",
					"TXT_KEY_CITY_NAME_PAPHOS",
					"TXT_KEY_CITY_NAME_SALONAE",
					"TXT_KEY_CITY_NAME_EBURACUM",
					"TXT_KEY_CITY_NAME_LAURIACUM",
					"TXT_KEY_CITY_NAME_VERONA",
					"TXT_KEY_CITY_NAME_COLONIA_AGRIPPINA",
					"TXT_KEY_CITY_NAME_NARBO",
					"TXT_KEY_CITY_NAME_TINGI",
					"TXT_KEY_CITY_NAME_SARMIZEGETUSA",
					"TXT_KEY_CITY_NAME_SIRMIUM"
				]
			)
		elif self == CivilizationType.english:
			#
			# cities taken from here: https://civilization.fandom.com/wiki/English_cities_(Civ6)
			return CivilizationData(
				name='TXT_KEY_CIVILIZATION_ENGLISH',
				ability=CivilizationAbility.workshopOfTheWorld,
				cityNames=[
					"TXT_KEY_CITY_NAME_LONDON",
					"TXT_KEY_CITY_NAME_LIVERPOOL",
					"TXT_KEY_CITY_NAME_MANCHESTER",
					"TXT_KEY_CITY_NAME_BIRMINGHAM",
					"TXT_KEY_CITY_NAME_LEEDS",
					"TXT_KEY_CITY_NAME_SHEFFIELD",
					"TXT_KEY_CITY_NAME_BRISTOL",
					"TXT_KEY_CITY_NAME_PLYMOUTH",
					"TXT_KEY_CITY_NAME_NEWCASTLE_UPON_TYNE",
					"TXT_KEY_CITY_NAME_BRADFORD",
					"TXT_KEY_CITY_NAME_STOKE_UPON_TRENT",
					"TXT_KEY_CITY_NAME_HULL",
					"TXT_KEY_CITY_NAME_PORTSMOUTH",
					"TXT_KEY_CITY_NAME_PRESTON",
					"TXT_KEY_CITY_NAME_SUNDERLAND",
					"TXT_KEY_CITY_NAME_BRIGHTON",
					"TXT_KEY_CITY_NAME_NORWICH",
					"TXT_KEY_CITY_NAME_YORK",
					"TXT_KEY_CITY_NAME_NOTTINGHAM",
					"TXT_KEY_CITY_NAME_LEICESTER",
					"TXT_KEY_CITY_NAME_BLACKBURN",
					"TXT_KEY_CITY_NAME_WOLVERHAMPTON",
					"TXT_KEY_CITY_NAME_BATH",
					"TXT_KEY_CITY_NAME_COVENTRY",
					"TXT_KEY_CITY_NAME_EXETER",
					"TXT_KEY_CITY_NAME_LINCOLN",
					"TXT_KEY_CITY_NAME_CANTERBURY",
					"TXT_KEY_CITY_NAME_IPSWICH",
					"TXT_KEY_CITY_NAME_DOVER",
					"TXT_KEY_CITY_NAME_HASTINGS",
					"TXT_KEY_CITY_NAME_OXFORD",
					"TXT_KEY_CITY_NAME_SHREWSBURY",
					"TXT_KEY_CITY_NAME_CAMBRIDGE",
					"TXT_KEY_CITY_NAME_NEWCASTLE",
					"TXT_KEY_CITY_NAME_WARWICK"
				]
			)
		elif self == CivilizationType.russian:
			# https://civilization.fandom.com/wiki/Russian_(Civ6)
			# cities taken from here: https://civilization.fandom.com/wiki/Russian_cities_(Civ6)
			return CivilizationData(
				name='TXT_KEY_CIVILIZATION_RUSSIAN',
				ability=CivilizationAbility.motherRussia,
				cityNames=[
					"TXT_KEY_CITY_NAME_ST_PETERSBURG",
					"TXT_KEY_CITY_NAME_MOSCOW",
					"TXT_KEY_CITY_NAME_NOVGOROD",
					"TXT_KEY_CITY_NAME_KAZAN",
					"TXT_KEY_CITY_NAME_ASTRAKHAN",
					"TXT_KEY_CITY_NAME_YAROSLAVL",
					"TXT_KEY_CITY_NAME_SMOLENSK",
					"TXT_KEY_CITY_NAME_VORONEZH",
					"TXT_KEY_CITY_NAME_TULA",
					"TXT_KEY_CITY_NAME_SOLIKAMSK",
					"TXT_KEY_CITY_NAME_TVER",
					"TXT_KEY_CITY_NAME_NIZHNIY_NOVGOROD",
					"TXT_KEY_CITY_NAME_ARKHANGELSK",
					"TXT_KEY_CITY_NAME_VOLOGDA",
					"TXT_KEY_CITY_NAME_OLONETS",
					"TXT_KEY_CITY_NAME_SARATOV",
					"TXT_KEY_CITY_NAME_TAMBOV",
					"TXT_KEY_CITY_NAME_PSKOV",
					"TXT_KEY_CITY_NAME_KRASNOYARSK",
					"TXT_KEY_CITY_NAME_IRKUTSK",
					"TXT_KEY_CITY_NAME_YEKATERINBURG",
					"TXT_KEY_CITY_NAME_ROSTOV",
					"TXT_KEY_CITY_NAME_BRYANSK",
					"TXT_KEY_CITY_NAME_YAKUTSK",
					"TXT_KEY_CITY_NAME_STARAYA_RUSSA",
					"TXT_KEY_CITY_NAME_PERM",
					"TXT_KEY_CITY_NAME_PETROZAVODSK",
					"TXT_KEY_CITY_NAME_OKHOTSK",
					"TXT_KEY_CITY_NAME_KOSTROMA",
					"TXT_KEY_CITY_NAME_NIZHNEKOLYMSK",
					"TXT_KEY_CITY_NAME_SERGIYEV_POSAD",
					"TXT_KEY_CITY_NAME_OMSK"
				]
			)


		raise InvalidEnumError(self)

	def cityNames(self):
		return self._data().cityNames


class WeightedCivilizationList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for civilization in list(CivilizationType):
			self.setWeight(0.0, civilization)


class LeaderAbility(ExtendedEnum):
	none = 'none'
	trajansColumn = 'trajansColumn'  # trajan, roman
	westernizer = 'westernizer'  # peter, russian


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
	peter = 'peter'

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
		elif self == LeaderType.peter:
			return LeaderTypeData(
				name='Peter',
				civilization=CivilizationType.russian,
				ability=LeaderAbility.westernizer,
				flavors=[
				],
				traits=[Trait(TraitType.boldness, 6)]
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