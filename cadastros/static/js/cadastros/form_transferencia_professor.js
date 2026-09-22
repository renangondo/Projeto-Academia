document.addEventListener('DOMContentLoaded', function () {
    initAutocomplete({
        inputId: 'aluno-busca',
        hiddenId: 'aluno-id',
        listId: 'aluno-lista',
        dadosId: 'dados-alunos'
    });

    initAutocomplete({
        inputId: 'professor-busca',
        hiddenId: 'professor-id',
        listId: 'professor-lista',
        dadosId: 'dados-professores'
    });
});