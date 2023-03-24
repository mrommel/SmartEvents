from enum import Enum


class NotificationType(Enum):
	POLICY_NEEDED = 3
	CIVIC_NEEDED = 2
	TECH_NEEDED = 1
	PRODUCTION_NEEDED = 0


class Notification:
	def __init__(self, notificationType: NotificationType, city=None, player=None):
		self.notificationType = notificationType
		self.city = city
		self.player = player


class Notifications:
	def __init__(self, player):
		self.player = player
		self.notifications = []

	def add(self, notification: Notification):
		self.notifications.append(notification)

	def cleanUp(self, simulation):
		pass
