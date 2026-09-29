# modules/identity_management.py
import re
from modules.context import ChatContext

NAME_PATTERNS = [
    r"(?:my name is|i am|i'm|you can call me|call me)\s+([A-Za-z][A-Za-z\-\s']{1,40})",
]

ASK_NAME_PATTERNS = [
    r"what's my name\??",
    r"do you remember my name\??",
]

FORGET_PATTERNS = [
    r"forget my name",
]

CHANGE_PATTERNS = [
    r"change my name to\s+([A-Za-z][A-Za-z\-\s']{1,40})",
]

def _clean_name(name: str) -> str:
    name = name.strip().strip(".,!?:;\"'()[]{}")
    # Tile
    if re.search(r"[A-Za-z]", name):
        name = " ".join([w.capitalize() for w in name.split()])
    return name

def _extract_name(user_input: str):
    text = user_input.lower()
    for pat in NAME_PATTERNS:
        m = re.search(pat, user_input, flags=re.IGNORECASE)
        if m:
            return _clean_name(m.group(1))
    return None

def get_response(user_input: str, context: ChatContext, threshold: float = 0.0):
    # change name
    for pat in CHANGE_PATTERNS:
        m = re.search(pat, user_input, flags=re.IGNORECASE)
        if m:
            new_name = _clean_name(m.group(1))
            context.user_name = new_name
            return f"Got it. I’ll call you {new_name} from now on.", 1.0

    # forget name
    for pat in FORGET_PATTERNS:
        if re.search(pat, user_input, flags=re.IGNORECASE):
            had = context.is_named()
            context.user_name = None
            return ("Okay, I’ve forgotten your name." if had
                    else "I hadn’t saved a name yet, but okay."), 1.0

    # ask for name
    for pat in ASK_NAME_PATTERNS:
        if re.search(pat, user_input, flags=re.IGNORECASE):
            if context.is_named():
                return f"Your name is {context.user_name}.", 1.0
            return "I don't know yet—what should I call you?", 1.0

    name = _extract_name(user_input)
    if name:
        context.user_name = name
        return f"Nice to meet you, {name}! I’ll remember that.", 1.0

    # ask for name
    if not context.is_named():
        return "What should I call you?", 1.0

    return f"Hi {context.user_name}! What can I do for you?", 1.0
