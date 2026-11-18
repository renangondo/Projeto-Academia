# Projeto Academia

Sistema Django para gestão de academia: alunos, professores, treinos, exercícios, medidas corporais, agenda de aulas e transferência de alunos entre professores.

## Requisitos

- Python 3.13
- Django 5.2
- django-braces

```bash
pip install django django-braces
```

## Perfis de acesso (grupos)

O sistema controla o acesso por **grupos do Django**. Os nomes precisam ser exatamente estes, pois o código os consulta pelo nome (`cadastros/permissoes.py`, `cadastros/context_processors.py` e `group_required` nas views):

| Grupo | Quem é | Acesso |
|---|---|---|
| `Administrador` | Gestão da academia | Tudo: estados, cidades, professores, alunos, exercícios |
| `Professor` | Instrutores | Seus alunos, treinos, medidas, agenda e transferências |
| `Aluno` | Alunos | Seus treinos, medidas, cargas e agenda |

Os grupos são criados **automaticamente pelo `migrate`**, por uma migração de dados (`cadastros/migrations/0002_grupos_iniciais.py`). Não é preciso cadastrá-los à mão.

> **Se criar um novo grupo ou renomear um existente**, atualize a migração de dados (ou crie uma nova) e o código que usa o nome, para não esquecer de cadastrá-lo em outro ambiente.

O usuário também é vinculado a uma `Pessoa` (`tipo` = `ALUNO`, `PROFESSOR` ou `ADMINISTRADOR`). O login usa o **CPF** como usuário. Alunos e professores criados pelo sistema recebem o CPF como senha inicial e são obrigados a trocá-la no primeiro acesso.

## Criar o banco do zero

Use estes passos para recomeçar com um banco limpo (por exemplo, quando o banco local ficou com registros inválidos).

```bash
# 1. Apague o banco
rm db.sqlite3

# 2. (Opcional) Recrie as migrações: apague os arquivos 0*.py de cada app e gere de novo.
#    Mantenha os __init__.py e a migração de grupos (cadastros/migrations/0002_grupos_iniciais.py).
python3 manage.py makemigrations

# 3. Crie as tabelas e os grupos
python3 manage.py migrate

# 4. Popule com dados fictícios (opcional, veja a seção abaixo)
python3 manage.py popular_banco
```

Se apagar as migrações do app `cadastros`, **recrie a migração dos grupos** (`0002_grupos_iniciais.py`), que depende de `cadastros.0001_initial`. Sem ela os grupos não são criados pelo `migrate`.

### Banco vazio, sem dados fictícios

Para usar o sistema de verdade, rode apenas o `migrate` e crie o primeiro administrador:

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

O superusuário acessa o Django Admin e passa nas verificações de administrador do sistema, mas **não tem uma `Pessoa` vinculada**. Para ele aparecer nas listas e usar todas as telas, cadastre pelo Django Admin (`/admin/`) uma `Pessoa` do tipo Administrador com o mesmo usuário, e adicione o usuário ao grupo `Administrador`.

## Dados fictícios (`popular_banco`)

```bash
python3 manage.py popular_banco
```

O comando só roda em banco **sem pessoas cadastradas** (ele recusa se já houver dados) e gera sempre os mesmos CPFs. A opção `--semente` altera a variação aleatória de telefones, medidas e cargas. Ele cria:

- 3 estados e 9 cidades
- 1 administrador, 3 professores e 10 alunos, cada um no grupo correspondente
- 11 categorias e 36 exercícios reais de musculação
- Treinos reais por perfil: ABC para homens, A/B/C com foco em inferiores para mulheres e Full Body para iniciantes, com um ciclo encerrado e um em andamento
- Medidas corporais mensais dos últimos 6 meses, histórico semanal de cargas e agenda de aulas
- 2 solicitações de transferência de aluno (uma pendente e uma recusada)

Ao final, o comando imprime os CPFs. **Todos fazem login com usuário = CPF e senha = CPF** (somente números). Os usuários do seed não são obrigados a trocar a senha no primeiro acesso. Os dados são fictícios; os CPFs gerados têm dígitos verificadores válidos, mas não pertencem a pessoas reais.

### Acessos para teste

Com a semente padrão, os CPFs são sempre os mesmos:

| Perfil | Nome | Usuário | Senha |
|---|---|---|---|
| Administrador | Marcos Antônio Ribeiro | `12345713747` | `12345713747` |
| Professor | Fernanda Cristina Lopes | `12345827408` | `12345827408` |
| Professor | Ricardo Almeida Tavares | `12345941103` | `12345941103` |
| Professor | Juliana Matos Ferreira | `12346054810` | `12346054810` |
| Aluno | Lucas Gabriel Souza | `12346168580` | `12346168580` |
| Aluno | Mariana Oliveira Costa | `12346282286` | `12346282286` |
| Aluno | Pedro Henrique Lima | `12346395994` | `12346395994` |
| Aluno | Ana Beatriz Santos | `12346509671` | `12346509671` |
| Aluno | Carlos Eduardo Pereira | `12346623377` | `12346623377` |
| Aluno | Camila Rodrigues Alves | `12346737038` | `12346737038` |
| Aluno | Rafael Martins Barbosa | `12346850780` | `12346850780` |
| Aluno | Larissa Fernandes Rocha | `12346964441` | `12346964441` |
| Aluno | Gustavo Nunes Carvalho | `12347078100` | `12347078100` |
| Aluno | Beatriz Gomes Araújo | `12347191853` | `12347191853` |

Cada aluno pertence a um professor: Fernanda (Lucas, Ana, Rafael e Beatriz), Ricardo (Mariana, Carlos e Larissa) e Juliana (Pedro, Camila e Gustavo).

## Executar

```bash
python3 manage.py runserver
```

Acesse http://localhost:8000/ e entre com um dos CPFs listados pelo `popular_banco`.

## Convenções do projeto

Componentes reutilizáveis, padrões de interface e commits estão descritos em [AGENTS.md](AGENTS.md) e nas skills em [.github/skills/](.github/skills).
