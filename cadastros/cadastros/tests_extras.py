from datetime import date, datetime, time, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from agenda.models import HorarioAula
from agenda.utils import montar_semana, proxima_aula
from cadastros.models import Pessoa, TransferenciaAluno
from cadastros.tests import DADOS_MEDIDAS, SENHA, BaseTestes
from exercicio.cargas import registrar_carga
from exercicio.compartilhar import montar_link_whatsapp
from exercicio.models import Exercicio, ExercicioTreino, HistoricoCarga
from exercicio.views import exercicios_visiveis
from medidas.models import Medidas
from medidas.utils import CAMPOS_VARIACAO, calcular_variacoes


class BaseExtras(BaseTestes):

    def criar_medida(self, aluno, data, peso):
        dados = {k: v for k, v in DADOS_MEDIDAS.items() if k != "data_medida"}
        dados["peso"] = peso
        return Medidas.objects.create(
            aluno=aluno, cadastrado_por=self.prof1.usuario, data_medida=data, **dados
        )

    def criar_item(self, treino, peso=40):
        return ExercicioTreino.objects.create(
            treino=treino, exercicio=self.exercicio, series=3, repeticoes=12,
            descanso=1, peso_atual=peso, cadastrado_por=self.prof1,
        )

    def criar_transferencia(self):
        return TransferenciaAluno.objects.create(
            aluno=self.aluno1, professor_atual=self.prof1,
            professor_novo=self.prof2, origem="PROFESSOR",
        )

    def responder(self, pessoa, transferencia, acao):
        self.entrar_como(pessoa)
        return self.client.post(
            reverse("responder-transferencia", args=[transferencia.pk]), {"acao": acao}
        )


