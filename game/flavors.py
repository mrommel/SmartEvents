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
    recon = 'recon'


class Flavor:
    def __init__(self, flavorType: FlavorType, value: int):
        self.flavorType = flavorType
        self.value = value


class Flavors:
    def __init__(self):
        self._items = []

    def isEmpty(self):
        return len(self._items) == 0

    def reset(self):
        self._items = []

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

    def __iadd__(self, other):
        if isinstance(other, Flavors):
            for flavorType in list(FlavorType):
                self.set(flavorType, self.value(flavorType) + other.value(flavorType))

            return self
        elif isinstance(other, Flavor):
            item = next((flavor for flavor in self._items if flavor.flavorType == other.flavorType), None)

            if item is not None:
                item.value += other.value

            return self
        else:
            raise Exception(f'type is not accepted {type(other)}')
