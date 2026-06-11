ESCOLA DE NEGÓCIOS, TECNOLOGIA E INOVAÇÃO DO

CESUPA

# TRABALHO DE PESQUISA E DESENVOLVIMENTO PARTE 1: SISTEMAS DE CONTROLE FUZZY

INTELIGÊNCIA ARTIFICIAL E COMPUTACIONAL (0700M8)_Prof. Daniel Leal Souza – Semestre: 01/2026_

| Disciplina Tema | Inteligência Artificial e Computacional: Ciência da Computação. Pesquisa, modelagem, implementação, validação, documentação técnica e |
| --- | --- |
| Conteúdos | apresentação de uma solução baseada em Sistemas de Controle Fuzzy. Lógica Fuzzy; conjuntos fuzzy; variáveis linguísticas; funções de pertinência; |
| mobilizados | fuzzificação; operadores fuzzy; base de regras; inferência; defuzzificação; sistemas Mamdani ; sistemas TSK ; validação por simulação; documentação |
| Formato | técnica; uso responsável de IA. Trabalho em equipe. Equipes de até 4 integrantes seguem os requisitos |

regulares. Equipes com **5 integrantes**, quando autorizadas, deverãocumprir uma tarefa de ampliação obrigatória, descrita nesta lauda.

| Pontuação regular Pontuação extra | 2,0 pts Até 0,5 pts opcionais , conforme o Plano de Ensino. , mediante entrega de uma extensão Neuro-Fuzzy ou |
| --- | --- |
| Entrega e | de otimização automática de parâmetros fuzzy com CC5MA: 09/06/2026 . CC5NA: 11/06/2026 . Submissão final no AG ou PSO . |
| apresentação | Google Classroom até 23h59 da data da respectiva turma, salvo orientação posterior do professor. |
| Entregáveis | Documento em PDF + link do repositório GitHub obrigatório + código-fonte + manual de execução + base de regras + funções de |

pertinência + resultados experimentais + slides + declaração de uso de IA.

# 1. Finalidade e perfil da atividade

_Esta atividade avalia a capacidade da equipe de_ pesquisar, modelar, implementar, validar,documentar e defender tecnicamente _uma solução baseada em_ sistemas de controle fuzzy_._

O trabalho deverá partir de um problema prático, científico, social, operacional, industrial, agrícola, educacional, comercial ou de apoio à decisão que envolva imprecisão, gradação de decisão, incerteza

qualitativa, julgamento linguístico ou controle aproximado.

O trabalho foi dimensionado para ser executável, com qualidade, em pouco mais de um mês. A expectativa não é a construção de um produto comercial completo, mas de um protótipo tecnicamente

consistente, reprodutível, bem documentado e defendido com domínio conceitual. Não será suficiente apenas executar um sistema ou uma biblioteca pronta: a equipe deverá explicar as variáveis, os

universos de discurso, as funções de pertinência, a base de regras, os operadores utilizados, o mecanismode inferência, o método de defuzzificação ou, no caso **TSK**, o cálculo ponderado da saída.

Durante a apresentação e a entrega do trabalho, será exigido de cada aluno o domínio dos conceitos apresentados no trabalho.

Todo trabalho deverá possuir um **repositório no GitHub**, criado e mantido pela equipe, contendo ocódigo-fonte, o documento ou instruções de execução, evidências mínimas de organização e o histórico

de desenvolvimento do projeto. O link do repositório deverá ser informado no documento principal e no Google Classroom. Repositórios privados serão aceitos apenas se o professor tiver acesso antes do

prazo final de entrega.

Página 1 de 10 08/05/2026

# 2. Resumo do trabalho

Cada equipe deverá escolher **exatamente uma** modalidade principal. As modalidades preservam aproposta original da atividade, mas foram reorganizadas para reduzir redundâncias e facilitar a leitura.

**Opção Foco Resultado esperadoA** Pesquisa e implementação Estudo de literatura, escolha de artigo(s), implementação de

