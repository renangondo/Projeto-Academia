---
name: cards-kpi
description: Use when building or editing KPI cards in this Django project, such as summary info, personal data, or key figures shown on detail and dashboard screens. Enforces the shared kpi-card component (colored icon, small uppercase label, strong value, hover lift) from static/css/global/kpi_cards.css.
---

# Cards KPI

Cards de indicador (KPI) do projeto usam um único componente global. Não crie CSS novo para esse tipo de card em telas específicas: use as classes abaixo.

O CSS já está carregado em `paginas/templates/modelo.html` (`static/css/global/kpi_cards.css`), então basta usar as classes no template.

## Estrutura

```html
<ul class="kpi-grid">
    <li class="kpi-card kpi-azul">
        <span class="kpi-icone"><i class="fa-solid fa-id-card"></i></span>
        <div class="kpi-conteudo">
            <span class="kpi-rotulo">CPF</span>
            <strong class="kpi-valor">{{ aluno.cpf_formatado|default:"-" }}</strong>
        </div>
    </li>
</ul>
```

- **`.kpi-grid`**: grade responsiva (`repeat(auto-fit, minmax(220px, 1fr))`). Use `<ul>` com `<li class="kpi-card">` para lista semântica.
- **`.kpi-card`**: o card. Recebe uma cor de tema (ver abaixo).
- **`.kpi-icone`**: círculo com o ícone Font Awesome 6 (`<i class="fa-solid fa-...">`), com fundo da cor do tema.
- **`.kpi-conteudo`**: bloco de texto ao lado do ícone.
- **`.kpi-rotulo`**: rótulo pequeno, em maiúsculas, em `<span>`.
- **`.kpi-valor`**: valor em destaque, em `<strong>`.

Quando o card estiver dentro de um container que já tem margem inferior (como o topo do detalhe), ajuste o espaçamento no CSS da tela, e não na classe global.

## Cores

Use uma cor por card. Escolha em ordem para não repetir na mesma grade quando possível:

| Classe | Uso sugerido |
| --- | --- |
| `kpi-azul` | dados principais, identificação |
| `kpi-verde` | contato, progresso positivo |
| `kpi-laranja` | datas, prazos |
| `kpi-roxo` | perfil, classificação |
| `kpi-rosa` | localização |
| `kpi-ciano` | vínculos, registros e metadados |

Não crie novas cores fora dessa lista. Se precisar de outra, adicione a classe em `kpi_cards.css` e atualize esta tabela.

## Ícones

- Use Font Awesome 6 Free, estilo `fa-solid`.
- Escolha um ícone que represente o dado (`fa-id-card` para CPF, `fa-phone` para telefone, `fa-location-dot` para cidade).
- Não repita o mesmo ícone em cards da mesma grade.

## Regras

- **Valor vazio:** sempre use `|default:"-"` (ou `{% if %}` para valores compostos, como a idade). Nunca deixe o valor em branco.
- **Datas:** formate com `|date:"d/m/Y"`.
- **Textos longos:** o `.kpi-valor` quebra linha (`overflow-wrap: anywhere`). Não limite com `nowrap`.
- **Hover:** já vem no componente (elevação de 3px com sombra suave). Não sobrescreva.
- **Não use** para cards de conteúdo com listas, gráficos ou ações (como cards de treino ou de medida). Esses cards têm estrutura própria.

## Como aplicar em uma tela nova

1. Monte o grid com `<ul class="kpi-grid">`.
2. Para cada indicador, escreva um `<li class="kpi-card kpi-<cor>">` com ícone, rótulo e valor.
3. Trate valores vazios com `|default:"-"`.
4. Não adicione CSS de card local. Se a tela precisar de espaçamento, use uma regra de contexto (ex.: `.minha-tela > .kpi-grid { margin-bottom: 35px; }`).

## Validação

- `python3 manage.py check` deve passar.
- Renderize a tela com o test client do Django e confirme que as classes `kpi-card`, `kpi-icone`, `kpi-rotulo` e `kpi-valor` aparecem no HTML.
- Confirme que nenhum valor vazio aparece em branco (deve aparecer `-`).
- Confira o visual no navegador com hard reload (Cmd+Shift+R), porque o CSS é cacheado.

## Exemplo de referência

`cadastros/templates/cadastros/detalhe_aluno.html`: cards de topo (Idade, Objetivo, Nível, Professor) e a seção "Dados pessoais".
