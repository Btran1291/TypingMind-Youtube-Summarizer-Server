import re
from typing import List, Optional, Union
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter
from youtube_summarizer.models import TranscriptSnippet

def extract_video_id(url_or_id: str) -> str:
    """Extracts YouTube video ID from URL or returns ID if already provided."""
    youtube_regex = (
        r'(?:https?://)?(?:www\.)?(?:m\.)?'
        r'(?:youtube\.com|youtu\.be)/(?:watch\?v=|embed/|v/|)'
        r'([a-zA-Z0-9_-]{11})(?:[^#&?]*|$)'
    )
    match = re.match(youtube_regex, url_or_id)
    if match:
        return match.group(1)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    raise ValueError(f"Invalid YouTube video ID or URL format: {url_or_id}")

def parse_time_to_seconds(time_input: Union[float, str]) -> float:
    """Parses time (float seconds or 'MM:SS'/'HH:MM:SS') into total seconds, ensuring non-negative."""
    if isinstance(time_input, float):
        total_seconds = time_input
    else:
        parts = list(map(float, time_input.split(':')))
        if len(parts) == 1:
            total_seconds = parts[0]
        elif len(parts) == 2:
            total_seconds = parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            total_seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        else:
            raise ValueError(f"Invalid time format: {time_input}. Expected seconds, MM:SS, or HH:MM:SS.")
    
    if total_seconds < 0:
        raise ValueError(f"Time cannot be negative: {time_input}")
        
    return total_seconds

async def get_youtube_transcript_and_metadata(
    video_id: str,
    languages: Optional[List[str]] = None,
    preserve_formatting: bool = False,
    translate_to: Optional[str] = None,
    # punctuated_transcript parameter removed
    start_time: Optional[Union[float, str]] = None,
    end_time: Optional[Union[float, str]] = None
):
    """
    Fetches YouTube transcript and metadata, applying language preference,
    optional YouTube translation, and time filtering.
    Prioritizes manual transcripts and handles various input formats.
    """
    selected_language = "Unknown"
    selected_language_code = "unk"
    is_generated = True
    is_translatable = False
    fetched_transcript_raw = []
    filtered_transcript_snippets = []
    final_text_output = ""
    status_message = "Transcript fetched and processed successfully."

    try:
        processed_video_id = extract_video_id(video_id)
        processed_start_time = parse_time_to_seconds(start_time) if start_time is not None else None
        processed_end_time = parse_time_to_seconds(end_time) if end_time is not None else None
    except ValueError as e:
        return {
            "video_id": video_id, "language": "N/A", "language_code": "N/A",
            "is_generated": False, "is_translatable": False,
            "raw_transcript_snippets": [], "final_transcript_text": "",
            "message": f"Input error: {e}"
        }

    if not languages:
        languages = ['en']

    try:
        yt_api = YouTubeTranscriptApi()
        transcript_list = yt_api.list(processed_video_id)
        transcript_obj = None

        try:
            transcript_obj = transcript_list.find_manually_created_transcript(languages)
        except NoTranscriptFound:
            try:
                transcript_obj = transcript_list.find_transcript(languages)
            except NoTranscriptFound:
                all_available = list(transcript_list)
                if all_available:
                    transcript_obj = next((t for t in all_available if t.language_code == 'en'), all_available[0])
                else:
                    raise NoTranscriptFound(f"No transcripts available for video ID: {processed_video_id}")

        fetched_transcript_raw = transcript_obj.fetch().to_raw_data()
        selected_language = transcript_obj.language
        selected_language_code = transcript_obj.language_code
        is_generated = transcript_obj.is_generated
        is_translatable = transcript_obj.is_translatable

        if translate_to and is_translatable and transcript_obj.language_code != translate_to:
            translated_transcript_obj = transcript_obj.translate(translate_to)
            fetched_transcript_raw = translated_transcript_obj.fetch().to_raw_data()
            selected_language = translated_transcript_obj.language
            selected_language_code = translated_transcript_obj.language_code
            is_generated = translated_transcript_obj.is_generated
            is_translatable = False

        if processed_start_time is not None or processed_end_time is not None:
            for snippet_data in fetched_transcript_raw:
                snippet_start = snippet_data['start']
                snippet_duration = snippet_data['duration']
                snippet_text = snippet_data['text']
                snippet_end = snippet_start + snippet_duration

                segment_start = max(snippet_start, processed_start_time if processed_start_time is not None else snippet_start)
                segment_end = min(snippet_end, processed_end_time if processed_end_time is not None else snippet_end)

                if segment_start < segment_end:
                    chars_per_second = len(snippet_text) / snippet_duration if snippet_duration > 0 else 0
                    text_start_index = int((segment_start - snippet_start) * chars_per_second)
                    text_end_index = int((segment_end - snippet_start) * chars_per_second)
                    
                    text_start_index = max(0, text_start_index)
                    text_end_index = min(len(snippet_text), text_end_index)

                    if text_start_index < text_end_index:
                        filtered_transcript_snippets.append(TranscriptSnippet(
                            text=snippet_text[text_start_index:text_end_index],
                            start=segment_start,
                            duration=segment_end - segment_start
                        ))
            
            if not filtered_transcript_snippets and (processed_start_time is not None or processed_end_time is not None):
                status_message = "No transcript snippets found within the specified time range."
        else:
            filtered_transcript_snippets = [
                TranscriptSnippet(**s) for s in fetched_transcript_raw
            ]

        formatter = TextFormatter()
        final_text_output = formatter.format_transcript(filtered_transcript_snippets) # Always raw, concatenated text
        status_message = "Transcript fetched and processed successfully." # Simplified message

    except (NoTranscriptFound, TranscriptsDisabled) as e:
        status_message = f"Error fetching transcript: {e}. It might not have subtitles or they are disabled."
        return {
            "video_id": processed_video_id,
            "language": selected_language,
            "language_code": selected_language_code,
            "is_generated": is_generated,
            "is_translatable": is_translatable,
            "raw_transcript_snippets": [],
            "final_transcript_text": "",
            "message": status_message
        }
    except Exception as e:
        status_message = f"An unexpected error occurred: {e}"
        print(f"Unexpected error for video ID {processed_video_id}: {e}")
        return {
            "video_id": processed_video_id,
            "language": selected_language,
            "language_code": selected_language_code,
            "is_generated": is_generated,
            "is_translatable": is_translatable,
            "raw_transcript_snippets": [],
            "final_transcript_text": "",
            "message": status_message
        }

    return {
        "video_id": processed_video_id,
        "language": selected_language,
        "language_code": selected_language_code,
        "is_generated": is_generated,
        "is_translatable": is_translatable,
        "raw_transcript_snippets": filtered_transcript_snippets,
        "final_transcript_text": final_text_output,
        "message": status_message
    }
