from livekit.agents import function_tool

@function_tool
async def instagram_dm_tool(username: str, message: str) -> str:
    """
    Placeholder Instagram DM tool.

    Instagram blocks automated actions for security.
    This tool only responds safely and does not perform real automation.

    If you want real Instagram automation:
    - You must use Selenium
    - You must log in manually
    - Then we can send messages safely

    For now, this safe version works inside Jarvies.
    """

    return (
        f"📌 Instagram automation is restricted.\n"
        f"➡ Username: {username}\n"
        f"➡ Message: {message}\n\n"
        f"❗ If you want REAL Instagram DM automation, "
        f"I can generate a Selenium bot for you."
    )
