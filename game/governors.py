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


class Governor:
	def __init__(self, type: GovernorType):
		self._type = type
		self._location = constants.invalidHexPoint
