# InfraAgent ReplayOps - MASTER TODO

Generated: 2026-05-10, Europe/Minsk

## PROJECT ONE-LINER

InfraAgent ReplayOps должен стать судейски убедительным AMD Hackathon проектом: не "AI пишет runbook", а доказуемая incident-triage система, где LangGraph, Qwen на AMD MI300X, evidence timeline, runtime truth, eval scorecard и War Room Packet видны в одном end-to-end демо.

## IDEA ANCHOR

- core value: быстро превращать шумный инфраструктурный инцидент в проверяемый, воспроизводимый и безопасный War Room Packet с доказательствами, владельцем, рисками и планом восстановления.
- core user: SRE, platform engineer, incident commander, DevOps lead, которые отвечают за разбор инцидентов, MTTR, ownership и доверие к AI-ассистентам.
- correct end-state: публичная судейская демонстрация работает end-to-end, показывает `live_vllm` на AMD MI300X/Qwen, объясняет агентный путь, не скрывает ограничения и даёт артефакты, которые можно проверить.
- do not drift into: generic chatbot, simple RAG demo, декоративный dashboard, auto-remediation без человека, фейковая production telemetry, скрытие fallback-режима, расширение в огромную AIOps-платформу без доказательности.

## INTERPRETATION

На момент проверки проекта локальный и публичный fallback-контур уже сильный: GitHub, HF Space, видео, слайды, readiness gate, evidence timeline, node trace, scorecard и War Room Packet есть. Главный судейский blocker: нет подтверждённого live-запуска на AMD Developer Cloud MI300X с Qwen/vLLM, где публичный run показывает `runtime_proof.backend_mode=live_vllm` и `Qwen critic: ok`.

Проверенные источники: официальная страница AMD Developer Hackathon, локальные `README.md`, `docs/STATE.md`, `docs/EXEC_PLAN.md`, `docs/DECISIONS.md`, `HACKATHON_READINESS.md`, `docs/COMPETITION_REVIEW.md`. Live readiness на момент строгого gate: local `7/7`, external `4/7`, blockers `live_vllm`, `amd_runtime_proof`, `qwen_critic_ok`.

## RECOMMENDED PROJECT SHAPE

Оставить продукт в форме InfraAgent ReplayOps: узкий, доказуемый, пятиузловой incident-replay агент для Track 1. Не расширять в общий AIOps suite. Победный акцент должен быть на AMD/Qwen runtime proof, replayable evidence, judge-visible evaluation, честной runtime truth и сильной презентации business pain.

## ASSUMPTIONS / NEEDS CONFIRMATION

- Нужен доступ к AMD Developer Cloud MI300X; в текущей локальной среде он не найден.
- Победу нельзя гарантировать, но можно закрыть максимум судейских критериев и убрать слабые места.
- Если Quick Tunnel останется временным, перед judging нужен обязательный refresh; стабильный hostname лучше.
- Build in Public extra challenge релевантен, потому что официальная страница конкурса явно выделяет его как отдельный призовой сигнал.
- Токены и секреты не должны попадать в TODO, markdown, git или chat; использовать только уже настроенную авторизацию, переменные окружения или credential store.

## PHASE MAP

1. Contest truth, freshness и финальная рамка проекта.
2. AMD live runtime proof и инфраструктурная доказательность.
3. ReplayOps product core, evidence quality и agent behavior.
4. Уникальное design-DNA, визуальная доказательность и HF Space UI.
5. Судейская история, submission package и Build in Public.
6. QA, security, reliability, recovery и проектная гигиена.
7. Final release gate, public rehearsal и официальная отправка.
8. Post-release loop, finalist readiness и устойчивое развитие.

## MASTER TODO

### PHASE 1 - Contest Truth, Freshness И Финальная Рамка Проекта