class CadastrosExtrasTestes(BaseExtras):

    def test_ta16_professor_se_cadastra_pela_tela_publica(self):
        """TA-16 - O cadastro público de professor cria o acesso com o CPF."""
        resposta = self.client.post(reverse("cadastrar-professor"), {
            "nome": "Novo Professor", "cpf": "22233344455",
            "telefone": "44977776666", "cidade": self.cidade.pk,
        })
        self.assertEqual(resposta.status_code, 302)

        professor = Pessoa.objects.get(cpf="22233344455")
        self.assertEqual(professor.tipo, "PROFESSOR")
        self.assertTrue(professor.usuario.check_password("22233344455"))
        self.assertTrue(professor.usuario.groups.filter(name="Professor").exists())

    def test_ta17_professor_edita_so_o_proprio_perfil(self):
        """TA-17 - O professor edita o próprio perfil, mas não o de outro professor."""
        self.entrar_como(self.prof1)
        resposta = self.client.post(reverse("editar-professor", args=[self.prof1.pk]), {
            "nome": "Professor Um Editado", "telefone": "44911112222", "cidade": self.cidade.pk,
        })
        self.assertEqual(resposta.status_code, 302)

        self.prof1.refresh_from_db()
        self.assertEqual(self.prof1.nome, "Professor Um Editado")
        self.assertEqual(
            self.client.get(reverse("editar-professor", args=[self.prof2.pk])).status_code, 404
        )

    def test_ta18_professor_edita_e_exclui_aluno(self):
        """TA-18 - O professor edita um aluno e exclui um aluno sem vínculos."""
        self.entrar_como(self.prof1)
        resposta = self.client.post(reverse("editar-aluno", args=[self.aluno1.pk]), {
            "nome": "Aluno Um Editado", "telefone": "44900001111", "cidade": self.cidade.pk,
        })
        self.assertEqual(resposta.status_code, 302)
        self.aluno1.refresh_from_db()
        self.assertEqual(self.aluno1.nome, "Aluno Um Editado")

        resposta = self.client.post(reverse("excluir-aluno", args=[self.aluno3.pk]))
        self.assertEqual(resposta.status_code, 302)
        self.assertFalse(Pessoa.objects.filter(pk=self.aluno3.pk).exists())

    def test_ta19_busca_de_alunos_por_nome_sem_acento_e_por_cpf(self):
        """TA-19 - A lista de alunos busca por nome (sem acento) e por CPF."""
        self.entrar_como(self.prof1)

        por_nome = self.client.get(reverse("listar-aluno"), {"q": "tres"})
        self.assertContains(por_nome, "Aluno Três")
        self.assertNotContains(por_nome, "Aluno Um")

        por_cpf = self.client.get(reverse("listar-aluno"), {"q": "00000000004"})
        self.assertContains(por_cpf, "Aluno Um")
        self.assertNotContains(por_cpf, "Aluno Três")

    def test_ta20_aceitar_transferencia_passa_o_aluno_ao_novo_professor(self):
        """TA-20 - Ao aceitar a transferência, o novo professor passa a ver o aluno."""
        transferencia = self.criar_transferencia()
        self.responder(self.prof2, transferencia, "aceitar")

        self.aluno1.refresh_from_db()
        transferencia.refresh_from_db()
        self.assertEqual(self.aluno1.professor, self.prof2)
        self.assertEqual(transferencia.status, "ACEITA")
        self.assertContains(self.client.get(reverse("listar-aluno")), "Aluno Um")

    def test_ta21_recusar_transferencia_mantem_o_professor(self):
        """TA-21 - Ao recusar a transferência, o aluno continua com o professor atual."""
        transferencia = self.criar_transferencia()
        self.responder(self.prof2, transferencia, "recusar")

        self.aluno1.refresh_from_db()
        transferencia.refresh_from_db()
        self.assertEqual(self.aluno1.professor, self.prof1)
        self.assertEqual(transferencia.status, "RECUSADA")

    def test_ta22_so_o_destinatario_responde_a_transferencia(self):
        """TA-22 - Quem não é o destinatário não pode responder à solicitação."""
        transferencia = self.criar_transferencia()
        resposta = self.responder(self.prof1, transferencia, "aceitar")

        self.assertEqual(resposta.status_code, 403)
        transferencia.refresh_from_db()
        self.assertEqual(transferencia.status, "PENDENTE")

    def test_ta23_professor_solicita_transferencia_e_ve_as_telas(self):
        """TA-23 - O professor solicita a transferência; a duplicada é bloqueada."""
        self.entrar_como(self.prof1)
        dados = {"aluno": self.aluno1.pk, "professor_novo": self.prof2.pk, "observacao": ""}

        self.assertEqual(self.client.post(reverse("solicitar-transferencia"), dados).status_code, 302)
        self.assertEqual(TransferenciaAluno.objects.get().origem, "PROFESSOR")

        self.assertEqual(self.client.post(reverse("solicitar-transferencia"), dados).status_code, 200)
        self.assertEqual(TransferenciaAluno.objects.count(), 1)

        self.assertContains(self.client.get(reverse("minhas-transferencias")), "Aluno Um")
        self.entrar_como(self.aluno1)
        self.assertEqual(self.client.get(reverse("minhas-solicitacoes")).status_code, 200)

    def test_ta24_primeiro_acesso_exige_troca_de_senha(self):
        """TA-24 - No primeiro acesso a troca de senha é obrigatória e depois é liberada."""
        Pessoa.objects.filter(pk=self.aluno1.pk).update(precisa_trocar_senha=True)
        self.entrar_como(self.aluno1)

        resposta = self.client.get(reverse("inicio"))
        self.assertRedirects(resposta, reverse("alterar-senha"), fetch_redirect_response=False)

        resposta = self.client.post(reverse("alterar-senha"), {
            "old_password": SENHA,
            "new_password1": "NovaSenha@2026",
            "new_password2": "NovaSenha@2026",
        })
        self.assertRedirects(resposta, reverse("inicio"), fetch_redirect_response=False)

        self.aluno1.refresh_from_db()
        self.assertFalse(self.aluno1.precisa_trocar_senha)


