import random
from typing import Optional

from game.cities import AgeType, DedicationType
from game.civilizations import CivilizationType
from game.flavors import FlavorType
from game.moments import Moment, MomentType
from game.types import TechType, CivicType, EraType
from utils.base import WeightedBaseList


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
		# simulation.sendGossip(type:.technologyResearched(tech: tech), of: self.player)

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


class DiplomacyAI:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
		pass

	def hasMetWith(self, player) -> bool:
		return False

	def update(self, simulation):
		pass

	def doFirstContactWith(self, otherPlayer, simulation):
		pass


class HomelandAI:
	def __init__(self, player):
		self.player = player

	def doTurn(self, simulation):
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

	def addMomentOf(self, momentType: MomentType, turn: int, civilization: Optional[CivilizationType] = None):
		self._momentsArray.append(Moment(momentType, turn, civilization))

		self._currentEraScore += momentType.eraScore()

	def moments(self) -> [Moment]:
		return self._momentsArray

	def eraScore(self) -> int:
		return self._currentEraScore

	def resetEraScore(self):
		self._currentEraScore = 0
