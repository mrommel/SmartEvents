import copy
import unittest

from game.baseTypes import HandicapType
from game.cities import City
from game.civilizations import LeaderType
from game.game import GameModel
from game.greatPersons import GreatPersonType
from game.players import Player
from game.promotions import UnitPromotionType, UnitPromotions
from game.states.ages import AgeType
from game.states.dedications import DedicationType
from game.states.victories import VictoryType
from game.types import TechType
from game.unitTypes import UnitType
from game.units import Unit
from map.base import HexPoint
from map.improvements import ImprovementType
from map.types import TerrainType
from tests.testBasics import MapModelMock, UserInterfaceMock


class TestUnitPromotions(unittest.TestCase):
	def test_possiblePromotions_melee(self):
		# GIVEN
		playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		playerTrajan.initialize()
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, playerTrajan)
		promotions = UnitPromotions(warrior)

		# WHEN
		initialPromotions = promotions.possiblePromotions()

		promotions.earnPromotion(UnitPromotionType.battlecry)
		promotions.earnPromotion(UnitPromotionType.tortoise)
		secondPromotions = promotions.possiblePromotions()

		# THEN
		self.assertEqual(initialPromotions, [UnitPromotionType.embarkation, UnitPromotionType.healthBoostMelee,
		                                     UnitPromotionType.battlecry, UnitPromotionType.tortoise])
		self.assertEqual(secondPromotions, [UnitPromotionType.embarkation, UnitPromotionType.healthBoostMelee,
		                                    UnitPromotionType.commando, UnitPromotionType.amphibious,
		                                    UnitPromotionType.zweihander])


