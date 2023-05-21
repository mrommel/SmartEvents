from enum import Enum

from game.units import UnitType
from utils.base import InvalidEnumError
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
    cultural = 'cultural'
    industrial = 'industrial'
    militaristic = 'militaristic'
    religious = 'religious'
    scientific = 'scientific'
    trade = 'trade'

    def _data(self):
        if self == CityStateCategory.cultural:
            return CityStateCategoryData(
                name=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_NAME"),
                color=Color.MAGENTA,
                firstEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_FIRST_ENVOY_BONUS"),
                thirdEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_THIRD_ENVOY_BONUS"),
                sixthEnvoyBonus=_("TXT_KEY_CITY_STATE_CATEGORY_CULTURAL_SIXTH_ENVOY_BONUS")
            )
        elif self == CityStateCategory.industrial:
            return CityStateCategoryData()
        elif self == CityStateCategory.militaristic:
            return CityStateCategoryData()
        elif self == CityStateCategory.religious:
            return CityStateCategoryData()
        elif self == CityStateCategory.scientific:
            return CityStateCategoryData()
        elif self == CityStateCategory.trade:
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
                category=CityStateCategory.militaristic,
                suzerainBonus=_("TXT_KEY_CITY_STATE_AKKAD_SUZERAIN")
            )
        else:
            raise InvalidEnumError(self)


class HandicapType(Enum):
    settler = 0
    chieftain = 1
    warlord = 2
    prince = 3
    king = 4
    emperor = 5
    immortal = 6
    deity = 7

    def freeHumanStartingUnitTypes(self) -> [UnitType]:
        if self == HandicapType.settler:
            return [UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.chieftain:
            return [UnitType.settler, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.warlord:
            return [UnitType.settler, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.prince:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.king:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.emperor:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.immortal:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.deity:
            return [UnitType.settler, UnitType.warrior]

    def freeAIStartingUnitTypes(self) -> [UnitType]:
        if self == HandicapType.settler:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.chieftain:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.warlord:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.prince:
            return [UnitType.settler, UnitType.warrior]
        elif self == HandicapType.king:
            return [UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.builder]
        elif self == HandicapType.emperor:
            return [UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.warrior,
                    UnitType.builder]
        elif self == HandicapType.immortal:
            return [UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior, UnitType.warrior,
                    UnitType.warrior, UnitType.builder, UnitType.builder]
        elif self == HandicapType.deity:
            return [UnitType.settler, UnitType.settler, UnitType.settler, UnitType.warrior, UnitType.warrior,
                    UnitType.warrior, UnitType.warrior, UnitType.warrior, UnitType.builder, UnitType.builder]

    def firstImpressionBaseValue(self):
        # // -3 - +3
        # Deity -2 to -8
        # Immortal -1 to -7
        # Emperor 0 a -6
        # King1 to -5
        # Prince 2 to -4
        # https://forums.civfanatics.com/threads/first-impression-of-you.613161/ */
        if self == HandicapType.settler:
            return 2
        elif self == HandicapType.chieftain:
            return 1
        elif self == HandicapType.warlord:
            return 0
        elif self == HandicapType.prince:
            return -1
        elif self == HandicapType.king:
            return -2
        elif self == HandicapType.emperor:
            return -3
        elif self == HandicapType.immortal:
            return -4
        elif self == HandicapType.deity:
            return -5

        raise InvalidEnumError(self)


class GameState(Enum):
    on = 'on'
    over = 'over'
    extended = 'extended'
