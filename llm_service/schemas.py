# llm_service/schemas.py
# @docs
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

# OpenAI-compatible Schemas
# Based on https://platform.openai.com/docs/api-reference/chat/create

class ChatMessage(BaseModel):
    role: str # "system", "user", "assistant"
    content: Optional[str] = None # Content can be None for delta chunks with only role
    name: Optional[str] = None

class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str # Will typically be a fixed value for this local service
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    n: Optional[int] = Field(default=1, ge=1) # How many chat completion choices to generate for each input message.
    stream: Optional[bool] = Field(default=False)
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None # A unique identifier representing your end-user

class ChatCompletionChoice(BaseModel):
    index: int
    message: Optional[ChatMessage] = None # For non-streaming response
    delta: Optional[DeltaMessage] = None   # For streaming response
    finish_reason: Optional[str] = None # e.g., "stop", "length"

class UsageStats(BaseModel):
    prompt_tokens: int
    completion_tokens: Optional[int] = None
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str # A unique identifier for the chat completion
    object: str = "chat.completion"
    created: int # Unix timestamp (seconds)
    model: str # Model identifier used for the completion
    choices: List[ChatCompletionChoice]
    usage: Optional[UsageStats] = None
    # system_fingerprint: Optional[str] = None # Optional field some OpenAI models return

# Potentially add schemas for /v1/completions if needed
# class CompletionRequest(BaseModel): ...
# class CompletionResponse(BaseModel): ...
