import unittest

from game.baseTypes import HandicapType
from game.civilizations import LeaderType, CivilizationType
from game.game import Game
from game.moments import MomentType
from game.players import Player
from game.states.dedications import DedicationType
from game.types import EraType
from map.types import TerrainType, FeatureType
from tests.testBasics import MapMock, UserInterfaceMock


class TestMoments(unittest.TestCase):
	def test_moment_cityNearVolcano(self):  # 5
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.cityNearVolcano, cityName='Berlin')
		playerTrajan.addMoment(MomentType.cityNearVolcano, cityName='Berlin', simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.cityNearVolcano, cityName='Berlin'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.cityNearVolcano, cityName='Potsdam'))

	def test_moment_cityOfAwe(self):  # 6
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.cityOfAwe, cityName='Berlin')
		playerTrajan.addMoment(MomentType.cityOfAwe, cityName='Berlin', simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.cityOfAwe, cityName='Berlin'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.cityOfAwe, cityName='Potsdam'))

	def test_moment_cityOnNewContinent(self):  # 7
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.cityOnNewContinent, cityName='Berlin', continentName='Europe')
		playerTrajan.addMoment(MomentType.cityOnNewContinent, cityName='Berlin', continentName='Europe', simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.cityOnNewContinent, cityName='Berlin', continentName='Europe'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.cityOnNewContinent, cityName='Berlin', continentName='Asia'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.cityOnNewContinent, cityName='Potsdam', continentName='Europe'))

	# cityStatesFirstSuzerain(cityState: CityStateType)  # 8
	# cityStateArmyLeviedNearEnemy 9
	# climateChangePhase 10
	# darkAgeBegins  # 11

	def test_moment_discoveryOfANaturalWonder(self):  # 12
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.discoveryOfANaturalWonder, naturalWonder=FeatureType.cliffsOfDover)
		playerTrajan.addMoment(MomentType.discoveryOfANaturalWonder, naturalWonder=FeatureType.cliffsOfDover, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.discoveryOfANaturalWonder, naturalWonder=FeatureType.cliffsOfDover))
		self.assertFalse(playerTrajan.hasMoment(MomentType.discoveryOfANaturalWonder, naturalWonder=FeatureType.mountEverest))

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

	def test_moment_firstNeighborhoodCompleted(self):  # 46
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.firstNeighborhoodCompleted)
		playerTrajan.addMoment(MomentType.firstNeighborhoodCompleted, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.firstNeighborhoodCompleted))

	# firstRailroadConnection 47
	# firstRailroadConnectionInWorld 48
	# firstResourceConsumedForPower 49
	# firstResourceConsumedForPowerInWorld 50
	# firstRockBandConcert 51
	# firstRockBandConcertInWorld 52
	# firstSeasideResort 53
	# firstShipwreckExcavated  # 54

	def test_moment_firstTechnologyOfNewEra(self):  # 55
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.firstTechnologyOfNewEra, eraType=EraType.classical)
		playerTrajan.addMoment(MomentType.firstTechnologyOfNewEra, eraType=EraType.classical, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.firstTechnologyOfNewEra, eraType=EraType.classical))
		self.assertFalse(playerTrajan.hasMoment(MomentType.firstTechnologyOfNewEra, eraType=EraType.future))

	# ...

	def test_moment_metNewCivilization(self):  # 222
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.english)
		playerTrajan.addMoment(MomentType.metNewCivilization, civilization=CivilizationType.english, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.english))
		self.assertFalse(playerTrajan.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.greek))

	def test_trigger_metNewCivilization(self):
		# GIVEN
		mapModel = MapMock(10, 10, TerrainType.ocean)
		simulation = Game(mapModel)

		player = Player(LeaderType.trajan, human=True)
		player.initialize()

		otherPlayer = Player(LeaderType.alexander, human=False)
		otherPlayer.initialize()

		simulation.userInterface = UserInterfaceMock()

		# WHEN
		player.doFirstContactWith(otherPlayer, simulation)

		# THEN
		self.assertEqual(player.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.greek), True)
		self.assertEqual(player.hasMoment(MomentType.metNewCivilization, civilization=CivilizationType.english), False)

	# firstTier1Government(governmentType: GovernmentType)  # 56
	# firstTier1GovernmentInWorld(governmentType: GovernmentType)  # 57
	# firstTier2Government(governmentType: GovernmentType)  # 58
	# firstTier2GovernmentInWorld(governmentType: GovernmentType)  # 59
	# firstTier3Government(governmentType: GovernmentType)  # 60
	# firstTier3GovernmentInWorld(governmentType: GovernmentType)  # 61
	# firstTier4Government(governmentType: GovernmentType)  # 62
	# firstTier4GovernmentInWorld(governmentType: GovernmentType)  # 63
	# firstTradingPostsInAllCivilizations  # 64
	# firstUnitPromotedWithDistinction  # 65
	# firstWaterParkFullyDeveloped 66
	# freeCityJoins 67
	# generalDefeatsEnemy  # 68
	# goldenAgeBegins  # 69 #
	# governorFullyPromoted  # 70
	# greatPersonLuredByFaith 71
	# greatPersonLuredByGold 72
	# heroicAgeBegins  # 73
	# inquisitionBegins 74
	# leviedArmyStandsDown 75
	# metAllCivilizations  # 76
	# nationalParkFounded  # 77
	# normalAgeBegins  # 78 #
	# onTheWaves  # 79 #
	# religionAdoptsAllBeliefs  # 80
	# religionFounded(religion: ReligionType)  # 81
	# rivalHolyCityConverted  # 82 #
	# splendidCampusCompleted  # 83 #
	# splendidCommercialHubCompleted  # 84
	# splendidHarborCompleted  # 85
	# splendidHolySiteCompleted  # 86
	# splendidIndustrialZoneCompleted  # 87
	# splendidTheaterSquareCompleted  # 88
	# takingFlight  # 89
	# threateningCampDestroyed  # 90
	# tradingPostsInAllCivilizations  # 91
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
	# worldsFirstExoplanetExpeditionLaunched  # 103
	# worldsFirstFleet  # 104
	# worldsFirstFlight  # 105
	# worldsFirstGiganticCity(cityName: String)  # 106
	# worldsFirstInquisition 107
	# worldsFirstLandingOnTheMoon  # 108
	# worldsFirstLargeCity(cityName: String)  # 109
	# worldsFirstMartianColonyEstablished  # 110
	# worldsFirstNationalPark  # 111

	def test_moment_worldsFirstNeighborhood(self):  # 112
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.worldsFirstNeighborhood)
		playerTrajan.addMoment(MomentType.worldsFirstNeighborhood, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.worldsFirstNeighborhood))

	# worldsFirstPantheon  # 113
	# worldsFirstReligion  # 114
	# worldsFirstReligionToAdoptAllBeliefs  # 115
	# worldsFirstSatelliteInOrbit  # 116
	# worldsFirstSeafaring  # 117
	# worldsFirstSeasideResort  # 118
	# worldsFirstShipwreckExcavated  # 119
	# worldsFirstStrategicResourcePotentialUnleashed  # 120

	def test_moment_worldsFirstTechnologyOfNewEra(self):  # 121
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.worldsFirstTechnologyOfNewEra, eraType=EraType.classical)
		playerTrajan.addMoment(MomentType.worldsFirstTechnologyOfNewEra, eraType=EraType.classical, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.worldsFirstTechnologyOfNewEra, eraType=EraType.classical))
		self.assertFalse(playerTrajan.hasMoment(MomentType.worldsFirstTechnologyOfNewEra, eraType=EraType.future))

	# worldsFirstToMeetAllCivilizations  # 122

	def test_moment_worldsLargestCivilization(self):  # 123
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.worldsLargestCivilization)
		playerTrajan.addMoment(MomentType.worldsLargestCivilization, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.worldsLargestCivilization))

	def test_moment_worldCircumnavigated(self):  # 124
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.worldCircumnavigated)
		playerTrajan.addMoment(MomentType.worldCircumnavigated, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.worldCircumnavigated))

	def test_moment_snowCity(self):  # 229
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.snowCity, cityName='Berlin')
		playerTrajan.addMoment(MomentType.snowCity, cityName='Berlin', simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.snowCity, cityName='Berlin'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.snowCity, cityName='Potsdam'))

	# strategicResourcePotentialUnleashed  # 230 #
	# tradingPostEstablishedInNewCivilization(civilization: CivilizationType)  # 231
	# tribalVillageContacted  # 232

	def test_moment_tundraCity(self):  # 233
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.tundraCity, cityName='Berlin')
		playerTrajan.addMoment(MomentType.tundraCity, cityName='Berlin', simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.tundraCity, cityName='Berlin'))
		self.assertFalse(playerTrajan.hasMoment(MomentType.tundraCity, cityName='Potsdam'))

	# unitPromotedWithDistinction  # 234
	# wonderCompleted(wonder: WonderType)  # 235

	# hidden
	# shipSunk  # 300 for artifacts
	# battleFought  # 301
	def test_moment_dedicationTriggered(self):  # 302
		# GIVEN
		mapModel = MapMock(24, 20, TerrainType.grass)
		simulation = Game(mapModel, handicap=HandicapType.chieftain)

		# add UI
		simulation.userInterface = UserInterfaceMock()

		playerTrajan = Player(LeaderType.trajan, human=False)
		playerTrajan.initialize()

		# WHEN
		beforeMoment = playerTrajan.hasMoment(MomentType.dedicationTriggered, dedication=DedicationType.monumentality)
		playerTrajan.addMoment(MomentType.dedicationTriggered, dedication=DedicationType.monumentality, simulation=simulation)

		# THEN
		self.assertFalse(beforeMoment)
		self.assertTrue(playerTrajan.hasMoment(MomentType.dedicationTriggered, dedication=DedicationType.monumentality))
		self.assertFalse(playerTrajan.hasMoment(MomentType.dedicationTriggered, dedication=DedicationType.freeInquiry))
