# modules/discoverability.py

def get_response(user_input, ctx=None):
    """
    Generate a dynamic help / discoverability message.
    The content depends on the current context, e.g. whether
    the user has a saved name, has used kitchen inventory, etc.
    """

    # intruduction
    if ctx is not None and ctx.is_named():
        header = f"{ctx.user_name}, I am Venem. Here’s what I can do:\n"
    else:
        header = "I am Venem. Here’s what I can do:\n"

    # function list
    features = [
        "1. Small talk — light conversation.",
        "2. Question answering — answer questions using my QA dataset.",
        "3. Identity management — remember, change, or forget how I should address you.",
    ]

    # check kitchen list
    if ctx is not None:
        features.append(
            "4. Kitchen inventory — add, remove, and list food items with quantities and units."
        )

    # context
    extra_tips = []
    if ctx is not None:
        if ctx.last_intent == "kitchen_inventory":
            extra_tips.append(
                "For example, you can say: 'add 2 eggs', 'add 1L milk', or 'show my kitchen inventory'."
            )
        elif not ctx.is_named():
            extra_tips.append(
                "You can also tell me your name, e.g. 'my name is Alice', so I can address you personally."
            )
        else:
            extra_tips.append(
                "You can ask me general questions, or just say 'help' again to see this menu."
            )


    menu_lines = [header] + features
    if extra_tips:
        menu_lines.append("")
        menu_lines.extend(extra_tips)

    menu_text = "\n".join(menu_lines)
    return menu_text, 1.0

