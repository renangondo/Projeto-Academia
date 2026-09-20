document.addEventListener('DOMContentLoaded', function () {
    const dadosEl = document.getElementById('dados-alunos');
    const dados = JSON.parse(dadosEl.textContent);

    const input = document.getElementById('aluno-busca');
    const hidden = document.getElementById('aluno-id');
    const lista = document.getElementById('aluno-lista');

    input.addEventListener('input', function () {
        const termo = this.value.toLowerCase().trim();
        lista.innerHTML = '';
        hidden.value = '';

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