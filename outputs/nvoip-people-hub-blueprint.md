# Nvoip People Hub - blueprint de produto

## Visao

Sistema proprio de RH com duas experiencias:

- Colaborador: acompanha apenas seus dados, responde pesquisas, reconhece colegas no mural publico, avalia parceiros liberados pelo gestor, solicita 1:1/feedback, atualiza perfil e acompanha PDI.
- Gestor/RH: cadastra colaboradores, define liderancas, controla quem avalia quem, ve resultados completos, acompanha People Analytics, 360, PDI, pesquisas, matcher comportamental e sinais de clima.
- RH/DP: area separada para cadastro operacional, admissoes, colaboradores ativos/inativos, dados de Departamento Pessoal, folha, contratacao e metricas cadastrais da empresa.

## Modulos do MVP

0. Digital Office
   - Ambiente virtual de trabalho da Nvoip, pensado para dar a sensacao de "entrar no escritorio".
   - Nao substitui a filosofia de RH; ele vira a camada operacional onde pessoas, contexto, reunioes e colaboracao acontecem.
   - Deve permitir encontrar pessoas, chegar em mesas, bater na mesa, entrar em salas, compartilhar contexto e resolver demandas sem trocar de sistema.
   - Nao deve usar webcam, mouse, teclado ou captura de tela para inferir atividade.

1. Autenticacao e primeiro acesso
   - Usuario administrador inicial do projeto: guilherme.faria@nvoip.com.br.
   - Senha inicial do administrador no prototipo: 123456.
   - A tela de login deve ser geral, nao "entrar como administrador"; o tipo de acesso vem do cadastro.
   - O botao de acesso deve ser "Entrar", pois usuarios cadastrados podem ser colaboradores, gestores ou administradores.
   - Esse administrador pode cadastrar colaboradores, lideres, diretores, RHs e outros administradores dentro do RH/DP.
   - Cadastro de usuario fica somente no modulo RH/DP, nao no People Hub.
   - Quem pode cadastrar: RH autorizado, lider com permissao de RH ou administrador.
   - Cadastro inicial do colaborador exige nome completo, email, funcao, setor, modalidade e data de contratacao.
   - Ao salvar o cadastro, o sistema gera um link de primeiro acesso dentro do proprio cadastro do colaborador.
   - Link de primeiro acesso expira em 12 horas.
   - Gestor/administrador pode gerar novo link quando necessario.
   - Primeiro acesso obriga criacao de senha antes de liberar o sistema.
   - Depois da troca, colaborador completa foto, apelido/nome preferido, dados cadastrais, nome do contato de emergencia, telefone do contato de emergencia e "sobre mim".
   - No primeiro acesso, colaborador preenche os dados obrigatorios de cadastro: endereco pessoal, nome completo, nome social, telefone, data de nascimento, estado civil, genero, raca/cor, orientacao sexual, escolaridade, curso/faculdade se estiver cursando, nome da mae, nome do pai, CPF, endereco atualizado, contato de emergencia com nome e telefone separados e tamanho de uniforme.
   - O administrador/RH define quais campos de perfil complementar tambem serao obrigatorios no primeiro acesso.

