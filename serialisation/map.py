from marshmallow import Schema, fields, validate


class PointSchema(Schema):
	x = fields.Integer()
	y = fields.Integer()


class TileSchema(Schema):
	point = fields.Nested(PointSchema)
	terrain = fields.String(attribute="_terrainValue", required=True)
	isHills = fields.Boolean(attribute="_isHills")
	feature = fields.String(attribute="_featureValue")
	resource = fields.String(attribute="_resourceValue")
	resourceQuantity = fields.Integer(attribute="_resourceQuantity")

	river = fields.Integer(attribute="_riverValue")
	riverName = fields.String(attribute="_riverName", allow_none=True)

	climateZone = fields.String(attribute="_climateZone")
	route = fields.String(attribute="_route")
	improvement = fields.String(attribute="_improvementValue")
	improvementPillaged = fields.Boolean(attribute="_improvementPillagedValue")
	continentIdentifier = fields.String(allow_none=True)
	oceanIdentifier = fields.String(allow_none=True)
	# self.discovered = dict()
	# self.visible = dict()
	# self._cityValue = None
	# self._districtValue = None
	# self._wonderValue = WonderType.none
	# self._owner = None
	# self._workingCity = None
	# self._buildProgressList = WeightedBuildList()
	# self._area = None


class StartLocationSchema(Schema):
	location = fields.Nested(PointSchema)
	leader = fields.String(allow_none=True)
	cityState = fields.String(allow_none=True)
	isHuman = fields.Boolean()


class ContinentSchema(Schema):
	identifier = fields.String()
	name = fields.String()
	points = fields.List(fields.Nested(PointSchema))
	continentType = fields.String()


class OceanSchema(Schema):
	identifier = fields.String()
	name = fields.String()
	points = fields.List(fields.Nested(PointSchema))
	oceanType = fields.String()


class MapModelSchema(Schema):
	width = fields.Int()
	height = fields.Int()
	tiles = fields.List(fields.List(fields.Nested(TileSchema)))

	# self._cities = []
	# self._units = []
	startLocations = fields.List(fields.Nested(StartLocationSchema))
	cityStateStartLocations = fields.List(fields.Nested(StartLocationSchema))

	continents = fields.List(fields.Nested(ContinentSchema))
	oceans = fields.List(fields.Nested(OceanSchema))
