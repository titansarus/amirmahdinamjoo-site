# amirmahdinamjoo-site

The personal academic website of **Amirmahdi Namjoo**. Content is authored as
JSON and Markdown; the site is built by the reusable
[`acadsite`](https://github.com/titansarus/academic-site-generator) static site
generator.

## Note

Most of the site code was written with the help of AI coding tools, including OpenAI Codex and Claude Code.

I wanted to personally evaluate their workflow and how well they could follow the instructions I gave them for building a modular academic site generator (think of it like Jekyll), and then creating a website for myself using this academic site generator. The overall design direction, how the content should be organized on each page, what features the website should include, and similar decisions were instructed by me, while most of the actual code was written by AI.

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

## Projects page

Projects use the academic preset's reusable card-grid component. The personal
configuration selects the generic `collection_page` layout and the projects
collection uses `type: cards`; no site-specific project template is required.

## Partial page navigation

Navbar links progressively fetch the destination's generated HTML and replace
only `<main>`. The header, footer, theme state, and JavaScript stay mounted while
the URL, title, active navigation item, and browser history remain correct.
Direct links, refreshes, search engines, and browsers without JavaScript still
receive complete static HTML pages.

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

## Enable or disable sections

Edit `features.yml` and change one value. To hide the blog everywhere:

```yaml
blog: false
```

That hides the blog from navigation and the homepage and stops generating its
pages and feed entries. The JSON and Markdown content stays untouched. The same
switches apply to both themes.

To hide only the Personal preview from the main page while keeping the full
Personal page, change the nested homepage flag:

```yaml
homepage:
  personal_sections: false
```

The `pages` group independently controls standalone pages and their navigation
links. Top-level flags remain the global master switches.

University and organization logo paths remain in the content and assets but
are hidden in the first public design. Restore them later with one line:

```yaml
organization_logos: true
```

## Blog and Personal editor

The local rich-text editor is a development tool and is never copied into the
generated website. Run it from this repository:

```powershell
python tools/content_editor/app.py
```

It opens <http://127.0.0.1:8790/> and can create, load, edit, or remove Blog and
Personal entries. Saving updates the appropriate `content/*.json` inventory and
`markdown/**/<slug>.md` body file together. See
`tools/content_editor/README.md` for recovery and command-line details.

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