1.1. RH / Departamento Pessoal
   - Deve ficar em uma area propria, acessada por botao a partir do People Hub, com botao de retorno ao Hub.
   - Nao deve poluir a interface principal de cultura, comportamento e engajamento.
   - Ao entrar no RH/DP, a navegacao principal do People Hub deve sair de cena para evitar confusao.
   - O RH/DP deve ter menu interno proprio: visao geral, colaboradores, cadastro DP, contratacao, financeiro e permissoes.
   - Cada item do menu deve abrir um contexto enxuto, sem renderizar todos os blocos ao mesmo tempo.
   - O retorno ao People Hub deve ser tratado como breadcrumb/acao discreta, nao como botao pesado de destaque.
   - Mantem cadastro de todos os colaboradores ativos e inativos.
   - Permite cadastrar colaborador que nao e gestor, mas e RH.
   - Papéis principais: colaborador, lider, diretor, RH e administrador.
   - Grupos de permissao padrao: colaborador, lider, RH, lider de RH, diretor e admin.
   - A aba Permissoes do RH/DP configura o modelo de permissao de cada grupo.
   - Ao cadastrar colaborador, selecionar um grupo aplica automaticamente o conjunto padrao de funcionalidades.
   - O cadastro do colaborador pode ter excecoes individuais sobre o modelo do grupo.
   - Papeis podem ser combinados quando fizer sentido, por exemplo lider + RH, representado pelo grupo "lider de RH".
   - Lider deve permitir selecionar multiplos liderados.
   - Diretor deve permitir selecionar quais lideres ele lidera.
   - Diretor acessa dados dos lideres sob sua responsabilidade e dos colaboradores ligados a esses lideres.
   - Lideres e diretores tambem podem pedir feedback, dar feedback e solicitar 1:1 dentro da cadeia de relacao definida.
   - RH tem a mesma experiencia base de colaborador, com acesso adicional ao RH/DP conforme permissao.
   - Administrador tem acesso total a cadastros, dados, evolucao da empresa e configuracoes.
   - Acesso RH pode ser concedido com permissoes financeiras separadas: folha de pagamento, bonificacoes, comissoes e PLR.
   - Para colaborador criado direto no cadastro RH/DP, o primeiro acesso coleta apenas o conjunto obrigatorio definido no fluxo de cadastro.
   - O formulario completo da planilha deve ficar no fluxo de processo seletivo/candidato, nao no cadastro manual de usuario.
   - Para novos processos seletivos, candidato aprovado recebe link de cadastro DP antes da admissao.
   - Metricas desta area sao da empresa e do cadastro: headcount, ativos, inativos, admissoes, desligamentos, links pendentes, turnover, custos e status de documentacao.

1.2. Contratacao
   - RH cria vagas, etapas, responsaveis e pipeline de candidatos.
   - Processo seletivo acompanha triagem, entrevista, proposta, aprovado, reprovado e admissao.
   - Ao aprovar candidato, sistema cria pre-cadastro e link DP.
   - Historico do processo deve ficar ligado ao colaborador depois da admissao.

1.3. Ponto, ferias e folha
   - Colaborador registra ponto no People Hub: entrada, saida para almoco, retorno do almoco, saida cafe manha, retorno cafe manha, saida cafe tarde, retorno cafe tarde e fim do expediente.
   - Colaborador pode anexar atestados, justificar atrasos e solicitar correcao de esquecimento de ponto.
   - Indicadores do colaborador mostram banco de horas, atrasos no mes e redflags de recorrencia.
   - Estagiarios nao podem gerar banco de horas; o sistema deve destacar essa regra para RH.
   - Colaborador pode lancar pretensao de ferias.
   - Ferias podem ser solicitadas em 3 periodos de 10 dias, 2 periodos de 15 dias ou 1 periodo de 30 dias.
   - Ferias nao podem iniciar em sexta-feira nem em vespera de feriado.
   - Pretensao de ferias vai para aba Ferias no RH/DP, com aprovacao ou recusa e comentario do lider.
   - RH/DP deve mostrar ferias a vencer, colaboradores com atestado, atrasos recorrentes e banco de horas como prioridades.
   - RH/DP deve ter modulo de folha de pagamento com espelho de ponto, banco de horas, atestados, atrasos e extracao de relatorios.

2. Mural publico
   - Reconhecimentos nominais e visiveis para todos.
   - Foto, nome, horario, texto, emojis e reacoes.
   - Sem anonimato.

3. Avaliacao anonima de parceiros
   - Gestor define, no cadastro do usuario, quais colaboradores podem ser avaliados por cada pessoa.
   - Colaborador ve apenas os parceiros liberados.
   - Gestor/RH ve consolidado anonimo por colaborador avaliado.
   - O colaborador nunca ve resultados, autoria ou respostas de avaliacoes feitas por parceiros.
   - O gestor ve somente avaliacoes dos colaboradores sob sua responsabilidade, salvo liberacao de RH/administrador.

4. Analise comportamental
   - Pesquisas padrao: DISC, Big Five/OCEAN, Eneagrama, MBTI e EQ Assessment.
   - Gestor pode editar perguntas, dimensoes, pesos, textos de interpretacao e periodicidade.
   - Colaborador ve resumo proprio com grafico radar e historico.
   - Gestor ve todos os resultados e comparativos.

5. Matcher de perfis
   - Compara dois colaboradores ou colaborador x time.
   - Cruza comportamento, PDI, 360, desempenho, pesquisas e avaliacoes.
   - Entrega compatibilidade, forcas da combinacao, riscos e recomendacoes de gestao.

