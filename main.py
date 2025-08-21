# analytics_platform/main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.router_factory import load_config, create_router_from_config
from resources.constant import load_environs
import logging
import traceback

# Load environment variables
load_environs()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_agents")

app = FastAPI(
    title="Smart Agents",
    description="create, analyze, suggest and many more use cases to achieve.",
    version="1.0.0"
)

# ✅ Enable all origins CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # All origins allowed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ✅ Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled error: {exc}\nTraceback:\n{error_trace}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc),  # Hide in production
            "path": request.url.path
        }
    )

config = load_config("api/controllers/routes.yaml")
router = create_router_from_config(config)

app.include_router(router)

# Include routes
#app.include_router(routes, prefix="/api")

# Run app
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8025, reload=True,workers=int(os.getenv("WORKERS")))
