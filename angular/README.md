# Angular files for wger

This folder contains the angular components used in the wger application.


## Installation

Note that installing angular is only needed during development of angular code,
the compiled javascript is in `core/static/angular`.

Compile angular code, in wger root folder:

```bash
yarn build:angular
```

or in this folder:

```
ng build --configuration production --output-path ../wger/core/static/angular --watch --output-hashing none
```

## Updating angular

Update angular to a new version with

```bash
ng update @angular/core @angular/cli
```
