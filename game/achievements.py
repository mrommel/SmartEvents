from game.unit_types import UnitType


class CivicAchievements:
	def __init__(self, civic):
		self.buildingTypes = list(filter(lambda building: building.requiredCivic() == civic, BuildingType.list()))
		self.unitTypes = list(filter(lambda unit: unit.civilization() is None and unit.requiredCivic() == civic, UnitType.list()))
		self.wonderTypes = list(filter(lambda wonder: wonder.requiredCivic() == civic, WonderType.list()))
		self.buildTypes = []
		self.districtTypes = list(filter(lambda district: district.requiredCivic() == civic, DistrictType.list()))
		self.policyCards = list(filter(lambda policyCard: not policyCard.requiresDarkAge() and policyCard.requiredCivic() == civic, PolicyCardType.list()))
		self.governments = list(filter(lambda government: government.requiredCivic() == civic, GovernmentType.list()))
