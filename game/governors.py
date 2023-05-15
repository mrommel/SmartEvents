from utils.base import ExtendedEnum


class GovernorType(ExtendedEnum):
	liang = 'liang'
	reyna = 'reyna'


class GovernorTitle(ExtendedEnum):
	# reyna
	forestryManagement = 'forestryManagement'


class Governor:
	def __init__(self, type: GovernorType):
		self.type = type