class PaineisEAgendaTestes(BaseExtras):

    def test_ta25_dashboard_do_professor(self):
        """TA-25 - O dashboard do professor mostra totais e a agenda da semana."""
        HorarioAula.objects.create(
            aluno=self.aluno1, professor=self.prof1, dia_semana=1, horario=time(10, 0)
        )
        self.criar_treino(self.aluno1, self.prof1)
        self.entrar_como(self.prof1)

        resposta = self.client.get(reverse("inicio"))

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(resposta.context["semana"]), 7)
        self.assertEqual(resposta.context["total_alunos"], 2)
        self.assertEqual(resposta.context["total_treinos"], 1)

    def test_ta26_dashboard_do_aluno(self):
        """TA-26 - O dashboard do aluno mostra a próxima aula, o IMC e a variação."""
        treino = self.criar_treino(self.aluno1, self.prof1)
        HorarioAula.objects.create(
            aluno=self.aluno1, professor=self.prof1, treino=treino,
            dia_semana=timezone.localdate().isoweekday(), horario=time(23, 59),
        )
        self.criar_medida(self.aluno1, date(2026, 10, 10), 70)
        self.criar_medida(self.aluno1, date(2026, 11, 10), 71)
        self.entrar_como(self.aluno1)

        resposta = self.client.get(reverse("inicio"))

        self.assertEqual(resposta.status_code, 200)
        self.assertIsNotNone(resposta.context["proxima_aula"])
        self.assertIsNotNone(resposta.context["imc"])
        self.assertEqual(resposta.context["variacoes"]["peso"]["sentido"], "subiu")

    def test_ta27_proxima_aula_considera_o_dia_e_a_hora_atuais(self):
        """TA-27 - A próxima aula é calculada a partir do dia e da hora atuais."""
        agora = timezone.make_aware(datetime(2026, 11, 20, 10, 0))   # sexta-feira, 10h

        def quando(dia, hora):
            aula = HorarioAula(dia_semana=dia, horario=hora)
            with patch("agenda.utils.timezone.localtime", return_value=agora):
                return proxima_aula([aula])["quando"]

        self.assertEqual(quando(5, time(15, 0)), "Hoje")
        self.assertEqual(quando(6, time(8, 0)), "Amanhã")
        self.assertEqual(quando(5, time(9, 0)), "Sexta-feira")   # já passou: só na semana que vem
        self.assertIsNone(proxima_aula([]))

    def test_ta28_agenda_agrupa_as_aulas_por_dia_da_semana(self):
        """TA-28 - A semana tem 7 dias, marca o dia de hoje e agrupa as aulas."""
        semana = montar_semana([HorarioAula(dia_semana=3, horario=time(8, 0))])

        self.assertEqual(len(semana), 7)
        self.assertEqual(sum(1 for dia in semana if dia["eh_hoje"]), 1)
        self.assertEqual(len(semana[2]["horarios"]), 1)        # quarta-feira
        self.assertEqual(semana[0]["abreviado"], "Seg")

    def test_ta29_variacao_entre_as_duas_ultimas_medidas(self):
        """TA-29 - A variação indica se cada medida subiu, desceu ou ficou igual."""
        def medida(**valores):
            base = {campo: 50.0 for campo in CAMPOS_VARIACAO}
            base.update(valores)
            return SimpleNamespace(**base)

        variacoes = calcular_variacoes(
            medida(peso=70.5, cintura=80.0), medida(peso=70.0, cintura=82.0)
        )

        self.assertEqual(variacoes["peso"], {"valor": 0.5, "sentido": "subiu"})
        self.assertEqual(variacoes["cintura"], {"valor": 2.0, "sentido": "desceu"})
        self.assertEqual(variacoes["peito"]["sentido"], "igual")
        self.assertEqual(calcular_variacoes(medida(), None), {})


