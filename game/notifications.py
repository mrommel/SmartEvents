from typing import Optional

from game.moments import MomentType
from utils.base import ExtendedEnum


class NotificationType(ExtendedEnum):
	momentAdded = 'momentAdded'
	policyNeeded = 'policyNeeded'
	civicNeeded = 'civicNeeded'
	techNeeded = 'techNeeded'
	productionNeeded = 'productionNeeded'


class Notification:
	def __init__(self, notificationType: NotificationType, city=None, player=None, momentType: Optional[MomentType] = None):
		self.notificationType = notificationType
		self.city = city
		self.player = player
		self.momentType = momentType


class Notifications:
	def __init__(self, player):
		self.player = player
		self.notifications = []

	def add(self, notification: Notification):
		self.notifications.append(notification)

	def cleanUp(self, simulation):
		pass

	def addNotification(self, notificationType: NotificationType, momentType: Optional[MomentType] = None):
		notification = Notification(notificationType=notificationType, momentType=momentType)
		self.notifications.append(notification)
