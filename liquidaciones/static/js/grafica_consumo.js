document.addEventListener('DOMContentLoaded', function() {
    const data = window.datosGraficas || {};
    
    // BLINDAJE: Si los arreglos están vacíos, ponemos datos falsos en cero 
    // para forzar a Chart.js a dibujar el lienzo (canvas)
    const labels = (data.labelsLinea && data.labelsLinea.length > 0) ? data.labelsLinea : ['Sin registros'];
    const datosActiva = (data.datosActiva && data.datosActiva.length > 0) ? data.datosActiva : [0];
    const datosReactiva = (data.datosReactiva && data.datosReactiva.length > 0) ? data.datosReactiva : [0];
    
    // Para el boxplot, si no hay datos, creamos 24 campos vacíos
    const boxplotData = (data.boxplotData && data.boxplotData.length > 0) ? data.boxplotData : Array(24).fill(null);

    // CONFIGURACIÓN DE TEMA
    const isDark = document.documentElement.classList.contains('dark');
    const textColor = isDark ? '#a1a1aa' : '#64748b'; 
    const gridColor = isDark ? 'rgba(63, 63, 70, 0.3)' : 'rgba(226, 232, 240, 0.8)';
    const tooltipBg = isDark ? 'rgba(24, 24, 27, 0.95)' : 'rgba(255, 255, 255, 0.95)';
    const tooltipTitle = isDark ? '#ffffff' : '#0f172a';
    const tooltipBody = isDark ? '#e4e4e7' : '#334155';
    const borderColor = isDark ? 'rgba(63, 63, 70, 0.8)' : 'rgba(203, 213, 225, 0.8)';

    Chart.defaults.color = textColor;
    Chart.defaults.font.family = "'Raleway', 'sans-serif'";
    Chart.defaults.font.weight = '600';

    // 1. GRÁFICA DE BARRAS
    const ctxBar = document.getElementById('graficaConsumoDiario');
    if (ctxBar) {
        new Chart(ctxBar.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Energía Activa (kWh)',
                    data: datosActiva,
                    backgroundColor: '#10b981',
                    hoverBackgroundColor: '#34d399',
                    borderRadius: 4
                }, {
                    label: 'Energía Reactiva (kVArh)',
                    data: datosReactiva,
                    backgroundColor: isDark ? '#3f3f46' : '#94a3b8',
                    hoverBackgroundColor: isDark ? '#52525b' : '#cbd5e1',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { beginAtZero: true, grid: { color: gridColor, drawBorder: false }, ticks: { padding: 10 } },
                    x: { grid: { display: false, drawBorder: false }, ticks: { padding: 10 } }
                },
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true, padding: 20, boxWidth: 8 } },
                    tooltip: {
                        backgroundColor: tooltipBg, titleColor: tooltipTitle, bodyColor: tooltipBody,
                        borderColor: borderColor, borderWidth: 1, padding: 12, usePointStyle: true
                    }
                }
            }
        });
    }

    // 2. GRÁFICA BOX PLOT
    const ctxBox = document.getElementById('boxplotChart');
    if (ctxBox) {
        const horasLabels = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);

        new Chart(ctxBox.getContext('2d'), {
            type: 'boxplot',
            data: {
                labels: horasLabels,
                datasets: [{
                    label: 'Consumo Activo (kWh)',
                    data: boxplotData, 
                    backgroundColor: isDark ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.1)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    outlierBackgroundColor: '#ef4444',
                    outlierBorderColor: '#ef4444',
                    outlierRadius: 3,
                    itemRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: tooltipBg, titleColor: tooltipTitle, bodyColor: tooltipBody,
                        borderColor: borderColor, borderWidth: 1, padding: 12,
                        callbacks: {
                            label: function (context) {
                                const stats = context.raw;
                                if (!stats) return 'Sin datos en esta hora';
                                return [
                                    `Máximo: ${stats.max.toFixed(2)} kWh`,
                                    `Q3 (75%): ${stats.q3.toFixed(2)} kWh`,
                                    `Mediana: ${stats.median.toFixed(2)} kWh`,
                                    `Q1 (25%): ${stats.q1.toFixed(2)} kWh`,
                                    `Mínimo: ${stats.min.toFixed(2)} kWh`
                                ];
                            }
                        }
                    }
                },
                onClick: (event, elements, chart) => {
                    if (elements.length > 0) {
                        const el = elements[0];
                        const stats = chart.data.datasets[el.datasetIndex].data[el.index];
                        if (stats) {
                            const panel = document.getElementById('boxplotDetails');
                            panel.classList.remove('hidden');
                            panel.classList.add('animate-fade-in');
                            document.getElementById('bp-hora').textContent = horasLabels[el.index];
                            document.getElementById('bp-max').textContent = stats.max.toFixed(2);
                            document.getElementById('bp-q3').textContent = stats.q3.toFixed(2);
                            document.getElementById('bp-med').textContent = stats.median.toFixed(2);
                            document.getElementById('bp-q1').textContent = stats.q1.toFixed(2);
                            document.getElementById('bp-min').textContent = stats.min.toFixed(2);
                        }
                    }
                },
                onHover: (event, elements) => {
                    event.native.target.style.cursor = elements.length ? 'pointer' : 'default';
                },
                scales: {
                    x: { grid: { display: false, drawBorder: false }, ticks: { maxRotation: 45, minRotation: 0 } },
                    y: { beginAtZero: true, grid: { color: gridColor, drawBorder: false }, title: { display: true, text: 'Consumo (kWh)', color: textColor, font: { size: 12 } } }
                }
            }
        });
    }
});