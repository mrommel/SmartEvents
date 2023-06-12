from core.base import ExtendedEnum


class SpecialistType(ExtendedEnum):
	none = 'none'

	citizen = 'citizen'

	merchant = 'merchant'
	captain = 'captain'
	artist = 'artist'
	priest = 'priest'
	commander = 'commander'
	engineer = 'engineer'


class SpecialistSlots:
	def __init__(self, specialistType: SpecialistType, amount: int):
		self.specialistType = specialistType
		self.amount = amount
