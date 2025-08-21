from usecases.agpt_generation.models.QueryConfig import QueryConfigModel

QueryConfigModelExample = QueryConfigModel(
    isValidQuery= False,
    multiResponse= False,
    type= 'other',
    intent= 'none',
    topic= 'irrelevant',
    urgency= 'low',
    fieldsMentioned = True,
    requiresAuth= False,
    language= 'en',
    messageResponse= 'The query is not related to analytics or metric.',
    widgetType= 'chart'
)

# Final context string passed to the LLM
QUERY_CONTEXT = QueryConfigModelExample.model_dump_json(indent=2)
