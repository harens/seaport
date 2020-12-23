# 🌊 seaport

<img src="https://avatars2.githubusercontent.com/u/4225322?s=280&v=4" align="right"
     alt="MacPorts Logo" width="150">

*A more mighty `port bump`!*

*⚠️ This program is very early on in development, and is still currently being built. Watch this space! ⚠️*

Effortlessly bumps version numbers and checksums for MacPorts portfiles.

## 💻 Usage

```txt
>>> seaport help
🌊 seaport 🌊
A more mighty port bump

Usage:
        seaport help            Display this message
        seaport name            Bump the version and checksums for this port

        seaport name [version]
```

## 📨 How it works

1) The first time the command is run, it creates a folder at `$HOME/seaport`. This is where the [local portfile repo](https://guide.macports.org/chunked/development.local-repositories.html) and cloned [macports/macports-ports](https://github.com/macports/macports-ports) are kept.
2) From the livecheck, it determines the new version.
3) Bumps the version and checksums, and then sends a PR.

## 🔨 Contributing

Any change, big or small, that you think can help improve this action is more than welcome 🎉.

As well as this, feel free to open an issue with any new suggestions or bug reports. Every contribution is appreciated.

## 📒 Notice of Non-Affiliation and Disclaimer

This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the MacPorts Project, or any of its subsidiaries or its affiliates. The official MacPorts Project website can be found at <https://www.macports.org>.

The name MacPorts as well as related names, marks, emblems and images are registered trademarks of their respective owners.
