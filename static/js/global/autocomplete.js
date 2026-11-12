function normalizarBusca(texto) {
    return texto.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function initAutocomplete({ inputId, hiddenId, listId, dadosId, obrigatorio = true, onSelect = null, onClear = null }) {
    const dadosEl = document.getElementById(dadosId);
    if (!dadosEl) return null;

    const dados = JSON.parse(dadosEl.textContent);
    const input = document.getElementById(inputId);
    const hidden = document.getElementById(hiddenId);
    const lista = document.getElementById(listId);

    let itens = [];
    let indiceAtivo = -1;

    // "required" em campo oculto é ignorado pelo navegador,
    // então a validação fica no campo de texto visível
    function validar() {
        if (!obrigatorio) return;
        input.setCustomValidity(hidden.value ? '' : 'Selecione uma opção da lista');
    }

    function fechar() {
        lista.style.display = 'none';
        indiceAtivo = -1;
    }

    function selecionar(opcao) {
        input.value = opcao.nome;
        hidden.value = opcao.id;
        fechar();
        validar();
        if (onSelect) onSelect(opcao);
    }

    function destacar(indice) {
        indiceAtivo = indice;
        itens.forEach((it, i) => it.el.classList.toggle('ativo', i === indiceAtivo));
        if (indiceAtivo >= 0) itens[indiceAtivo].el.scrollIntoView({ block: 'nearest' });
    }

    function renderizar() {
        const termo = normalizarBusca(input.value.trim());

        lista.innerHTML = '';
        itens = [];
        indiceAtivo = -1;

        if (!termo) {
            fechar();
            return;
        }

        const filtrados = dados.filter(d => normalizarBusca(d.nome).includes(termo));

        if (filtrados.length === 0) {
            const vazio = document.createElement('div');
            vazio.className = 'autocomplete-vazio';
            vazio.textContent = 'Nenhum resultado encontrado';
            lista.appendChild(vazio);
            lista.style.display = 'block';
            return;
        }

        filtrados.forEach(function (opcao) {
            const el = document.createElement('div');
            el.className = 'autocomplete-item';
            el.textContent = opcao.nome;

            // mousedown + preventDefault evita que o campo perca o foco antes do clique
            el.addEventListener('mousedown', function (e) {
                e.preventDefault();
                selecionar(opcao);
            });

            lista.appendChild(el);
            itens.push({ el: el, opcao: opcao });
        });

        lista.style.display = 'block';
    }

    input.addEventListener('input', function () {
        if (hidden.value) {
            hidden.value = '';
            if (onClear) onClear();
        }
        validar();
        renderizar();
    });

    input.addEventListener('keydown', function (e) {
        const aberta = lista.style.display === 'block';

        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            if (!aberta || itens.length === 0) return;
            e.preventDefault();

            const total = itens.length;
            destacar(
                e.key === 'ArrowDown'
                    ? (indiceAtivo + 1) % total
                    : (indiceAtivo - 1 + total) % total
            );

        } else if (e.key === 'Enter') {
            if (aberta && itens.length > 0) {
                // Enter escolhe a sugestão destacada (ou a primeira) e NÃO envia o formulário
                e.preventDefault();
                selecionar(itens[indiceAtivo >= 0 ? indiceAtivo : 0].opcao);

            } else if (!hidden.value && obrigatorio) {
                // nada escolhido ainda: não envia, e avisa o que falta
                e.preventDefault();
                input.reportValidity();
            }

        } else if (e.key === 'Escape') {
            fechar();
        }
    });

    input.addEventListener('blur', fechar);

    // clicar na barra de rolagem da lista não pode fechar a lista
    lista.addEventListener('mousedown', function (e) {
        e.preventDefault();
    });

    validar();

    return {
        definir: function (opcao) {
            input.value = opcao.nome;
            hidden.value = opcao.id;
            validar();
        },
        limpar: function () {
            input.value = '';
            hidden.value = '';
            validar();
        },
    };
}