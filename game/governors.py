from map import constants
from utils.base import ExtendedEnum


class GovernorType(ExtendedEnum):
	liang = 'liang'
	reyna = 'reyna'


class GovernorTitle(ExtendedEnum):
	# reyna
	forestryManagement = 'forestryManagement'

	# ???
	researcher = 'researcher'
	librarian = 'librarian'
	connoisseur = 'connoisseur'
	redoubt = 'redoubt'
	zoningCommissioner = 'zoningCommissioner'


class Governor:
	def __init__(self, type: GovernorType):
		self._type = type
		self._location = constants.invalidHexPoint

	def type(self) -> GovernorType:
		return self._type

	def defaultTitle(self) -> GovernorTitle:
		return self._type.defaultTitle()
