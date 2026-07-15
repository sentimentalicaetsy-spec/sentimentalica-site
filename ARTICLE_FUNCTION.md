# /article — «листинг → готовая статья на sentimentalica.com»

> Самодостаточная инструкция. Исполнитель — любой Claude (Cowork / Claude Code).
> Запуск из Cowork: «Прочитай ARTICLE_FUNCTION.md в sentimentalica-site и сделай
> статью для листинга <имя>». Запуск из Claude Code в репо сайта: `/article <имя>`.

## Что делает
Один вызов = одна полная опубликованная статья для одного листинга:
реальная палитра листинга (именованные сво́тчи) → 2–3 его настоящие картинки →
живая карточка товара Etsy → 3 слота под SD-сцены (генерятся сразу, если
запущен A1111, иначе вставляются позже одной командой) → публикация → живой URL.

## Пути
- Репо сайта: `/Users/kseniateter/sentimentalica-site` (все команды отсюда)
- PY: `/Users/kseniateter/sentimentalica-pipeline/.venv/bin/python`
- Голос/структура-референс: `public/blog/colorful-junk-journal-ideas-for-maximalists-and-a-palette-to-steal.html`

## Режим редактора («напиши статью» без листинга)
Если листинг НЕ указан — работай по `.claude/skills/write-article/SKILL.md`
(в Cowork: «прочитай write-article SKILL в sentimentalica-site и напиши статью»):
сам исследуешь тренды/сезонность, смотришь живые листинги, решаешь тему
(вплоть до общей трафиковой «50 things…»), печатаешь решение в 3 строки и
исполняешь всю механику ниже без пауз.

## Шаги
1. `python3 tools/resolve_listing.py "<имя листинга>"` → `NNN_Theme|etsy_id|thumbs_dir`.
   Ошибки (NOT FOUND / NO ETSY_ID / NO IMAGES / AMBIGUOUS) — сообщить Ксении дословно и остановиться.
2. `PY tools/gen_article_assets.py "<строка из шага 1>"` → `staging/overnight/assets/<listing>/{img1..img4.jpg, meta.json}`.
3. Написать статью → `staging/overnight/assets/<listing>/post.html`:
   - Front matter: `title / category / excerpt / thumb: ./img1.jpg /
     related_ids: <fresh related LIVE Etsy IDs>`; титул 45–70 зн.,
     buyer-intent, без номеров листинга; не совпадать с titles в `public/blog/index.json`.
   - 550–850 слов, тёплый small-studio голос (см. референс), реально полезный крафт-контент.
     Запрещено: восклицательные, «digital/instant download» как продажа, счётчики страниц, хайп.
   - Архетип по теме (чередовать между статьями): спотлайт темы · список идей ·
     этюд о палитре · how-to проект.
   - Обязательно: палитра-блок `.post-palette` из meta.json (`<div class="sw"><i style="background:HEX"></i><b>NAME</b><span>роль</span></div>`) ·
     `<img src="./img2.jpg">`(…img4) · ОДНА строка `{{etsy:ETSY_ID}}` в середине ·
     ТРИ маркера `<!-- genimg:gen1 -->`…gen3 в естественных местах · мягкое закрытие со ссылкой `../blog.html`.
4. Промпты → `staging/overnight/prompts/<slug>.json` (slug = титул в lowercase-дефисах):
   `{"slug":..., "slots":[{"id":"gen1","prompt":"фотореалистичная уютная сцена junk-journal
   в теме и палитре листинга, конкретно: стол/свет/реквизит, 30–60 слов",
   "negative":"text, watermark, logo, low quality, deformed hands",
   "width":1216,"height":832,"caption":"alt-текст"}, ×3]}`
