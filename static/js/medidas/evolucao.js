document.addEventListener('DOMContentLoaded', function () {
    // quantas medidas aparecem em cada gráfico
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

    // ---------- formatação ----------

    function formatar(valor) {
        return Number(valor).toLocaleString('pt-BR', { maximumFractionDigits: 1 });
    }

    function comUnidade(valor, unidade) {
        return formatar(valor) + (unidade ? ' ' + unidade : '');
    }

    // ---------- comparativo ----------

    function criarChip(atual, base, unidade) {
        const diferenca = Math.round((atual - base) * 10) / 10;

        const chip = document.createElement('em');
        chip.className = 'comp-chip';

        const icone = document.createElement('i');

        if (diferenca > 0) {
            chip.classList.add('comp-subiu');
            icone.className = 'fas fa-arrow-up';
        } else if (diferenca < 0) {
            chip.classList.add('comp-desceu');
            icone.className = 'fas fa-arrow-down';
        } else {
            chip.classList.add('comp-igual');
            icone.className = 'fas fa-minus';
        }

        chip.appendChild(icone);

        let texto;
        if (diferenca === 0) {
            texto = ' sem variação';
        } else {
            texto = ' ' + comUnidade(Math.abs(diferenca), unidade);
            if (base) {
                texto += ' · ' + formatar(Math.abs(diferenca / base * 100)) + '%';
            }
        }

        chip.appendChild(document.createTextNode(texto));
        return chip;
    }

    function adicionarLinha(bloco, atual, base, unidade, legenda) {
        if (base === null || base === undefined) return;

        const linha = document.createElement('div');
        linha.className = 'comp-linha';

        linha.appendChild(criarChip(atual, base, unidade));

        const legendaEl = document.createElement('small');
        legendaEl.textContent = legenda + ' (' + comUnidade(base, unidade) + ')';
        linha.appendChild(legendaEl);

        bloco.appendChild(linha);
    }

    function criarBloco(rotulo, campo, unidade) {
        const total = dados.length;
        const atual = dados[total - 1][campo];

        const bloco = document.createElement('div');
        bloco.className = 'comp-bloco';

        if (rotulo) {
            const rotuloEl = document.createElement('span');
            rotuloEl.className = 'comp-rotulo';
            rotuloEl.textContent = rotulo;
            bloco.appendChild(rotuloEl);
        }

        const valor = document.createElement('strong');
        valor.className = 'comp-atual';
        valor.textContent = (atual === null || atual === undefined) ? '--' : comUnidade(atual, unidade);
        bloco.appendChild(valor);

        if (atual === null || atual === undefined || total < 2) return bloco;
        // compara só as duas últimas medidas
        adicionarLinha(bloco, atual, dados[total - 2][campo], unidade, 'vs. anterior');

        return bloco;
    }

    // ---------- valores escritos em cima das barras ----------

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

                    ctx.fillText(formatar(valor), barra.x, barra.y - 4);
                });
            });

            ctx.restore();
        },
    };

    // ---------- cards ----------

    GRAFICOS.forEach(function (config) {
        const card = document.createElement('div');
        card.className = 'grafico-card';

        const titulo = document.createElement('h3');
        titulo.textContent = config.unidade ? config.titulo + ' (' + config.unidade + ')' : config.titulo;

        const corpo = document.createElement('div');
        corpo.className = 'grafico-corpo';

        const area = document.createElement('div');
        area.className = 'grafico-area';

        const canvas = document.createElement('canvas');
        area.appendChild(canvas);

        const painel = document.createElement('aside');
        painel.className = 'comparativo';

        const tituloPainel = document.createElement('h4');
        tituloPainel.textContent = 'Comparativo';
        painel.appendChild(tituloPainel);

        config.series.forEach(function (serie) {
            const rotulo = config.series.length > 1 ? serie[1] : '';
            painel.appendChild(criarBloco(rotulo, serie[0], config.unidade));
        });

        corpo.appendChild(area);
        corpo.appendChild(painel);
        card.appendChild(titulo);
        card.appendChild(corpo);
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
            data: {
                // no eixo só dia/mês (cabe melhor); a data completa aparece ao passar o mouse
                labels: recentes.map(d => d.data.slice(0, 5)),
                datasets: datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: datasets.length > 1 },
                    tooltip: {
                        callbacks: {
                            title: function (itens) {
                                return recentes[itens[0].dataIndex].data;
                            },
                        },
                    },
                },
                scales: {
                    y: { beginAtZero: COMECAR_DO_ZERO, grace: '12%' },
                },
            },
            plugins: [valoresNasBarras],
        });
    });
});