# autoware_guideline_check

## Usage as pre-commit

```yaml
repos:
  - repo: https://github.com/isamu-takagi/autoware-guideline-check
    rev: 0.1.0
    hooks:
      - id: check-package-depends
      - id: check-directory-structure
```

## Usage as a command line tool

```bash
pip install git+https://github.com/isamu-takagi/autoware-guideline-check.git
```

The following commands will be installed.

- check-package-depends
- check-directory-structure

## check-package-depends

Checks for dependencies on packages not listed in package.xml.
Dependent packages are listed using the following method.

- Search for `$(find-pkg-share <name>)` in launch.xml files (exec_depend).

## check-directory-structure

Checks whether the package directory structure meets the following.

- The 'include' directory contains only 'autoware' directory.
- The 'include/autoware' directory contains only the 'package name' directory.