5. `python3 tools/publish_post.py staging/overnight/assets/<listing>/post.html`
6. **Картинки — автоматически, без участия Ксении:**
   a. Проверить API: `curl -s -m 3 http://127.0.0.1:7860/sdapi/v1/progress`
   b. Если НЕ отвечает — **запустить самому**: 
      `cd ~/stable-diffusion-webui && nohup ./webui.sh --api > /tmp/a1111.log 2>&1 &`
      и ждать до 6 минут: `until curl -s -m 3 http://127.0.0.1:7860/sdapi/v1/progress >/dev/null; do sleep 10; done`
   c. Когда API жив: `PY tools/insert_generated_images.py` **без --slug** — заполнит
      слоты и этой статьи, И все незакрытые слоты прошлых статей (backfill).
   d. Если A1111 так и не поднялся за 6 минут (ошибка в /tmp/a1111.log) — публиковать
      без сцен и написать это в отчёте; следующий запуск функции довставит их сам.
      Никаких команд Ксении помнить не нужно.
7. `git add public && git pull --rebase && git commit -m "post: <title>" && git push`
8. Через ~60 с: `curl -sL "https://sentimentalica.com/blog/<slug>?cb=$RANDOM" | head -3` —
   и отчёт: живой URL · какие картинки · палитра · статус ген-сцен · что пропущено.

9. **Пины и CSV (обязательный финал каждой статьи):** агент `pinterest-seo`
   проходит по пинабельным картинкам статьи (мокапы, палитра, сцены, сильные
   страницы) и для каждой добавляет строку: `python3 tools/pin_csv.py add
   <листинг> ...` (title/description/keywords/board/link, капельные даты).
   Pinterest = lead funnel на сайт: CSV `Link` по умолчанию ведёт на статью
   `https://sentimentalica.com/blog/<slug>`, не напрямую на Etsy. Название пина
   = search phrase + причина открыть статью; description заканчивается мягким
   CTA (`see the full guide`, `more ideas on Sentimentalica`). Прямой Etsy-link
   только если Ксения явно попросила.
   CSV автоматически зеркалится в **Google Drive →
   `Sentimentalica/Pinterest_CSV/<листинг>.csv`** — Ксения берёт файл там и
   загружает в Pinterest балком. Мульти-листинговая статья = строки в CSV
   каждого участника. В отчёте: путь CSV и сколько строк добавлено.
**Когда загрузила CSV в Pinterest** — скажи в чат «я загрузила CSV» (можно
конкретный листинг): выполняется `pin_csv.py mark-uploaded --all` — строки
уезжают в `Pinterest_CSV/uploaded/<листинг>__uploaded_<дата>.csv`, активный
файл продолжается пустым, повтор уже загруженного пина невозможен.

## Правила
- **Критик — КОД-ГЕЙТ, не пожелание (2026-07-07):** `publish_post.py` физически
  не опубликует статью, пока у каждой сгенерированной картинки (gen1..genN) нет
  записанного вердикта PASS в `staging/overnight/critic/<slug>.json`. Нет
  вердикта или REGENERATE → `sys.exit`, пуша не будет. Забыть критика
  невозможно — машина не дойдёт до git push. (Причина правила: провал 2026-07-06.)
- **Референсы Ксении = ФАЙЛЫ, не мои слова (2026-07-07/09):** папки `refs/`
  — эталон. Критик и генератор сверяются с картинками ОТТУДА, а не с моим
  пересказом в SCENE_STYLE.md. Пустая релевантная папка = агент слепой.
  Сгенерированные Claude/Codex/rendered картинки, staging assets, live images
  и демо-графика НЕ являются референсами, даже если выглядят "похоже".
  Reference = только то, что Ксения намеренно положила в `refs/`.
  Но ref-файл — это эталон вкуса/структуры/критики, не publish asset: не копировать
  сам референс в статью/пин, если Ксения явно не сказала, что этот конкретный
  файл можно использовать как production/brand-owned asset.
  Типы refs:
  `refs/branding/` = общий Sentimentalica look (голубой логотипа, бумажность,
  bird/logo мотивы); `refs/infographics/` = полезные графики; `refs/iphone notes/`
  = authentic iPhone Notes subtype; `refs/scrapbook and junk jornal scenes/` = реалистичные journal/mockup/
  process сцены; `refs/scenes/` = атмосферные комнаты/столы/офисы; `refs/50things/`
  = спец-референс для 50 things.
