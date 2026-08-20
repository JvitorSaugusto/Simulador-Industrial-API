import random
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from enums.factory_enums import DownTimeEventTypeEnum
from services.production_line_service import ProductionLineService
from services.production_order_service import ProductionOrderService
from services.simulation.down_time_event_simulator_service import DownTimeEventSimulator
from services.simulation.machine_simulator_service import MachineSimulator
from services.simulation.production_order_simulator_service import ProductionOrderSimulator
from services.simulation.production_line_simulator_service import LineSimulator


logger = logging.getLogger(__name__)

#maestro dos outros simulators services
class SimulationOrchestrator:
    def __init__(self, db: AsyncSession, op_service: ProductionOrderService, op_simulator: ProductionOrderSimulator, machine_simulator: MachineSimulator, line_simulator: LineSimulator, line_service: ProductionLineService, down_time_simulator: DownTimeEventSimulator):
        self.db = db
        self.op_service = op_service
        self.op_simulator = op_simulator
        self.machine_simulator = machine_simulator
        self.line_simulator = line_simulator
        self.line_service = line_service
        self.down_time_simulator = down_time_simulator

    async def initialize_simulation(self, quantity_lines: int, machines_per_line: int, auto_generate_op: bool):
        logger.info("Iniciando inicialização da simulação (quantity_lines=%s, machines_per_line=%s, auto_generate_op=%s)", quantity_lines, machines_per_line, auto_generate_op,)
        created_lines = await self.line_simulator.generate_line_mock(quantity_lines)
        logger.info("Linhas mockadas criadas (total=%s)", len(created_lines))
        
        for line in created_lines:
            created_machines = await self.machine_simulator.generate_machine_mock(line.id, machines_per_line)
            logger.debug("Máquinas mockadas criadas para a linha (line_id=%s, total=%s)", line.id, len(created_machines))
            
            if auto_generate_op:
                op = await self.op_simulator.generate_op_mock(line.id)
                logger.debug("OP mockada criada para a linha (line_id=%s, op_id=%s)", line.id, op.id)
        
        logger.info("Inicialização da simulação finalizada com sucesso")
        
    async def start_simulation_line(self, line_id, auto_generate: bool):
        logger.info("Iniciando linha de produção (line_id=%s, auto_generate=%s)", line_id, auto_generate)
        
        await self.line_simulator.start_line(line_id)
        logger.debug("Status da linha alterado para RUNNING (line_id=%s)", line_id)
        
        await self.machine_simulator.start_all_machines(line_id)
        logger.debug("Máquinas da linha ligadas (line_id=%s)", line_id)
        
        active_op = await self.op_service.get_active_op_by_line(line_id=line_id)
        
        if not active_op:
            if auto_generate:
                logger.info("Nenhuma OP ativa encontrada, gerando OP automática (line_id=%s)", line_id)
                await self.op_simulator.generate_op_mock(line_id)
            else:
                logger.warning("Linha iniciada sem OP ativa e sem geração automática (line_id=%s)", line_id)
        else:
            logger.debug("OP ativa já existente encontrada para a linha (line_id=%s, op_id=%s)", line_id, active_op.id)

            
    async def process_factory_tick(self):
        """
        Executado pelo Celery a cada X segundos.

        Responsável por percorrer todas as linhas em execução e
        delegar o processamento aos simuladores especializados.
        """

        running_lines = await self.line_service.get_running_lines()

        if not running_lines:
            logger.debug("Nenhuma linha em execução encontrada durante o tick")
            return
        
        logger.debug("Linhas em execução encontradas para processamento (total=%s)", len(running_lines),)

        for line in running_lines:
            active_op = await self.op_service.get_active_op_by_line(line.id)
            op_id = active_op.id if active_op else None

            await self.machine_simulator.process_machine_states(line_id=line.id, op_id=op_id,)
            logger.debug("Processando estados das máquinas (line_id=%s, op_id=%s)", line.id, op_id,)
            
            cycle_pieces = await self.line_simulator.process_line_production(line)
            logger.debug("Produção calculada no ciclo (line_id=%s, cycle_pieces=%s)", line.id, cycle_pieces,)

            if active_op:              
                finished_op = await self.op_simulator.process_op_state(line_id=line.id, op_id=op_id, cycle_pieces=cycle_pieces)
                
                if finished_op:
                    logger.info("Ordem de Produção finalizada (op_id=%s, line_id=%s)", op_id,line.id,)
                    
                    if random.random() > 0.20: #chance das maquina não desligarem no fim de uma op
                        logger.debug("Colocando máquinas em IDLE após término de OP (line_id=%s)", line.id,)
                        await self.machine_simulator.idle_all_machines(line.id)
                    else:
                        logger.warning("Simulação manteve máquinas ligadas após término da OP (line_id=%s)", line.id,)
                
            else:
                logger.warning("Linha em execução sem OP ativa. Registrando evento de parada (line_id=%s)", line.id,)
                await self.down_time_simulator.generate_event(line_id=line.id, type=DownTimeEventTypeEnum.UNDEFINED_PRODUCTION)
                logger.debug("Evento de produção indefinida registrado (line_id=%s)", line.id)
                
                if random.random() > 0.20: #chance de adiar o inicio de uma op, simulando atrasos
                    logger.info("Iniciando OP e encerrando evento de parada na linha (line_id=%s)", line.id,)
                    
                    await self.op_simulator.start_op(line.id)
                    await self.down_time_simulator.close_active_event(line.id)
                    logger.debug("Evento de parada encerrado após início da OP (line_id=%s)", line.id)
                else:
                    logger.warning("Simulando atraso estocástico no início da próxima OP (line_id=%s)", line.id,)
                    
                logger.debug("Gerando backlog automático de OPs para a linha (line_id=%s)", line.id,)
                await self.op_simulator.auto_generate_ops_backlog(line.id)
                logger.debug("Backlog automático de OPs gerado com sucesso (line_id=%s)", line.id)
         
        await self.db.commit()
        logger.info("Ciclo do tick da fábrica finalizado com sucesso")