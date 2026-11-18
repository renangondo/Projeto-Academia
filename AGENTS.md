# AGENTS.md

Instruções para agentes de IA que trabalham neste repositório.

## Sobre o projeto

Projeto-Academia é um sistema web de gestão de academia, feito em Django. Interface e mensagens em português (pt-BR), fuso `America/Sao_Paulo`.

- **Stack:** Python 3.13, Django 5.2, SQLite (`db.sqlite3` na raiz), templates Django, CSS e JS puros.
- **Front-end externo (CDN):** Font Awesome 6.7.2 (ícones), jQuery 3.7.1 e jquery.mask 1.14.16 (máscaras).
- **Idioma do código:** nomes de models, views, variáveis e templates em português.

## Estrutura

| App | Responsabilidade |
| --- | --- |
| `Academia/` | Configurações do projeto (`settings.py`, `urls.py`) |
| `paginas/` | Layout base (`modelo.html`), menu, dashboards, partials globais |
| `cadastros/` | Pessoas (alunos, professores), cidades, estados, transferências, meu perfil |
| `exercicio/` | Exercícios, categorias, treinos e histórico de cargas |
| `medidas/` | Medidas corporais e evolução |
| `agenda/` | Horários de aula |
| `usuarios/` | Login, troca de senha e permissões de acesso |

- Templates ficam em `<app>/templates/<app>/`. O layout global e os partials ficam em `paginas/templates/`.
- CSS em `static/css/<app>/<tela>.css`. Estilos globais em `static/css/global/`.
- JS em `static/js/global/` (reutilizável) e `static/js/<app>/`.
- Permissões: grupos `Administrador`, `Professor` e `Aluno` (`cadastros/permissoes.py`).

## Comandos

```bash
python3 manage.py check            # validação do projeto
python3 manage.py test             # testes (os arquivos tests.py estão vazios hoje)
python3 manage.py runserver        # servidor local em http://localhost:8000
node --check static/js/global/<arquivo>.js   # sintaxe de JS
```

Em ambiente sem porta liberada, valide views com o test client do Django (`django.test.Client`, `HTTP_HOST='localhost'`).

## Dados de teste

- O banco já tem dados fictícios (professores, alunos, treinos, medidas, agenda).
- Login padrão: **usuário = senha = CPF** (11 dígitos, sem máscara). Admin: usuário `admin`.
- CPF e telefone são salvos só com dígitos. Use `cpf_formatado` e `telefone_formatado` para exibir.
- Antes de testar POST/escrita, use `transaction.atomic()` com rollback forçado. `savepoint_rollback` sozinho não desfaz o que foi salvo no shell.

## Convenções de interface

- **Tabelas de listagem:** ordenação por coluna é opt-in. Use `data-ordenavel` na `<table>` e `data-ordenar="false"` nas `<th>` que não devem ordenar (`static/js/global/ordenar_tabela.js`).
- **Ações de linha:** use o partial `paginas/templates/_acoes_dropdown.html` (ícone de três pontos), seguindo a skill `.github/skills/acoes-dropdown`. Editar em azul (`#2563eb`), excluir em vermelho (`#dc2626`).
- **Máscaras:** campos com `data-mascara="cpf"` ou `telefone` (ver `static/js/global/mascaras.js`). Datas não recebem máscara (são `type="date"`). Os valores são limpos para só dígitos antes do envio.
- **Formulários genéricos:** `cadastros/form.html` troca o título e o botão para "Editar" quando há objeto.
- **Cards KPI:** use o componente `kpi-card` (`static/css/global/kpi_cards.css`), seguindo a skill `.github/skills/cards-kpi`.

## Git e commits

- Commits seguem **Conventional Commits**. Use a skill `.github/skills/conventional-commits`.
- Inclua o trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
- Não faça stage de `__pycache__` nem `.pyc`: eles são rastreados e aparecem modificados sem motivo.
- Não altere `git config --global`. Passe a identidade do autor com `git -c user.name=... -c user.email=...`.

## Estilo de código

- Comente apenas trechos que precisem de explicação.
- Não faça mudanças fora do pedido. Corrija bugs apenas quando estiverem ligados à mudança.
- Atualize a documentação relacionada ao que mudou.
