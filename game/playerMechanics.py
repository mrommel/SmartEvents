import random
from functools import reduce
from typing import Optional

from game.ai.baseTypes import PlayerStateAllWars, WarGoalType
from game.ai.militaries import MilitaryThreatType
from game.civilizations import CivilizationType, LeaderType
from game.flavors import FlavorType
from game.moments import Moment, MomentType
from game.notifications import NotificationType
from game.states.accessLevels import AccessLevel
from game.states.ages import AgeType
from game.states.dedications import DedicationType
from game.states.diplomaticMessages import DiplomaticRequestState, DiplomaticRequestMessage, LeaderEmotionType
from game.states.gossips import GossipType
from game.types import TechType, CivicType, EraType
from utils.base import WeightedBaseList, ExtendedEnum, InvalidEnumError


class WeightedTechList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for tech in list(TechType):
			self.setWeight(0.0, tech)


class TechEurekas:
	def __init__(self):
		self._eurekaTrigger = WeightedTechList()

	def triggerFor(self, tech: TechType):
		self._eurekaTrigger.setWeight(1.0, tech)

	def triggeredFor(self, tech: TechType) -> bool:
		return self._eurekaTrigger.weight(tech) > 0.0

	def triggerIncreaseFor(self, tech: TechType):
		self._eurekaTrigger.addWeight(1.0, tech)

	def triggerCountFor(self, tech: TechType) -> int:
		return int(self._eurekaTrigger.weight(tech))


