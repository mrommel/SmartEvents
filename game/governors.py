from map import constants
from core.base import ExtendedEnum


class GovernorType(ExtendedEnum):
	liang = 'liang'
	reyna = 'reyna'
	magnus = 'magnus'


class GovernorTitle(ExtendedEnum):
	# reyna
	forestryManagement = 'forestryManagement'

	# ???
	researcher = 'researcher'
	librarian = 'librarian'
	connoisseur = 'connoisseur'
	redoubt = 'redoubt'
	zoningCommissioner = 'zoningCommissioner'
	layingOnOfHands = 'layingOnOfHands'
	surplusLogistics = 'surplusLogistics'


class Governor:
	def __init__(self, type: GovernorType):
		self._type = type
		self._location = constants.invalidHexPoint

	def type(self) -> GovernorType:
		return self._type

	def defaultTitle(self) -> GovernorTitle:
		return self._type.defaultTitle()
