function normalizar(texto) {
    return texto.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function initCombobox({ inputId, listId, valorEl, getOpcoes, obrigatorio = false, onSelect = null, onClear = null }) {
    const input = document.getElementById(inputId);
    const lista = document.getElementById(listId);
    let itens = [];
    let indiceAtivo = -1;

    function validar() {
        if (!obrigatorio) return;
        input.setCustomValidity(valorEl.value ? '' : 'Selecione uma opção da lista');
    }

    function fechar() {
        lista.style.display = 'none';
        indiceAtivo = -1;
    }

    function selecionar(opcao) {
        input.value = opcao.nome;
        valorEl.value = opcao.id;
        fechar();
        validar();
        if (onSelect) onSelect(opcao);
    }

    function renderizar() {
        const termo = normalizar(input.value.trim());
        const opcoes = getOpcoes().filter(o => normalizar(o.nome).includes(termo));

        lista.innerHTML = '';
        itens = [];
        indiceAtivo = -1;

        if (opcoes.length === 0) {
            const vazio = document.createElement('div');
            vazio.className = 'autocomplete-vazio';
            vazio.textContent = 'Nenhum resultado encontrado';
            lista.appendChild(vazio);
        }

        opcoes.forEach(function (opcao) {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.textContent = opcao.nome;

            if (opcao.extra) {
                const extra = document.createElement('small');
                extra.className = 'autocomplete-extra';
                extra.textContent = opcao.extra;
                item.appendChild(extra);
            }

            // mousedown + preventDefault evita que o campo perca o foco antes do clique
            item.addEventListener('mousedown', function (e) {
                e.preventDefault();
                selecionar(opcao);
            });

            lista.appendChild(item);
            itens.push({ el: item, opcao: opcao });
        });

        lista.style.display = 'block';
    }

    input.addEventListener('focus', renderizar);
    input.addEventListener('click', renderizar);

    input.addEventListener('input', function () {
        if (valorEl.value) {
            valorEl.value = '';
            if (onClear) onClear();
        }
        validar();
        renderizar();
    });

    input.addEventListener('keydown', function (e) {
        const aberta = lista.style.display === 'block';

        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            if (!aberta) renderizar();
            if (itens.length === 0) return;
            e.preventDefault();

            indiceAtivo = e.key === 'ArrowDown'
                ? (indiceAtivo + 1) % itens.length
                : (indiceAtivo - 1 + itens.length) % itens.length;

            itens.forEach((it, i) => it.el.classList.toggle('ativo', i === indiceAtivo));
            itens[indiceAtivo].el.scrollIntoView({ block: 'nearest' });

        } else if (e.key === 'Enter' && aberta && indiceAtivo >= 0) {
            e.preventDefault();
            selecionar(itens[indiceAtivo].opcao);

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
            valorEl.value = opcao.id;
            validar();
        },
        limpar: function () {
            input.value = '';
            valorEl.value = '';
            validar();
        }
    };
}