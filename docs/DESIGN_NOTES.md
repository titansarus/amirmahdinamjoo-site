# Design Notes

Source of inspiration: `design/Homepage.dc.html` (a Claude Design mockup, with
`support.js`). It is used **only** as visual reference. The generated site does
not load, embed, or depend on it, and its exact DOM is not copied.

## Ideas adopted

| Reference idea | How it maps into the generator |
|----------------|-------------------------------|
| IBM Plex Sans (body) + IBM Plex Mono (labels, dates, code) | `academic.css` font stacks with system fallbacks |
| CSS custom properties for color, switchable light/dark | `:root` + `[data-theme]` variables; inline no-flash theme init in `base.html.j2` |
| Blue accent (`#2563eb`), gray-to-white light background, slate dark background | Palette in the academic preset's `academic.css` |
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

Content is sourced from the author's Hugo/Wowchemy repository
[`titansarus/amirmahdi-namjoo`](https://github.com/titansarus/amirmahdi-namjoo)
(the source of `amirmahdinamjoo.com`) and reorganized into this generator's
collection model. Publications carry the real titles, authors, DOIs, links, and
BibTeX from that repo's `cite.bib` files; experience, honors, service, and the
15 projects reflect the real record. Current affiliation is **University of
Southern California**, where the ECE Ph.D. begins in August 2026; the M.Sc. at
the University of Maryland spans 2024–2026.

## Icons and logos

Real assets are reused from the source repository rather than text glyphs:

- **Social links** render real brand icons (GitHub, LinkedIn, Google Scholar,
  email, Telegram) via an inline-SVG macro (`components/social_icon.html.j2`,
  `currentColor` so they theme automatically).
- **University / organization logos** (Sharif, CMMRS, ICPC, SSC, WSS, Hardwar,
  DataDays, YSC) appear on experience, honors, and service items via each item's
  `logo` field; items without an available logo fall back to initials.
- **Technology icons** on project cards are driven by the generic `tech_icons`
  map in `site.config.json`, so the engine ships no built-in icon set.
- The avatar (`assets/images/profile.jpg`) and résumé (`assets/files/cv.pdf`)
  are the real files from the source repo.
