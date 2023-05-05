from game.flavors import FlavorType, Flavor
from utils.base import ExtendedEnum, InvalidEnumError


class TraitType(ExtendedEnum):
    boldness = 0


class Trait:
    def __init__(self, traitType: TraitType, value: int):
        self.traitType = traitType
        self.value = value


class CivilizationType(ExtendedEnum):
    barbarian = -3
    free = -2
    cityState = -1

    greek = 0
    roman = 1
    english = 2

    def startingBias(self, tile, grid) -> int:
        # https://civilization.fandom.com/wiki/Starting_bias_(Civ5)
        if self == CivilizationType.greek:
            return 0  # no special bias
        elif self == CivilizationType.roman:
            return 0  # no special bias
        elif self == CivilizationType.english:
            return 2 if grid.isCoastalAt(tile.point) else 0

        return 0  # rest


class LeaderType(ExtendedEnum):
    barbar = -2
    cityState = -1
    none = 0

    alexander = 1
    trajan = 2
    victoria = 3

    def civilization(self) -> CivilizationType:
        if self == LeaderType.alexander:
            return CivilizationType.greek
        elif self == LeaderType.trajan:
            return CivilizationType.roman
        elif self == LeaderType.victoria:
            return CivilizationType.english

        raise Exception(f'Enum not handled: {self}')

    def flavor(self, flavorType: FlavorType) -> int:
        item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

        if item is not None:
            return item.value

        return 0

    def _flavors(self) -> [Flavor]:
        if self == LeaderType.alexander:
            return [
                Flavor(FlavorType.cityDefense, 5),
                Flavor(FlavorType.culture, 7),
                Flavor(FlavorType.defense, 5),
                Flavor(FlavorType.diplomacy, 9),
                Flavor(FlavorType.expansion, 8),
                Flavor(FlavorType.gold, 3),
                Flavor(FlavorType.growth, 4),
                Flavor(FlavorType.amenities, 5),
                Flavor(FlavorType.infrastructure, 4),
                Flavor(FlavorType.militaryTraining, 5),
                Flavor(FlavorType.mobile, 8),
                Flavor(FlavorType.naval, 5),
                Flavor(FlavorType.navalGrowth, 6),
                Flavor(FlavorType.navalRecon, 5),
                Flavor(FlavorType.navalTileImprovement, 6),
                Flavor(FlavorType.offense, 8),
                Flavor(FlavorType.production, 5),
                Flavor(FlavorType.recon, 5),
                Flavor(FlavorType.science, 6),
                Flavor(FlavorType.tileImprovement, 4),
                Flavor(FlavorType.wonder, 6)
            ]
        elif self == LeaderType.trajan:
            return [
                Flavor(FlavorType.cityDefense, 5),
                Flavor(FlavorType.culture, 5),
                Flavor(FlavorType.defense, 6),
                Flavor(FlavorType.diplomacy, 5),
                Flavor(FlavorType.expansion, 8),
                Flavor(FlavorType.gold, 6),
                Flavor(FlavorType.growth, 5),
                Flavor(FlavorType.amenities, 8),
                Flavor(FlavorType.infrastructure, 8),
                Flavor(FlavorType.militaryTraining, 7),
                Flavor(FlavorType.mobile, 4),
                Flavor(FlavorType.naval, 5),
                Flavor(FlavorType.navalGrowth, 4),
                Flavor(FlavorType.navalRecon, 5),
                Flavor(FlavorType.navalTileImprovement, 4),
                Flavor(FlavorType.offense, 5),
                Flavor(FlavorType.production, 6),
                Flavor(FlavorType.recon, 3),
                Flavor(FlavorType.science, 5),
                Flavor(FlavorType.tileImprovement, 7),
                Flavor(FlavorType.wonder, 6)
            ]
        elif self == LeaderType.victoria:
            return [
                Flavor(FlavorType.cityDefense, 6),
                Flavor(FlavorType.culture, 6),
                Flavor(FlavorType.defense, 6),
                Flavor(FlavorType.diplomacy, 6),
                Flavor(FlavorType.expansion, 6),
                Flavor(FlavorType.gold, 8),
                Flavor(FlavorType.growth, 4),
                Flavor(FlavorType.amenities, 5),
                Flavor(FlavorType.infrastructure, 5),
                Flavor(FlavorType.militaryTraining, 5),
                Flavor(FlavorType.mobile, 3),
                Flavor(FlavorType.naval, 8),
                Flavor(FlavorType.navalGrowth, 7),
                Flavor(FlavorType.navalRecon, 8),
                Flavor(FlavorType.navalTileImprovement, 7),
                Flavor(FlavorType.offense, 3),
                Flavor(FlavorType.production, 6),
                Flavor(FlavorType.recon, 6),
                Flavor(FlavorType.science, 6),
                Flavor(FlavorType.tileImprovement, 6),
                Flavor(FlavorType.wonder, 5)
            ]
        elif self == LeaderType.cityState:
            return []
        elif self == LeaderType.barbar:
            return []

        raise InvalidEnumError(self)

    def traitValue(self, traitType: TraitType) -> int:
        item = next((trait for trait in self._traits() if trait.traitType == traitType), None)

        if item is not None:
            return item.value

        return 0

    def _traits(self) -> [Trait]:
        if self == LeaderType.alexander:
            return [Trait(TraitType.boldness, 8)]
        elif self == LeaderType.trajan:
            return [Trait(TraitType.boldness, 6)]
        elif self == LeaderType.victoria:
            return [Trait(TraitType.boldness, 4)]
        elif self == LeaderType.cityState:
            return []
        elif self == LeaderType.barbar:
            return []

        raise InvalidEnumError(self)


class LeaderWeightList(dict):
    def __init__(self):
        super().__init__()
        for leaderType in list(LeaderType):
            self[leaderType.name] = 0