de sistemas fuzzy baseados uma reprodução mínima ou adaptação fundamentada e em artigos científicos escrita em formato de artigo técnico/científico.

**B** Aplicação ou produto de Levantamento de problema real, requisitos, implementaçãomercado de protótipo funcional, documentação de produto, testes e

apresentação como solução aplicável.**C** Takagi-Sugeno-Kang (_TSK_) Execução da Opção A ou B usando _TSK_.

Nas opções A e B, o modelo padrão será **Mamdani**. Na opção C, dado que as regras exigem o usode Takagi-Sugeno-Kang como motor de inferência, as regras deverão possuir consequentes constantes,

lineares ou afins, por exemplo:

_Se_ _x__1_ é Alto _e_ _x__2_ é Baixo, _então_ _y_ **=** _a__0_ **+** _a__1__x__1_ **+** _a__2__x__2_.

# 3. Requisitos técnicos obrigatórios

A tabela abaixo reúne os requisitos mínimos. A equipe poderá ir além desses itens, desde que mantenha coerência e viabilidade.

**Dimensão Exigência mínimaProblema** O problema deve ser realista, claramente delimitado e adequado à lógica fuzzy.

Exemplos excessivamente simples, meras trocas de nomes em tutoriais ou repetições de sala sem expansão serão penalizados.

| Variáveis | valorizadas quando bem justificadas. Pelo menos 2 entradas e 1 saída . Soluções com 3 ou mais entradas serão |
| --- | --- |
| Termos linguísticos | Pelo menos 3 termos linguísticos na principal variável de entrada. No modelo Mamdani , pelo menos 3 termos linguísticos na saída. |
| Funções de pertinência | Devem ser apresentadas por gráficos, fórmulas, parâmetros ou tabelas. Podem ser triangulares, trapezoidais, gaussianas, sigmoides, bell-shaped, etc. |
| Base de regras | Pelo menos regras devem refletir literatura, conhecimento do domínio, dados, consulta a 12 regras efetivamente utilizadas, salvo justificativa técnica forte. As |

especialista ou análise própria._Inferência e_ Em **Mamdani**, explicar operadores, implicação, agregação e defuzzificação. Em

| saída | TSK equivalente. , explicar pesos das regras, consequentes e média ponderada ou procedimento |
| --- | --- |
| Testes | Pelo menos fronteiriços, conflitantes ou críticos. 6 cenários de teste , incluindo casos baixos, médios, altos, |
| Validação | A equipe deverá analisar o comportamento do sistema, não apenas listar saídas. Esperam-se tabelas, gráficos, superfícies de controle, mapas de decisão, curvas de |

sensibilidade ou comparação com referência.**Reprodução e** O código deve executar, o manual deve permitir reprodução e os resultados do

**consistência** relatório devem corresponder ao que foi implementado. O link do GitHub devepermitir acesso aos arquivos necessários para execução e avaliação.

**GitHub** Cada equipe deverá manter um repositório GitHub próprio, com acesso concedido**obrigatório** ao professor. O repositório deverá conter README, código-fonte, instruções de

execução, dependências, organização dos arquivos e, quando possível, histórico de commits compatível com o desenvolvimento do projeto.

Página 2 de 10 08/05/2026

# 4. O que caracteriza uma boa solução fuzzy?

_Uma solução fuzzy bem elaborada apresenta coerência entre_ problema_,_ variáveis_,_ universos dediscurso_,_ funções de pertinência_,_ base de regras_,_ mecanismo de inferência _e_ resultados_. A_

equipe deverá evitar sistemas artificiais, genéricos ou óbvios demais. Será valorizado o trabalho que demonstre que a lógica fuzzy foi escolhida por ser adequada ao problema, e não apenas porque era

exigida na atividade.

**Aspecto esperado Evidência de qualidade**Delimitação do problema A decisão, classificação, recomendação ou ação de controle é

