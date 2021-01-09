# Ulauncher Repo Opener

> [ulauncher](https://ulauncher.io/) An ulauncher extension to open your local git repositories with your favorite editor.

## Usage

TODO: ADD DEMO GIF

## Features

TODO: ADD FEATURES

## Requirements

- [ulauncher 5](https://ulauncher.io/)
- Python > 3

## Install

Open ulauncher preferences window -> extensions -> add extension and paste the following url:

`https://github.com/pascalbe-dev/ulauncher-repo-opener.git`

## Usage

TODO: EXPLAIN USAGE

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