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

A new version is a new folder. A folder that has been pushed is not edited again, except to fix the recipe itself.
