document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-semana]').forEach(function (semana) {
        const abas = semana.querySelectorAll('.semana-aba');
        const paineis = semana.querySelectorAll('.semana-painel');

        abas.forEach(function (aba) {
            aba.addEventListener('click', function () {
                const dia = aba.dataset.dia;

                abas.forEach(a => a.classList.toggle('ativa', a === aba));
                paineis.forEach(p => p.classList.toggle('ativo', p.dataset.painel === dia));
            });
        });
    });
});