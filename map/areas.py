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


class ContinentType:
	pass


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

	@staticmethod
	def fromName(continentName: str) -> ContinentType:
		if continentName == 'ContinentType.none' or continentName == 'none':
			return ContinentType.none

		elif continentName == 'ContinentType.africa' or continentName == 'africa':
			return ContinentType.africa
		elif continentName == 'ContinentType.amasia' or continentName == 'amasia':
			return ContinentType.amasia
		elif continentName == 'ContinentType.america' or continentName == 'america':
			return ContinentType.america
		elif continentName == 'ContinentType.antarctica' or continentName == 'antarctica':
			return ContinentType.antarctica
		elif continentName == 'ContinentType.arctica' or continentName == 'arctica':
			return ContinentType.arctica
		# asia = 'asia'
		# asiamerica = 'asiamerica'
		# atlantica = 'atlantica'
		# atlantis = 'atlantis'
		# australia = 'australia'
		# avalonia = 'avalonia'
		# azania = 'azania'
		# baltica = 'baltica'
		# cimmeria = 'cimmeria'
		# columbia = 'columbia'
		# congocraton = 'congocraton'
		elif continentName == 'ContinentType.euramerica' or continentName == 'euramerica':
			return ContinentType.euramerica
		# europe = 'europe'
		# gondwana = 'gondwana'
		# kalaharia = 'kalaharia'
		# kazakhstania = 'kazakhstania'
		# kernorland = 'kernorland'
		# kumarikandam = 'kumarikandam'
		# laurasia = 'laurasia'
		# laurentia = 'laurentia'
		# lemuria = 'lemuria'
		# mu = 'mu'
		# nena = 'nena'
		elif continentName == 'ContinentType.northAmerica' or continentName == 'northAmerica':
			return ContinentType.northAmerica
		# novoPangaea = 'novoPangaea'
		# nuna = 'nuna'
		# pangaea = 'pangaea'
		# pangaeaUltima = 'pangaeaUltima'
		# pannotia = 'pannotia'
		# rodinia = 'rodinia'
		# siberia = 'siberia'
		# southAmerica = 'southAmerica'
		# terraAustralis = 'terraAustralis'
		# ur = 'ur'
		# vaalbara = 'vaalbara'
		# vendian = 'vendian'
		# zealandia = 'zealandia'

		raise Exception(f'No matching case for continentName: "{continentName}"')

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


class OceanType:
	pass


class OceanType(ExtendedEnum):
	atlantic = 'atlantic'
	pacific = 'pacific'
	northSea = 'northSea'
	mareNostrum = 'mareNostrum'
	balticSea = 'balticSea'

	@staticmethod
	def fromName(oceanName: str) -> OceanType:
		if oceanName == 'OceanType.atlantic' or oceanName == 'atlantic':
			return OceanType.atlantic
		elif oceanName == 'OceanType.pacific' or oceanName == 'pacific':
			return OceanType.pacific
		elif oceanName == 'OceanType.northSea' or oceanName == 'northSea':
			return OceanType.northSea
		elif oceanName == 'OceanType.mareNostrum' or oceanName == 'mareNostrum':
			return OceanType.mareNostrum
		elif oceanName == 'OceanType.balticSea' or oceanName == 'balticSea':
			return OceanType.balticSea

		raise Exception(f'No matching case for oceanName: "{oceanName}"')
