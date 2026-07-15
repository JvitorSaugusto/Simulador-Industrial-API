from time import timezone

from datetime import datetime, timezone, timedelta

from enums.factory_enums import MachineStatusEnum, ProductionOrderEnum
from errors.exceptions import NotFoundException

import random

from sqlalchemy.ext.asyncio import AsyncSession
from models.production_order_model import ProductionOrderModel
from schemas.production_order_schema import ProductionOrderRequestSchema
from services.machine_service import MachineService
from services.production_order_service import ProductionOrderService


MOCK_PRODUCTION_ORDERS = [
    {
        "product_name": "Motor Elétrico Industrial X1",
        "quantity_planned": 500,
        "hours_to_complete": 8  
    },
    {
        "product_name": "Eixo de Transmissão Aço 1045",
        "quantity_planned": 1200,
        "hours_to_complete": 12
    },
    {
        "product_name": "Placa de Controle CNC v4",
        "quantity_planned": 800,
        "hours_to_complete": 6
    },
    {
        "product_name": "Sensor de Presença Óptico",
        "quantity_planned": 1500,
        "hours_to_complete": 10
    },
    {
        "product_name": "Gabinete Metálico Blindado",
        "quantity_planned": 350,
        "hours_to_complete": 16
    },
    {
        "product_name": "Suporte de Fixação Universal",
        "quantity_planned": 2000,
        "hours_to_complete": 24
    },
    {
        "product_name": "Cabo de Conexão Blindado 5m",
        "quantity_planned": 3000,
        "hours_to_complete": 18
    }
]

class ProductionOrderSimulator:
    def __init__(self, db: AsyncSession, machineService: MachineService, op_service: ProductionOrderService):
        self.db = db
        self.machineService = machineService
        self.op_service = op_service
        
    def _analyze_pieces(self, op: ProductionOrderModel, cycle_pieces):
            op.quantity_produced += cycle_pieces
            op.quantity_bad = random.randint(0, cycle_pieces)
            op.quantity_good = op.quantity_produced - op.quantity_bad               
      
                
    async def process_op_state(self, op_id, line_id, cycle_pieces) -> bool:
        op = await self.db.get(ProductionOrderModel, op_id)
        if not op:
            raise NotFoundException("Ordem de Produção")
        
        machines = await self.machineService.get_all_machines_by_line(line_id)
        machines_list = list(machines)

        if all(m.status == MachineStatusEnum.PRODUCTION for m in machines_list):
            op.status = ProductionOrderEnum.PRODUCTION
        else:
            op.status = ProductionOrderEnum.STOP
            return False
            
        self._analyze_pieces(op, cycle_pieces)
            
        if op.quantity_produced >= op.quantity_planned:
            op.status = ProductionOrderEnum.FINISHED 
            return True
        
        return False
        
    async def generate_op_mock(self, line_id):
        order_template = random.choice(MOCK_PRODUCTION_ORDERS)
        now = datetime.now(timezone.utc)
        
        payload = ProductionOrderRequestSchema(
            product_name=order_template["product_name"],
            quantity_planned=order_template["quantity_planned"],
            planned_start=now,
            planned_end=now + timedelta(hours=order_template["hours_to_complete"]),
            production_line_id=line_id
        )
        
        op = await self.op_service.create_op(payload)
        
        return op