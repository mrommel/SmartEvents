from typing import Optional

from game.civilizations import CivilizationType
from game.flavors import Flavor
from game.types import TechType, CivicType
from map.types import Yields
from utils.base import ExtendedEnum, InvalidEnumError


class ImprovementTypeData:
	def __init__(self, name: str, effects: [str], requiredTech: Optional[TechType],
				 civilization: Optional[CivilizationType], flavors: [Flavor]):
		self.name = name
		self.effects = effects
		self.requiredTech = requiredTech
		self.civilization = civilization
		self.flavors = flavors


class ImprovementType(ExtendedEnum):
	none = 'none'

	barbarianCamp = 'barbarianCamp'

	mine = 'mine'
	plantation = 'plantation'
	farm = 'farm'
	quarry = 'quarry'
	camp = 'camp'
	fishingBoats = 'fishingBoats'
	pasture = 'pasture'
	oilWell = 'oilWell'
	fort = 'fort'
	goodyHut = 'goodyHut'

	def name(self):
		return self._data().name

	def _data(self) -> ImprovementTypeData:
		if self == ImprovementType.none:
			return ImprovementTypeData(
				name="",
				effects=[],
				requiredTech=None,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.barbarianCamp:
			#
			return ImprovementTypeData(
				name="Barbarian camp",
				effects=[],
				requiredTech=None,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.mine:
			# https://civilization.fandom.com/wiki/Mine_(Civ6)
			return ImprovementTypeData(
				name="Mine",
				effects=[
					"-1 Appeal",
					"+1 [Production] Production",
					"+1 [Production] Production (Apprenticeship)",
					"+1 [Production] Production (Industrialization)",
					"+1 [Production] Production (Smart Materials)"
				],
				requiredTech=TechType.mining,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			return ImprovementTypeData(
				name="Plantation",
				effects=[
					"+2 [Gold] Gold",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Scientific Theory)",
					"+2 [Gold] Gold (Globalization)"
				],
				requiredTech=TechType.irrigation,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.farm:
			# https://civilization.fandom.com/wiki/Farm_(Civ6)
			return ImprovementTypeData(
				name="Farm",
				effects=[
					"+1 [Food] Food",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food with two adjacent Farms (Feudalism)",
					"+1 [Food] Food for each adjacent Farm (Replaceable Parts)"
				],
				requiredTech=None,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.quarry:
			# https://civilization.fandom.com/wiki/Quarry_(Civ6)
			return ImprovementTypeData(
				name="Quarry",
				effects=[
					"-1 Appeal",
					"+1 [Production] Production",
					"+2 [Gold] Gold (Banking)",
					"+1 [Production] Production (Rocketry)",
					"+1 [Production] Production (Gunpowder)",
					"+1 [Production] Production (Predictive Systems)"
				],
				requiredTech=TechType.mining,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.camp:
			# https://civilization.fandom.com/wiki/Camp_(Civ6)
			return ImprovementTypeData(
				name="Camp",
				effects=[
					"+2 [Gold] Gold",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Mercantilism)",
					"+1 [Production] (Mercantilism)",
					"+1 [Gold] Gold (Synthetic Materials)"
				],
				requiredTech=TechType.animalHusbandry,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.fishingBoats:
			# https://civilization.fandom.com/wiki/Fishing_Boats_(Civ6)
			return ImprovementTypeData(
				name="Fishing Boats",
				effects=[
					"+1 [Food] Food",
					"+0.5 [Housing] Housing",
					"+2 [Gold] Gold (Cartography)",
					"+1 [Food] Food (Plastics)"
				],
				requiredTech=TechType.sailing,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			return ImprovementTypeData(
				name="Pasture",
				effects=[
					"+1 [Production] Production",
					"+0.5 [Housing] Housing",
					"+1 [Food] Food (Stirrups)",
					"+1 [Production] Production (Robotics)"
				],
				requiredTech=TechType.animalHusbandry,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.oilWell:
			# https://civilization.fandom.com/wiki/Oil_Well_(Civ6)
			return ImprovementTypeData(
				name="Oil well",
				effects=[
					"-1 Appeal",
					"+2 [Production] Production"
				],
				requiredTech=TechType.steel,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.fort:
			# https://civilization.fandom.com/wiki/Fort_(Civ6)
			return ImprovementTypeData(
				name="Fort",
				effects=[
					"Occupying unit receives +4 Defense Strength and 2 turns of fortification.",
					"Built by a Military Engineer."
				],
				requiredTech=TechType.siegeTactics,
				civilization=None,
				flavors=[]
			)
		elif self == ImprovementType.goodyHut:
			#
			return ImprovementTypeData(
				name="Goodyhut",
				effects=[],
				requiredTech=None,
				civilization=None,
				flavors=[]
			)

		raise InvalidEnumError(self)

	def yieldsFor(self, player, visibleResource):
		if self == ImprovementType.none:
			return Yields(food=0, production=0, gold=0, science=0)
		elif self == ImprovementType.mine:
			# https://civilization.fandom.com/wiki/Mine_(Civ6)
			yieldValue =  Yields(food=0, production=1, gold=0, science=0, appeal=-1.0)

			# +1 additional Production (requires Apprenticeship)
			if player.techs.hasTech(TechType.apprenticeship):
				yieldValue.production += 1

			# +1 additional Production (requires Industrialization)
			if player.techs.hasTech(TechType.industrialization):
				yieldValue.production += 1

			# Provides adjacency bonus for Industrial Zones (+1 Production, ½ in GS-Only.png).

			# +1 additional Production (requires Smart Materials)
			#  /*if techs.has(tech: .smartMaterials) {
			#   yieldValue.production += 2

			return yieldValue
		elif self == ImprovementType.plantation:
			# https://civilization.fandom.com/wiki/Plantation_(Civ6)
			yieldValue = Yields(food=0, production=0, gold=2, science=0, housing=0.5)

			if player.civics.hasCivic(CivicType.feudalism):
				yieldValue.food += 1

			# +1 Food (Scientific Theory)
			if player.techs.hasTech(TechType.scientificTheory):
				yieldValue.food += 1

			# +2 Gold (Globalization)
			if player.civics.hasCivic(CivicType.globalization):
				yieldValue.gold += 2

			return yieldValue
		elif self == ImprovementType.farm:
			# https//civilization.fandom.com/wiki/Farm_(Civ6)
			yieldValue = Yields(food=1, production=0, gold=0, science=0, housing=0.5)

			# +1 additional Food with two adjacent Farms (requires Feudalism)
			if player.civics.hasCivic(CivicType.feudalism):
				yieldValue.food += 1

			# +1 additional Food for each adjacent Farm (requires Replaceable Parts)
			if player.techs.hasTech(TechType.replaceableParts):
				yieldValue.food += 1

			return yieldValue
		elif self == ImprovementType.quarry:
			yieldValue = Yields(food=0, production=1, gold=0, science=0, appeal=-1.0)

			# +2 Gold (Banking)
			if player.techs.hasTech(TechType.banking):
				yieldValue.gold += 2

			# +1 Production (Rocketry)
			if player.techs.hasTech(TechType.rocketry):
				yieldValue.production += 1

			# +1 Production (Gunpowder)
			if player.techs.hasTech(TechType.gunpowder):
				yieldValue.production += 1

			# +1 Production (Predictive Systems)
			#  /*if techs.has(tech: .pred) {
			# yieldValue.production += 1

			return yieldValue
		elif self == ImprovementType.camp:
			yieldValue = Yields(food=0, production=0, gold=1, science=0)

			# +1 Food and +1 Production (requires Mercantilism)
			if player.civics.hasCivic(CivicType.mercantilism):
				yieldValue.food += 1
				yieldValue.production += 1

			# +2 additional Gold (requires Synthetic Materials)
			if player.techs.hasTech(TechType.syntheticMaterials):
				yieldValue.gold += 2

			return yieldValue
		elif self == ImprovementType.fishingBoats:
			# https://civilization.fandom.com/wiki/Fishing_Boats_(Civ6)
			yieldValue = Yields(food=1, production=0, gold=0, science=0, housing=0.5)

			if player.techs.hasTech(TechType.cartography):
				yieldValue.gold += 2

			if player.civics.hasCivic(CivicType.colonialism):
				yieldValue.production += 1

			if player.techs.hasTech(TechType.plastics):
				yieldValue.food += 1

			return yieldValue
		elif self == ImprovementType.pasture:
			# https://civilization.fandom.com/wiki/Pasture_(Civ6)
			yieldValue = Yields(food=0, production=1, gold=0, science=0, housing=0.5)

			# +1 Food (requires Stirrups)
			if player.techs.hasTech(TechType.stirrups):
				yieldValue.food += 1

			# +1 additional Production and +1 additional Food (requires Robotics)
			if player.techs.hasTech(TechType.robotics):
				yieldValue.production += 1
				yieldValue.food += 1

			# +1 Production from every adjacent Outback Station (requires Steam Power)

			# +1 additional Production (requires Replaceable Parts)
			if player.techs.hasTech(TechType.replaceableParts):
				yieldValue.production += 1

			return yieldValue

		raise InvalidEnumError(self)
