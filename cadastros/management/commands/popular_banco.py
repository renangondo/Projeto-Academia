import random
from datetime import date, time, timedelta
from itertools import cycle

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from agenda.models import HorarioAula
from cadastros.models import Cidade, Estado, Pessoa, TransferenciaAluno
from exercicio.models import (
    Categoria,
    Exercicio,
    ExercicioTreino,
    HistoricoCarga,
    Treino,
)
from medidas.models import Medidas

# Exercícios reais de musculação: categoria -> [(nome, descrição, carga base em kg)]
CATALOGO = {
    "Peito": [
        ("Supino reto com barra", "Deitado no banco, empurre a barra até estender os braços.", 50),
        ("Supino inclinado com halteres", "Banco a 30-45 graus, foco na porção superior do peitoral.", 18),
        ("Crucifixo máquina (peck deck)", "Junte as mãos à frente do corpo controlando a volta.", 35),
        ("Flexão de braços", "Corpo alinhado, desça o peito até perto do chão.", 0),
    ],
    "Costas": [
        ("Puxada frontal", "Puxe a barra até a altura do queixo com as costas eretas.", 45),
        ("Remada curvada com barra", "Tronco inclinado, puxe a barra em direção ao abdômen.", 40),
        ("Remada baixa no cabo", "Sentado, puxe o triângulo até o abdômen.", 40),
        ("Barra fixa", "Pegada pronada, suba até o queixo passar da barra.", 0),
    ],
    "Ombros": [
        ("Desenvolvimento com halteres", "Sentado, empurre os halteres acima da cabeça.", 16),
        ("Elevação lateral", "Eleve os halteres até a altura dos ombros.", 8),
        ("Elevação frontal", "Eleve os halteres à frente até a altura dos ombros.", 8),
        ("Crucifixo inverso", "Tronco inclinado, abra os braços para trás.", 8),
    ],
    "Bíceps": [
        ("Rosca direta com barra", "Em pé, flexione os cotovelos sem balançar o tronco.", 25),
        ("Rosca martelo", "Pegada neutra com halteres, alternando os braços.", 12),
        ("Rosca scott", "Apoie os braços no banco scott e flexione.", 20),
    ],
    "Tríceps": [
        ("Tríceps pulley", "Cotovelos junto ao corpo, estenda os braços para baixo.", 30),
        ("Tríceps testa", "Deitado, flexione os cotovelos levando a barra à testa.", 20),
        ("Mergulho no banco", "Mãos no banco atrás do corpo, desça e suba.", 0),
    ],
    "Quadríceps": [
        ("Agachamento livre", "Barra nas costas, desça até as coxas ficarem paralelas.", 60),
        ("Leg press 45", "Empurre a plataforma sem travar os joelhos.", 120),
        ("Cadeira extensora", "Estenda os joelhos até alinhar as pernas.", 40),
        ("Afundo com halteres", "Passo à frente e desça até o joelho de trás quase tocar o chão.", 14),
    ],
    "Posterior de coxa": [
        ("Mesa flexora", "Deitado, flexione os joelhos levando o calcanhar ao glúteo.", 35),
        ("Stiff com barra", "Pernas semiflexionadas, desça a barra rente às pernas.", 40),
        ("Cadeira flexora", "Sentado, flexione os joelhos contra a resistência.", 35),
    ],
    "Glúteos": [
        ("Elevação pélvica", "Costas apoiadas no banco, eleve o quadril com a barra.", 60),
        ("Agachamento sumô", "Pés afastados e pontas para fora, desça com o tronco ereto.", 30),
        ("Cadeira abdutora", "Abra as pernas contra a resistência da máquina.", 45),
    ],
    "Panturrilha": [
        ("Panturrilha em pé", "Eleve os calcanhares o máximo possível e desça devagar.", 60),
        ("Panturrilha sentado", "Sentado na máquina, eleve os calcanhares.", 40),
    ],
    "Abdômen": [
        ("Abdominal supra", "Deitado, eleve o tronco contraindo o abdômen.", 0),
        ("Prancha isométrica", "Apoie antebraços e pontas dos pés mantendo o corpo reto.", 0),
        ("Elevação de pernas", "Deitado, eleve as pernas estendidas até 90 graus.", 0),
    ],
    "Cardio": [
        ("Esteira", "Caminhada ou corrida em ritmo moderado.", 0),
        ("Bicicleta ergométrica", "Pedalada contínua em intensidade moderada.", 0),
        ("Elíptico", "Movimento contínuo com baixo impacto nas articulações.", 0),
    ],
}

