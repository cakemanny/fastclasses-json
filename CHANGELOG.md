# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Removed
- Support for Python 3.7. If you still use Python 3.7, ensure you pin the
  version to 0.7.0

## [0.7.0] - 2024-02-04
### Added
- Support for Python 3.12

## [0.6.1] - 2022-11-26
### Fixed
- Made implicit Optional type annotations explicit following change in
  mypy defaults (see <https://github.com/python/mypy/pull/13401>)

## [0.6.0] - 2022-10-07
### Added
- `field_name_transform` option for allowing universal field name
  tranformations ([#7][#7])

## [0.5.0] - 2022-03-29
### Added
- Support for Python 3.7 ([#6][#6])

## [0.4.1] - 2022-01-10
### Fixed
- The mypy plugin being broken as of mypy 0.930.
  (Namely by these changes <https://github.com/python/mypy/pull/11332>)

## [0.4.0] - 2021-12-17
### Added
- Support for all kinds of keys types that `json.dumps` supports, for `Dict`
  fields. And UUIDs
- Support for Mapping, Sequence and Tuple fields
### Fixed
- Not producing subclasses of datetime when [python-dateutil] is installed.

## [0.3.2] - 2021-12-07
### Fixed
- Performance issue caused by importing dateutil in every `from_dict`
  when [python-dateutil] is installed

## [0.3.1] - 2021-11-12
### Fixed
- Custom encoder not being used on Union typed fields ([#5][#5]).
  Thanks [@Borealin][user-Borealin] for reporting.

## [0.3.0] - 2021-11-09
### Added
- Support the use of defaults and `default_factory` when deserialising.

## [0.2.3] - 2021-11-06
### Fixed
- The mypy plugin not working in external projects due to mypy refusing
  to analyse the module.

## [0.2.2] - 2021-11-04
### Added
- Dummy `infer_missing` parameter to `from_dict` to make migration from
  dataclasses-json easier

## [0.2.1] - 2021-10-16
### Added
- Use of [python-dateutil] for date/datetime parsing when installed
### Fixed
- Fix crash when type arguments are omitted for typing.List and typing.Dict

[python-dateutil]: https://github.com/dateutil/dateutil

## [0.2.0] - 2021-08-31
### Added
- Support for custom encoders and decoders
- Support for overriding field names

## [0.1.0] - 2021-08-14
### Added
- This CHANGELOG file
- Support for Decimals and UUIDs

<!-- VERSION LINKS START -->
[Unreleased]: https://github.com/cakemanny/fastclasses-json/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/cakemanny/fastclasses-json/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/cakemanny/fastclasses-json/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/cakemanny/fastclasses-json/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/cakemanny/fastclasses-json/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/cakemanny/fastclasses-json/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/cakemanny/fastclasses-json/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/cakemanny/fastclasses-json/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/cakemanny/fastclasses-json/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/cakemanny/fastclasses-json/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/cakemanny/fastclasses-json/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/cakemanny/fastclasses-json/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/cakemanny/fastclasses-json/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/cakemanny/fastclasses-json/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/cakemanny/fastclasses-json/releases/tag/v0.1.0
<!-- VERSION LINKS END -->
[user-Borealin]: https://github.com/Borealin
[#5]: https://github.com/cakemanny/fastclasses-json/issues/5
[#6]: https://github.com/cakemanny/fastclasses-json/issues/6
[#7]: https://github.com/cakemanny/fastclasses-json/issues/7
