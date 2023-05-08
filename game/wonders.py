from typing import Optional

from game.flavors import Flavor, FlavorType
from game.greatworks import GreatWorkSlotType
from game.types import CivicType, TechType, EraType
from map.types import Yields
from utils.base import ExtendedEnum


class WonderTypeData:
	def __init__(self, name: str, effects: [str], era: EraType, productionCost: int, requiredTech: Optional[TechType],
	             requiredCivic: Optional[CivicType], amenities: float, yields: Yields, slots: [GreatWorkSlotType],
	             flavours: [Flavor]):
		self.name = name
		self.effects = effects
		self.era = era
		self.productionCost = productionCost
		self.requiredTech = requiredTech
		self.requiredCivic = requiredCivic
		self.amenities = amenities
		self.yields = yields
		self.slots = slots
		self.flavours = flavours


class WonderType(ExtendedEnum):
	# default
	none = 'none'

	# ancient
	greatBath = 'greatBath'
	etemenanki = 'etemenanki'
	pyramids = 'pyramids'
	hangingGardens = 'hangingGardens'
	oracle = 'oracle'
	stonehenge = 'stonehenge'
	templeOfArtemis = 'templeOfArtemis'

	# classical
	greatLighthouse = 'greatLighthouse'
	greatLibrary = 'greatLibrary'
	apadana = 'apadana'
	colosseum = 'colosseum'
	colossus = 'colossus'
	jebelBarkal = 'jebelBarkal'
	mausoleumAtHalicarnassus = 'mausoleumAtHalicarnassus'
	mahabodhiTemple = 'mahabodhiTemple'
	petra = 'petra'
	terracottaArmy = 'terracottaArmy'
	machuPicchu = 'machuPicchu'
	statueOfZeus = 'statueOfZeus'

	# ???
	hueyTeocalli = 'hueyTeocalli'
	stBasilsCathedral = 'stBasilsCathedral'

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def _data(self) -> WonderTypeData:
		# default
		if self == WonderType.none:
			return WonderTypeData(
				name='',
				effects=[],
				era=EraType.ancient,
				productionCost=-1,
				requiredTech=None,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavours=[]
			)

		# ancient
		elif self == WonderType.greatBath:
			# https://civilization.fandom.com/wiki/Great_Bath_(Civ6)
			return WonderTypeData(
				name="TXT_KEY_WONDER_GREAT_BATH_TITLE",
				effects=[
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT1',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT2',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT3',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT4',
					'TXT_KEY_WONDER_GREAT_BATH_EFFECT5'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.pottery,
				requiredCivic=None,
				amenities=1.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, housing=3.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.wonder, value=15),
					Flavor(FlavorType.religion, value=10)
				]
			)
		elif self == WonderType.etemenanki:
			# https://civilization.fandom.com/wiki/Etemenanki_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_ETEMENANKI_TITLE',
				effects=[
					'TXT_KEY_WONDER_ETEMENANKI_EFFECT1',
					'TXT_KEY_WONDER_ETEMENANKI_EFFECT2',
					'TXT_KEY_WONDER_ETEMENANKI_EFFECT3'
				],
				era=EraType.ancient,
				productionCost=220,
				requiredTech=TechType.writing,
				requiredCivic=None,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=2.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.science, value=7),
					Flavor(FlavorType.production, value=3)
				]
			)
		elif self == WonderType.pyramids:
			# https://civilization.fandom.com/wiki/Pyramids_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_PYRAMIDS_TITLE',
				effects=[
					'TXT_KEY_WONDER_PYRAMIDS_EFFECT1',
					'TXT_KEY_WONDER_PYRAMIDS_EFFECT2',
					'TXT_KEY_WONDER_PYRAMIDS_EFFECT3'
				],
				era=EraType.ancient,
				productionCost=220,
				requiredTech=TechType.masonry,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=2.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.wonder, value=25),
					Flavor(FlavorType.culture, value=20)
				]
			)
		elif self == WonderType.hangingGardens:
			# https://civilization.fandom.com/wiki/Hanging_Gardens_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_HANGING_GARDENS_TITLE',
				effects=[
					'TXT_KEY_WONDER_HANGING_GARDENS_EFFECT1',
					'TXT_KEY_WONDER_HANGING_GARDENS_EFFECT2'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.irrigation,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, housing=2.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.wonder, value=20),
					Flavor(FlavorType.growth, value=20)
				]
			)
		elif self == WonderType.oracle:
			# https://civilization.fandom.com/wiki/Oracle_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_ORACLE_TITLE',
				effects=[
					'TXT_KEY_WONDER_ORACLE_EFFECT1',
					'TXT_KEY_WONDER_ORACLE_EFFECT2',
					'TXT_KEY_WONDER_ORACLE_EFFECT3',  #
					'TXT_KEY_WONDER_ORACLE_EFFECT4'
				],
				era=EraType.ancient,
				productionCost=290,
				requiredTech=None,
				requiredCivic=CivicType.mysticism,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=1.0, faith=1.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.wonder, value=20),
					Flavor(FlavorType.culture, value=15)
				]
			)
		elif self == WonderType.stonehenge:
			# https://civilization.fandom.com/wiki/Stonehenge_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_STONEHENGE_TITLE',
				effects=[
					'TXT_KEY_WONDER_STONEHENGE_EFFECT1',
					'TXT_KEY_WONDER_STONEHENGE_EFFECT2'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.astrology,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=2.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.wonder, value=25),
					Flavor(FlavorType.culture, value=20)
				]
			)
		elif self == WonderType.templeOfArtemis:
			# https://civilization.fandom.com/wiki/Temple_of_Artemis_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_TITLE',
				effects=[
					'TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_EFFECT1',
					'TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_EFFECT2',
					'TXT_KEY_WONDER_TEMPLE_OF_ARTEMIS_EFFECT3'
				],
				era=EraType.ancient,
				productionCost=180,
				requiredTech=TechType.archery,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=4.0, production=0.0, gold=0.0, housing=3.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.wonder, value=20),
					Flavor(FlavorType.growth, value=10)
				]
			)

		# classical
		elif self == WonderType.greatLighthouse:
			# https://civilization.fandom.com/wiki/Great_Lighthouse_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_GREAT_LIGHTHOUSE_TITLE',
				effects=[
					'TXT_KEY_WONDER_GREAT_LIGHTHOUSE_EFFECT1',
					'TXT_KEY_WONDER_GREAT_LIGHTHOUSE_EFFECT2',
					'TXT_KEY_WONDER_GREAT_LIGHTHOUSE_EFFECT3'
				],
				era=EraType.classical,
				productionCost=290,
				requiredTech=TechType.celestialNavigation,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=3.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.greatPeople, value=20),
					Flavor(FlavorType.gold, value=15),
					Flavor(FlavorType.navalGrowth, value=10),
					Flavor(FlavorType.navalRecon, value=8)
				]
			)
		elif self == WonderType.greatLibrary:
			# https://civilization.fandom.com/wiki/Great_Library_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_GREAT_LIBRARY_TITLE',
				effects=[
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT1',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT2',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT3',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT4',
					'TXT_KEY_WONDER_GREAT_LIBRARY_EFFECT5'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.recordedHistory,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=2.0),
				slots=[GreatWorkSlotType.written, GreatWorkSlotType.written],
				flavours=[
					Flavor(FlavorType.science, value=20),
					Flavor(FlavorType.greatPeople, value=15)
				]
			)
		elif self == WonderType.apadana:
			# https://civilization.fandom.com/wiki/Apadana_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_APADANA_TITLE',
				effects=[
					'TXT_KEY_WONDER_APADANA_EFFECT1',
					'TXT_KEY_WONDER_APADANA_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.politicalPhilosophy,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[GreatWorkSlotType.any, GreatWorkSlotType.any],
				flavours=[
					Flavor(FlavorType.diplomacy, value=20),
					Flavor(FlavorType.culture, value=7)
				]
			)
		elif self == WonderType.colosseum:
			# https://civilization.fandom.com/wiki/Colosseum_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_COLOSSEUM_TITLE',
				effects=[
					'TXT_KEY_WONDER_COLOSSEUM_EFFECT1'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.gamesAndRecreation,
				amenities=0.0, # is handled differently !
				yields=Yields(food=0.0, production=0.0, gold=0.0, culture=2.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.amenities, value=20),
					Flavor(FlavorType.culture, value=10)
				]
			)
		elif self == WonderType.colossus:
			# https://civilization.fandom.com/wiki/Colossus_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_COLOSSUS_TITLE',
				effects=[
					'TXT_KEY_WONDER_COLOSSUS_EFFECT1',
					'TXT_KEY_WONDER_COLOSSUS_EFFECT2',
					'TXT_KEY_WONDER_COLOSSUS_EFFECT3',
					'TXT_KEY_WONDER_COLOSSUS_EFFECT4'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.shipBuilding,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=3.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.gold, value=12),
					Flavor(FlavorType.naval, value=14),
					Flavor(FlavorType.navalRecon, value=3)
				]
			)
		elif self == WonderType.jebelBarkal:
			# https://civilization.fandom.com/wiki/Jebel_Barkal_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_JEBEL_BARKAL_TITLE',
				effects=[
					'TXT_KEY_WONDER_JEBEL_BARKAL_EFFECT1',  #
					'TXT_KEY_WONDER_JEBEL_BARKAL_EFFECT2'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.ironWorking,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.religion, value=12),
					Flavor(FlavorType.tileImprovement, value=7)
				]
			)
		elif self == WonderType.mausoleumAtHalicarnassus:
			# https://civilization.fandom.com/wiki/Mausoleum_at_Halicarnassus_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_MAUSOLEUM_AT_HALICARNASSUS_TITLE',
				effects=[
					'TXT_KEY_WONDER_MAUSOLEUM_AT_HALICARNASSUS_EFFECT1',
					'TXT_KEY_WONDER_MAUSOLEUM_AT_HALICARNASSUS_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.defensiveTactics,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, science=1.0, faith=1.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.tileImprovement, value=7),
					Flavor(FlavorType.science, value=5),
					Flavor(FlavorType.religion, value=5),
					Flavor(FlavorType.culture, value=7)
				]
			)
		elif self == WonderType.mahabodhiTemple:
			# https://civilization.fandom.com/wiki/Mahabodhi_Temple_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_MAHABODHI_TEMPLE_TITLE',
				effects=[
					'TXT_KEY_WONDER_MAHABODHI_TEMPLE_EFFECT1',
					'TXT_KEY_WONDER_MAHABODHI_TEMPLE_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.theology,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0, faith=4.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.religion, value=20),
					Flavor(FlavorType.greatPeople, value=7)
				]
			)
		elif self == WonderType.petra:
			# https://civilization.fandom.com/wiki/Petra_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_PETRA_TITLE',
				effects=[
					'TXT_KEY_WONDER_ETRA_EFFECT1'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.mathematics,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=2.0, production=1.0, gold=2.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.tileImprovement, value=10),
					Flavor(FlavorType.growth, value=12),
					Flavor(FlavorType.gold, value=10)
				]
			)
		elif self == WonderType.terracottaArmy:
			# https://civilization.fandom.com/wiki/Terracotta_Army_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_TERRACOTTA_ARMY_TITLE',
				effects=[
					'TXT_KEY_WONDER_TERRACOTTA_ARMY_EFFECT1',
					'TXT_KEY_WONDER_TERRACOTTA_ARMY_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.construction,
				requiredCivic=None,
				amenities=0.0,
				yields=Yields(food=0.0, production=0.0, gold=0.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.greatPeople, value=10),
					Flavor(FlavorType.militaryTraining, value=7)
				]
			)
		elif self == WonderType.machuPicchu:
			# https://civilization.fandom.com/wiki/Machu_Picchu_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_MACHU_PICCHU_TITLE',
				effects=[
					'TXT_KEY_WONDER_MACHU_PICCHU_EFFECT1',
					'TXT_KEY_WONDER_MACHU_PICCHU_EFFECT2'  #
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=TechType.engineering,
				requiredCivic=None,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=4.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.production, value=7)
				]
			)
		elif self == WonderType.statueOfZeus:
			# https://civilization.fandom.com/wiki/Statue_of_Zeus_(Civ6)
			return WonderTypeData(
				name='TXT_KEY_WONDER_STATUE_OF_ZEUS_TITLE',
				effects=[
					'TXT_KEY_WONDER_STATUE_OF_ZEUS_EFFECT1',
					'TXT_KEY_WONDER_STATUE_OF_ZEUS_EFFECT2',
					'TXT_KEY_WONDER_STATUE_OF_ZEUS_EFFECT3'
				],
				era=EraType.classical,
				productionCost=400,
				requiredTech=None,
				requiredCivic=CivicType.militaryTraining,
				amenities=0,
				yields=Yields(food=0.0, production=0.0, gold=3.0),
				slots=[],
				flavours=[
					Flavor(FlavorType.gold, value=7)
				]
			)

		raise AttributeError(f'cant get data for wonder {self}')
