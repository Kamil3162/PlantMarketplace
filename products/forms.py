from django import forms
from products.models import Product


class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class BaseForm(forms.ModelForm):

    class Meta:
        """
            In this class we have a real impact on fields also labels of elemen
            ents during render on our website.
        """

class CreateBaseProduct(forms.Form):
    id = forms.UUIDField()
    name = forms.CharField()