| Entradas e saída | compreensível e tem utilidade no domínio escolhido. Cada variável tem papel explícito; variáveis irrelevantes ou artificiais são |
| --- | --- |
| Universos de discurso | evitadas. Intervalos, unidades, limites e hipóteses são declarados e coerentes com o |
| Pertinência | domínio. As funções não são estreitas a ponto de eliminar o caráter fuzzy, nem |
| Regras | largas a ponto de tornar o sistema indiferente. A base cobre casos típicos, intermediários, críticos e situações de conflito; |
| Análise crítica | as regras possuem justificativa. A equipe discute quando o sistema funciona bem, quando falha, quais |

parâmetros são sensíveis e que melhorias são possíveis. Organização no GitHub O repositório permite localizar código, documentação, resultados,

instruções de execução e artefatos relevantes sem depender de explicações externas.

4.1 Exemplos de problemas aceitáveis

Os exemplos abaixo são sugestões, não uma lista fechada: climatização inteligente; priorização de atendimento em saúde; risco de crédito, fraude ou inadimplência; controle de velocidade de robô ou

veículo autônomo; irrigação agrícola com múltiplas variáveis e expansão substancial; avaliação de risco em projetos; controle de estoque e reposição; manutenção preditiva; avaliação de desempenho

acadêmico; recomendação logística; precificação dinâmica; apoio à decisão em ambientes com múltiplos critérios.

_Exemplos muito parecidos com_ gorjetas, irrigação simples, ventilador básico, risco de projetocom apenas duas variáveis _ou_ qualquer exemplo apresentado em sala de aula _deverão_

apresentar **expansão clara significativa (dentro das regras estabelecidas acima)**. A equipedeve assegurar novas variáveis, nova validação, novas configurações e nova aplicação que as diferenciem

substancialmente dos exemplos apresentados em aula. Caso contrário, a nota poderá ser limitada e/ou sofrer penalidades.

Página 3 de 10 08/05/2026

# 5. Modalidades do trabalho

5.1 Opção A: Pesquisa em artigos científicos

Nesta modalidade, a equipe deverá conduzir levantamento bibliográfico sobre uso, aplicação ou melhoria de sistemas de controle fuzzy. O resultado deverá ser apresentado em formato de artigo técnico/científico,

seguindo padrão reconhecível de conferência, periódico ou relatório científico estruturado.

A equipe deverá pesquisar artigos científicos relacionados ao problema escolhido. O levantamento deverá incluir os seguintes pontos:

1. bases ou mecanismos utilizados na busca, tais como IEEE Xplore, ACM Digital Library, Science- Direct, SpringerLink, Scopus, Web of Science, Google Scholar ou repositórios equivalentes;
2. palavras-chave utilizadas; 3. critérios de inclusão e exclusão dos artigos;
4. justificativa para a escolha do artigo principal ou dos artigos principais utilizados como referência.
| Item Levantamento | O que entregar Bases ou mecanismos de busca utilizados; palavras-chave; critérios de |
| --- | --- |
| A1: Reprodução | inclusão/exclusão; tabela com pelo menos Escolher um artigo principal, explicar o problema, identificar 5 trabalhos relacionados . |

entradas/saídas/regras/pertinências, implementar uma reprodução mínima viável e comparar resultados.

A2: Adaptação Usar um ou mais artigos como base para construir uma solução própria, declarando o que foi reaproveitado, adaptado, expandido ou modificado.

Quando dados faltarem Declarar limitações de reprodução, justificar adaptações e apresentar uma reprodução mínima viável.

Estrutura mínima Título, autores, resumo, introdução, fundamentação teórica, trabalhos relacionados, metodologia, modelagem fuzzy, implementação, experimentos,

discussão, conclusão e referências.

5.2 Opção B: Aplicação ou produto baseado em controle fuzzy

Nesta modalidade, a equipe deverá construir uma solução apresentada como produto, protótipo ou ferramenta de apoio à decisão. O produto pode ser notebook interativo, aplicação web, dashboard, API,

