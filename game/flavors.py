from utils.base import ExtendedEnum


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


class Flavor:
    def __init__(self, flavorType: FlavorType, value: int):
        self.flavorType = flavorType
        self.value = value


class Flavors:
    def __init__(self):
        self._items = []

    def isEmpty(self):
        return len(self._items) == 0

    def set(self, flavorType: FlavorType, value: int):
        item = next((flavor for flavor in self._items if flavor.flavorType == flavorType), None)

        if item is not None:
            item.value = value
        else:
            self._items.append(Flavor(flavorType, value))

    def value(self, flavorType: FlavorType):
        item = next((flavor for flavor in self._items if flavor.flavorType == flavorType), None)

        if item is not None:
            return item.value

        return 0
