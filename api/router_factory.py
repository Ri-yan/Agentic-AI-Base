import yaml
import logging
from fastapi import APIRouter, HTTPException
from api.models.base_payload import BasePayload
from core.utils.utils import import_payload_class
from usecases.usecase_factory import UseCaseFactory

# Setup logger
logger = logging.getLogger("router_factory")
logging.basicConfig(level=logging.INFO)

def load_config(yml_path="usecase_routes.yml"):
    with open(yml_path) as f:
        return yaml.safe_load(f)

def  create_router_from_config(config: dict):
    router = APIRouter()
    failed_routes = []

    for name, meta in config.items():
        route = meta["route"]
        methods = meta["methods"]
        use_case_name = meta["use_case"]
        payload_name = meta.get("payload", "dict")
        tags = meta.get("tags", [])
        try:
            use_case_instance = UseCaseFactory.create_use_case(use_case_name)
            payload_cls = import_payload_class(payload_name)

        except Exception as e:
            logger.error(f"[{name}] Skipping route '{route}': {e}")
            failed_routes.append((name, route, str(e)))
            continue

        # ✅ Properly bind endpoint
        def create_endpoint(use_case, payload_cls):
            async def endpoint(payload: payload_cls):  # 👈 This line is key
                try:
                    payload_data = payload.dict() if hasattr(payload, "dict") else payload
                    result = use_case.execute(payload_data)

                    # 🔍 Check if result is a coroutine
                    if hasattr(result, "__await__"):
                        result = await result

                    return result

                except Exception as e:
                    logger.exception(f"Execution error in use case '{use_case}': {e}")
                    raise HTTPException(status_code=500, detail=str(e))

            return endpoint

        router.add_api_route(route, create_endpoint(use_case_instance, payload_cls), methods=methods,tags=tags)
        logger.info(f"✅ Route registered: {methods} {route} -> {use_case_name}")

    if failed_routes:
        logger.warning("⚠️ Some routes failed to load:")
        for name, route, reason in failed_routes:
            logger.warning(f" - [{name}] Route '{route}' skipped: {reason}")

    return router