aplicação desktop, aplicação mobile, simulador, sistema embarcado, interface em linha de comando bem documentada ou solução equivalente.

| Item Problema e | O que entregar Descrever o problema, quem usaria a solução, qual decisão o sistema apoia |
| --- | --- |
| público-alvo Requisitos | e por que a lógica fuzzy é adequada. Listar requisitos funcionais e não funcionais, entradas, saídas, fluxo de uso, |
| Protótipo | limitações e riscos de interpretação incorreta. Entregar uma versão funcional e demonstrável. Não é necessário produto |
| Documentação | comercial completo, mas a execução deve ser clara. Visão geral, arquitetura, modelo fuzzy, instalação, execução, manual de uso, |

exemplos de entrada/saída, testes, limitações, melhorias futuras e link do repositório GitHub.

Apresentação Defender a solução como produto: problema, usuário-alvo, diferencial, demonstração funcional, riscos, limitações e próximos passos.

Página 4 de 10 08/05/2026

5.3 Opção C: Sistema Fuzzy Takagi–Sugeno–Kang (TSK)

A Opção C consiste em executar a Opção A ou B usando **TSK**. A equipe deverá declarar _C-A_ quandoseguir a trilha de artigo científico, ou _C-B_ quando seguir a trilha de produto. Diferentemente de

**Mamdani**, as regras **TSK** não têm consequentes fuzzy como “saída baixa”, “saída média” ou “saídaalta”; elas têm consequentes constantes, lineares ou afins.

| Exigência TSK Antecedentes | Descrição Funções de pertinência nas entradas devem ser descritas como no |
| --- | --- |
| Consequentes | modelo fuzzy usual. Cada regra deve produzir uma função constante, linear ou afim das |
| Peso da regra | entradas. Explicar como o grau de ativação de cada regra foi calculado. |

Saída final Explicar o cálculo por média ponderada ou método equivalente.Comparação recomendada Discutir, conceitual ou experimentalmente, diferenças entre **TSK** e

**Mamdani**: interpretabilidade, continuidade da saída, facilidade deajuste e custo computacional.

# 6. Equipes, participação e tarefa extra para equipes com 5 integrantes

O formato regular é de até **4 integrantes**. Em caráter excepcional, uma equipe poderá ter **5integrantes**; nesse caso, a ampliação de equipe deverá ser acompanhada de ampliação objetiva do

trabalho. A regra busca preservar proporcionalidade entre quantidade de alunos e volume de entrega.

Equipes com 5 integrantes deverão cumprir, além dos requisitos mínimos, **uma trilha obrigatória deampliação** dentre as opções abaixo. Essa tarefa não é a mesma coisa que a pontuação extra opcional;

ela é condição para que a equipe ampliada seja avaliada sem desvantagem por divisão excessiva de tarefas.

Trilha de ampliação Tarefa adicional obrigatória para equipe com 5 integrantesAmpliação técnica do _Usar no mínimo_ 3 entradas_, pelo menos_ 18 regras _e no mínimo_ 12

| modelo | cenários de teste função de pertinência. , incluindo análise de sensibilidade de pelo menos uma |
| --- | --- |
| Comparação de modelos | Implementar ou simular uma comparação entre duas versões: por exemplo, Mamdani versus TSK , ou duas bases de regras/funções de |
| Validação ampliada | pertinência, discutindo diferenças de saída. Realizar validação com dados reais, sintéticos controlados ou consulta |

estruturada a especialista/usuário, apresentando tabela de comparação entre expectativa e saída do sistema.

**Produto ampliado** Na Opção B, entregar interface mais completa, registro delogs/experimentos, exportação de resultados ou módulo de configuração

de parâmetros pelo usuário.

Todos os integrantes devem compreender o projeto. Durante a apresentação, o professor poderá direcionar perguntas a qualquer aluno. A ausência de domínio conceitual por parte de um integrante

poderá afetar a nota individual de apresentação, mesmo que o produto funcione.

Página 5 de 10 08/05/2026