- **Инфографика = два источника, не один:** `refs/infographics/` даёт только
  композиционную идею / тип полезности (сетку предметов, prompt list,
  checklist, diagram, annotated guide). Финальный визуальный стиль всегда
  перестраивается через `refs/branding/`: Sentimentalica blue, бумажный
  scrapbook-collage, кружево, ботаника, handwritten texture, bird/logo motif,
  мягкий женственный journal look. Нельзя тащить чужой бренд, чужую палитру,
  чужой URL, чужой логотип или точную картинку из infographic reference.
  `public/`, `staging/`, старые Claude/Codex outputs и demo-файлы запрещены как
  источники вдохновения.
  Фон инфографики меняется под каждую статью/тему; запрещено использовать один
  общий branded paper background для всего batch. Качество и бренд-язык должны
  быть стабильными, но сам мир/предметы/композиция/фон/mood создаются заново
  под каждую статью. Повторить хороший фон = всё равно REGENERATE.
- **Никаких котов/собак в чужих темах; фото животного в нейтральной статье =
  брак:** карточки `{{etsy:}}` и картинки подбираются ТОЛЬКО по теме статьи;
  случайное фото кота/собаки в конце — запрещено (провал 2026-07-06).
- **Листикл → инфографика обязательна:** каждая статья-список получает полную
  инфографику (`render_list_infographic.py` или будущий renderer), но стиль
  теперь определяется `refs/infographics/` + `refs/branding/`: полезная структура
  должна быть переделана в Sentimentalica look. Исключение — iPhone Notes
  инфографика: она должна выглядеть как настоящая заметка в айфоне по
  `refs/iphone notes/`, натурально и не overdesigned. Emoji можно и часто нужно
  использовать в title/маленьком cluster/внутри или в конце строки. Emoji НЕ
  используются как маркеры в начале пунктов.
- **image-critic смотрит ВСЁ визуальное перед публикацией** — не только
  SD-генерации, но и рендеренную графику (инфографики, палитры-карточки,
  мокапы). Ничто не публикуется без его PASS. Нарушение этого шага — причина
  провала 2026-07-06; шаг обязателен.
- **Палитра = КАРТИНКА** (правило 2026-07-06): не CSS-блок, а изображение —
  `PY tools/render_palette_card.py <лучшая картинка по CLIP-скореру> "<Тема>"
  <out.jpg>` (сво́тчи с HEX и именами на красивом фото листинга, формат
  референса). Вставляется в статью И уходит палитра-пином в CSV.
- **Тон статей: успокаивать, радовать, давать пользу.** Аудитория — девочки,
  которые джорналят ради романтичной эстетики. Никаких стен текста: списки
  сканируемые (.keep-list), абзацы короткие, голос «ты молодец».
- **Тематические статьи без листингов — да**: успокаивающие/эстетические
  (инфографик-жанр из SCENE_STYLE.md), их картинки должны сохранять тысячи.
- **Промпты сцен — строго по формуле `SCENE_STYLE.md`** (плотность, свет с характером, палитра листинга).
- **Обложки статей не повторяют один шаблон.** На листе Journal соседние
  обложки обязаны отличаться ТИПОМ: мокап со страницами / атмосферная сцена /
  сильная страница крупно / инфографика. Перед выбором обложки посмотри
  thumb'ы существующих статей (blog/index.json) и возьми другой тип.
- **Мокапы не повторяются.** Обложка (gen2) не появляется в теле статьи ещё раз
  (движок это блокирует). Если мокап нужен и в теле — это ВТОРОЙ, другой мокап
  (другие страницы/другая сцена, слот gen4 type=mockup).
