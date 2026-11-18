// Abre e fecha os menus de ação (.acoes-dropdown). Um clique fora, rolagem ou Esc fecha o menu aberto.
(function () {
    function fechar(dropdown) {
        dropdown.classList.remove('aberto');
        dropdown.querySelector('.acoes-dropdown-toggle').setAttribute('aria-expanded', 'false');
    }

    function fecharTodos(exceto) {
        document.querySelectorAll('.acoes-dropdown.aberto').forEach(function (dropdown) {
            if (dropdown !== exceto) fechar(dropdown);
        });
    }

    // O menu é fixed, então é posicionado em relação ao botão. Abre para cima se não couber embaixo.
    function posicionar(dropdown) {
        const botao = dropdown.querySelector('.acoes-dropdown-toggle').getBoundingClientRect();
        const menu = dropdown.querySelector('.acoes-dropdown-menu');
        const abaixo = botao.bottom + 4;
        const cabeEmbaixo = abaixo + menu.offsetHeight <= window.innerHeight;
        menu.style.top = (cabeEmbaixo ? abaixo : botao.top - menu.offsetHeight - 4) + 'px';
        menu.style.left = (botao.right - menu.offsetWidth) + 'px';
    }

    document.addEventListener('click', function (e) {
        const toggle = e.target.closest('.acoes-dropdown-toggle');
        if (toggle) {
            const dropdown = toggle.closest('.acoes-dropdown');
            const abrir = !dropdown.classList.contains('aberto');
            fecharTodos(dropdown);
            dropdown.classList.toggle('aberto', abrir);
            toggle.setAttribute('aria-expanded', String(abrir));
            if (abrir) posicionar(dropdown);
            return;
        }
        fecharTodos(null);
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') fecharTodos(null);
    });

    window.addEventListener('scroll', function () { fecharTodos(null); }, true);
    window.addEventListener('resize', function () { fecharTodos(null); });
})();
