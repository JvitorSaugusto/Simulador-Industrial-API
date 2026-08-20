import logging

def setup_logging():
    # 1. Trava o logger RAIZ em WARNING para que nenhuma biblioteca externa fale por padrão
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True  # Limpa qualquer handler que o Celery tentou criar antes
    )

    # 2. Silencia explicitamente todas as bibliotecas de infraestrutura
    for lib in ["sqlalchemy.engine", "aiosqlite", "kombu", "asyncio", "urllib3"]:
        logger_lib = logging.getLogger(lib)
        logger_lib.setLevel(logging.WARNING)
        logger_lib.propagate = False  # Impede que elas enviem mensagens para o terminal

    # 3. LIBERA TUDO (DEBUG, INFO, WARNING, ERROR) APENAS PARA A SUA SIMULAÇÃO
    # Isso cobre o simulation_service e todos os outros simuladores da pasta
    logging.getLogger("services.simulation").setLevel(logging.DEBUG)
    
    # Se você tiver logs dentro de 'tasks.py' que queira ver também:
    logging.getLogger("tasks").setLevel(logging.DEBUG)