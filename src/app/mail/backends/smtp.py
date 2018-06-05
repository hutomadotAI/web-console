from django.conf import settings
from django.core.mail.backends import smtp

from hashlib import blake2b

from logging import getLogger

logger = getLogger(__name__)


class EmailBackend(smtp.EmailBackend):

    def send_messages(self, email_messages):
        """Logs all the email being sent hashing recipients email addresses"""

        try:
            for msg in email_messages:
                logger.info('Sending message "{subject}" to recipients: {to}'.format(
                    subject=msg.subject,
                    to=[blake2b(
                        email.encode('utf-8'),
                        digest_size=4,
                        key=settings.SECRET_KEY
                    ).hexdigest() for email in msg.to]
                ))
        except Exception as error:
            logger.exception('Problem logging recipients, ignoring: {error}'.format(error=error))

        return super(EmailBackend, self).send_messages(email_messages)
