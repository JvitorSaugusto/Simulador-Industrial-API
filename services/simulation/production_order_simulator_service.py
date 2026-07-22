from datetime import datetime, timezone, timedelta

from sqlalchemy import or_, select

from enums.factory_enums import MachineStatusEnum, ProductionOrderEnum
from errors.exceptions import NotFoundException

import random

from sqlalchemy.ext.asyncio import AsyncSession
from models.production_order_model import ProductionOrderModel
from schemas.production_order_schema import ProductionOrderRequestSchema
from services.machine_service import MachineService
from services.production_order_service import ProductionOrderService
from services.simulation.machine_simulator_service import MachineSimulator


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
    def __init__(self, db: AsyncSession, machine_service: MachineService, op_service: ProductionOrderService, machine_simulator: MachineSimulator):
        self.db = db
        self.machine_service = machine_service
        self.op_service = op_service
        self.machine_simulator = machine_simulator
        
    def _analyze_pieces(self, op: ProductionOrderModel, cycle_pieces):
            op.quantity_produced += cycle_pieces
            op.quantity_bad = random.randint(0, cycle_pieces)
            op.quantity_good = op.quantity_produced - op.quantity_bad            
            
    async def _start_op(self, line_id):
        query = (select(ProductionOrderModel)
        .where(ProductionOrderModel.production_line_id == line_id, ProductionOrderModel.planned_start >= datetime.now(timezone.utc))
        .order_by(ProductionOrderModel.planned_start.asc())
        )
        
        result = await self.db.execute(query)
        op = result.scalars().first()

        if op is None:
            raise NotFoundException("op")
        
        
        if op.planned_start <= datetime.now(timezone.utc):
            op.status = ProductionOrderEnum.PRODUCTION
        
            
                
    async def process_op_state(self, op_id, line_id, cycle_pieces) -> bool:
        op = await self.db.get(ProductionOrderModel, op_id)
        if not op:
            raise NotFoundException("Ordem de Produção")
        
        machines = await self.machine_service.get_all_machines_by_line(line_id)
        machines_list = list(machines)

        # isso tem q mudar, tenho que checar se existe alguma maquina parada ao inves de todas n estarem com status produzindo, pq se n 
        # pode ocorrer problema com outros estados de maquina por exemplo o IDLE
        for machine in machines_list:
            if machine.status == MachineStatusEnum.IDLE:
                return False
        
        if not all(m.status == MachineStatusEnum.PRODUCTION for m in machines_list):
            op.status = ProductionOrderEnum.STOP
            return False
            
        self._analyze_pieces(op, cycle_pieces)
            
        if op.quantity_produced >= op.quantity_planned:
            op.status = ProductionOrderEnum.FINISHED
            op.actual_end =  datetime.now(timezone.utc)
            return True
        
        return False
    
    async def start_op(self, line_id):
        query = (select(ProductionOrderModel)
        .where(ProductionOrderModel.production_line_id == line_id, ProductionOrderModel.status == ProductionOrderEnum.PENDING, ProductionOrderModel.planned_start <= datetime.now(timezone.utc))
        .order_by(ProductionOrderModel.planned_start.asc())
        )
        
        result = await self.db.execute(query)
        op = result.scalars().first()
        
        if op is None:
            return
     
        if random.random() < 0.80:
            op.status = ProductionOrderEnum.PRODUCTION
            op.actual_start =  datetime.now(timezone.utc)
            
            await self.machine_simulator.start_all_machines(line_id)
    
        
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
    
    async def _append_to_op_backlog(self, line_id, planned_start):
        order_template = random.choice(MOCK_PRODUCTION_ORDERS)
        
        payload = ProductionOrderRequestSchema(
            product_name=order_template["product_name"],
            quantity_planned=order_template["quantity_planned"],
            planned_start=planned_start,
            planned_end=planned_start + timedelta(hours=order_template["hours_to_complete"]),
            production_line_id=line_id
        )
        
        op = await self.op_service.create_op(payload)
        
        return op
    
    async def auto_generate_ops_backlog(self, line_id):
        query = (select(ProductionOrderModel)
        .where(ProductionOrderModel.production_line_id == line_id, or_(ProductionOrderModel.status == ProductionOrderEnum.PENDING, ProductionOrderModel.status == ProductionOrderEnum.PRODUCTION))
        .order_by(ProductionOrderModel.planned_end.asc())
        )
        result = await self.db.execute(query)
        ops = result.scalars().all()
        
        if len(ops) < 3:
            ops_list = list(ops)
            
            for _ in range(3 - len(ops_list)):
                if not ops_list:
                    last_op_date = datetime.now(timezone.utc)
                else:
                    last_op = ops_list[-1]
                    last_op_date = last_op.planned_end
                
                planned_start = last_op_date + timedelta(hours=random.randint(0, 2))
                new_op = await self._append_to_op_backlog(line_id, planned_start=planned_start)
                ops_list.append(new_op)