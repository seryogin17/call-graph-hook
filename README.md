### Call graph git hook

This repository is created to generate a git pre-commit hook, building a function call graph, via [`pre-commit`](https://pre-commit.com/#intro) framework.

The main tool of the project is `Pyan`, a Python module that performs static analysis of Python code to build a function call graph.
The [original codebase](https://github.com/davidfraser/pyan) for Pyan support neither `asyncio`, nor installation via `pip install` command,
so forks were created to implement these features ([asyncio](https://github.com/bdeetz/pyan) and [pip install](https://github.com/ttylec/pyan)).
We endeavoured to combine those modifications in a homebrew version of Pyan, maintained in [this repository](https://github.com/seryogin17/pyan).

So to use this call graph hook via `pre-commit` framework run the folowing commands:
1. Install `Pyan` module
```bash
pip install git+https://github.com/seryogin17/pyan.git
```
2. Install `pre-commit` framework via conda or pip
```bash
conda install -c conda-forge pre-commit
```
```bash
pip install pre-commit
```
3. Create `callgraph.config.json` file in your project directory and supply it with the relevant options as in the example given below:
```json
{
    "files": ['module_name.py', 'another_module_name.py'],
    "input_directory": "/path/to/progect/dir",
    "output_format": "png"
}
```
4. Create `.pre-commit-config.yaml` file in your project directory according to the rules described [here](https://pre-commit.com/#2-add-a-pre-commit-configuration) in detail and fill the `args` field with the name of `callgraph.config.json` file.
repos:
```yaml
-   repo: https://github.com/seryogin17/callgraph-hook.git
    rev: v1.0
    hooks:
    -   id: pre-commit-callgraph
        args: [callgraph.config.json]
```
5. Install all hook scripts listed in your `.yaml` file
```bash
pre-commit install
pre-commit installed at .git/hooks/pre-commit
```
6. Stage all the changes you are to commit
```
git stage module_name.py another_module_name.py
```
7. Commit the changes and watch the output hook resulted
```
git commit -m "commit message"
Callgraph.........................................Passed
[master ba9905b] commit message
```

For more available git hooks, supported by `pre-commit` click [here](https://pre-commit.com/hooks.html).
