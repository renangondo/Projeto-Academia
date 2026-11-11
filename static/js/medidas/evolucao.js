document.addEventListener('DOMContentLoaded', function () {
    const dados = JSON.parse(document.getElementById('dados-medidas').textContent);
    const canvas = document.getElementById('grafico-medidas');
    const seletor = document.getElementById('grafico-grupo');

    if (!canvas || !seletor || dados.length === 0) return;

    const CORES = ['#2563eb', '#f59e0b'];

    const GRUPOS = {
        peso: { unidade: 'kg', series: [['peso', 'Peso']] },
        imc: { unidade: '', series: [['imc', 'IMC']] },
        cintura_quadril: { unidade: 'cm', series: [['cintura', 'Cintura'], ['quadril', 'Quadril']] },
        bracos: { unidade: 'cm', series: [['braco_direito', 'Direito'], ['braco_esquerdo', 'Esquerdo']] },
        coxas: { unidade: 'cm', series: [['coxa_direita', 'Direita'], ['coxa_esquerda', 'Esquerda']] },
        panturrilhas: { unidade: 'cm', series: [['panturrilha_direita', 'Direita'], ['panturrilha_esquerda', 'Esquerda']] },
        peito: { unidade: 'cm', series: [['peito', 'Peito']] },
    };

    let grafico = null;

    function desenhar(chave) {
        const grupo = GRUPOS[chave];

        const datasets = grupo.series.map(function (serie, i) {
            return {
                label: serie[1],
                data: dados.map(d => d[serie[0]]),
                borderColor: CORES[i],
                backgroundColor: CORES[i],
                tension: 0.3,
                pointRadius: 4,
            };
        });

        if (grafico) grafico.destroy();

        grafico = new Chart(canvas, {
            type: 'line',
            data: { labels: dados.map(d => d.data), datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: datasets.length > 1 } },
                scales: {
                    y: { title: { display: !!grupo.unidade, text: grupo.unidade } },
                },
            },
        });
    }

    seletor.addEventListener('change', function () {
        desenhar(seletor.value);
    });

    desenhar(seletor.value);
});