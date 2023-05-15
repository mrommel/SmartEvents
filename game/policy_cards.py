from typing import Optional

from game.flavors import Flavor, FlavorType
from game.types import CivicType, EraType
from utils.base import ExtendedEnum


class PolicyCardSlot(ExtendedEnum):
	diplomatic = 'diplomatic'
	wildcard = 'wildcard'
	economic = 'economic'
	military = 'military'


class PolicyCardType:
	pass


class PolicyCardTypeData:
	def __init__(self, name: str, bonus: str, slot: PolicyCardSlot, requiredCivic: Optional[CivicType] = None,
	             obsoleteCivic: Optional[CivicType] = None, startEra: Optional[EraType] = [],
	             endEra: Optional[EraType] = [], replace: [PolicyCardType] = [], flavors: [Flavor] = [],
	             requiresDarkAge: bool = False):
		self.name = name
		self.bonus = bonus
		self.slot = slot
		self.requiredCivic = requiredCivic
		self.obsoleteCivic = obsoleteCivic
		self.startEra = startEra
		self.endEra = endEra
		self.replace = replace,
		self.flavors = flavors
		self.requiresDarkAge = requiresDarkAge


class PolicyCardType(ExtendedEnum):
	none = 'none'

	# ancient
	survey = 'survey'
	godKing = 'godKing'
	discipline = 'discipline'
	urbanPlanning = 'urbanPlanning'
	ilkum = 'ilkum'
	agoge = 'agoge'
	caravansaries = 'caravansaries'
	maritimeIndustries = 'maritimeIndustries'
	maneuver = 'maneuver'
	strategos = 'strategos'
	conscription = 'conscription'
	corvee = 'corvee'
	landSurveyors = 'landSurveyors'
	colonization = 'colonization'
	inspiration = 'inspiration'
	revelation = 'revelation'
	limitanei = 'limitanei'

	# classical
	insulae = 'insulae'
	#
	naturalPhilosophy = 'naturalPhilosophy'

	# medieval
	navalInfrastructure = 'navalInfrastructure'
	navigation = 'navigation'
	feudalContract = 'feudalContract'
	serfdom = 'serfdom'
	meritocracy = 'meritocracy'
	retainers = 'retainers'
	sack = 'sack'
	professionalArmy = 'professionalArmy'
	retinues = 'retinues'
	tradeConfederation = 'tradeConfederation'
	merchantConfederation = 'merchantConfederation'
	aesthetics = 'aesthetics'
	medinaQuarter = 'medinaQuarter'
	craftsmen = 'craftsmen'  # added
	townCharters = 'townCharters'
	travelingMerchants = 'travelingMerchants'
	chivalry = 'chivalry'
	gothicArchitecture = 'gothicArchitecture'
	civilPrestige = 'civilPrestige'

	# renaissance
	colonialOffices = 'colonialOffices'
	# invention
	# frescoes
	# machiavellianism
	# warsOfReligion
	# simultaneum
	# religiousOrders
	# logistics
	# triangularTrade
	# drillManuals
	# rationalism
	# freeMarket
	liberalism = 'liberalism'
	# wisselbanken
	# pressGangs

	# industrial
	# nativeConquest
	# grandeArmee
	# ...

	# modern
	# resourceManagement
	# propaganda
	# leveeEnMasse
	# laissezFaire
	# marketEconomy
	policeState = 'policeState'
	# nobelPrize
	# scienceFoundations
	# nuclearEspionage
	# economicUnion
	# theirFinestHour
	# arsenalOfDemocracy
	newDeal = 'newDeal'
	# lightningWarfare
	# thirdAlternative
	# martialLaw
	# gunboatDiplomacy
	fiveYearPlan = 'fiveYearPlan'
	# collectivization
	# patrioticWar
	# defenseOfTheMotherland

	# atomic
	# cryptography
	# internationalWaters
	# containment
	# heritageTourism
	# sportsMedia
	# militaryFirst
	# satelliteBroadcasts
	# musicCensorship
	# integratedSpaceCell
	# secondStrikeCapability

	# information
	# strategicAirForce
	# ecommerce
	# internationalSpaceAgency
	# onlineCommunities
	# collectiveActivism
	# afterActionReports
	# communicationsOffice
	# aerospaceContractors

	# future
	# spaceTourism
	# hallyu
	# nonStateActors
	# integratedAttackLogistics
	# rabblerousing
	# diplomaticCapital
	# globalCoalition

	# dark age
	automatedWorkforce = 'automatedWorkforce'
	collectivism = 'collectivism'
	# cyberWarfare
	# decentralization
	# despoticPaternalism
	# disinformationCampaign
	# eliteForces
	# flowerPower
	# inquisition
	# isolationism
	# lettersOfMarque
	# monasticism
	robberBarons = 'robberBarons'
	# rogueState
	# samoderzhaviye
	# softTargets
	# twilightValor

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
		elif self == PolicyCardType.survey:
			# https://civilization.fandom.com/wiki/Survey_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_SURVEY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_SURVEY_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.exploration,
				replace=[],
				flavors=[
					Flavor(FlavorType.recon, value=5)
				]
			)
		elif self == PolicyCardType.godKing:
			# https://civilization.fandom.com/wiki/God_King_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_GOD_KING_TITLE",
				bonus="TXT_KEY_POLICY_CARD_GOD_KING_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.theology,
				replace=[],
				flavors=[
					Flavor(FlavorType.religion, value=3),
					Flavor(FlavorType.gold, value=2)
				]
			)
		elif self == PolicyCardType.discipline:
			# https://civilization.fandom.com/wiki/Discipline_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_DISCIPLINE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_DISCIPLINE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.colonialism,
				replace=[],
				flavors=[
					Flavor(FlavorType.defense, value=4),
					Flavor(FlavorType.growth, value=1)
				]
			)
		elif self == PolicyCardType.urbanPlanning:
			#
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_URBAN_PLANNING_TITLE",
				bonus="TXT_KEY_POLICY_CARD_URBAN_PLANNING_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.codeOfLaws,
				obsoleteCivic=CivicType.gamesAndRecreation,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.production, value=3)
				]
			)
		elif self == PolicyCardType.ilkum:
			# https://civilization.fandom.com/wiki/Ilkum_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_ILKUM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_ILKUM_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.craftsmanship,
				obsoleteCivic=CivicType.gamesAndRecreation,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=2),
					Flavor(FlavorType.tileImprovement, value=3)
				]
			)
		elif self == PolicyCardType.agoge:
			# https://civilization.fandom.com/wiki/Agoge_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_AGOGE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_AGOGE_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.craftsmanship,
				obsoleteCivic=CivicType.feudalism,
				replace=[],
				flavors=[
					Flavor(FlavorType.offense, value=3),
					Flavor(FlavorType.defense, value=2)
				]
			)
		elif self == PolicyCardType.caravansaries:
			# https://civilization.fandom.com/wiki/Caravansaries_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CARAVANSARIES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CARAVANSARIES_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.foreignTrade,
				obsoleteCivic=CivicType.mercantilism,
				replace=[],
				flavors=[
					Flavor(FlavorType.gold, value=5)
				]
			)
		elif self == PolicyCardType.maritimeIndustries:
			# https://civilization.fandom.com/wiki/Maritime_Industries_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MARITIME_INDUSTRIES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MARITIME_INDUSTRIES_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.foreignTrade,
				obsoleteCivic=CivicType.colonialism,
				replace=[],
				flavors=[
					Flavor(FlavorType.navalGrowth, value=3),
					Flavor(FlavorType.naval, value=2)
				]
			)
		elif self == PolicyCardType.maneuver:
			# https://civilization.fandom.com/wiki/Maneuver_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MANEUVER_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MANEUVER_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.militaryTradition,
				obsoleteCivic=CivicType.divineRight,
				replace=[],
				flavors=[
					Flavor(FlavorType.mobile, value=4),
					Flavor(FlavorType.offense, value=1)
				]
			)
		elif self == PolicyCardType.strategos:
			# https://civilization.fandom.com/wiki/Strategos_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_STRATEGOS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_STRATEGOS_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.militaryTradition,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[
					Flavor(FlavorType.greatPeople, value=5)
				]
			)
		elif self == PolicyCardType.conscription:
			# https://civilization.fandom.com/wiki/Conscription_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CONSCRIPTION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CONSCRIPTION_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.stateWorkforce,
				obsoleteCivic=CivicType.mobilization,
				replace=[],
				flavors=[
					Flavor(FlavorType.offense, value=4),
					Flavor(FlavorType.gold, value=1)
				]
			)
		elif self == PolicyCardType.corvee:
			# https://civilization.fandom.com/wiki/Corv%C3%A9e_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CORVEE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CORVEE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.stateWorkforce,
				obsoleteCivic=CivicType.divineRight,
				replace=[],
				flavors=[
					Flavor(FlavorType.wonder, value=5)
				]
			)
		elif self == PolicyCardType.landSurveyors:
			# https://civilization.fandom.com/wiki/Land_Surveyors_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LAND_SURVEYORS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LAND_SURVEYORS_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.earlyEmpire,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=3),
					Flavor(FlavorType.tileImprovement, value=2)
				]
			)
		elif self == PolicyCardType.colonization:
			# https://civilization.fandom.com/wiki/Colonization_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLONIZATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLONIZATION_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.earlyEmpire,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=5)
				]
			)
		elif self == PolicyCardType.inspiration:
			# https://civilization.fandom.com/wiki/Inspiration_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INSPIRATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INSPIRATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.mysticism,
				obsoleteCivic=CivicType.nuclearProgram,
				replace=[],
				flavors=[
					Flavor(FlavorType.science, value=2),
					Flavor(FlavorType.greatPeople, value=3)
				]
			)
		elif self == PolicyCardType.revelation:
			# https://civilization.fandom.com/wiki/Revelation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_REVELATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_REVELATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.mysticism,
				obsoleteCivic=CivicType.humanism,
				replace=[],
				flavors=[
					Flavor(FlavorType.religion, value=2),
					Flavor(FlavorType.greatPeople, value=3)
				]
			)
		elif self == PolicyCardType.limitanei:
			# https://civilization.fandom.com/wiki/Limitanei_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LIMITANEI_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LIMITANEI_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.earlyEmpire,
				obsoleteCivic=None,
				replace=[],
				flavors=[Flavor(FlavorType.growth, value=5)]
			)

		# classical
		elif self == PolicyCardType.insulae:
			# https://civilization.fandom.com/wiki/Insulae_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_INSULAE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_INSULAE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.gamesAndRecreation,
				obsoleteCivic=CivicType.medievalFaires,
				replace=[],
				flavors=[
					Flavor(FlavorType.growth, value=3),
					Flavor(FlavorType.tileImprovement, value=2)
				]
			)
		elif self == PolicyCardType.naturalPhilosophy:
			# https://civilization.fandom.com/wiki/Natural_Philosophy_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NATURAL_PHILOSOPHY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NATURAL_PHILOSOPHY_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.recordedHistory,
				obsoleteCivic=CivicType.classStruggle,
				replace=[],
				flavors=[]
			)

		# medieval
		elif self == PolicyCardType.navalInfrastructure:
			# https://civilization.fandom.com/wiki/Naval_Infrastructure_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NAVAL_INFRASTRUCTURE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NAVAL_INFRASTRUCTURE_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.navalTradition,
				obsoleteCivic=CivicType.suffrage,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.navigation:
			# https://civilization.fandom.com/wiki/Navigation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NAVIGATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NAVIGATION_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.navalTradition,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.feudalContract:
			# https://civilization.fandom.com/wiki/Feudal_Contract_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_FEUDAL_CONTRACT_TITLE",
				bonus="TXT_KEY_POLICY_CARD_FEUDAL_CONTRACT_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.feudalism,
				obsoleteCivic=CivicType.nationalism,
				replace=[PolicyCardType.agoge],
				flavors=[]
			)
		elif self == PolicyCardType.serfdom:
			# https://civilization.fandom.com/wiki/Serfdom_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_SERFDOM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_SERFDOM_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.feudalism,
				obsoleteCivic=CivicType.civilEngineering,
				replace=[PolicyCardType.ilkum],
				flavors=[]
			)
		elif self == PolicyCardType.meritocracy:
			# https://civilization.fandom.com/wiki/Meritocracy_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MERITOCRACY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MERITOCRACY_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.civilService,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.retainers:
			# https://civilization.fandom.com/wiki/Retainers_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_RETAINERS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_RETAINERS_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.civilService,
				obsoleteCivic=CivicType.massMedia,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.sack:
			# https://civilization.fandom.com/wiki/Sack_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_SACK_TITLE",
				bonus="TXT_KEY_POLICY_CARD_SACK_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.scorchedEarth,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.professionalArmy:
			# https://civilization.fandom.com/wiki/Professional_Army_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_PROFESSIONAL_ARMY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_PROFESSIONAL_ARMY_BONUS",
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.urbanization,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.retinues:
			# https://civilization.fandom.com/wiki/Retinues_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_RETINUES_TITLE",
				bonus="TXT_KEY_POLICY_CARD_RETINUES_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.urbanization,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.tradeConfederation:
			# https://civilization.fandom.com/wiki/Trade_Confederation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TRADE_CONFEDERATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TRADE_CONFEDERATION_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.mercenaries,
				obsoleteCivic=CivicType.capitalism,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.merchantConfederation:
			# https://civilization.fandom.com/wiki/Merchant_Confederation_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MERCHANT_CONFEDERATION_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MERCHANT_CONFEDERATION_BONUS",  #
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.medievalFaires,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.aesthetics:
			# https://civilization.fandom.com/wiki/Aesthetics_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_AESTHETICS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_AESTHETICS_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.medievalFaires,
				obsoleteCivic=CivicType.professionalSports,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.medinaQuarter:
			# https://civilization.fandom.com/wiki/Medina_Quarter_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_MEDINA_QUARTER_TITLE",
				bonus="TXT_KEY_POLICY_CARD_MEDINA_QUARTER_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.medievalFaires,
				obsoleteCivic=CivicType.suffrage,
				replace=[PolicyCardType.insulae],
				flavors=[]
			)
		elif self == PolicyCardType.craftsmen:
			# https://civilization.fandom.com/wiki/Craftsmen_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CRAFTSMEN_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CRAFTSMEN_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.guilds,
				obsoleteCivic=CivicType.classStruggle,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.townCharters:
			# https://civilization.fandom.com/wiki/Town_Charters_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TOWN_CHARTERS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TOWN_CHARTERS_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.guilds,
				obsoleteCivic=CivicType.suffrage,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.travelingMerchants:
			# https://civilization.fandom.com/wiki/Traveling_Merchants_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_TRAVELING_MERCHANTS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_TRAVELING_MERCHANTS_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=CivicType.guilds,
				obsoleteCivic=CivicType.capitalism,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.chivalry:
			# https://civilization.fandom.com/wiki/Chivalry_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CHIVALRY_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CHIVALRY_BONUS",  #
				slot=PolicyCardSlot.military,
				requiredCivic=CivicType.divineRight,
				obsoleteCivic=CivicType.totalitarianism,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.gothicArchitecture:
			# https://civilization.fandom.com/wiki/Gothic_Architecture_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_GOTHIC_ARCHITECTURE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_GOTHIC_ARCHITECTURE_BONUS",  #
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.divineRight,
				obsoleteCivic=CivicType.civilEngineering,
				replace=[],
				flavors=[]
			)
		elif self == PolicyCardType.civilPrestige:
			# https://civilization.fandom.com/wiki/Civil_Prestige_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_CIVIL_PRESTIGE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_CIVIL_PRESTIGE_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.civilService,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)

		# renaissance
		elif self == PolicyCardType.colonialOffices:
			# https://civilization.fandom.com/wiki/Colonial_Offices_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_COLONIAL_OFFICE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_COLONIAL_OFFICE_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.exploration,
				obsoleteCivic=None,
				replace=[PolicyCardType.urbanPlanning],
				flavors=[]
			)
		# invention
		# frescoes
		# machiavellianism
		# warsOfReligion
		# simultaneum
		# religiousOrders
		# logistics
		# triangularTrade
		# drillManuals
		# rationalism
		# freeMarket
		elif self == PolicyCardType.liberalism:
			# https://civilization.fandom.com/wiki/Liberalism_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_LIBERALISM_TITLE",
				bonus="TXT_KEY_POLICY_CARD_LIBERALISM_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.enlightenment,
				obsoleteCivic=None,
				replace=[PolicyCardType.newDeal],
				flavors=[]
			)
		# wisselbanken
		# pressGangs

		# modern
		# resourceManagement
		# propaganda
		# leveeEnMasse
		# laissezFaire
		# marketEconomy
		elif self == PolicyCardType.policeState:
			# https://civilization.fandom.com/wiki/Police_State_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_POLICY_STATE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_POLICY_STATE_BONUS",
				slot=PolicyCardSlot.diplomatic,
				requiredCivic=CivicType.ideology,
				obsoleteCivic=None,
				replace=[],
				flavors=[]
			)
		# nobelPrize
		# scienceFoundations
		# nuclearEspionage
		# economicUnion
		# theirFinestHour
		# arsenalOfDemocracy
		elif self == PolicyCardType.newDeal:
			# https://civilization.fandom.com/wiki/New_Deal_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_NEW_DEAL_TITLE",
				bonus="TXT_KEY_POLICY_CARD_NEW_DEAL_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.suffrage,
				obsoleteCivic=None,
				replace=[
					PolicyCardType.medinaQuarter,
					PolicyCardType.liberalism
				],
				flavors=[]
			)
		# lightningWarfare
		# thirdAlternative
		# martialLaw
		# gunboatDiplomacy
		elif self == PolicyCardType.fiveYearPlan:
			# https://civilization.fandom.com/wiki/Five-Year_Plan_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_FIVE_YEAR_PLAN_TITLE",
				bonus="TXT_KEY_POLICY_CARD_FIVE_YEAR_PLAN_BONUS",
				slot=PolicyCardSlot.economic,
				requiredCivic=CivicType.classStruggle,
				obsoleteCivic=None,
				replace=[PolicyCardType.craftsmen, PolicyCardType.naturalPhilosophy],
				flavors=[]
			)
		# collectivization
		# patrioticWar
		# defenseOfTheMotherland

		# dark age
		elif self == PolicyCardType.automatedWorkforce:
			# https://civilization.fandom.com/wiki/Automated_Workforce_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_AUTOMATED_WORKFORCE_TITLE",
				bonus="TXT_KEY_POLICY_CARD_AUTOMATED_WORKFORCE_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.information,
				endEra=EraType.future,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
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
				flavors=[],
				requiresDarkAge=True
			)
		# cyberWarfare
		# decentralization
		# despoticPaternalism
		# disinformationCampaign
		# eliteForces
		# flowerPower
		# inquisition
		# isolationism
		# lettersOfMarque
		# monasticism
		elif self == PolicyCardType.robberBarons:
			# https://civilization.fandom.com/wiki/Robber_Barons_(Civ6)
			return PolicyCardTypeData(
				name="TXT_KEY_POLICY_CARD_ROBBER_BARONS_TITLE",
				bonus="TXT_KEY_POLICY_CARD_ROBBER_BARONS_BONUS",
				slot=PolicyCardSlot.wildcard,
				requiredCivic=None,
				obsoleteCivic=None,
				startEra=EraType.industrial,
				endEra=EraType.information,
				replace=[],
				flavors=[],
				requiresDarkAge=True
			)
		# rogueState
		# samoderzhaviye
		# softTargets
		# twilightValor

		raise AttributeError(f'cant get data for policy card {self}')

