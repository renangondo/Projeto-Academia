document.addEventListener('DOMContentLoaded', function () {

    function lerJson(id) {
        const el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : [];
    }

    const alunos = lerJson('dados-alunos');
    const treinos = lerJson('dados-treinos');

    const input = document.getElementById('aluno-busca');
    const hidden = document.getElementById('aluno-id');
    const lista = document.getElementById('aluno-lista');
    const treinoSelect = document.getElementById('id_treino');

    if (!input || !hidden || !lista || !treinoSelect) {
        console.error('Agenda: campos do formulário não encontrados.');
        return;
    }

    let itens = [];
    let indiceAtivo = -1;

    function normalizar(texto) {
        return texto.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    // mostra só os treinos do aluno escolhido
    function filtrarTreinos(alunoId, selecionado) {
        treinoSelect.innerHTML = '';

        if (!alunoId) {
            treinoSelect.add(new Option('Escolha o aluno primeiro', ''));
            treinoSelect.disabled = true;
            return;
        }

        const doAluno = treinos.filter(t => String(t.aluno) === String(alunoId));

        treinoSelect.disabled = false;
        treinoSelect.add(new Option(
            doAluno.length ? 'Definir depois' : 'Este aluno ainda não tem treinos', ''
        ));

        doAluno.forEach(function (t) {
            const opcao = new Option(t.nome, t.id);
            if (String(t.id) === String(selecionado)) opcao.selected = true;
            treinoSelect.add(opcao);
        });
    }

    // "required" em campo oculto é ignorado pelo navegador,
    // então a validação fica no campo de texto visível
    function validar() {
        input.setCustomValidity(hidden.value ? '' : 'Selecione um aluno da lista');
    }

    function fechar() {
        lista.style.display = 'none';
        indiceAtivo = -1;
    }

    function selecionar(aluno) {
        input.value = aluno.nome;
        hidden.value = aluno.id;
        fechar();
        validar();
        filtrarTreinos(aluno.id, null);
    }

    function destacar(indice) {
        indiceAtivo = indice;
        itens.forEach((it, i) => it.el.classList.toggle('ativo', i === indiceAtivo));
        if (indiceAtivo >= 0) itens[indiceAtivo].el.scrollIntoView({ block: 'nearest' });
    }

    function renderizar() {
        const termo = normalizar(input.value.trim());

        lista.innerHTML = '';
        itens = [];
        indiceAtivo = -1;

        if (!termo) {
            fechar();
            return;
        }

        const filtrados = alunos.filter(a => normalizar(a.nome).includes(termo));

        if (filtrados.length === 0) {
            const vazio = document.createElement('div');
            vazio.className = 'autocomplete-vazio';
            vazio.textContent = 'Nenhum aluno encontrado';
            lista.appendChild(vazio);
            lista.style.display = 'block';
            return;
        }

        filtrados.forEach(function (aluno) {
            const el = document.createElement('div');
            el.className = 'autocomplete-item';
            el.textContent = aluno.nome;

            // mousedown evita que o campo perca o foco antes do clique
            el.addEventListener('mousedown', function (e) {
                e.preventDefault();
                selecionar(aluno);
            });

            lista.appendChild(el);
            itens.push({ el: el, aluno: aluno });
        });

        lista.style.display = 'block';
    }

    input.addEventListener('input', function () {
        if (hidden.value) {
            hidden.value = '';
            filtrarTreinos('', null);
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
                // Enter escolhe a sugestão destacada (ou a primeira) e não envia o formulário
                e.preventDefault();
                selecionar(itens[indiceAtivo >= 0 ? indiceAtivo : 0].aluno);

            } else if (!hidden.value) {
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

    // estado inicial (e restauração quando a página volta com erro)
    const treinoInicial = treinoSelect.value;
    const alunoInicial = alunos.find(a => String(a.id) === String(hidden.value));

    if (alunoInicial) {
        input.value = alunoInicial.nome;
        filtrarTreinos(alunoInicial.id, treinoInicial);
    } else {
        hidden.value = '';
        filtrarTreinos('', null);
    }

    validar();
});