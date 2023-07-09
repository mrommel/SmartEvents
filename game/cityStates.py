from game.envoys import EnvoyEffectLevel
from core.base import ExtendedEnum, InvalidEnumError
from core.theming import Color
from utils.translation import gettext_lazy as _


class CityStateCategoryData:
	def __init__(self, name: str, color: Color, firstEnvoyBonus: str, thirdEnvoyBonus: str, sixthEnvoyBonus: str):
		self.name = name
		self.color = color
		self.firstEnvoyBonus = firstEnvoyBonus
		self.thirdEnvoyBonus = thirdEnvoyBonus
		self.sixthEnvoyBonus = sixthEnvoyBonus


class CityStateCategory(ExtendedEnum):
	cultural = 'cultural'
	industrial = 'industrial'
	militaristic = 'militaristic'
	religious = 'religious'
	scientific = 'scientific'
	trade = 'trade'

	def name(self) -> str:
		return self._data().name

	def _data(self):
		if self == CityStateCategory.cultural:
			return CityStateCategoryData(
				name=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_NAME"),
				color=Color.magenta,
				firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_FIRST_ENVOY_BONUS"),
				thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_THIRD_ENVOY_BONUS"),
				sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_SIXTH_ENVOY_BONUS")
			)
		elif self == CityStateCategory.industrial:
			return CityStateCategoryData(
				name=_("TXT_KEY_CITY_STATE_CATEGORY_INDUSTRIAL_NAME"),
				color=Color.orange,
				firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_INDUSTRIAL_FIRST_ENVOY_BONUS"),
				thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_INDUSTRIAL_THIRD_ENVOY_BONUS"),
				sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_INDUSTRIAL_SIXTH_ENVOY_BONUS")
			)
		elif self == CityStateCategory.militaristic:
			return CityStateCategoryData(
				name=_("TXT_KEY_CITY_STATE_CATEGORY_MILITARISTIC_NAME"),
				color=Color.red,
				firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_MILITARISTIC_FIRST_ENVOY_BONUS"),
				thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_MILITARISTIC_THIRD_ENVOY_BONUS"),
				sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_MILITARISTIC_SIXTH_ENVOY_BONUS")
			)
		elif self == CityStateCategory.religious:
			return CityStateCategoryData(
				name=_("TXT_KEY_CITY_STATE_CATEGORY_RELIGIOUS_NAME"),
				color=Color.white,
				firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_RELIGIOUS_FIRST_ENVOY_BONUS"),
				thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_RELIGIOUS_THIRD_ENVOY_BONUS"),
				sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_RELIGIOUS_SIXTH_ENVOY_BONUS")
			)
		elif self == CityStateCategory.scientific:
			return CityStateCategoryData(
				name=_("TXT_KEY_CITY_STATE_CATEGORY_SCIENTIFIC_NAME"),
				color=Color.blue,
				firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_SCIENTIFIC_FIRST_ENVOY_BONUS"),
				thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_SCIENTIFIC_THIRD_ENVOY_BONUS"),
				sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_SCIENTIFIC_SIXTH_ENVOY_BONUS")
			)
		elif self == CityStateCategory.trade:
			return CityStateCategoryData(
				name=_("TXT_KEY_CITY_STATE_CATEGORY_TRADE_NAME"),
				color=Color.yellow,
				firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_TRADE_FIRST_ENVOY_BONUS"),
				thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_TRADE_THIRD_ENVOY_BONUS"),
				sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_TRADE_SIXTH_ENVOY_BONUS")
			)

		raise InvalidEnumError(self)

	def firstEnvoyBonus(self):
		return self._data().firstEnvoyBonus

	def thirdEnvoyBonus(self):
		return self._data().thirdEnvoyBonus

	def sixthEnvoyBonus(self):
		return self._data().sixthEnvoyBonus


class CityStateTypeData:
	def __init__(self, name: str, category: CityStateCategory, suzarinBonus: str):
		self.name = name
		self.category = category
		self.suzarinBonus = suzarinBonus


class CityStateType:
	pass


