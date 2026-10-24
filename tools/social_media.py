import webbrowser
import os
import subprocess
from typing import Dict
from livekit.agents import function_tool

# =====================================================
# SOCIAL MEDIA MANAGER (Optimized for Jarvies v4.0)
# =====================================================

class SocialMediaManager:
    def __init__(self):
        self.user_name = "Himanshu sir"

        # Register Chrome on Windows (fallback safe)
        if os.name == 'nt':
            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
            if os.path.exists(chrome_path):
                try:
                    webbrowser.register(
                        'chrome',
                        None,
                        webbrowser.BackgroundBrowser(chrome_path)
                    )
                except:
                    pass

        # Social media profile links
        self.social_links = {
            "twitter":  "https://twitter.com/himanshu231204",
            "instagram": "https://instagram.com/fitz_himanshu",
            "linkedin": "https://linkedin.com/in/himanshu231204",
            "github": "https://github.com/himanshu231204",
            "youtube": "https://youtube.com",
            "chatgpt": "https://chat.openai.com",
        }

    # =====================================================
    # OPEN ANY SOCIAL MEDIA PLATFORM
    # =====================================================
    def open_social_media(self, platform: str) -> str:
        platform = platform.lower().strip()

        if platform not in self.social_links:
            return (
                f"❌ {self.user_name}, '{platform}' link set nahi hai.\n"
                f"Available: {', '.join(self.social_links.keys())}"
            )

        url = self.social_links[platform]

        # Try Chrome first
        try:
            webbrowser.get("chrome").open(url)
            return f"🌐 {self.user_name}, {platform} open kar diya."
        except:
            pass

        # Try default browser
        try:
            webbrowser.open(url)
            return f"🌐 {self.user_name}, {platform} open kar diya."
        except:
            pass

        # Fallback -> Windows start command
        if os.name == "nt":
            try:
                subprocess.Popen(f'start "" "{url}"', shell=True)
                return f"🌐 {self.user_name}, {platform} open kar diya."
            except Exception as e:
                return f"❌ Browser error: {str(e)}"

        return f"❌ {self.user_name}, browser open nahi ho paaya."

    # =====================================================
    # SHOW ALL SOCIAL LINKS
    # =====================================================
    def show_social_links(self) -> str:
        if not self.social_links:
            return f"❌ {self.user_name}, koi link set nahi hai."

        msg = f"📱 {self.user_name}, aapke social media links:\n\n"
        for p, url in self.social_links.items():
            msg += f"• {p.capitalize()} → {url}\n"
        return msg

    # =====================================================
    # UPDATE A SOCIAL LINK
    # =====================================================
    def set_social_link(self, platform: str, url: str) -> str:
        if not url.startswith("http"):
            return f"❌ {self.user_name}, valid URL dijiye."

        self.social_links[platform.lower().strip()] = url
        return f"✅ {platform} link update ho gaya: {url}"

    # =====================================================
    # RETURN DICTIONARY OF ALL LINKS
    # =====================================================
    def get_all_links(self) -> Dict[str, str]:
        return self.social_links


# Global instance
social_manager = SocialMediaManager()

# =====================================================
# LIVEKIT TOOL WRAPPERS (Hinglish)
# =====================================================

@function_tool
async def open_social_media_tool(platform: str):
    """Kisi bhi social media platform ko browser me open karein."""
    return social_manager.open_social_media(platform)

@function_tool
async def show_social_links_tool():
    """Social media ke saare links dikhayein."""
    return social_manager.show_social_links()

@function_tool
async def set_social_link_tool(platform: str, url: str):
    """Kisi social media ka link set ya update karein."""
    return social_manager.set_social_link(platform, url)

@function_tool
async def get_social_links_tool():
    """Saare social media links get karein."""
    return str(social_manager.get_all_links())


# Quick Access Tools
@function_tool
async def open_twitter_tool():
    """Twitter open karein."""
    return social_manager.open_social_media("twitter")

@function_tool
async def open_instagram_tool():
    """Instagram open karein."""
    return social_manager.open_social_media("instagram")

@function_tool
async def open_linkedin_tool():
    """LinkedIn open karein."""
    return social_manager.open_social_media("linkedin")

@function_tool
async def open_github_tool():
    """GitHub open karein."""
    return social_manager.open_social_media("github")

@function_tool
async def open_youtube_tool():
    """YouTube open karein."""
    return social_manager.open_social_media("youtube")

@function_tool
async def open_chatgpt_tool():
    """ChatGPT open karein."""
    return social_manager.open_social_media("chatgpt")


# Setup helper (optional)
def setup_social_media():
    return f"✅ {social_manager.user_name}, social media setup complete!"
