from enum import Enum

# Enums for model management
class ModelEnum(Enum):
    SchemaModel = 1
    FieldDefinition = 2
    FilterDefinition = 3
    GraphData = 4
    QueryConfigModel = 5
    SimpleListModel = 6

graph_types = ["column", "bar", "stackedGraph", "stackColumn", "pieChart", "donut", "semiCirclePieChart", "lineChart", "multilineChart", "scatterplot", "bubble","funnel"]
dashlet_types = {"CustomizedDashlets":"multipleDashlets"}