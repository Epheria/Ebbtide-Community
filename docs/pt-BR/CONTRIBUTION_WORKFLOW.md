# Tarefas de tradução

> **Envio de gravações:** consulte o [guia de gravações no Drive privado (em inglês)](../VOICE_SUBMISSIONS.md). Após o envio e a marcação das caixas, outra pessoa ouve e aprova os arquivos antes da criação de um PR apenas com a lista de entregas. O áudio fica no Drive. As instruções abaixo são para tradução de texto.

Este guia foi traduzido com ajuda de IA. A [versão em inglês](../CONTRIBUTION_WORKFLOW.md) é a referência. Se você domina o português brasileiro, sugestões de melhoria são bem-vindas; esta versão não é apresentada como revisada por um falante nativo.

O Google Planilhas é o lugar para escrever e revisar traduções. Uma tarefa no GitHub reserva o trecho, registra os responsáveis e controla quando uma cópia revisada pode virar um pull request (PR).

**Editar a planilha não atualiza o repositório nem o jogo.** O bot coloca uma cópia exata do conteúdo revisado em um PR. Um responsável pelo repositório ainda precisa revisar e fazer o merge; depois, o desenvolvedor incorpora o resultado a uma versão do jogo.

Este processo atende textos de interface existentes (`ui`) e traduções escritas de roteiros de voz (`voice-text`). Gravações, testes de voz, falas novas e textos sem um ID de origem seguem processos próprios de preparação. A publicação deste guia não atribui tarefas: espere a confirmação do bot antes de começar.

As traduções da comunidade são entregues pelo PR criado pelo bot. Um PR de tradução aberto manualmente não pode pular a reserva nem a aprovação da cópia revisada.

## Quem faz o quê

| Pessoa | Responsabilidade |
| --- | --- |
| Colaborador (`Contributor`) | Escreve a tradução atribuída na planilha e solicita uma prévia. |
| Revisor (`Reviewer`) | Confere contexto, termos, naturalidade e a cópia exata. Aprova o hash usando sua própria conta do GitHub. |
| Responsável pelo repositório | Prepara ou confere a tarefa, reserva o trecho, administra o acesso à planilha, revisa o PR e faz o merge. |

Colaborador e revisor precisam ser **usuários diferentes do GitHub**. O bot confere identidade e estrutura dos arquivos; a qualidade da tradução fica a cargo de pessoas.

Você pode traduzir inteiramente no Google Planilhas, sem instalar Git, clonar o repositório ou criar seu próprio PR. Quem aprova a prévia precisa de uma conta do GitHub. Se precisar de ajuda para comentar no GitHub, um responsável pode solicitar a prévia por você.

## 1. Combinar uma tarefa pequena

Candidate-se pela issue de tradutor existente ou por um ticket de suporte no Discord. Antes do início, um responsável combina idioma, colaborador, revisor e trecho.

A planilha privada de candidatos serve apenas para receber e organizar inscrições. Ela não é o registro de reservas, e seu conteúdo não deve ser copiado para issues públicas.

