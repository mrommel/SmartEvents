from typing import Optional

from game.flavors import Flavor, FlavorType
from game.policyCards import PolicyCardType
from game.types import CivicType, EraType
from core.base import ExtendedEnum


class PolicyCardSlots:
	def __init__(self, military: int, economic: int, diplomatic: int, wildcard: int):
		self.military = military
		self.economic = economic
		self.diplomatic = diplomatic
		self.wildcard = wildcard


class GovernmentTypeData:
	def __init__(self, name: str, bonus1Summary: str, bonus2Summary: str, era: EraType,
	             requiredCivic: Optional[CivicType], policyCardSlots: PolicyCardSlots, flavors: [Flavor],
	             influencePointsPerTurn: int, envoyPerInfluencePoints: int, envoysFromInfluencePoints: int,
	             tourismFactor: int):
		self.name = name
		self.bonus1Summary = bonus1Summary
		self.bonus2Summary = bonus2Summary
		self.era = era
		self.requiredCivic = requiredCivic
		self.policyCardSlots = policyCardSlots
		self.flavors = flavors
		self.influencePointsPerTurn = influencePointsPerTurn
		self.envoyPerInfluencePoints = envoyPerInfluencePoints
		self.envoysFromInfluencePoints = envoysFromInfluencePoints
		self.tourismFactor = tourismFactor


