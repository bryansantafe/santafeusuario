document.addEventListener('DOMContentLoaded', function () {
    // Configuración del Gráfico de Energía
    const ctx = document.getElementById('energyChart').getContext('2d');

    // Gradiente para el área bajo la curva
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(16, 185, 129, 0.4)');
    gradient.addColorStop(1, 'rgba(16, 185, 129, 0)');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:59'],
            datasets: [{
                label: 'Precio Energía ($/kWh)',
                data: [780, 740, 910, 1050, 920, 860, 800],
                borderColor: '#10b981',
                borderWidth: 3,
                pointBackgroundColor: '#10b981',
                pointRadius: 4,
                pointHoverRadius: 6,
                tension: 0.4, // Curvatura de la línea
                fill: true,
                backgroundColor: gradient,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#18181b',
                    titleColor: '#fff',
                    bodyColor: '#10b981',
                    borderColor: '#27272a',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(39, 39, 42, 0.5)', drawBorder: false },
                    ticks: { color: '#71717a', font: { size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#71717a', font: { size: 11 } }
                }
            }
        }
    });

    console.log("Sistema CAT_WIND cargado correctamente.");
});