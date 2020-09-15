# Tile that can display Multiple Release Information

[![License MIT][license-image]][license-url]
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/775983abff7e44cf9645ed5515546019)](https://www.codacy.com/gh/xebialabs-community/xlr-multi-release-tile?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=xebialabs-community/xlr-multi-release-tile&amp;utm_campaign=Badge_Grade)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-blue.svg)](https://github.com/RichardLitt/standard-readme)
[![Github All Releases](https://img.shields.io/github/downloads/xebialabs-community/xlr-multi-release-tile/total.svg)]()
![Code Climate](https://codeclimate.com/github/xebialabs-community/xlr-multi-release-tile/badges/gpa.svg)


## Preface

This document describes the functionality provided by the XL Release Multiple Release Tile.

See the [XL Release reference manual](https://docs.xebialabs.com/xl-release) for background information on XL Release and release automation concepts.

## Overview

The `xlr-multi-release-tile` is an [XL Release](https://docs.xebialabs.com/v.9.6/xl-release) tile allows
you to extend the tiles to view statics on multiple releases that you can currently only see per release

## Installation

### Building the Plugin

You can use the gradle wrapper to build the plugin. Use the following command to build
using [Gradle](https://gradle.org/):

```
./gradlew clean assemble

```
The built plugin, along with other files from the build, can then be found in the _build_ folder.

### Adding the Plugin to XL Deploy

For the latest instructions on installing XL Deploy plugins, consult the [associated documentation on docs.xebialabs.com](https://docs.xebialabs.com/xl-deploy/how-to/install-or-remove-xl-deploy-plugins.html).

## Usage

This plugin allows for insights on the multiple releases that is normally restricted to each release itself. The tile in this plugin allows you to see all the release that fit a certain creiteria like a time period (tags coming soon) and view the expected times of all the phases in the selected releases at once instead of going to each release individually.

To configure the tool you must first at your xl release instance in the shared configurations.
Then add the multi release tile and set your parameters as desired. (tags and date range not available yet)

This tile should be extended to give more tiles for multiple releases

Filters are OR not AND

## Contributing

Please review the contributing guidelines for _xebialabs-community_ at [http://xebialabs-community.github.io/](http://xebialabs-community.github.io/)

## License

This community plugin is licensed under the [MIT license][license-url].

See license in [LICENSE.md](LICENSE.md)

[license-image]: https://img.shields.io/badge/license-MIT-yellow.svg
[license-url]: https://opensource.org/licenses/MIT

# References #
* [XL Release Rest Api](https://docs.xebialabs.com/xl-release/6.0.x/rest-api)
* [Custom endpoints in XL Release](https://docs.xebialabs.com/v.9.5/xl-release/how-to/declare-custom-rest-endpoints)
