This repository is created to generate a git pre-commit hook, building a function call graph, via `pre-commit` framework.

The main tool of the project is `Pyan`, a Python module that performs static analysis of Python code to build a function call graph.

The [original codebase](https://github.com/davidfraser/pyan) for Pyan support neither `asyncio`, nor installation via `pip install` command,
so forks were created to implement these features ([asyncio](https://github.com/bdeetz/pyan) and [pip install](https://github.com/ttylec/pyan)).
We endeavoured to combine those modifications in a homebrew version of Pyan, maintained in [this repository](https://github.com/seryogin17/pyan).