# Divisões de treino: nome (máx. 20 caracteres) -> (descrição, [(exercício, séries, repetições, descanso em s)])
TREINOS_MASCULINO = {
    "Treino A - Peito": ("Peito e tríceps", [
        ("Supino reto com barra", 4, 10, 90), ("Supino inclinado com halteres", 3, 10, 90),
        ("Crucifixo máquina (peck deck)", 3, 12, 60), ("Tríceps pulley", 3, 12, 60),
        ("Tríceps testa", 3, 10, 60),
    ]),
    "Treino B - Costas": ("Costas e bíceps", [
        ("Puxada frontal", 4, 10, 90), ("Remada curvada com barra", 4, 10, 90),
        ("Remada baixa no cabo", 3, 12, 60), ("Rosca direta com barra", 3, 10, 60),
        ("Rosca martelo", 3, 12, 60),
    ]),
    "Treino C - Pernas": ("Pernas e ombros", [
        ("Agachamento livre", 4, 8, 120), ("Leg press 45", 4, 10, 90),
        ("Cadeira extensora", 3, 12, 60), ("Mesa flexora", 3, 12, 60),
        ("Desenvolvimento com halteres", 3, 10, 75), ("Elevação lateral", 3, 12, 45),
        ("Panturrilha em pé", 4, 15, 45),
    ]),
}

TREINOS_FEMININO = {
    "Treino A - Inferior": ("Glúteos e quadríceps", [
        ("Elevação pélvica", 4, 12, 90), ("Agachamento sumô", 4, 12, 75),
        ("Leg press 45", 3, 12, 90), ("Cadeira abdutora", 3, 15, 60),
        ("Panturrilha em pé", 3, 15, 45),
    ]),
    "Treino B - Superior": ("Costas, ombros e braços", [
        ("Puxada frontal", 3, 12, 75), ("Remada baixa no cabo", 3, 12, 75),
        ("Desenvolvimento com halteres", 3, 12, 75), ("Elevação lateral", 3, 12, 45),
        ("Rosca martelo", 3, 12, 45), ("Tríceps pulley", 3, 12, 45),
    ]),
    "Treino C - Posterior": ("Posterior, glúteos e abdômen", [
        ("Stiff com barra", 4, 10, 90), ("Mesa flexora", 3, 12, 60),
        ("Afundo com halteres", 3, 12, 75), ("Abdominal supra", 3, 20, 30),
        ("Prancha isométrica", 3, 40, 30),
    ]),
}

TREINOS_INICIANTE = {
    "Full Body": ("Corpo inteiro para adaptação", [
        ("Leg press 45", 3, 12, 90), ("Supino reto com barra", 3, 12, 90),
        ("Puxada frontal", 3, 12, 90), ("Desenvolvimento com halteres", 3, 12, 75),
        ("Prancha isométrica", 3, 30, 45), ("Esteira", 1, 15, 0),
    ]),
}

ESTADOS = {
    ("Paraná", "PR"): ["Curitiba", "Londrina", "Maringá", "Paranavaí", "Cascavel"],
    ("Santa Catarina", "SC"): ["Florianópolis", "Joinville"],
    ("São Paulo", "SP"): ["São Paulo", "Campinas"],
}

# nome, sexo, nascimento (ano, mês, dia), cidade
ADMINISTRADOR = ("Marcos Antônio Ribeiro", "M", (1980, 3, 14), "Paranavaí")
PROFESSORES = [
    ("Fernanda Cristina Lopes", "F", (1989, 7, 22), "Paranavaí"),
    ("Ricardo Almeida Tavares", "M", (1985, 11, 5), "Maringá"),
    ("Juliana Matos Ferreira", "F", (1993, 2, 17), "Londrina"),
]
# nome, sexo, nascimento, cidade, nível (1-3), objetivo, altura (cm), peso inicial (kg)
ALUNOS = [
    ("Lucas Gabriel Souza", "M", (2001, 4, 9), "Paranavaí", 2, "Hipertrofia", 178, 74),
    ("Mariana Oliveira Costa", "F", (1998, 9, 30), "Maringá", 2, "Definição muscular", 165, 62),
    ("Pedro Henrique Lima", "M", (1995, 1, 12), "Londrina", 3, "Ganho de força", 182, 88),
    ("Ana Beatriz Santos", "F", (2003, 6, 25), "Paranavaí", 1, "Condicionamento físico", 160, 58),
    ("Carlos Eduardo Pereira", "M", (1988, 12, 3), "Curitiba", 1, "Emagrecimento", 175, 96),
    ("Camila Rodrigues Alves", "F", (1996, 5, 18), "Cascavel", 2, "Hipertrofia de glúteos", 168, 64),
    ("Rafael Martins Barbosa", "M", (2000, 8, 7), "Florianópolis", 2, "Hipertrofia", 180, 78),
    ("Larissa Fernandes Rocha", "F", (1992, 10, 21), "Joinville", 3, "Competição fitness", 170, 66),
    ("Gustavo Nunes Carvalho", "M", (1990, 3, 28), "Campinas", 1, "Saúde e qualidade de vida", 172, 85),
    ("Beatriz Gomes Araújo", "F", (2004, 11, 14), "São Paulo", 1, "Tonificar o corpo", 163, 55),
]

