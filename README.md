# 🌊 seaport

*A more mighty `port bump` for MacPorts!*

| Test Status | [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/harens/seaport/Tests?logo=github&style=flat-square)](https://github.com/harens/seaport/actions?query=workflow%3ATests) [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/harens/seaport/ShellCheck?label=ShellCheck&logo=github%20actions&logoColor=white&style=flat-square)](https://github.com/harens/seaport/actions?query=workflow%3AShellCheck) [![Codecov](https://img.shields.io/codecov/c/github/harens/seaport?logo=codecov&style=flat-square)](https://codecov.io/gh/harens/seaport)  |
|:--|:--|
| __Version Info__ | [![PyPI](https://img.shields.io/pypi/v/seaport?logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/seaport/) [![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/harens/seaport?logo=github&style=flat-square)](https://github.com/harens/seaport/releases) [![PyPI - Downloads](https://img.shields.io/pypi/dm/seaport?logo=python&logoColor=white&style=flat-square)](https://pypi.org/project/seaport/) |
| __Code Analysis__ |[![LGTM Grade](https://img.shields.io/lgtm/grade/python/github/harens/seaport?logo=lgtm&style=flat-square)](https://lgtm.com/projects/g/harens/seaport/) [![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/harens/seaport?logo=code%20climate&style=flat-square)](https://codeclimate.com/github/harens/seaport) [![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/harens/seaport?logo=codefactor&style=flat-square)](https://www.codefactor.io/repository/github/harens/seaport) [![Codacy grade](https://img.shields.io/codacy/grade/8539131738c3433f8057e65aab21de03?logo=codacy&style=flat-square)](https://app.codacy.com/gh/harens/seaport/dashboard?branch=master)|

## ✨ Features

* __Automatically determines new version numbers and checksums__ for MacPorts portfiles.
* __Copies the changes to your clipboard 📋__, and optionally __sends a PR to update them__.
* Contains __additional checking functionality__, such as running tests, linting and installing the updated program.
* __[PEP 561 compatible](https://www.python.org/dev/peps/pep-0561)__, with built in support for type checking.

## 🤖 Example

```
> seaport clip gping
🌊 Starting seaport...
👍 New version is 1.2.0-post
🔻 Downloading from https://github.com/orf/gping/tarball/v1.2.0-post/gping-1.2.0-post.tar.gz
🔎 Checksums:
Old rmd160: 8b274132c8389ec560f213007368c7f521fdf682
New rmd160: 4a614e35d4e1e496871ee2b270ba8836f84650c6
Old sha256: 1879b37f811c09e43d3759ccd97d9c8b432f06c75a27025cfa09404abdeda8f5
New sha256: 1008306e8293e7c59125de02e2baa6a17bc1c10de1daba2247bfc789eaf34ff5
Old size: 853432
New size: 853450
⏪️ Changing revision numbers
No changes necessary
📋 The contents of the portfile have been copied to your clipboard!
```

## ⬇️ Install

Note that if installing from PyPi or building from source, [MacPorts](https://www.macports.org/) needs to already be installed, and [GitHub CLI](https://cli.github.com/) is required if using the `--pr` flag.

### Homebrew 🍺

Binary bottles are available for x86_64_linux, catalina and big_sur.

```
brew install harens/tap/seaport
```

### PyPi 🐍

```
pip install seaport
```

## 💻 Usage

```txt
> seaport --help
Usage: seaport [OPTIONS] COMMAND [ARGS]...

  Bumps the version number and checksum of a port.

  For more information, please visit https://github.com/harens/seaport

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  clip  Bumps the version number and checksum of NAME, and copies the
        result...

  pr    Bumps the version number and checksum of NAME, and sends a PR to...
```

### 📋 `seaport clip NAME`

Copies the updated portfile to your clipboard

```txt
> seaport clip --help
🌊 Starting seaport...
Usage: seaport clip [OPTIONS] NAME

  Bumps the version number and checksum of NAME, and copies the result to
  your clipboard.

Options:
  --bump TEXT               The new version number
  --test / --no-test        Runs port test
  --lint / --no-lint        Runs port lint --nitpick
  --install / --no-install  Installs the port and allows testing of basic
                            functionality

  --help                    Show this message and exit.
```

#### 📛 `name` (_Required_)

The name of the port to update.

e.g. `seaport clip gping`

#### 🔻 `--bump TEXT`

Manually set the version number to bump it to. This should be in the same format as the output of the livecheck.

By default, it uses the value outputted from the livecheck.

This flag can be useful if there's no livecheck available or you want to override it.

e.g. `seaport clip gping --bump 1.2.0-post`

#### 🧪 `--test / --no-test` (_default `--no-test`_)

Runs `sudo port test NAME` after updating the portfile.

e.g. `seaport clip py-rich --test`

#### 🤔 `--lint / --no-lint` (_default `--no-lint`_)

Runs `port lint --nitpick NAME` after updating the portfile.

e.g. `seaport clip gping --lint`

#### 🔨 `--install / --no-install` (_default `--no-install`_)

Installs the port via the updated portfile and allows testing of basic functionality. After this has been completed, the port is uninstalled from the user's system.

e.g. `seaport clip gping --install`

### ✉️ `seaport pr NAME`

Sends a pull requrest to [macports/macports-ports](https://github.com/macports/macports-ports) with the updated portfile contents.

The flags in `clip` are also valid for this subcommand.

The pull request template is automatically filled in depending on what flags the command was run with (e.g. if `--lint` was used, this would be noted in the verification section of the template).

```txt
> seaport pr --help
🌊 Starting seaport...
Usage: seaport pr [OPTIONS] NAME LOCATION

  Bumps the version number and checksum of NAME, and sends a PR to update
  it.

Options:
  --bump TEXT               The new version number
  --test / --no-test        Runs port test
  --lint / --no-lint        Runs port lint --nitpick
  --install / --no-install  Installs the port and allows testing of basic
                            functionality

  --new                     Send a PR from the local portfile repo
  --help                    Show this message and exit.
  ```

#### 🗺 `location` (_Required_)

Where to clone the macports-ports directory to.
Note that macports-ports should not be in the location (unless you want to clone the repo to a folder with that name)

It is recommended to set the direction to a directory that already contains the cloned repo to speed up the process.
However, if you do so, please make sure your master branch is clear and has upstream defined.

The following example would create the folder ~/GitHub/macports-ports, creating any subdirectories if they don't exist.
e.g. `seaport pr gping ~/GitHub/`
  
#### ✅ `--new`

This flag is used if sending a PR for a new portfile from the user's [local portfile repo](https://guide.macports.org/chunked/development.local-repositories.html).

### 🚀 Use of sudo

Sudo is only required if `--test`, `--lint` or `--install` are specified, and it will be asked for during runtime. This is since the local portfile repo needs to be modified to be able to run the relevant commands.

Any changes made to the local portfile repo are reverted during the cleanup stage.

## 🔨 Contributing

Any change, big or small, that you think can help improve this action is more than welcome 🎉.

As well as this, feel free to open an issue with any new suggestions or bug reports. Every contribution is appreciated.

## 📒 Notice of Non-Affiliation and Disclaimer

<img src="https://avatars2.githubusercontent.com/u/4225322?s=280&v=4" align="right"
     alt="MacPorts Logo" width="150">

This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the MacPorts Project, or any of its subsidiaries or its affiliates. The official MacPorts Project website can be found at <https://www.macports.org>.

The name MacPorts as well as related names, marks, emblems and images are registered trademarks of their respective owners.

## ©️ License

Similar to other MacPorts-based projects, seaport is licensed under the [BSD 3-Clause "New" or "Revised" License](https://github.com/harens/seaport/blob/master/LICENSE).

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fharens%2Fseaport.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fharens%2Fseaport?ref=badge_large)
