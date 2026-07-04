## Academic Site Generator

This website is produced by a small static site generator I wrote in Python. The
core engine is deliberately generic — it understands *collections*, *pages*,
*components*, *templates*, and *static assets* — while everything academic
(publications, experience, projects, service, blog, and personal notes) lives in
a swappable **academic preset** and in per-site configuration.

### Highlights

- Content authored in JSON/YAML and Markdown, with math support.
- A template override chain so a site can restyle one component without forking
  the whole theme.
- Light/dark theming, a responsive layout, BibTeX generation, sitemap, and an
  Atom feed.
- GitHub Pages deployment via GitHub Actions.

The generator is a separate, reusable project, so the same engine could build a
very different academic website from a different configuration.
