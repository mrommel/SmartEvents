from typing import Optional

from game.flavors import Flavor, FlavorType
from game.types import CivicType, EraType
from utils.base import ExtendedEnum


class PolicyCardSlot(ExtendedEnum):
	wildcard = 'wildcard'
	economic = 'economic'
	military = 'military'


class PolicyCardType:
	pass


class PolicyCardTypeData:
	def __init__(self, name: str, bonus: str, slot: PolicyCardSlot, requiredCivic: Optional[CivicType] = None,
	             obsoleteCivic: Optional[CivicType] = None, startEra: Optional[EraType] = [],
	             endEra: Optional[EraType] = [], replace: [PolicyCardType] = [], flavours: [Flavor] = [],
	             requiresDarkAge: bool = False):
		self.name = name
		self.bonus = bonus
		self.slot = slot
		self.requiredCivic = requiredCivic
		self.obsoleteCivic = obsoleteCivic
		self.startEra = startEra
		self.endEra = endEra
		self.replace = replace,
		self.flavours = flavours
		self.requiresDarkAge = requiresDarkAge


class PolicyCardType(ExtendedEnum):
	none = 'none'

	# ancient
	urbanPlanning = 'urbanPlanning'

	# classical
	naturalPhilosophy = 'naturalPhilosophy'

	# medieval
	craftsmen = 'craftsmen'

	# modern
	fiveYearPlan = 'fiveYearPlan'

	# dark age
	collectivism = 'collectivism'

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def requiresDarkAge(self) -> bool:
		return self._data().requiresDarkAge

	def _data(self) -> PolicyCardTypeData:
		if self == PolicyCardType.none:
			return PolicyCardTypeData(
				name='KEY_NONE',
				bonus='',
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				requiresDarkAge=False
			)

		# ancient
		elif self == PolicyCardType.urbanPlanning:
			#
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_URBAN_PLANNING_TITLE",
				bonus="TXT_KEY_POLICY_CARD_URBAN_PLANNING_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.gamesAndRecreation,
				replace=[],
				flavours=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.production, value=3)
				]
			)

		# classical
		elif self == PolicyCardType.naturalPhilosophy:
			# https://civilization.fandom.com/wiki/Natural_Philosophy_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NATURAL_PHILOSOPHY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NATURAL_PHILOSOPHY_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.recordedHistory,
				obsoleteCivic=CivicType.classStruggle,
				replace=[],
				flavours=[]
			)

		# medieval
		elif self == PolicyCardType.craftsmen:
			# https://civilization.fandom.com/wiki/Craftsmen_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CRAFTSMEN_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CRAFTSMEN_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.guilds,
				obsoleteCivic=CivicType.classStruggle,
				replace=[],
				flavours=[]
			)

		# modern
		elif self == PolicyCardType.fiveYearPlan:
			# https://civilization.fandom.com/wiki/Five-Year_Plan_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_FIVE_YEAR_PLAN_TITLE",
				bonus="TXT_KEY_POLICY_CARD_FIVE_YEAR_PLAN_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.classStruggle,
				obsoleteCivic=None,
				replace=[PolicyCardType.craftsmen, PolicyCardType.naturalPhilosophy],
				flavours=[]
			)

		# dark age
		elif self == PolicyCardType.collectivism:
			# https://civilization.fandom.com/wiki/Collectivism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLLECTIVISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLLECTIVISM_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.modern,
				endEra=EraType.information,
				replace=[],
				flavours=[],
				requiresDarkAge=True
			)

		raise AttributeError(f'cant get data for policy card {self}')

