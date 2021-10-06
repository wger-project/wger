# Angular files for wger

This folder contains the angular components used in the wger application.


## Installation

Note that installing angular is only needed during development of angular code,
the compiled javascript is in `core/static/angular`.

Compile angular code, in wger root folder:

```shell
yarn build:angular
```

or in this folder:

```shell
ng build --configuration production \
  --output-path ../wger/core/static/angular \
  --output-hashing none \
  --localize
```

## i18n

```shell
ng extract-i18n --output-path src/locale/
```


## Updating angular

Update angular to a new version with

```shell
ng update @angular/core @angular/cli
```