6. People Analytics
   - Indicadores de engajamento, humor, desempenho, PDI, respostas pendentes, pedidos de 1:1, risco de saida e aderencia de time.
   - Filtros por time, lideranca, cargo, ciclo e metodologia.

7. Analise 360
   - Registro periodico por ciclo.
   - Consolida autoavaliacao, pares, lideranca e resposta final do RH/gestor.
   - Deve guardar evidencias e recomendacoes de desenvolvimento.

8. PDI
   - Objetivos, acoes, responsaveis, prazos, evidencias e progresso.
   - Pode nascer de 360, analise comportamental, pedido de feedback ou decisao do gestor.

9. Pesquisas internas
   - Gestor cria pesquisas livres, anonimas ou nominais.
   - Se nao houver pesquisa aberta, colaborador ve tela vazia.

10. Lideranca e 1:1
   - Gestor marca quem e lider e quem cada lider lidera.
   - Colaborador solicita feedback, 1:1 ou papo com lider.
   - Lider recebe mensagem privada e tem uma resposta unica por solicitacao.
   - Solicitações de 1:1 devem aparecer em uma fila de notificações/solicitações para o gestor ou líder responsável.
   - Mensagens privadas da liderança aparecem como notificação discreta na tela inicial do colaborador, sem ir para o mural.

## Modelo de dados essencial

- User: nome, email, senha_hash nullable no prototipo, must_change_password, primary_role, status, created_at.
- EmployeeProfile: user_id, foto, nome_preferido, nome_social, cargo_funcao, setor, modalidade, data_contratacao, contato_emergencia_nome, contato_emergencia_telefone, sobre_mim.
- UserRoleAssignment: user_id, role_type, active, granted_by, granted_at.
- LeadershipRelation: leader_id, employee_id.
- DirectorLeadershipRelation: director_id, leader_id.
- PeerReviewPermission: reviewer_id, reviewee_id, active.
- PublicRecognition: author_id, target_ids, text, reactions, created_at.
- PeerReview: reviewer_id_hash, reviewee_id, cycle_id, scores_json, comments_encrypted, created_at.
- AssessmentTemplate: type, title, dimensions_json, questions_json, weights_json, editable_by_company.
- AssessmentResponse: employee_id, template_id, cycle_id, answers_json, scores_json, summary_json.
- MatchReport: subject_a_id, subject_b_id ou team_id, score, strengths_json, risks_json, recommendations_json.
- PDI: employee_id, owner_id, title, goals_json, status, due_date, progress.
- Survey: title, audience_json, anonymous, questions_json, status, close_at.
- SurveyResponse: survey_id, employee_id nullable, employee_hash nullable, answers_json.
- Review360Cycle: title, period_start, period_end, status.
- Review360Response: cycle_id, employee_id, source_type, source_hash, answers_json.
- OneOnOneRequest: requester_id, leader_id, type, message, status, single_reply, replied_at.
- TimeEntry: employee_id, entry_type, recorded_at, source, status, adjusted_by nullable, adjustment_reason nullable.
- TimeJustification: employee_id, type, date, description, attachment_url nullable, status, reviewed_by nullable, reviewed_at nullable.
- TimeBalance: employee_id, period, balance_minutes, is_intern, redflags_json.
- VacationRequest: employee_id, model, periods_json, leader_id, status, leader_comment, reviewed_by nullable, reviewed_at nullable.
- PayrollReportExport: requested_by, report_type, filters_json, file_url, created_at.
- HRAccessPermission: user_id, can_access_hr, can_manage_users, can_generate_links, can_view_payroll, can_view_bonus, can_view_commission, can_view_plr, can_manage_permissions, granted_by, granted_at.
- FirstAccessLink: user_id, token_hash, purpose, expires_at, used_at, revoked_at, created_by.
- EmployeeDPRecord: employee_id, contract_type, full_name, social_name, birth_date, marital_status, gender_identity, race_color, sexual_orientation, education, course_college, mother_name, father_name, birth_city_state, residential_address, emergency_contact_name, emergency_contact_relation, emergency_contact_phone, best_email, phone, mobile, cpf, rg, rg_issuer, rg_issue_date, rg_state, voter_registration, voter_zone, voter_section, first_job, pis, ctps_number, ctps_series, ctps_state, ctps_issue_date, transport_voucher, dependents_json, dependent_vaccine_files_json, usual_email_name, uniform_male_size, uniform_female_size, status, completed_at.
- PayrollRecord: employee_id, salary, benefits_json, cost_center, bonus_json, commission_json, plr_json, effective_from, effective_to, visibility_scope.
- RecruitingProcess: title, department, owner_id, status, opened_at, closed_at, stages_json.
- Candidate: process_id, name, email, phone, stage, status, notes_json, approved_at, dp_link_id nullable, hired_employee_id nullable.
- OfficeDepartment: nome, descricao, ordem, ativo.
- OfficeDesk: employee_id, department_id, status_manual, canal_atual, contexto_ativo_json, updated_at.
- OfficeRoom: nome, tipo, department_id nullable, temporaria, archive_at, contexto_json, status.
- KnockRequest: from_employee_id, to_employee_id, context_json, status, response_option, expires_at.
- ContextShare: from_employee_id, to_employee_id nullable, room_id nullable, type, entity_id, payload_json, created_at.
- Meeting: title, type, starts_at, ends_at, room_id nullable, context_json, created_from_type, created_from_id.
- MeetingParticipant: meeting_id, employee_id, role, status.
- MeetingRoom: nome, capacidade, permissao_de_uso, status, ativo.
- OfficeLocation: employee_id, location_type, room_id nullable, with_employee_ids_json, game_name nullable, updated_at.
- OfficeTimelineEvent: employee_id, type, source_type, source_id, summary, context_json, created_at.
- SkillIndex: employee_id, skill, source_type, confidence, last_seen_at.

