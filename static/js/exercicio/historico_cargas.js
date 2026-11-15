document.addEventListener('DOMContentLoaded', function () {
    const el = document.getElementById('dados-cargas');
    if (!el) return;

    const dados = JSON.parse(el.textContent);

    dados.forEach(function (item) {
        const canvas = document.getElementById('grafico-carga-' + item.id);
        if (!canvas) return;

        new Chart(canvas, {
            type: 'line',   // troque por 'bar' se o professor preferir barras
            data: {
                labels: item.serie.map(s => s.data),
                datasets: [{
                    label: 'Carga (kg)',
                    data: item.serie.map(s => s.carga),
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.12)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: false,
                        grace: '15%',
                        title: { display: true, text: 'kg' },
                    },
                },
            },
        });
    });
});