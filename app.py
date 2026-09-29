import streamlit as st

from chatbot_demo import GREETING, chatbot_response
from modules.context import ChatContext
from modules.kitchen_inventory import DEFAULT_UNIT, _format_amount

PAGE_TITLE = "Venem"
NEW_CONVERSATION_LABEL = "New conversation"
SESSION_HEADING = "This session"
NAME_LABEL = "Name"
INVENTORY_LABEL = "Inventory"
EMPTY_INVENTORY_TEXT = "Empty"
UNNAMED_TEXT = "Not set yet"
CHAT_PLACEHOLDER = "Type a message"


def _inventory_lines(inventory: dict) -> list[str]:
    lines = []
    for item, units in inventory.items():
        for unit, amount in units.items():
            amount_text = _format_amount(amount)
            if unit == DEFAULT_UNIT:
                lines.append(f"- {item}: {amount_text}")
            else:
                lines.append(f"- {item}: {amount_text} {unit}")
    return lines


def _render_message(content: str) -> None:
    st.markdown(content.replace("\n", "  \n"))


def _reset_session() -> None:
    st.session_state.ctx = ChatContext()
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]


st.set_page_config(page_title=PAGE_TITLE, page_icon="💬", layout="centered")

if "ctx" not in st.session_state or "messages" not in st.session_state:
    _reset_session()

st.title(PAGE_TITLE)

with st.sidebar:
    st.header(SESSION_HEADING)
    ctx = st.session_state.ctx
    st.write(f"**{NAME_LABEL}:** {ctx.user_name if ctx.is_named() else UNNAMED_TEXT}")
    st.write(f"**{INVENTORY_LABEL}**")
    inventory_lines = _inventory_lines(ctx.inventory)
    if inventory_lines:
        st.markdown("\n".join(inventory_lines))
    else:
        st.write(EMPTY_INVENTORY_TEXT)
    if st.button(NEW_CONVERSATION_LABEL):
        _reset_session()
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        _render_message(message["content"])

prompt = st.chat_input(CHAT_PLACEHOLDER)
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply, _similarity = chatbot_response(prompt, context=st.session_state.ctx)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
