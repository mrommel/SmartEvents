from map import constants
from core.base import ExtendedEnum


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
	provision = 'provision'
	guildmaster = 'guildmaster'
	blackMarketeer = 'blackMarketeer'
	embrasure = 'embrasure'


class GovernorType(ExtendedEnum):
	liang = 'liang'
	reyna = 'reyna'
	magnus = 'magnus'
	victor = 'victor'

	def defaultTitle(self) -> GovernorTitle:
		if self == GovernorType.reyna:
			return GovernorTitle.redoubt

		return GovernorTitle.redoubt


class Governor:
	def __init__(self, type: GovernorType):
		self._type = type
		self._location = constants.invalidHexPoint
		self._titles = []

	def type(self) -> GovernorType:
		return self._type

	def defaultTitle(self) -> GovernorTitle:
		return self._type.defaultTitle()

	def hasTitle(self, title: GovernorTitle) -> bool:
		return title in self._titles
