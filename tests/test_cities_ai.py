import unittest

from game.ai.cities import WeightedFlavorList, WeightedYieldList, BuildableType, BuildableItemWeights, BuildingWeights, \
	DistrictWeights, UnitWeights, WonderWeights, CityStrategyAdoptions, CityStrategyType, BuildableItem
from game.buildings import BuildingType
from game.civilizations import WeightedCivilizationList, CivilizationType
from game.districts import DistrictType
from game.flavors import FlavorType
from game.playerMechanics import WeightedCivicList, WeightedTechList
from game.states.builds import BuildType
from game.types import CivicType, TechType
from game.unitTypes import UnitType
from game.wonders import WonderType
from map.base import HexPoint
from map.map import WeightedBuildList
from map.types import YieldType
from utils.base import WeightedStringList


class TestWeightedList(unittest.TestCase):
	def helper(self, cls, types, extra):
		items = cls()
		for item in types:
			items.addWeight(0.5, item)

		items.addWeight(0.01, extra)

		top3Items = items.top3()
		itemsArray = top3Items.distributeByWeight()
		self.assertEqual(len(itemsArray), 100)

		for item in types:
			self.assertIn(item, itemsArray)

	def test_flavors(self):
		self.helper(
			WeightedFlavorList,
			[FlavorType.gold, FlavorType.production, FlavorType.growth],
			FlavorType.wonder
		)

	def test_yields(self):
		self.helper(
			WeightedYieldList,
			[YieldType.gold, YieldType.production, YieldType.food],
			YieldType.science
		)

	def test_civilizations(self):
		self.helper(
			WeightedCivilizationList,
			[CivilizationType.english, CivilizationType.greek, CivilizationType.roman],
			CivilizationType.barbarian
		)

	def test_civics(self):
		self.helper(
			WeightedCivicList,
			[CivicType.mysticism, CivicType.futureCivic, CivicType.naturalHistory],
			CivicType.earlyEmpire
		)

	def test_techs(self):
		self.helper(
			WeightedTechList,
			[TechType.pottery, TechType.steel, TechType.steamPower],
			TechType.archery
		)

	def test_buildables(self):
		self.helper(
			BuildableItemWeights,
			[BuildableType.unit, BuildableType.wonder, BuildableType.project],
			BuildableType.building
		)

	def test_buildings(self):
		self.helper(
			BuildingWeights,
			[BuildingType.palace, BuildingType.library, BuildingType.arena],
			BuildingType.waterMill
		)

	def test_districts(self):
		self.helper(
			DistrictWeights,
			[DistrictType.campus, DistrictType.cityCenter, DistrictType.harbor],
			DistrictType.encampment
		)

	def test_units(self):
		self.helper(
			UnitWeights,
			[UnitType.settler, UnitType.warrior, UnitType.archer],
			UnitType.trebuchet
		)

	def test_wonders(self):
		self.helper(
			WonderWeights,
			[WonderType.etemenanki, WonderType.colosseum, WonderType.colossus],
			WonderType.pyramids
		)

	def test_builds(self):
		self.helper(
			WeightedBuildList,
			[BuildType.removeMarsh, BuildType.removeRainforest, BuildType.pasture],
			BuildType.farm
		)

	def test_strings(self):
		self.helper(
			WeightedStringList,
			["abc", "def", "ghi"],
			"jiu"
		)


class TestBuildableItem(unittest.TestCase):
	def test_constructor(self):
		item = BuildableItem(DistrictType.campus, HexPoint(2, 3))

		self.assertEqual(item.buildableType, BuildableType.district)
		self.assertEqual(item.districtType, DistrictType.campus)
		self.assertEqual(item.location, HexPoint(2, 3))
		self.assertIsNotNone(item.__repr__())

		item = BuildableItem(BuildingType.palace)

		self.assertEqual(item.buildableType, BuildableType.building)
		self.assertEqual(item.buildingType, BuildingType.palace)
		self.assertIsNone(item.location)
		self.assertIsNotNone(item.__repr__())

		item = BuildableItem(UnitType.warrior)

		self.assertEqual(item.buildableType, BuildableType.unit)
		self.assertEqual(item.unitType, UnitType.warrior)
		self.assertIsNone(item.location)
		self.assertIsNotNone(item.__repr__())

		item = BuildableItem(WonderType.colosseum, HexPoint(2, 3))

		self.assertEqual(item.buildableType, BuildableType.wonder)
		self.assertEqual(item.wonderType, WonderType.colosseum)
		self.assertEqual(item.location, HexPoint(2, 3))
		self.assertIsNotNone(item.__repr__())


class TestCityStrategyAdoption(unittest.TestCase):
	def test_constructor(self):
		adoptions = CityStrategyAdoptions()

		for cityStrategyType in list(CityStrategyType):
			self.assertEqual(adoptions.adopted(cityStrategyType), False)
			self.assertEqual(adoptions.turnOfAdoption(cityStrategyType), -1)