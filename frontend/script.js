// Função para alternar o tema
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Função para buscar dados do backend
async function fetchDashboardData() {
    try {
        // Exemplo de chamada para o endpoint de snapshot (ajuste conforme necessário)
        const response = await fetch('http://localhost:8000/dashboard/1');
        const data = await response.json();
        
        // Atualizar dados da OP
        const opCard = document.getElementById('op-data');
        if (data.active_op) {
            opCard.innerHTML = `
                <h3>${data.active_op.code}</h3>
                <p>Produto: ${data.active_op.product_name}</p>
                <p>Planejado: ${data.active_op.quantity_planned} unidades</p>
                <p>Produzido: ${data.active_op.quantity_produced} unidades</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${data.active_op.progress_percentage}%"></div>
                </div>
                <p>Progresso: ${data.active_op.progress_percentage}%</p>
            `;
        }
        
        // Atualizar dados das máquinas
        if (data.machines && data.machines.length > 0) {
            data.machines.forEach(machine => {
                const machineCard = document.getElementById(`machine-${machine.id}`);
                if (machineCard) {
                    // Remover classes de status anteriores
                    machineCard.className = 'machine-card';
                    
                    // Adicionar classe de status baseada no status da máquina
                    switch(machine.status) {
                        case 'production':
                            machineCard.classList.add('status-production');
                            break;
                        case 'idle':
                            machineCard.classList.add('status-idle');
                            break;
                        case 'maintenance':
                            machineCard.classList.add('status-maintenance');
                            break;
                        default:
                            machineCard.classList.add('status-idle');
                    }
                    
                    machineCard.innerHTML = `
                        <h3>${machine.name}</h3>
                        <p>Status: ${machine.status}</p>
                        <p>Última inicialização: ${machine.last_start_time || 'N/A'}</p>
                        <p>Nível de desgaste: ${machine.wear_level}%</p>
                    `;
                }
            });
        }
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
    }
}

// Aplicar o tema salvo ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
    
    // Adicionar evento ao botão de toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Chamar a função a cada 5 segundos
    setInterval(fetchDashboardData, 5000);
    
    // Chamar uma vez imediatamente
    fetchDashboardData();
});