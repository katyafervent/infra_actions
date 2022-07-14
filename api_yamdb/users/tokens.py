from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class ConfirmationCodeTokenGenerator(PasswordResetTokenGenerator):
    """Custom token generator."""

    def _make_hash_value(self, user, timestamp: int) -> str:
        """Custom algorithm for making hashed token."""
        return (six.text_type(user.pk) + six.text_type(timestamp)
                + six.text_type(user.username) + six.text_type(user.email)
                )
