# context-sdk

Super simple Context SDK published as `context-sdk`.

## Install

```bash
pip install context-sdk
```

## Usage

```python
from context_sdk import Context

ctx = Context()
print(ctx.echo("hello"))
```

## Development

Build the package:

```bash
python -m pip install --upgrade build twine
python -m build
```

Publish to PyPI:

```bash
python -m twine upload dist/*
```

frontier's context tool sdk
