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

## Шаги
1. `python3 tools/resolve_listing.py "<имя листинга>"` → `NNN_Theme|etsy_id|thumbs_dir`.
   Ошибки (NOT FOUND / NO ETSY_ID / NO IMAGES / AMBIGUOUS) — сообщить Ксении дословно и остановиться.
2. `PY tools/gen_article_assets.py "<строка из шага 1>"` → `staging/overnight/assets/<listing>/{img1..img4.jpg, meta.json}`.
3. Написать статью → `staging/overnight/assets/<listing>/post.html`:
   - Front matter: `title / category / excerpt / thumb: ./img1.jpg`; титул 45–70 зн.,
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

## Правила
- Один листинг за вызов; «сделай для нескольких» = последовательные вызовы.
- Ничего не выдумывать про кит: только meta.json и vault. Etsy ID — только из resolve.
- Ошибка публикации → показать её дословно, не править сгенерированное руками.
- Аварийная отмена всех статей ночного/массового прогона: `python3 tools/unpublish_overnight.py`.
