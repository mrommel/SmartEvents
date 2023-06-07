from typing import Optional

from game.cityStates import CityStateType
from game.civilizations import LeaderType
from game.moments import MomentType
from map.base import HexPoint
from utils.base import ExtendedEnum, InvalidEnumError


class NotificationTypeData:
	def __init__(self, name: str, message: str):
		self.name = name
		self.message = message


class NotificationType(ExtendedEnum):
	turn = 'turn'  #0

	generic = 'generic'  #1

	techNeeded = 'techNeeded'  # 2
	civicNeeded = 'civicNeeded'  # 3
	productionNeeded = 'productionNeeded'  # (cityName: String, location: HexPoint)  # 4
	canChangeGovernment = 'canChangeGovernment'  # 5
	policiesNeeded = 'policiesNeeded'  # 6
	canFoundPantheon = 'canFoundPantheon'  # 7
	governorTitleAvailable = 'governorTitleAvailable'  # 8

	cityGrowth = 'cityGrowth'  # (cityName: String, population: Int, location: HexPoint)  # 9
	starving = 'starving'  # (cityName: String, location: HexPoint)  # 10

	diplomaticDeclaration = 'diplomaticDeclaration'  # (leader: LeaderType) # 11

	war = 'war'  # (leader: LeaderType)  # 12
	enemyInTerritory = 'enemyInTerritory'  # (location: HexPoint, cityName: String)  # 13

	unitPromotion = 'unitPromotion'  # (location: HexPoint)  # 14
	unitNeedsOrders = 'unitNeedsOrders'  # (location: HexPoint)  # 15
	unitDied = 'unitDied'  # (location: HexPoint)  # 16

	greatPersonJoined = 'greatPersonJoined'  # parameter: location # 17

	canRecruitGreatPerson = 'canRecruitGreatPerson'  # (greatPerson: GreatPerson)  # 18

	cityLost = 'cityLost'  # (location: HexPoint)  # 19
	goodyHutDiscovered = 'goodyHutDiscovered'  # (location: HexPoint)  # 20
	barbarianCampDiscovered = 'barbarianCampDiscovered'  # (location: HexPoint)  # 21

	waiting = 'waiting'  # 22

	metCityState = 'metCityState'  # (cityState: CityStateType, first: Bool)  # 23
	questCityStateFulfilled = 'questCityStateFulfilled'  # (cityState: CityStateType, quest: CityStateQuestType)  # 24
	questCityStateObsolete = 'questCityStateObsolete'  # (cityState: CityStateType, quest: CityStateQuestType)  # 25
	questCityStateGiven = 'questCityStateGiven'  # (cityState: CityStateType, quest: CityStateQuestType)  # 26

	momentAdded = 'momentAdded'  # (type: MomentType) 27
	tradeRouteCapacityIncreased = 'tradeRouteCapacityIncreased'  # 28

	naturalWonderDiscovered = 'naturalWonderDiscovered'  # (location: HexPoint) #29
	continentDiscovered = 'continentDiscovered'  # (location: HexPoint, continentName: String)  # 30
	wonderBuilt = 'wonderBuilt'  # (wonder: WonderType, civilization: CivilizationType) #31

	cityCanShoot = 'cityCanShoot'  # (cityName: String, location: HexPoint) #32
	cityAcquired = 'cityAcquired'  # (cityName: String, location: HexPoint) # 33

	envoyEarned = 'envoyEarned' # 34

	def name(self) -> str:
		return self._data().name

	def message(self) -> str:
		return self._data().message

	def _data(self) -> NotificationTypeData:
		if self == NotificationType.turn:  # 0
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_TURN_NAME',
				message='KEY_TXT_NOTIFICATION_TURN_MESSAGE'
			)

		elif self == NotificationType.generic:  # 1
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GENERIC_NAME',
				message='KEY_TXT_NOTIFICATION_GENERIC_MESSAGE'
			)

		elif self == NotificationType.techNeeded:  # 2
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_TECH_NEEDED_NAME',
				message='KEY_TXT_NOTIFICATION_TECH_NEEDED_MESSAGE'
			)
		elif self == NotificationType.civicNeeded:  # 3
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CIVIC_NEEDED__NAME',
				message='KEY_TXT_NOTIFICATION_CIVIC_NEEDED_MESSAGE'
			)
		elif self == NotificationType.productionNeeded:  # (cityName: String, location: HexPoint)  # 4
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_PRODUCTION_NEEDED_NAME',
				message='KEY_TXT_NOTIFICATION_PRODUCTION_NEEDED_MESSAGE'
			)
		elif self == NotificationType.canChangeGovernment:  # 5
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CAN_CHANGE_GOVERNMENT_NAME',
				message='KEY_TXT_NOTIFICATION_CAN_CHANGE_GOVERNMENT_MESSAGE'
			)
		elif self == NotificationType.policiesNeeded:  # 6
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_POLICIES_NEEDED_NAME',
				message='KEY_TXT_NOTIFICATION_POLICIES_NEEDED_MESSAGE'
			)
		elif self == NotificationType.canFoundPantheon:  # 7
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CAN_FOUND_PANTHEON_NAME',
				message='KEY_TXT_NOTIFICATION_CAN_FOUND_PANTHEON_MESSAGE'
			)
		elif self == NotificationType.governorTitleAvailable:  # 8
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GOVERNOR_TITLE_AVAILABLE_NAME',
				message='KEY_TXT_NOTIFICATION_GOVERNOR_TITLE_AVAILABLE_MESSAGE'
			)

		elif self == NotificationType.cityGrowth:  # (cityName: String, population: Int, location: HexPoint)  # 9
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_GROWTH_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_GROWTH_MESSAGE'
			)
		elif self == NotificationType.starving:  # (cityName: String, location: HexPoint)  # 10
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_STARVING_NAME',
				message='KEY_TXT_NOTIFICATION_STARVING_MESSAGE'
			)

		elif self == NotificationType.diplomaticDeclaration:  # (leader: LeaderType) # 11
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_DIPLOMATIC_DECLARATION_NAME',
				message='KEY_TXT_NOTIFICATION_DIPLOMATIC_DECLARATION_MESSAGE'
			)

		elif self == NotificationType.war:  # (leader: LeaderType)  # 12
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_WAR_NAME',
				message='KEY_TXT_NOTIFICATION_WAR_MESSAGE'
			)
		elif self == NotificationType.enemyInTerritory:  # (location: HexPoint, cityName: String)  # 13
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_ENEMY_IN_TERRITORY_NAME',
				message='KEY_TXT_NOTIFICATION_ENEMY_IN_TERRITORY_MESSAGE'
			)

		elif self == NotificationType.unitPromotion:  # (location: HexPoint)  # 14
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_UNIT_PROMOTION_NAME',
				message='KEY_TXT_NOTIFICATION_UNIT_PROMOTION_MESSAGE'
			)
		elif self == NotificationType.unitNeedsOrders:  # (location: HexPoint)  # 15
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_UNIT_NEEDS_ORDERS_NAME',
				message='KEY_TXT_NOTIFICATION_UNIT_NEEDS_ORDERS_MESSAGE'
			)
		elif self == NotificationType.unitDied:  # (location: HexPoint)  # 16
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_UNIT_DIED_NAME',
				message='KEY_TXT_NOTIFICATION_UNIT_DIED_MESSAGE'
			)

		elif self == NotificationType.greatPersonJoined:  # parameter: location # 17
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GREAT_PERSON_JOINED_NAME',
				message='KEY_TXT_NOTIFICATION_GREAT_PERSON_JOINED_MESSAGE'
			)

		elif self == NotificationType.canRecruitGreatPerson:  # (greatPerson: GreatPerson)  # 18
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CAN_RECRUIT_GREAT_PERSON_NAME',
				message='KEY_TXT_NOTIFICATION_CAN_RECRUIT_GREAT_PERSON_MESSAGE'
			)

		elif self == NotificationType.cityLost:  # (location: HexPoint)  # 19
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_LOST_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_LOST_MESSAGE'
			)
		elif self == NotificationType.goodyHutDiscovered:  # (location: HexPoint)  # 20
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_GOODY_HUT_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_GOODY_HUT_DISCOVERED_MESSAGE'
			)
		elif self == NotificationType.barbarianCampDiscovered:  # (location: HexPoint)  # 21
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_BARBARIAN_CAMP_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_BARBARIAN_CAMP_DISCOVERED_MESSAGE'
			)

		elif self == NotificationType.waiting:  # 22
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_WAITING_NAME',
				message='KEY_TXT_NOTIFICATION_WAITING_MESSAGE'
			)

		elif self == NotificationType.metCityState:  # (cityState: CityStateType, first: Bool)  # 23
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_MET_CITY_STATE_NAME',
				message='KEY_TXT_NOTIFICATION_MET_CITY_STATE_MESSAGE'
			)
		elif self == NotificationType.questCityStateFulfilled:  # (cityState: CityStateType, quest: CityStateQuestType)  # 24
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_FULFILLED_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_FULFILLED_MESSAGE'
			)
		elif self == NotificationType.questCityStateObsolete:  # (cityState: CityStateType, quest: CityStateQuestType)  # 25
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_OBSOLETE_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_OBSOLETE_MESSAGE'
			)
		elif self == NotificationType.questCityStateGiven:  # (cityState: CityStateType, quest: CityStateQuestType)  # 26
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_GIVEN_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_STATE_QUEST_GIVEN_MESSAGE'
			)

		elif self == NotificationType.momentAdded:  # (type: MomentType) 27
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_MOMENT_ADDED_NAME',
				message='KEY_TXT_NOTIFICATION_MOMENT_ADDED_MESSAGE'
			)
		elif self == NotificationType.tradeRouteCapacityIncreased:  # 28
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_TRADE_ROUTE_CAPACITY_INCREASED_NAME',
				message='KEY_TXT_NOTIFICATION_TRADE_ROUTE_CAPACITY_INCREASED_MESSAGE'
			)

		elif self == NotificationType.naturalWonderDiscovered:  # (location: HexPoint) #29
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_NATURAL_WONDER_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_NATURAL_WONDER_DISCOVERED_MESSAGE'
			)
		elif self == NotificationType.continentDiscovered:  # (location: HexPoint, continentName: String)  # 30
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CONTINENT_DISCOVERED_NAME',
				message='KEY_TXT_NOTIFICATION_CONTINENT_DISCOVERED_MESSAGE'
			)
		elif self == NotificationType.wonderBuilt:  # (wonder: WonderType, civilization: CivilizationType) #31
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_WONDER_BUILT_NAME',
				message='KEY_TXT_NOTIFICATION_WONDER_BUILT_MESSAGE'
			)

		elif self == NotificationType.cityCanShoot:  # (cityName: String, location: HexPoint) #32
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_CAN_SHOOT_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_CAN_SHOOT_MESSAGE'
			)
		elif self == NotificationType.cityAcquired:  # (cityName: String, location: HexPoint) #33
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_CITY_ACQUIRED_NAME',
				message='KEY_TXT_NOTIFICATION_CITY_ACQUIRED_MESSAGE'
			)

		elif self == NotificationType.envoyEarned:  # 34
			return NotificationTypeData(
				name='KEY_TXT_NOTIFICATION_ENVOY_EARNED_NAME',
				message='KEY_TXT_NOTIFICATION_ENVOY_EARNED_MESSAGE'
			)

		raise InvalidEnumError(self)


