# Content Agents — архитектура Ксении (каноническая, 2026-07-06)

> Полная система из её спеки: 11 ролей; стартовая связка — 6 + 2 для сайта.
> Главная мысль: агенты делают не картинки, а СИСТЕМУ ВХОДОВ в один листинг:
> боль · идея · эстетика · палитра · список · commercial use · shortcut · SEO.
> Порядок стратегии: статья на сайте → пины из её материалов (article-first).

## Минимальная связка (6) → наши файлы (.claude/agents/)
| Роль Ксении | Агент | Статус |
|---|---|---|
| 1. Listing Analysis — что за пак, тема, стиль, аудитории | `listing-analysis` | NEW |
| 2. Pinterest Strategy — типы пинов и маркетинговые углы | `pin-strategist` | есть |
| 3. Pin Copy — короткие тексты на пины (overlay/CTA/списки) | `pin-copy` | NEW |
| 4. Visual Direction / SD Prompt — как собрать визуал; что реальное, что генерится | `visual-direction` | NEW |
| 5. Pinterest SEO — title/description/keywords, search intents | `pinterest-seo` | есть |
| 6. Quality Control — ложные обещания, дубли, читаемость, продукт виден | `qa-critic` (+`marketing-critic`) | есть |

## +2 для сайта
| 7. Website Content — статьи/лендинги под SEO-страницы | `copywriter` + /article, /listing-content | есть |
| 8. Commercial Use Audience — sellers/creators/малый бизнес | `commercial-audience` | NEW |

## Расширение (когда система запущена)
9. Blog/Saveable Content — списки/prompts/подборки (покрывает copywriter по
   ARTICLE_ARCHETYPES) · 10. Compliance — в qa-critic · 11. **Batch Production** —
   листинг → 18 типов → тексты → visual directions → SD prompts → SEO → JSON/CSV
   (= /listing-content + pin_csv.py, масштабируется после утверждения пилота).

## Жёсткие общие правила (для всех)
Продукт: большой тематический набор ~150–300 commercial-use watercolor-style
изображений — НЕ PNG clipart / sticker / ephemera / background-only / frames,
если не включено. SD создаёт сцену/фон/стол/свет; реальные картинки листинга —
поверх, как продукт. Ножницы/руки/люди в генерации запрещены. У каждого пина
одна маркетинговая причина. Полные брифы 18+3 типов: PIN_STRATEGY.md.