class TreinosExerciciosECargasTestes(BaseExtras):

    def test_ta30_exercicio_do_professor_e_privado(self):
        """TA-30 - O exercício criado por um professor é visível só para ele."""
        self.entrar_como(self.prof1)
        resposta = self.client.post(reverse("cadastrar-exercicio"), {
            "nome": "Crucifixo", "categoria": self.categoria.pk, "descricao": "Peitoral",
        })
        self.assertEqual(resposta.status_code, 302)

        privado = Exercicio.objects.get(nome="Crucifixo")
        self.assertEqual(privado.cadastrado_por, self.prof1)
        self.assertIn(privado, exercicios_visiveis(self.prof1.usuario))
        self.assertNotIn(privado, exercicios_visiveis(self.prof2.usuario))
        # o catálogo do administrador continua visível para todos
        self.assertIn(self.exercicio, exercicios_visiveis(self.prof2.usuario))

    def test_ta31_lista_de_exercicios_do_professor(self):
        """TA-31 - A lista separa os exercícios do professor e o catálogo geral."""
        Exercicio.objects.create(
            nome="Crucifixo", categoria=self.categoria, descricao="d", cadastrado_por=self.prof1
        )
        self.entrar_como(self.prof1)

        meus = self.client.get(reverse("listar-exercicio"))
        self.assertContains(meus, "Crucifixo")
        self.assertNotContains(meus, "Supino reto")

        catalogo = self.client.get(reverse("listar-exercicio"), {"origem": "catalogo"})
        self.assertContains(catalogo, "Supino reto")
        self.assertNotContains(catalogo, "Crucifixo")

        busca = self.client.get(reverse("listar-exercicio"), {"origem": "todos", "q": "supino"})
        self.assertContains(busca, "Supino reto")
        self.assertNotContains(busca, "Crucifixo")

    def test_ta32_editar_treino_valida_as_datas(self):
        """TA-32 - A edição do treino recusa data de encerramento anterior ao início."""
        treino = self.criar_treino(self.aluno1, self.prof1)
        self.entrar_como(self.prof1)
        url = reverse("editar-treino", args=[treino.pk])
        inicio = timezone.localdate()

        invalido = self.client.post(url, {
            "nome_treino": "Treino B", "descricao": "x",
            "data_inicio": inicio.isoformat(),
            "data_fim": (inicio - timedelta(days=1)).isoformat(),
        })
        self.assertEqual(invalido.status_code, 200)
        treino.refresh_from_db()
        self.assertEqual(treino.nome_treino, "Treino A")

        valido = self.client.post(url, {
            "nome_treino": "Treino B", "descricao": "x",
            "data_inicio": inicio.isoformat(),
            "data_fim": (inicio + timedelta(days=10)).isoformat(),
        })
        self.assertEqual(valido.status_code, 302)
        treino.refresh_from_db()
        self.assertEqual(treino.nome_treino, "Treino B")

    def test_ta33_editar_e_excluir_exercicio_do_treino(self):
        """TA-33 - Editar a carga de um exercício do treino gera histórico; excluir remove."""
        item = self.criar_item(self.criar_treino(self.aluno1, self.prof1), peso=40)

        self.entrar_como(self.prof2)   # outro professor não pode excluir
        self.assertEqual(
            self.client.post(reverse("excluir-exercicioTreino", args=[item.pk])).status_code, 404
        )

        self.entrar_como(self.prof1)
        resposta = self.client.post(reverse("editar-exercicioTreino", args=[item.pk]), {
            "exercicio": self.exercicio.pk, "series": 4, "repeticoes": 8,
            "descanso": 2, "peso_atual": 50,
        })
        self.assertEqual(resposta.status_code, 302)
        item.refresh_from_db()
        self.assertEqual((item.series, item.peso_atual), (4, 50))
        self.assertEqual(HistoricoCarga.objects.get().carga, 50)

        resposta = self.client.post(reverse("excluir-exercicioTreino", args=[item.pk]))
        self.assertEqual(resposta.status_code, 302)
        self.assertFalse(ExercicioTreino.objects.filter(pk=item.pk).exists())

    def test_ta34_historico_de_cargas(self):
        """TA-34 - O histórico guarda uma carga por dia e respeita o acesso do aluno."""
        item = self.criar_item(self.criar_treino(self.aluno1, self.prof1), peso=40)

        registrar_carga(self.aluno1, self.exercicio, 40, self.prof1.usuario)
        registrar_carga(self.aluno1, self.exercicio, 45, self.prof1.usuario)  # mesmo dia: atualiza
        self.assertEqual(HistoricoCarga.objects.count(), 1)
        self.assertEqual(HistoricoCarga.objects.get().carga, 45)

        # o aluno registra a carga que usou
        self.entrar_como(self.aluno1)
        resposta = self.client.post(reverse("registrar-carga", args=[item.pk]), {"peso_atual": 50})
        self.assertEqual(resposta.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.peso_atual, 50)
        self.assertEqual(HistoricoCarga.objects.get().carga, 50)

        # tela do histórico, geral e filtrada por exercício
        url = reverse("historico-cargas", args=[self.aluno1.pk])
        tela = self.client.get(url)
        self.assertEqual(tela.status_code, 200)
        self.assertEqual(len(tela.context["cartoes"]), 1)
        self.assertEqual(self.client.get(url, {"exercicio": self.exercicio.pk}).status_code, 200)

        # outro aluno não vê nem registra
        self.entrar_como(self.aluno2)
        self.assertEqual(self.client.get(url).status_code, 404)
        resposta = self.client.post(reverse("registrar-carga", args=[item.pk]), {"peso_atual": 99})
        self.assertEqual(resposta.status_code, 404)

        # o aluno exclui um registro seu
        self.entrar_como(self.aluno1)
        registro = HistoricoCarga.objects.get()
        self.assertEqual(self.client.post(reverse("excluir-carga", args=[registro.pk])).status_code, 302)
        self.assertEqual(HistoricoCarga.objects.count(), 0)

    def test_ta35_compartilhar_treino_por_whatsapp(self):
        """TA-35 - O link do WhatsApp leva o número do aluno e o treino na mensagem."""
        treino = self.criar_treino(self.aluno1, self.prof1)
        self.criar_item(treino)

        link = montar_link_whatsapp(treino, ExercicioTreino.objects.filter(treino=treino))
        self.assertTrue(link.startswith("https://wa.me/5544999990000?text="))
        self.assertIn("Supino%20reto", link)

        self.entrar_como(self.prof1)
        resposta = self.client.get(reverse("detalhe-treino", args=[treino.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta.context["link_whatsapp"].startswith("https://wa.me/"))

    def test_ta36_aluno_registra_edita_e_exclui_as_proprias_medidas(self):
        """TA-36 - O aluno registra medidas (reaproveitando a altura), edita e exclui."""
        self.entrar_como(self.aluno1)
        url = reverse("cadastrar-medidas", args=[self.aluno1.pk])
        self.assertEqual(self.client.post(url, DADOS_MEDIDAS).status_code, 302)

        segunda = {k: v for k, v in DADOS_MEDIDAS.items() if k != "altura"}
        segunda.update(peso=71, data_medida="2026-11-17")
        self.assertEqual(self.client.post(url, segunda).status_code, 302)

        ultima = Medidas.objects.order_by("-data_medida").first()
        self.assertEqual((ultima.peso, ultima.altura), (71, 1.75))

        resposta = self.client.post(
            reverse("editar-medidas", args=[ultima.pk]),
            {**DADOS_MEDIDAS, "peso": 72, "data_medida": "2026-11-17"},
        )
        self.assertEqual(resposta.status_code, 302)
        ultima.refresh_from_db()
        self.assertEqual(ultima.peso, 72)

        resposta = self.client.post(reverse("excluir-medidas", args=[ultima.pk]))
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(Medidas.objects.count(), 1)

    def test_ta37_representacoes_e_propriedades_dos_models(self):
        """TA-37 - Formatação de CPF e telefone, idade e textos dos registros."""
        pessoa = Pessoa(
            nome="Maria", tipo="ALUNO", cpf="12345678909",
            telefone="44998765432", data_nascimento=date(1990, 1, 1),
        )
        self.assertEqual(pessoa.cpf_formatado, "123.456.789-09")
        self.assertEqual(pessoa.cpf_mascarado, "***.456.789-**")
        self.assertEqual(pessoa.telefone_formatado, "(44) 99876-5432")
        self.assertIsInstance(pessoa.idade, int)
        self.assertEqual(str(pessoa), "Maria - Aluno")
        self.assertEqual(str(self.cidade), "Paranavaí (PR)")
        self.assertIn("Supino reto", str(self.exercicio))
        self.assertEqual(Medidas(altura=186).altura_em_metros, 1.86)
        self.assertEqual(Medidas(altura=1.7).altura_em_metros, 1.7)

        transferencia = self.criar_transferencia()
        self.assertIn("PENDENTE", str(transferencia))
        self.assertFalse(transferencia.esta_vencida)
        self.assertGreater(transferencia.prazo_limite, timezone.now())