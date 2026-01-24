"""
SSE Streaming Utilities

Server-Sent Events helpers for real-time agent progress updates.
"""

import json
from typing import AsyncGenerator, Any
from fastapi.responses import StreamingResponse


async def event_generator(
    data_generator: AsyncGenerator[dict, None],
    event_type: str = "message"
) -> AsyncGenerator[str, None]:
    """
    Convert a data generator to SSE format.
    
    Args:
        data_generator: Async generator yielding dict data
        event_type: The SSE event type
        
    Yields:
        SSE formatted strings
    """
    async for data in data_generator:
        yield f"event: {event_type}\n"
        yield f"data: {json.dumps(data)}\n\n"


def create_sse_response(generator: AsyncGenerator[str, None]) -> StreamingResponse:
    """
    Create an SSE StreamingResponse.
    
    Args:
        generator: Async generator yielding SSE formatted strings
        
    Returns:
        FastAPI StreamingResponse configured for SSE
    """
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


def format_sse_event(event_type: str, data: Any) -> str:
    """
    Format a single SSE event.
    
    Args:
        event_type: The event type name
        data: Data to serialize as JSON
        
    Returns:
        SSE formatted string
    """
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
