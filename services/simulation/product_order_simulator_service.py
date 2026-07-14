from enums.factory_enums import MachineStatusEnum, ProductionOrderEnum
from errors.exceptions import NotFoundException
#calcular quantas peças foram produzidas
# calcular peças boas
# calcular peças ruins
# finalizar OP quando atingir a meta
# atualizar contadores da OP


import random

from sqlalchemy.ext.asyncio import AsyncSession

from models.production_order_model import ProductionOrderModel
from services.machine_service import MachineService


class ProductionOrderSimulator:
    def __init__(self, db: AsyncSession, machineService: MachineService):
        self.db = db
        self.machineService = machineService
        
    def _produce_pieces(self, op: ProductionOrderModel):
            pieces_per_cycle = random.randint(3, 8)
            op.quantity_produced += pieces_per_cycle
            op.quantity_bad = random.randint(0, pieces_per_cycle)
            op.quantity_good = op.quantity_produced - op.quantity_bad
                
                
    async def process_op_state(self, op_id, line_id):
        op = await self.db.get(ProductionOrderModel, op_id)
        if not op:
            raise NotFoundException("Ordem de Produção")
        
        machines = await self.machineService.get_all_machines_by_line(line_id)
        machines_list = list(machines)

        if all(m.status == MachineStatusEnum.PRODUCTION for m in machines_list):
            op.status = ProductionOrderEnum.PRODUCTION
        else:
            op.status = ProductionOrderEnum.STOP
            return
            
        self._produce_pieces(op)
            
        if op.quantity_produced >= op.quantity_planned:
            op.status = ProductionOrderEnum.FINISHED
            return