from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agenda.models import HorarioAula
from cadastros.models import (
    Cidade, Estado, Pessoa, TransferenciaAluno, expirar_transferencias_vencidas,
)
from exercicio.models import Categoria, Exercicio, ExercicioTreino, Treino
from medidas.models import Medidas
from medidas.utils import calcular_imc, classificar_imc

SENHA = "SenhaTeste@123"

DADOS_MEDIDAS = {
    "altura": 1.75, "peso": 70, "cintura": 80, "quadril": 95,
    "braco_direito": 33, "braco_esquerdo": 33, "coxa_direita": 55, "coxa_esquerda": 55,
    "panturrilha_direita": 37, "panturrilha_esquerda": 37, "peito": 100,
    "data_medida": "2026-11-10",
}


def criar_pessoa(tipo, nome, cpf, cidade, professor=None):
    administrador = tipo == "ADMINISTRADOR"
    usuario = User.objects.create_user(
        username=cpf, password=SENHA, is_superuser=administrador, is_staff=administrador
    )
    grupo, _ = Group.objects.get_or_create(name=tipo.capitalize())  # Administrador, Professor, Aluno
    usuario.groups.add(grupo)

    return Pessoa.objects.create(
        usuario=usuario, tipo=tipo, nome=nome, cpf=cpf,
        telefone="44999990000", cidade=cidade, professor=professor,
    )


class BaseTestes(TestCase):
    """Cenário: 1 administrador, 2 professores, alunos de cada um e um exercício do catálogo."""

    @classmethod
    def setUpTestData(cls):
        estado = Estado.objects.create(nome="Paraná", sigla="PR")
        cls.cidade = Cidade.objects.create(nome="Paranavaí", estado=estado)

        cls.admin = criar_pessoa("ADMINISTRADOR", "Admin", "00000000001", cls.cidade)
        cls.prof1 = criar_pessoa("PROFESSOR", "Professor Um", "00000000002", cls.cidade)
        cls.prof2 = criar_pessoa("PROFESSOR", "Professor Dois", "00000000003", cls.cidade)
        cls.aluno1 = criar_pessoa("ALUNO", "Aluno Um", "00000000004", cls.cidade, cls.prof1)
        cls.aluno2 = criar_pessoa("ALUNO", "Aluno Dois", "00000000005", cls.cidade, cls.prof2)
        cls.aluno3 = criar_pessoa("ALUNO", "Aluno Três", "00000000006", cls.cidade, cls.prof1)

        cls.categoria = Categoria.objects.create(nome="Peito")
        cls.exercicio = Exercicio.objects.create(
            nome="Supino reto", categoria=cls.categoria,
            descricao="Peitoral", cadastrado_por=cls.admin,
        )

    def entrar_como(self, pessoa):
        self.client.force_login(pessoa.usuario)

    def criar_treino(self, aluno, dono):
        hoje = timezone.localdate()
        return Treino.objects.create(
            aluno=aluno, nome_treino="Treino A", descricao="Peito", cadastrado_por=dono,
            data_inicio=hoje, data_fim=hoje + timedelta(days=30),
        )


