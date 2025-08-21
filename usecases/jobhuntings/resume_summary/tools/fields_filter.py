import json
from typing import Any


def fields_filter_tool(filtered_keywords: Any, raw_response: str, log=None) -> Any:
    try:
        # Parse the raw JSON response into a list of dictionaries
        data_list = json.loads(raw_response)
        filtered_keywords = sorted(filtered_keywords)
        # Sort the data list by the "Name" field
        data_list = sorted(data_list, key=lambda x: x["Name"].strip().lower())

        # Create a reduced list based on partial matching of filtered keywords
        filtered_data_list = []

        # Loop through the data list and match each entry with the filtered_keywords
        for entry in data_list:
            for keyword in filtered_keywords:
                if entry["Name"].lower().startswith(keyword[:4].lower()):
                    filtered_data_list.append(entry)


        # Return the filtered data list
        if not filtered_data_list:
            raise ValueError("No fields matched the keywords.")

        return filtered_data_list

    except Exception as e:
        if log:
            log.error(f"{str(e)}")
        raise
