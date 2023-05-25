from typing import Optional

from game.states.builds import BuildType
from game.unitTypes import UnitMissionType, MoveOptions, UnitActivityType
from map.base import HexPoint
from map.path_finding.base import HexPath


class UnitMission:
	def __init__(self, missionType: UnitMissionType, buildType: Optional[BuildType] = None,
				 target: Optional[HexPoint] = None, path: Optional[HexPath] = None,
				 options: Optional[MoveOptions] = None):
		self.missionType = missionType
		self.buildType = buildType
		self.target = target
		self.path = path
		self.options = options
		self.unit = None

		self.startedInTurn: int = -1

		if missionType.needsTarget() and (target is None and path is None):
			raise Exception("need target")

	def start(self, simulation):
		"""Initiate a mission"""
		self.startedInTurn = simulation.currentTurn

		delete = False
		notify = False
		action = False

		if self.unit.canMove():
			self.unit.setActivityType(UnitActivityType.mission, simulation)
		else:
			self.unit.setActivityType(UnitActivityType.hold, simulation)

		if not self.unit.canStartMission(self, simulation):
			delete = True
		else:
			if self.missionType == UnitMissionType.skip:
				self.unit.setActivityType(UnitActivityType.hold, simulation)
				delete = True
			elif self.missionType == UnitMissionType.sleep:
				self.unit.setActivityType(UnitActivityType.sleep, simulation)
				delete = True
				notify = True
			elif self.missionType == UnitMissionType.fortify:
				self.unit.setActivityType(UnitActivityType.sleep, simulation)
				delete = True
				notify = True
			elif self.missionType == UnitMissionType.heal:
				self.unit.setActivityType(UnitActivityType.heal, simulation)
				delete = True
				notify = True

			if self.unit.canMove():

				if self.missionType == UnitMissionType.fortify or self.missionType == UnitMissionType.heal or \
					self.missionType == UnitMissionType.alert or self.missionType == UnitMissionType.skip:

					self.unit.setFortifiedThisTurnTo(True, simulation)

					# start the animation right now to give feedback to the player
					if not self.unit.isFortified() and not self.unit.hasMoved(simulation) and \
						self.unit.canFortifyAt(self.unit.location, simulation):
						simulation.userInterface.refreshUnit(self.unit)
				elif self.unit.isFortified():
					# unfortify for any other mission
					simulation.userInterface.refreshUnit(self.unit)

				# ---------- now the real missions with action -----------------------

				if self.missionType == UnitMissionType.embark or self.missionType == UnitMissionType.disembark:
					action = True

				# FIXME nuke, paradrop, airlift
				elif self.missionType == UnitMissionType.rebase:
					if self.unit.doRebaseTo(self.target):
						action = True
				elif self.missionType == UnitMissionType.rangedAttack:
					if not self.unit.canRangeStrikeAt(self.target, needWar=False, noncombatAllowed=False, simulation=simulation):
						# Invalid, delete the mission
						delete = True
				elif self.missionType == UnitMissionType.pillage:
					if self.unit.doPillage(simulation):
						action = True
				elif self.missionType == UnitMissionType.found:
					if self.unit.doFoundWith(None, simulation):
						action = True

		if action and self.unit.player.isHuman():
			timer = self.calculateMissionTimerFor(self.unit)
			self.unit.setMissionTimerTo(timer)

		if delete:
			self.unit.popMission()
		elif self.unit.activityType() == UnitActivityType.mission:
			self.continueMissionSteps(0, simulation)

		return

	def calculateMissionTimerFor(self, unit, steps: int = 0) -> int:
		"""
			---------------------------------------------------------------------------
			Update the mission timer to a new value based on the mission (or lack thereof) in the queue
			KWG: The mission timer controls when the next time the unit's mission will be checked, not
				in absolute time, but in passes through the Game Core update loop.  Previously,
				this was used to delay processing so that the user could see the visualization of
				units.  The Game Core no longer deals with visualization timing, but this system is
				still used to keep the units sequencing their missions with each other.
				i.e. each unit will get a chance to complete a mission segment, rather than a unit
				exhausting its mission queue all in one go.
		"""
		peekMission = unit.peekMission()

		if not unit.player.isHuman():
			time = 0
		elif peekMission is not None:
			time = 1

			if peekMission.missionType == UnitMissionType.moveTo:  # or peekMission.type ==.routeTo or peekMission.type ==.moveToUnit

				# targetPlot: Optional[HexPoint] = None
				# / * if peekMission.type ==.moveToUnit
				# {
				# 	pTargetUnit = GET_PLAYER((PlayerTypes)
				# kMissionData.iData1).getUnit(kMissionData.iData2);
				# if (pTargetUnit) {
				# pTargetPlot = pTargetUnit->plot();
				# } else {
				# pTargetPlot = NULL;
				# }
				# } else {* /
				targetPlot = peekMission.target

				if targetPlot is not None and unit.location == targetPlot:
					time += steps
				else:
					time = min(time, 2)

			if unit.player.isHuman() and unit.isAutomated():
				time = min(time, 1)
		else:
			time = 0

		return time