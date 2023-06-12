from core.base import ExtendedEnum


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
		pass

	@classmethod
	def doAirAttack(cls, attacker, plot, simulation) -> CombatResult:
		pass

	@classmethod
	def doMeleeAttack(cls, self, defenderUnit, simulation):
		pass