- **Реалистичные генерации ВСЕГДА в теме и палитре листинга (не обсуждается)** и
  на уровне «сохранил бы ради эстетики»: красивая композиция, красивые цвета,
  режиссёрский свет. Промпт сцены обязан называть 2–3 цвета палитры. Каждую
  генерацию проверяет агент `image-critic` (смотрит файл): PASS или REGENERATE
  с конкретной правкой промпта (макс. 2 круга).
- **Сгенерированное ≠ товар (анти-обман):** иллюстративные генерации — либо
  явная ФОТОГРАФИЯ (атмосферная сцена / realistic scrapbook-journal scene /
  mockup), либо явная ГРАФИКА (диаграмма/инфографика/iphone-notes list), никогда
  — рисунок в стиле акварелей листинга. В сценах НЕ изображать сюжет листинга
  (пёс в статье про собачий кит, кот в кошачьем) — только среда/процесс:
  стол, бумага, свет, журнал, инструменты. Похожее на «страницу из набора» =
  вводит в заблуждение = запрещено.
- **Статья делается ДЛЯ Pinterest**: каждый блок — будущий пин. Картинки либо
  потрясающе красивые, либо полезные (инфографика). «Реклама листинга» без
  пользы запрещена — nobody cares.
- **Каждая generated-картинка для Pinterest/статьи**: маленький footer
  `sentimentalica.com` внизу + мягкий CTA, если формат позволяет (`full guide`,
  `more ideas`, `read the article`, `save this`). iPhone Notes не используем
  как thumbnail и не ломаем им аутентичный UI.
- **В статье**: мягкие CTA в тексте обязательны. Предлагай релевантные LIVE
  листинги, когда это естественно, но neutral/listicle остаётся value-first,
  продукт в конце.
- **AI disclosure**: внизу каждой статьи перед финальным related/shop блоком
  должна быть тихая, но читаемая строка: “Image note: Some visuals in this
  article were created with AI and curated by Sentimentalica.”
- **Related/shop block is not random.** `publish_post.py` больше не добавляет
  hardcoded default listings. Если нужен финальный related-shop блок, статья
  должна иметь front matter `related_ids:` — максимум 4 LIVE ID, выбранных
  product-bridge из свежих данных live shop/feed на момент создания статьи.
  IDs должны быть связаны с темой статьи: floral ephemera → floral options,
  dark academia → dark academia/library/gothic, animals → animals, etc. Если
  свежих релевантных листингов нет, related-shop block пропускается; не заменять
  его случайными товарами.
- **Amazon affiliate links**: не добавлять без affiliate/tag системы Ксении.
  Когда появятся Amazon-ссылки, disclosure должен стоять до первой affiliate
  ссылки, а рекомендации должны быть реально полезны для junk journal.
- **Визуальная плотность статьи:** iPhone Notes / list infographic НЕ заменяет
  остальные картинки. У статьи должны быть оба типа визуала: полезная saveable
  графика + красивые desire-визуалы (generated scene/mockup или реальные страницы).
  Если есть подходящий листинг, в продуктовой части добавляй carousel с 3–5
  НАСТОЯЩИМИ pageN.jpg/listing assets, НЕ Etsy thumbnails/previews, чтобы
  читатель видел больше, чем одну карточку товара.
- **Thin atmospheric scene — обязательна в КАЖДОЙ статье.** Это wide/letterbox
  mood-картинка из `refs/scenes/`, как велосипедная сцена: атмосфера вокруг темы,
  а не junk journal mockup. Не вставлять страницы листинга, не показывать
  разворот как продукт, не делать hands/process hero. Даже если статья уже имеет
  инфографику/iPhone Notes, добавь отдельную thin atmospheric scene как
  desire-визуал.
- **Single-listing article visual package:** минимум 3 palette images, каждая
  на основе РАЗНОЙ showpiece-картинки из листинга/кита (не thumbnail, не collage);
  1 thin atmospheric scene inspired by the listing mood (без продукта/журнала);
  1 realistic junk journal/process scene inspired by the listing palette; carousel
  с 3–5 настоящими страницами; затем `{{etsy:ID}}`.
