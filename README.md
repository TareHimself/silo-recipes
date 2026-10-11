# silo-recipes

Recipes for [silo](https://github.com/TareHimself/silo), one folder per package and version:

```
recipes/<name>/<version>/silopkg.py
```

A project uses them by listing this repository in its `silo.config.toml`:

```toml
[[registry]]
name = "silo-recipes"
git = "https://github.com/TareHimself/silo-recipes"
```

and depending on a package by name and exact version:

```python
def deps(self):
    self.dep("zlib@1.3.1")
```

Recipes here depend on each other the same way. To build one from a checkout:

```
silo build recipes/zlib/1.3.1
```

Before pushing, format and check the recipes, so the same recipe always has the same text:

```
uvx ruff format . && uvx ruff check .
```

A pull request builds every recipe it reaches, one job per recipe and configuration: the changed recipes and the ones that link or run them (`silo affected`). The configurations are the profile files in `ci/profiles`, and adding a file adds one. A job fails at the start when its runner's compiler is not the kind and generation its file names. A recipe that cannot build with a profile says so in `validate()` and is skipped for it.

A new version is a new folder. A folder that has been pushed is not edited again, except to fix the recipe itself.
