# amirmahdinamjoo-site

The personal academic website of **Amirmahdi Namjoo**. Content is authored as
JSON and Markdown; the site is built by the reusable
[`acadsite`](https://github.com/titansarus/academic-site-generator) static site
generator.

## Structure

```
site.config.json        # site config: collections, pages, homepage sections, envs
content/                # structured content (JSON)
  profile.json          # hero / about / research interests / links
  publications.json     # publications (with DOIs and BibTeX support)
  experience.json       # research, teaching, industry, education timeline
  awards.json           # honors & awards
  projects.json         # project cards (+ detail pages)
  service.json          # academic service timeline
  blog.json             # blog posts (+ detail pages)
  personal.json         # open-ended personal Markdown sections
  news.json             # homepage news list
markdown/               # Markdown bodies for posts, projects, personal sections
assets/                 # images, logos, files (cv.pdf)
templates/              # optional overrides; currently documentation only
design/                 # Claude Design reference (inspiration only)
docs/DESIGN_NOTES.md    # how the reference maps to the templates
.github/workflows/      # GitHub Pages deployment
```

## Themes

The same content is available in **two independent themes**, selected by config
file. The content, assets, and Markdown are shared; only the preset (templates +
CSS) differs.

| | Theme1 | Theme2 |
|---|--------|--------|
| Config | `site.config.json` | `site.theme2.json` |
| Preset | `academic` | `minimal` |
| Feel | Clean, professional, card/timeline layout, blue accent | Personal single-column essay, warm paper, serif display, terracotta accent |

Build each:

```bash
acadsite build --site . --output public                          # Theme1
acadsite build --site . --config site.theme2.json --output public-theme2   # Theme2
```

Preview folders: `_site-preview/amirmahdinamjoo-site/` (Theme1) and
`_site-preview/amirmahdinamjoo-site-theme2/` (Theme2). Serve either with
`python -m http.server -d <folder> 8000`.

## Projects page — two designs to compare

The **Projects** page selects the academic preset's reusable
`projects_showcase` layout and currently renders the same projects in **two
designs** so they can be compared:

- **Design A — List view:** a compact horizontal list, like the experience and
  service sections.
- **Design B — Card view:** reworked cards with an accent bar instead of an
  empty image placeholder.

Once a preferred design is chosen, set the page's `layout` back to
`collection_page` (Design B is the default `cards` rendering), or update the
reusable preset layout in the generator. Presentation code remains generator-owned.

## Local development

Install the sibling generator in editable mode, then build:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -e "../academic-site-generator[dev]"

acadsite validate --site .
acadsite build --site . --output public
```

Open the result with a local web server (absolute asset paths need a server,
not `file://`):

```bash
python -m http.server -d public 8000
# visit http://localhost:8000/
```

## Environments

The config defines environment overlays:

| Command | base_url | base_path | CNAME |
|---------|----------|-----------|-------|
| `acadsite build --site .` | *(none)* | `/` | no |
| `acadsite build --site . --env github-pages` | `https://titansarus.github.io` | `/amirmahdinamjoo-site/` | no |
| `acadsite build --site . --env production` | `https://amirmahdinamjoo.com` | `/` | `amirmahdinamjoo.com` |

The **default** and **github-pages** environments do not emit a `CNAME`. The
custom domain is only enabled by the `production` overlay, so the test
deployment on `titansarus.github.io` stays on the project-page domain.

## Deployment (GitHub Pages)

`.github/workflows/deploy.yml` builds and deploys on every push to `main` using
GitHub Actions (`actions/checkout@v7`, `configure-pages`, `upload-pages-artifact`,
`deploy-pages`). It installs the generator version pinned in `requirements.txt`,
validates the site, and generates the static Pages artifact.

Steps to go live on the test domain:

1. Push this repo to `https://github.com/titansarus/amirmahdinamjoo-site`.
2. In **Settings → Pages**, set **Source: GitHub Actions**.
3. The workflow builds with `--env github-pages` and publishes to
   `https://titansarus.github.io/amirmahdinamjoo-site/`.

To later move to the custom domain, switch the build to `--env production`
(which emits the `CNAME`) and configure DNS.

## Content

Content (profile, publications with real BibTeX, experience, honors, service,
and projects) is sourced from the author's Hugo/Wowchemy site,
[`titansarus/amirmahdi-namjoo`](https://github.com/titansarus/amirmahdi-namjoo),
and reorganized into this generator's collection model. The real résumé
(`assets/files/cv.pdf`), avatar (`assets/images/profile.jpg`), and the
university/organization logos and technology icons under `assets/logos/` and
`assets/icons/tech/` are copied from that repository.

Social links render real brand icons via an inline-SVG macro
(`components/social_icon.html.j2`); project technology pills show icons via the
`tech_icons` map in `site.config.json`. The only placeholder is the Google
Scholar link, which points to a name search until a profile URL is added.
