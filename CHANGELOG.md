Example content to imitate

# Changelog
All notable changes to this project will be documented in this file.
The format is based on Keep a Changelog and this project adheres to Semantic Versioning.

## [Unreleased]

## [1.4.0] - 2025-08-31
### Added
- New CHSH scoring policy interface (#412).

### Changed
- `SamplerAdapter` now accepts an instantiated backend instead of a name (#405).

### Fixed
- Avoid crash when `backend.properties()` is unavailable (#418).

## [1.3.2] - 2025-07-12
### Fixed
- Correct T1 dictionary generation for Aer simulator (#399).

## [1.3.0] - 2025-06-01
### Added
- `MinimumAcceptableValue` threshold policy (#372).