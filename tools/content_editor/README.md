# Local content editor

This tool is separate from the generated website. It provides a localhost-only
rich-text editor for Blog and Personal entries and writes the site's JSON and
body files for you.

From `amirmahdinamjoo-site` run:

```powershell
python tools/content_editor/app.py
```

The editor opens at <http://127.0.0.1:8790/>. Use `--no-open` if you do not want
it to open a browser automatically, or `--port 9000` to choose another port.

Saving an entry updates both:

- `content/blog.json` and `markdown/posts/<slug>.md`, or
- `content/personal.json` and `markdown/personal/<slug>.md`.

Existing entries retain fields the editor does not manage. Changing a slug
creates a new body file and leaves the old one in place as a recovery copy.
Deleting an entry removes it from the JSON collection but deliberately retains
its body file.
