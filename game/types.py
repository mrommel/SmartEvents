from utils.base import ExtendedEnum
from gettext import gettext as _


class EraType(ExtendedEnum):
    # default
    ANCIENT = 'ancient'
    CLASSICAL = 'classical'

    INDUSTRIAL = 'industrial'
    MODERN = 'modern'

    def name(self) -> str:
        if self == EraType.ANCIENT:
            return _('TXT_KEY_ERA_ANCIENT')
        elif self == EraType.CLASSICAL:
            return _('TXT_KEY_ERA_CLASSICAL')

        elif self == EraType.INDUSTRIAL:
            return _('TXT_KEY_ERA_INDUSTRIAL')
        elif self == EraType.MODERN:
            return _('TXT_KEY_ERA_MODERN')

        raise AttributeError(f'cant get name of {self}')


class TechTypeData:
    def __init__(self, name, eureka_summary, eureka_description, era, cost, required):
        self.name = name
        self.eureka_summary = eureka_summary
        self.eureka_description = eureka_description
        self.era = era
        self.cost = cost
        self.required = required


class TechType:
    pass


class TechType(ExtendedEnum):
    # default
    none = 'none'

    # ancient
    mining = 'mining'
    pottery = 'pottery'
    animalHusbandry = 'animalHusbandry'
    sailing = 'sailing'
    astrology = 'astrology'
    irrigation = 'irrigation'
    writing = 'writing'
    masonry = 'masonry'
    archery = 'archery'
    bronzeWorking = 'bronzeWorking'
    wheel = 'wheel'

    # classical
    celestialNavigation = 'celestialNavigation'
    horsebackRiding = 'horsebackRiding'
    currency = 'currency'
    construction = 'construction'
    ironWorking = 'ironWorking'
    shipBuilding = 'shipBuilding'
    mathematics = 'mathematics'
    engineering = 'engineering'

    # medieval

    # renaissance

    # industrial
    industrialization = 'industrialization'

    # modern
    refining = 'refining'

    def name(self) -> str:
        return self._data().name

    def required(self) -> []:
        return self._data().required

    def cost(self) -> int:
        return self._data().cost

    def _data(self):
        if self == TechType.none:
            return TechTypeData(
                _('TXT_KEY_TECH_NONE'),
                '',
                '',
                EraType.ANCIENT,
                0,
                []
            )

        # ANCIENT
        if self == TechType.mining:
            return TechTypeData(
                _('TXT_KEY_TECH_MINING_NAME'),
                _('TXT_KEY_TECH_MINING_EUREKA'),
                _('TXT_KEY_TECH_MINING_EUREKA_TEXT'),
                EraType.ANCIENT,
                25,
                []
            )
        elif self == TechType.pottery:
            return TechTypeData(
                _('TXT_KEY_TECH_POTTERY_NAME'),
                _('TXT_KEY_TECH_POTTERY_EUREKA'),
                _('TXT_KEY_TECH_POTTERY_EUREKA_TEXT'),
                EraType.ANCIENT,
                25,
                []
            )
        elif self == TechType.animalHusbandry:
            return TechTypeData(
                _('TXT_KEY_TECH_ANIMAL_HUSBANDRY_NAME'),
                _('TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA'),
                _('TXT_KEY_TECH_ANIMAL_HUSBANDRY_EUREKA_TEXT'),
                EraType.ANCIENT,
                25,
                []
            )
        elif self == TechType.sailing:
            return TechTypeData(
                _('TXT_KEY_TECH_SAILING_NAME'),
                _('TXT_KEY_TECH_SAILING_EUREKA'),
                _('TXT_KEY_TECH_SAILING_EUREKA_TEXT'),
                EraType.ANCIENT,
                50,
                []
            )
        elif self == TechType.astrology:
            return TechTypeData(
                _('TXT_KEY_TECH_ASTROLOGY_NAME'),
                _('TXT_KEY_TECH_ASTROLOGY_EUREKA'),
                _('TXT_KEY_TECH_ASTROLOGY_EUREKA_TEXT'),
                EraType.ANCIENT,
                50,
                []
            )
        elif self == TechType.irrigation:
            return TechTypeData(
                _('TXT_KEY_TECH_IRRIGATION_NAME'),
                _('TXT_KEY_TECH_IRRIGATION_EUREKA'),
                _('TXT_KEY_TECH_IRRIGATION_EUREKA_TEXT'),
                EraType.ANCIENT,
                50,
                [TechType.pottery]
            )
        elif self == TechType.writing:
            return TechTypeData(
                _('TXT_KEY_TECH_WRITING_NAME'),
                _('TXT_KEY_TECH_WRITING_EUREKA'),
                _('TXT_KEY_TECH_WRITING_EUREKA_TEXT'),
                EraType.ANCIENT,
                50,
                [TechType.pottery]
            )
        elif self == TechType.masonry:
            return TechTypeData(
                _('TXT_KEY_TECH_MASONRY_NAME'),
                _('TXT_KEY_TECH_MASONRY_EUREKA'),
                _('TXT_KEY_TECH_MASONRY_EUREKA_TEXT'),
                EraType.ANCIENT,
                80,
                [TechType.mining]
            )
        elif self == TechType.archery:
            return TechTypeData(
                _('TXT_KEY_TECH_ARCHERY_NAME'),
                _('TXT_KEY_TECH_ARCHERY_EUREKA'),
                _('TXT_KEY_TECH_ARCHERY_EUREKA_TEXT'),
                EraType.ANCIENT,
                50,
                [TechType.animalHusbandry]
            )
        elif self == TechType.bronzeWorking:
            return TechTypeData(
                _('TXT_KEY_TECH_BRONZE_WORKING_NAME'),
                _('TXT_KEY_TECH_BRONZE_WORKING_EUREKA'),
                _('TXT_KEY_TECH_BRONZE_WORKING_EUREKA_TEXT'),
                EraType.ANCIENT,
                80,
                [TechType.mining]
            )
        elif self == TechType.wheel:
            return TechTypeData(
                _('TXT_KEY_TECH_WHEEL_NAME'),
                _('TXT_KEY_TECH_WHEEL_EUREKA'),
                _('TXT_KEY_TECH_WHEEL_EUREKA_TEXT'),
                EraType.ANCIENT,
                80,
                [TechType.mining]
            )

        # classical
        elif self == TechType.celestialNavigation:
            return TechTypeData(
                _('TXT_KEY_TECH_CELESTIAL_NAVIGATION_NAME'),
                _('TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA'),
                _('TXT_KEY_TECH_CELESTIAL_NAVIGATION_EUREKA_TEXT'),
                EraType.classical,
                120,
                [TechType.sailing, TechType.astrology]
            )
        elif self == TechType.horsebackRiding:
            return TechTypeData(
                _('TXT_KEY_TECH_HORSEBACK_RIDING_NAME'),
                _('TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA'),
                _('TXT_KEY_TECH_HORSEBACK_RIDING_EUREKA_TEXT'),
                EraType.CLASSICAL,
                120,
                [TechType.animalHusbandry]
            )
        elif self == TechType.currency:
            return TechTypeData(
                _('TXT_KEY_TECH_CURRENCY_NAME'),
                _('TXT_KEY_TECH_CURRENCY_EUREKA'),
                _('TXT_KEY_TECH_CURRENCY_EUREKA_TEXT'),
                EraType.CLASSICAL,
                120,
                [TechType.writing]
            )
        elif self == TechType.construction:
            return TechTypeData(
                _('TXT_KEY_TECH_CONSTRUCTION_NAME'),
                _('TXT_KEY_TECH_CONSTRUCTION_EUREKA'),
                _('TXT_KEY_TECH_CONSTRUCTION_EUREKA_TEXT'),
                EraType.CLASSICAL,
                200,
                [TechType.masonry, TechType.horsebackRiding]
            )
        elif self == TechType.ironWorking:
            return TechTypeData(
                _('TXT_KEY_TECH_IRON_WORKING_NAME'),
                _('TXT_KEY_TECH_IRON_WORKING_EUREKA'),
                _('TXT_KEY_TECH_IRON_WORKING_EUREKA_TEXT'),
                EraType.CLASSICAL,
                120,
                [TechType.bronzeWorking]
            )
        elif self == TechType.shipBuilding:
            return TechTypeData(
                _('TXT_KEY_TECH_SHIP_BUILDING_NAME'),
                _('TXT_KEY_TECH_SHIP_BUILDING_EUREKA'),
                _('TXT_KEY_TECH_SHIP_BUILDING_EUREKA_TEXT'),
                EraType.CLASSICAL,
                200,
                [TechType.sailing]
            )
        elif self == TechType.mathematics:
            return TechTypeData(
                _('TXT_KEY_TECH_MATHEMATICS_NAME'),
                _('TXT_KEY_TECH_MATHEMATICS_EUREKA'),
                _('TXT_KEY_TECH_MATHEMATICS_EUREKA_TEXT'),
                EraType.CLASSICAL,
                200,
                [TechType.currency]
            )
        elif self == TechType.engineering:
            return TechTypeData(
                _('TXT_KEY_TECH_ENGINEERING_NAME'),
                _('TXT_KEY_TECH_ENGINEERING_EUREKA'),
                _('TXT_KEY_TECH_ENGINEERING_EUREKA_TEXT'),
                EraType.CLASSICAL,
                200,
                [TechType.wheel]
            )

        # industrial
        elif self == TechType.industrialization:
            return TechTypeData(
                _('TXT_KEY_TECH_INDUSTRIALIZATION_NAME'),
                _('TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA'),
                _('TXT_KEY_TECH_INDUSTRIALIZATION_EUREKA_TEXT'),
                EraType.industrial,
                700,
                [""".massProduction, .squareRigging"""]
            )

        # modern
        elif self == TechType.refining:
            return TechTypeData(
                _('TXT_KEY_TECH_REFINING_NAME'),
                _('TXT_KEY_TECH_REFINING_EUREKA'),
                _('TXT_KEY_TECH_REFINING_EUREKA_TEXT'),
                EraType.modern,
                1250,
                [""".rifling"""]
            )

        raise AttributeError(f'cant get data for tech {self}')

    def __str__(self):
        return self.value


class CivicTypeData:
    def __init__(self, name, inspiration_summary, inspiration_description, era, cost, required):
        self.name = name
        self.inspiration_summary = inspiration_summary
        self.inspiration_description = inspiration_description
        self.era = era
        self.cost = cost
        self.required = required


class CivicType:
    pass


class CivicType(ExtendedEnum):
    # default
    none = 'none'

    # ANCIENT

    def name(self) -> str:
        return self._data().name

    def required(self) -> []:
        return self._data().required

    def cost(self) -> int:
        return self._data().cost

    def _data(self):
        if self == CivicType.none:
            return CivicTypeData(
                _('TXT_KEY_CIVIC_NONE'),
                '',
                '',
                EraType.ANCIENT,
                0,
                []
            )

        # ANCIENT

        raise AttributeError(f'cant get data for civic {self}')

    def __str__(self):
        return self.value
