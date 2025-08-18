from pydantic import BaseModel, Field
from typing import List, Optional, Union

class YouTubeTranscriptRequest(BaseModel):
    video_id: str = Field(..., description="The ID or URL of the YouTube video.")
    languages: Optional[List[str]] = Field(
        None,
        description="List of preferred language codes (e.g., ['en', 'de']). Defaults to ['en']."
    )
    preserve_formatting: bool = Field(
        False,
        description="Whether to preserve HTML formatting (e.g., <i>, <b>). Defaults to False."
    )
    translate_to: Optional[str] = Field(
        None,
        description="Language code to translate the transcript to (e.g., 'es'). Uses YouTube's translation."
    )
    start_time: Optional[Union[float, str]] = Field(
        None,
        description="Start time in seconds or 'MM:SS'/'HH:MM:SS' format. Inclusive."
    )
    end_time: Optional[Union[float, str]] = Field(
        None,
        description="End time in seconds or 'MM:SS'/'HH:MM:SS' format. Inclusive."
    )

class TranscriptSnippet(BaseModel):
    text: str = Field(..., description="Text content of the snippet.")
    start: float = Field(..., description="Start time of the snippet in seconds.")
    duration: float = Field(..., description="Duration of the snippet in seconds.")

class YouTubeTranscriptResponse(BaseModel):
    video_id: str = Field(..., description="The ID of the YouTube video.")
    language: str = Field(..., description="Language of the fetched transcript.")
    language_code: str = Field(..., description="Language code of the fetched transcript.")
    is_generated: bool = Field(..., description="True if auto-generated, False otherwise.")
    is_translatable: bool = Field(..., description="True if YouTube can translate this transcript.")
    raw_transcript_snippets: List[TranscriptSnippet] = Field(
        ...,
        description="Raw transcript snippets, filtered by time range if specified."
    )
    final_transcript_text: str = Field(
        ...,
        description="The final concatenated transcript text (raw, time-filtered, and optionally translated by YouTube)."
    )
    message: str = Field("Transcript fetched and processed successfully.", description="Status message.")
