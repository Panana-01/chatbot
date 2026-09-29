# modules/kitchen_inventory.py
import re

DEFAULT_UNIT = "pcs"  # default unit


def _normalise_unit(unit: str | None) -> str:
    if not unit:
        return DEFAULT_UNIT
    unit = unit.strip().lower()
    if unit in ["l", "lt", "liter", "litre"]:
        return "L"
    if unit in ["ml", "milliliter", "millilitre"]:
        return "ml"
    if unit in ["kg", "kilogram"]:
        return "kg"
    if unit in ["g", "gram"]:
        return "g"
    return unit.upper()


def _normalise_item_name(item: str) -> str:
    """
    单复数统一：

    """
    item = item.strip().lower()
    if not item:
        return item

    parts = item.split()
    last = parts[-1]
    if last.endswith("s") and not last.endswith("ss"):
        last = last[:-1]
    parts[-1] = last
    return " ".join(parts)


def _format_amount(amount: float) -> str:
    if amount.is_integer():
        return str(int(amount))
    return str(amount)


def _ensure_item(inv, item: str):
    if item not in inv:
        inv[item] = {}


def _apply_removal(inv, item: str, unit: str, amount: float):
    """真正执行删除逻辑的辅助函数。"""
    if item not in inv:
        return f"You don't have any {item} in your inventory.", 1.0

    if unit not in inv[item]:
        existing_units = ", ".join(inv[item].keys())
        return (
            f"You don't have {item} with unit '{unit}'. "
            f"You currently have units: {existing_units}.",
            1.0,
        )

    inv[item][unit] -= amount
    amount_str = _format_amount(amount)

    if inv[item][unit] <= 0:
        del inv[item][unit]
        if not inv[item]:
            del inv[item]
        if unit == DEFAULT_UNIT:
            return f"OK, I removed {amount_str} {item}. You don't have any {item} now.", 1.0
        else:
            return (
                f"OK, I removed {amount_str} {unit} {item}. "
                f"You don't have any {unit} {item} now.",
                1.0,
            )
    else:
        remaining_str = _format_amount(inv[item][unit])
        if unit == DEFAULT_UNIT:
            return (
                f"OK, I removed {amount_str} {item}. "
                f"You still have {remaining_str} {item} left.",
                1.0,
            )
        else:
            return (
                f"OK, I removed {amount_str} {unit} {item}. "
                f"You still have {remaining_str} {unit} {item} left.",
                1.0,
            )


def get_response(user_input, ctx):

    text = user_input.strip().lower()
    inv = ctx.inventory  # {item_name: {unit: amount_float}}

    # yes / no
    if ctx.pending_inventory_action is not None:
        pending = ctx.pending_inventory_action
        if text in ["yes", "y"]:
            # 用户确认执行删除
            if pending["type"] == "remove":
                item = pending["item"]
                unit = pending["unit"]
                amount = pending["amount"]
                ctx.pending_inventory_action = None  # 清空 pending
                return _apply_removal(inv, item, unit, amount)
        elif text in ["no", "n", "cancel"]:
            ctx.pending_inventory_action = None
            return "OK, I cancelled that removal.", 1.0
        # 其他输入就继续往下，当作新指令

    # 显示库存
    if any(kw in text for kw in ["show", "list", "inventory", "what do i have", "what's in my kitchen"]):
        if not inv:
            return "Your kitchen inventory is currently empty.", 1.0
        lines = []
        for item, units in inv.items():
            for unit, amount in units.items():
                amount_str = _format_amount(amount)
                if unit == DEFAULT_UNIT:
                    lines.append(f"- {item}: {amount_str}")
                else:
                    lines.append(f"- {item}: {amount_str} {unit}")
        reply = "Here is your kitchen inventory:\n" + "\n".join(lines)
        return reply, 1.0

    # add item
    if text.startswith("add"):
        match = re.match(r"add\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s+(.+)", text)
        if match:
            amount = float(match.group(1))
            unit = _normalise_unit(match.group(2))
            item_raw = match.group(3).strip()
            item = _normalise_item_name(item_raw)

            _ensure_item(inv, item)
            inv[item][unit] = inv[item].get(unit, 0.0) + amount

            amount_str = _format_amount(amount)
            total_str = _format_amount(inv[item][unit])
            if unit == DEFAULT_UNIT:
                return (
                    f"OK, I added {amount_str} {item} to your inventory. "
                    f"Now you have {total_str} {item}.",
                    1.0,
                )
            else:
                return (
                    f"OK, I added {amount_str} {unit} {item} to your inventory. "
                    f"Now you have {total_str} {unit} {item}.",
                    1.0,
                )
        else:
            return (
                "Please say something like:\n"
                "- 'Add 2 eggs'\n"
                "- 'Add 1L milk'\n"
                "- 'Add 1 kg chicken breasts'",
                0.7,
            )

    # remove / delete
    if text.startswith("remove") or text.startswith("delete"):
        match = re.match(r"(remove|delete)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s+(.+)", text)
        if match:
            amount = float(match.group(2))
            unit_raw = match.group(3)
            item_raw = match.group(4).strip()
            item = _normalise_item_name(item_raw)

            if item not in inv:
                return f"You don't have any {item} in your inventory.", 1.0

            # 如果没写单位且只有一种单位就自动填
            if unit_raw is None:
                units_for_item = list(inv[item].keys())
                if len(units_for_item) == 1:
                    unit = units_for_item[0]
                else:
                    existing_units = ", ".join(units_for_item)
                    return (
                        f"{item} has multiple units ({existing_units}). "
                        f"Please specify which unit you want to remove.",
                        1.0,
                    )
            else:
                unit = _normalise_unit(unit_raw)

            amount_str = _format_amount(amount)
            if unit == DEFAULT_UNIT:
                confirm_text = (
                    f"Do you want to remove {amount_str} {item} from your inventory? "
                    f"Please type 'yes' or 'no'."
                )
            else:
                confirm_text = (
                    f"Do you want to remove {amount_str} {unit} {item} from your inventory? "
                    f"Please type 'yes' or 'no'."
                )

            ctx.pending_inventory_action = {
                "type": "remove",
                "item": item,
                "unit": unit,
                "amount": amount,
            }
            return confirm_text, 1.0
        else:
            return (
                "Please say something like:\n"
                "- 'Remove 1L milk'\n"
                "- 'Remove 1 kg chicken breasts'\n"
                "- 'Remove 2 eggs'",
                0.7,
            )

    # help
    help_msg = (
        "I can help you manage your kitchen inventory. Try commands like:\n"
        "- 'Add 2 eggs'\n"
        "- 'Add 1L milk'\n"
        "- 'Add 1 kg chicken breasts'\n"
        "- 'Remove 1L milk'\n"
        "- 'Show my kitchen inventory'"
    )
    return help_msg, 0.5