class PlayerTechs:
	def __init__(self, player):
		self.player = player
		self._techs: [TechType] = []
		self._currentTechValue: Optional[TechType] = None
		self._lastScienceEarnedValue: float = 1.0
		self._progresses = WeightedTechList()
		self._eurekas = TechEurekas()

	def eurekaTriggeredFor(self, tech: TechType) -> bool:
		return self._eurekas.triggeredFor(tech)

	def triggerEurekaFor(self, tech: TechType, simulation):
		# check if eureka is still needed
		if self.hasTech(tech):
			return

		# check if eureka is already active
		if self.eurekaTriggeredFor(tech):
			return

		self._eurekas.triggerFor(tech)

		# update progress
		eurekaBoost = 0.5

		# freeInquiry + golden - Eureka provide an additional 10% of Technology costs.
		if self.player.currentAge() == AgeType.golden and self.player.hasDedication(DedicationType.freeInquiry):
			eurekaBoost += 0.1

		self._progresses.addWeight(float(tech.cost()) * eurekaBoost, tech)

		# freeInquiry + normal - Gain +1 Era Score when you trigger a [Eureka] Eureka
		# if player.currentAge() == AgeType.normal and player.hasDedication(DedicationType.freeInquiry):
		#    player.addMoment(of: .dedicationTriggered(dedicationType: .freeInquiry), in: gameModel)

		# check quests
		# for quest in player.ownQuests(in: gameModel):
		#
		#     if case .triggerEureka(tech: let questTechType) = quest.type {
		#
		#         if techType == questTechType {
		#             let cityStatePlayer = gameModel?.cityStatePlayer(for: quest.cityState)
		#             cityStatePlayer?.fulfillQuest(by: player.leader, in: gameModel)

		# trigger event to user
		# if player.isHuman():
		#    simulation.userInterface.showPopup(popupType: .eurekaTriggered(tech: tech))
		return

	def needToChooseTech(self) -> bool:
		return self._currentTechValue is None

	def discover(self, tech: TechType, simulation):
		# check if this tech is the first of a new era
		# techsInEra = sum(1 for t in self._techs if t.era() == tech.era())
		# if techsInEra == 0 and tech.era() != EraType.ancient:
		# 	if simulation.anyHasMoment(of: .worldsFirstTechnologyOfNewEra(eraType: tech.era())) {
		# 		self.player?.addMoment(of:.firstTechnologyOfNewEra(eraType: tech.era()), in: gameModel)
		# 	else:
		# 		self.player?.addMoment(of:.worldsFirstTechnologyOfNewEra(eraType: tech.era()), in: gameModel)

		self.updateEurekas(simulation)

		# check quests
		# for quest in self.player.ownQuests(simulation):
		# 	if case.trainUnit(type: let unitType) = quest.type
		# 		obsolete = false
		#
		# 	for upgradeUnitType in unitType.upgradesTo() {
		# 		if let requiredTech = upgradeUnitType.requiredTech() {
		# 			if requiredTech == tech {
		# 				obsolete = true
		#
		#
		# 		if let obsoleteTech = unitType.obsoleteTech() {
		# 		if obsoleteTech == tech {
		# 		obsolete = true
		# 		}
		# 		}
		#
		# if obsolete {
		# if let cityStatePlayer = gameModel.cityStatePlayer( for: quest.cityState) {
		# 	                                                                          cityStatePlayer.obsoleteQuest(
		# 		                                                                          by: player.leader, in: gameModel)
		# }
		# }
		# }
		#
		# if case.triggerEureka(tech: let
		# questTechType) = quest.type
		# {
		# if questTechType == tech
		# {
		# if let
		# cityStatePlayer = gameModel.cityStatePlayer(
		# for: quest.cityState) {
		# 	    cityStatePlayer.obsoleteQuest(by: player.leader, in: gameModel)

		# send gossip
		simulation.sendGossip(GossipType.technologyResearched, tech=tech, player=self.player)

		# check for printing
		# Researching the Printing technology. This will increase your visibility with all civilizations by one level.
		# if tech == TechType.printing:
		# 	for loopPlayer in gameModel.players:
		#
		# 		guard !loopPlayer.isBarbarian() & & !loopPlayer.isFreeCity() & & !loopPlayer.isCityState() else {
		# 			continue
		# 		}
		#
		# 		guard !loopPlayer.isEqual(to: player) else {
		# 			continue
		#
		# 		if player.hasMet(with: loopPlayer) {
		# 			player.diplomacyAI?.increaseAccessLevel(towards: loopPlayer)

		self._techs.append(tech)

	def hasTech(self, tech: TechType) -> bool:
		return tech in self._techs

	def updateEurekas(self, simulation):
		# Games and Recreation - Research the Construction technology.
		if self.hasTech(TechType.construction):
			if not self.player.civics.inspirationTriggeredFor(CivicType.gamesAndRecreation):
				self.player.civics.triggerInspirationFor(CivicType.gamesAndRecreation, simulation)

		# Mass Media - Research Radio.
		if self.hasTech(TechType.radio):
			if not self.player.civics.inspirationTriggeredFor(CivicType.massMedia):
				self.player.civics.triggerInspirationFor(CivicType.massMedia, simulation)

	def possibleTechs(self) -> [TechType]:
		returnTechs: [TechType] = []

		for tech in list(TechType):
			if tech == TechType.none:
				continue

			if self.hasTech(tech):
				continue

			allRequiredPresent = True

			for req in tech.required():

				if not self.hasTech(req):
					allRequiredPresent = False

			if allRequiredPresent:
				returnTechs.append(tech)

		return returnTechs

	def setCurrentTech(self, tech: TechType, simulation):
		if tech not in self.possibleTechs():
			raise Exception(f'cannot choose current tech: {tech}')

		self._currentTechValue = tech

		if self.player.isHuman():
			simulation.userInterface.selectTech(tech=tech)

	def currentTech(self) -> Optional[TechType]:
		return self._currentTechValue

	def currentScienceProgress(self) -> float:
		if self._currentTechValue is None:
			return 0.0

		return self._progresses.weight(self._currentTechValue)

	def turnsRemainingFor(self, tech: TechType) -> int:

		if self._lastScienceEarnedValue > 0.0:
			cost: float = float(tech.cost())
			remaining = cost - self._progresses.weight(tech)

			return int(remaining / self._lastScienceEarnedValue + 0.5)

		return 1

	def currentScienceTurnsRemaining(self) -> int:
		if self._currentTechValue is None:
			return 1

		return self.turnsRemainingFor(self._currentTechValue)

	def lastScienceEarned(self) -> float:
		return self._lastScienceEarnedValue

	def flavorWeightedOf(self, tech: TechType, flavor: FlavorType) -> float:
		if self.player is None:
			return 0.0

		return float(tech.flavorValue(flavor) * self.player.leader.flavor(flavor))

	def chooseNextTech(self) -> Optional[TechType]:
		weightedTechs: WeightedTechList = WeightedTechList()
		weightedTechs.removeAll()

		possibleTechsList = self.possibleTechs()

		for possibleTech in possibleTechsList:
			weightByFlavor = 0.0

			# weight of current tech
			for flavor in list(FlavorType):
				weightByFlavor += self.flavorWeightedOf(possibleTech, flavor)

			# add techs that can be research with this tech, but only with a little less weight
			for activatedTech in possibleTech.leadsTo():

				for flavor in list(FlavorType):
					weightByFlavor += self.flavorWeightedOf(activatedTech, flavor) * 0.75

				for secondActivatedTech in activatedTech.leadsTo():

					for flavor in list(FlavorType):
						weightByFlavor += self.flavorWeightedOf(secondActivatedTech, flavor) * 0.5

					for thirdActivatedTech in secondActivatedTech.leadsTo():

						for flavor in list(FlavorType):
							weightByFlavor += self.flavorWeightedOf(thirdActivatedTech, flavor) * 0.25

			# revalue based on cost / number of turns
			numberOfTurnsLeft = self.turnsRemainingFor(possibleTech)
			additionalTurnCostFactor = 0.015 * float(numberOfTurnsLeft)
			totalCostFactor = 0.15 + additionalTurnCostFactor
			weightDivisor = pow(float(numberOfTurnsLeft), totalCostFactor)

			# modify weight
			weightByFlavor = float(weightByFlavor) / weightDivisor

			weightedTechs.addWeight(weightByFlavor, possibleTech)

		# select one
		selectedIndex = random.randrange(100)

		weightedTechs = weightedTechs.top3()
		weightedTechsArray = weightedTechs.distributeByWeight()
		selectedTech = weightedTechsArray[selectedIndex]

		return selectedTech


class WeightedCivicList(WeightedBaseList):
	def __init__(self):
		super().__init__()
		for civic in list(CivicType):
			self.setWeight(0.0, civic)


class CivicInspirations:
	def __init__(self):
		self._inspirationTrigger = WeightedCivicList()
		self._inspirationCount = WeightedCivicList()

	def triggerFor(self, civic: CivicType):
		self._inspirationTrigger.setWeight(1.0, civic)
		self._inspirationCount.setWeight(0.0, civic)

	def triggeredFor(self, civic: CivicType) -> bool:
		return self._inspirationTrigger.weight(civic) > 0.0

	def triggerIncreaseFor(self, civic: CivicType, change: int = 1):
		self._inspirationCount.addWeight(float(change), civic)

	def triggerCountFor(self, civic: CivicType) -> int:
		return int(self._inspirationCount.weight(civic))


