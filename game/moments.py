from typing import Optional

from game.civilizations import CivilizationType
from game.types import EraType
from utils.base import ExtendedEnum, InvalidEnumError


class MomentCategory(ExtendedEnum):
	major = 'major'
	minor = 'minor'
	hidden = 'hidden'


class MomentTypeData:
	def __init__(self, name: str, summary: str, instanceText: Optional[str],
                 category: MomentCategory, eraScore: int, minEra: EraType = EraType.ancient,
                 maxEra: EraType = EraType.future):
		self.name = name
		self.summary = summary
		self.instanceText = instanceText
		self.category = category
		self.eraScore = eraScore
		self.minEra = minEra
		self.maxEra = maxEra


class MomentType(ExtendedEnum):
	# major
	# admiralDefeatsEnemy  # 1 #
	# allGovernorsAppointed  # 2
	# canalCompleted  # 3 #
	# cityNearFloodableRiver(cityName: String)  # 4 #
	cityNearVolcano = 'cityNearVolcano'  # (cityName: String)  # 5
	cityOfAwe = 'cityOfAwe'  # (cityName: String)  # 6
	cityOnNewContinent = 'cityOnNewContinent'  # (cityName: String, continentName: String)  # 7
	# cityStatesFirstSuzerain(cityState: CityStateType)  # 8
	# cityStateArmyLeviedNearEnemy 9
	# climateChangePhase 10
	# darkAgeBegins  # 11
	discoveryOfANaturalWonder = 'discoveryOfANaturalWonder'  # (naturalWonder: FeatureType)  # 12
	# emergencyCompletedSuccessfully 13
	# emergencySuccessfullyDefended 14
	# enemyCityAdoptsOurReligion  # 15 #
	# enemyCityStatePacified 16
	# enemyFormationDefeated  # 17 #
	# enemyVeteranDefeated  # 18 #
	# exoplanetExpeditionLaunched  # 19 #
	# finalForeignCityTaken  # 20 #
	# firstAerodromeFullyDeveloped  # 21 #
	# firstBustlingCity(cityName: String)  # 22
	# firstCivicOfNewEra(eraType: EraType)  # 23
	# firstCorporationCreated 24
	# firstCorporationInTheWorld 25
	# firstDiscoveryOfANaturalWonder  # 26 #
	# firstDiscoveryOfANewContinent  # 27
	# firstEncampmentFullyDeveloped  # 28 #
	# firstEnormousCity(cityName: String)  # 29
	# firstEntertainmentComplexFullyDeveloped  # 30 #
	# firstGiganticCity(cityName: String)  # 31
	# firstGreenImprovement 32
	# firstGreenImprovementInWorld 33
	# firstHeroClaimed 34
	# firstHeroDeparted 35
	# firstHeroRecalled 36
	# firstImprovementAfterNaturalDisaster 37
	# firstIndustryCreated 38
	# firstIndustryInTheWorld 39
	# firstLargeCity(cityName: String)  # 40
	# firstLuxuryResourceMonopoly 41
	# firstLuxuryResourceMonopolyInTheWorld 42
	# firstMasterSpyEarned 43
	# firstMountainTunnel 44
	# firstMountainTunnelInTheWorld 45
	firstNeighborhoodCompleted = 'firstNeighborhoodCompleted'  # 46
	# firstRailroadConnection 47
	# firstRailroadConnectionInWorld 48
	# firstResourceConsumedForPower 49
	# firstResourceConsumedForPowerInWorld 50
	# firstRockBandConcert 51
	# firstRockBandConcertInWorld 52
	# firstSeasideResort 53
	# firstShipwreckExcavated  # 54 #
	# firstTechnologyOfNewEra(eraType: EraType)  # 55
	# firstTier1Government(governmentType: GovernmentType)  # 56 #
	# firstTier1GovernmentInWorld(governmentType: GovernmentType)  # 57 #
	# firstTier2Government(governmentType: GovernmentType)  # 58 #
	# firstTier2GovernmentInWorld(governmentType: GovernmentType)  # 59 #
	# firstTier3Government(governmentType: GovernmentType)  # 60 #
	# firstTier3GovernmentInWorld(governmentType: GovernmentType)  # 61 #
	# firstTier4Government(governmentType: GovernmentType)  # 62 #
	# firstTier4GovernmentInWorld(governmentType: GovernmentType)  # 63 #
	# firstTradingPostsInAllCivilizations  # 64 #
	# firstUnitPromotedWithDistinction  # 65 #
	# firstWaterParkFullyDeveloped 66
	# freeCityJoins 67
	# generalDefeatsEnemy  # 68 #
	# goldenAgeBegins  # 69 #
	# governorFullyPromoted  # 70
	# greatPersonLuredByFaith 71
	# greatPersonLuredByGold 72
	# heroicAgeBegins  # 73 #
	# inquisitionBegins 74
	# leviedArmyStandsDown 75
	# metAllCivilizations  # 76 #
	# nationalParkFounded  # 77 #
	# normalAgeBegins  # 78 #
	# onTheWaves  # 79 #
	# religionAdoptsAllBeliefs  # 80 #
	# religionFounded(religion: ReligionType)  # 81
	# rivalHolyCityConverted  # 82 #
	# splendidCampusCompleted  # 83 #
	# splendidCommercialHubCompleted  # 84 #
	# splendidHarborCompleted  # 85 #
	# splendidHolySiteCompleted  # 86 #
	# splendidIndustrialZoneCompleted  # 87 #
	# splendidTheaterSquareCompleted  # 88 #
	# takingFlight  # 89 #
	# threateningCampDestroyed  # 90 #
	# tradingPostsInAllCivilizations  # 91 #
	# uniqueBuildingConstructed 92
	# uniqueDistrictCompleted 93
	# uniqueTileImprovementBuilt 94
	# uniqueUnitMarches 95
	# worldsFirstArmada 96
	# worldsFirstArmy 97
	# worldsFirstBustlingCity(cityName: String)  # 98
	# worldsFirstCircumnavigation  # 99
	# worldsFirstCivicOfNewEra(eraType: EraType)  # 100
	# worldsFirstCorps 101
	# worldsFirstEnormousCity(cityName: String)  # 102
	# worldsFirstExoplanetExpeditionLaunched  # 103 #
	# worldsFirstFleet  # 104 #
	# worldsFirstFlight  # 105 #
	# worldsFirstGiganticCity(cityName: String)  # 106
	# worldsFirstInquisition 107
	# worldsFirstLandingOnTheMoon  # 108 #
	# worldsFirstLargeCity(cityName: String)  # 109
	# worldsFirstMartianColonyEstablished  # 110 #
	# worldsFirstNationalPark  # 111 #
	worldsFirstNeighborhood = 'worldsFirstNeighborhood'  # 112
	# worldsFirstPantheon  # 113
	# worldsFirstReligion  # 114
	# worldsFirstReligionToAdoptAllBeliefs  # 115 #
	# worldsFirstSatelliteInOrbit  # 116 #
	# worldsFirstSeafaring  # 117 #
	# worldsFirstSeasideResort  # 118 #
	# worldsFirstShipwreckExcavated  # 119 #
	# worldsFirstStrategicResourcePotentialUnleashed  # 120 #
	# worldsFirstTechnologyOfNewEra(eraType: EraType)  # 121
	# worldsFirstToMeetAllCivilizations  # 122 #
	worldsLargestCivilization = 'worldsLargestCivilization'  # 123
	# worldCircumnavigated  # 124
	# 
	# minor
	# aggressiveCityPlacement  # 200 #
	# artifactExtracted  # 201 #
	# barbarianCampDestroyed  # 202
	# causeForWar(warType: CasusBelliType, civilizationType: CivilizationType)  # 203 #
	# cityReturnsToOriginalOwner(cityName: String, originalCivilization: CivilizationType)  # 204 #
	# cityStateArmyLevied  # 205 #
	# coastalFloodMitigated  # 206 #
	desertCity = 'desertCity'  # (cityName: String)  # 207
	# diplomaticVictoryResolutionWon  # 208 #
	# firstArmada 209
	# firstArmy  # 210 #
	# firstCorps  # 211 #
	# firstFleet  # 212 #
	# foreignCapitalTaken  # 213 #
	# greatPersonRecruited  # 214
	# heroClaimed  # 215 #
	# heroDeparted  # 216 #
	# heroRecalled  # 217 #
	# landedOnTheMoon  # 218 #
	# manhattanProjectCompleted  # 219 #
	# martianColonyEstablished  # 220 #
	# masterSpyEarned  # 221 #
	metNewCivilization = 'metNewCivilization'  # 222
	# oldGreatPersonRecruited  # 223
	# oldWorldWonderCompleted  # 224
	# operationIvyCompleted 225
	# pantheonFounded(pantheon: PantheonType)  # 226
	# riverFloodMitigated  # 227 #
	# satelliteLaunchedIntoOrbit  # 228 #
	snowCity = 'snowCity'  # (cityName: String)  # 229
	# strategicResourcePotentialUnleashed  # 230 #
	# tradingPostEstablishedInNewCivilization(civilization: CivilizationType)  # 231
	# tribalVillageContacted  # 232
	tundraCity = 'tundraCity'  # (cityName: String)  # 233
	# unitPromotedWithDistinction  # 234
	# wonderCompleted(wonder: WonderType)  # 235
	# 
	# hidden
	# shipSunk  # 300 for artifacts
	# battleFought  # 301
	dedicationTriggered = 'dedicationTriggered'  # 302 for dedications

	def name(self):
		return self._data().name

	def eraScore(self):
		return self._data().eraScore

	def minEra(self) -> EraType:
		return self._data().minEra

	def maxEra(self) -> EraType:
		return self._data().maxEra

	def _data(self) -> MomentTypeData:
		# ...
		if self == MomentType.cityNearVolcano: # (cityName: String)
			# 5
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_NEAR_VOLCANO_TITLE",
				summary="TXT_KEY_MOMENT_CITY_NEAR_VOLCANO_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		elif self == MomentType.cityOfAwe:  # (cityName: String)
			# 6
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_OF_AWE_TITLE",
				summary="TXT_KEY_MOMENT_CITY_OF_AWE_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=3
			)
		elif self == MomentType.cityOnNewContinent:  # (cityName: String, continentName: String)
			# 7
			return MomentTypeData(
				name="TXT_KEY_MOMENT_CITY_ON_NEW_CONTINENT_TITLE",
				summary="TXT_KEY_MOMENT_CITY_OF_NEW_CONTINENT_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=2
			)
		# ...
		elif self == MomentType.discoveryOfANaturalWonder:  # (naturalWonder: FeatureType)
			# 12
			return MomentTypeData(
				name="TXT_KEY_MOMENT_DISCOVERY_OF_A_NATURAL_WONDER_TITLE",
				summary="TXT_KEY_MOMENT_DISCOVERY_OF_A_NATURAL_WONDER_SUMMARY",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=1
			)
		# ..
		if self == MomentType.firstNeighborhoodCompleted:
			# 46
			return MomentTypeData(
				name="First Neighborhood Completed",
				summary="You have completed your civilization's first Neighborhood district.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=2
			)
		# ...
		elif self == MomentType.worldsFirstNeighborhood:
			# 112
			return MomentTypeData(
				name="World's First Neighborhood",
				summary="You have completed the world's first Neighborhood district.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=3
			)
		# ...
		elif self == MomentType.worldsLargestCivilization:
			# 123
			return MomentTypeData(
				name="World's Largest Civilization",
				summary="Your civilization has become the largest in the world, with at least 3 more cities than its "
				        "next biggest rival.",
				instanceText=None,
				category=MomentCategory.major,
				eraScore=3
			)
		# ...
		elif self == MomentType.desertCity:  # (cityName: String)
			# 207
			return MomentTypeData(
				name="TXT_KEY_MOMENT_DESERT_CITY_TITLE",
				summary="TXT_KEY_MOMENT_DESERT_CITY_SUMMARY",
				instanceText="TXT_KEY_MOMENT_DESERT_CITY_INSTANCE",
				category=MomentCategory.minor,
				eraScore=1
			)
		# ...
		elif self == MomentType.metNewCivilization:
			# 222
			return MomentTypeData(
				name="Met New Civilization",
				summary="You have made contact with a new civilization.",
				instanceText=None,
				category=MomentCategory.minor,
				eraScore=1
			)
		# oldGreatPersonRecruited  # 223
		# oldWorldWonderCompleted  # 224
		# operationIvyCompleted 225
		# pantheonFounded(pantheon: PantheonType)  # 226
		# riverFloodMitigated  # 227 #
		# satelliteLaunchedIntoOrbit  # 228 #
		elif self == MomentType.snowCity:  # (cityName: String)
			# 229
			return MomentTypeData(
				name="TXT_KEY_MOMENT_SNOW_CITY_TITLE",
				summary="TXT_KEY_MOMENT_SNOW_CITY_SUMMARY",
				instanceText="TXT_KEY_MOMENT_SNOW_CITY_INSTANCE",
				category=MomentCategory.minor,
				eraScore=1
			)
		# strategicResourcePotentialUnleashed  # 230 #
		# tradingPostEstablishedInNewCivilization(civilization: CivilizationType)  # 231
		# tribalVillageContacted  # 232
		elif self == MomentType.tundraCity:  # (cityName: String)
			# 233
			return MomentTypeData(
				name="TXT_KEY_MOMENT_TUNDRA_CITY_TITLE",
				summary="TXT_KEY_MOMENT_TUNDRA_CITY_SUMMARY",
				instanceText="TXT_KEY_MOMENT_TUNDRA_CITY_INSTANCE",
				category=MomentCategory.minor,
				eraScore=1
			)
		# unitPromotedWithDistinction  # 234
		# wonderCompleted(wonder: WonderType)  # 235

		# hidden
		# shipSunk  # 300 for artifacts
		# battleFought  # 301
		elif self == MomentType.dedicationTriggered:
			# 302
			return MomentTypeData(
				name="Dedication triggered",
				summary="Dedication triggered",
				instanceText=None,
				category=MomentCategory.hidden,
				eraScore=1
			)

		raise InvalidEnumError(self)


class Moment:
	def __init__(self, momentType: MomentType, turn: int, civilization: Optional[CivilizationType] = None,
	                cityName: Optional[str] = None, continentName: Optional[str] = None):
		self.type = momentType
		self.turn = turn

		# meta
		self.civilization = civilization
		self.cityName = cityName
		self.continentName = continentName