- [x] T001 [P0] Закрыть актуальную сводку правил AMD Developer Hackathon на дату 2026-05-10: треки, критерии, сроки, submit-поля, призовые сигналы и ограничения.
- [x] T002 [P0] Зафиксировать, что InfraAgent ReplayOps идёт в Track 1 как agentic workflow, а не fine-tuning, multimodal или generic app.
- [x] T003 [P0] Сопоставить текущий проект с официальными критериями originality, technical implementation, usefulness, presentation и end-to-end completeness.
- [x] T004 [P0] Развести обязательный submission scope и дополнительные prize-scope сигналы, включая Build in Public и AMD feedback.
- [x] T005 [P0] Зафиксировать главный судейский blocker: отсутствие live AMD MI300X/Qwen proof в публичном run.
- [x] T006 [P0] Обновить IDEA ANCHOR в проектных документах так, чтобы вся команда держала фокус на evidence-verified incident triage.
- [x] T007 [P1] Перепроверить список видимых конкурентных заявок и выделить проекты, которые пересекаются с AIOps, ROCm tooling, SOC automation и Qwen runtime proof.
- [x] T008 [P1] Обновить competitive risk matrix: где InfraAgent сильнее, где слабее, где нужен явный судейский контраргумент.
- [x] T009 [P1] Зафиксировать, что проект не должен конкурировать шириной платформы, а должен выигрывать доказательностью, replayability и честным runtime truth.
- [x] T010 [P0] Сформировать one-minute judging thesis: проблема, агентный workflow, AMD unlock, доказательства, результат.
- [x] T011 [P0] Перепроверить, что в проекте нет обещаний production telemetry, auto-remediation или live Qwen там, где это не доказано.
- [x] T012 [P1] Зафиксировать freshness-sensitive зависимости: правила конкурса, AMD access, Qwen/vLLM совместимость, HF Space состояние, Cloudflare tunnel, конкуренты.
- [x] T013 [P1] Подготовить короткий цикл обновления freshness-фактов перед каждым финальным rehearsal.
- [x] T014 [P1] Проверить актуальный README/release/security model для autoskills или аналогичного skill-discovery пути и принять решение install / skip / manual skills.
- [x] T015 [P1] Если skill discovery полезен, зафиксировать выбранные AI skills в project notes или lock-файле без раскрытия секретов.
- [x] T016 [P1] Оценить, нужен ли SocratiCode или другой codebase-intelligence слой для shared agent navigation; при малом размере проекта зафиксировать `SKIP` с причиной.
- [x] T017 [P1] Сохранить правило: exploration можно усиливать codebase search, но точные строки, ошибки и identifiers проверять обычным known-string search.
- [x] T018 [P0] Сверить README, SUBMISSION, HACKATHON_READINESS и STATE на отсутствие противоречий по текущему статусу.
- [x] T019 [P0] Подготовить judge-facing gap statement: "fallback demo verified, live AMD/Qwen proof pending" без оправданий и без размытия.
- [x] T020 [P1] Зафиксировать полный список артефактов, которые должны быть обновлены после live AMD proof.
- [x] T021 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [x] T022 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 1 закрыта. Переходим к фазе 2" или "Фаза 1 не закрыта. Стоп. Вот что мешает: ..."

### PHASE 2 - AMD Live Runtime Proof И Инфраструктурная Доказательность

- [ ] T023 [P0] Получить или подтвердить рабочий доступ к AMD Developer Cloud MI300X среде.
- [ ] T024 [P0] Проверить наличие реального GPU-runtime доступа на целевой машине, не подменяя его локальным fallback.
- [ ] T025 [P0] Подготовить чистую runtime-сессию для Qwen2.5-72B-Instruct без смешения с локальными Windows/WSL ограничениями.
- [ ] T026 [P0] Запустить model-serving контур так, чтобы InfraAgent мог честно отличить live model mode от fallback.
- [ ] T027 [P0] Подтвердить, что Qwen отвечает из целевой AMD-среды, а не из внешнего API или локальной заглушки.
- [ ] T028 [P0] Зафиксировать runtime evidence: model identity, runtime mode, latency, critic status и timestamp.
- [ ] T029 [P0] Добиться, чтобы публичный run показывал `live_vllm` именно в UI, а не только в логах.
- [ ] T030 [P0] Добиться, чтобы root cause panel показывал `Qwen critic: ok` на живом run.
- [ ] T031 [P0] Проверить, что readiness gate закрывает `live_vllm` blocker только при реальном live proof.
- [x] T032 [P1] Зафиксировать fallback behavior как честный degraded mode, а не как скрытую замену live runtime.
- [x] T033 [P1] Подготовить AMD runtime proof note для README и submission copy.
- [x] T034 [P1] Проверить, что public tunnel открывает только agent service, а не raw model service.
- [x] T035 [P1] Подготовить stable public access plan для финального judging, чтобы временный tunnel не умер в момент проверки.
- [ ] T036 [P1] Закрыть smoke-доказательство public UI -> public API -> AMD-backed agent -> Qwen critic -> War Room Packet.
- [x] T037 [P1] Зафиксировать измеримые runtime факты без завышения: что реально проверено, где лимиты, где наблюдение одноразовое.
- [x] T038 [P1] Перепроверить актуальные AMD/ROCm/vLLM/Qwen допущения перед финальным run и отметить всё, что может устареть.
- [x] T039 [P2] Подготовить short troubleshooting path для случаев, когда AMD runtime не стартует с первого раза.
- [x] T040 [P2] Подготовить fallback judge path, который честно показывает продукт, но не претендует на closed live proof.
- [ ] T041 [P0] Зафиксировать финальный AMD proof artifact: screenshot, public run status, readiness verdict и timestamp.
- [ ] T042 [P0] Обновить machine/human state после live AMD proof, чтобы проектная память совпадала с реальностью.
- [x] T043 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [x] T044 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 2 закрыта. Переходим к фазе 3" или "Фаза 2 не закрыта. Стоп. Вот что мешает: ..."

