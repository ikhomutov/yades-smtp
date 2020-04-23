import asyncio
import logging
import os
from distutils.util import strtobool

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

from yades_smtp.controller import Controller


def main():
    load_dotenv()
    config = {
        'mongodb_uri': os.getenv('MONGODB_URI'),
        'mongodb_name': os.getenv('MONGODB_NAME'),
        'host': os.getenv('SMTP_HOST', 'localhost'),
        'port': os.getenv('SMTP_PORT', '8080'),
        'collect_statistic': strtobool(
            os.getenv('COLLECT_STATISTIC')
        ),
        'log_level': os.getenv('LOG_LEVEL'),
    }
    logging.basicConfig(level=config['log_level'])
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
