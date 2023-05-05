from enum import Enum

from game.flavors import FlavorType, Flavor
from game.units import UnitType
from utils.base import ExtendedEnum, InvalidEnumError
from utils.theming import Color
from utils.translation import gettext_lazy as _


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
            return [UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.CHIEFTAIN:
            return [UnitType.settler, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.WARLORD:
            return [UnitType.settler, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.PRINCE:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.KING:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.EMPEROR:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.IMMORTAL:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.DEITY:
            return [UnitType.settler, UnitType.warrior]

    def freeAIStartingUnitTypes(self) -> [UnitType]:
        if self == HandicapType.SETTLER:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.CHIEFTAIN:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.WARLORD:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.PRINCE:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.KING:
            return [UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.EMPEROR:
            return [UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.warrior,
                    UnitType.builder]
        elif self == HandicapType.IMMORTAL:
            return [UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.warrior,
                    UnitType.warrior, UnitType.builder, UnitType.builder]
        elif self == HandicapType.DEITY:
            return [UnitType.settler, UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior,
                    UnitType.warrior, UnitType.warrior, UnitType.warrior, UnitType.builder, UnitType.builder]