### PHASE 3 - ReplayOps Product Core, Evidence Quality И Agent Behavior

- [x] T045 [P0] Проверить, что LangGraph остаётся не больше пяти узлов и не разрастается ради демонстративной "многоагентности".
- [x] T046 [P0] Довести каждый демо-сценарий до понятной incident story: симптом, service owner, business risk, evidence trail, root cause, recovery.
- [x] T047 [P0] Обеспечить, чтобы evidence IDs были видимыми, стабильными и цитировались в root cause и War Room Packet.
- [x] T048 [P0] Проверить, что root cause не появляется без достаточной evidence coverage.
- [x] T049 [P0] Обеспечить видимый rejected alternatives блок, чтобы judges видели не только ответ, но и отбраковку слабых гипотез.
- [x] T050 [P1] Усилить сценарии так, чтобы они покрывали разные классы инфраструктурных отказов, а не повторяли один паттерн.
- [x] T051 [P1] Проверить, что runbook не содержит опасных автоматических действий и явно требует human approval для рискованных шагов.
- [x] T052 [P1] Довести business / ownership lens до практического уровня: кто отвечает, какой риск, кому сообщить, что проверить после восстановления.
- [x] T053 [P1] Обеспечить понятное degraded-state поведение при слабой evidence coverage.
- [x] T054 [P1] Обеспечить понятное degraded-state поведение при недоступности Qwen.
- [x] T055 [P1] Подготовить отдельный scenario для model-serving saturation, чтобы AMD/Qwen слой был не только инфраструктурой, но и предметом incident logic.
- [x] T056 [P1] Проверить, что scorecard не является декоративным 100/100, а реально отражает root cause match, evidence coverage и runbook completeness.
- [x] T057 [P1] Добавить negative-case ожидания: где система должна сказать "нужен человек", а не уверенно выдумать причину.
- [x] T058 [P1] Зафиксировать acceptance criteria для War Room Packet: summary, evidence, cause, runbook, limitations, runtime truth, audit seal.
- [x] T059 [P2] Подготовить краткий internal glossary для judges: evidence item, node trace, runtime truth, packet, scorecard.
- [x] T060 [P2] Убедиться, что UI и docs используют одни и те же названия сценариев и артефактов.
- [x] T061 [P1] Развести product proof и implementation proof: judges должны понимать результат без чтения кода.
- [x] T062 [P1] Перепроверить, что deterministic fixtures не выглядят как fake production data.
- [x] T063 [P1] Добавить честное объяснение, зачем mock observability выбран для demo stability и evaluator clarity.
- [x] T064 [P0] Закрыть full replay path: выбранный сценарий можно пройти, пересказать и проверить по packet без устных пояснений автора.
- [x] T065 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [x] T066 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 3 закрыта. Переходим к фазе 4" или "Фаза 3 не закрыта. Стоп. Вот что мешает: ..."

### PHASE 4 - Уникальное Design-DNA, Визуальная Доказательность И HF Space UI

