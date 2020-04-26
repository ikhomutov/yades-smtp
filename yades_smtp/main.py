import argparse
import asyncio
import logging

from environs import Env
from motor.motor_asyncio import AsyncIOMotorClient

from yades_smtp.controller import Controller


def _parse_args():
    """Parse the CLI arguments for use by yades-smtp."""
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        '--host', type=str, default='localhost',
        help='Host to listen on (defaults to localhost)'
    )
    parser.add_argument(
        '--port', type=int, default=25,
        help='Port to listen on (defaults to 25)'
    )
    parser.add_argument(
        '--db-uri', type=str, default='mongodb://localhost:27017',
        help='Uri of mongodb server'
    )
    parser.add_argument(
        '--db-name', type=str, default='yades',
        help='Name of mongodb database'
    )
    parser.add_argument(
        '--collect-statistic', action='store_true',
        help='Save statistic about receiving emails'
    )
    parser.add_argument(
        '--emails-count-limit', type=int, default=0,
        help='Limit the number of emails for separate mailbox'
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    env = Env()
    env.read_env()
    with env.prefixed('YADES_'):
        config = {
            'mongodb_uri': env.str('MONGODB_URI', args.db_uri),
            'mongodb_name': env.str('MONGODB_NAME', args.db_name),
            'smtp_host': env('SMTP_HOST', args.host),
            'smtp_port': env.int('SMTP_PORT', args.port),
            'collect_statistic': env.bool(
                'COLLECT_STATISTIC', args.collect_statistic
            ),
            'emails_count_limit': env.int(
                'EMAILS_COUNT_LIMIT', args.emails_count_limit
            ),
        }
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()

    db = AsyncIOMotorClient(
        config['mongodb_uri'],
        io_loop=loop
    )[config['mongodb_name']]

    controller = Controller(db, config, loop)
    server = loop.run_until_complete(controller.run())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info('Stopping server')
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.stop()


if __name__ == '__main__':
    main()
