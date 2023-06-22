from typing import Optional

from core.base import ExtendedEnum, contains
from game.flavors import Flavor
from game.unitTypes import UnitClassType
from map.types import FeatureType


class PromotionCombatModifierDirection(ExtendedEnum):
	attack = 'attack'
	defend = 'defend'
	both = 'both'


class PromotionCombatModifierData:
	def __init__(self, amount: int, unitClasses: [UnitClassType], combatDirection: PromotionCombatModifierDirection,
				 damagedOnly: bool, fortifiedOnly: bool, roughOnly: bool):
		self.amount = amount
		self.unitClasses = unitClasses
		self.combatDirection = combatDirection
		self.damagedOnly = damagedOnly
		self.fortifiedOnly = fortifiedOnly
		self.roughOnly = roughOnly


class UnitPromotionType:
	pass


class UnitPromotionTypeData:
	"""
	https://civilization.fandom.com/wiki/Promotions_(Civ6)
	https://github.com/LoneGazebo/Community-Patch-DLL/blob/b33ee4a04e91d27356af0bcc421de1b7899ac073/(2)%20Vox%20Populi/Balance%20Changes/Units/PromotionChanges.xml

	"""
	def __init__(self, name: str, effect: str, tier: int, unitClass: UnitClassType, required: [UnitPromotionType],
				 consumable: bool, enemyRoute: bool, ignoreZoneOfControl: bool,
				 combatModifier: Optional[PromotionCombatModifierData], flavours: [Flavor]):
		self.name = name
		self.effect = effect
		self.tier = tier
		self.unitClass = unitClass
		self.required = required
		self.consumable = consumable
		self.enemyRoute = enemyRoute
		self.ignoreZoneOfControl = ignoreZoneOfControl
		self.combatModifier = combatModifier
		self.flavours = flavours


class CombatModifier:
	def __init__(self, amount: int, text: str):
		self.amount = amount
		self.text = text


class UnitPromotionType(ExtendedEnum):
	spyglass = 'spyglass'
	commando = 'commando'
	helmsman = 'helmsman'
	redeploy = 'redeploy'
	pursuit = 'pursuit'
	sentry = 'sentry'
	rutter = 'rutter'
	depredation = 'depredation'
	embarkation = 'embarkation'
	breakthrough = 'breakthrough'
	eliteGuard = 'eliteGuard'
	expertMarksman = 'expertMarksman'

	def name(self) -> str:
		return self._data().name

	def effect(self) -> str:
		return self._data().effect

	def tier(self) -> int:
		return self._data().tier

	def unitClass(self) -> UnitClassType:
		return self._data().unitClass

	def required(self) -> [UnitPromotionType]:
		return self._data().required

	def consumable(self) -> bool:
		return self._data().consumable

	def isEnemyRoute(self) -> bool:
		return self._data().enemyRoute

	def ignoreZoneOfControl(self) -> bool:
		return self._data().ignoreZoneOfControl

	def attackStrengthModifierAgainst(self, defender) -> Optional[CombatModifier]:
		combatModifier = self._data().combatModifier

		if combatModifier is None:
			return None

		if combatModifier.combatDirection == PromotionCombatModifierDirection.defend:
			return None

		if combatModifier.damagedOnly and defender.damage() == 0:
			return None

		if combatModifier.fortifiedOnly and not defender.isFortified():
			return None

		if contains(lambda unitClass: unitClass == defender.unitClassType(), combatModifier.unitClasses):
			return CombatModifier(combatModifier.amount, self.name())

		return None

	def defenderStrengthModifierAgainst(self, attacker) -> Optional[CombatModifier]:
		combatModifier = self._data().combatModifier

		if combatModifier is None:
			return None

		if combatModifier.combatDirection == PromotionCombatModifierDirection.attack:
			return None

		if combatModifier.damagedOnly and attacker.damage() == 0:
			return None

		if contains(lambda unitClass: unitClass == attacker.unitClassType(), combatModifier.unitClasses):
			return CombatModifier(combatModifier.amount, self.name())

		return None

	def  defenderStrengthModifierOn(self, tile) -> Optional[CombatModifier]:
		combatModifier = self._data().combatModifier

		if combatModifier is None:
			return None

		if combatModifier.combatDirection == PromotionCombatModifierDirection.attack:
			return None

		tileIsRough = tile.hasFeature(FeatureType.forest) or tile.hasFeature(FeatureType.rainforest) or \
			tile.isHills() or tile.hasFeature(FeatureType.marsh)

		if combatModifier.roughOnly and not tileIsRough:
			return None

		return CombatModifier(combatModifier.amount, self.name())

	def _data(self) -> UnitPromotionTypeData:
		sdfjdsgfh


class UnitPromotions:
	def __init__(self, unit):
		self.unit = unit
		self._promotions: [UnitPromotionType] = []

	def hasPromotion(self, promotion: UnitPromotionType) -> bool:
		return promotion in self._promotions

	def gainedPromotions(self) -> [UnitPromotionType]:
		return self._promotions

	def earnPromotion(self, promotion: UnitPromotionType):
		if self.hasPromotion(promotion):
			return

		self._promotions.append(promotion)

	def possiblePromotions(self) -> [UnitPromotionType]:
		promotionList: [UnitPromotionType] = []

		for promotion in list(UnitPromotionType):
			if not self.unit.isOfUnitClass(promotion.unitClass()):
				continue

			if self.hasPromotion(promotion):
				continue

			valid = True
			for requiredPromotion in promotion.required():
				if not self.hasPromotion(requiredPromotion):
					valid = False

			if not valid:
				continue

			promotionList.append(promotion)

		return promotionList
