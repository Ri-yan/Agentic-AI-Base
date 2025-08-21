from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class GraphField(BaseModel):
    valueField: str
    type: str
    title: str    # title for chart

class AxisField(BaseModel):
    title: str    # field using from schema detail

class ChartCursor(BaseModel):
    pass

class Responsive(BaseModel):
    enabled: bool

class GraphDataModel(BaseModel):
    type: str
    dataProvider: List
    categoryField: str
    graphs: List[GraphField]
    categoryAxis: AxisField
    valueAxes: List[AxisField]
    chartCursor: ChartCursor
    responsive: Responsive