- [x] T067 [P0] Зафиксировать визуальное направление: operational war-room, evidence-first, calm high-signal interface, а не generic AI dashboard.
- [x] T068 [P0] Разработать DESIGN.md, пригодный для Google Stitch или самостоятельной генерации дизайна AI-агентом.
- [x] T069 [P1] Проанализировать эталонные design-md репозитории: google-labs-code/design.md, VoltAgent/awesome-design-md, kzhrknt/awesome-design-md-jp, bergside/awesome-design-skills, shaom/brand-to-design-md-skill, hasi98/designpull.
- [x] T070 [P1] Проверить актуальные README/license/security notes этих репозиториев перед использованием идей.
- [x] T071 [P1] Организовать GitHub research через уже настроенную авторизацию или credential store, не печатая и не сохраняя секреты.
- [x] T072 [P1] Проверить Lazyweb или аналогичный visual-evidence путь: актуальный README, instructions, health/search workflow и ограничения.
- [x] T073 [P1] Собрать visual references для incident command, observability timeline, eval dashboard и runtime proof surfaces.
- [x] T074 [P1] Перевести visual references в конкретные design rules, не копируя чужие layout, тексты, ассеты или бренд.
- [x] T075 [P0] Довести first viewport HF Space до мгновенного понимания: что случилось, что делает агент, где доказательства, где AMD runtime proof.
- [x] T076 [P0] Довести visual hierarchy так, чтобы judges за 10 секунд видели status, score, live runtime, root cause и packet.
- [x] T077 [P1] Развести в интерфейсе evidence timeline, node trace и final answer, чтобы они не конкурировали в одном текстовом полотне.
- [x] T078 [P1] Подготовить degraded визуальные состояния: no live Qwen, tunnel down, run failed, evidence insufficient, readiness blocker.
- [x] T079 [P1] Обеспечить консистентный ритм, плотность, spacing, typography и panel hierarchy между desktop и mobile.
- [x] T080 [P1] Подготовить иконографику для evidence, runtime, scorecard, owner, risk и packet через производственный цикл, а не одним "сгенерировать иконки".
- [x] T081 [P1] Для AI-графики собрать references, подготовить стилевое ТЗ, генерировать ассеты поштучно, вручную отбирать и отбраковывать визуальный мусор.
- [x] T082 [P1] Провести AI-agent curation визуальных ассетов: проверить line weight, metaphors, contrast, artifacts и соответствие DESIGN.md.
- [x] T083 [P1] Подготовить правила для будущих AI-illustrations, чтобы новые картинки не ломали стиль продукта.
- [x] T084 [P1] Проверить, что скриншоты для README, submission и видео не скрывают fallback/live truth.
- [x] T085 [P1] Убедиться, что визуал не выглядит как дешёвый шаблон: убрать пластик, случайные gradients, декоративные cards и бессмысленный hero-copy.
- [x] T086 [P0] Провести финальный screen-level QA: текст не перекрывается, ключевые панели читаются, critical states видны, runtime truth не теряется.
- [x] T087 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [x] T088 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 4 закрыта. Переходим к фазе 5" или "Фаза 4 не закрыта. Стоп. Вот что мешает: ..."

### PHASE 5 - Судейская История, Submission Package И Build In Public

