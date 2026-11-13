document.addEventListener('DOMContentLoaded', function () {
    // quantas medidas aparecem em cada gráfico (mais que isso deixa as barras apertadas)
    const LIMITE_MEDIDAS = 2;

    // false = o eixo começa perto do menor valor, para a variação ficar visível;
    // true  = o eixo começa no zero
    const COMECAR_DO_ZERO = false;

    const CORES = ['#2563eb', '#38bdf8'];

    const GRAFICOS = [
        { titulo: 'Peso', unidade: 'kg', series: [['peso', 'Peso']] },
        { titulo: 'IMC', unidade: '', series: [['imc', 'IMC']] },
        { titulo: 'Cintura', unidade: 'cm', series: [['cintura', 'Cintura']] },
        { titulo: 'Quadril', unidade: 'cm', series: [['quadril', 'Quadril']] },
        { titulo: 'Braços', unidade: 'cm', series: [['braco_direito', 'Direito'], ['braco_esquerdo', 'Esquerdo']] },
        { titulo: 'Coxas', unidade: 'cm', series: [['coxa_direita', 'Direita'], ['coxa_esquerda', 'Esquerda']] },
        { titulo: 'Panturrilhas', unidade: 'cm', series: [['panturrilha_direita', 'Direita'], ['panturrilha_esquerda', 'Esquerda']] },
        { titulo: 'Peito', unidade: 'cm', series: [['peito', 'Peito']] },
    ];

    const dados = JSON.parse(document.getElementById('dados-medidas').textContent);
    const container = document.getElementById('graficos');

    if (!container || dados.length === 0) return;

    const recentes = dados.slice(-LIMITE_MEDIDAS);
    const rotulos = recentes.map(d => d.data);

    // escreve o valor em cima de cada barra
    const valoresNasBarras = {
        id: 'valoresNasBarras',
        afterDatasetsDraw: function (chart) {
            const ctx = chart.ctx;
            ctx.save();
            ctx.font = '600 10px sans-serif';
            ctx.fillStyle = '#334155';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';

            chart.data.datasets.forEach(function (dataset, i) {
                chart.getDatasetMeta(i).data.forEach(function (barra, j) {
                    const valor = dataset.data[j];
                    if (valor === null || valor === undefined) return;

                    const texto = Number(valor).toLocaleString('pt-BR', { maximumFractionDigits: 1 });
                    ctx.fillText(texto, barra.x, barra.y - 4);
                });
            });

            ctx.restore();
        },
    };

    GRAFICOS.forEach(function (config) {
        const card = document.createElement('div');
        card.className = 'grafico-card';

        const titulo = document.createElement('h3');
        titulo.textContent = config.unidade ? config.titulo + ' (' + config.unidade + ')' : config.titulo;

        const area = document.createElement('div');
        area.className = 'grafico-area';

        const canvas = document.createElement('canvas');

        area.appendChild(canvas);
        card.appendChild(titulo);
        card.appendChild(area);
        container.appendChild(card);

        const datasets = config.series.map(function (serie, i) {
            return {
                label: serie[1],
                data: recentes.map(d => d[serie[0]]),
                backgroundColor: CORES[i],
                borderRadius: 6,
                maxBarThickness: 46,
            };
        });

        new Chart(canvas, {
            type: 'bar',
            data: { labels: rotulos, datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: datasets.length > 1 },
                },
                scales: {
                    y: { beginAtZero: COMECAR_DO_ZERO, grace: '12%' },
                },
            },
            plugins: [valoresNasBarras],
        });
    });
});