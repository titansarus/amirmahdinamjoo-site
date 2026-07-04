# amirmahdinamjoo-site

The personal academic website of **Amirmahdi Namjoo**. Content is authored as
JSON and Markdown; the site is built by the reusable
[`acadsite`](https://github.com/titansarus/academic-site-generator) static site
generator (the `academic` preset).

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
static/css/site.css     # site-specific style layer (extends the preset)
templates/              # optional template overrides (see templates/README.md)
design/                 # Claude Design reference (inspiration only)
docs/DESIGN_NOTES.md    # how the reference maps to the templates
.github/workflows/      # GitHub Pages deployment
```

## Local development

Install the generator from the sibling repo in editable mode, then build:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -e ../academic-site-generator

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
`deploy-pages`). It installs the generator from a sibling checkout if present,
otherwise from `requirements.txt` (a Git dependency).

Steps to go live on the test domain:

1. Push this repo to `https://github.com/titansarus/amirmahdinamjoo-site`.
2. In **Settings → Pages**, set **Source: GitHub Actions**.
3. The workflow builds with `--env github-pages` and publishes to
   `https://titansarus.github.io/amirmahdinamjoo-site/`.

To later move to the custom domain, switch the build to `--env production`
(which emits the `CNAME`) and configure DNS.

## Content notes

Some publication entries include a `_todo` field marking an exact title or
author list to confirm; `_todo` fields are ignored by the build. Replace
`assets/files/cv.pdf` and `assets/images/profile.svg` with the real CV and
portrait when available.