- **Multi-listing selection rule:** для статьи, которая продвигает несколько
  листингов, product-bridge выбирает максимум 4 LIVE листинга из ОДНОЙ категории
  live shop/vault или очень плотного theme cluster. Примеры: background/base
  papers/swatches; nature/botanical/floral; dark academia/library/gothic. Нельзя
  миксовать случайные красивые листинги из разных миров. Если одной сильной
  категории нет — выбрать 1 листинг или tie=end-only/none.
- **Multi-listing comparison visual package:** если статья сравнивает несколько
  листингов (например, до 4 flower/nature ephemera из одной категории), у КАЖДОГО
  featured listing должна быть своя palette image на основе showpiece real listing
  page. Плюс одна общая thin atmospheric scene, один realistic mockup/process
  image, и carousel 2–3 реальных страниц хотя бы от основного представленного
  листинга (или от каждого, если статья строится секциями). Все страницы — из
  customer/listing assets, не Etsy thumbnails/previews.
- **Карусель кита** (статья об одном листинге): сразу после лида —
  `<div class="kit-carousel">` с ≥3 `<img>` НАСТОЯЩИХ страниц кита (pageN.jpg из customer-папки — НЕ Etsy-превью/thumbnails; стрелки и точки добавляются автоматически).
- **Картинка на КАЖДЫЙ нумерованный пункт** («6 ways…» = 6 картинок): реальные
  страницы/фрагменты кита или сгенерированные сцены. Люди не читают — смотрят.
- **Руки/ножницы/часть девушки — больше НЕ абсолютный бан, но только reference-backed:**
  в realistic scrapbook/junk journal сценах можно промптить cropped hands,
  partial girl holding/opening a journal, scissors/tools, если это похоже на
  `refs/scrapbook and junk jornal scenes/` и не становится фокусом кадра.
  В atmospheric mood scenes по умолчанию избегать людей/рук. Плохие пальцы,
  creepy skin, fake scissors, deformed hands = REGENERATE.
- **Обложка статьи НИКОГДА не равна обложке Etsy-листинга** — после генерации
  выполнить `python3 tools/set_article_thumb.py <slug> gen2.jpg` (мокап-сцена как
  маркетинговая обложка; если SD упал — любой pageN/imgN кроме img1).
- **Только ЖИВЫЕ листинги** — resolve сам проверяет активность на Etsy и откажет
  (NOT LIVE), если листинг в драфте: ссылки статьи должны работать для покупателя.
- **Каждая картинка статьи кликабельна** → ведёт на листинг Etsy (правило работает
  автоматически через post.js для всех статей, старых и новых).
- **Слот gen2 = мокап**: в prompts JSON помечать `"type":"mockup",
  "insert_images":["page1.jpg","page2.jpg","page3.jpg"], "mood":"<палитра темы>"`
  — до **3 НАСТОЯЩИХ страниц** из customer-папки (asset-тул кладёт их как pageN.jpg) — **v4 native embedding**: настоящие страницы кладутся ПЕРВЫМИ и защищаются
  маской, SD **генерирует сцену ВОКРУГ них** (inpaint-around) — перекрытие объектов
  невозможно по построению, края сливаются естественно. Вертикаль 832×1216.
  Минимум один мокап/process scene, если статья связана с листингом; для pure
  neutral/infographic статьи mockup не заменяет thin atmospheric scene и ставится
  только если он естественно помогает теме.
- Explicit `/article <listing>` = один листинг за вызов. Multi-listing
  comparison article создаётся только как один approved row из write-article /
  product-bridge: до 4 LIVE листингов из одной категории, не произвольный batch.
  «Сделай статьи для нескольких независимых листингов» = последовательные вызовы.
- Ничего не выдумывать про кит: только meta.json и vault. Etsy ID — только из resolve.
- Ошибка публикации → показать её дословно, не править сгенерированное руками.
- Аварийная отмена всех статей ночного/массового прогона: `python3 tools/unpublish_overnight.py`.
