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
from tests.testBasics import MapModelMock, UserInterfaceMock


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


class TestCombat(unittest.TestCase):
	def test_combat_warrior_against_warrior(self):
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

		attacker = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		gameModel.addUnit(attacker)

		defender = Unit(HexPoint(6, 6), UnitType.warrior, playerTrajan)
		gameModel.addUnit(attacker)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, defender, gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 26)
		self.assertEqual(result.defenderDamage, 33)

	def test_combat_warrior_against_warrior_flanking(self):
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

		playerAlexander.civics.discover(CivicType.militaryTradition, gameModel)

		attacker = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		gameModel.addUnit(attacker)

		flanking = Unit(HexPoint(5, 5), UnitType.warrior, playerAlexander)
		gameModel.addUnit(flanking)

		defender = Unit(HexPoint(6, 5), UnitType.warrior, playerTrajan)
		gameModel.addUnit(attacker)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, defender, gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 24)
		self.assertEqual(result.defenderDamage, 36)

	def test_combat_warrior_against_capital(self):
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
		gameModel.userInterface = UserInterfaceMock()

		attacker = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		gameModel.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=playerTrajan)
		city.initialize(gameModel)
		gameModel.addCity(city)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, city, gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 22)
		self.assertEqual(result.defenderDamage, 17)
		self.assertEqual(city.maxHealthPoints(), 200)

	def test_combat_warrior_against_city(self):
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
		gameModel.userInterface = UserInterfaceMock()

		attacker = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		gameModel.addUnit(attacker)

		city = City("Berlin", HexPoint(5, 5), isCapital=False, player=playerTrajan)
		city.initialize(gameModel)
		gameModel.addCity(city)

		# WHEN
		result = Combat.predictMeleeAttack(attacker, city, gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 22)
		self.assertEqual(result.defenderDamage, 48)
		self.assertEqual(city.maxHealthPoints(), 200)

	def test_combat_city_against_warrior(self):
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
		gameModel.userInterface = UserInterfaceMock()

		defender = Unit(HexPoint(5, 6), UnitType.warrior, playerAlexander)
		gameModel.addUnit(defender)

		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=playerTrajan)
		city.initialize(gameModel)
		gameModel.addCity(city)

		# WHEN
		result = Combat.predictRangedAttack(city, defender, gameModel)

		# THEN
		self.assertEqual(result.attackerDamage, 0)
		self.assertEqual(result.defenderDamage, 22)
