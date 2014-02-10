# YAML CSS Framework

YAML (*Yet Another Multicolumn Layout*) is a modular CSS framework for truly flexible, accessible and responsive websites. YAML is focussed on device independent screen design and provides bullet-proof modules for flexible layouts. This is a perfect starting point and the key to truly responsive design.

- Latest version: 4.1.2
- Website: <http://www.yaml.de>

## Quick Start
### Using the CSS port
Download the project and take a look at the provided examples in the `demos/` folder.

### Using the Sass Port
You need to have [Ruby](http://www.ruby-lang.org/en/downloads/), [Sass](http://sass-lang.com/download.html) and [Compass](http://compass-style.org/install/) installed.

* `compass compile` starts a single compass run to compile sass/scss files to CSS.
* `compass watch` starts the compass watcher that recompiles your sass/scss files on every change.

#### Folder Structure
The Sass port is built in a way that allows you to create a fully customized version of YAML's framework files.

* `./sass/css/` (for your Sass projects)
* `./sass/docs/assets/css/` (YAML Docs CSS - built with Sass)
* `./sass/static-build/` (file wrapper for YAML builds, can be deleted if don't want to compile static YAML builds)
* `./sass/yaml-sass/` (Sass port of YAML CSS Framework)

Please keep in mind, that the /yaml-sass/ folder also contains several JavaScript files that are needed to create a complete YAML build.


### Create Custom YAML Builds

You need to have [Node.js](http://nodejs.org/download/), [Grunt-CLI](http://gruntjs.com/getting-started), [Ruby](http://www.ruby-lang.org/en/downloads/), [Sass](http://sass-lang.com/download.html) and [Compass](http://compass-style.org/install/) installed. Run `npm install` once in the root directory of this project to resolve and install all Grunt dependencies.

The following tasks are provided:

* `grunt` starts a single compass run to compile sass/scss files to CSS.
* `grunt watch` starts the compass watcher that recompiles your sass/scss files on every change.
* `grunt build` compiles and optimizes all static YAML4 CSS files for release/production.
* `grunt build-utf8` same functionality like `grunt build` but doesn't remove `@charset "utf8"` rule from CSS files

## Docs
Download or clone this project and open file `docs/index.html` in your browser.

## Licenses
### YAML under Creative Commons License (CC-BY 2.0)

The YAML framework is published under the [Creative Commons Attribution 2.0 License (CC-BY 2.0)](http://creativecommons.org/licenses/by/2.0/), which permits
both private and commercial use.

*Condition: For the free use of the YAML framework, a backlink to the YAML homepage (<http://www.yaml.de>) in a
suitable place (e.g.: footer of the website or in the imprint) is required.*

In general it would be nice to get a short note when new YAML-based projects are released. If you are highly
pleased with YAML, perhaps you would like to take a look at my [Amazon wish](https://www.amazon.de/gp/registry/wishlist/108Q0YYJ49UC2/) list?

### YAML under Commercial Distribution License (YAML-CDL)

If you are a commercial software developer and you want to release your software under a license that doesn't fit to the [Creative Commons Attribution 2.0 License](http://creativecommons.org/licenses/by/2.0/), you may purchase a commercial license. We offer the following commercial license models:

- Project Related License
- General License
- OEM License

Full license texts and contact information are available at: <http://www.yaml.de/license.html>

