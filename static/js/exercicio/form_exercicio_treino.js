document.addEventListener('DOMContentLoaded', function () {
    const categorias = JSON.parse(document.getElementById('dados-categorias').textContent);
    const exercicios = JSON.parse(document.getElementById('dados-exercicios').textContent);

    const exercicioSelect = document.getElementById('id_exercicio');
    const categoriaHidden = document.getElementById('categoria-id');

    // o select original do Django continua guardando o valor enviado, só fica escondido
    exercicioSelect.closest('p').style.display = 'none';
    exercicioSelect.required = false;  // a validação passa a ser do campo com busca

    const nomeCategoria = {};
    categorias.forEach(c => nomeCategoria[c.id] = c.nome);

    const comboCategoria = initCombobox({
        inputId: 'categoria-busca',
        listId: 'categoria-lista',
        valorEl: categoriaHidden,
        getOpcoes: () => categorias,
        onSelect: function (categoria) {
            // se o exercício já escolhido é de outra categoria, limpa
            const atual = exercicios.find(e => String(e.id) === String(exercicioSelect.value));
            if (atual && String(atual.categoria) !== String(categoria.id)) {
                comboExercicio.limpar();
            }
        }
    });

    const comboExercicio = initCombobox({
        inputId: 'exercicio-busca',
        listId: 'exercicio-lista',
        valorEl: exercicioSelect,
        obrigatorio: true,
        getOpcoes: function () {
            const categoriaId = categoriaHidden.value;
            const filtrados = categoriaId
                ? exercicios.filter(e => String(e.categoria) === String(categoriaId))
                : exercicios;

            return filtrados.map(e => ({
                id: e.id,
                nome: e.nome,
                extra: categoriaId ? '' : nomeCategoria[e.categoria]
            }));
        },
        onSelect: function (opcao) {
            // escolheu o exercício direto: preenche a categoria dele
            const exercicio = exercicios.find(e => String(e.id) === String(opcao.id));
            if (exercicio && !categoriaHidden.value) {
                comboCategoria.definir({ id: exercicio.categoria, nome: nomeCategoria[exercicio.categoria] });
            }
        }
    });

    // se a página recarregou com erro de validação, restaura o que já estava escolhido
    const inicial = exercicios.find(e => String(e.id) === String(exercicioSelect.value));
    if (inicial) {
        comboExercicio.definir({ id: inicial.id, nome: inicial.nome });
        comboCategoria.definir({ id: inicial.categoria, nome: nomeCategoria[inicial.categoria] });
    }
});