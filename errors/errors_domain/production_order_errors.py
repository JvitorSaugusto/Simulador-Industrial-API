class ProductionOrderInvalidStatusException(Exception):
    def __init__(self, op_code: str):
        self.op_code = op_code