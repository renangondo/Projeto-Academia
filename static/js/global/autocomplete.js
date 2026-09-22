function initAutocomplete({ inputId, hiddenId, listId, dadosId }) {
    const dadosEl = document.getElementById(dadosId);
    if (!dadosEl) return;

    const dados = JSON.parse(dadosEl.textContent);
    const input = document.getElementById(inputId);
    const hidden = document.getElementById(hiddenId);
    const lista = document.getElementById(listId);

    input.addEventListener('input', function () {
        const termo = this.value.toLowerCase().trim();
        lista.innerHTML = '';
        hidden.value = '';

        if (!termo) {
            lista.style.display = 'none';
            return;
        }

        const filtrados = dados.filter(item => item.nome.toLowerCase().includes(termo));

        if (filtrados.length === 0) {
            const item = document.createElement('div');
            item.classList.add('autocomplete-vazio');
            item.textContent = 'Nenhum resultado encontrado';
            lista.appendChild(item);
            lista.style.display = 'block';
            return;
        }

        filtrados.forEach(item => {
            const el = document.createElement('div');
            el.classList.add('autocomplete-item');
            el.textContent = item.nome;

            el.addEventListener('click', function () {
                input.value = item.nome;
                hidden.value = item.id;
                lista.innerHTML = '';
                lista.style.display = 'none';
            });

            lista.appendChild(el);
        });

        lista.style.display = 'block';
    });

    document.addEventListener('click', function (e) {
        if (!e.target.closest(`#${inputId}`) && !e.target.closest(`#${listId}`)) {
            lista.style.display = 'none';
        }
    });
}