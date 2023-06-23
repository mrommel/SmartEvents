import random

from core.base import ExtendedEnum


class FlavorType(ExtendedEnum):
    # default
    none = 'none'

    production = 'production'
    tileImprovement = 'tileImprovement'
    mobile = 'mobile'
    growth = 'growth'
    naval = 'naval'
    navalTileImprovement = 'navalTileImprovement'
    wonder = 'wonder'
    navalRecon = 'navalRecon'
    amenities = 'amenities'
    science = 'science'
    culture = 'culture'
    diplomacy = 'diplomacy'
    cityDefense = 'cityDefense'
    ranged = 'ranged'
    offense = 'offense'
    defense = 'defense'
    militaryTraining = 'militaryTraining'
    infrastructure = 'infrastructure'
    gold = 'gold'
    navalGrowth = 'navalGrowth'
    energy = 'energy'
    expansion = 'expansion'
    greatPeople = 'greatPeople'
    religion = 'religion'
    tourism = 'tourism'
    recon = 'recon'
    air = 'air'


class Flavor:
    def __init__(self, flavorType: FlavorType, value: int):
        self.flavorType = flavorType
        self.value = value

        if isinstance(value, FlavorType):
            raise Exception('wrong type')

    def __str__(self) -> str:
        return f'Flavor({self.flavorType}, {self.value})'

    def __repr__(self) -> str:
        return f'Flavor({self.flavorType}, {self.value})'


class Flavors:
    def __init__(self):
        self._items = []

    def isEmpty(self):
        return len(self._items) == 0

    def reset(self):
        self._items = []

    def set(self, flavorType: FlavorType, value: int):
        item = next(filter(lambda flavor: flavor.flavorType == flavorType, self._items), None)

        if item is not None:
            item.value = value
        else:
            self._items.append(Flavor(flavorType, value))

    def value(self, flavorType: FlavorType):
        item = next(filter(lambda flavor: flavor.flavorType == flavorType, self._items), None)
        # (flavor for flavor in  if flavor.flavorType == flavorType)

        if item is not None:
            return item.value

        return 0

    def __iadd__(self, other):
        if isinstance(other, Flavors):
            for flavorType in list(FlavorType):
                self.set(flavorType, self.value(flavorType) + other.value(flavorType))

            return self
        elif isinstance(other, Flavor):
            item = next((flavor for flavor in self._items if flavor.flavorType == other.flavorType), None)

            if item is not None:
                item.value += other.value
            else:
                self._items.append(other)

            return self
        else:
            raise Exception(f'type is not accepted {type(other)}')

    def addFlavor(self, flavorType: FlavorType, value: int):
        item = next((flavor for flavor in self._items if flavor.flavorType == flavorType), None)

        if item is not None:
            item.value += value
        else:
            self._items.append(Flavor(flavorType, value))

    @classmethod
    def adjustedValue(cls, originalValue: int, plusMinus: int, minimum: int, maximum: int):
        """Add a random plus/minus to an integer (but keep it in range)"""
        adjust = random.randint(0, plusMinus * 2 + 1)
        rtnValue = originalValue + adjust - plusMinus

        if rtnValue < minimum:
            rtnValue = minimum
        elif rtnValue > maximum:
            rtnValue = maximum

        return rtnValue
