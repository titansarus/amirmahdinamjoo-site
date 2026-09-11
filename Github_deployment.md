# Deploying the site with GitHub Pages

This project is split into two Git repositories:

- `academic-site-generator` contains the reusable Python static-site generator.
- `amirmahdinamjoo-site` contains this site's configuration, content, and deployment workflow.

During local development, install the generator from the sibling checkout. In GitHub Actions, the site installs the generator from the release tag pinned in `requirements.txt`. Publish the generator repository and its tag before deploying the site repository.

## 1. Create the GitHub repositories

Sign in to the `titansarus` GitHub account and create these two repositories:

1. `academic-site-generator`
2. `amirmahdinamjoo-site`

Create them empty: do not initialize them with a README, `.gitignore`, or license, because both local repositories already contain commits.

GitHub Pages is simplest when the site repository is public. Private-repository availability depends on the GitHub plan and organization policy.

## 2. Publish the generator first

From the parent workspace in PowerShell:

```powershell
git -C .\academic-site-generator remote add origin https://github.com/titansarus/academic-site-generator.git
git -C .\academic-site-generator remote -v
git -C .\academic-site-generator push -u origin main
git -C .\academic-site-generator push origin v0.2.0
```

The last command is required because the site currently installs:

```text
acadsite @ git+https://github.com/titansarus/academic-site-generator.git@v0.2.0
```

Do not move or reuse a published release tag. Create a new version tag for each generator release.

If `origin` already exists, replace the first command with:

```powershell
git -C .\academic-site-generator remote set-url origin https://github.com/titansarus/academic-site-generator.git
```

## 3. Publish the site

Still from the parent workspace:

```powershell
git -C .\amirmahdinamjoo-site remote add origin https://github.com/titansarus/amirmahdinamjoo-site.git
git -C .\amirmahdinamjoo-site remote -v
git -C .\amirmahdinamjoo-site push -u origin main
```

If `origin` already exists, use:

```powershell
git -C .\amirmahdinamjoo-site remote set-url origin https://github.com/titansarus/amirmahdinamjoo-site.git
```

Use Git Credential Manager, SSH, or the GitHub CLI to authenticate. Never store a personal access token in either repository.

## 4. Enable GitHub Pages

In the `amirmahdinamjoo-site` repository on GitHub:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Do not select a branch-based deployment source; the workflow uploads and deploys a generated artifact.
4. Open the **Actions** tab and allow repository workflows if GitHub prompts you to do so.

The `github-pages` environment is created by the deployment flow. The workflow itself grants only the permissions it needs: read access while building, then `pages: write` and `id-token: write` only in the deployment job.

## 5. Understand the included workflow

The deployment workflow already exists at `.github/workflows/deploy.yml`:

```yaml
name: Deploy website to GitHub Pages

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: github-pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - name: Check out repository
        uses: actions/checkout@v7
        with:
          persist-credentials: false

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install generator
        run: |
          python -m pip install --disable-pip-version-check --upgrade pip==26.2.1
          python -m pip install --disable-pip-version-check -r requirements.txt

      - name: Validate content
        run: acadsite validate --site . --env production

      - name: Build static site
        run: acadsite build --site . --output public --env production

      - name: Configure GitHub Pages
        uses: actions/configure-pages@v5

      - name: Upload GitHub Pages artifact
        uses: actions/upload-pages-artifact@v4
        with:
          path: public

  deploy:
    runs-on: ubuntu-latest
    needs: build
    timeout-minutes: 10
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

On each push to `main`, the workflow installs the tagged generator, validates the `production` environment, builds static files into `public`, uploads that directory as a Pages artifact, and deploys it. `workflow_dispatch` also adds a **Run workflow** button for manual deployments. The `production` environment is required for the current custom domain because it builds root-relative asset URLs and emits `CNAME`.

The generated `public` directory is a build artifact and should not be committed. No `gh-pages` branch or server-side Python process is needed.

## 6. Verify the first deployment

After the generator repository, `v0.2.0` tag, and site repository have been pushed:

1. Open **Actions → Deploy website to GitHub Pages**.
2. Confirm that both the `build` and `deploy` jobs succeed.
3. Open the deployment URL shown by the `deploy` job.

With the current custom-domain configuration, the site URL is:

```text
https://amirmahdinamjoo.com/
```

The corresponding environment in `site.config.json` is already configured as:

```json
"production": {
  "site": {
    "base_url": "https://amirmahdinamjoo.com",
    "base_path": "/",
    "custom_domain": "amirmahdinamjoo.com"
  }
}
```

If the custom domain is removed, change both workflow commands back to `--env github-pages`. The existing `github-pages` environment builds for `https://titansarus.github.io/amirmahdinamjoo-site/` with `/amirmahdinamjoo-site/` as its base path.