class GovernmentType(ExtendedEnum):
	# ancient
	chiefdom = 'chiefdom'

	# classical
	autocracy = 'autocracy'
	classicalRepublic = 'classicalRepublic'
	oligarchy = 'oligarchy'

	# medieval
	merchantRepublic = 'merchantRepublic'
	monarchy = 'monarchy'

	# renaissance
	theocracy = 'theocracy'

	# modern
	fascism = 'fascism'
	communism = 'communism'
	democracy = 'democracy'

	def name(self) -> str:
		return self._data().name

	def requiredCivic(self) -> Optional[CivicType]:
		return self._data().requiredCivic

	def _data(self) -> GovernmentTypeData:
		# ancient
		if self == GovernmentType.chiefdom:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_CHIEFDOM_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_CHIEFDOM_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_CHIEFDOM_BONUS2",
				era=EraType.ancient,
				requiredCivic=CivicType.codeOfLaws,
				policyCardSlots=PolicyCardSlots(military=1, economic=1, diplomatic=0, wildcard=0),
				flavors=[],
				influencePointsPerTurn=1,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=0
			)

		# classical
		elif self == GovernmentType.autocracy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_AUTOCRACY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_AUTOCRACY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_AUTOCRACY_BONUS2",
				era=EraType.classical,
				requiredCivic=CivicType.politicalPhilosophy,
				policyCardSlots=PolicyCardSlots(military=2, economic=1, diplomatic=0, wildcard=0),
				flavors=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.production, value=3)
				],
				influencePointsPerTurn=3,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=-2
			)
		elif self == GovernmentType.classicalRepublic:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_CLASSICAL_REPUBLIC_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_CLASSICAL_REPUBLIC_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_CLASSICAL_REPUBLIC_BONUS2",  #
				era=EraType.classical,
				requiredCivic=CivicType.politicalPhilosophy,
				policyCardSlots=PolicyCardSlots(military=0, economic=2, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.amenities, value=4)],
				influencePointsPerTurn=3,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=-1
			)
		elif self == GovernmentType.oligarchy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_OLIGARCHY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_OLIGARCHY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_OLIGARCHY_BONUS2",
				era=EraType.classical,
				requiredCivic=CivicType.politicalPhilosophy,
				policyCardSlots=PolicyCardSlots(military=1, economic=1, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.offense, value=4)],
				influencePointsPerTurn=3,
				envoyPerInfluencePoints=100,
				envoysFromInfluencePoints=1,
				tourismFactor=-2
			)

		# medieval
		elif self == GovernmentType.merchantRepublic:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_MERCHANT_REPUBLIC_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_MERCHANT_REPUBLIC_BONUS1",  #
				bonus2Summary="TXT_KEY_GOVERNMENT_MERCHANT_REPUBLIC_BONUS2",
				era=EraType.medieval,
				requiredCivic=CivicType.exploration,
				policyCardSlots=PolicyCardSlots(military=1, economic=2, diplomatic=1, wildcard=2),
				flavors=[Flavor(FlavorType.gold, value=4)],
				influencePointsPerTurn=5,
				envoyPerInfluencePoints=150,
				envoysFromInfluencePoints=2,
				tourismFactor=-2
			)
		elif self == GovernmentType.monarchy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_MONARCHY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_MONARCHY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_MONARCHY_BONUS2",  #
				era=EraType.medieval,
				requiredCivic=CivicType.divineRight,
				policyCardSlots=PolicyCardSlots(military=3, economic=1, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.growth, value=3)],
				influencePointsPerTurn=5,
				envoyPerInfluencePoints=150,
				envoysFromInfluencePoints=2,
				tourismFactor=-3
			)

		# renaissance
		elif self == GovernmentType.theocracy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_THEOCRACY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_THEOCRACY_BONUS1",  #
				bonus2Summary="TXT_KEY_GOVERNMENT_THEOCRACY_BONUS2",  #
				era=EraType.renaissance,
				requiredCivic=CivicType.reformedChurch,
				policyCardSlots=PolicyCardSlots(military=2, economic=2, diplomatic=1, wildcard=1),
				flavors=[Flavor(FlavorType.religion, value=4)],
				influencePointsPerTurn=5,
				envoyPerInfluencePoints=150,
				envoysFromInfluencePoints=2,
				tourismFactor=-4
			)

		# modern
		elif self == GovernmentType.fascism:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_FASCISM_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_FASCISM_BONUS1",  # 2nd
				bonus2Summary="TXT_KEY_GOVERNMENT_FASCISM_BONUS2",
				era=EraType.modern,
				requiredCivic=CivicType.totalitarianism,
				policyCardSlots=PolicyCardSlots(military=4, economic=1, diplomatic=1, wildcard=2),
				flavors=[Flavor(FlavorType.offense, value=5)],
				influencePointsPerTurn=7,
				envoyPerInfluencePoints=200,
				envoysFromInfluencePoints=3,
				tourismFactor=-5
			)
		elif self == GovernmentType.communism:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_COMMUNISM_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_COMMUNISM_BONUS1",  #
				bonus2Summary="TXT_KEY_GOVERNMENT_COMMUNISM_BONUS2",
				era=EraType.modern,
				requiredCivic=CivicType.classStruggle,
				policyCardSlots=PolicyCardSlots(military=3, economic=3, diplomatic=1, wildcard=1),
				flavors=[
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.cityDefense, value=2)
				],
				influencePointsPerTurn=7,
				envoyPerInfluencePoints=200,
				envoysFromInfluencePoints=3,
				tourismFactor=-6
			)
		elif self == GovernmentType.democracy:
			#
			return GovernmentTypeData(
				name="TXT_KEY_GOVERNMENT_DEMOCRACY_TITLE",
				bonus1Summary="TXT_KEY_GOVERNMENT_DEMOCRACY_BONUS1",
				bonus2Summary="TXT_KEY_GOVERNMENT_DEMOCRACY_BONUS2",  #
				era=EraType.modern,
				requiredCivic=CivicType.suffrage,
				policyCardSlots=PolicyCardSlots(military=1, economic=3, diplomatic=2, wildcard=2),
				flavors=[
					Flavor(FlavorType.gold, value=2),
					Flavor(FlavorType.greatPeople, value=4)
				],
				influencePointsPerTurn=7,
				envoyPerInfluencePoints=200,
				envoysFromInfluencePoints=3,
				tourismFactor=-3
			)

		raise AttributeError(f'cant get data for government {self}')


class PolicyCardSet:
	def __init__(self):
		self._cards: [PolicyCardType] = []

	def hasCard(self, policyCard: PolicyCardType) -> bool:
		return policyCard in self._cards

	def addCard(self, policyCard: PolicyCardType):
		self._cards.append(policyCard)

	def cards(self) -> [PolicyCardType]:
		return self._cards

	def removeCard(self, policyCard: PolicyCardType):
		self._cards = list(filter(lambda card: card != policyCard, self._cards))


class PlayerGovernment:
	def __init__(self, player):
		self.player = player
		self._currentGovernmentValue = GovernmentType.chiefdom
		self._policyCards = PolicyCardSet()

	def setGovernment(self, governmentType: GovernmentType, simulation):
		self._currentGovernmentValue = governmentType

	def currentGovernment(self) -> GovernmentType:
		return self._currentGovernmentValue

	def hasCard(self, policyCard: PolicyCardType) -> bool:
		return self._policyCards.hasCard(policyCard)

	def addCard(self, policyCard: PolicyCardType):
		self._policyCards.addCard(policyCard)
