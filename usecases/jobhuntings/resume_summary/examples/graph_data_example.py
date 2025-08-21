from usecases.agpt_generation.models.GraphDataModel import AxisField, Responsive, ChartCursor, GraphField, GraphDataModel

Context = GraphDataModel(
    type="",
    categoryField="",
    categoryAxis = AxisField(title=""),
    valueAxes = [AxisField(title="")],
    responsive = Responsive(enabled = True),
    dataProvider = [],
    chartCursor = ChartCursor(),
    graphs = [
        GraphField(type = "", valueField = "", title="")
    ]
)
# Graph Context
GRAPH_CONTEXT = Context.model_dump_json(indent=2)



# CONTEXT = """{   "type": "",   "dataProvider": [],   "categoryField": "",   "graphs": [{     "valueField": "",     "type": "",     "title": ""   }],   "categoryAxis": {     "title": ""   },   "valueAxes": [{     "title": ""   }],   "chartCursor": {},   "responsive": {     "enabled":   } }"""
