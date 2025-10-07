# autoware-guideline-check

This package provides tools to check the [Autoware contributing guidelines](https://autowarefoundation.github.io/autoware-documentation/main/contributing/) and other recommended conventions.

## Features

- [autoware-interface-check](./document/autoware-interface-check.md)
- [check-package-depends](./document/check-package-depends.md)
- [check-directory-structure](./document/check-directory-structure.md)

## Command line tools

```bash
pip install git+https://github.com/autowarefoundation/autoware-guideline-check.git
```

## GitHub Actions

```yaml
name: autoware-guideline-check

on:
  pull_request:
  workflow_dispatch:

jobs:
  autoware-guideline-check:
    runs-on: ubuntu-22.04
    container: ros:humble-ros-core-jammy
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Check out dependency
        run: |
          apt-get update && apt-get install -y python3-vcstool git
          mkdir -p dependency_ws
          vcs import dependency_ws < param_depends.repos
        shell: bash

      - name: Run autoware-guideline-check
        uses: autowarefoundation/autoware-guideline-check@0.2.0
```

## pre-commit

```yaml
repos:
  - repo: https://github.com/autowarefoundation/autoware-guideline-check
    rev: 0.2.0
    hooks:
      - id: check-package-depends
      - id: check-directory-structure
```
