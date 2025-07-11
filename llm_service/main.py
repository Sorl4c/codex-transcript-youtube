# llm_service/main.py
# @docs
import time
import uuid
import asyncio # Added for Lock
import json # Added for SSE streaming
from fastapi import FastAPI, HTTPException, Request # Added Request for client disconnect check
from fastapi.responses import JSONResponse, StreamingResponse # Added StreamingResponse

from .schemas import ChatCompletionRequest, ChatCompletionResponse, ChatMessage, ChatCompletionChoice, UsageStats
from .model_loader import get_llm_instance, model_manager # Import model_manager for startup
from .config import settings
from .logger import logger # Use centralized logger

# Concurrency lock for LLM access
llm_lock = asyncio.Lock()

app = FastAPI(
    title="Local LLM Service",
    description="OpenAI-compatible API for local GGUF models",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    try:
        model_manager.load_model() # Pre-load the model
        logger.info("Model loading process initiated at startup.")
    except Exception as e:
        logger.error(f"Fatal error during model loading at startup: {e}", exc_info=True)
        # Depending on desired behavior, you might want to prevent startup or allow it with no model
        # For now, we log and continue; endpoints will fail if model is not loaded.

@app.post("/v1/chat/completions") # response_model removed for dynamic response (streaming/non-streaming)
async def create_chat_completion(chat_request: ChatCompletionRequest, fastapi_request: Request): # Renamed request to chat_request
    # Check if client disconnected early for streaming requests
    async def check_client_disconnected():
        if await fastapi_request.is_disconnected():
            logger.info("Client disconnected, stopping stream.")
            raise asyncio.CancelledError("Client disconnected")

    try:
        llm = get_llm_instance()
    except RuntimeError as e:
        logger.error(f"Model not available: {e}")
        raise HTTPException(status_code=503, detail=f"Model not available: {e}")
    except Exception as e:
        logger.error(f"Failed to get LLM instance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error: Could not load LLM.")

    if llm is None:
        # This should ideally be caught by get_llm_instance() raising an error
        logger.error("LLM object is None after trying to load. This should not happen.")
        raise HTTPException(status_code=503, detail="Model is not loaded or failed to load.")

    # Convert Pydantic messages to the format LlamaCPP expects if necessary
    # For LlamaCPP, the entire conversation history is usually passed.
    # The `create_chat_completion` method of LlamaCPP handles this directly.

    try:
        logger.info(f"Received chat completion request for model: {chat_request.model}")

        completion_params = {
            "temperature": chat_request.temperature if chat_request.temperature is not None else settings.DEFAULT_TEMPERATURE,
            "top_p": chat_request.top_p if chat_request.top_p is not None else settings.DEFAULT_TOP_P,
            "max_tokens": chat_request.max_tokens if chat_request.max_tokens is not None else settings.DEFAULT_MAX_TOKENS,
            "stream": chat_request.stream, # Pass stream parameter to LlamaCPP
            # "stop": chat_request.stop, # Add if supported and needed
        }
        completion_params = {k: v for k, v in completion_params.items() if v is not None}

        messages_for_llm = [msg.model_dump(exclude_none=True) for msg in chat_request.messages]

        response_id = f"chatcmpl-{uuid.uuid4()}"
        created_timestamp = int(time.time())

        async def stream_generator():
            stream_ended_properly = False
            try:
                logger.info(f"Starting stream for request {response_id}")
                async with llm_lock: # Acquire lock for the duration of the LLM call
                    llm_stream = llm.create_chat_completion(
                        messages=messages_for_llm,
                        **completion_params
                    )
                
                for chunk in llm_stream:
                    await check_client_disconnected() # Check before processing each chunk
                    # logger.debug(f"Stream chunk: {chunk}")
                    # Construct OpenAI-compatible streaming chunk
                    stream_choice = {
                        "index": chunk["choices"][0]["index"],
                        "delta": chunk["choices"][0]["delta"],
                        "finish_reason": chunk["choices"][0]["finish_reason"]
                    }
                    # Ensure delta content is not None, even if empty
                    if "content" not in stream_choice["delta"]:
                        stream_choice["delta"]["content"] = ""
                        
                    sse_data = {
                        "id": response_id,
                        "object": "chat.completion.chunk",
                        "created": created_timestamp,
                        "model": settings.MODEL_PATH, # Or a more generic name
                        "choices": [stream_choice]
                    }
                    yield f"data: {json.dumps(sse_data)}\n\n"
                    if stream_choice["finish_reason"] is not None:
                        logger.info(f"Stream finished for {response_id}, reason: {stream_choice['finish_reason']}")
                        stream_ended_properly = True
                        break # Exit after sending the chunk with finish_reason
                
                if not stream_ended_properly:
                    # This case might occur if the stream ends without a finish_reason in the last chunk
                    # or if the loop finishes for other reasons. Send a final empty content chunk with finish_reason if needed.
                    # However, llama-cpp-python usually provides finish_reason in the last chunk.
                    logger.warning(f"Stream for {response_id} ended without explicit finish_reason in final chunk data.")

            except asyncio.CancelledError:
                logger.info(f"Stream {response_id} cancelled by client disconnect.")
                # No need to yield further, connection is closed
                return # Important to exit the generator
            except Exception as e:
                logger.error(f"Error during streaming for {response_id}: {e}", exc_info=True)
                # Try to send an error message if possible, though client might be gone
                error_payload = {"error": {"message": str(e), "type": "internal_server_error", "code": 500}}
                try:
                    yield f"data: {json.dumps(error_payload)}\n\n"
                except Exception as send_err:
                    logger.error(f"Could not send error SSE for {response_id}: {send_err}")
            finally:
                logger.info(f"Finalizing stream for {response_id}. Sending [DONE] message.")
                yield f"data: [DONE]\n\n"

        if chat_request.stream:
            return StreamingResponse(stream_generator(), media_type="text/event-stream")
        else:
            async with llm_lock: # Acquire lock for non-streaming LLM call
                start_time = time.time()
                raw_completion = llm.create_chat_completion(
                    messages=messages_for_llm,
                    **completion_params
                )
                duration = time.time() - start_time
            logger.info(f"LLM call completed in {duration:.2f}s")
            logger.debug(f"Raw completion from LLM: {raw_completion}")

            choices = []
            for choice_data in raw_completion.get("choices", []):
                choices.append(
                    ChatCompletionChoice(
                        index=choice_data.get("index"),
                        message=ChatMessage(
                            role=choice_data.get("message", {}).get("role"),
                            content=choice_data.get("message", {}).get("content")
                        ),
                        finish_reason=choice_data.get("finish_reason")
                    )
                )
            
            usage_data = raw_completion.get("usage")
            usage = None
            if usage_data:
                usage = UsageStats(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0)
                )

            return ChatCompletionResponse(
                id=response_id,
                created=created_timestamp,
                model=settings.MODEL_PATH,
                choices=choices,
                usage=usage
            )

    except HTTPException: # Re-raise HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"Error during chat completion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    # More sophisticated health checks could verify model loading status
    try:
        llm = get_llm_instance()
        if llm:
            return {"status": "ok", "model_loaded": True, "model_path": settings.MODEL_PATH}
    except Exception:
        pass # Fall through to not loaded / error state
    return JSONResponse(
        status_code=503,
        content={"status": "error", "model_loaded": False, "detail": "Model not loaded or error during loading."}
    )

# To run this app (from the project root directory, assuming venv is active):
# uvicorn llm_service.main:app --host 0.0.0.0 --port 8000 --reload