# 7. Pontuação extra opcional: até 0,5 pts

A pontuação extra é opcional, não substitui os requisitos regulares e somente será considerada se otrabalho principal estiver funcional e minimamente completo. A equipe poderá escolher **uma** das duas

opções abaixo.

**Opção extra O que deve ser feito1. Neuro-Fuzzy** Pesquisar e implementar uma extensão Neuro-Fuzzy, demonstrando como

redes neurais, aprendizado supervisionado ou ajuste de parâmetros podem se conectar ao sistema fuzzy. A equipe deverá explicar a arquitetura, o

| 2. Otimização de | fluxo de dados, o que foi aprendido/ajustado e quais limitações existem. Fazer conexão com Computação Evolutiva implementando otimização |
| --- | --- |
| Hiperparâmetros com AG ou PSO | automática de parâmetros fuzzy com limites das funções de pertinência, pesos de regras, consequentes AG ou PSO . Podem ser ajustados TSK ou |

parâmetros equivalentes. A equipe deverá definir função objetivo, representação da solução, critérios de parada e comparação antes/depois.

| 3. Implementação de artigos com | Utilize bases de dados renomadas como Web of Science (JCR), Scopus ou Google Acadêmico, focando em periódicos com alto Journal Impact Factor |
| --- | --- |
| elevado fator de impacto | (JIF). A busca deve ser refinada por área do conhecimento no Journal Citation Reports (JCR) para comparar revistas. Para a plataforma Qualis, |

pesquisar por artigos classificados como A1, A2, A3 ou A4 nas áreas de Computação ou Engenharias IV (Engenharia de Computação).

A pontuação extra será atribuída conforme qualidade técnica, integração com o sistema principal, clareza da explicação e evidências experimentais. Entrega superficial, apenas conceitual ou desconectada

do projeto não receberá pontuação extra.

# 8. Entregáveis obrigatórios e repositório GitHub

A submissão final deverá conter os arquivos solicitados e o **link do repositório GitHub do projeto**.O repositório é obrigatório para todas as equipes e faz parte da avaliação. Recomenda-se nomear

arquivos, pastas e commits de forma clara, incluindo turma, equipe, opção escolhida e finalidade de cada artefato.

8.1 Regras mínimas para o GitHub

**Item Exigência mínimaAcesso** O repositório deve ser público ou privado com acesso concedido ao professor

até o prazo final. Link quebrado, repositório inacessível ou permissão não concedida será tratado como ausência de GitHub.

| README | Deve conter título do projeto, turma, integrantes, modalidade escolhida, resumo da solução, tecnologias usadas, instruções de instalação, execução, |
| --- | --- |
| Organização | reprodução dos testes e descrição dos principais arquivos. O repositório deve separar, quando aplicável, código-fonte, notebooks, dados |

ou amostras, documentação, resultados, imagens, slides e relatório. Arquivos soltos e sem identificação serão penalizados.

**Reprodutibilidade** Devem estar presentes dependências, versão de bibliotecas, comandos deexecução ou notebook executável. Quando dados completos não puderem ser

publicados, a equipe deverá fornecer amostra, dados sintéticos ou instruções claras de obtenção.

**Coerência** O conteúdo do GitHub deve corresponder ao relatório, à apresentação e àdemonstração. Código que não corresponde ao sistema apresentado será

penalizado.

Página 6 de 10 08/05/2026

8.2 Lista de entregáveis

**Entregável Conteúdo mínimoDocumento** Relatório, artigo ou documentação de produto em PDF, contendo problema,

| principal | fundamentação, metodologia, modelagem fuzzy, implementação, resultados, discussão, referências e link do GitHub. |
| --- | --- |
| Repositório GitHub | Link obrigatório do repositório contendo README, código-fonte, instruções de execução, dependências, artefatos relevantes e organização compatível com o |

trabalho entregue.**Código-fonte** Arquivos organizados, executáveis e compatíveis com o que foi descrito no

