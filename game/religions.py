from core.base import ExtendedEnum


class PantheonTypeData:
	def __init__(self, name: str, bonus: str):
		self.name = name
		self.bonus = bonus

class PantheonType(ExtendedEnum):
	none = 'none'

	cityPatronGoddess = 'cityPatronGoddess'
	danceOfTheAurora = 'danceOfTheAurora'
	desertFolklore = 'desertFolklore'
	divineSpark = 'divineSpark'
	earthGoddess = 'earthGoddess'
	fertilityRites = 'fertilityRites'
	fireGoddess = 'fireGoddess'
	godOfCraftsmen = 'godOfCraftsmen'
	godOfHealing = 'godOfHealing'
	godOfTheForge = 'godOfTheForge'
	godOfTheOpenSky = 'godOfTheOpenSky'
	godOfTheSea = 'godOfTheSea'
	godOfWar = 'godOfWar'
	goddessOfFestivals = 'goddessOfFestivals'
	goddessOfTheHarvest = 'goddessOfTheHarvest'
	goddessOfTheHunt = 'goddessOfTheHunt'
	initiationRites = 'initiationRites'
	ladyOfTheReedsAndMarshes = 'ladyOfTheReedsAndMarshes'
	monumentToTheGods = 'monumentToTheGods'
	oralTradition = 'oralTradition'
	religiousIdols = 'religiousIdols'
	religiousSettlements = 'religiousSettlements'
	riverGoddess = 'riverGoddess'
	sacredPath = 'sacredPath'
	stoneCircles = 'stoneCircles'

	def name(self) -> str:
		return self._data().name

	def _data(self) -> PantheonTypeData:
		if self == PantheonType.none:
			return PantheonTypeData(
				name="None",
				bonus=""
			)
		elif self == PantheonType.cityPatronGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_CITY_PATRON_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_CITY_PATRON_GODDESS_BONUS"
			)
		elif self == PantheonType.danceOfTheAurora:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_DANCE_OF_THE_AURORA_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_DANCE_OF_THE_AURORA_BONUS"
			)
		elif self == PantheonType.desertFolklore:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_DESERT_FOLKLORE_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_DESERT_FOLKLORE_BONUS"
			)
		elif self == PantheonType.divineSpark:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_DIVINE_SPARK_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_DIVINE_SPARK_BONUS"
			)
		elif self == PantheonType.earthGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_EARTH_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_EARTH_GODDESS_BONUS"
			)
		elif self == PantheonType.fertilityRites:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_FERTILITY_RITES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_FERTILITY_RITES_BONUS"
			)
		elif self == PantheonType.fireGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_FIRE_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_FIRE_GODDESS_BONUS"
			)
		elif self == PantheonType.godOfCraftsmen:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_CRAFTSMEN_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_CRAFTSMEN_BONUS"
			)
		elif self == PantheonType.godOfHealing:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_HEALING_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_HEALING_BONUS"
			)
		elif self == PantheonType.godOfTheForge:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_FORGE_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_FORGE_BONUS"
			)
		elif self == PantheonType.godOfTheOpenSky:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_OPEN_SKY_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_OPEN_SKY_BONUS"
			)
		elif self == PantheonType.godOfTheSea:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_SEA_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_THE_SEA_BONUS"
			)
		elif self == PantheonType.godOfWar:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GOD_OF_WAR_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GOD_OF_WAR_BONUS"
			)
		elif self == PantheonType.goddessOfFestivals:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_FESTIVALS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_FESTIVALS_BONUS"
			)
		elif self == PantheonType.goddessOfTheHarvest:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HARVEST_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HARVEST_BONUS"
			)
		elif self == PantheonType.goddessOfTheHunt:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HUNT_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_GODDESS_OF_THE_HUNT_BONUS"
			)
		elif self == PantheonType.initiationRites:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_INITIATION_RITES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_INITIATION_RITES_BONUS"
			)
		elif self == PantheonType.ladyOfTheReedsAndMarshes:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_LADY_OF_THE_REEDS_AND_MARSHES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_LADY_OF_THE_REEDS_AND_MARSHES_BONUS"
			)
		elif self == PantheonType.monumentToTheGods:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_MONUMENT_TO_THE_GODS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_MONUMENT_TO_THE_GODS_BONUS"
			)
		elif self == PantheonType.oralTradition:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_ORAL_TRADITION_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_ORAL_TRADITION_BONUS"
			)
		elif self == PantheonType.religiousIdols:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_IDOLS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_IDOLS_BONUS"
			)
		elif self == PantheonType.riverGoddess:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_RIVER_GODDESS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_RIVER_GODDESS_BONUS"
			)
		elif self == PantheonType.religiousSettlements:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_SETTLEMENTS_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_RELIGIOUS_SETTLEMENTS_BONUS"
			)
		elif self == PantheonType.sacredPath:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_SACRED_PATH_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_SACRED_PATH_BONUS"
			)
		elif self == PantheonType.stoneCircles:
			return PantheonTypeData(
				name="TXT_KEY_RELIGION_PANTHEON_STONE_CIRCLES_TITLE",
				bonus="TXT_KEY_RELIGION_PANTHEON_STONE_CIRCLES_BONUS"
			)


class ReligionType(ExtendedEnum):
	none = 'none'
