// Ordenação client-side de tabelas.
// Uso: <table data-ordenavel> ... o clique no título da coluna ordena as linhas.
// Colunas sem título ou com data-ordenar="false" não são ordenáveis.
(function () {
    const REGEX_DATA = /^(\d{2})\/(\d{2})\/(\d{4})/;
    const REGEX_NUMERO = /^-?\d+(?:[.,]\d+)?(?:\s*[^\d\s]+)?$/;

    function valorDaCelula(celula) {
        if (celula.dataset.valor !== undefined) return celula.dataset.valor;
        return celula.textContent.replace(/\s+/g, ' ').trim();
    }

    // Converte o texto em uma chave comparável: data (dd/mm/aaaa), número ou texto.
    function chave(texto) {
        const data = texto.match(REGEX_DATA);
        if (data) return { tipo: 'numero', valor: Number(data[3] + data[2] + data[1]) };

        if (REGEX_NUMERO.test(texto)) {
            return { tipo: 'numero', valor: parseFloat(texto.replace(',', '.')) };
        }
        return { tipo: 'texto', valor: texto };
    }

    function comparar(a, b) {
        const ca = chave(a);
        const cb = chave(b);

        if (ca.tipo === 'numero' && cb.tipo === 'numero') return ca.valor - cb.valor;
        // número antes de texto quando só um dos lados é numérico
        if (ca.tipo !== cb.tipo) return ca.tipo === 'numero' ? -1 : 1;
        return ca.valor.localeCompare(cb.valor, 'pt-BR', { numeric: true, sensitivity: 'base' });
    }

    function atualizarIndicadores(tabela, thAtivo, direcao) {
        tabela.querySelectorAll('thead th.ordenavel').forEach(function (th) {
            const icone = th.querySelector('.ordenar-icone');
            if (th === thAtivo) {
                th.dataset.direcao = direcao;
                th.setAttribute('aria-sort', direcao === 'asc' ? 'ascending' : 'descending');
                icone.className = 'fas ordenar-icone ' + (direcao === 'asc' ? 'fa-sort-up' : 'fa-sort-down');
            } else {
                th.dataset.direcao = '';
                th.removeAttribute('aria-sort');
                icone.className = 'fas fa-sort ordenar-icone';
            }
        });
    }

    function ordenar(tabela, indice, th) {
        const tbody = tabela.tBodies[0];
        if (!tbody || tbody.querySelector('.sem-registro')) return;

        const direcao = th.dataset.direcao === 'asc' ? 'desc' : 'asc';
        const fator = direcao === 'asc' ? 1 : -1;

        const linhas = Array.from(tbody.rows);
        linhas.sort(function (l1, l2) {
            return fator * comparar(
                valorDaCelula(l1.cells[indice]),
                valorDaCelula(l2.cells[indice])
            );
        });
        linhas.forEach(function (linha) { tbody.appendChild(linha); });

        atualizarIndicadores(tabela, th, direcao);
    }

    function iniciarTabela(tabela) {
        tabela.querySelectorAll('thead th').forEach(function (th, indice) {
            if (th.dataset.ordenar === 'false' || !th.textContent.trim()) return;

            th.classList.add('ordenavel');
            th.tabIndex = 0;

            const icone = document.createElement('i');
            icone.className = 'fas fa-sort ordenar-icone';
            icone.setAttribute('aria-hidden', 'true');
            th.appendChild(icone);

            th.addEventListener('click', function () {
                ordenar(tabela, indice, th);
            });
            th.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    ordenar(tabela, indice, th);
                }
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('table[data-ordenavel]').forEach(iniciarTabela);
    });
})();