documento, preferencialmente mantidos no GitHub. O código deve conter comentários suficientes para compreensão.

**Manual de** Instruções para instalar dependências, configurar ambiente, executar o sistema e**execução** reproduzir os principais resultados.

_Base de_ Tabela explícita com todas as regras. Em **TSK**, incluir os consequentes e a forma_regras_ de cálculo da saída.

**Funções de** Gráficos, fórmulas, parâmetros ou tabelas das funções de pertinência, com**pertinência** universos de discurso e unidades.

**Cenários de** Tabela com entradas, saída produzida, interpretação e comentário sobre coerência**teste** do resultado.

**Evidências** Prints, logs, notebooks executados, capturas de tela, gráficos, superfícies de**de execução** controle, vídeos curtos opcionais ou outputs reprodutíveis.

**Slides** Arquivo em PDF ou link acessível com a apresentação. Slides devem apoiar adefesa técnica, não substituir a demonstração.

**Declaração** Seção ou documento específico indicando ferramenta, finalidade, prompts**de uso de IA** resumidos, partes aproveitadas e revisão humana.

**Referências** Artigos, livros, documentação técnica, bases de dados, tutoriais e ferramentasutilizadas, citados de forma consistente.

# 9. Declaração obrigatória de uso de IA

O uso de IA generativa, IA agêntica, assistentes de programação, ferramentas de autocompletar código, geradores de texto, ferramentas de busca assistida ou agentes de desenvolvimento é permitido. A

equipe, entretanto, deverá declarar o uso com transparência e demonstrar revisão humana.

Ferramenta Finalidade Prompt/comando Revisão crítica da equipe resumido

Ex.: ChatGPT, Ex.: revisar texto, Descrever resumidamente, Explicar o que foi aceito, Gemini, Copilot, gerar esboço de sem copiar conversas corrigido, rejeitado, testado

Claude, Cursor código, depurar erro, completas. ou validado. etc. sugerir regras.

Declarar o uso de IA não reduz a nota. O que reduz a nota é usar IA sem compreender, sem revisar, sem validar, sem citar fontes ou sem declarar. Quando a IA for usada para gerar código, documentação

ou testes, a equipe deverá garantir que o material presente no GitHub tenha sido revisado, executado e validado pelos integrantes.

Página 7 de 10 08/05/2026

# 10. Estrutura recomendada para o documento principal

A estrutura poderá variar conforme a modalidade escolhida, mas deverá permitir avaliação técnica clara. Recomenda-se a estrutura abaixo:

| Parte 1 | Conteúdo Capa ou cabeçalho com título, turma, equipe, integrantes, opção escolhida e link do |
| --- | --- |
| 2 | repositório GitHub. Resumo, introdução, motivação, descrição do problema e justificativa para uso de |
| 3 | lógica fuzzy. Fundamentação teórica e, conforme a opção, trabalhos relacionados ou análise de |
| 4 | mercado/requisitos. Metodologia, modelagem fuzzy, variáveis, universos de discurso, funções de pertinência |
| 5 | e base de regras. Implementação, arquitetura do sistema, dependências, estrutura do GitHub, interface |
| 6 | ou modo de execução. Experimentos, cenários de teste, resultados, gráficos/tabelas, análise crítica e |
| 7 | limitações. Conclusão, trabalhos futuros, declaração de uso de IA, referências e apêndices. |

# 11. Rubrica de avaliação (0,0–2,0 pts)

A tabela abaixo descreve os critérios de avaliação a serem utilizados durante o trabalho. O peso de cada critério orienta a avaliação, mas o professor poderá considerar a coerência global do trabalho,

a dificuldade da solução escolhida e a qualidade da defesa oral. Em todos os casos, a equipe deverá demonstrar domínio conceitual, funcionamento do sistema, análise crítica e organização mínima do

projeto no GitHub.

**Critério Peso Como será avaliado1. Escolha do 0,25** Relevância do problema, justificativa do uso de fuzzy, pesquisa

