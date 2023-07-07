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
	# self._route = RouteType.none
	# self._improvementValue = ImprovementType.none
	# self._improvementPillagedValue: bool = False
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


class MapModelSchema(Schema):
	width = fields.Int()
	height = fields.Int()
	tiles = fields.List(fields.List(fields.Nested(TileSchema)))

	# self._cities = []
	# self._units = []
	# self.startLocations = []
	# cityStateStartLocations = []
	#
	# self.continents = []
	# self.oceans = []