## Regras de permissao

- Colaborador nao acessa dados de terceiros, exceto mural publico.
- Colaborador pode ver mesas, status operacional declarado e contexto compartilhavel, mas nao informacoes privadas de RH.
- Timeline existe para contexto e continuidade, nunca para vigilancia individual.
- Status inteligente deve usar somente agenda, ligacoes, atendimento, reunioes, pausa, almoco, foco e status informado.
- Colaborador nao ve autoria de avaliacao anonima.
- Lider ve mensagens e dados dos liderados definidos pelo gestor.
- Lider pode ter multiplos liderados selecionados no cadastro.
- Diretor ve lideres sob sua responsabilidade e colaboradores vinculados a esses lideres.
- Diretor tambem pode receber feedback, dar feedback e participar de 1:1 como qualquer lideranca.
- Gestor/RH ve tudo, inclusive consolidado anonimo de avaliacoes.
- Dados sensiveis de comportamento e avaliacoes devem ter trilha de auditoria.
- Acesso RH nao implica acesso financeiro automaticamente.
- Lider com papel adicional de RH acessa RH/DP conforme as permissoes marcadas.
- RH sem lideranca continua com experiencia base de colaborador no People Hub.
- Administrador acessa todos os modulos, cadastros, metricas, configuracoes e trilhas de auditoria.
- Folha de pagamento, bonificacoes, comissoes e PLR exigem permissoes separadas.
- Dados de DP e documentos devem ter auditoria de acesso, exportacao e alteracao.
- Candidatos acessam apenas o proprio link de cadastro DP enquanto o convite estiver valido.

## Banco padrao das metodologias

Use escala de 1 a 5:

1. Discordo totalmente
2. Discordo parcialmente
3. Neutro
4. Concordo parcialmente
5. Concordo totalmente

### DISC

Dimensoes: Dominancia, Influencia, Estabilidade, Conformidade.

Perguntas iniciais:

- Tomo decisoes com agilidade quando ha pressao por resultado.
- Assumo a frente quando percebo falta de direcao.
- Tenho facilidade para influenciar e engajar pessoas.
- Costumo comunicar ideias com entusiasmo.
- Prefiro ambientes previsiveis e combinados estaveis.
- Mantenho constancia mesmo em rotinas longas.
- Analiso detalhes antes de concluir uma entrega.
- Valorizo padroes, regras e criterios claros.
- Sinto energia ao lidar com desafios competitivos.
- Procuro consenso antes de mudar uma rotina do time.

### Big Five / OCEAN

Dimensoes: Abertura, Conscienciosidade, Extroversao, Amabilidade, Neuroticismo.

Perguntas iniciais:

