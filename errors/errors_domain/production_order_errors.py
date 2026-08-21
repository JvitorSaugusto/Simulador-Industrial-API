class ProductionOrderInvalidStatusException(Exception):
    def __init__(self, op_code: str):
        self.op_code = op_code
        super().__init__(f"Status inválido para a Ordem de Produção: {op_code}")