class Notification:
	def __init__(self, notificationType: NotificationType, city=None, player=None,
	             momentType: Optional[MomentType] = None, cityState: Optional[CityStateType] = None,
	             first: Optional[bool] = None, location: Optional[HexPoint] = None, cityName: Optional[str] = None,
	             leader: Optional[LeaderType] = None):
		self.notificationType = notificationType
		self.city = city
		self.player = player
		self.momentType = momentType
		self.cityState = cityState
		self.first = first
		self.location = location
		self.cityName = cityName
		self.leader = leader


class Notifications:
	def __init__(self, player):
		self.player = player
		self.notifications = []

	def add(self, notification: Notification):
		self.notifications.append(notification)

	def cleanUp(self, simulation):
		pass

	def addNotification(self, notificationType: NotificationType, momentType: Optional[MomentType] = None,
	                    cityState: Optional[CityStateType] = None, cityName: Optional[str] = None,
	                    first: Optional[bool] = None, location: Optional[HexPoint] = None,
	                    leader: Optional[LeaderType] = None):
		notification = Notification(
			notificationType=notificationType,
			momentType=momentType,
			cityState=cityState,
			first=first,
			cityName=cityName,
			location=location,
			leader=leader
		)
		self.notifications.append(notification)

	def update(self, simulation):
		pass
