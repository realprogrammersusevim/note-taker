# Note Taker

Information disappears over time. Note taker is a Python script to allow you to
save your Nostr notes into a file so you can keep them forever even if relays
delete them. This is the poor man's alternative to running your own relay.

## How to use

The bot automatically keeps track of when it last ran and will only fetch notes
since then. This makes it perfect for running as a cron job on your device.

To run the bot, run

```bash
pip install -r requirements.txt
cp config.json.example config.json
```

and fill in the configuration values.