**problema e** bibliográfica ou análise de mercado, qualidade das fontes, clareza**fundamentação** das hipóteses e delimitação do escopo.

**2. Modelagem 0,40** Coerência das entradas e saídas, universos de discurso, termos**fuzzy** linguísticos, funções de pertinência, regras, operadores, inferência,
defuzzificação ou cálculo **TSK**. Avalia-se mais a consistênciatécnica do que a quantidade mecânica de elementos.

**3. Implementação 0,30** Sistema funcional, código organizado, execução reproduzível,**e funcionamento** compatibilidade entre relatório e implementação, clareza do
manual, qualidade da demonstração e consistência com o código publicado no GitHub.

| 4. Experimentos e análise | 0,30 | Cenários de teste, casos extremos/fronteiriços, tabelas e gráficos, interpretação dos resultados, discussão de limitações, análise de |
| --- | --- | --- |
| 5. Documento | 0,20 | sensibilidade ou comparação com referência. Estrutura, clareza, linguagem técnica, completude, figuras e |

**escrito** tabelas, referências, adequação ao formato escolhido: artigo,relatório técnico ou documentação de produto.

| 6. Apresentação, demonstração e | 0,35 | Organização da exposição, demonstração funcional, participação dos integrantes, domínio conceitual e capacidade de responder |
| --- | --- | --- |
| arguição 7. GitHub, | 0,20 | perguntas técnicas sem depender apenas da leitura de slides. Existência e acessibilidade do GitHub; README; organização de |

| reprodutibilidade, integridade e uso | arquivos; instruções de execução; compatibilidade entre código, relatório e apresentação; histórico ou evidência de desenvolvimento; |
| --- | --- |
| de IA | declaração de uso de IA; referências corretas e honestidade metodológica. |

Página 8 de 10 08/05/2026

11.1 Faixas qualitativas de desempenho

**Faixa InterpretaçãoExcelente** Trabalho funcional, bem modelado, bem justificado, reprodutível, organizado no

GitHub e defendido com segurança. Apresenta análise crítica e evidências fortes.**Adequado** Atende aos principais requisitos, possui implementação funcional, documentação

suficiente e GitHub acessível, ainda que com limitações pontuais.**Parcial** Há implementação ou documentação, mas com lacunas relevantes em modelagem,

validação, clareza, GitHub ou domínio conceitual.**Insuficiente** O sistema não executa, a modelagem fuzzy é frágil, o GitHub está

ausente/inacessível, o relatório não permite avaliação técnica ou a equipe não consegue explicar o que entregou.

# 12. Penalidades, limites de nota e situações críticas

As penalidades poderão ser aplicadas cumulativamente, sempre considerando gravidade, reincidência, prejuízo à avaliação e evidências apresentadas. A lista abaixo orienta a correção, sem transformar a

avaliação em processo puramente mecânico.

**Situação Consequência possível**Ausência de sistema fuzzy funcional Redução severa de nota ou nota zero, dependendo do que

| Código ausente, não executável ou | foi entregue. Redução proporcional, podendo comprometer |
| --- | --- |
| incompatível com o relatório Repositório GitHub ausente, | implementação, GitHub e reprodutibilidade. Nota zero no critério de GitHub e reprodutibilidade. |
| inacessível, vazio ou sem permissão ao professor | Dependendo do prejuízo à avaliação do código, a nota final poderá ser limitada a 1,4 pts . |
| GitHub sem README, sem instruções de execução ou com organização | Redução no critério de GitHub, reprodutibilidade e implementação. Se o problema impedir execução ou |
| insuficiente Link do GitHub enviado | avaliação, outras penalidades poderão ser acumuladas. Tratado como entrega incompleta ou fora do prazo, |
| incorretamente, quebrado ou apenas após o prazo | conforme a gravidade e as regras do Google Classroom. |

Base de regras arbitrária, pequena Redução na modelagem fuzzy e na análise técnica. demais ou sem relação com o domínio

Funções de pertinência sem Redução na modelagem e na documentação. justificativa, sem parâmetros ou sem

