# Article Archetypes — банк из идей Ксении (2026-07-06)

> Источник: её 18+3 типов из PIN_STRATEGY.md, ПЕРЕОСМЫСЛЕННЫЕ как СТАТЬИ.
> Правило стратегии: **сначала сайт, потом Pinterest** — всё, что уйдёт в пины,
> сперва живёт статьёй/картинкой на sentimentalica.com и переиспользуется.
> Каждая статья рождает свои пины (картинки уже на сайте → Media URL готов).

Обозначения: [1] = один листинг · [N] = несколько листингов (2–4, `{{etsy:id1,id2,id3}}`
можно ставить НЕСКОЛЬКО раз в любом месте статьи — середина, конец).

| # | Архетип | Листинги | Суть статьи | Пины из неё |
|---|---------|----------|-------------|-------------|
| 1 | Problem Solver | [1/N] | «Your journal feels flat?» — боль → решение с примерами | hero-пин с болью, мокап |
| 2 | Stuck / Ideas | [N] | «30 journal theme ideas» — идеи по темам, каждая ведёт на листинг | big-number пин, идея-пины |
| 3 | List / Ideas | [1] | «20 Gothic Journal Ideas» под тему листинга | листикл-пин, 2–3 идея-пина |
| 4 | Aesthetic Match | [N] | «For dark romantic creators» — эстетика + 3 листинга под неё | аэстетик-пин |
| 5 | Palette / Moodboard | [1] | этюд о палитре (сво́тчи — есть автоматикой) | **palette-пин** |
| 6 | Theme Board | [N] | тема как мудборд: «Dark Academia» + 3 листинга в ней | theme-board пин |
| 7 | Transformation | [1] | «from blank page to beautiful spread» — до/после, шаги | до/после пин |
| 8 | Use Case | [1/N] | что сделать: journals, cards, collage, wall art | use-case пин |
| 9 | Collection Variety | [1] | «one collection, endless projects» — глубина кита | variety/chaos пин |
| 10 | Close-Up Detail | [1] | детали и фактуры крупно | detail-пин |
| 11 | Scrapbook / Collage | [1/N] | техника слоёв со страницами листинга | craft-пин |
| 12 | Cards / Invitations | [1/N] | открытки/приглашения из картинок | card-мокап пин |
| 13 | Etsy Seller Ideas | [N] | «art for your next Etsy product» — для продавцов | seller-пин |
| 14 | Digital Product Starter | [N] | старт цифрового продукта из пака | starter-пин |
| 15 | Design Asset Library | [N] | пак как библиотека ресурсов | library-пин |
| 16 | Small Business | [N] | визуалы для малого бизнеса | biz-пин |
| 17 | Product Mockup Ideas | [1] | во что превратить арт (обложки, принты) | product-пин |
| 18 | Keyword / SEO | [1] | прямая посадочная под запрос | SEO-пин |
| 19 | Teacher / Worksheets | [N] | опционально: educational-темы | worksheet-пин |
| 20 | Faith Creator | [N] | опционально: только faith-темы | faith-пин |
| 21 | Seasonal | [N] | опционально: сезон/праздник + листинги сезона | seasonal-пин |

## Бандл «новый листинг» (автоматизация)
Команда: `/listing-content <листинг>` → **3–5 статей одним заходом**:
1. **Spotlight** — /article для самого листинга (архетипы 3/5/6/7 по характеру);
2. **Тематическая [N]** — листинг + 2–3 родственных ЖИВЫХ листинга (архетип 4/6/21);
3. **Идеи/утилита** — из банка под тему (архетип 2/8/11);
4–5. опционально: seller/seasonal, если тема подходит.
Каждая статья → пины → строки в CSV листинга. Родственные листинги агент
подбирает по теме (vault/feed) и ПОКАЗЫВАЕТ Ксении выбор в отчёте.

## Правила преемственности
Все правила /article действуют: живые листинги · факты только из meta/vault ·
кликабельные картинки · мокапы с реальными страницами · обложка ≠ Etsy-обложка ·
язык продукта точный (commercial-use watercolor images, не clipart/ephemera).