class CityStateType(ExtendedEnum):
	# akkad
	amsterdam = 'amsterdam'
	# anshan
	# antananarivo
	# antioch
	# armagh
	auckland = 'auckland'
	# ayutthaya
	babylon = 'babylon'
	# bandarBrunei
	bologna = 'bologna'
	# brussels
	# buenosAires
	# caguana
	# cahokia
	# cardiff
	carthage = 'carthage'
	# chinguetti
	# fez
	geneva = 'geneva'
	# granada
	# hattusa
	# hongKong
	# hunza
	# jakarta
	# jerusalem
	johannesburg = 'johannesburg'
	kabul = 'kabul'
	# kandy
	# kumasi
	# laVenta
	# Lahore
	# Lisbon
	# Mexico City
	# Mitla
	# Mogadishu
	# Mohenjo-Daro
	# Muscat
	# Nalanda
	# Nan Madol
	# Nazca
	# Ngazargamu
	# Palenque
	# Preslav
	# Rapa Nui
	# samarkand
	seoul = 'seoul'
	singapore = 'singapore'
	stockholm = 'stockholm'
	# taruga
	toronto = 'toronto'
	valletta = 'valletta'
	# vaticanCity
	venice = 'venice'
	vilnius = 'vilnius'
	wolin = 'wolin'
	# yerevan
	# zanzibar
	
	@staticmethod
	def fromName(cityStateName: str) -> CityStateType:
		# akkad
		if cityStateName == 'CityStateType.amsterdam' or cityStateName == 'amsterdam':
			return CityStateType.amsterdam
		# anshan
		# antananarivo
		# antioch
		# armagh
		if cityStateName == 'CityStateType.auckland' or cityStateName == 'auckland':
			return CityStateType.auckland
		# ayutthaya
		if cityStateName == 'CityStateType.babylon' or cityStateName == 'babylon':
			return CityStateType.babylon
		# bandarBrunei
		if cityStateName == 'CityStateType.bologna' or cityStateName == 'bologna':
			return CityStateType.bologna
		# brussels
		# buenosAires
		# caguana
		# cahokia
		# cardiff
		if cityStateName == 'CityStateType.carthage' or cityStateName == 'carthage':
			return CityStateType.carthage
		# chinguetti
		# fez
		if cityStateName == 'CityStateType.geneva' or cityStateName == 'geneva':
			return CityStateType.geneva
		# granada
		# hattusa
		# hongKong
		# hunza
		# jakarta
		# jerusalem
		if cityStateName == 'CityStateType.johannesburg' or cityStateName == 'johannesburg':
			return CityStateType.johannesburg
		if cityStateName == 'CityStateType.kabul' or cityStateName == 'kabul':
			return CityStateType.kabul
		# kandy
		# kumasi
		# laVenta
		# Lahore
		# Lisbon
		# Mexico City
		# Mitla
		# Mogadishu
		# Mohenjo-Daro
		# Muscat
		# Nalanda
		# Nan Madol
		# Nazca
		# Ngazargamu
		# Palenque
		# Preslav
		# Rapa Nui
		# samarkand
		if cityStateName == 'CityStateType.seoul' or cityStateName == 'seoul':
			return CityStateType.seoul
		if cityStateName == 'CityStateType.singapore' or cityStateName == 'singapore':
			return CityStateType.singapore
		if cityStateName == 'CityStateType.stockholm' or cityStateName == 'stockholm':
			return CityStateType.stockholm
		# taruga
		if cityStateName == 'CityStateType.toronto' or cityStateName == 'toronto':
			return CityStateType.toronto
		if cityStateName == 'CityStateType.valletta' or cityStateName == 'valletta':
			return CityStateType.valletta
		# vaticanCity
		if cityStateName == 'CityStateType.venice' or cityStateName == 'venice':
			return CityStateType.venice
		if cityStateName == 'CityStateType.vilnius' or cityStateName == 'vilnius':
			return CityStateType.vilnius
		if cityStateName == 'CityStateType.wolin' or cityStateName == 'wolin':
			return CityStateType.wolin
		# yerevan
		# zanzibar

		raise Exception(f'No matching case for cityStateName: "{cityStateName}"')

	def name(self) -> str:
		return self._data().name

	def category(self) -> CityStateCategory:
		return self._data().category

	def bonusFor(self, level: EnvoyEffectLevel) -> str:
		if level == EnvoyEffectLevel.first:
			return self.category().firstEnvoyBonus()
		elif level == EnvoyEffectLevel.third:
			return self.category().thirdEnvoyBonus()
		elif level == EnvoyEffectLevel.sixth:
			return self.category().sixthEnvoyBonus()
		elif level == EnvoyEffectLevel.suzerain:
			return self._data().suzarinBonus

		raise InvalidEnumError(level)

	def _data(self) -> CityStateTypeData:
		# akkad
		if self == CityStateType.amsterdam:
			# https://civilization.fandom.com/wiki/Amsterdam_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_AMSTERDAM_NAME"),
				category=CityStateCategory.trade,
				suzarinBonus=_("TXT_KEY_CITY_STATE_AMSTERDAM_SUZARIN")
			)
		# anshan
		# antananarivo
		# antioch
		# armagh
		elif self == CityStateType.auckland:
			# https://civilization.fandom.com/wiki/Auckland_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_AUCKLAND_NAME"),
				category=CityStateCategory.industrial,
				suzarinBonus=_("TXT_KEY_CITY_STATE_AUCKLAND_SUZARIN")
			)
		# ayutthaya
		elif self == CityStateType.babylon:
			# https://civilization.fandom.com/wiki/Babylon_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_BABYLON_NAME"),
				category=CityStateCategory.scientific,
				suzarinBonus=_("TXT_KEY_CITY_STATE_BABYLON_SUZARIN")
			)
		# bandarBrunei
		elif self == CityStateType.bologna:
			# https://civilization.fandom.com/wiki/Bologna_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_BOLOGNA_NAME"),
				category=CityStateCategory.scientific,
				suzarinBonus=_("TXT_KEY_CITY_STATE_BOLOGNA_SUZARIN")
			)
		# brussels
		# buenosAires
		# caguana
		# cahokia
		# cardiff
		elif self == CityStateType.carthage:
			# https://civilization.fandom.com/wiki/Carthage_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_CARTHAGE_NAME"),
				category=CityStateCategory.militaristic,
				suzarinBonus=_("TXT_KEY_CITY_STATE_CARTHAGE_SUZARIN")
			)
		# chinguetti
		# fez
		elif self == CityStateType.geneva:
			# https://civilization.fandom.com/wiki/Geneva_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_GENEVA_NAME"),
				category=CityStateCategory.scientific,
				suzarinBonus=_("TXT_KEY_CITY_STATE_GENEVA_SUZARIN")
			)
		# granada
		# hattusa
		# hongKong
		# hunza
		# jakarta
		# jerusalem
		elif self == CityStateType.johannesburg:
			# https://civilization.fandom.com/wiki/Johannesburg_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_JOHANNESBURG_NAME"),
				category=CityStateCategory.industrial,
				suzarinBonus=_("TXT_KEY_CITY_STATE_JOHANNESBURG_SUZARIN")
			)
		elif self == CityStateType.kabul:
			# https://civilization.fandom.com/wiki/Kabul_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_KABUL_NAME"),
				category=CityStateCategory.militaristic,
				suzarinBonus=_("TXT_KEY_CITY_STATE_KABUL_SUZARIN")
			)
		# kandy
		# kumasi
		# laVenta
		# Lahore
		# Lisbon
		# Mexico City
		# Mitla
		# Mogadishu
		# Mohenjo-Daro
		# Muscat
		# Nalanda
		# Nan Madol
		# Nazca
		# Ngazargamu
		# Palenque
		# Preslav
		# Rapa Nui
		# samarkand
		elif self == CityStateType.seoul:
			# https://civilization.fandom.com/wiki/Seoul_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_SEOUL_NAME"),
				category=CityStateCategory.scientific,
				suzarinBonus=_("TXT_KEY_CITY_STATE_SEOUL_SUZARIN")
			)
		elif self == CityStateType.singapore:
			# https://civilization.fandom.com/wiki/Singapore_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_SINGAPORE_NAME"),
				category=CityStateCategory.industrial,
				suzarinBonus=_("TXT_KEY_CITY_STATE_SINGAPORE_SUZARIN")
			)
		elif self == CityStateType.stockholm:
			# https://civilization.fandom.com/wiki/Stockholm_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_STOCKHOLM_NAME"),
				category=CityStateCategory.scientific,
				suzarinBonus=_("TXT_KEY_CITY_STATE_STOCKHOLM_SUZARIN")
			)
		# taruga
		elif self == CityStateType.toronto:
			# https://civilization.fandom.com/wiki/Toronto_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_TORONTO_NAME"),
				category=CityStateCategory.industrial,
				suzarinBonus=_("TXT_KEY_CITY_STATE_TORONTO_SUZARIN")
			)
		elif self == CityStateType.valletta:
			# https://civilization.fandom.com/wiki/Valletta_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_VALLETTA_NAME"),
				category=CityStateCategory.militaristic,
				suzarinBonus=_("TXT_KEY_CITY_STATE_VALLETTA_SUZARIN")
			)
		# vaticanCity
		elif self == CityStateType.venice:
			# https://civilization.fandom.com/wiki/Venice_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_VENICE_NAME"),
				category=CityStateCategory.trade,
				suzarinBonus=_("TXT_KEY_CITY_STATE_VENICE_SUZARIN")
			)
		elif self == CityStateType.vilnius:
			# https://civilization.fandom.com/wiki/Vilnius_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_VILNIUS_NAME"),
				category=CityStateCategory.cultural,
				suzarinBonus=_("TXT_KEY_CITY_STATE_VILNIUS_SUZARIN")
			)
		elif self == CityStateType.wolin:
			# https://civilization.fandom.com/wiki/Wolin_(Civ6)
			return CityStateTypeData(
				name=_("TXT_KEY_CITY_STATE_WOLIN_NAME"),
				category=CityStateCategory.militaristic,
				suzarinBonus=_("TXT_KEY_CITY_STATE_WOLIN_SUZARIN")
			)
		# yerevan
		# zanzibar

		raise InvalidEnumError(self)