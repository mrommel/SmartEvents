from typing import Optional

from core.base import ExtendedEnum
from game.flavors import Flavor, FlavorType
from game.types import TechType


class PlayerStateAllWars(ExtendedEnum):
	neutral = 'neutral'
	winning = 'winning'
	losing = 'losing'


class WarGoalType(ExtendedEnum):
	none = 'none'

	prepare = 'prepare'



class MilitaryStrategyTypeData:
	def __init__(self, name: str, requiredTech: Optional[TechType], obsoleteTech: Optional[TechType],
	             notBeforeTurnElapsed: int, checkEachTurns: int, minimumAdoptionTurns: int, flavors: [Flavor]):
		self.name = name
		self.requiredTech = requiredTech
		self.obsoleteTech = obsoleteTech
		self.notBeforeTurnElapsed = notBeforeTurnElapsed
		self.checkEachTurns = checkEachTurns
		self.minimumAdoptionTurns = minimumAdoptionTurns
		self.flavors = flavors


class MilitaryStrategyType(ExtendedEnum):
	needRanged = 'needRanged'
	enoughRanged = 'enoughRanged'
	needMilitaryUnits = 'needMilitaryUnits'
	enoughMilitaryUnits = 'enoughMilitaryUnits'
	needNavalUnits = 'needNavalUnits'
	needNavalUnitsCritical = 'needNavalUnitsCritical'
	enoughNavalUnits = 'enoughNavalUnits'

	empireDefense = 'empireDefense'
	empireDefenseCritical = 'empireDefenseCritical'
	atWar = 'atWar'
	warMobilization = 'warMobilization'
	eradicateBarbarians = 'eradicateBarbarians'

	winningWars = 'winningWars'
	losingWars = 'losingWars'

	def name(self) -> str:
		return self._data().name

	def requiredTech(self) -> Optional[TechType]:
		return self._data().requiredTech

	def obsoleteTech(self) -> Optional[TechType]:
		return self._data().obsoleteTech

	def notBeforeTurnElapsed(self) -> int:
		return self._data().notBeforeTurnElapsed

	def flavorModifiers(self) -> [Flavor]:
		return self._data().flavors

	def _data(self) -> MilitaryStrategyTypeData:
		if self == MilitaryStrategyType.needRanged:
			#
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_NONE',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=-5),
					Flavor(FlavorType.defense, value=-5),
					Flavor(FlavorType.ranged, value=20)
				]
			)
		elif self == MilitaryStrategyType.enoughRanged:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ENOUGH_RANGED',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=5),
					Flavor(FlavorType.ranged, value=-20)
				]
			)
		elif self == MilitaryStrategyType.needMilitaryUnits:
			return MilitaryStrategyTypeData(
				name='',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.enoughMilitaryUnits:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ENOUGH_MILITARY_UNITS',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=-50),
					Flavor(FlavorType.defense, value=-50),
					Flavor(FlavorType.ranged, value=-50)
				]
			)
		elif self == MilitaryStrategyType.needNavalUnits:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_NEED_NAVAL_UNITS',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=50,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.needNavalUnitsCritical:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_NEED_NAVAL_UNITS_CRITICAL',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=50,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.enoughNavalUnits:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ENOUGH_NAVAL_UNITS',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=50,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.empireDefense:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_EMPIRE_DEFENSE',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.empireDefenseCritical:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_EMPIRE_DEFENSE_CRITICAL',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[]
			)
		elif self == MilitaryStrategyType.atWar:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_AT_WAR',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=1,
				minimumAdoptionTurns=5,
				flavors=[
					Flavor(FlavorType.offense, value=15),
					Flavor(FlavorType.defense, value=15),
					Flavor(FlavorType.ranged, value=15),
					Flavor(FlavorType.cityDefense, value=10),
					Flavor(FlavorType.wonder, value=-10)
				]
			)
		elif self == MilitaryStrategyType.warMobilization:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_WAR_MOBILIZATION',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=5,
				minimumAdoptionTurns=15,
				flavors=[
					Flavor(FlavorType.offense, value=10),
					Flavor(FlavorType.defense, value=10),
					Flavor(FlavorType.ranged, value=10),
					Flavor(FlavorType.militaryTraining, value=10)
				]
			)
		elif self == MilitaryStrategyType.eradicateBarbarians:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_ERADICATE_BARBARIANS',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=25,
				checkEachTurns=5,
				minimumAdoptionTurns=5,
				flavors=[
					Flavor(FlavorType.offense, value=5)
				]
			)
		elif self == MilitaryStrategyType.winningWars:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_WINNING_WARS',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=5),
					Flavor(FlavorType.defense, value=-5)
				]
			)
		elif self == MilitaryStrategyType.losingWars:
			return MilitaryStrategyTypeData(
				name='TXT_KEY_MILITARY_STRATEGY_LOSING_WARS',
				requiredTech=None,
				obsoleteTech=None,
				notBeforeTurnElapsed=-1,
				checkEachTurns=2,
				minimumAdoptionTurns=2,
				flavors=[
					Flavor(FlavorType.offense, value=-5),
					Flavor(FlavorType.defense, value=5),
					Flavor(FlavorType.cityDefense, value=25),
					Flavor(FlavorType.expansion, value=-15),
					Flavor(FlavorType.tileImprovement, value=-10),
					Flavor(FlavorType.recon, value=-15),
					Flavor(FlavorType.wonder, value=-15)
				]
			)

	def shouldBeActiveFor(self, player, simulation) -> bool:
		if self == MilitaryStrategyType.needRanged:
			return self._shouldBeActiveNeedRangedFor(player, simulation)
		elif self == MilitaryStrategyType.enoughRanged:
			return self._shouldBeActiveEnoughRangedFor(player, simulation)
		elif self == MilitaryStrategyType.needMilitaryUnits:
			return self._shouldBeActiveNeedMilitaryUnitsFor(player, simulation)
		elif self == MilitaryStrategyType.enoughMilitaryUnits:
			return self._shouldBeActiveEnoughMilitaryUnitsFor(player, simulation)
		elif self == MilitaryStrategyType.needNavalUnits:
			return False  # FIXME
		elif self == MilitaryStrategyType.needNavalUnitsCritical:
			return False  # FIXME
		elif self == MilitaryStrategyType.enoughNavalUnits:
			return False  # FIXME
		elif self == MilitaryStrategyType.empireDefense:
			return self._shouldBeActiveEmpireDefenseFor(player, simulation)
		elif self == MilitaryStrategyType.empireDefenseCritical:
			return self._shouldBeActiveEmpireDefenseCriticalFor(player, simulation)
		elif self == MilitaryStrategyType.atWar:
			return self._shouldBeActiveAtWarFor(player, simulation)
		elif self == MilitaryStrategyType.warMobilization:
			return self._shouldBeActiveWarMobilizationFor(player, simulation)
		elif self == MilitaryStrategyType.eradicateBarbarians:
			return self._shouldBeActiveEradicateBarbariansFor(player, simulation)
		elif self == MilitaryStrategyType.winningWars:
			return self._shouldBeActiveWinningWarsFor(player)
		elif self == MilitaryStrategyType.losingWars:
			return self._shouldBeActiveLosingWarsFor(player)

	def _shouldBeActiveNeedRangedFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEnoughRangedFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveNeedMilitaryUnitsFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEnoughMilitaryUnitsFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEmpireDefenseFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEmpireDefenseCriticalFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveAtWarFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveWarMobilizationFor(self, player, simulation) -> bool:
		# @fixme
		return False

	def _shouldBeActiveEradicateBarbariansFor(self, player, simulation) -> bool:
		# If we're at war don't bother with this Strategy
		if player.militaryAI.militaryStrategyAdoption.adopted(MilitaryStrategyType.atWar):
			return False

		# Also don't bother, if we're building up for a sneak attack
		for loopPlayer in simulation.players:
			if not player.isEqualTo(loopPlayer) and loopPlayer.isAlive() and player.hasMetWith(loopPlayer):
				if player.diplomacyAI.warGoalTowards(loopPlayer) == WarGoalType.prepare:
					return False

		# If we have an operation of this type running, we don't want to turn this strategy off
		# FIXME
		# if (pPlayer->haveAIOperationOfType(AI_OPERATION_DESTROY_BARBARIAN_CAMP)):
		# return true;

		# Two visible camps or 4 Barbarians will trigger this
		strategyWeight = player.militaryAI.barbarianData().barbarianCampCount * 50 + \
		                 player.militaryAI.barbarianData().visibleBarbarianCount * 25

		if strategyWeight >= 100:
			return True

		return False

	def _shouldBeActiveWinningWarsFor(self, player) -> bool:
		return player.diplomacyAI.stateOfAllWars == PlayerStateAllWars.winning

	def _shouldBeActiveLosingWarsFor(self, player) -> bool:
		# @fixme
		return False
