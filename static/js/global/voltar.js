document.addEventListener('DOMContentLoaded', function () {
    const botao = document.getElementById('btn-voltar');
    if (!botao) return;

    botao.addEventListener('click', function (e) {
        e.preventDefault();

        // volta para a página anterior se ela for do próprio sistema;
        // senão (aba nova, link externo) leva para o Dashboard
        const veioDoSistema = document.referrer &&
            new URL(document.referrer).origin === window.location.origin;

        if (veioDoSistema) {
            window.history.back();
        } else {
            window.location.href = botao.href;
        }
    });
});