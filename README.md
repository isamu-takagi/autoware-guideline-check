# autoware_guideline_check

## check-package-depends

Checks for dependencies on packages not listed in package.xml.
Dependent packages are listed using the following method.

- Search for `$(find-pkg-share <name>)` in launch.xml files (exec_depends).

## check-directory-structure

Checks whether the package directory structure meets the following.

- The 'include' directory contains only 'autoware' directory.
- The 'include/autoware' directory contains only the package name directory.