- [ ] T089 [P0] Переписать submission copy после live AMD proof так, чтобы claims точно совпадали с observed behavior.
- [x] T090 [P0] Подготовить короткое описание проекта с явным отличием от simple RAG.
- [x] T091 [P0] Подготовить long description вокруг incident pain, agent workflow, AMD unlock и evidence verification.
- [x] T092 [P0] Обновить README так, чтобы judge мог проверить проект без личного созвона.
- [ ] T093 [P0] Обновить HACKATHON_READINESS после live proof и убрать устаревшие blocker statements.
- [x] T094 [P0] Обновить SUBMISSION links и убедиться, что все URL публичны, стабильны и открываются без локального контекста.
- [ ] T095 [P1] Пересобрать demo script под live AMD/Qwen run, а не fallback run.
- [ ] T096 [P1] Записать demo video, где за 75-90 секунд видны problem, workflow, live runtime proof, evidence, scorecard и packet.
- [x] T097 [P1] Убедиться, что видео не скрывает limitations и не обещает production telemetry.
- [x] T098 [P1] Обновить slide deck вокруг судейского нарратива: pain, workflow, AMD, demo proof, scorecard, impact, limitations.
- [x] T099 [P1] Проверить, что слайды не перегружены implementation details и показывают продуктовый результат.
- [x] T100 [P1] Подготовить technical walkthrough для Build in Public / open-source story без раскрытия секретов.
- [x] T101 [P1] Подготовить два содержательных технических update-поста с тегами конкурса и AMD/lablab, если команда выбирает extra challenge.
- [x] T102 [P1] Включить в Build in Public честный feedback по ROCm, AMD Developer Cloud, vLLM/Qwen и tunnel friction.
- [x] T103 [P1] Проверить, что public GitHub history не содержит секретов, локальных runtime-файлов и временного мусора.
- [x] T104 [P1] Подготовить judge FAQ: что live, что mocked, что deterministic, что human-approved, что не является auto-remediation.
- [x] T105 [P2] Подготовить короткий comparison note против generic incident assistant и generic dashboard проектов.
- [x] T106 [P2] Сформировать "why AMD matters" section: MI300X memory, local Qwen, ROCm/vLLM serving, public proof.
- [x] T107 [P1] Подготовить contingency wording, если final live AMD proof сломается перед deadline.
- [x] T108 [P0] Провести final claim audit всех публичных материалов: README, submission, slides, video, HF Space, readiness, project state.
- [x] T109 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [x] T110 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 5 закрыта. Переходим к фазе 6" или "Фаза 5 не закрыта. Стоп. Вот что мешает: ..."

### PHASE 6 - QA, Security, Reliability, Recovery И Проектная Гигиена

- [x] T111 [P0] Провести полный локальный test pass после всех изменений submission и UI.
- [x] T112 [P0] Провести full public smoke через HF Space после обновления backend base и secrets.
- [ ] T113 [P0] Провести AMD-backed public smoke: live run, scorecard, packet, readiness GO.
- [x] T114 [P0] Проверить все supported scenarios, а не только один счастливый judge path.
- [x] T115 [P1] Проверить failure paths: недоступный runtime, неверная авторизация, умерший tunnel, долгий run, неполные evidence.
- [x] T116 [P1] Проверить, что публичный UI не раскрывает секреты, internal paths, local process details или лишние debug traces.
- [x] T117 [P1] Проверить, что auth boundary защищает public API от случайного публичного злоупотребления.
- [x] T118 [P1] Проверить, что logs и runtime artifacts не содержат ключи, токены, private hostnames или случайные payloads.
- [x] T119 [P1] Подготовить manual recovery checklist: как перезапустить runtime, agent service, tunnel и HF Space config.
- [x] T120 [P1] Подготовить judging-day runbook: порядок запуска, проверки, refresh, smoke, screenshot, submit.
- [x] T121 [P1] Зафиксировать stop condition для readiness: нельзя отправлять "GO" без live AMD/Qwen proof.
- [ ] T122 [P1] Провести безопасный dead-code audit: найти неиспользуемые компоненты и изолировать только после проверки сборки.
- [ ] T123 [P1] Настроить поиск orphan assets и неиспользуемой графики, не удаляя ничего без проверки влияния.
- [ ] T124 [P1] Перенести черновики, промежуточные AI-generations, временные screenshots и test artifacts вне релизного пакета или в ignored archive.
- [ ] T125 [P1] Провести ревизию зависимостей и убрать только подтверждённо неиспользуемые, проверив отсутствие скрытых конфликтов.
- [ ] T126 [P1] Проверить bundle/repo hygiene: финальный public repo не должен тащить raw refs, logs, caches и локальные browser artifacts.
- [ ] T127 [P1] Проверить docs hygiene: нет stale links, conflicting dates, old tunnel URLs как active path.
- [ ] T128 [P2] Подготовить lightweight changelog для последней финальной версии.
- [ ] T129 [P1] Провести final security/privacy review: mock data, public URLs, credential handling, limitation wording.
- [ ] T130 [P0] Зафиксировать reproducible proof bundle: test output, screenshots, public run evidence, video, slides, readiness status.
- [ ] T131 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [ ] T132 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 6 закрыта. Переходим к фазе 7" или "Фаза 6 не закрыта. Стоп. Вот что мешает: ..."

### PHASE 7 - Final Release Gate, Public Rehearsal И Официальная Отправка

