# tools/__init__.py
from .google_search import google_search_tool, get_current_datetime_tool
from .weather import weather_tool
from .system_control import (
    volume_control_tool, take_screenshot_tool, system_shutdown_tool,
    system_restart_tool, cancel_shutdown_tool, open_application_tool as open_app_tool,
    close_application_tool as close_tool, get_system_info_tool, open_website_tool
)
from .window_ctrl import open as open_window_tool, close as close_window_tool, folder_file as folder_file_tool
from .file_indexer import play_file_tool, file_indexer_tool
from .keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool,
    type_text_tool, press_key_tool, press_hotkey_tool,
    control_volume_tool, swipe_gesture_tool
)
from .brightness import brightness_tool
from .auto_modes import auto_modes_tool
from .macro_recorder import macro_recorder_tool
from .groq_llm import groq_answer_tool
from .study_mode_tool import study_mode_tool
from .answer_router import get_best_answer
from .google_llm import gemini_answer_tool
from .groq_llm import groq_answer_tool
from .net_speed import net_status_tool
from .youtube_player import play_youtube_song_tool
from .whatsapp import whatsapp_send_tool
from .intent_classifier import classify_intent_tool
from .gate_mode import gate_mode_tool
from .tool_router import tool_router_get_answer
from .radio_spotify import spotify_play_tool
from .instagram_dm import instagram_dm_tool
from .gmail_tool import gmail_send_tool
from .profile_face_unlock import profile_face_unlock_tool
from .memory import memory_get_tool, memory_set_tool
from .social_media import SocialMediaManager, open_social_media_tool, show_social_links_tool, set_social_link_tool, get_social_links_tool
from .social_media import (
    open_twitter_tool, open_instagram_tool, open_linkedin_tool,
    open_github_tool, open_youtube_tool
)
  
   