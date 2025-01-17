# Ulauncher Repo Opener

> [ulauncher](https://ulauncher.io/) An ulauncher extension to open your local git repositories with your favorite editor.

## Demo

https://github.com/pascalbe-dev/ulauncher-repo-opener/assets/26909176/ee0686ba-d299-4bb2-98e0-b62a0e0c844e

## Features

- supported editors: 
  - intellij (community and ultimate)
  - vscode (normal and insiders)
  - goland
  - rustrover
  - pycharm
  - webstorm
  - rider
- open your local git repositories quickly with the editor fitting to the repos mainly used programming language (e.g. intellij for java, goland for go, ...)
  - the language <-> editor mapping can be configured in the plugin preferences
- open your local git repositories quickly with a shorthand for your preferred editor
- open subdirectories or the main directory of your mono-repository easily
  - the mono-repositories need to be configured in the plugin preferences

## Requirements

- [ulauncher 5](https://ulauncher.io/)
- Python > 3

## Installation

Open ulauncher preferences window -> extensions -> add extension and paste the following url:

`https://github.com/pascalbe-dev/ulauncher-repo-opener.git`

## Configuration

- Before usage you might want to change your base search path in the plugin preferences.

## Contribution

Please refer to [the contribution guidelines](./CONTRIBUTING.md)

## Local development

### Requirements

- `less` package installed
- `inotify-tools` package installed

### Steps

1. Clone the repo `git clone https://github.com/pascalbe-dev/ulauncher-repo-opener.git`
2. Cd into the folder `cd ulauncher-repo-opener`
3. Watch and deploy your extension for simple developing and testing in parallel `./watch-and-deploy.sh` (this will restart ulauncher without extensions and deploy this extension at the beginning and each time a file in this directory changes)
4. Check the extension log `less /tmp/ulauncher-extension.log +F`
5. Check ulauncher dev log `less /tmp/ulauncher.log +F`
