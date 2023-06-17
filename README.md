# Note Taker

[![GitHub license](https://img.shields.io/github/license/realprogrammersusevim/note-taker.svg?style=flat-square)](https://github.com/realprogrammersusevim/note-taker/blob/master/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-green.svg?style=flat-square)](http://makeapullrequest.com)

Information disappears over time. Note taker is a Python script that finds your
Nostr notes on relays and saves them locally into a file so you can keep them
forever even if relays delete them.

## Installation

Clone the repository onto your device.

```bash
git clone https://github.com/realprogrammersusevim/note-taker
cd note-taker
pip install -r requirements.txt
```

## Usage

Almost all the options are specified in the configuration file. Copy the example
configuration file to a new location and edit the values.

```bash
cp config.json.example config.json
```

Once you have your configuration written out you can run the script.

```bash
./main.py -c config.json
```

The other CLI options can be seen by running `./main.py --help`.
