

def email_service_create():
    from producer import EmailProducer
    return EmailProducer()

__all__ = ['email_service_create']