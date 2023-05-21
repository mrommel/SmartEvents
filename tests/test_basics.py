import unittest

from game.flavors import Flavors, FlavorType, Flavor


class TestFlavors(unittest.TestCase):
	def test_initial_value(self):
		# GIVEN
		self.objectToTest = Flavors()

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 0)

	def test_add_value(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 5)

	def test_add_two_values(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)
		self.objectToTest += Flavor(FlavorType.culture, value=2)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 7)

	def test_add_values(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest += Flavor(FlavorType.culture, value=5)
		self.objectToTest.addFlavor(FlavorType.culture, value=3)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 8)

	def test_reset(self):
		# GIVEN
		self.objectToTest = Flavors()
		self.objectToTest.addFlavor(FlavorType.culture, value=3)
		self.objectToTest.reset()
		self.objectToTest.addFlavor(FlavorType.culture, value=2)

		# WHEN
		cultureValue = self.objectToTest.value(FlavorType.culture)

		# THEN
		self.assertEqual(cultureValue, 2)