visualização Ausência de validação experimental Redução relevante em experimentos e discussão crítica.

| Trabalho muito parecido com exemplo de sala ou tutorial público | Nota poderá ser limitada a literal, poderá ser atribuída nota zero. 1,2 pts ; em caso de cópia |
| --- | --- |
| Uso de IA sem declaração ou sem compreensão | Redução proporcional; se houver autoria falsa, plágio ou falsificação, poderá haver nota zero. |
| Integrante sem participação ou sem domínio mínimo na apresentação | Redução individual na parte de apresentação/arguição, a critério do professor. |
| Entrega fora do prazo | Sujeita às regras do Google Classroom e às orientações do professor. |

Similaridade entre trabalhos, Nota poderá ser limitada a **1,0 pts** conforme o grau deprotótipos, artigos idênticos escolhidos similaridade for estabelecido; em caso de cópia literal,

por mais de uma equipe poderá ser atribuída nota zero.

Página 9 de 10 08/05/2026

# 13. Checklist geral de entrega

| □ □ Equipe e opção escolhida identificadas. Entradas, saída e universos de discurso | □ □ Problema prático definido e justificado. Funções de pertinência especificadas e |
| --- | --- |
| □ definidos. Base de regras completa e justificada. | □ visualizadas. Inferência/defuzzificação ou cálculo TSK |
| □ Sistema implementado e funcional. | □ explicado. Cenários de teste executados e analisados. |
| □ □ Código-fonte organizado. README do GitHub completo. | □ □ Repositório GitHub criado e acessível. Manual de execução incluído. |
| □ □ Documento principal finalizado. Uso de IA declarado. | □ □ Slides preparados. Referências citadas corretamente. |
| □ Arquivos e link do GitHub submetidos no Classroom. | □ Todos os integrantes preparados para arguição. |

13.1 Checklists específicos por modalidade

| Opção A | □ escolha A1 ou A2 declarada; Artigos pesquisados; □ tabela com pelo menos 5 trabalhos relacionados; □ reprodução/adaptação implementada; □ □ |
| --- | --- |
| Opção B | comparação com literatura; □ Público-alvo definido; □ proposta de valor; □ artigo técnico/científico estruturado. □ requisitos; □ protótipo |

demonstrável; **□** documentação de produto; **□** GitHub com código e instruções deexecução; **□** apresentação com defesa técnica e demonstração.

_Opção C_ **□** Modalidade C-A ou C-B declarada; **□** regras com consequentes _TSK_; **□** cálculoponderado explicado; **□** adequação do _TSK_ justificada; **□** comparação conceitual

ou experimental com _Mamdani_ discutida._5 integrantes_ **□** Trilha de ampliação escolhida; **□** tarefa extra executada; **□** contribuição de

| Pontuação | cada integrante documentada; □ Opção Neuro-Fuzzy ou AG / □ PSO todos aptos à arguição. declarada; □ implementação integrada ao |
| --- | --- |
| extra | projeto; arquitetura explicada; □ código da extensão presente no GitHub; □ resultados antes/depois ou análise comparativa □ função objetivo ou |

apresentados.

# 14. Orientações finais

Serão valorizados trabalhos que demonstrem pesquisa real, modelagem fuzzy consistente, implementação funcional, validação experimental, organização no GitHub, boa comunicação técnica e domínio conceitual

durante a arguição. A equipe deve estar preparada para responder por que escolheu aquelas variáveis, por que as funções de pertinência são adequadas, por que as regras fazem sentido e como os resultados

devem ser interpretados.

A nota máxima será reservada a trabalhos suficientemente complexos, reproduzíveis, bem documentados, devidamente publicados no GitHub e defendidos com segurança. A equipe não precisa construir um

sistema perfeito; precisa construir uma solução fuzzy tecnicamente coerente, demonstrável, defensável, analisada com honestidade e compatível com o tempo disponível.

Página 10 de 10 08/05/2026
