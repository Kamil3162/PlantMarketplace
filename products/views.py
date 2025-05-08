from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import utils as django_db_exceptions

from products.models import Product
from .forms import CreateProductForm

def product_create(request):
    submitted = False
    if request.method == "POST":
        submitted = True
        create_product = CreateProductForm(request.POST)
        print(Product._meta)
        if create_product.is_valid():
            product = create_product.save()
            product_dict = model_to_dict(product)

            return render(request, 'create_product.html', {
                'test_data': product_dict,
                'submitted': submitted,
            })

    if request.method == "GET":
        create_product_from = CreateProductForm()

        return render(request, 'create_product.html', {
            'create_product_form': create_product_from,
            'submitted': submitted
        })


def product_list(request):
    products = Product.objects.all()
    paginator = Paginator(products, 4)

    try:
        page_number = request.GET.get('page', 1)
        page_objects = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        # Handle invalid page numbers by defaulting to first page
        page_objects = paginator.page(1)

    page_information = {
        'previous_page': page_objects.previous_page_number() if page_objects.has_previous() else None,
        'next_page': page_objects.next_page_number() if page_objects.has_next() else None,
        'current_page': page_objects.number,
        'total_pages': paginator.num_pages,
        'object_list': page_objects.object_list,
    }

    return render(
        request,
        'product_list.html',
        page_information)

def product_detail(request, product_uuid):
    # we have to get particular product details
    product = get_object_or_404(Product, pk=product_uuid)
    return render(request, 'product_detail.html', {
        'product': product,
    })


# def delete_product(request, product_uuid):
    # try:
    #
    #     product = get_object_or_404(Product, pk=product_uuid)
    #     product.delete()
    #     return JsonResponse(
    #         data={
    #             'status': 'success',
    #             'message': 'Product deleted'
    #         }
    #     )

