
class NotFoundException(Exception):
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        super().__init__(f"{resource_name} não encontrado(a).")
