from enum import Enum

from game.flavors import FlavorType, Flavor
from game.units import UnitType
from utils.base import ExtendedEnum, InvalidEnumError
from utils.theming import Color
from utils.translation import gettext_lazy as _


class TraitType(ExtendedEnum):
    BOLDNESS = 0


class Trait:
    def __init__(self, traitType: TraitType, value: int):
        self.traitType = traitType
        self.value = value


class CivilizationType(ExtendedEnum):
    BARBARIAN = -3
    FREE = -2
    CITY_STATE = -1

    GREEK = 0
    ROMAN = 1
    ENGLISH = 2

    def startingBias(self, tile, grid) -> int:
        # https://civilization.fandom.com/wiki/Starting_bias_(Civ5)
        if self == CivilizationType.GREEK:
            return 0  # no special bias
        elif self == CivilizationType.ROMAN:
            return 0  # no special bias
        elif self == CivilizationType.ENGLISH:
            return 2 if grid.isCoastalAt(tile.point) else 0

        return 0  # rest


class LeaderType(ExtendedEnum):
    BARBAR = -2
    CITY_STATE = -1
    NONE = 0

    ALEXANDER = 1
    TRAJAN = 2
    VICTORIA = 3

    def civilization(self) -> CivilizationType:
        if self == LeaderType.ALEXANDER:
            return CivilizationType.GREEK
        elif self == LeaderType.TRAJAN:
            return CivilizationType.ROMAN
        elif self == LeaderType.VICTORIA:
            return CivilizationType.ENGLISH

        raise Exception(f'Enum not handled: {self}')

    def flavor(self, flavorType: FlavorType) -> int:
        item = next((flavor for flavor in self._flavors() if flavor.flavorType == flavorType), None)

        if item is not None:
            return item.value

        return 0

    def _flavors(self) -> [Flavor]:
        if self == LeaderType.ALEXANDER:
            return [
                Flavor(FlavorType.CITY_DEFENSE, 5),
                Flavor(FlavorType.CULTURE, 7),
                Flavor(FlavorType.DEFENSE, 5),
                Flavor(FlavorType.DIPLOMACY, 9),
                Flavor(FlavorType.EXPANSION, 8),
                Flavor(FlavorType.GOLD, 3),
                Flavor(FlavorType.GROWTH, 4),
                Flavor(FlavorType.AMENITIES, 5),
                Flavor(FlavorType.INFRASTRUCTURE, 4),
                Flavor(FlavorType.MILITARY_TRAINING, 5),
                Flavor(FlavorType.MOBILE, 8),
                Flavor(FlavorType.NAVAL, 5),
                Flavor(FlavorType.NAVAL_GROWTH, 6),
                Flavor(FlavorType.NAVAL_RECON, 5),
                Flavor(FlavorType.NAVAL_TILE_IMPROVEMENT, 6),
                Flavor(FlavorType.OFFENSE, 8),
                Flavor(FlavorType.PRODUCTION, 5),
                Flavor(FlavorType.RECON, 5),
                Flavor(FlavorType.SCIENCE, 6),
                Flavor(FlavorType.TILE_IMPROVEMENT, 4),
                Flavor(FlavorType.WONDER, 6)
            ]
        elif self == LeaderType.TRAJAN:
            return [
                Flavor(FlavorType.CITY_DEFENSE, 5),
                Flavor(FlavorType.CULTURE, 5),
                Flavor(FlavorType.DEFENSE, 6),
                Flavor(FlavorType.DIPLOMACY, 5),
                Flavor(FlavorType.EXPANSION, 8),
                Flavor(FlavorType.GOLD, 6),
                Flavor(FlavorType.GROWTH, 5),
                Flavor(FlavorType.AMENITIES, 8),
                Flavor(FlavorType.INFRASTRUCTURE, 8),
                Flavor(FlavorType.MILITARY_TRAINING, 7),
                Flavor(FlavorType.MOBILE, 4),
                Flavor(FlavorType.NAVAL, 5),
                Flavor(FlavorType.NAVAL_GROWTH, 4),
                Flavor(FlavorType.NAVAL_RECON, 5),
                Flavor(FlavorType.NAVAL_TILE_IMPROVEMENT, 4),
                Flavor(FlavorType.OFFENSE, 5),
                Flavor(FlavorType.PRODUCTION, 6),
                Flavor(FlavorType.RECON, 3),
                Flavor(FlavorType.SCIENCE, 5),
                Flavor(FlavorType.TILE_IMPROVEMENT, 7),
                Flavor(FlavorType.WONDER, 6)
            ]
        elif self == LeaderType.VICTORIA:
            return [
                Flavor(FlavorType.CITY_DEFENSE, 6),
                Flavor(FlavorType.CULTURE, 6),
                Flavor(FlavorType.DEFENSE, 6),
                Flavor(FlavorType.DIPLOMACY, 6),
                Flavor(FlavorType.EXPANSION, 6),
                Flavor(FlavorType.GOLD, 8),
                Flavor(FlavorType.GROWTH, 4),
                Flavor(FlavorType.AMENITIES, 5),
                Flavor(FlavorType.INFRASTRUCTURE, 5),
                Flavor(FlavorType.MILITARY_TRAINING, 5),
                Flavor(FlavorType.MOBILE, 3),
                Flavor(FlavorType.NAVAL, 8),
                Flavor(FlavorType.NAVAL_GROWTH, 7),
                Flavor(FlavorType.NAVAL_RECON, 8),
                Flavor(FlavorType.NAVAL_TILE_IMPROVEMENT, 7),
                Flavor(FlavorType.OFFENSE, 3),
                Flavor(FlavorType.PRODUCTION, 6),
                Flavor(FlavorType.RECON, 6),
                Flavor(FlavorType.SCIENCE, 6),
                Flavor(FlavorType.TILE_IMPROVEMENT, 6),
                Flavor(FlavorType.WONDER, 5)
            ]
        elif self == LeaderType.CITY_STATE:
            return []
        elif self == LeaderType.BARBAR:
            return []

        raise InvalidEnumError(self)

    def traitValue(self, traitType: TraitType) -> int:
        item = next((trait for trait in self._traits() if trait.traitType == traitType), None)

        if item is not None:
            return item.value

        return 0

    def _traits(self) -> [Trait]:
        if self == LeaderType.ALEXANDER:
            return [Trait(TraitType.BOLDNESS, 8)]
        elif self == LeaderType.TRAJAN:
            return [Trait(TraitType.BOLDNESS, 6)]
        elif self == LeaderType.VICTORIA:
            return [Trait(TraitType.BOLDNESS, 4)]
        elif self == LeaderType.CITY_STATE:
            return []
        elif self == LeaderType.BARBAR:
            return []

        raise InvalidEnumError(self)


