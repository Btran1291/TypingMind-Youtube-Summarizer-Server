from fastapi import APIRouter, HTTPException, status
from youtube_summarizer.models import YouTubeTranscriptRequest, YouTubeTranscriptResponse
from youtube_summarizer.services import get_youtube_transcript_and_metadata

router = APIRouter()

@router.post(
    "/youtube/transcript",
    response_model=YouTubeTranscriptResponse,
    summary="Fetch YouTube Video Transcript and Metadata",
    description="Fetches the transcript and metadata for a given YouTube video ID or URL. "
                "Supports language preferences, optional YouTube translation, "
                "and filtering by a specific time range. This function is ideal for "
                "preparing video content for AI summarization. Note: Punctuation "
                "correction is not available in this lightweight version.",
    response_description="The fetched transcript and associated metadata."
)
async def fetch_youtube_transcript(
    request: YouTubeTranscriptRequest
):
    result = await get_youtube_transcript_and_metadata(
        video_id=request.video_id,
        languages=request.languages,
        preserve_formatting=request.preserve_formatting,
        translate_to=request.translate_to,
        start_time=request.start_time,
        end_time=request.end_time
    )

    return YouTubeTranscriptResponse(**result)
