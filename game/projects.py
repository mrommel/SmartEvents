from utils.base import ExtendedEnum


class ProjectType(ExtendedEnum):
	none = 'none'
	def productionCost(self) -> float:
		return 0.0
