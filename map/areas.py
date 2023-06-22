from core.base import ExtendedEnum


class Continent:
	def __init__(self, identifier: int, name: str, mapModel):
		self.identifier = identifier
		self.name = name
		self.mapModel = mapModel
		self.points = []
		self.continentType = ContinentType.none

	def add(self, point):
		self.points.append(point)

	def __str__(self):
		return f'Content: {self.identifier} {self.name}'


class ContinentType(ExtendedEnum):
	none = 'none'

	africa = 'africa'
	amasia = 'amasia'
	america = 'america'
	antarctica = 'antarctica'
	arctica = 'arctica'
	asia = 'asia'
	asiamerica = 'asiamerica'
	atlantica = 'atlantica'
	atlantis = 'atlantis'
	australia = 'australia'
	avalonia = 'avalonia'
	azania = 'azania'
	baltica = 'baltica'
	cimmeria = 'cimmeria'
	columbia = 'columbia'
	congocraton = 'congocraton'
	euramerica = 'euramerica'
	europe = 'europe'
	gondwana = 'gondwana'
	kalaharia = 'kalaharia'
	kazakhstania = 'kazakhstania'
	kernorland = 'kernorland'
	kumarikandam = 'kumarikandam'
	laurasia = 'laurasia'
	laurentia = 'laurentia'
	lemuria = 'lemuria'
	mu = 'mu'
	nena = 'nena'
	northAmerica = 'northAmerica'
	novoPangaea = 'novoPangaea'
	nuna = 'nuna'
	pangaea = 'pangaea'
	pangaeaUltima = 'pangaeaUltima'
	pannotia = 'pannotia'
	rodinia = 'rodinia'
	siberia = 'siberia'
	southAmerica = 'southAmerica'
	terraAustralis = 'terraAustralis'
	ur = 'ur'
	vaalbara = 'vaalbara'
	vendian = 'vendian'
	zealandia = 'zealandia'

	def name(self) -> str:
		return f'Continent: {self.value}'


class Ocean:
	def __init__(self, identifier: int, name: str, mapModel):
		self.identifier = identifier
		self.name = name
		self.mapModel = mapModel
		self.points = []
		self.continentType = ContinentType.none

	def add(self, point):
		self.points.append(point)

	def __str__(self):
		return f'Ocean: {self.identifier} {self.name}'


class OceanType(ExtendedEnum):
	atlantic = 'atlantic'
	pacific = 'pacific'
	northSea = 'northSea'
	mareNostrum = 'mareNostrum'
