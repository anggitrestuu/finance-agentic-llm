from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def add_error_handlers(app: FastAPI) -> None:
    """
    Add global error handlers to the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle HTTP exceptions
        
        Args:
            request: FastAPI request
            exc: HTTP exception
            
        Returns:
            JSONResponse with error details
        """
        logger.warning(
            f"HTTP error occurred - status: {exc.status_code}, detail: {exc.detail}, "
            f"path: {request.url.path}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.status_code,
                "message": str(exc.detail),
                "path": request.url.path
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle general exceptions
        
        Args:
            request: FastAPI request
            exc: Unhandled exception
            
        Returns:
            JSONResponse with error details
        """
        logger.error(
            f"Unhandled exception occurred - type: {type(exc).__name__}, "
            f"detail: {str(exc)}, path: {request.url.path}",
            exc_info=True
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "code": 500,
                "message": "Internal server error",
                "path": request.url.path
            }
        )