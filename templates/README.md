# Site template overrides (optional)

Files here override the generator's templates by matching their relative path.
Resolution order (first match wins):

1. `templates/` in this repo (here)
2. the active preset's templates (`acadsite/presets/academic/templates/`)
3. core templates (`acadsite/templates/core/`)

For example, to restyle only project cards, create:

```
templates/components/project_card.html.j2
```

You do **not** need to copy the whole theme — override just the one component or
layout you want to change. This site currently relies on the academic preset
templates and only customizes appearance through `static/css/site.css`.
