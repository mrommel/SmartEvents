import unittest

from game.baseTypes import HandicapType
from game.cities import City
from game.civilizations import LeaderType
from game.combat import Combat
from game.game import GameModel
from game.players import Player
from game.policyCards import PolicyCardType
from game.promotions import CombatModifier, UnitPromotionType
from game.states.victories import VictoryType
from game.types import CivicType
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint
from map.map import Tile
from map.types import TerrainType, MapSize
from tests.testBasics import MapModelMock, UserInterfaceMock, BetweenAssertMixin


class TestCombatModifier(unittest.TestCase):
	def test_defensive_combat_modifier(self):
		# GIVEN

		# players
		barbarianPlayer = Player(LeaderType.barbar, human=False)
		barbarianPlayer.initialize()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		playerAlexander = Player(LeaderType.alexander, human=True)
		playerAlexander.initialize()

		# map
		mapModel = MapModelMock(MapSize.duel, TerrainType.grass)

		# game
		gameModel = GameModel(
			victoryTypes=[VictoryType.domination, VictoryType.cultural, VictoryType.diplomatic],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[barbarianPlayer, playerTrajan, playerAlexander],
			map=mapModel
		)

		warrior = Unit(HexPoint(5, 6), UnitType.warrior, playerTrajan)
		gameModel.addUnit(warrior)

		barbarianWarrior = Unit(HexPoint(5, 7), UnitType.warrior, barbarianPlayer)
		gameModel.addUnit(barbarianWarrior)

		# WHEN
		modifiersBarbarian = barbarianWarrior.defensiveStrengthModifierAgainst(None, None, None, ranged=False, simulation=gameModel)
		modifiersNormal = warrior.defensiveStrengthModifierAgainst(None, None, None, ranged=False, simulation=gameModel)

		# policy twilightValor
		playerTrajan.government.addCard(PolicyCardType.twilightValor)
		modifiersTwilightValor = warrior.defensiveStrengthModifierAgainst(None, None, None, ranged=False, simulation=gameModel)
		playerTrajan.government.removeCard(PolicyCardType.twilightValor)

		# hills
		tile = Tile(HexPoint(5, 5), TerrainType.grass)
		tile.setHills(True)
		modifiersHills = warrior.defensiveStrengthModifierAgainst(None, None, tile, ranged=False, simulation=gameModel)

		# promotion
		warrior.doPromote(UnitPromotionType.battlecry, gameModel)
		modifiersPromotion = warrior.defensiveStrengthModifierAgainst(barbarianWarrior, None, None, ranged=False, simulation=gameModel)

		# THEN
		self.assertEqual(modifiersBarbarian, [])  # no modifiers for barbarians
		self.assertEqual(modifiersNormal, [CombatModifier(-1, "Bonus due to difficulty")])
		self.assertListEqual(modifiersTwilightValor, [
			CombatModifier(5, "TXT_KEY_POLICY_CARD_TWILIGHT_VALOR_TITLE"),
			CombatModifier(-1, "Bonus due to difficulty")
		])
		self.assertListEqual(modifiersHills, [
			CombatModifier(3, "Ideal terrain"),
			CombatModifier(-1, "Bonus due to difficulty")
		])
		self.assertListEqual(modifiersPromotion, [
			CombatModifier(-1, "Bonus due to difficulty"),
			CombatModifier(7, "TXT_KEY_UNIT_PROMOTION_BATTLECRY_NAME")
		])


class TestCombat(unittest.TestCase, BetweenAssertMixin):
	def setUp(self) -> None:
		# players
		self.barbarianPlayer = Player(LeaderType.barbar, human=False)
		self.barbarianPlayer.initialize()

		self.playerTrajan = Player(LeaderType.trajan, human=False)
		self.playerTrajan.initialize()

		self.playerAlexander = Player(LeaderType.alexander, human=True)
		self.playerAlexander.initialize()

		# map
		self.mapModel = MapModelMock(MapSize.duel, TerrainType.grass)

		# game
		self.gameModel = GameModel(
			victoryTypes=[VictoryType.domination, VictoryType.cultural, VictoryType.diplomatic],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.barbarianPlayer, self.playerTrajan, self.playerAlexander],
			map=self.mapModel
		)
		self.gameModel.userInterface = UserInterfaceMock()

		self.playerTrajan.doFirstContactWith(self.playerAlexander, self.gameModel)

	def test_predict_warrior_against_warrior(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(attacker)

		defender = Unit(HexPoint(6, 6), UnitType.warrior, self.playerTrajan)
		self.gameModel.addUnit(attacker)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, defender, self.gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 26)
		self.assertEqual(result.defenderDamage, 33)

	def test_predict_warrior_against_warrior_flanking(self):
		# GIVEN
		self.playerAlexander.civics.discover(CivicType.militaryTradition, self.gameModel)

		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(attacker)

		flanking = Unit(HexPoint(5, 5), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(flanking)

		defender = Unit(HexPoint(6, 5), UnitType.warrior, self.playerTrajan)
		self.gameModel.addUnit(attacker)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, defender, self.gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 24)
		self.assertEqual(result.defenderDamage, 36)

	def test_predict_warrior_against_capital(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.gameModel)
		self.gameModel.addCity(city)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, city, self.gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 22)
		self.assertEqual(result.defenderDamage, 17)
		self.assertEqual(city.maxHealthPoints(), 200)

	def test_predict_warrior_against_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=False, player=self.playerTrajan)
		city.initialize(self.gameModel)
		self.gameModel.addCity(city)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, city, self.gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 22)
		self.assertEqual(result.defenderDamage, 48)
		self.assertEqual(city.maxHealthPoints(), 200)

	def test_predict_city_against_warrior(self):
		# GIVEN
		defender = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(defender)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.gameModel)
		self.gameModel.addCity(city)

		# WHEN
		result = Combat.predictRangedAttack(city, defender, self.gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 0)
		self.assertEqual(result.defenderDamage, 22)

	def test_combat_warrior_against_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.gameModel)
		self.gameModel.addCity(city)

		# WHEN
		result = Combat.doMeleeAttack(attacker, city, self.gameModel)

		# THEN
		self.assertBetween(result.attackerDamage, 21, 23)
		self.assertBetween(result.defenderDamage, 16, 21)

	def test_conquer_city(self):
		# GIVEN
		attacker = Unit(HexPoint(5, 6), UnitType.warrior, self.playerAlexander)
		self.gameModel.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.gameModel)
		city.setDamage(190)
		self.gameModel.addCity(city)

		city2 = City("Potsdam", HexPoint(10, 5), isCapital=False, player=self.playerTrajan)
		city2.initialize(self.gameModel)
		self.gameModel.addCity(city2)

		numberOfCitiesBefore = len(self.gameModel.citiesOf(self.playerTrajan))

		# WHEN
		result = Combat.doMeleeAttack(attacker, city, self.gameModel)

		# THEN
		self.assertBetween(result.attackerDamage, 21, 23)
		self.assertBetween(result.defenderDamage, 16, 21)

		cityAtLocation = self.gameModel.cityAt(HexPoint(5, 5))
		numberOfCitiesAfter = len(self.gameModel.citiesOf(self.playerTrajan))
		self.assertEqual(cityAtLocation.player.leader, LeaderType.alexander)
		self.assertEqual(numberOfCitiesBefore, 2)
		self.assertEqual(numberOfCitiesAfter, 1)
