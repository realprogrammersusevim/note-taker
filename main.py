#!python3

import argparse
import json
import logging
import math
import time

from nostr.event import EncryptedDirectMessage, Event, EventKind
from nostr.filter import Filter, Filters
from nostr.key import PrivateKey
from nostr.message_type import ClientMessageType
from nostr.relay_manager import RelayManager

parser = argparse.ArgumentParser(description="Note Taker")
parser.add_argument("-c", "--config", help="Path to config file")
parser.add_argument(
    "-m",
    "--metadata",
    action="store_true",
    help="Publish Nostr metadata event about the bot",
)
parser.add_argument("-q", "--quiet", action="store_true", help="Don't DM the user")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
args = parser.parse_args()

config = json.load(open(args.config))

if args.verbose:
    level = logging.DEBUG
else:
    level = logging.INFO

logging.basicConfig(
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=level,
    filename=config["logging"],
    filemode="a",
)

logging.info("Starting")

logging.debug(f"Config: {config}")

relay_manager = RelayManager()

for relay in config["relays"]:
    relay_manager.add_relay(relay)

private_key = PrivateKey().from_nsec(config["private_key"])

if args.metadata:
    # Send an event to update the bot's metadata to whatever is set in the config file
    metadata = json.dumps(config["metadata"])

    logging.debug(f"Metadata: {metadata}")
    metadata_event = Event(metadata, kind=EventKind.SET_METADATA)
    private_key.sign_event(metadata_event)

    logging.debug(f"Metadata event: {metadata_event.to_message()}")
    relay_manager.open_connections()
    time.sleep(2)
    relay_manager.publish_event(metadata_event)
    logging.info("Metadata published")
else:
    # Send a DM update to whoever is running the bot
    if not args.quiet:
        start_dm = EncryptedDirectMessage(
            recipient_pubkey=config["public_key"], cleartext_content="Taking notes"
        )
        private_key.sign_event(start_dm)
        relay_manager.publish_event(start_dm)

    # Request all the notes from the pubkey we're taking notes on since we last ran the
    # bot to make sure we only get new notes
    filter = Filters([Filter(authors=[config["public_key"]], since=config["last_run"])])
    sub_id = "ilovenostr"
    request = [ClientMessageType.REQUEST, sub_id]
    request.extend(filter.to_json_array())

    relay_manager.add_subscription(sub_id, filter)
    relay_manager.open_connections()
    time.sleep(1)
    logging.info("Connections open")

    # Send a message to the relays requesting the notes
    message = json.dumps(request)
    relay_manager.publish_message(message)
    time.sleep(1)
    logging.info("Message published")

    event_list = []

    # Store the received events in a list
    while relay_manager.message_pool.has_events():
        event_msg = relay_manager.message_pool.get_event()
        current_event = event_msg.event

        if current_event.verify():
            event_list.append(event_msg.event)

    logging.info("Events received")

    # Remove the duplicates
    deduped_events = []

    for event in event_list:
        if event not in deduped_events:
            deduped_events.append(event)

    deduped_events.sort(key=lambda x: x.created_at)

    stringified = [event.to_message() for event in deduped_events]

    logging.debug(f"New events: {stringified}")
    logging.info("Events deduped, writing to file")

    # Now save those new events to a file
    with open(config["output"], "a") as f:
        f.write("\n".join(stringified))

    # Update the last run for the next time the bot runs
    last_run = math.floor(time.time())
    logging.debug(f"New last run: {last_run}")
    new_config = config
    new_config["last_run"] = last_run
    with open(args.config, "w") as f:
        json.dump(new_config, f, indent=2)

    # Tell the user we're all done
    if not args.quiet:
        end_dm = EncryptedDirectMessage(
            recipient_pubkey=config["public_key"],
            cleartext_content=f"Finished taking {len(stringified)} new notes",
        )
        private_key.sign_event(end_dm)
        relay_manager.publish_event(end_dm)

# Shut everything down
logging.info("Closing connections")
relay_manager.close_connections()
logging.info("Connections closed")

logging.info("Done")