class PlayerCivics:
	def __init__(self, player):
		self.player = player

		self._civics: [CivicType] = []
		self._currentCivicValue: Optional[CivicType] = None
		self._lastCultureEarnedValue: float = 1.0
		self._progresses = WeightedCivicList()
		self._inspirations = CivicInspirations()

	def hasCivic(self, civic: CivicType) -> bool:
		return civic in self._civics

	def discover(self, civic: CivicType, simulation):
		if civic in self._civics:
			raise Exception(f'Civic {civic} already discovered')

		if civic.hasGovernorTitle():
			self.player.addGovernorTitle()

		if civic.envoys() > 0:
			self.player.changeUnassignedEnvoysBy(civic.envoys())

			# notify player about envoy to spend
			if self.player.isHuman():
				# player.notifications()?.add(notification:.envoyEarned)
				pass

		# check if this civic is the first of a new era
		civicsInEra = sum(1 for c in self._civics if c.era() == civic.era())
		if civicsInEra == 0 and civic.era() != EraType.ancient:
			# if simulation.anyHasMoment(of: .worldsFirstCivicOfNewEra(eraType: civic.era())):
			# 	self.player?.addMoment(of:.firstCivicOfNewEra(eraType: civic.era()), in: gameModel)
			# else:
			# 	self.player?.addMoment(of:.worldsFirstCivicOfNewEra(eraType: civic.era()), in: gameModel)
			pass

		self.updateInspirations(simulation)

		# check quests
		# for quest in self.player.ownQuests(simulation):
		# 	if case.triggerInspiration(civic: let questCivicType) = quest.type:
		# 		if questCivicType == civic:
		# 			cityStatePlayer = gameModel?.cityStatePlayer(for: quest.cityState)
		# 			cityStatePlayer.obsoleteQuest(by: player.leader, in: gameModel)

		# send gossip
		# simulation.sendGossip(type:.civicCompleted(civic: civic), of: self.player)

		self._civics.append(civic)

		self.player.doUpdateTradeRouteCapacity(simulation)

		#
		if civic == CivicType.naturalHistory or civic == CivicType.culturalHeritage:
			simulation.checkArchaeologySites()

		return

	def needToChooseCivic(self):
		pass

	def currentCultureProgress(self) -> float:
		if self._currentCivicValue is None:
			return 0.0

		return self._progresses.weight(self._currentCivicValue)

	def updateInspirations(self, simulation):
		# NOOP
		pass

	def possibleCivics(self):
		returnCivics: [CivicType] = []

		for civic in list(CivicType):
			if civic == CivicType.none:
				continue

			if self.hasCivic(civic):
				continue

			allRequiredPresent = True

			for req in civic.required():
				if not self.hasCivic(req):
					allRequiredPresent = False

			if allRequiredPresent:
				returnCivics.append(civic)

		return returnCivics

	def setCurrentCivic(self, civic: CivicType, simulation):
		if civic not in self.possibleCivics():
			raise Exception(f'cant select current civic: {civic} - its not in {self.possibleCivics()}')

		self._currentCivicValue = civic

		if self.player.isHuman():
			simulation.userInterface.selectCivic(civic)

		return

	def currentCivic(self) -> Optional[CivicType]:
		return self._currentCivicValue

	def inspirationTriggeredFor(self, civic: CivicType):
		return self._inspirations.triggeredFor(civic)

	def triggerInspirationFor(self, civic: CivicType, simulation):
		# check if eureka is still needed
		if self.hasCivic(civic):
			return

		# check if already active
		if self._inspirations.triggeredFor(civic):
			return

		self._inspirations.triggerFor(civic)

		# update progress
		inspirationBoost = 0.5

		# penBrushAndVoice + golden - Inspiration provide an additional 10% of Civic costs.
		if self.player.currentAge() == AgeType.golden and self.player.hasDedication(DedicationType.penBrushAndVoice):
			inspirationBoost += 0.1

		self._progresses.addWeight(float(civic.cost()) * inspirationBoost, civic)

		# penBrushAndVoice + normal - Gain + 1 Era Score when you trigger an Inspiration
		if self.player.currentAge() == AgeType.normal and self.player.hasDedication(DedicationType.penBrushAndVoice):
			# self.player.addMoment(of:.dedicationTriggered(dedicationType:.penBrushAndVoice), in: gameModel)
			pass

		# check quests
		# for quest in player.ownQuests( in: gameModel):
		# 	if case.triggerInspiration(civic: let questCivicType) = quest.type
		# 		if civic == questCivicType
		# 			cityStatePlayer = simulation.cityStatePlayer(for: quest.cityState)
		# 			cityStatePlayer.fulfillQuest(by: player.leader, in: gameModel)

		# trigger event to user
		if self.player.isHuman():
			# simulation.userInterface?.showPopup(popupType:.inspirationTriggered(civic: civicType))
			pass

		return

	def changeInspirationValueFor(self, civic: CivicType, change: int):
		self._inspirations.triggerIncreaseFor(civic, change)

	def inspirationValueOf(self, civic: CivicType) -> int:
		return self._inspirations.triggerCountFor(civic)


class BuilderTaskingAI:
	def __init__(self, player):
		self.player = player

	def update(self, simulation):
		pass


class TacticalAI:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass


class ApproachType:
	pass