- Busco formas novas de resolver problemas conhecidos.
- Tenho curiosidade por ideias fora da minha area.
- Organizo prioridades antes de iniciar uma entrega importante.
- Cumpro combinados mesmo quando ninguem esta acompanhando.
- Ganho energia em conversas e trocas com o time.
- Gosto de iniciar interacoes com pessoas novas.
- Considero as necessidades dos outros antes de decidir.
- Tenho facilidade para cooperar em situacoes de conflito.
- Percebo rapidamente quando estou sob estresse.
- Em pressao, consigo regular minhas reacoes.

### Eneagrama

Dimensoes sugeridas: tipos 1 a 9.

Perguntas iniciais:

- Busco fazer o que e correto, mesmo quando isso exige mais esforco.
- Sinto motivacao ao ajudar pessoas de forma concreta.
- Gosto de metas claras e reconhecimento por resultado.
- Valorizo autenticidade e significado no que faco.
- Preciso entender profundamente antes de agir.
- Procuro seguranca, previsibilidade e confianca.
- Fico motivado por possibilidades, movimento e novidades.
- Tenho facilidade para me posicionar com firmeza.
- Evito conflitos quando percebo que podem desgastar relacoes.

### MBTI

Dimensoes praticas para o sistema: E/I, S/N, T/F, J/P.

Perguntas iniciais:

- Prefiro construir ideias conversando com outras pessoas.
- Preciso de tempo sozinho para organizar pensamentos complexos.
- Confio mais em fatos concretos do que em possibilidades abstratas.
- Tenho facilidade para imaginar cenarios futuros.
- Ao decidir, priorizo logica, criterios e consistencia.
- Ao decidir, considero impacto humano e relacional.
- Gosto de planejamento, prazos e definicoes antecipadas.
- Prefiro manter flexibilidade ate entender melhor o contexto.

### EQ Assessment

Dimensoes: Autopercepcao, Autorregulacao, Empatia, Influencia, Conversas dificeis.

Perguntas iniciais:

- Consigo nomear o que estou sentindo antes de reagir.
- Percebo como meu comportamento afeta o ambiente.
- Consigo pausar antes de responder em momentos tensos.
- Mantenho respeito mesmo quando discordo.
- Leio sinais emocionais de colegas com facilidade.
- Valido sentimentos antes de propor solucao.
- Consigo engajar pessoas sem pressionar.
- Adapto minha comunicacao conforme o perfil da pessoa.
- Tenho repertorio para conversas dificeis.
- Dou feedback com clareza, cuidado e exemplos.

## Formula inicial do matcher

Pontuacao de compatibilidade sugerida:

- 35% comportamento: distancia normalizada entre DISC, Big Five, Eneagrama, MBTI e EQ.
- 20% colaboracao: avaliacoes anonimas, feedbacks publicos e 360.
- 20% desenvolvimento: PDI, metas e interesses de carreira.
- 15% desempenho: performance, entregas e confiabilidade.
- 10% contexto: time, lideranca, carga atual e senioridade.

Saida do matcher:

- Score geral.
- Pontos fortes da dupla/time.
- Riscos de atrito.
- Recomendacao de comunicacao.
- Melhor tipo de projeto para aquela combinacao.
- Contrapeso comportamental recomendado, se houver.

## Cuidados importantes

- Nao apresentar metodologia comportamental como diagnostico clinico.
- Explicar que resultados indicam tendencias e contexto, nao rotulos fixos.
- Manter avaliacoes anonimas realmente anonimas para colaboradores e lideres diretos, com acesso consolidado para RH/gestao.
- Evitar decisoes automatizadas de promocao, desligamento ou contratacao baseadas apenas nos testes.
- Registrar consentimento e politica interna de uso dos dados comportamentais.

## Digital Office - experiencia

### Escritório virtual

- Departamentos: Suporte, Customer Success, Comercial, Financeiro, Telecom, Produto, Desenvolvimento e Diretoria.
- Cada departamento possui mesas virtuais.
- Cada mesa mostra foto, nome, cargo, departamento, status, canal principal, disponibilidade, atendimento ativo, reuniao, foco, ausente ou almoco.
- A navegação deve parecer uma caminhada leve entre departamentos, sem animacoes exageradas.
- Visualmente, os setores devem aparecer um abaixo do outro para reduzir embolamento e facilitar leitura.
- O mapa deve ser ludico e profissional: mais proximo de um escritorio vivo do que de um dashboard.
- As mesas podem ter representacao visual propria, com computador e pequenos objetos escolhidos pelo colaborador.
- A customizacao deve gerar pertencimento, mas dentro de uma biblioteca visual controlada para manter padrao e performance.

