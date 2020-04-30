import logging
from datetime import datetime
from datetime import timezone
from email import message_from_bytes
from uuid import uuid4

from aiosmtpd.smtp import SMTP, MISSING
from aiosmtpd.handlers import AsyncMessage
from flanker import mime
from flanker.addresslib import address

from yades_smtp.utils import get_message_payload


class Handler(AsyncMessage):
    def __init__(self, db, config):
        self.db = db
        self.config = config
        super().__init__()

    async def handle_RCPT(
        self, server, session, envelope, address, rcpt_options
    ):
        mailbox = await self.db.mailboxes.find_one({'address': address})
        if not mailbox:
            return '550 Non-existent email address'
        emails_in_mailbox = len(mailbox.get('emails', []))
        emails_count_limit = mailbox.get(
            'emails_count_limit', self.config['emails_count_limit']
        )
        if emails_count_limit and emails_in_mailbox >= emails_count_limit:
            return '552 Exceeded storage allocation'
        return MISSING

    async def handle_DATA(self, server, session, envelope):
        message = mime.from_string(
            message_from_bytes(envelope.content).as_string()
        )
        timestamp = datetime.now(tz=timezone.utc)

        payload = await get_message_payload(message)
        parsed_from = address.parse(message.headers['From'])
        parsed_to_list = address.parse_list(message.headers['To'])

        for mail_to in parsed_to_list.addresses:
            if mail_to not in envelope.rcpt_tos:
                continue
            document = {
                'uuid': str(uuid4()),
                'from_name': parsed_from.display_name,
                'from_address': parsed_from.address,
                'to': mail_to,
                'subject': message.headers['Subject'],
                'payload': payload,
                'timestamp': timestamp.isoformat(timespec='seconds')
            }

            await self.db.emails.insert_one(document)
            await self.db.mailboxes.update_one(
                {'address': mail_to}, {
                    '$push': {
                        'emails': {
                            'uuid': document['uuid'],
                            'from_address': document['from_address'],
                            'from_name': document['from_name'],
                            'subject': document['subject'],
                            'timestamp': document['timestamp'],
                            'is_read': False,
                        }
                    }
                }
            )
        if self.config['collect_statistic']:
            self.db.income_counter.update_one(
                {'from_address': parsed_from.address},
                {'$inc': {'count': 1}},
                upsert=True,
            )
            self.db.email_counter.update_one(
                {},
                {'$inc': {'count': 1},
                 '$setOnInsert': {'since': timestamp.date().isoformat()}},
                upsert=True
            )
        return '250 OK'


class Controller:
    def __init__(self, db, config, loop):
        self.db = db
        self.config = config
        self.loop = loop

    def factory(self):
        return SMTP(Handler(self.db, self.config), enable_SMTPUTF8=True)

    def run(self):
        host = self.config['smtp_host']
        port = self.config['smtp_port']
        logging.info(f'Starting server at {host}:{port}')
        server = self.loop.create_server(self.factory, host=host, port=port)
        return server