## 7. Test before pushing

Create and activate a virtual environment once, then install the sibling generator in editable mode:

```powershell
cd .\amirmahdinamjoo-site
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e "..\academic-site-generator[dev]"
```

For ordinary local preview:

```powershell
acadsite validate --site .
acadsite build --site . --output public
python -m http.server 8000 --directory public
```

Open `http://localhost:8000/`. Stop the server with `Ctrl+C`.

Also validate the deployed custom-domain environment before pushing:

```powershell
acadsite validate --site . --env production
acadsite build --site . --output public --env production
```

That second build uses root-relative URLs and writes `public/CNAME` for `amirmahdinamjoo.com`. The Actions workflow performs the same validation and build on Linux.

## 8. Release generator updates

When a site change requires a generator change:

1. Update the generator version in `academic-site-generator`.
2. Run its tests and commit the change.
3. Create and push a new release tag, for example `v0.2.1`.
4. Change the tag in `amirmahdinamjoo-site/requirements.txt` to the new tag.
5. Validate and build the site locally.
6. Commit and push the site change.

Example release commands after committing a tested generator update:

```powershell
git -C .\academic-site-generator tag -a v0.2.1 -m "Release v0.2.1"
git -C .\academic-site-generator push origin main
git -C .\academic-site-generator push origin v0.2.1
```

Push the site only after the new generator tag is available on GitHub. Otherwise, the workflow cannot install it.

## 9. Custom domain

The workflow is currently configured to deploy `https://amirmahdinamjoo.com`:

1. Keep both workflow commands set to `--env production`.
2. Confirm that the `production` environment in `site.config.json` has `base_path: "/"` and `custom_domain: "amirmahdinamjoo.com"`.
3. The generator will include the correct `CNAME` file in the deployed artifact.
4. In **Settings → Pages → Custom domain**, enter `amirmahdinamjoo.com` and save it. A `CNAME` file alone does not configure the repository setting.
5. At the DNS provider, add GitHub Pages' current apex-domain `A` records. Optional `AAAA` records provide IPv6. For a `www` subdomain, use a `CNAME` pointing to `titansarus.github.io`.
6. Verify the domain in the GitHub account's Pages settings to reduce domain-takeover risk.
7. After GitHub provisions the certificate, enable **Enforce HTTPS**.

Check GitHub's documentation immediately before editing DNS because the published IP addresses and domain instructions can change. Avoid wildcard DNS records such as `*.amirmahdinamjoo.com`.

## Troubleshooting

### The workflow cannot install `acadsite`

If the log says that `v0.2.0` cannot be found, confirm that the generator repository is accessible and the tag was pushed:

```powershell
git -C .\academic-site-generator ls-remote --tags origin v0.2.0
```

### The page loads without styles, or links return 404

The deployment environment probably does not match the public URL. For `amirmahdinamjoo.com`, the workflow must build `--env production` and `base_path` must be `/`. For the project URL, the workflow must build `--env github-pages` and `base_path` must be `/amirmahdinamjoo-site/`.

### The Pages deployment job is skipped or rejected

Confirm that **Settings → Pages → Source** is set to **GitHub Actions**. For organization-owned repositories, also check organization Actions and Pages policies.

### A push does not start the workflow

The automatic trigger watches the `main` branch. Confirm the pushed branch with:

```powershell
git -C .\amirmahdinamjoo-site branch --show-current
```

You can also start it manually from **Actions → Deploy website to GitHub Pages → Run workflow**.

## Official references

- [Adding locally hosted code to GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [Configuring a publishing source for GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Verifying a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
- [Securing a Pages site with HTTPS](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https)
