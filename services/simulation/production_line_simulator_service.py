import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.production_order_model import ProductionOrderModel
from schemas.production_line_schema import ProductionLineRequestSchema
from services.production_line_service import ProductionLineService
from models.production_line_model import ProductionLineModel

MOCK_PRODUCTION_LINES = [
    # --- Setor de Metalmecânica & Motores (Ciclos mais lentos, peças complexas) ---
    {
        "name": "Linha de Usinagem e Motores - Setor Bloco",
        "ideal_production_rate": 45.0,  # 45 peças por hora (~0.75 peças/min)
        "description": "Linha dedicada à retificação e usinagem de alta precisão de blocos de motores.",
    },
    {
        "name": "Linha de Estamparia e Soldagem Pesada - Célula B",
        "ideal_production_rate": 90.0,  # 90 peças por hora (1.5 peças/min)
        "description": "Estamparia robotizada e montagem de componentes estruturais em aço.",
    },
    # --- Setor de Eletrônicos & Placas (Ciclos rápidos, alta tecnologia) ---
    {
        "name": "Linha de Montagem SMT - Placas Eletrônicas",
        "ideal_production_rate": 300.0,  # 300 placas por hora (5 placas/min)
        "description": "Inserção automática de componentes em placas de circuito impresso com inspeção óptica integrada.",
    },
    {
        "name": "Linha de Integração e Teste de Dispositivos - Setor C",
        "ideal_production_rate": 180.0,  # 180 peças por hora (3 peças/min)
        "description": "Montagem final de gabinetes de controle, gravação de firmware e testes funcionais analógicos.",
    },
    # --- Setor de Injeção Plástica & Montagem Leve ---
    {
        "name": "Linha de Injeção e Acabamento Termoplástico",
        "ideal_production_rate": 240.0,  # 240 peças por hora (4 peças/min)
        "description": "Moldagem por injeção plástica de alta velocidade de peças técnicas e acabamento superficial.",
    },
    {
        "name": "Linha de Montagem de Sensores de Fluxo",
        "ideal_production_rate": 150.0,  # 150 sensores por hora (2.5 peças/min)
        "description": "Linha dedicada à calibração, montagem final e embalagem de sensores de medição industrial.",
    },
    # --- Setor de Embalagem e Envase (Ciclos ultrarrápidos) ---
    {
        "name": "Linha de Envase e Rotulagem Automatizada - Área Verde",
        "ideal_production_rate": 600.0,  # 600 unidades por hora (10 peças/min)
        "description": "Dosagem volumétrica automatizada de líquidos, fechamento de tampas e rotulagem em alta velocidade.",
    },
]


class LineSimulator:
    def __init__(self, db: AsyncSession, line_service: ProductionLineService):
        self.db = db
        self.line_service = line_service

    async def generate_line_mock(self, quantity_lines: int = 3):
        query = select(ProductionLineModel.name)
        result = await self.db.execute(query)
        existing_names = set(result.scalars().all())
        
        available_lines = []
        
        for line in MOCK_PRODUCTION_LINES:
            if line["name"] not in existing_names:
                available_lines.append(line)

        if not available_lines:
            raise ValueError("Todas as linhas possiveis ja foram criadas")
        
        # nesse fluxo atual n vou poder usa o for das linhas la no simulator service
        
        num_lines_to_create = min(quantity_lines, len(available_lines))
        
        selected_lines = random.sample(available_lines, num_lines_to_create)
        
        created_lines = []

        for line_data in selected_lines:
            payload = ProductionLineRequestSchema(
                name=line_data["name"],
                description=line_data["description"],
                target_oee=85.00,
                ideal_production_rate=line_data["ideal_production_rate"],
            )

            line = await self.line_service.create_production_line(payload)
            created_lines.append(line)

        return created_lines
