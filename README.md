# autoware_guideline_check

## check-package-depends

Checks for dependencies on packages not listed in package.xml.
Dependent packages are detected as shown in the table below.

| Dependency Type | Description                                                |
| --------------- | ---------------------------------------------------------- |
| exec_depends    | Search for `$(find-pkg-share <name>)` in launch.xml files. |

## check-directory-structure

Checks whether the package directory structure meets the following.

- The 'include' directory contains only 'autoware' directory.
- The 'include/autoware' directory contains only the package name directory.