class LeaderWeightList(dict):
    def __init__(self):
        super().__init__()
        for leaderType in list(LeaderType):
            self[leaderType.name] = 0


class CityStateCategoryData:
    def __init__(self, name: str, color: Color, firstEnvoyBonus: str, thirdEnvoyBonus: str, sixthEnvoyBonus: str):
        self.name = name
        self.color = color
        self.firstEnvoyBonus = firstEnvoyBonus
        self.thirdEnvoyBonus = thirdEnvoyBonus
        self.sixthEnvoyBonus = sixthEnvoyBonus


class CityStateCategory(Enum):
    CULTURAL = 0
    INDUSTRIAL = 1
    MILITARISTIC = 2
    RELIGIOUS = 3
    SCIENTIFIC = 4
    TRADE = 5

    def _data(self):
        if self == CityStateCategory.CULTURAL:
            return CityStateCategoryData(
                name=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_NAME"),
                color=Color.MAGENTA,
                firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_FIRST_ENVOY_BONUS"),
                thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_THIRD_ENVOY_BONUS"),
                sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_SIXTH_ENVOY_BONUS")
            )
        elif self == CityStateCategory.INDUSTRIAL:
            return CityStateCategoryData()
        elif self == CityStateCategory.MILITARISTIC:
            return CityStateCategoryData()
        elif self == CityStateCategory.RELIGIOUS:
            return CityStateCategoryData()
        elif self == CityStateCategory.SCIENTIFIC:
            return CityStateCategoryData()
        elif self == CityStateCategory.TRADE:
            return CityStateCategoryData()
        else:
            raise InvalidEnumError(self)


class CityStateData:
    def __init__(self, name: str, category: CityStateCategory, suzerainBonus: str):
        self.name = name
        self.category = category
        self.suzerainBonus = suzerainBonus