class TestUnit(unittest.TestCase):
	def setUp(self) -> None:
		self.mapModel = MapModelMock(24, 20, TerrainType.grass)

		self.playerBarbarian = Player(leader=LeaderType.barbar, cityState=None, human=False)
		self.playerBarbarian.initialize()

		self.playerTrajan = Player(leader=LeaderType.trajan, cityState=None, human=False)
		self.playerTrajan.initialize()

		self.playerVictoria = Player(leader=LeaderType.victoria, cityState=None, human=True)
		self.playerVictoria.initialize()

		self.simulation = GameModel(
			victoryTypes=[VictoryType.domination],
			handicap=HandicapType.chieftain,
			turnsElapsed=0,
			players=[self.playerBarbarian, self.playerTrajan, self.playerVictoria],
			map=self.mapModel
		)

		# add UI
		self.simulation.userInterface = UserInterfaceMock()

	def test_move(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		warrior.doMoveOnto(HexPoint(6, 5), self.simulation)

		# THEN
		self.assertEqual(warrior.location, HexPoint(6, 5))

	def test_maxMoves(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		builder = Unit(HexPoint(5, 6), UnitType.builder, self.playerTrajan)
		missionary = Unit(HexPoint(5, 7), UnitType.missionary, self.playerTrajan)
		cavalry = Unit(HexPoint(5, 8), UnitType.horseman, self.playerTrajan)

		# WHEN
		maxMovesWarriorNormal = warrior.maxMoves(self.simulation)
		maxMovesBuilderNormal = builder.maxMoves(self.simulation)

		# golden age + monumentality
		self.playerTrajan._currentAgeValue = AgeType.golden
		self.playerTrajan._currentDedicationsValue = [DedicationType.monumentality]
		maxMovesBuilderGoldenAgeMonumentality = builder.maxMoves(self.simulation)

		# golden age + exodusOfTheEvangelists
		self.playerTrajan._currentAgeValue = AgeType.golden
		self.playerTrajan._currentDedicationsValue = [DedicationType.exodusOfTheEvangelists]
		maxMovesBuilderGoldenAgeExodusOfTheEvangelists = missionary.maxMoves(self.simulation)

		# reset
		self.playerTrajan._currentAgeValue = AgeType.normal
		self.playerTrajan._currentDedicationsValue = []

		# promotion commando
		self.assertTrue(warrior.doPromote(UnitPromotionType.battlecry, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.commando, self.simulation))
		maxMovesWarriorCommando = warrior.maxMoves(self.simulation)

		# promotion pursuit
		cavalry._promotions._promotions = []
		self.assertTrue(cavalry.doPromote(UnitPromotionType.caparison, self.simulation))
		self.assertTrue(cavalry.doPromote(UnitPromotionType.depredation, self.simulation))
		self.assertTrue(cavalry.doPromote(UnitPromotionType.pursuit, self.simulation))
		maxMovesCavalryPursuit = cavalry.maxMoves(self.simulation)

		# THEN
		self.assertEqual(maxMovesWarriorNormal, 2)
		self.assertEqual(maxMovesBuilderNormal, 2)
		self.assertEqual(maxMovesBuilderGoldenAgeMonumentality, 4)
		self.assertEqual(maxMovesBuilderGoldenAgeExodusOfTheEvangelists, 5)

		self.assertEqual(maxMovesWarriorCommando, 3)
		self.assertEqual(maxMovesCavalryPursuit, 5)

		# fixme more conditions

	def test_readyToMove(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		readyToMoveNormal = warrior.readyToMove()

		# garrison
		city = City("Berlin", HexPoint(5, 5), isCapital=True, player=self.playerTrajan)
		city.initialize(self.simulation)
		self.simulation.addCity(city)
		warrior.doGarrison(self.simulation)
		readyToMoveGarrisoned = warrior.readyToMove()

		# THEN
		self.assertTrue(readyToMoveNormal)
		self.assertFalse(readyToMoveGarrisoned)

	def test_isDead(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		isDeadNormal = warrior.isDead()

		warrior.changeDamage(101, None, self.simulation)
		isDeadDamaged = warrior.isDead()

		# THEN
		self.assertFalse(isDeadNormal)
		self.assertTrue(isDeadDamaged)

	def test_isPlayer(self):
		# GIVEN
		warriorAI = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		warriorHuman = Unit(HexPoint(5, 6), UnitType.warrior, self.playerVictoria)

		# WHEN
		# ...

		# THEN
		self.assertFalse(warriorAI.isHuman())
		self.assertTrue(warriorHuman.isHuman())
		self.assertFalse(warriorAI.isBarbarian())
		self.assertFalse(warriorHuman.isBarbarian())

	def test_sight(self):
		# GIVEN
		scout = Unit(HexPoint(5, 5), UnitType.scout, self.playerTrajan)
		galley = Unit(HexPoint(5, 6), UnitType.galley, self.playerTrajan)

		# WHEN
		sightScoutNormal = scout.sight()
		self.assertTrue(scout.doPromote(UnitPromotionType.ranger, self.simulation))
		self.assertTrue(scout.doPromote(UnitPromotionType.sentry, self.simulation))
		self.assertTrue(scout.doPromote(UnitPromotionType.spyglass, self.simulation))
		sightScoutSpyglass = scout.sight()

		sightGalleyNormal = galley.sight()
		self.assertTrue(galley.doPromote(UnitPromotionType.helmsman, self.simulation))
		self.assertTrue(galley.doPromote(UnitPromotionType.rutter, self.simulation))
		sightGalleySpyglass = galley.sight()

		# THEN
		self.assertEqual(sightScoutNormal, 2)
		self.assertEqual(sightScoutSpyglass, 3)
		self.assertEqual(sightGalleyNormal, 2)
		self.assertEqual(sightGalleySpyglass, 3)

	def test_eq(self):
		# GIVEN
		scout = Unit(HexPoint(5, 5), UnitType.scout, self.playerTrajan)
		galley = Unit(HexPoint(5, 6), UnitType.galley, self.playerTrajan)

		# WHEN

		# THEN
		self.assertEqual(scout, scout)
		self.assertNotEqual(scout, galley)
		self.assertNotEqual(scout, None)

	def test_numberOfAttacksPerTurn(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		knight = Unit(HexPoint(5, 6), UnitType.knight, self.playerTrajan)

		# WHEN
		numberOfAttacksPerTurnNormal = warrior.numberOfAttacksPerTurn(self.simulation)

		self.assertTrue(knight.doPromote(UnitPromotionType.charge, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.marauding, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.rout, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.armorPiercing, self.simulation))
		self.assertTrue(knight.doPromote(UnitPromotionType.breakthrough, self.simulation))
		numberOfAttacksPerTurnBreakthrough = knight.numberOfAttacksPerTurn(self.simulation)

		self.assertTrue(warrior.doPromote(UnitPromotionType.battlecry, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.tortoise, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.zweihander, self.simulation))
		self.assertTrue(warrior.doPromote(UnitPromotionType.eliteGuard, self.simulation))
		numberOfAttacksPerTurnEliteGuard = warrior.numberOfAttacksPerTurn(self.simulation)

		# THEN
		self.assertEqual(numberOfAttacksPerTurnNormal, 1)
		self.assertEqual(numberOfAttacksPerTurnBreakthrough, 2)
		self.assertEqual(numberOfAttacksPerTurnEliteGuard, 2)

	def test_isGreatPerson(self):
		# GIVEN
		scout = Unit(HexPoint(5, 5), UnitType.scout, self.playerTrajan)
		general = Unit(HexPoint(5, 6), UnitType.general, self.playerTrajan)
		general.greatPerson = GreatPersonType.boudica

		# WHEN

		# THEN
		self.assertFalse(scout.isGreatPerson())
		self.assertTrue(general.isGreatPerson())

	def test_doKill(self):
		# GIVEN
		barbarianWarrior = Unit(HexPoint(5, 5), UnitType.barbarianWarrior, self.playerBarbarian)

		# WHEN
		eurekaBefore = self.playerTrajan.techs.eurekaValue(TechType.bronzeWorking)
		barbarianWarrior.doKill(delayed=False, otherPlayer=self.playerTrajan, simulation=self.simulation)
		eurekaAfter = self.playerTrajan.techs.eurekaValue(TechType.bronzeWorking)

		# THEN
		self.assertEqual(eurekaBefore, 0)
		self.assertEqual(eurekaAfter, 1)

	def test_canEmbarkInto(self):
		# GIVEN
		self.mapModel.modifyTerrainAt(HexPoint(6, 5), TerrainType.ocean)
		self.playerTrajan.techs.discover(TechType.shipBuilding, self.simulation)

		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		warrior._isEmbarkedValue = True
		canEmbarkIntoEmbarked = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		warrior._isEmbarkedValue = False

		canEmbarkIntoOcean = warrior.canEmbarkInto(point=HexPoint(6, 5), simulation=self.simulation)

		warrior._movesValue = 0
		canEmbarkIntoNoMoves = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		warrior._movesValue = 2

		# THEN
		self.assertEqual(canEmbarkIntoEmbarked, False)
		self.assertEqual(canEmbarkIntoOcean, True)
		self.assertEqual(canEmbarkIntoNoMoves, False)

	def test_doEmbark(self):
		# GIVEN
		self.mapModel.modifyTerrainAt(HexPoint(6, 5), TerrainType.ocean)
		self.playerTrajan.techs.discover(TechType.shipBuilding, self.simulation)

		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		doEmbarkNormal = warrior.canEmbarkInto(point=HexPoint(6, 5), simulation=self.simulation)

		# THEN
		self.assertEqual(doEmbarkNormal, True)

	def test_canPillage(self):
		# GIVEN
		self.mapModel.tileAt(HexPoint(5, 5)).setImprovement(ImprovementType.farm)

		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		canPillageNormal = warrior.canPillageAt(HexPoint(5, 5), self.simulation)

		warrior._isEmbarkedValue = True
		canPillageEmbarked = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		warrior._isEmbarkedValue = False

		self.mapModel.tileAt(HexPoint(5, 5)).setImprovementPillaged(True)
		canPillagePillaged = warrior.canEmbarkInto(point=None, simulation=self.simulation)
		self.mapModel.tileAt(HexPoint(5, 5)).setImprovementPillaged(False)

		# THEN
		self.assertEqual(canPillageNormal, True)
		self.assertEqual(canPillageEmbarked, False)
		self.assertEqual(canPillagePillaged, False)

	def test_canHeal(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)
		barbarianWarrior = Unit(HexPoint(5, 5), UnitType.barbarianWarrior, self.playerBarbarian)

		# WHEN
		canHealNormal = warrior.canHeal(self.simulation)
		canHealBarbarian = barbarianWarrior.canHeal(self.simulation)

		# damage
		warrior.changeDamage(20, None, self.simulation)

		canHealDamaged = warrior.canHeal(self.simulation)

		warrior._isEmbarkedValue = True
		canHealEmbarked = warrior.canHeal(self.simulation)
		warrior._isEmbarkedValue = False

		# todo PolicyCardType.twilightValor

		# THEN
		self.assertEqual(canHealNormal, False)
		self.assertEqual(canHealBarbarian, False)
		self.assertEqual(canHealDamaged, True)
		self.assertEqual(canHealEmbarked, False)

	def test_gainedPromotions(self):
		# GIVEN
		warrior = Unit(HexPoint(5, 5), UnitType.warrior, self.playerTrajan)

		# WHEN
		gainedPromotionsNormal = copy.deepcopy(warrior.gainedPromotions())

		self.assertTrue(warrior._promotions.earnPromotion(UnitPromotionType.battlecry))
		gainedPromotionsBattlecry = warrior.gainedPromotions()

		# THEN
		self.assertListEqual(gainedPromotionsNormal, [])
		self.assertListEqual(gainedPromotionsBattlecry, [UnitPromotionType.battlecry])