class ApproachType(ExtendedEnum):
	none = 'none'

	allied = 'allied'
	declaredFriend = 'declaredFriend'
	friendly = 'friendly'
	neutral = 'neutral'
	unfriendly = 'unfriendly'
	denounced = 'denounced'
	war = 'war'

	@classmethod
	def fromValue(cls, value) -> ApproachType:
		if value > 91:
			return ApproachType.allied
		elif value > 74:
			return ApproachType.declaredFriend
		elif value > 58:
			return ApproachType.friendly
		elif value > 41:
			return ApproachType.neutral
		elif value > 24:
			return ApproachType.unfriendly
		elif value > 8:
			return ApproachType.denounced
		else:
			return ApproachType.war


class PlayerOpinionType(ExtendedEnum):
	none = 'none'


class StrengthType(ExtendedEnum):
	immense = 'immense'
	powerful = 'powerful'
	strong = 'strong'
	average = 'average'
	poor = 'poor'
	weak = 'weak'
	pathetic = 'pathetic'


class DiplomaticPact:
	def __init__(self, duration: int = 25):
		self.duration = duration


class PlayerProximityType(ExtendedEnum):
	neighbors = 'neighbors'
	none = 'none'


class PlayerWarFaceType(ExtendedEnum):
	none = 'none'


class PlayerWarStateType(ExtendedEnum):
	none = 'none'


class PlayerTargetValueType(ExtendedEnum):
	none = 'none'


class WarDamageLevelType(ExtendedEnum):
	none = 'none'


class WarProjectionType(ExtendedEnum):
	unknown = 'unknown'


class LandDisputeLevelType(ExtendedEnum):
	none = 'none'


class AggressivePostureType(ExtendedEnum):
	none = 'none'


class PeaceTreatyType(ExtendedEnum):
	none = 'none'


class LeaderAgendaType(ExtendedEnum):
	pass


class ApproachModifierTypeData:
	def __init__(self, summary: str, initialValue: int, reductionTurns: int, reductionValue: int,
				 hiddenAgenda: Optional[LeaderAgendaType]):
		self.summary = summary
		self.initialValue = initialValue
		self.reductionTurns = reductionTurns
		self.reductionValue = reductionValue
		self.hiddenAgenda = hiddenAgenda


class ApproachModifierType(ExtendedEnum):
	delegation = 'delegation'  # STANDARD_DIPLOMATIC_DELEGATION
	embassy = 'embassy'  # STANDARD_DIPLOMACY_RESIDENT_EMBASSY
	declaredFriend = 'declaredFriend'  # STANDARD_DIPLOMATIC_DECLARED_FRIEND
	denounced = 'denounced'  # STANDARD_DIPLOMATIC_DENOUNCED
	firstImpression = 'firstImpression'  # STANDARD_DIPLOMACY_RANDOM ??
	establishedTradeRoute = 'establishedTradeRoute'  # STANDARD_DIPLOMACY_TRADE_RELATIONS
	nearBorder = 'nearBorder'  # STANDARD_DIPLOMATIC_NEAR_BORDER_WARNING

	def initialValue(self) -> int:
		return self._data().initialValue

	def reductionTurns(self) -> int:
		return self._data().reductionTurns

	def reductionValue(self) -> int:
		return self._data().reductionValue

	def _data(self) -> ApproachModifierTypeData:
		if self == ApproachModifierType.delegation:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_DELEGATION",
				initialValue=3,
				reductionTurns=-1,
				reductionValue=0,
				hiddenAgenda=None
			)
		elif self == ApproachModifierType.embassy:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_RESIDENT_EMBASSY",
				initialValue=5,
				reductionTurns=-1,
				reductionValue=0,
				hiddenAgenda=None
			)
		elif self == ApproachModifierType.declaredFriend:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_DECLARED_FRIEND",
				initialValue=-9,
				reductionTurns=10,
				reductionValue=-1,
				hiddenAgenda=None
			)
		elif self == ApproachModifierType.denounced:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_DENOUNCED",
				initialValue=-9,
				reductionTurns=10,
				reductionValue=-1,
				hiddenAgenda=None
			)
		elif self == ApproachModifierType.firstImpression:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_FIRST_IMPRESSION",
				initialValue=0,  # overriden
				reductionTurns=10,
				reductionValue=-1,  # overriden
				hiddenAgenda=None
			)
		elif self == ApproachModifierType.establishedTradeRoute:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_ESTABLISHED_TRADE_ROUTE",
				initialValue=2,
				reductionTurns=1,
				reductionValue=-1,
				hiddenAgenda=None
			)
		elif self == ApproachModifierType.nearBorder:
			return ApproachModifierTypeData(
				summary="TXT_KEY_DIPLOMACY_MODIFIER_NEAR_BORDER_WARNING",
				initialValue=-2,
				reductionTurns=20,
				reductionValue=-1,
				hiddenAgenda=None
			)

		raise InvalidEnumError(self)


class DiplomaticAIPlayerApproachItem:
	def __init__(self, approachModifierType: ApproachModifierType, initialValue: Optional[int] = None,
				 reductionValue: Optional[int] = None):
		self.approachModifierType = approachModifierType

		if initialValue is not None:
			self.value = initialValue
		else:
			self.value = approachModifierType.initialValue()

		self.remainingTurn = approachModifierType.reductionTurns()

		if reductionValue is not None:
			self.reductionValue = reductionValue
		else:
			self.reductionValue = approachModifierType.reductionValue()

		self.expiredValue = False