OBJETIVOS_EMAGRECER = ("Emagrecimento", "Tonificar o corpo", "Definição muscular")


def cpf_valido(base):
    """Gera um CPF com dígitos verificadores corretos a partir de 9 dígitos."""
    digitos = [int(d) for d in f"{base:09d}"]
    for tamanho in (9, 10):
        soma = sum(d * (tamanho + 1 - i) for i, d in enumerate(digitos))
        digitos.append((soma * 10 % 11) % 10)
    return "".join(map(str, digitos))


def arredondar(valor, passo=2.5):
    return round(valor / passo) * passo


class Command(BaseCommand):
    help = "Popula um banco vazio com administrador, professores, alunos e treinos fictícios."

    def add_arguments(self, parser):
        parser.add_argument("--semente", type=int, default=2024, help="Semente para gerar dados repetíveis.")

    @transaction.atomic
    def handle(self, *args, **opcoes):
        if Pessoa.objects.exists():
            raise CommandError("O banco já tem pessoas cadastradas. Rode em um banco recém-migrado.")

        self.rnd = random.Random(opcoes["semente"])
        self.hoje = timezone.localdate()
        self.proximo_cpf = 123456000

        # Garante os grupos mesmo que a migração de dados não tenha rodado.
        for nome in ("Administrador", "Professor", "Aluno"):
            Group.objects.get_or_create(name=nome)

        self.cidades = self.criar_localidades()
        admin = self.criar_pessoa(*ADMINISTRADOR, "ADMINISTRADOR")
        admin.usuario.is_staff = admin.usuario.is_superuser = True
        admin.usuario.save()
        professores = [self.criar_pessoa(*p, "PROFESSOR") for p in PROFESSORES]
        self.categorias = {n: Categoria.objects.create(nome=n) for n in CATALOGO}
        self.exercicios = self.criar_exercicios(professores[0])

        alunos = []
        for i, (nome, sexo, nasc, cidade, nivel, objetivo, altura, peso) in enumerate(ALUNOS):
            professor = professores[i % len(professores)]
            aluno = self.criar_pessoa(
                nome, sexo, nasc, cidade, "ALUNO",
                nivel=nivel, objetivo=objetivo, professor=professor,
            )
            alunos.append(aluno)
            self.criar_medidas(aluno, professor, altura, peso)
            treinos = self.criar_treinos(aluno, professor)
            self.criar_cargas(treinos)
            self.criar_agenda(aluno, professor, treinos, i)

        self.criar_transferencias(alunos, professores)

        self.stdout.write(self.style.SUCCESS(
            f"Banco populado: 1 administrador, {len(professores)} professores, {len(alunos)} alunos."
        ))
        self.stdout.write("Login de todos: usuário = CPF e senha = CPF.")
        for p in Pessoa.objects.order_by("tipo", "nome"):
            self.stdout.write(f"  {p.get_tipo_display():<14} {p.cpf}  {p.nome}")

    def criar_localidades(self):
        cidades = {}
        for (nome, sigla), lista in ESTADOS.items():
            estado = Estado.objects.create(nome=nome, sigla=sigla)
            for cidade in lista:
                cidades[cidade] = Cidade.objects.create(nome=cidade, estado=estado)
        return cidades

    def criar_pessoa(self, nome, sexo, nasc, cidade, tipo, nivel=None, objetivo=None, professor=None):
        self.proximo_cpf += 1137
        cpf = cpf_valido(self.proximo_cpf)
        usuario = User.objects.create_user(username=cpf, password=cpf)
        usuario.groups.add(Group.objects.get(name=tipo.capitalize()))
        telefone = f"(44) 99{self.rnd.randint(100, 999)}-{self.rnd.randint(1000, 9999)}"
        return Pessoa.objects.create(
            tipo=tipo, nome=nome, sexo=sexo, data_nascimento=date(*nasc), cpf=cpf,
            telefone=telefone, cidade=self.cidades[cidade],
            nivel=nivel, objetivo=objetivo, professor=professor, usuario=usuario,
        )

    def criar_exercicios(self, autor):
        return {
            nome: Exercicio.objects.create(
                nome=nome, categoria=self.categorias[categoria], descricao=descricao, cadastrado_por=autor,
            )
            for categoria, itens in CATALOGO.items()
            for nome, descricao, _ in itens
        }

    def criar_medidas(self, aluno, professor, altura, peso):
        # Uma medição mensal nos últimos 6 meses, com evolução gradual.
        emagrecer = aluno.objetivo in OBJETIVOS_EMAGRECER
        for mes in range(5, -1, -1):
            progresso = 5 - mes
            delta_peso = -0.9 * progresso if emagrecer else 0.5 * progresso
            ganho = 0 if emagrecer else 0.3 * progresso
            Medidas.objects.create(
                aluno=aluno, altura=altura, peso=round(peso + delta_peso, 1),
                cintura=round(altura * 0.46 + (peso - 70) * 0.25 + (delta_peso if emagrecer else 0), 1),
                quadril=round(altura * 0.55 + (peso - 70) * 0.2, 1),
                braco_direito=round(altura * 0.19 + ganho, 1), braco_esquerdo=round(altura * 0.188 + ganho, 1),
                coxa_direita=round(altura * 0.32 + ganho, 1), coxa_esquerda=round(altura * 0.318 + ganho, 1),
                panturrilha_direita=round(altura * 0.21, 1), panturrilha_esquerda=round(altura * 0.209, 1),
                peito=round(altura * 0.55 + (peso - 70) * 0.2 + ganho, 1),
                data_medida=self.hoje - timedelta(days=30 * mes + self.rnd.randint(0, 4)),
                cadastrado_por=professor.usuario,
            )

    def criar_treinos(self, aluno, professor):
        if aluno.nivel == 1:
            modelo = TREINOS_INICIANTE
        else:
            modelo = TREINOS_FEMININO if aluno.sexo == "F" else TREINOS_MASCULINO

        # Ciclo anterior (encerrado) para ter histórico, e ciclo atual em andamento.
        ciclos = [(self.hoje - timedelta(days=120), self.hoje - timedelta(days=61)),
                  (self.hoje - timedelta(days=60), self.hoje + timedelta(days=30))]
        atuais = []
        for inicio, fim in ciclos:
            for nome, (descricao, itens) in modelo.items():
                treino = Treino.objects.create(
                    aluno=aluno, nome_treino=nome, data_inicio=inicio, data_fim=fim,
                    descricao=descricao, cadastrado_por=professor,
                )
                for exercicio, series, reps, descanso in itens:
                    ExercicioTreino.objects.create(
                        treino=treino, exercicio=self.exercicios[exercicio], series=series,
                        repeticoes=reps, descanso=descanso,
                        peso_atual=self.carga_inicial(aluno, exercicio), cadastrado_por=professor,
                    )
                if fim >= self.hoje:
                    atuais.append(treino)
        return atuais

    def carga_inicial(self, aluno, exercicio):
        base = next(c for itens in CATALOGO.values() for n, _, c in itens if n == exercicio)
        fator = {1: 0.6, 2: 1.0, 3: 1.3}[aluno.nivel] * (0.55 if aluno.sexo == "F" else 1.0)
        return arredondar(base * fator) if base else 0

    def criar_cargas(self, treinos):
        # Evolução semanal de carga nos exercícios do treino atual.
        for treino in treinos:
            for item in treino.exercicio_do_treino.all():
                if item.peso_atual <= 0:
                    continue
                carga = item.peso_atual
                for semana in range(7, 0, -1):
                    HistoricoCarga.objects.get_or_create(
                        aluno=treino.aluno, exercicio=item.exercicio,
                        data=self.hoje - timedelta(weeks=semana),
                        defaults={"carga": carga, "registrado_por": treino.aluno.usuario},
                    )
                    carga = arredondar(carga * self.rnd.choice([1, 1, 1.025, 1.05]))
                item.peso_atual = carga
                item.save(update_fields=["peso_atual"])

    def criar_agenda(self, aluno, professor, treinos, indice):
        # 3 aulas por semana; o horário muda a cada 3 alunos para não conflitar no mesmo professor.
        dias = [(1, 3, 5), (2, 4, 6)][indice % 2]
        hora = time(6 + (indice // 3) * 2, 0)
        for dia, treino in zip(dias, cycle(treinos)):
            HorarioAula.objects.create(
                aluno=aluno, professor=professor, dia_semana=dia, horario=hora, treino=treino,
            )

    def criar_transferencias(self, alunos, professores):
        a1, a2 = alunos[0], alunos[1]
        TransferenciaAluno.objects.create(
            aluno=a1, professor_atual=a1.professor,
            professor_novo=next(p for p in professores if p != a1.professor),
            origem="ALUNO", observacao="Mudança de horário de treino.",
        )
        TransferenciaAluno.objects.create(
            aluno=a2, professor_atual=a2.professor,
            professor_novo=next(p for p in professores if p != a2.professor),
            origem="PROFESSOR", status="RECUSADA", observacao="Reorganização de turmas.",
        )
