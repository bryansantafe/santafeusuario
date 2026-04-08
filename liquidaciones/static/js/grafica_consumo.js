document.addEventListener('DOMContentLoaded', function () {
    // Configuración global de Chart.js para un diseño oscuro moderno
    Chart.defaults.color = '#a1a1aa';
    Chart.defaults.font.family = "'Inter', 'system-ui', 'sans-serif'";

    // --------------------------------------------------------
    // 1. GRÁFICA ORIGINAL (BARRAS - ENERGÍA ACTIVA/REACTIVA)
    // --------------------------------------------------------
    const canvas = document.getElementById('graficaConsumoDiario');

    if (canvas) {
        const labels = JSON.parse(canvas.dataset.labels || '[]');
        const dataActiva = JSON.parse(canvas.dataset.activa || '[]');
        const dataReactiva = JSON.parse(canvas.dataset.reactiva || '[]');

        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Energía Activa (kWh)',
                    data: dataActiva,
                    backgroundColor: '#10b981', // emerald-500
                    hoverBackgroundColor: '#34d399', // emerald-400
                    borderRadius: 6,
                    borderSkipped: false
                }, {
                    label: 'Energía Reactiva (kVArh)',
                    data: dataReactiva,
                    backgroundColor: '#3f3f46', // zinc-700
                    hoverBackgroundColor: '#52525b', // zinc-600
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(63, 63, 70, 0.4)', drawBorder: false },
                        ticks: { padding: 10 }
                    },
                    x: {
                        grid: { display: false, drawBorder: false },
                        ticks: { padding: 10 }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { usePointStyle: true, padding: 20, boxWidth: 8 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(24, 24, 27, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#e4e4e7',
                        borderColor: 'rgba(63, 63, 70, 0.8)',
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 6,
                        usePointStyle: true
                    }
                }
            }
        });
    }

    // --------------------------------------------------------
    // 2. NUEVA GRÁFICA (BOX PLOT HORARIO)
    // --------------------------------------------------------
    const datos = window.datosGraficas || {};
    const ctxBox = document.getElementById('boxplotChart');

    if (ctxBox && datos.boxplotData && datos.boxplotData.length > 0) {
        const horasLabels = Array.from({ length: 24 }, (_, i) => `${i + 1}:00`);

        new Chart(ctxBox.getContext('2d'), {
            type: 'boxplot',
            data: {
                labels: horasLabels,
                datasets: [{
                    label: 'Consumo Activo (kWh)',
                    data: datos.boxplotData,
                    backgroundColor: 'rgba(59, 130, 246, 0.2)', // blue-500 con transparencia
                    borderColor: 'rgba(59, 130, 246, 0.8)',     // blue-500
                    borderWidth: 2,
                    outlierBackgroundColor: '#ef4444', // red-500
                    outlierBorderColor: '#ef4444',
                    outlierRadius: 4,
                    itemRadius: 0 // Oculta los puntos para dejar una vista más limpia
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(24, 24, 27, 0.95)',
                        borderColor: 'rgba(63, 63, 70, 0.8)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function (context) {
                                // AHORA USAMOS context.raw PORQUE PYTHON YA MANDÓ EL OBJETO
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

                        // EXTRAEMOS LOS DATOS CRUDOS QUE LLEGARON DESDE DJANGO
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
                    // Cambia el cursor para indicar que es interactivo
                    event.native.target.style.cursor = elements.length ? 'pointer' : 'default';
                },
                scales: {
                    x: {
                        grid: { display: false, drawBorder: false },
                        title: { display: true, text: 'Hora del Día', color: '#71717a', font: { size: 12 } },
                        ticks: { maxRotation: 45, minRotation: 0 }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(63, 63, 70, 0.4)', drawBorder: false },
                        title: { display: true, text: 'Consumo (kWh)', color: '#71717a', font: { size: 12 } }
                    }
                }
            }
        });
    }
});