class DiplomaticAIPlayerItem:
	def __init__(self, leader: LeaderType, turnOfFirstContact: int):
		self.leader = leader
		self.turnOfFirstContact = turnOfFirstContact
		self.accessLevel = AccessLevel.none
		self.gossipItems = []
		self.opinion = PlayerOpinionType.none
		self.militaryStrengthComparedToUs = StrengthType.average
		self.militaryThreat = MilitaryThreatType.none
		self.economicStrengthComparedToUs = StrengthType.average
		self.approachItems = []

		self.approach = 50  # default
		self.warFace = PlayerWarFaceType.none
		self.warState = PlayerWarStateType.none
		self.warGoal = WarGoalType.none
		self.targetValue = PlayerTargetValueType.none
		self.warDamageLevel = WarDamageLevelType.none
		self.warProjection = WarProjectionType.unknown
		self.lastWarProjection = WarProjectionType.unknown
		self.warValueLost = 0
		self.warWeariness = 0

		self.hasDelegationValue = False
		self.hasEmbassyValue = False

		self.landDisputeLevel = LandDisputeLevelType.none
		self.lastTurnLandDisputeLevel = LandDisputeLevelType.none

		self.militaryAggressivePosture = AggressivePostureType.none
		self.lastTurnMilitaryAggressivePosture = AggressivePostureType.none
		self.expansionAggressivePosture = AggressivePostureType.none
		self.plotBuyingAggressivePosture = AggressivePostureType.none

		# pacts
		self.declarationOfWar = DiplomaticPact()
		self.declarationOfFriendship = DiplomaticPact()
		self.openBorderAgreement = DiplomaticPact(duration=15)  # has a runtime of 15 turns
		self.defensivePact = DiplomaticPact(duration=15)  # has a runtime of 15 turns
		self.peaceTreaty = DiplomaticPact(duration=15)  # has a runtime of 15 turns
		self.alliance = DiplomaticPact()

		# deals
		self.deals = []

		self.hasDenounced = False
		self.isRecklessExpander = False

		self.proximity = PlayerProximityType.none

		# counter
		self.turnsAtWar = 0
		self.recentTradeValue = 0

		self.turnOfLastMeeting = -1
		self.numTurnsLockedIntoWar = 0
		self.wantPeaceCounter = 0
		self.musteringForAttack = False

		# agreements
		self.coopAgreements = None # DiplomaticPlayerArray < CoopWarState > ()
		self.workingAgainstAgreements = None # DiplomaticPlayerArray < Bool > ()

		# peace treaty willingness
		self.peaceTreatyWillingToOffer = PeaceTreatyType.none
		self.peaceTreatyWillingToAccept = PeaceTreatyType.none


class DiplomaticPlayerDict:
	def __init__(self):
		self.items: [DiplomaticAIPlayerItem] = []

	def initContactWith(self, otherPlayer, turn: int):
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			item.turnOfFirstContact = turn
		else:
			self.items.append(DiplomaticAIPlayerItem(otherLeader, turnOfFirstContact=turn))

	def hasMetWith(self, otherPlayer) -> bool:
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			return item.turnOfFirstContact != -1
		else:
			return False

	def updateMilitaryStrengthComparedToUsOf(self, otherPlayer, strength: StrengthType):
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			item.militaryStrengthComparedToUs = strength
		else:
			raise Exception("not gonna happen")

	def approachTowards(self, otherPlayer) -> ApproachType:
		value = self.approachValueTowards(otherPlayer)
		return ApproachType.fromValue(value)

	def approachValueTowards(self, otherPlayer) -> int:
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			return item.approach

		return 50  # default

	def addApproachOf(self, approachModifierType: ApproachModifierType, initialValue: int, reductionValue: int, otherPlayer):
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			approachItem = DiplomaticAIPlayerApproachItem(approachModifierType, initialValue, reductionValue)
			item.approachItems.append(approachItem)
		else:
			raise Exception("not gonna happen")

	def militaryThreatOf(self, otherPlayer) -> MilitaryThreatType:
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			return item.militaryThreat
		else:
			raise Exception("not gonna happen")

	def updateMilitaryThreatOf(self, otherPlayer, strength: StrengthType):
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			item.militaryStrength = strength
		else:
			raise Exception("not gonna happen")

	def accessLevelTowards(self, otherPlayer) -> AccessLevel:
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			return item.accessLevel

		return AccessLevel.none

	def hasSentDelegationTo(self, otherPlayer) -> bool:
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			return item.hasDelegationValue

		return False

	def sendDelegationTo(self, otherPlayer, send):
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			item.hasDelegationValue = send
		else:
			raise Exception("not gonna happen")

	def addApproach(self, approachModifier: ApproachModifierType, initialValue: Optional[int] = None,
	                reductionValue: Optional[int] = None, otherPlayer = None):
		if otherPlayer is None:
			raise Exception('otherPlayer must be filled')

		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			approachItem = DiplomaticAIPlayerApproachItem(
				approachModifierType=approachModifier,
				initialValue=initialValue,
				reductionValue=reductionValue
			)
			item.approachItems.append(approachItem)
		else:
			raise Exception("not gonna happen")

	def updateAccessLevelTo(self, accessLevel: AccessLevel, otherPlayer):
		otherLeader = otherPlayer.leader
		item = next((item for item in self.items if item.leader == otherLeader), None)

		if item is not None:
			item.accessLevel = accessLevel
		else:
			raise Exception("not gonna happen")