class CasosFuncionaisTestes(BaseTestes):
    """Automatiza os casos CT-01 a CT-09 da Tabela 7."""

    def test_ta01_cadastrar_aluno_com_dados_validos(self):
        """TA-01 (CT-01) - Cadastrar aluno com dados válidos."""
        self.entrar_como(self.prof1)
        resposta = self.client.post(reverse("cadastrar-aluno"), {
            "nome": "Maria Souza", "cpf": "11122233344",
            "telefone": "44988887777", "cidade": self.cidade.pk,
        })
        self.assertEqual(resposta.status_code, 302)

        aluno = Pessoa.objects.get(cpf="11122233344")
        self.assertEqual(aluno.tipo, "ALUNO")
        self.assertEqual(aluno.professor, self.prof1)

        lista = self.client.get(reverse("listar-aluno"))
        self.assertContains(lista, "Maria Souza")

    def test_ta02_cadastro_com_cpf_ja_existente_e_rejeitado(self):
        """TA-02 (CT-02) - Cadastrar pessoa com CPF já existente."""
        self.entrar_como(self.prof1)
        total = Pessoa.objects.count()

        resposta = self.client.post(reverse("cadastrar-aluno"), {
            "nome": "Duplicado", "cpf": self.aluno1.cpf,
            "telefone": "44900000000", "cidade": self.cidade.pk,
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Pessoa.objects.count(), total)
        self.assertIn("cpf", resposta.context["form"].errors)

    def test_ta03_registrar_medidas_vinculadas_ao_aluno(self):
        """TA-03 (CT-03) - Registrar medidas corporais de um aluno."""
        self.entrar_como(self.prof1)
        resposta = self.client.post(
            reverse("cadastrar-medidas", args=[self.aluno1.pk]), DADOS_MEDIDAS
        )
        self.assertEqual(resposta.status_code, 302)

        medida = Medidas.objects.get()
        self.assertEqual(medida.aluno, self.aluno1)
        self.assertEqual(medida.data_medida, date(2026, 11, 10))
        self.assertEqual(medida.peso, 70)

    def test_ta04_criar_treino_com_exercicios(self):
        """TA-04 (CT-04) - Criar treino com exercícios, séries, repetições, descanso e carga."""
        self.entrar_como(self.prof1)
        inicio = timezone.localdate()

        resposta = self.client.post(reverse("cadastrar-treino", args=[self.aluno1.pk]), {
            "aluno": self.aluno1.pk, "nome_treino": "Treino A", "descricao": "Peito e tríceps",
            "data_inicio": inicio.isoformat(),
            "data_fim": (inicio + timedelta(days=30)).isoformat(),
        })
        self.assertEqual(resposta.status_code, 302)
        treino = Treino.objects.get()

        resposta = self.client.post(reverse("cadastrar-exercicioTreino", args=[treino.pk]), {
            "exercicio": self.exercicio.pk, "series": 4, "repeticoes": 10,
            "descanso": 2, "peso_atual": 40,
        })
        self.assertEqual(resposta.status_code, 302)

        item = ExercicioTreino.objects.get()
        self.assertEqual((item.series, item.repeticoes, item.descanso, item.peso_atual), (4, 10, 2, 40))

        # o treino aparece nas listas do professor e do aluno
        self.assertContains(self.client.get(reverse("listar-treino")), "Treino A")
        self.entrar_como(self.aluno1)
        self.assertContains(self.client.get(reverse("listar-treino")), "Treino A")

    def test_ta05_evolucao_das_medidas_com_mais_de_um_registro(self):
        """TA-05 (CT-05) - Evolução do aluno com mais de um registro de medidas."""
        for data, peso in ((date(2026, 10, 10), 70), (date(2026, 11, 10), 71)):
            Medidas.objects.create(
                aluno=self.aluno1, cadastrado_por=self.prof1.usuario, data_medida=data,
                **{**{k: v for k, v in DADOS_MEDIDAS.items() if k != "data_medida"}, "peso": peso},
            )

        for pessoa in (self.prof1, self.aluno1):   # tela do professor e tela do aluno
            self.entrar_como(pessoa)
            resposta = self.client.get(reverse("evolucao-medidas", args=[self.aluno1.pk]))
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(len(resposta.context["serie_json"]), 2)
            self.assertIn("resumo", resposta.context)

    def test_ta06_exportar_treino_em_pdf(self):
        """TA-06 (CT-06) - Exportar um treino em PDF."""
        treino = self.criar_treino(self.aluno1, self.prof1)
        ExercicioTreino.objects.create(
            treino=treino, exercicio=self.exercicio, series=3, repeticoes=12,
            descanso=1, peso_atual=40, cadastrado_por=self.prof1,
        )
        self.entrar_como(self.prof1)

        resposta = self.client.get(reverse("treino-pdf", args=[treino.pk]))

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "application/pdf")
        self.assertTrue(resposta.content.startswith(b"%PDF"))

    def test_ta07_agendar_aula_em_horario_ocupado(self):
        """TA-07 (CT-07) - Cadastrar aula em horário já ocupado pelo professor."""
        HorarioAula.objects.create(
            aluno=self.aluno1, professor=self.prof1, dia_semana=1, horario=time(10, 0)
        )
        self.entrar_como(self.prof1)

        resposta = self.client.post(reverse("agendar-aula"), {
            "aluno": self.aluno3.pk, "treino": "", "dia_semana": 1, "horario": "10:00",
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(HorarioAula.objects.count(), 1)
        self.assertTrue(resposta.context["form"].non_field_errors())

    def solicitar_transferencia_como_aluno(self):
        self.entrar_como(self.aluno1)
        return self.client.post(
            reverse("solicitar-transferencia-aluno"),
            {"professor_novo": self.prof2.pk, "observacao": ""},
        )

    def test_ta08_transferencia_com_solicitacao_pendente_e_bloqueada(self):
        """TA-08 (CT-08) - Solicitar transferência de aluno que já possui solicitação pendente."""
        self.assertEqual(self.solicitar_transferencia_como_aluno().status_code, 302)

        resposta = self.solicitar_transferencia_como_aluno()

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(TransferenciaAluno.objects.count(), 1)

    def test_ta09_solicitacao_sem_resposta_expira_em_48_horas(self):
        """TA-09 (CT-09) - Solicitação de transferência sem resposta após 48 horas."""
        transferencia = TransferenciaAluno.objects.create(
            aluno=self.aluno1, professor_atual=self.prof1, professor_novo=self.prof2
        )
        TransferenciaAluno.objects.filter(pk=transferencia.pk).update(
            cadastrado_em=timezone.now() - timedelta(hours=49)
        )

        expirar_transferencias_vencidas()

        transferencia.refresh_from_db()
        self.assertEqual(transferencia.status, "EXPIRADA")

        self.entrar_como(self.prof2)
        self.assertContains(self.client.get(reverse("minhas-transferencias")), "Expirada")


class SegurancaERegrasTestes(BaseTestes):
    """Controle de acesso por objeto, cálculos e senha."""

    def test_ta10_professor_nao_ve_aluno_de_outro_professor(self):
        """TA-10 - Professor não acessa o detalhe de aluno de outro professor."""
        self.entrar_como(self.prof2)
        resposta = self.client.get(reverse("detalhe-aluno", args=[self.aluno1.pk]))
        self.assertEqual(resposta.status_code, 404)

    def test_ta11_aluno_nao_ve_evolucao_de_outro_aluno(self):
        """TA-11 - O aluno não acessa a evolução de outro aluno."""
        self.entrar_como(self.aluno1)
        resposta = self.client.get(reverse("evolucao-medidas", args=[self.aluno2.pk]))
        self.assertEqual(resposta.status_code, 404)

    def test_ta12_professor_nao_ve_treino_de_aluno_de_outro_professor(self):
        """TA-12 - Professor não acessa o treino de aluno de outro professor."""
        treino = self.criar_treino(self.aluno1, self.prof1)
        self.entrar_como(self.prof2)
        resposta = self.client.get(reverse("detalhe-treino", args=[treino.pk]))
        self.assertEqual(resposta.status_code, 404)

    def test_ta13_visitante_e_redirecionado_ao_login(self):
        """TA-13 - Quem não está logado é redirecionado para o login."""
        resposta = self.client.get(reverse("inicio"))
        self.assertEqual(resposta.status_code, 302)

    def test_ta14_calculo_e_classificacao_do_imc(self):
        """TA-14 - O IMC é calculado e classificado nas faixas da OMS."""
        self.assertEqual(calcular_imc(70, 1.75), 22.9)
        self.assertEqual(calcular_imc(70, 175), 22.9)   # altura digitada em centímetros
        self.assertEqual(classificar_imc(17.0), "Abaixo do peso")
        self.assertEqual(classificar_imc(22.9), "Peso normal")
        self.assertEqual(classificar_imc(27.0), "Sobrepeso")
        self.assertEqual(classificar_imc(31.0), "Obesidade")

    def test_ta15_senha_fraca_e_recusada_e_senha_forte_e_aceita(self):
        """TA-15 - Senhas fracas são recusadas na troca de senha."""
        self.entrar_como(self.aluno1)

        def alterar(nova):
            return self.client.post(reverse("alterar-senha"), {
                "old_password": SENHA, "new_password1": nova, "new_password2": nova,
            })

        self.assertEqual(alterar("12345678").status_code, 200)   # só números
        self.assertEqual(alterar("abc123").status_code, 200)     # curta
        self.assertEqual(alterar("NovaSenha@2026").status_code, 302)

        self.aluno1.usuario.refresh_from_db()
        self.assertTrue(self.aluno1.usuario.check_password("NovaSenha@2026"))