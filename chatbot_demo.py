from modules.intent_management import match_intent
from modules.small_talk import get_response as small_talk_response
from modules.question_answer import get_response as qa_response
from modules.identity_management import get_response as id_response
from modules.discoverability import get_response as disco_response
from modules.context import ChatContext
from modules.kitchen_inventory import get_response as ki_response

_default_context = ChatContext()

GREETING = "Hi, I'm Venem. How can I help you?"
CLI_EXIT_HINT = " Type 'exit' or 'quit' to quit."

HELP_WORDS = {"help", "menu", "how to use", "what can you do?","what can you do"}

def chatbot_response(user_input, context=None):
    ctx = _default_context if context is None else context
    user_lower = user_input.strip().lower()

    # 如果厨房模块有未确认的操作，优先交给 kitchen_inventory 处理
    if getattr(ctx, "pending_inventory_action", None) is not None \
       and ctx.last_intent == "kitchen_inventory":
        ctx.reset_fail()
        reply, sim = ki_response(user_input, ctx)
        if ctx.is_named():
            reply = f"{ctx.user_name}, {reply}"
        return reply, sim

    intent, sim_intent = match_intent(user_input)

    if user_lower in HELP_WORDS:
        ctx.last_intent = "discoverability"
        ctx.reset_fail()
        reply, sim = disco_response(user_input, ctx)
        return reply, sim

    # identity
    if intent == "identity_management":
        ctx.last_intent = "identity_management"
        ctx.reset_fail()
        reply, sim = id_response(user_input, ctx)
        return reply, sim

    # Kitchen inventory
    if intent == "kitchen_inventory":
        ctx.last_intent = "kitchen_inventory"
        ctx.reset_fail()
        reply, sim = ki_response(user_input, ctx)
        if ctx.is_named():
            reply = f"{ctx.user_name}, {reply}"
        return reply, sim

    # Small talk
    reply, sim_small = small_talk_response(user_input)
    if reply:
        ctx.reset_fail()
        ctx.last_intent = "small_talk"
        if ctx.is_named():
            reply = f"{ctx.user_name}, {reply}"
        return reply, sim_small

    # discoverability
    if intent == "discoverability":
        ctx.last_intent = "discoverability"
        ctx.reset_fail()
        reply, sim = disco_response(user_input, ctx)
        return reply, sim

    # QA
    reply, sim_qa = qa_response(user_input)
    if reply:
        ctx.reset_fail()
        ctx.last_intent = "question_answer"
        if ctx.is_named():
            reply = f"{ctx.user_name}, {reply}"
        return reply, sim_qa




    ctx.fail_count += 1
    if ctx.fail_count >= 2:
        # two times
        ctx.last_intent = "discoverability"
        return (
            "I didn’t quite get that."
            + "\nType 'help' to see everything I can do."
        ), 0.0
    return "Sorry, I didn’t quite understand that.", 0.0


if __name__ == "__main__":
    print(f"Bot:{GREETING}{CLI_EXIT_HINT}")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye!")
            break
        reply, sim = chatbot_response(user_input)
        print(f"Bot: {reply}")