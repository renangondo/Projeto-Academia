document.addEventListener('DOMContentLoaded', function () {
    const dados = JSON.parse(document.getElementById('dados-alunos').textContent);
    const treinos = JSON.parse(document.getElementById('dados-treinos').textContent);

    const input = document.getElementById('aluno-busca');
    const hidden = document.getElementById('aluno-id');
    const lista = document.getElementById('aluno-lista');
    const treinoSelect = document.getElementById('id_treino');

    function filtrarTreinos(alunoId) {
        treinoSelect.innerHTML = '';

        if (!alunoId) {
            treinoSelect.add(new Option('Escolha o aluno primeiro', ''));
            treinoSelect.disabled = true;
            return;
        }

        treinoSelect.disabled = false;
        treinoSelect.add(new Option('Definir depois', ''));

        treinos
            .filter(t => String(t.aluno) === String(alunoId))
            .forEach(t => treinoSelect.add(new Option(t.nome, t.id)));
    }

    filtrarTreinos('');

    input.addEventListener('input', function () {
        const termo = this.value.toLowerCase().trim();
        lista.innerHTML = '';
        hidden.value = '';
        filtrarTreinos('');

        if (!termo) {
            lista.style.display = 'none';
            return;
        }

        const filtrados = dados.filter(a => a.nome.toLowerCase().includes(termo));

        if (filtrados.length === 0) {
            const item = document.createElement('div');
            item.classList.add('autocomplete-vazio');
            item.textContent = 'Nenhum aluno encontrado';
            lista.appendChild(item);
            lista.style.display = 'block';
            return;
        }

        filtrados.forEach(a => {
            const item = document.createElement('div');
            item.classList.add('autocomplete-item');
            item.textContent = a.nome;

            item.addEventListener('click', function () {
                input.value = a.nome;
                hidden.value = a.id;
                lista.innerHTML = '';
                lista.style.display = 'none';
                filtrarTreinos(a.id);
            });

            lista.appendChild(item);
        });

        lista.style.display = 'block';
    });

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.campo-autocomplete')) {
            lista.style.display = 'none';
        }
    });
});