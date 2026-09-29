# modules/context.py

class ChatContext:
    def __init__(self):
        self.user_name = None
        self.last_intent = None
        self.fail_count = 0

        # 厨房库存{"eggs": {"PCS": 6}, "milk": {"L": 1.0}}
        self.inventory = {}

        #等待确认的库存操作
        #{"type": "remove", "item": "eggs", "unit": "PCS", "amount": 2.0}
        self.pending_inventory_action = None

    def reset_fail(self):
        self.fail_count = 0

    def is_named(self):
        return self.user_name is not None
