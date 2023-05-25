from typing import Optional

from game.cities import CityStateType
from game.moments import MomentType
from map.base import HexPoint
from utils.base import ExtendedEnum


class NotificationType(ExtendedEnum):
	momentAdded = 'momentAdded'
	policyNeeded = 'policyNeeded'
	civicNeeded = 'civicNeeded'
	techNeeded = 'techNeeded'
	productionNeeded = 'productionNeeded'
	metCityState = 'metCityState'
	goodyHutDiscovered = 'goodyHutDiscovered'
	naturalWonderDiscovered = 'naturalWonderDiscovered'


class Notification:
	def __init__(self, notificationType: NotificationType, city=None, player=None,
	             momentType: Optional[MomentType] = None, cityState: Optional[CityStateType] = None,
	             first: Optional[bool] = None, location: Optional[HexPoint] = None):
		self.notificationType = notificationType
		self.city = city
		self.player = player
		self.momentType = momentType
		self.cityState = cityState
		self.first = first
		self.location = location


class Notifications:
	def __init__(self, player):
		self.player = player
		self.notifications = []

	def add(self, notification: Notification):
		self.notifications.append(notification)

	def cleanUp(self, simulation):
		pass

	def addNotification(self, notificationType: NotificationType, momentType: Optional[MomentType] = None,
	                    cityState: Optional[CityStateType] = None, first: Optional[bool] = None):
		notification = Notification(
			notificationType=notificationType,
			momentType=momentType,
			cityState=cityState,
			first=first
		)
		self.notifications.append(notification)

	def update(self, simulation):
		pass
