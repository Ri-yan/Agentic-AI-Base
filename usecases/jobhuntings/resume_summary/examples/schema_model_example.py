from usecases.agpt_generation.models.SchemaModel import SchemaModelOutput,FilterDefinition,FieldDefinition,OrderDefinition

SchemaModelExample = SchemaModelOutput(
    Fields=[
        FieldDefinition(FieldName="salary", FieldType="dimension",Type="Number", Aggregation="None"),
        FieldDefinition(FieldName="age", FieldType="dimension",Type="Number", Aggregation="Count")
    ],
    Filters=[
        FilterDefinition(FieldName="department",Type="Text", FieldType="dimension", OperatorType="Equal", Value="finance")
    ],
    GroupBy=["department"],
    OrderBy=[OrderDefinition(FieldName="salary", OrderType="ASC")],
    BatchSize=10,
    RoundUpCount=0
)

# Final context string passed to the LLM
SCHEMA_CONTEXT = SchemaModelExample.model_dump_json(indent=2)


#
# SCHEMA_CONTEXT = dedent("""
# {
#   "Fields": [
#     {
#       "FieldName": "<FieldName>",
#       "FieldType": "<FieldType>",
#       "Aggregation": "<Aggregation>"
#     }
#   ],
#   "Filters": [
#     {
#       "FieldName": "<FieldName>",
#       "FieldType": "<FieldType>",
#       "OperatorType": "<OperatorType>",
#       "Value": "<Value>"
#     }
#   ],
#   "GroupBy": [],
#   "OrderBy": [],
#   "BatchSize": null
# }
#
# ### Example Output:
# {
#   "Fields": [
#     {
#       "FieldName": "Name",
#       "FieldType": "TEXT",
#       "Aggregation": null
#     },
#     {
#       "FieldName": "salary",
#       "FieldType": "INTEGER",
#       "Aggregation": "MAX"
#     }
#   ],
#   "Filters": [
#     {
#       "FieldName": "department",
#       "FieldType": "TEXT",
#       "OperatorType": "Equals",
#       "Value": "finance"
#     }
#   ],
#    "GroupBy": [],
#   "OrderBy": [
#     {
#       "FieldName": "salary",
#       "OrderType": "DESC"
#     }
#   ],
#   "BatchSize": 10
# }
# """)