class DiplomacyAI:
	def __init__(self, player):
		self.playerDict = DiplomaticPlayerDict()
		self.stateOfAllWars = PlayerStateAllWars.neutral
		self.player = player
		self.greetPlayers = []

	def doTurn(self, simulation):
		# Military Stuff
		self.doLockedIntoWarDecay(simulation)
		self.doWarDamageDecay(simulation)
		self.doUpdateWarDamageLevel(simulation)
		self.updateMilitaryStrengths(simulation)
		self.updateEconomicStrengths(simulation)

		# DoUpdateWarmongerThreats();
		self.updateMilitaryThreats(simulation)
		self.updateTargetValue(simulation)  # DoUpdatePlayerTargetValues
		self.updateWarStates(simulation)
		self.doUpdateWarProjections(simulation)
		self.doUpdateWarGoals(simulation)

		self.doUpdatePeaceTreatyWillingness(simulation)

		# Issues of Dispute
		self.doUpdateLandDisputeLevels(simulation)
		# DoUpdateVictoryDisputeLevels();
		# DoUpdateWonderDisputeLevels();
		# DoUpdateMinorCivDisputeLevels();

		# Has any player gone back on any promises he made?
		# DoTestPromises();

		# What we think other Players are up to
		# self.doUpdateOtherPlayerWarDamageLevel(simulation)
		# DoUpdateEstimateOtherPlayerLandDisputeLevels();
		# DoUpdateEstimateOtherPlayerVictoryDisputeLevels();
		# DoUpdateEstimateOtherPlayerMilitaryThreats();
		# DoEstimateOtherPlayerOpinions();
		# LogOtherPlayerGuessStatus();

		# Look at the situation
		self.doUpdateMilitaryAggressivePostures(simulation)
		self.doUpdateExpansionAggressivePostures(simulation)
		self.doUpdatePlotBuyingAggressivePosture(simulation)

		# Player Opinion & Approach
		# DoUpdateApproachTowardsUsGuesses();

		self.doHiddenAgenda(simulation)
		self.updateOpinions(simulation)
		self.updateApproaches(simulation)
		# DoUpdateMinorCivApproaches();

		self.updateProximities(simulation)

		# These functions actually DO things, and we don't want the shadow AI behind a human player doing things for him
		if not self.player.isHuman():
			# MakeWar();
			# DoMakePeaceWithMinors();

			# DoUpdateDemands();

			# DoUpdatePlanningExchanges();
			# DoContactMinorCivs();
			self.doContactMajorCivs(simulation)

		# Update Counters
		self.doCounters(simulation)

	def hasMetWith(self, otherPlayer) -> bool:
		return self.playerDict.hasMetWith(otherPlayer)

	def update(self, simulation):
		activePlayer = simulation.activePlayer()
		if activePlayer is not None:
			# check if activePlayer is in greetPlayers
			if reduce(lambda b0, b1: b0 or b1, map(lambda player: activePlayer.isEqualTo(player), self.greetPlayers), False):
				if self.player.isCityState() or activePlayer.isCityState():
					if activePlayer.isHuman() and self.player.isCityState():
						cityState = self.player.cityState
						# is `activePlayer the first major player to meet this city state
						if simulation.countMajorCivilizationsMetWith(cityState) == 1:
							# first player gets a free envoy
							activePlayer.changeUnassignedEnvoysBy(1)

							# this free envoy is assigned to
							activePlayer.assignEnvoyTo(cityState, simulation)

							# inform human player
							activePlayer.notifications().addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=True
							)
						else:
							activePlayer.notifications().addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=False
							)

						# reveal city state to player
						cityStateCapital = simulation.capitalOf(self.player)
						if cityStateCapital is not None:
							simulation.discoverAt(cityStateCapital.location, sight=3, player=activePlayer)

					elif activePlayer.isCityState() and self.player.isHuman():
						cityState = activePlayer.cityState

						# is ´player´ the first major player to meet this city state
						if simulation.countMajorCivilizationsMetWith(cityState) == 1:
							# first player gets a free envoy
							self.player.changeUnassignedEnvoysBy(1)

							# this free envoy is assigned to
							self.player.assignEnvoyTo(cityState, simulation)

							# inform human player
							self.player.notifications().addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=True
							)
						else:
							self.player.notifications().addNotification(
								NotificationType.metCityState,
								cityState=cityState,
								first=False
							)

						# reveal city state to player
						cityStateCapital = simulation.capitalOf(activePlayer)
						if cityStateCapital is not None:
							simulation.discoverAt(cityStateCapital.location, sight=3, player=self.player)

					else:
						self.player.diplomacyRequests.sendRequest(
							activePlayer.leader,
							state=DiplomaticRequestState.intro,
							message=DiplomaticRequestMessage.messageIntro,
							emotion=LeaderEmotionType.neutral,
							simulation=simulation
						)

					self.greetPlayers =	[item for item in self.greetPlayers if not activePlayer.isEqualTo(item)]

		return

	def doFirstContactWith(self, otherPlayer, simulation):
		if self.hasMetWith(otherPlayer):
			return

		if self.player.isBarbarian() or otherPlayer.isBarbarian():
			return

		self.playerDict.initContactWith(otherPlayer, simulation.currentTurn)
		self.updateMilitaryStrengthOf(otherPlayer, simulation)

		impression = simulation.handicap.firstImpressionBaseValue() + random.randrange(-3, 3)
		self.playerDict.addApproachOf(ApproachModifierType.firstImpression, impression, 1 if impression > 0 else -1, otherPlayer)

		# Humans don't say hi to ai player automatically
		if not self.player.isHuman():
			# Should fire off a diplo message, when we meet a human
			if otherPlayer.isHuman():
				# Put in the list of people to greet human, when the human turn comes up.
				self.greetPlayers.append(otherPlayer)

		return

	def doLockedIntoWarDecay(self, simulation):
		for loopPlayer in simulation.players:
			if loopPlayer.isAlive() and not loopPlayer.isEqualTo(self.player) and loopPlayer.hasMetWith(self.player):
				# decay
				if self.numTurnsLockedIntoWarWith(loopPlayer) > 0:
					self.changeNumTurnsLockedIntoWarWith(loopPlayer, -1)

	def doWarDamageDecay(self, simulation):
		"""Every turn we're at peace war damage goes down a bit"""
		# Loop through all (known) Players
		for loopPlayer in simulation.players:
			if loopPlayer.isAlive() and not loopPlayer.isEqualTo(self.player) and loopPlayer.hasMetWith(self.player):
				# Update war damage we've suffered
				if not self.isAtWarWith(loopPlayer):
					value = self.warValueLostWith(loopPlayer)

					if value > 0:
						# Go down by 1/20th every turn at peace
						value /= 20

						# Make sure it's changing by at least 1
						value = max(1, value)

						self.changeWarValueLostWith(loopPlayer, -value)

				# Update war damage other players have suffered from our viewpoint
				# /*for(iThirdPlayerLoop = 0; iThirdPlayerLoop < MAX_CIV_PLAYERS; iThirdPlayerLoop++)
				# {
				#     eLoopThirdPlayer = (PlayerTypes) iThirdPlayerLoop;
				#     eLoopThirdTeam = GET_PLAYER(eLoopThirdPlayer).getTeam();
				#
				#     // These two players not at war?
				#     if(!GET_TEAM(eLoopThirdTeam).isAtWar(eLoopTeam))
				#     {
				#         iValue = GetOtherPlayerWarValueLost(eLoopPlayer, eLoopThirdPlayer);
				#
				#         if(iValue > 0)
				#         {
				#             // Go down by 1/20th every turn at peace
				#             iValue /= 20;
				#
				#             // Make sure it's changing by at least 1
				#             iValue = max(1, iValue);
				#
				#             ChangeOtherPlayerWarValueLost(eLoopPlayer, eLoopThirdPlayer, -iValue);
				#         }
				#     }
				# }*/
		return

	def updateMilitaryStrengths(self,simulation):
		for otherPlayer in simulation.players:
			if otherPlayer.leader != self.player.leader and self.player.hasMetWith(otherPlayer):
				self.updateMilitaryStrengthOf(otherPlayer, simulation)

	def updateMilitaryStrengthOf(self, otherPlayer, simulation):
		ownMilitaryStrength = self.player.militaryMight(simulation) + 30
		otherMilitaryStrength = otherPlayer.militaryMight(simulation) + 30
		militaryRatio = otherMilitaryStrength * 100 / ownMilitaryStrength

		if militaryRatio >= 250:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.immense)
		elif militaryRatio >= 165:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.powerful)
		elif militaryRatio >= 115:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.strong)
		elif militaryRatio >= 85:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.average)
		elif militaryRatio >= 60:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.poor)
		elif militaryRatio >= 40:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.weak)
		else:
			self.playerDict.updateMilitaryStrengthComparedToUsOf(otherPlayer, StrengthType.pathetic)

	def militaryThreatOf(self, otherPlayer) -> MilitaryThreatType:
		return self.playerDict.militaryThreatOf(otherPlayer)

	def updateMilitaryThreats(self, simulation):
		ownMilitaryMight = self.player.militaryMight(simulation)

		if ownMilitaryMight == 0:
			ownMilitaryMight = 1

		# Add in City Defensive Strength per city
		for city in simulation.citiesOf(self.player):
			damageFactor = (25.0 - float(city.damage())) / 25.0

			cityStrengthModifier = int(float(city.power(simulation)) * damageFactor)
			cityStrengthModifier *= 33
			cityStrengthModifier /= 100
			cityStrengthModifier /= 10

			ownMilitaryMight += cityStrengthModifier

		# Loop through all(known) Players
		for otherPlayer in simulation.players:
			if otherPlayer.leader != self.player.leader and self.player.hasMetWith(otherPlayer):
				otherMilitaryMight = otherPlayer.militaryMight(simulation)

				# If another player has double the Military strength of us, the Ratio will be 200
				militaryRatio = otherMilitaryMight * 100 / ownMilitaryMight
				militaryThreat = militaryRatio

				# At war: what is the current status of things?
				if self.isAtWarWith(otherPlayer):
					warStateValue = self.warStateTowards(otherPlayer)

					if warStateValue == PlayerWarStateType.none:
						# NOOP
						pass
					elif warStateValue == PlayerWarStateType.nearlyDefeated:
						militaryThreat += 150  # MILITARY_THREAT_WAR_STATE_NEARLY_DEFEATED
					elif warStateValue == PlayerWarStateType.defensive:
						militaryThreat += 80  # MILITARY_THREAT_WAR_STATE_DEFENSIVE
					elif warStateValue == PlayerWarStateType.stalemate:
						militaryThreat += 30  # MILITARY_THREAT_WAR_STATE_STALEMATE
					elif warStateValue == PlayerWarStateType.calm:
						militaryThreat += 0  # MILITARY_THREAT_WAR_STATE_CALM
					elif warStateValue == PlayerWarStateType.offensive:
						militaryThreat += -40  # MILITARY_THREAT_WAR_STATE_OFFENSIVE
					elif warStateValue == PlayerWarStateType.nearlyWon:
						militaryThreat += -100  # MILITARY_THREAT_WAR_STATE_NEARLY_WON

				# Factor in Friends this player has

				# TBD

				# Factor in distance
				proximityValue = self.proximityTo(otherPlayer)

				if proximityValue == PlayerProximityType.none:
					# NOOP
					pass
				elif proximityValue == PlayerProximityType.neighbors:
					militaryThreat += 100  # MILITARY_THREAT_NEIGHBORS
				elif proximityValue == PlayerProximityType.close:
					militaryThreat += 40  # MILITARY_THREAT_CLOSE
				elif proximityValue == PlayerProximityType.far:
					militaryThreat += -40  # MILITARY_THREAT_FAR
				elif proximityValue == PlayerProximityType.distant:
					militaryThreat += -100  # MILITARY_THREAT_DISTANT

				# Don't factor in # of players attacked or at war with now if we ARE at war with this guy already

				# FIXME

				# Now do the final assessment
				if militaryThreat >= 300:
					# MILITARY_THREAT_CRITICAL_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.critical)
				elif militaryThreat >= 220:  # MILITARY_THREAT_SEVERE_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.severe)
				elif militaryThreat >= 170:  # MILITARY_THREAT_MAJOR_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.major)
				elif militaryThreat >= 100:  # MILITARY_THREAT_MINOR_THRESHOLD
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.minor)
				else:
					self.playerDict.updateMilitaryThreatOf(otherPlayer, MilitaryThreatType.none)

		return

	def accessLevelTowards(self, otherPlayer) -> AccessLevel:
		return self.playerDict.accessLevelTowards(otherPlayer)

	def doSendDelegationTo(self, otherPlayer, simulation):
		if self.canSendDelegationTo(otherPlayer, simulation):
			self.playerDict.sendDelegationTo(otherPlayer, send=True)
			self.playerDict.addApproach(ApproachModifierType.delegation, otherPlayer=otherPlayer)

			# sight capital - our guys are there
			capital = simulation.capitalOf(otherPlayer)
			simulation.sightAt(capital.location, sight=3, player=self.player)

			# update access level
			self.increaseAccessLevelTowards(otherPlayer)
		
		return

	def canSendDelegationTo(self, otherPlayer, simulation) -> bool:
		# you can only send a delegation, if the `otherPlayer` has a capital
		if simulation.capitalOf(otherPlayer) is None:
			return False

		if self.player.treasury.value() < 25:
			return False

		if self.hasSentDelegationTo(otherPlayer):
			return False

		if self.player.civics.hasCivic(CivicType.diplomaticService):
			return False

		approach = self.approachTowards(otherPlayer)
		if approach == ApproachType.neutral or approach == ApproachType.friendly or \
			approach == ApproachType.declaredFriend or approach == ApproachType.allied:
			return True

		return False

	def hasSentDelegationTo(self, otherPlayer):
		return self.playerDict.hasSentDelegationTo(otherPlayer)

	def approachTowards(self, otherPlayer) -> ApproachType:
		return self.playerDict.approachTowards(otherPlayer)

	def increaseAccessLevelTowards(self, otherPlayer):
		currentAccessLevel = self.accessLevelTowards(otherPlayer)
		increasedAccessLevel = currentAccessLevel.increased()
		self.playerDict.updateAccessLevelTo(increasedAccessLevel, otherPlayer)

	def doUpdateWarDamageLevel(self, simulation):
		pass

	def updateEconomicStrengths(self, simulation):
		pass

	def updateTargetValue(self, simulation):
		pass

	def updateWarStates(self, simulation):
		pass

	def doUpdateWarProjections(self, simulation):
		pass

	def doUpdateWarGoals(self, simulation):
		pass

	def doUpdatePeaceTreatyWillingness(self, simulation):
		pass

	def doUpdateLandDisputeLevels(self, simulation):
		pass

	def doUpdateMilitaryAggressivePostures(self, simulation):
		pass

	def doUpdateExpansionAggressivePostures(self, simulation):
		pass

	def doUpdatePlotBuyingAggressivePosture(self, simulation):
		pass

	def doHiddenAgenda(self, simulation):
		pass

	def updateOpinions(self, simulation):
		pass

	def updateApproaches(self, simulation):
		pass

	def updateProximities(self, simulation):
		pass

	def doContactMajorCivs(self, simulation):
		pass

	def doCounters(self, simulation):
		pass


class DiplomacyRequests:
	def __init__(self, player):
		self.player = player

	def endTurn(self):
		pass


class PlayerMoments:
	def __init__(self, player):
		self.player = player
		self._momentsArray: [Moment] = []
		self._currentEraScore: int = 0

	def add(self, moment: Moment):
		self._momentsArray.append(moment)
		self._currentEraScore += moment.type.eraScore()

	def addMomentOf(self, momentType: MomentType, turn: int, civilization: Optional[CivilizationType] = None,
	                cityName: Optional[str] = None, continentName: Optional[str] = None):
		self._momentsArray.append(Moment(momentType, turn, civilization=civilization, cityName=cityName,
		                                 continentName=continentName))

		self._currentEraScore += momentType.eraScore()

	def moments(self) -> [Moment]:
		return self._momentsArray

	def eraScore(self) -> int:
		return self._currentEraScore

	def resetEraScore(self):
		self._currentEraScore = 0