### Personalizacao da mesa

O colaborador pode organizar sua propria mesa virtual.

Opcoes iniciais:

- Computador: monitor, notebook ou dois monitores.
- Objetos: cafe, luminaria, notas, headset e itens futuros aprovados pelo RH/Brand.
- Status visual: disponibilidade, atendimento, reuniao, foco, ausente e almoco.

Regras:

- Nao permitir upload livre de imagem na primeira versao.
- Usar objetos pre-aprovados para evitar poluicao visual.
- Permitir personalizacao suficiente para engajamento, sem transformar o escritorio em jogo complexo.
- O objetivo e criar pertencimento e recorrencia, nao competir com ferramentas de reuniao ou chat.

### Mesa virtual

Ao clicar em uma mesa, abre painel lateral representando "chegar na mesa da pessoa".

Acoes em um clique:

- Chat.
- Ligacao.
- Videochamada.
- Compartilhar tela.
- Compartilhar arquivo.
- Compartilhar ticket.
- Compartilhar cliente.
- Compartilhar dashboard.
- Compartilhar relatorio.
- Compartilhar alerta.
- Compartilhar conversa.
- Compartilhar playbook.

### Bater na mesa

Acao educada para pedir atencao sem interromper.

Quando uma pessoa bater na mesa, iniciar chat, chamada ou video, a outra pessoa deve receber um popup com a solicitacao, remetente e contexto.

Respostas padrao:

- Pode entrar.
- Estou em atendimento.
- Me chama em alguns minutos.
- Vamos fazer uma ligacao.
- Agendar horario.

O popup deve ser discreto, rapido e nao bloquear trabalho critico. Se a pessoa estiver em atendimento, deve ser facil responder sem abrir outra tela.

### Salas virtuais

- Salas permanentes por departamento.
- Salas temporarias por incidente, cliente, problema, projeto ou sprint.
- Salas temporarias podem ter arquivamento automatico.
- Chat, audio, video, tela, tickets e dashboards devem viver no mesmo contexto.
- Gestores/administradores podem cadastrar salas de reuniao, capacidade e permissoes de uso.
- No Digital Office deve aparecer onde as pessoas estao: mesa, sala, cafe, area de jogos, atendimento ou foco.

### Cafe e area de jogos

- Colaborador pode marcar que esta no Cafe para conversas rapidas.
- Colaborador pode marcar que esta na area de jogos, escolher com quem esta jogando e qual jogo.
- A informacao de jogo aparece para todos como pausa social, sem expor dados privados.
- O sistema pode sugerir jogos gratuitos online como Gartic.io, Stopots, Codenames Online e JigsawPuzzles.io.

### Reunioes

Tipos padrao:

- Daily.
- One-on-one.
- Feedback.
- PDI.
- Sprint.
- Alinhamento.
- Comite.
- Reuniao rapida.
- Diretoria.

Uma reuniao pode nascer de qualquer contexto: alerta, ticket, cliente, dashboard, PDI, feedback ou incidente.

### Cafe

Espaco simples para duvidas rapidas, conversas informais, ajuda e avisos curtos. Deve ser leve, mas integrado a operacao.

### Pesquisa inteligente

Consultas esperadas:

- Quem entende de SIP?
- Quem conhece Portabilidade?
- Quem trabalhou nesse cliente?
- Quem pode ajudar em API?
- Quem atende Revenda?
- Quem esta livre agora?
- Quem conhece esse produto?
- Quem trabalhou nesse ticket?

Fontes:

- Historico operacional.
- Competencias.
- Departamento.
- Senioridade.
- Experiencia anterior.
- Atendimentos e projetos.

### Criterio de UX

- Falar com alguem deve levar menos de tres cliques.
- Compartilhar contexto deve ser uma acao nativa, nao copia de link.
- A interface deve priorizar command palette, busca global, side panels, hover cards, menus de contexto, atalhos e drag and drop.
- O modulo nao deve parecer ERP, CRM antigo ou help desk tradicional.
