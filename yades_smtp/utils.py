
async def get_message_payload(message):
    payload = {}

    for part in message.walk(with_self=True):
        content_type = str(part.content_type)
        if content_type not in ('text/plain', 'text/html'):
            continue
        payload.update({
            content_type: part.body
        })

    return payload
