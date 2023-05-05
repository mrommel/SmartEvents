from game.buildings import BuildingType
from game.districts import DistrictType
from game.governments import GovernmentType
from game.policy_cards import PolicyCardType
from game.unit_types import UnitType
from game.wonders import WonderType


class CivicAchievements:
	def __init__(self, civic):
		self.buildingTypes = list(filter(lambda building: building.requiredCivic() == civic, list(BuildingType)))
		self.unitTypes = list(filter(lambda unit: unit.civilization() is None and unit.requiredCivic() == civic, list(UnitType)))
		self.wonderTypes = list(filter(lambda wonder: wonder.requiredCivic() == civic, list(WonderType)))
		self.buildTypes = []
		self.districtTypes = list(filter(lambda district: district.requiredCivic() == civic, list(DistrictType)))
		self.policyCards = list(filter(lambda policyCard: not policyCard.requiresDarkAge() and policyCard.requiredCivic() == civic, list(PolicyCardType)))
		self.governments = list(filter(lambda government: government.requiredCivic() == civic, list(GovernmentType)))