class CityStateType(Enum):
    AKKAD = 0
    AMSTERDAM = 1
    ANSHAN = 2
    ANTANANARIVO = 3
    ANTIOCH = 4
    ARMAGH = 5
    AUCKLAND = 6
    AYUTTHAYA = 7
    BABYLON = 8
    BANDARBRUNEI = 9
    BOLOGNA = 10
    BRUSSELS = 11
    BUENOSAIRES = 12
    CAGUANA = 13
    CAHOKIA = 14
    CARDIFF = 15
    CARTHAGE = 16
    CHINGUETTI = 17
    FEZ = 18
    GENEVA = 19
    GRANADA = 20
    HATTUSA = 21
    HONGKONG = 22
    HUNZA = 23
    JAKARTA = 24
    JERUSALEM = 25
    JOHANNESBURG = 26
    KABUL = 27
    KANDY = 28
    KUMASI = 29
    LAVENTA = 30

    # // Lahore
    #     // Lisbon
    #     // Mexico City
    #     // Mitla
    #     // Mogadishu
    #     // Mohenjo-Daro
    #     // Muscat
    #     // Nalanda
    #     // Nan Madol
    #     // Nazca
    #     // Ngazargamu
    #     // Palenque
    #     // Preslav
    #     // Rapa Nui
    #     case samarkand
    #     case seoul
    #     case singapore
    #     case stockholm
    #     case taruga
    #     case toronto
    #     case valletta
    #     case vaticanCity
    #     case venice
    #     case vilnius
    #     case wolin
    #     case yerevan
    #     case zanzibar

    def name(self) -> str:
        return self._data().name

    def category(self) -> CityStateCategory:
        return self._data().category

    def _data(self) -> CityStateData:
        if self == CityStateType.AKKAD:
            return CityStateData(
                name=_("TXT_KEY_CITY_STATE_AKKAD_NAME"),
                category=CityStateCategory.MILITARISTIC,
                suzerainBonus=_("TXT_KEY_CITY_STATE_AKKAD_SUZERAIN")
            )
        else:
            raise InvalidEnumError(self)


class VictoryType(Enum):
    DOMINATION = 0
    CULTURAL = 1


class HandicapType(Enum):
    SETTLER = 0
    CHIEFTAIN = 1
    WARLORD = 2
    PRINCE = 3
    KING = 4
    EMPEROR = 5
    IMMORTAL = 6
    DEITY = 7

    def freeHumanStartingUnitTypes(self) -> [UnitType]:
        if self == HandicapType.SETTLER:
            return [UnitType.SETTLER, UnitType.WARRIOR, UnitType.WARRIOR, UnitType.BUILDER]
        elif self == HandicapType.CHIEFTAIN:
            return [UnitType.SETTLER, UnitType.WARRIOR, UnitType.BUILDER]
        elif self == HandicapType.WARLORD:
            return [UnitType.SETTLER, UnitType.WARRIOR, UnitType.BUILDER]
        elif self == HandicapType.PRINCE:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.KING:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.EMPEROR:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.IMMORTAL:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.DEITY:
            return [UnitType.SETTLER, UnitType.WARRIOR]

    def freeAIStartingUnitTypes(self) -> [UnitType]:
        if self == HandicapType.SETTLER:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.CHIEFTAIN:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.WARLORD:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.PRINCE:
            return [UnitType.SETTLER, UnitType.WARRIOR]
        elif self == HandicapType.KING:
            return [UnitType.SETTLER, UnitType.WARRIOR, UnitType.WARRIOR, UnitType.BUILDER]
        elif self == HandicapType.EMPEROR:
            return [UnitType.SETTLER, UnitType.SETTLER, UnitType.WARRIOR, UnitType.WARRIOR, UnitType.WARRIOR,
                    UnitType.BUILDER]
        elif self == HandicapType.IMMORTAL:
            return [UnitType.SETTLER, UnitType.SETTLER, UnitType.WARRIOR, UnitType.WARRIOR, UnitType.WARRIOR,
                    UnitType.WARRIOR, UnitType.BUILDER, UnitType.BUILDER]
        elif self == HandicapType.DEITY:
            return [UnitType.SETTLER, UnitType.SETTLER, UnitType.SETTLER, UnitType.WARRIOR, UnitType.WARRIOR,
                    UnitType.WARRIOR, UnitType.WARRIOR, UnitType.WARRIOR, UnitType.BUILDER, UnitType.BUILDER]
