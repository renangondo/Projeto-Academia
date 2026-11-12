document.addEventListener('DOMContentLoaded', function () {
    const treinos = JSON.parse(document.getElementById('dados-treinos').textContent);
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

    initAutocomplete({
        inputId: 'aluno-busca',
        hiddenId: 'aluno-id',
        listId: 'aluno-lista',
        dadosId: 'dados-alunos',
        onSelect: function (aluno) { filtrarTreinos(aluno.id); },
        onClear: function () { filtrarTreinos(''); },
    });
});