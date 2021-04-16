# PhishFramework Developer Documentation

### Tartufo

[Tartufo](https://github.com/godaddy/tartufo) is a tool to search through git
repositories for secrets, digging deep into commit history and branches.
Tartufo is used by git pre-commit scripts to screen changes for secrets before
they are committed to the repository.

Tartufo should be executed automatically before any git commit operations take
place, if the **pre-commit** hook is installed, as described below.

To manually check the current working files for secrets, tartufo can be invoked
manually:

```
tartufo scan-local-repo .
```

### pre-commit

[pre-commit](https://pre-commit.com/) is a multi-language package manager for
pre-commit hooks, and
runs various
tests before a git commit can proceed.  The tests are described in the
`.pre-commit-config.yaml` file in the top level directory of this repository.

If you've just checked out this repository, you'll need to invoke the following
to install the pre-commit hook in your local git working tree:

```bash
pre-commit install
```

A tartufo scan will be run whenever `git commit` is performed.  To manually run
the pre-commit hooks, use the following command:

```bash
pre-commit run -a
```
