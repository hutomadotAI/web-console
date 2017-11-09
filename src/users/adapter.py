import logging

from django.core.mail import EmailMessage
from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter

logger = logging.getLogger(__name__)


class SendgridTemplatesAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        """
        Send emails using Sendgrid Templates, provide data for the template.

        More: https://anymail.readthedocs.io/en/stable/esps/sendgrid/#batch-sending-merge-and-esp-templates
        """

        logger.debug([email, template_prefix, context])

        # Remove non-serviceable objects from the way
        context.pop('current_site', None)
        context.pop('request', None)
        user = context.pop('user')

        # We build the message
        message = EmailMessage(
            to=['%s %s <%s>' % (user.first_name, user.last_name, email)]
        )

        # Enrich context with useful data
        context['first_name'] = user.first_name
        context['last_name'] = user.last_name
        context['username'] = user.username

        # Get a Sendgrid template ID
        message.template_id = settings.SENDGRID_TEMPLATES.get(
            template_prefix,
            settings.SENDGRID_DEFAULT_TEMPLATE
        )

        # Add context
        message.merge_global_data = context

        # send API call to Sendgrid
        message.send()