- [ ] T133 [P0] Перепроверить официальные submit-поля и deadline на дату финальной отправки.
- [ ] T134 [P0] Перепроверить, не изменились ли правила, judging criteria, required links и visibility requirements.
- [ ] T135 [P0] Перепроверить, что HF Space публичен, запускается и не показывает network error.
- [ ] T136 [P0] Перепроверить, что public GitHub открыт и README ведёт к рабочему demo path.
- [ ] T137 [P0] Перепроверить, что video artifact и slide deck artifact открываются из внешней среды.
- [ ] T138 [P0] Обновить public tunnel или stable hostname непосредственно перед final judging.
- [ ] T139 [P0] Провести final rehearsal как судья: открыть HF Space, стартовать scenario, дождаться READY, открыть packet, сверить readiness.
- [ ] T140 [P0] Сохранить screenshot/live evidence финального successful run.
- [ ] T141 [P0] Проверить, что live AMD/Qwen proof виден в финальном video или отдельном judge-visible artifact.
- [ ] T142 [P0] Проверить, что final readiness verdict действительно GO или явно объясняет единственный blocker.
- [ ] T143 [P1] Обновить STATE, state.json, EXEC_PLAN и PROJECT_HISTORY после финального rehearsal.
- [ ] T144 [P1] Зафиксировать быстро устаревающие элементы: tunnel URL, HF Space status, AMD runtime availability, model-serving health, contest page fields.
- [ ] T145 [P1] Подготовить pre-submit freshness checklist для этих элементов.
- [ ] T146 [P1] Проверить, что submission copy не содержит старого "links to fill" после заполнения ссылок.
- [ ] T147 [P1] Проверить, что public app не зависит от локального hostname, локального браузера или текущей shell-сессии без явного refresh.
- [ ] T148 [P1] Проверить, что repo license, title, tags и README совпадают с submission narrative.
- [ ] T149 [P1] Подготовить final no-go matrix: какие failures останавливают отправку, какие допускают fallback с честным wording.
- [ ] T150 [P0] Отправить только тот пакет, который был реально проверен через public judge path.
- [ ] T151 [P0] После отправки сохранить submitted URLs, timestamps, final commit, final Space revision и final readiness evidence.
- [ ] T152 [P1] Проверить отправленную страницу со стороны участника и убедиться, что все ссылки кликабельны.
- [ ] T153 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [ ] T154 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 7 закрыта. Переходим к фазе 8" или "Фаза 7 не закрыта. Стоп. Вот что мешает: ..."

### PHASE 8 - Post-Release Loop, Finalist Readiness И Устойчивое Развитие

- [ ] T155 [P0] Организовать monitoring window после отправки: HF Space availability, tunnel status, repo visibility, submitted link health.
- [ ] T156 [P0] Подготовить быстрый recovery path, если публичный demo перестал работать после submission.
- [ ] T157 [P1] Подготовить регулярный цикл обновления freshness-знаний после запуска: contest updates, AMD runtime, HF Space state, public links, competitor movement.
- [ ] T158 [P1] Зафиксировать, какие внешние зависимости устаревают быстрее всего и кто отвечает за их перепроверку.
- [ ] T159 [P1] Собрать feedback от первых зрителей или судейских просмотров и отделить реальные blockers от cosmetic wishes.
- [ ] T160 [P1] Подготовить finalist demo rehearsal: 2-minute pitch, 5-minute technical walkthrough, 10-minute Q&A.
- [ ] T161 [P1] Подготовить ответы на tough questions: why mocked observability, why no auto-remediation, why AMD matters, why not simple RAG.
- [ ] T162 [P1] Подготовить план улучшения после hackathon: live observability adapter, persistent run history, stronger eval set, enterprise trust surface.
- [ ] T163 [P1] Развести post-hackathon roadmap и contest submission, чтобы финальная заявка не обещала ещё не сделанное.
- [ ] T164 [P2] Подготовить issue backlog с honest labels: contest-critical, post-release, research, design, cleanup.
- [ ] T165 [P2] Зафиксировать support policy для публичного demo: что поддерживается, что экспериментально, что может быть выключено.
- [ ] T166 [P1] Подготовить incident report template для самого InfraAgent demo, если public path падает во время judging.
- [ ] T167 [P1] Проверить, что README после конкурса не вводит посетителей в заблуждение о статусе live AMD runtime.
- [ ] T168 [P2] Подготовить archive policy для временных submission assets, старых screenshots и fallback proof.
- [ ] T169 [P1] Подготовить next research pass по ROCm/vLLM/Qwen performance только после закрытия contest submission.
- [ ] T170 [P2] Сформировать список продуктовых метрик для будущей версии: time-to-diagnosis, evidence coverage, false confidence rate, operator acceptance.
- [ ] T171 [P2] Подготовить lightweight governance note: human approval, audit trail, limitation disclosure, data boundary.
- [ ] T172 [P1] Проверить, что post-release изменения не ломают пятиузловую contest demo path.
- [ ] T173 [P2] Подготовить "lessons learned" по AMD Developer Cloud и ROCm для sponsor feedback.
- [ ] T174 [P1] Закрыть финальную публичную синхронизацию: repo, Space, docs, state, submitted links и recovery notes совпадают.
- [ ] T175 [ANCHOR] 🔁 ANCHOR REVIEW - сверка с целью проекта
  - Агент-исполнитель обязан перечитать IDEA ANCHOR, проверить последние 20 пунктов на drift, исправить дрейф, а при нехватке актуальности использовать минимум 10 поисковых запросов с датой 2026-05-10. Если всё в порядке: "Anchor OK. Продолжаем."
