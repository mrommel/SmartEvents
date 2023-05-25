from utils.base import ExtendedEnum


class AccessLevel:
	pass


class AccessLevel(ExtendedEnum):
	none = 'none'

	limited = 'limited'
	open = 'open'
	secret = 'secret'
	topSecret = 'topSecret'

	def increased(self):
		if self == AccessLevel.none:
			return AccessLevel.limited
		elif self == AccessLevel.limited:
			return AccessLevel.open
		elif self == AccessLevel.open:
			return AccessLevel.secret
		elif self == AccessLevel.secret:
			return AccessLevel.topSecret
		elif self == AccessLevel.topSecret:
			return AccessLevel.topSecret