Abra uma issue pelo formulário [Translation work order](https://github.com/Epheria/Ebbtide-Community/issues/new?template=work_order.yml), mantendo estes nomes de campo:

| Campo | O que preencher |
| --- | --- |
| Kind | `ui` ou `voice-text` |
| Locale | Código de idioma do repositório, como `ja`, `ru` ou `pt-BR` |
| Table or voice role | Nome de uma tabela ou de um papel de voz existente, sem caminho nem extensão `.csv` |
| Contributor | Um nome de usuário do GitHub, sem `@` |
| Reviewer | O nome de outro usuário do GitHub, sem `@` |
| Spreadsheet URL | Link da planilha usada na tarefa |
| Sheet tab | Nome exato da aba |
| First key | Primeira chave de origem existente a incluir |
| Last key | Última chave de origem existente a incluir |

O trecho inclui **as duas extremidades, na ordem do arquivo de origem do repositório**. Não é a ordem alfabética nem a ordem atual das linhas da planilha. O limite é de **200 chaves**. Nos roteiros de voz, a chave é o identificador `file`, sem `.wav` ou `.flac`.

Cada tarefa cobre um idioma e uma tabela de interface ou um papel de voz. Trechos pequenos são mais fáceis de revisar e causam menos conflitos quando o texto do jogo muda.

## 2. Reservar antes de traduzir

Um responsável comenta na issue:

```text
/work assign
```

Espere o bot confirmar a reserva. Preencher ou fechar uma issue, ou escrever um nome na planilha, não reserva nem libera trabalho.

O bot registra a atribuição em `registry.json`, na branch `community-work-state`. Ele fixa os campos da issue, as chaves exatas e o hash da origem. Um trecho não pode se sobrepor a outra tarefa ativa do mesmo tipo, idioma e tabela ou papel. Idiomas diferentes podem trabalhar nas mesmas chaves.

Editar o corpo da issue depois não muda a atribuição. Se o trecho, a planilha, o colaborador ou o revisor precisar mudar, peça a um responsável para liberar a tarefa e criar uma nova reserva corrigida.

## 3. Trabalhar na planilha

Um responsável fornece as linhas de origem atuais e concede acesso de edição às pessoas atribuídas. O bot precisa conseguir ler a planilha sem fazer login no Google, mas somente as pessoas que trabalham nela devem poder editá-la.

Proteja as chaves e o inglês de origem. Dê acesso apenas às células de entrada necessárias. Não ative “Qualquer pessoa com o link pode editar”. Os acessos e intervalos protegidos são configurados manualmente; o bot do GitHub não administra permissões do Google.

Para interface, preserve estas quatro colunas CSV:

```text
key,en,translation,status
```

A aba deve conter linhas de **uma única tabela**, a indicada na tarefa. Uma lista geral que reúne várias tabelas serve como referência, mas não pode ser importada diretamente como aba de trabalho. O bot confere todas as linhas preenchidas da aba com essa tabela de origem.

Edite `translation` e use os valores existentes de `status`. Uma linha de interface só está pronta para importar quando `status` fica **em branco**. Os valores `review` e `outdated` bloqueiam a linha. Um status em branco não é aprovação: a revisão independente ainda é obrigatória.

Para tradução escrita de roteiros de voz, preserve estes cabeçalhos exatos, nesta ordem:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

As abas atuais de japonês, russo e coreano usam esse formato. O bot filtra pelo valor exato de `Role`, como `carrier_jet_pilot`, e seleciona as chaves reservadas de `Take file`. Preencha `Translation` e marque as linhas revisadas como `Approved` em `Review status`.

O texto aprovado é gravado em `voice/translations/<locale>/<role>.csv`, com as colunas `key,en,translation,status`. Isso importa **somente texto escrito**. Não aprova gravações nem confirma que uma fala provisória já foi implementada no jogo.

Para os dois tipos de tarefa:

- Preserve variáveis, tags necessárias e códigos de quebra de linha.
- Mantenha a chave e o inglês idênticos à origem atribuída.
- Preencha todas as traduções do trecho antes de solicitar a prévia.
- Trate as células como texto. Não use fórmulas para buscar ou gerar traduções.
- Não coloque contatos privados, mensagens de tickets ou gravações de teste na planilha ou na issue pública.

Se não conseguir terminar uma tarefa, combine sua divisão ou liberação com um responsável. Evite manter um trecho parcialmente traduzido reservado por tempo indeterminado.

## 4. Solicitar e revisar uma prévia

O colaborador atribuído, o revisor atribuído ou um responsável comenta:

```text
/work preview
```

O bot lê o trecho reservado pela exportação CSV pública do Google Planilhas. Confere a origem fixada, os estados, as traduções não vazias e as variáveis necessárias. Também confere a tradução atual do repositório para detectar alterações feitas por outra pessoa antes da aprovação.

O bot salva uma cópia imutável e publica seu hash SHA-256 com um link de revisão. Confira **essa cópia**, não apenas o resumo da issue ou a planilha ao vivo. A planilha pode mudar depois da prévia.

O revisor confere:

- Significado e contexto em relação ao inglês.
- Naturalidade e consistência com o glossário.
- Espaço na interface ou forma de falar a frase, quando pertinente.
- Posição de variáveis, tags e quebras de linha.

Se precisar mudar algo, edite a planilha e execute `/work preview` de novo. Use o novo hash. O link da prévia serve para revisão, não autoriza o merge.

## 5. Aprovar a cópia exata

**Somente o revisor atribuído** comenta, substituindo `<sha256>` pelo hash completo da prévia:

Publique os comandos como comentários na issue da tarefa atribuída a você no GitHub. Para aprovar, copie todos os 64 caracteres após `Digest:` na resposta do bot à prévia e substitua somente `<sha256>` no exemplo; mantenha o comando em inglês e não envie esse marcador literalmente.

```text
/work approve <sha256>
```

O bot verifica quem aprovou, lê a planilha novamente e exige que ela corresponda à cópia revisada. Também confere se a origem e o arquivo de destino do repositório continuam iguais. Mudanças na planilha ou no destino exigem uma nova prévia. Uma mudança na tabela de origem exige uma nova atribuição, conforme explicado abaixo.

Se tudo estiver correto, o bot abre um PR com os arquivos validados. **Ele não faz o merge.** O valor `Approved` na planilha ou um comentário como “ficou bom” não substitui esse comando.

Um responsável confere as alterações e faz o merge depois que as verificações passam. Até lá, o trecho continua reservado. Mantenha no PR as conversas sobre os arquivos propostos.

A política confiável `reviewed-sheet` compara o PR com sua reserva e a cópia aprovada. Ela lê os arquivos do PR como dados e executa código confiável da branch padrão. Rejeita PRs manuais de tradução, alterações posteriores no arquivo entregue e arquivos extras junto da tradução. Editar uma branch do bot não permite trocar o texto aprovado.

## 6. Concluir ou liberar a reserva

Depois que o PR for mesclado ou fechado, um responsável executa:

```text
/work sync
```

Um PR mesclado conclui a tarefa; um PR fechado sem merge libera a reserva. Confira a confirmação do bot, em vez de presumir que o estado da issue mudou o registro.

O coordenador também sincroniza os PRs registrados do bot quando recebe o evento de fechamento do GitHub. Use `/work sync` se essa execução automática não terminar. Em um PR aberto, o mesmo comando solicita as verificações novamente, por exemplo se houve falha ao iniciá-las após a criação do PR.

Para cancelar uma atribuição antes de existir um PR, um responsável comenta:

```text
/work release
```

Se houver um PR aberto, feche-o antes de liberar a reserva. Assim não haverá duas entregas ativas para o mesmo trecho.

## Referência dos comandos

| Comando | Quem pode usar | Resultado |
| --- | --- | --- |
| `/work assign` | Responsável | Fixa a tarefa e reserva as chaves. |
| `/work preview` | Colaborador atribuído, revisor atribuído ou responsável | Valida e salva uma cópia para revisão. |
| `/work approve <sha256>` | Revisor atribuído | Confere novamente essa cópia e abre um PR. |
| `/work release` | Responsável | Cancela a reserva quando não há PR aberto. |
| `/work sync` | Responsável | Sincroniza o PR com o registro; se continuar aberto, solicita suas verificações de novo. |

## Quando o texto do jogo muda

Não crie uma planilha nova para cada versão do jogo. IDs estáveis permitem reaproveitar traduções quando a origem é atualizada. Adicione linhas pelo processo de atualização do repositório e marque traduções afetadas para revisão, como explica [Localização](../../localization/README.md).

A atribuição fixa uma cópia de **toda a tabela de interface ou de todo o papel de voz**. Se essa origem mudar antes da aprovação, a importação para, mesmo que as chaves reservadas não tenham mudado. Um responsável fecha qualquer PR de entrega aberto, libera a tarefa anterior, atualiza a origem na planilha e abre **uma nova issue de trabalho**. Preserve a tradução já feita e compare-a com a origem atualizada; o revisor então confere uma nova prévia. Tarefas de outras tabelas podem continuar.

Uma linha de planejamento sem ID real de origem ainda não pode ser importada. Mantenha-a no planejamento até o desenvolvedor adicionar a entrada de origem. Não invente IDs de produção nem envie uma planilha inteira só para incluir conteúdo futuro.

## Configuração e limites para responsáveis

Ative o processo só depois de seu código e do formulário estarem mesclados na branch padrão. O registro fica em `community-work-state`; não o edite manualmente enquanto comandos estiverem em execução.

O processo usa o `GITHUB_TOKEN` do repositório com permissões para gravar o estado e a branch do bot, comentar em issues e criar PRs. Não exige uma conexão Google OAuth nem um token de acesso pessoal. O acesso ao Google se limita à leitura do CSV público.

Nas configurações de Actions, permita que o GitHub Actions crie PRs. Mantenha a identidade do bot separada da pessoa que revisa o idioma.

Não dependa de um PR do bot iniciar automaticamente os processos `pull_request`. O importador valida os arquivos e solicita explicitamente `check.yml` na branch do bot e `delivery-policy.yml` na branch padrão confiável para aquele número de PR.

Proteja a branch padrão exigindo `check` e o status de commit `reviewed-sheet`. O processo de política precisa de permissão para publicar esse status. Verifique os dois antes do merge: criar os arquivos de automação não configura por si só a proteção de branches.

O registro impede atribuições sobrepostas, e a política obrigatória impede que PRs manuais ignorem essas atribuições. Nenhum deles controla os acessos do Google Planilhas: restrinja a edição e proteja as colunas de origem.

As verificações automáticas detectam problemas de estrutura e conteúdo desatualizado. Pessoas continuam responsáveis pela qualidade, contexto, termos de contribuição e adequação ao jogo.
