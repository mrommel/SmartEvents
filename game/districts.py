from typing import Optional

from game.flavors import Flavor, FlavorType
from game.types import CivicType, TechType
from map.types import Yields
from utils.base import ExtendedEnum


class DistrictTypeData:
	def __init__(self, name: str, specialty: bool, effects: [str], productionCost: int, maintenanceCost: int,
	             requiredTech: Optional[TechType], requiredCivic: Optional[CivicType], domesticTradeYields: Yields,
	             foreignTradeYields: Yields, flavours: [Flavor], oncePerCivilization: bool = False):
		self.name = name
		self.specialty = specialty
		self.effects = effects
		self.productionCost = productionCost
		self.maintenanceCost = maintenanceCost
		self.requiredTech = requiredTech
		self.requiredCivic = requiredCivic

		self.domesticTradeYields = domesticTradeYields
		self.foreignTradeYields = foreignTradeYields

		self.flavours = flavours
		self.oncePerCivilization = oncePerCivilization


class DistrictType(ExtendedEnum):
	none = 'none'

	cityCenter = 'cityCenter'
	preserve = 'preserve'
	encampment = 'encampment'
	campus = 'campus'
	entertainmentComplex = 'entertainmentComplex'
	commercialHub = 'commercialHub'
	harbor = 'harbor'
	holySite = 'holySite'

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def _data(self) -> DistrictTypeData:
		if self == DistrictType.none:
			return DistrictTypeData(
				name="",
				specialty=False,
				effects=[],
				productionCost=-1,
				maintenanceCost=-1,
				requiredTech=None,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0),
				flavours=[]
			)
		elif self == DistrictType.cityCenter:
			# https://civilization.fandom.com/wiki/City_Center_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_CITY_CENTER_TITLE",
				specialty=False,
				effects=[
					'TXT_KEY_DISTRICT_CITY_CENTER_EFFECT1'
				],
				productionCost=0,
				maintenanceCost=0,
				requiredTech=None,
				requiredCivic=None,
				domesticTradeYields=Yields(food=1.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=3.0),
				flavours=[
					Flavor(FlavorType.cityDefense, 7)
				]
			)
		elif self == DistrictType.preserve:
			# https://civilization.fandom.com/wiki/Preserve_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_PRESERVE_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_PRESERVE_EFFECT1",
					"TXT_KEY_DISTRICT_PRESERVE_EFFECT2",
					"TXT_KEY_DISTRICT_PRESERVE_EFFECT3"
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=None,
				requiredCivic=CivicType.mysticism,
				domesticTradeYields=Yields(food=0, production=0, gold=0),
				foreignTradeYields=Yields(food=0, production=0, gold=0),
				flavours=[
					Flavor(FlavorType.culture, 6)
				]
			)
		elif self == DistrictType.encampment:
			# https://civilization.fandom.com/wiki/Encampment_(Civ6)
			return DistrictTypeData(
				name='TXT_KEY_DISTRICT_ENCAMPMENT_TITLE',
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT1',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT2',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT3',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT4',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT5',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT6',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT7',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT8',
					'TXT_KEY_DISTRICT_ENCAMPMENT_EFFECT9'
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=TechType.bronzeWorking,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				flavours=[
					Flavor(FlavorType.militaryTraining, value=7),
					Flavor(FlavorType.cityDefense, value=3)
				]
			)
		elif self == DistrictType.campus:
			# https://civilization.fandom.com/wiki/Campus_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_CAMPUS_TITLE",
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT1',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT2',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT3',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT4',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT5',
					'TXT_KEY_DISTRICT_CAMPUS_EFFECT6'
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=TechType.writing,
				requiredCivic=None,
				domesticTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0, science=1.0),
				flavours=[
					Flavor(FlavorType.science, 8)
				]
			)
		elif self == DistrictType.entertainmentComplex:
			# https://civilization.fandom.com/wiki/Entertainment_Complex_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT1",
					"TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT2",
					"TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT3",
					"TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT4",
					"TXT_KEY_DISTRICT_ENTERTAINMENT_COMPLEX_EFFECT5"
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=None,
				requiredCivic=CivicType.gamesAndRecreation,
				domesticTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				flavours=[
					Flavor(FlavorType.amenities, 7)
				]
			)
		elif self == DistrictType.commercialHub:
			# https://civilization.fandom.com/wiki/Commercial_Hub_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_COMMERCIAL_HUB_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT1",
					"TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT2",
					"TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT3",
					"TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT4",
					"TXT_KEY_DISTRICT_COMMERCIAL_HUB_EFFECT5"
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=TechType.currency,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=3.0),
				flavours=[
					Flavor(FlavorType.gold, 7)
				]
			)
		elif self == DistrictType.harbor:
			# https://civilization.fandom.com/wiki/Harbor_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_HARBOR_TITLE",
				specialty=True,
				effects=[
					"TXT_KEY_DISTRICT_HARBOR_EFFECT1",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT2",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT3",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT4",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT5",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT6",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT7",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT8",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT9",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT10",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT11",
					"TXT_KEY_DISTRICT_HARBOR_EFFECT12"
				],
				productionCost=54,
				maintenanceCost=0,
				requiredTech=TechType.celestialNavigation,
				requiredCivic=None,
				domesticTradeYields=Yields(food=0.0, production=1.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=3.0),
				flavours=[
					Flavor(FlavorType.naval, value=3),
					Flavor(FlavorType.navalGrowth, value=7)
				]
			)
		elif self == DistrictType.holySite:
			# https://civilization.fandom.com/wiki/Holy_Site_(Civ6)
			return DistrictTypeData(
				name="TXT_KEY_DISTRICT_HOLY_SITE_TITLE",
				specialty=True,
				effects=[
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT1',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT2',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT3',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT4',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT5',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT6',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT7',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT8',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT9',
					'TXT_KEY_DISTRICT_HOLY_SITE_EFFECT10'
				],
				productionCost=54,
				maintenanceCost=1,
				requiredTech=TechType.astrology,
				requiredCivic=None,
				domesticTradeYields=Yields(food=1.0, production=0.0, gold=0.0),
				foreignTradeYields=Yields(food=0.0, production=0.0, gold=0.0, faith=1.0),
				flavours=[
					Flavor(FlavorType.religion, 7)
				]
			)

		raise AttributeError(f'cant get data for district {self}')
