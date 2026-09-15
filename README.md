# moongas-py-mediatest
Moongas component leveraging pytest to enforce rules on media libraries. 
A simple way to use PyTest to help you keep your media collections (e.g. mp3 music libraries) organized. 
The idea is to write tests to enforce rules for your media collection. 

- A component of the `moongas` ecosystem of media library tools

- [moongas-py-mediaserver](https://github.com/bretttolbert/moongas-py-mediaserver) [![CI](https://github.com/bretttolbert/moongas-py-mediaserver/actions/workflows/ci.yml/badge.svg)](https://github.com/bretttolbert/moongas-py-mediaserver/actions/workflows/ci.yml) - Flask Web App to serve Moongas media collections enabling users to browse, search (various streaming services) and (optionally) play local media files
- [moongas-collection-demo](https://github.com/bretttolbert/moongas-collection-demo) [![CI](https://github.com/bretttolbert/moongas-collection-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/bretttolbert/moongas-collection-demo/actions/workflows/ci.yml) - Example Moongas media collection (metadata only)
- [moongas-py-mediascan](https://github.com/bretttolbert/moongas-py-mediascan) [![CI](https://github.com/bretttolbert/moongas-py-mediascan/actions/workflows/ci.yml/badge.svg)](https://github.com/bretttolbert/moongas-py-mediascan/actions/workflows/ci.yml) - Python package for loading Moongas database and Yaml
- [moongas-go-mediascan](https://github.com/bretttolbert/moongas-go-mediascan) [![CI](https://github.com/bretttolbert/moongas-go-mediascan/actions/workflows/ci.yml/badge.svg)](https://github.com/bretttolbert/moongas-go-mediascan/actions/workflows/ci.yml) - Golang module to scan media collections and Moongas Yaml metatadata, outputs Moongas database
- [moongas-py-mediatest](https://github.com/bretttolbert/moongas-py-mediatest) [![CI](https://github.com/bretttolbert/moongas-py-mediatest/actions/workflows/ci.yml/badge.svg)](https://github.com/bretttolbert/moongas-py-mediatest/actions/workflows/ci.yml) - Python tool for enforcing media collection rules (implemented with `pytest`)
- [Flask-JSGlue](https://github.com/bretttolbert/Flask-JSGlue) [![CI](https://github.com/bretttolbert/Flask-JSGlue/actions/workflows/ci.yml/badge.svg)](https://github.com/bretttolbert/Flask-JSGlue/actions/workflows/ci.yml) - Dependency of `moongas-py-mediaserver`

## Installation

### (User) Install from GitHub repo

```bash
pip install "git+https://github.com/bretttolbert/moongas-py-mediatest.git"
```

### (Developer) Clone GitHub repo and install (editable)

```bash
git clone git@github.com:bretttolbert/moongas-py-mediatest.git && cd mediatest
python -m pip install -e .
```

## Concept

The main (source) entry point of mediatest invokes pytest to run the tests under the `tests/mediatests` path. This allows mediatest to load its Yaml configuration file. 

## Usage

Modify settings in [mediatest-config.yml](./mediatest-config.yml) as needed, then run `mediatest`:

```bash
python -m mediatest mediatest-config.yml
```

Only test artist.yml:

```bash
python -m mediatest -k test_media_artist_dirs mediatest-config.yml
```

## Help

```bash
$ python -m mediatest --help
usage: python -m mediatest [-h] [--version] [--log-level LEVEL] [--ignore PATH] [-k EXPRESSION] [-m MARKEXPR] [--lf] [--pdb] [-v] [-s]
                           [-x] [--ff] [--maxfail NUM] [--durations NUM] [--durations-min SECONDS]
                           config_path

Run mediatest media tests using the provided config YAML file

positional arguments:
  config_path           Path to the mediatest config YAML file.

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --log-level LEVEL     Logging level (default: INFO).
  --ignore PATH         Path to ignore when collecting pytest tests; may be repeated.
  -k, --keyword EXPRESSION
                        Only run tests matching the pytest expression.
  -m MARKEXPR           Only run tests matching the pytest marker expression.
  --lf, --last-failed   Re-run only tests that failed during the previous execution.
  --pdb                 Drop into the Python debugger when a test fails.
  -v, --verbose         Increase pytest output details.
  -s, --capture=no      Disable pytest output capture.
  -x, --exitfirst       Stop the test suite after the first failure.
  --ff, --failed-first  Run previously failed tests first, then the remaining tests.
  --maxfail NUM         Stop after NUM test failures or errors.
  --durations NUM       Report the NUM slowest test durations.
  --durations-min SECONDS
                        Only report test durations at least SECONDS long.

```


## Development

For development purposes, if you just want to run pytest on the internal unit-tests for this package, run pytest with an `--ignore` argument to exclude the `tests/mediatests` path e.g.

```bash
pytest -vv -s --log-cli-level=DEBUG --ignore tests/media
```

## Example Test Failure

```bash
tests/test_media_lib_counts.py:97: AssertionError
======================================================= short test summary info ========================================================
FAILED tests/test_media_artist_dirs.py::test_artist_yaml_exists[artist_path2151] - AssertionError: assert False
 +  where False = exists()
 +    where exists = PosixPath('/data/Music/Various Artists/artist.yml').exists
FAILED tests/test_media_files_yaml.py::test_mediafile_albumartist_matches_artist_directory_name - AssertionError: File (path=/data/Music/Crosby, Stills and Nash/Crosby, Stills and Nash - Crosby, Stills and Nash [1969]/01.01 - Suite_ Judy Blue Eyes.mp3) albumartist 'Crosby, Stills & Nash' (escaped=Crosby, Stills & Nash)  does not match artist directory name 'Crosby, Stills and Nash'
assert 'David Crosby & Stephen Stills' == 'Crosby, Stills & Nash'
  
  - Crosby, Stills & Nash
  + David Crosby & Stephen Stills

```


## Advanced Usage

Only run filesystem tests (and not the slower files.yml tests):

```bash
pytest -k filesystem
```

## Developer Usage

Only run internal unit-tests and not media library tests:

```bash
pytest --ignore tests/media
```

## Depedencies
- [mediascan](https://github.com/bretttolbert/mediascan) (Required for ID3 tag tests) - A simple and fast Go (golang) command-line utility to recursively scan a directory for media files, extract metadata (including ID3v2 tags from both MP3 and M4A files), and save the output in a simple YAML format (e.g. [files.yml](https://github.com/bretttolbert/mediascan/blob/main/out/files.yml), and a Python library with data classes for working with the YAML files output by `mediascan.go`.

## Rules Enforced

- Top level folders are _artist_ folders
- Inside each _artist_ folder is one or more _album_ folders
- Every _album_ folder is required to have a `cover.jpg`
- Every _album_ folder name is required to have the year in square brackets
- No empty directories
- _album_ folders must contain one or more media files
- Media files types are `.mp3` and `.m4a`
- Media file count matches expected media file count
- Folder names don't contain prohibited characters which may cause problems with other filesystems (e.g. Windows)
- etc.
- Year ID3 tag must be greater than 0 (requires mediascan)
- Year ID3 tag must be less than current year (requires mediascan)
- Genre ID3 tag must be in allowed genres (see Genres below)

Of course you can adjust the rules as desired my modifying the Python.

## Genres

This library utilizes the comprehensive [`Genre` enum provided by the Moongas `mediascan` Python package](https://github.com/bretttolbert/moongas-py-mediascan/blob/main/src/mediascan/genres.py) with string values corresponding to the expected ID3 tag values. This helps avoid inconsistencies e.g. _"Post-punk"_ vs. _"Post-Punk"_ vs. _"Post punk"_ vs. _"Post Punk"_.
