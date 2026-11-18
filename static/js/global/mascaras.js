// Aplica máscaras (jQuery Mask) aos campos de CPF, telefone e sigla dos formulários.
// O campo é identificado pelo name ou, quando o name não bate, pelo data-mascara.
// Antes do envio, CPF e telefone voltam a ter só dígitos, como são salvos no banco.
(function () {
    const MASCARAS = {
        cpf: '000.000.000-00',
        telefone: function (valor) {
            return valor.replace(/\D/g, '').length > 10 ? '(00) 00000-0000' : '(00) 0000-0000';
        },
        sigla: 'SS'
    };
    const SOMENTE_DIGITOS = ['cpf', 'telefone'];

    function chaveDo(input) {
        return input.dataset.mascara || input.name;
    }

    function aplicarMascara(campo, mascara) {
        if (typeof mascara !== 'function') {
            campo.mask(mascara);
            return;
        }
        // Máscara dinâmica: a troca acontece no keydown, antes da tecla entrar no campo,
        // para que o 11º dígito não seja descartado pela máscara de 10.
        let atual = null;
        function ajustar(evento) {
            // No keydown o dígito digitado ainda não entrou no campo, então é previsto.
            const valor = evento.type === 'keydown' ? campo.val() + '0' : campo.val();
            const nova = mascara(valor);
            if (nova !== atual) {
                atual = nova;
                campo.mask(nova);
            }
        }
        ajustar({ type: 'init' });
        campo.on('keydown keyup', ajustar);
    }

    $(function () {
        $('input').each(function () {
            const mascara = MASCARAS[chaveDo(this)];
            if (mascara) aplicarMascara($(this), mascara);
        });

        $(document).on('submit', 'form', function () {
            $(this).find('input').each(function () {
                const chave = chaveDo(this);
                if (MASCARAS[chave] && SOMENTE_DIGITOS.includes(chave)) {
                    this.value = this.value.replace(/\D/g, '');
                }
            });
        });
    });
})();
