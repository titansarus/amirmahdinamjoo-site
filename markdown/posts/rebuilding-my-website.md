I recently rebuilt this website from scratch. The old version was a pile of
hand-written HTML that was painful to update, so I decided to build a small
static site generator instead while keeping the generator reusable rather than
hardcoding it around my own pages.

## The core idea

The engine knows nothing about "publications" or "experience". It only knows
about a few generic concepts:

- **collections**: lists of structured items loaded from JSON, YAML, or Markdown
- **pages**: output routes driven by a named layout template
- **components**: reusable template partials
- **homepage sections**: configurable blocks like a hero, a preview, or news

Everything academic lives in a *preset* and in configuration. That means the
same generator could build a very different site, such as a lab page, a course site, or a
portfolio, without touching the engine.

## What I get for free

Because the structure is data, the site gets consistent behavior everywhere:
sorted and grouped timelines, BibTeX buttons on publications, a light/dark
theme, a sitemap, and an Atom feed. Adding a new section is a config change, not
a code change.

## What's next

I want to add better citation metadata, per-post reading time, and maybe a small
search box. For now, it is already far nicer to maintain than what it replaced.
