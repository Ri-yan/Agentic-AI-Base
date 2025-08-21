import json
from typing import Any
from pydantic import ValidationError
from usecases.agpt_generation.models.GraphDataModel import GraphDataModel
from usecases.agpt_generation.models.QueryConfig import QueryConfigModel
from usecases.agpt_generation.models.SchemaModel import SchemaModelOutput,FieldDefinition,FilterDefinition
from usecases.agpt_generation.enums.enums import ModelEnum

#for validating the model class
def _validate_model(raw_response: str,model_type:ModelEnum, log=None) -> Any:
    try:
        raw_response = remove_json_wrappers(raw_response)
        data_json = json.loads(raw_response)
        match model_type:
            case ModelEnum.SchemaModel:
                if isinstance(data_json, list):
                    # Handle list of JSON objects
                    validated_list = [SchemaModelOutput(**item).dict() for item in data_json]
                    validated = validated_list
                elif isinstance(data_json, dict):
                    # Handle single JSON object
                    validated = SchemaModelOutput(**data_json).dict()
                else:
                    raise ValueError("Invalid JSON format: expected dict or list of dicts.")
            case ModelEnum.FieldDefinition:
                validated = FieldDefinition(**data_json)
                validated = validated.dict()
            case ModelEnum.QueryConfigModel:
                validated = QueryConfigModel(**data_json)
                validated = validated.dict()
            case ModelEnum.FilterDefinition:
                validated = FilterDefinition(**data_json)
                validated = validated.dict()
            case ModelEnum.GraphData:
                validated_list = [GraphDataModel(**item) for item in data_json]
                validated = [item.dict() for item in validated_list]
            case ModelEnum.SimpleListModel:
                if not isinstance(data_json, list):
                    raise ValueError("Invalid data: must be a list.")
                validated = data_json
            case _:
                raise ValueError(f"Unsupported model_type: {model_type}")

        validated_dict=validated
        #return json.dumps(validated_dict, indent=2)
        return validated_dict

    except ValidationError as ve:
        if log:
            log.error(f"Model Validation Occured: {raw_response}",False)
        error_messages = [
            error.get("msg", "Model validation error occurred") for error in ve.errors()
        ]
        raise ValueError("; ".join(error_messages)) from ve

    except json.JSONDecodeError:
        if log:
            log.error(f"Invalid JSON returned: {raw_response}")
        raise

def remove_json_wrappers(input_string: str) -> str:
    # Check if the string starts with '```json' and ends with '```'
    if input_string.startswith('```json') and input_string.endswith('```'):
        # Remove the '```json' at the start and '```' at the end
        return input_string[len('```json'): -len('```')].strip()
    # Check if the string starts with '```' and ends with '```' (without 'json' specified)
    elif input_string.startswith('```') and input_string.endswith('```'):
        # Remove the '```' at the start and '```' at the end
        return input_string[len('```'): -len('```')].strip()
    return input_string



