# Design Notes

Source of inspiration: `design/Homepage.dc.html` (a Claude Design mockup, with
`support.js`). It is used **only** as visual reference. The generated site does
not load, embed, or depend on it, and its exact DOM is not copied.

## Ideas adopted

| Reference idea | How it maps into the generator |
|----------------|-------------------------------|
| IBM Plex Sans (body) + IBM Plex Mono (labels, dates, code) | `academic.css` font stacks with system fallbacks |
| CSS custom properties for color, switchable light/dark | `:root` + `[data-theme]` variables; inline no-flash theme init in `base.html.j2` |
| Blue accent (`#2563eb`), gray-to-white light background, slate dark background | Palette in `academic.css`; site-level tweak in `static/css/site.css` |
| Sticky, blurred header with brand, nav underline for active page, theme toggle, CV button | `.site-header`, `.nav-link.active`, `.theme-toggle`, `.btn-primary` |
| Two-column hero: portrait + name/title on the left, About + research-interest pills on the right | `layouts/homepage.html.j2` hero section + `.hero-grid` |
| Monospace "eyebrow" labels above section headings | `.eyebrow` class |
| Publication rows with authors, venue, and an expandable **BibTeX** block | `components/publication_item.html.j2` + `academic.js` (toggle + copy) |
| Project cards with thumbnail, summary, tech pills, links | `components/project_card.html.j2` + `.card-grid` |
| Experience grouped by category with a compact preview and a **"show more"** expander | homepage `collection_preview` with `mode: "expandable"`; full grouped list on `/experience/` |
| Personal notes as small linked cards | `components/personal_card.html.j2` + `.personal-grid` |
| Footer with monospace name, copyright, and social chips | `.site-footer` in `base.html.j2` |
| Rounded pills for tags/interests | `.pill` / `.pill-list` |

## Intentional deviations

- **Reusable components, not inline styles.** The reference styles everything
  inline; here each pattern is a CSS class and a Jinja component so it stays
  consistent and themeable across pages.
- **No client framework.** The reference ships a React-like runtime
  (`support.js`); the real site uses a few tiny vanilla-JS enhancers
  (`theme-toggle.js`, `academic.js`) that degrade gracefully.
- **Accessibility.** Added a skip link, real `aria-*` state on toggles,
  focus-visible behavior, `prefers-reduced-motion` handling, and semantic
  headings/landmarks.
- **Content is data.** All sections are driven by JSON/Markdown and config, so
  the layout is not tied to any specific list of pages.

## Content reconciliation

Content was drawn from the live site (`amirmahdinamjoo.com`) and reconciled with
the reference. Publications, experience, projects, service, and awards reflect
the real record; a few items carry a `_todo` field where an exact title or
author list should be confirmed. Current affiliation is **University of
Maryland** (consistent with the co-authored MICRO/IISWC papers), which is the
factual record from the live site.
