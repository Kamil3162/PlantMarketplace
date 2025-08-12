# validators/email_validator.py
import re
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from exceptions import PageNumberException

class ProfessionalEmailValidator(EmailValidator):
    """
    Professional email validator with advanced features
    """

    # Disposable email domains to block
    DISPOSABLE_DOMAINS = {
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'throwaway.email', 'temp-mail.org',
        'yopmail.com', 'maildrop.cc', 'sharklasers.com'
    }

    # Common corporate domains (optional whitelist)
    CORPORATE_DOMAINS = {
        'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com',
        'company.com'  # Add your company domains
    }

    def __init__(self,
                 check_mx=True,
                 block_disposable=True,
                 require_corporate=False,
                 custom_domains=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.check_mx = check_mx
        self.block_disposable = block_disposable
        self.require_corporate = require_corporate
        self.custom_domains = custom_domains or set()

    def __call__(self, value):
        # First run Django's built-in email validation
        super().__call__(value)

        if not value or '@' not in value:
            return

        local_part, domain = value.rsplit('@', 1)
        domain = domain.lower()

        # Check disposable emails
        if self.block_disposable and domain in self.DISPOSABLE_DOMAINS:
            raise ValidationError(
                _('Disposable email addresses are not allowed.'),
                code='disposable_email'
            )

        # Check corporate domain requirement
        if self.require_corporate:
            allowed_domains = self.CORPORATE_DOMAINS | self.custom_domains
            if domain not in allowed_domains:
                raise ValidationError(
                    _('Please use a corporate email address.'),
                    code='non_corporate_email'
                )

        # Check MX record
        if self.check_mx:
            self._validate_mx_record(domain)

        # Additional local part validation
        self._validate_local_part(local_part)

    def _validate_mx_record(self, domain):
        """Check if domain has valid MX record"""
        try:
            dns.resolver.resolve(domain, 'MX')
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
            raise ValidationError(
                _('Email domain does not exist or cannot receive emails.'),
                code='invalid_domain'
            )

    def _validate_local_part(self, local_part):
        """Additional validation for local part of email"""
        if len(local_part) > 64:
            raise ValidationError(
                _('Email local part is too long (max 64 characters).'),
                code='local_part_too_long'
            )

        # Check for consecutive dots
        if '..' in local_part:
            raise ValidationError(
                _('Email cannot contain consecutive dots.'),
                code='consecutive_dots'
            )

        # Check for leading/trailing dots
        if local_part.startswith('.') or local_part.endswith('.'):
            raise ValidationError(
                _('Email cannot start or end with a dot.'),
                code='invalid_dot_position'
            )


class StrictEmailValidator(ProfessionalEmailValidator):
    """
    Very strict email validator for high-security applications
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('check_mx', True)
        kwargs.setdefault('block_disposable', True)
        super().__init__(**kwargs)

    def __call__(self, value):
        super().__call__(value)

        if not value:
            return

        # Additional strict checks
        local_part, domain = value.rsplit('@', 1)

        # No special characters in local part (very strict)
        if not re.match(r'^[a-zA-Z0-9._-]+$', local_part):
            raise ValidationError(
                _('Email can only contain letters, numbers, dots, hyphens, and underscores.'),
                code='invalid_characters'
            )

        # Domain must have at least one dot
        if '.' not in domain:
            raise ValidationError(
                _('Email domain must contain at least one dot.'),
                code='invalid_domain_format'
            )


class BusinessEmailValidator(ProfessionalEmailValidator):
    """
    Business-focused email validator
    """

    BUSINESS_DOMAINS = {
        'company.com', 'organization.org', 'business.net'
        # Add your business domains
    }

    def __init__(self, **kwargs):
        kwargs.setdefault('require_corporate', True)
        kwargs.setdefault('custom_domains', self.BUSINESS_DOMAINS)
        super().__init__(**kwargs)


def validate_page_number(page_number: int) -> bool:
    try:
        number = int(page_number)
        if number < 0:
            raise PageNumberException("Page number cannot be negative number")

        return number
    except (ValueError, TypeError) as e:
        raise PageNumberException(f"Page Validation: {str(e)}")