- [ ] T176 [ANCHOR] 🏁 PHASE END REVIEW - итог фазы и проверка направления
  - Агент-исполнитель обязан перечислить закрытое, сверить итог с IDEA ANCHOR, проверить RELEASE BLOCKER и дать сигнал: "Фаза 8 закрыта. MASTER TODO закрыт" или "Фаза 8 не закрыта. Стоп. Вот что мешает: ..."

## RELEASE BLOCKERS

- Нет live AMD Developer Cloud MI300X/Qwen proof в публичном run.
- Нет `runtime_proof.amd_runtime_evidence.ok=true` в публичном run.
- `Qwen critic: ok` не доказан на live runtime.
- Readiness gate сейчас остаётся `NO_GO_UNTIL_BLOCKERS_CLOSE`.
- Временный Cloudflare Quick Tunnel может умереть до судейской проверки.
- Submission/video/slides должны быть обновлены после live proof, иначе останется несоответствие между claims и evidence.
- Любые публичные материалы с fallback wording не должны быть превращены в live-claims без новой проверки.

## OUT OF SCOPE FOR NOW

- Полная production observability integration вместо deterministic fixtures.
- Auto-remediation без human approval.
- Расширение в широкую AIOps/SOC platform.
- Fine-tuning модели.
- Multimodal track features.
- Pricing, billing, enterprise admin, marketing site и второстепенные growth surfaces.
- Новый стек вместо уже выбранного AMD Developer Cloud + vLLM/Qwen + FastAPI/LangGraph + HF Space + polling.

## TODO COVERAGE CHECK

- total ordinary tasks: 160
- anchor tasks: 16
- covered phases: 8
- biggest risk gaps: live AMD/Qwen access, AMD runtime device proof, Qwen critic ok, stable public demo URL, final claim audit after live proof, readiness GO, freshness of contest/submission requirements.

## QA-ADDED CLOSED ITEMS

- [x] T177 [QA] Убрать устаревший submission placeholder `Links To Fill` после заполнения публичных ссылок.
- [x] T178 [QA] Убрать небезопасный default `CHANGE_ME_PUBLIC_API_KEY` из runtime auth path и требовать реальный `PUBLIC_API_KEY`.
- [x] T179 [QA] Сделать `/health` и `/api/readiness` лёгкими: не грузить LangGraph/LLM runtime до запуска triage.
- [x] T180 [QA] Убрать известный LangGraph serializer warning из smoke-output, не скрывая реальные ошибки.
- [x] T181 [QA] Добавить release-cycle audit для curated SVG/visual assets: manifest, accessibility title/desc, no gradients/placeholders, accepted curation.
- [x] T182 [QA] Добавить строгий финальный submit gate: `scripts/final_submission_gate.py` возвращает `GO_SUBMIT` только при зелёных тестах/audits, AMD device proof, live vLLM, `Qwen critic: ok`, public smoke и readiness `GO`.
