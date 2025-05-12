

class ProductDataSerivce:
    def __init__(self):
        # here we will craete a conncaetion to broker
        # next add celery for handle entire queue
        self.connection = None


# fist part we will get a list of all ids
# for example Product.objects.filter(id__in=
