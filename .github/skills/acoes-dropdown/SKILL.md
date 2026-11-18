---
name: acoes-dropdown
description: Use when adding or editing row actions (Editar, Excluir, Remover and similar) in list tables or list items in this Django project. Enforces the shared three-dot action dropdown from paginas/templates/_acoes_dropdown.html, with colored icons and fixed positioning so it is not clipped by overflow containers.
---

# Ações de linha em listas (dropdown)

Todas as listas do sistema usam o mesmo menu de ações: um botão com três pontinhos que abre um dropdown com as opções. O componente é global e já está carregado em `paginas/templates/modelo.html` (CSS e JS em `static/css/global/acoes_dropdown.css` e `static/js/global/acoes_dropdown.js`).

Não crie botões de ação soltos (ex.: `<a class="btn-editar">Editar</a>`) em listas. Use o partial.

## Uso

```django
{% url 'editar-aluno' aluno.pk as editar_url %}
{% url 'excluir-aluno' aluno.pk as excluir_url %}
{% include '_acoes_dropdown.html' with editar_url=editar_url excluir_url=excluir_url %}
```

Parâmetros do partial:

| Parâmetro | Obrigatório | Efeito |
| --- | --- | --- |
| `editar_url` | não | Mostra a opção "Editar" (azul). Omita se a linha não tem edição. |
| `excluir_url` | não | Mostra a opção "Excluir" (vermelha) como link. |
| `excluir_label` | não | Troca o texto da opção de exclusão (ex.: `excluir_label="Remover"`). Padrão: "Excluir". |
| `editar_label` | não | Troca o texto da opção de edição. Padrão: "Editar". |
| `excluir_bloqueado` | não | Sem `excluir_url`, mostra "Excluir" desativado com esse texto como dica (`title`). |

Regras de cor e ícone (já vêm no CSS, não sobrescreva):

- Editar: ícone `fa-pen` em azul `#2563eb`.
- Excluir / Remover: ícone `fa-trash` em vermelho `#dc2626`.
- Opção desativada: texto e ícone cinza, cursor `not-allowed`.

## Caso: exclusão bloqueada

Quando a exclusão depende de regra de negócio (ex.: categoria com exercícios), não omita a opção. Passe o motivo em `excluir_bloqueado`:

```django
{% url 'editar-categoria' categoria.pk as editar_url %}
{% if categoria.qtd_exercicios == 0 %}
{% url 'excluir-categoria' categoria.pk as excluir_url %}
{% endif %}
{% include '_acoes_dropdown.html' with editar_url=editar_url excluir_url=excluir_url excluir_bloqueado="Não é possível excluir: há exercícios nesta categoria" %}
```

## Caso: só uma ação

Use só o parâmetro que existir. Exemplo, histórico de cargas (só exclusão):

```django
{% url 'excluir-carga' r.pk as excluir_url %}
{% include '_acoes_dropdown.html' with excluir_url=excluir_url %}
```

Para a ação de "Remover" em uma linha de agenda, use `excluir_label="Remover"`.

## Onde o partial vai

- Dentro de um item de lista (`.item-acoes`, `.hc-lista li`, `.linha`), no mesmo lugar onde ficavam os botões antigos.
- O menu usa `position: fixed` e é posicionado pelo JS ao abrir, então não é cortado por `overflow: hidden` de cards ou `overflow-x: auto` de tabelas.
- Ao rolar a página ou redimensionar a janela, o menu fecha. Esc e clique fora também fecham.

## Exceção: botões com texto

Quando o usuário pediu explicitamente botões com texto, não use o dropdown. Exemplo: as duas ações de carga em `/exercicios/treino/7/` (`exercicio/templates/detalhe_treino.html`) são botões com texto ("Registrar carga" e "Ver histórico"), porque o ícone sozinho não deixa claro o que cada um faz.

Ações que não são edição nem exclusão (ex.: "Aceitar/Recusar" em transferências, "Ver treino") continuam como botões.

## Não use em

- Botões de ação de cards de conteúdo (ex.: "Editar" de uma medida no detalhe do aluno). Esses ficam como botão com texto.
- Ações principais de uma tela (ex.: "Editar meus dados" no perfil). Esses são botões com texto.

## Listas que usam o partial

- `cadastros/templates/cadastros/listar_alunos.html` (referência)
- `cadastros/templates/cadastros/listar_professores.html`
- `cadastros/templates/cadastros/listar_cidades.html`
- `cadastros/templates/cadastros/listar_estado.html`
- `exercicio/templates/listar_categoria.html`
- `exercicio/templates/listar_exercicio_categoria.html`
- `exercicio/templates/historico_cargas.html`
- `exercicio/templates/detalhe_treino.html` (ações por exercício)
- `medidas/templates/medidas/evolucao.html`
- `agenda/templates/agenda/agenda_professor.html`

## Validação

- `python3 manage.py check` deve passar.
- `node --check static/js/global/acoes_dropdown.js` deve passar.
- Renderize a tela com o test client do Django e confirme que `acoes-dropdown-toggle` aparece e que o link de editar/excluir tem a URL correta.
- Não deve sobrar `btn-editar`/`btn-excluir` em listas convertidas (use grep).
- Confira no navegador com hard reload (Cmd+Shift+R): o menu abre, não é cortado pelo card e fecha ao rolar.

## Exemplo de referência

`cadastros/templates/cadastros/listar_alunos.html`: tabela com `data-ordenavel`, coluna "Ações" com o partial, e a ação de editar/excluir.
