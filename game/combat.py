import inspect
import math

from core.base import ExtendedEnum


def isinstance_string(variable, string):
    return variable.__class__.__name__ == string


class CombatResultType(ExtendedEnum):
	totalDefeat = 'totalDefeat'
	majorDefeat = 'majorDefeat'
	minorDefeat = 'minorDefeat'
	stalemate = 'stalemate'
	minorVictory = 'minorVictory'
	majorVictory = 'majorVictory'
	totalVictory = 'totalVictory'


class CombatResult:
	def __init__(self, defenderDamage: int, attackerDamage: int, value: CombatResultType):
		self.defenderDamage = defenderDamage
		self.attackerDamage = attackerDamage
		self.value = value


class Combat:
	@classmethod
	def predictMeleeAttack(cls, attacker, defender, simulation) -> CombatResult:
		attackerTile = simulation.tileAt(attacker.location)
		defenderTile = simulation.tileAt(defender.location)

		if not isinstance_string(attacker, 'Unit'):
			raise Exception(f'attack of unsupported type: {attacker}')

		if isinstance_string(defender, 'Unit'):
			# attacker strikes
			attackerStrength = attacker.attackStrengthAgainst(defender, None, defenderTile, simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, None, defenderTile, ranged=False, simulation=simulation)
			attackerStrengthDifference = attackerStrength - defenderStrength

			defenderDamage: int = int(30.0 * pow(math.e, 0.04 * float(attackerStrengthDifference)))

			if defenderDamage < 0:
				defenderDamage = 0

			# defender strikes back
			attackerStrength2 = defender.attackStrengthAgainst(attacker, None, attackerTile, simulation)
			defenderStrength2 = attacker.defensiveStrengthAgainst(defender, None, attackerTile, ranged=True, simulation=simulation)

			defenderStrengthDifference = attackerStrength2 - defenderStrength2

			attackerDamage: int = int(30.0 * pow(math.e, 0.04 * float(defenderStrengthDifference)))

			if attackerDamage < 0:
				attackerDamage = 0

			# no damage for attacker, no suppression to cities
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=defenderDamage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=attackerDamage
			)
			return CombatResult(defenderDamage=defenderDamage, attackerDamage=attackerDamage, value=value)
		elif isinstance_string(defender, 'City'):
			# attacker strikes
			attackerStrength = attacker.attackStrengthAgainst(None, defender, defenderTile, simulation)
			defenderStrength = defender.defensiveStrengthAgainst(attacker, defenderTile, ranged=False, simulation=simulation)
			attackerStrengthDifference = attackerStrength - defenderStrength

			defenderDamage: int = int(30.0 * pow(math.e, 0.04 * float(attackerStrengthDifference)))

			if defenderDamage < 0:
				defenderDamage = 0

			# defender strikes back
			attackerStrength2 = defender.rangedCombatStrengthAgainst(attacker, attackerTile)
			defenderStrength2 = attacker.defensiveStrengthAgainst(None, defender, attackerTile, ranged=True, simulation=simulation)

			defenderStrengthDifference = attackerStrength2 - defenderStrength2

			attackerDamage: int = int(30.0 * pow(math.e, 0.04 * float(defenderStrengthDifference)))

			if attackerDamage < 0:
				attackerDamage = 0

			# no damage for attacker, no suppression to cities
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=defenderDamage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=attackerDamage
			)
			return CombatResult(defenderDamage=defenderDamage, attackerDamage=attackerDamage, value=value)
		else:
			raise Exception(f'attack against unsupported type: {defender}')

	@classmethod
	def predictRangedAttack(cls, attacker, defender, simulation) -> CombatResult:
		attackerTile = simulation.tileAt(attacker.location)
		defenderTile = simulation.tileAt(defender.location)

		if isinstance_string(attacker, 'City') and isinstance_string(defender, 'Unit'):
			attackerStrength = attacker.rangedCombatStrengthAgainst(defender, defenderTile)
			defenderStrength = defender.defensiveStrengthAgainst(None, None, defenderTile, ranged=True, simulation=simulation)
			strengthDifference = attackerStrength - defenderStrength

			damage: int = int(30.0 * pow(math.e, 0.04 * float(strengthDifference)))

			if damage < 0:
				damage = 0

			# no damage for attacker, no suppression to cities
			value = Combat.evaluateResult(
				defenderHealth=defender.healthPoints(),
				defenderDamage=damage,
				attackerHealth=attacker.healthPoints(),
				attackerDamage=0
			)
			return CombatResult(defenderDamage=damage, attackerDamage=0, value=value)
		else:
			raise Exception(f'unsupported combination of attacker / defender: {attacker} / {defender}')

	@classmethod
	def doAirAttack(cls, attacker, plot, simulation) -> CombatResult:
		pass

	@classmethod
	def doMeleeAttack(cls, self, defender, simulation):
		pass

	@classmethod
	def doRangedAttack(cls, self, defender, simulation):
		pass

	@classmethod
	def evaluateResult(cls,
	                   defenderHealth: int,
	                   defenderDamage: int,
	                   attackerHealth: int,
	                   attackerDamage: int) -> CombatResultType:

		if defenderDamage > defenderHealth and attackerHealth - attackerDamage > 10:
			return CombatResultType.totalVictory

		if attackerDamage > attackerHealth and defenderHealth - defenderDamage > 10:
			return CombatResultType.totalDefeat

		if defenderDamage > attackerDamage and defenderHealth - defenderDamage < attackerHealth - attackerDamage:
			return CombatResultType.majorVictory

		if defenderDamage < attackerDamage and defenderHealth - defenderDamage > attackerHealth - attackerDamage:
			return CombatResultType.majorDefeat

		if defenderDamage > attackerDamage:
			return CombatResultType.minorVictory

		if defenderDamage < attackerDamage:
			return CombatResultType.minorDefeat

		return CombatResultType.stalemate
