---
name: conventional-commits
description: Use when creating git commits in this repository. Formats commit messages following the Conventional Commits 1.0.0 spec (type(scope)!: description), with the required Co-authored-by trailer and without staging __pycache__ files.
---

# Conventional Commits

Toda mensagem de commit deste repositório segue a [Conventional Commits 1.0.0](https://www.conventionalcommits.org/pt-br/v1.0.0/).

## Formato

```
<tipo>(<escopo>)<!>: <descrição>

<corpo opcional>

<rodapé opcional>
```

- **tipo** (obrigatório, em minúsculo, em inglês):
  - `feat`: nova funcionalidade para o usuário
  - `fix`: correção de bug
  - `style`: apenas visual/CSS/HTML sem mudança de comportamento
  - `refactor`: reestruturação de código sem mudar comportamento
  - `perf`: melhoria de desempenho
  - `test`: criação ou ajuste de testes
  - `docs`: documentação (README, AGENTS.md, skills)
  - `chore`: manutenção (dependências, configuração, dados de seed)
  - `build`, `ci`: build e integração contínua
- **escopo** (opcional, minúsculo): app ou área afetada, por exemplo `cadastros`, `exercicio`, `medidas`, `agenda`, `usuarios`, `paginas`, `db`, `static`.
- **`!`** após o escopo marca mudança incompatível (breaking change). Explique no rodapé com `BREAKING CHANGE: ...`.
- **descrição**: resumo curto no imperativo, em português, sem ponto final, até ~72 caracteres. Exemplo: `feat(cadastros): adiciona ordenação nas tabelas de listagem`.
- **corpo**: explica o porquê quando não for óbvio. Quebre linhas em ~72 caracteres.

## Exemplos deste projeto

```
feat(static): adiciona ordenação por coluna nas tabelas de listagem
feat(paginas): adiciona menu de ações em dropdown nas listagens
feat(static): aplica máscaras de telefone e CPF nos formulários
fix(cadastros): redireciona para o detalhe do aluno após editar
style(cadastros): reorganiza botões da tela Meu perfil
chore(db): popula o banco com dados fictícios de teste
```

## Passo a passo

1. Veja o que mudou: `git status --short` e `git --no-pager diff`.
2. **Não inclua `__pycache__` nem arquivos `.pyc`** no commit. Eles são rastreados no git e aparecem como modificados; deixe-os fora do stage.
3. Agrupe por implementação: um commit por mudança lógica. Se um arquivo tiver trechos de duas mudanças, faça stage só dos trechos certos (`git add -p`).
4. Escolha tipo, escopo e descrição conforme acima.
5. Commit com a identidade do autor sem alterar a configuração global:

   ```
   git -c user.name="<nome>" -c user.email="<email>" commit -F <arquivo-de-mensagem>
   ```

   Use um arquivo de mensagem em `$TMPDIR` para preservar quebras de linha e acentos.
6. Inclua **sempre** o trailer no fim da mensagem, separado por uma linha em branco:

   ```
   Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
   ```

7. Confira com `git --no-pager log -1 --format='%s%n%an <%ae>'` e `git --no-pager show --stat HEAD`.

## Evite

- Mensagens genéricas como `ajustes`, `update`, `correções` ou `wip`.
- Misturar tipos num mesmo commit (ex.: `feat` + `refactor` + `chore` juntos).
- Usar `git commit --amend` ou reescrever commits já publicados sem pedido explícito.
- Alterar `git config --global`.
