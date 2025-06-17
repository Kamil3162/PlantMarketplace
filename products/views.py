from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import utils as django_db_exceptions
from django.db.models import ProtectedError

from models import Product
from redis_microservices import redis_product_client
from forms import CreateProductForm
from aws.aws_s3 import S3Instance

def product_create(request):
    submitted = False
    if request.method == "POST":
        try:
            submitted = True
            create_product = CreateProductForm(request.POST)

            if create_product.is_valid():
                file = request.FILES
                single_file = file['image']

                product = create_product.save(commit=False)

                generated_file_name = S3Instance.generate_file_name(original_name=single_file)
                product.image = generated_file_name

                product.save()

                s3_key = S3Instance.upload_image(single_file, s3_key=generated_file_name)

                product_dict = model_to_dict(product)

                product_uuid = product.id
                prepared_product_data = redis_product_client()._prepare_product_for_redis(product_dict)

                prepared_product_data['key'] = product_uuid
                added_product = redis_product_client().add_product(**prepared_product_data)

                return render(request, 'create_product.html', {
                    'test_data': product_dict,
                    'submitted': submitted,
                })
            else:
                return JsonResponse(
                    data={
                        'status': 'error',
                        'detail': create_product.errors
                    }
                )

        except Exception as e:
            print(type(e))
            raise Exception(str(e))


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
        page_information
    )

def product_detail(request, product_uuid):
    # TODO mircoservices to update for example 1000 rows in one time
    # TODO inventory services

    product_uuids = [
        "621e73fe-07cd-432e-812d-09460944934d",
        "561430f7-d502-492f-9017-984be0dde583"
    ]
    product_queryset = Product.objects.filter(id__in=product_uuids)

    # first we have to tyr to get this product from our redis db next if it doesnt exist we make a quesy inside postgresql database
    cache_product = redis_product_client().get_product(product_uuid)
    image_url = S3Instance.get_presigned_url(cache_product['image'])
    print(image_url)
    # get and display image using s3 buckets

    # redis_product_client().insert_db_products()
    if not cache_product:
        # return JsonResponse(data={
        #     'product': cache_product,
        #     'image_url': image_url
        # })
        cache_product = get_object_or_404(Product, pk=product_uuid)

    return render(request, 'product_detail.html', {
        'product': cache_product,
        'image_url': image_url
    })


def product_modify():
    pass


def delete_product(request, product_uuid):
    try:
        product = get_object_or_404(Product, pk=product_uuid)
        product.delete()
        return JsonResponse(
            data={
                'status': 'success',
                'message': 'Product deleted'
            }
        )
    except ValueError:
        return JsonResponse(
            data={
                'status': 'error',
                'message': 'Invalid UUID number'
            }
        )
    except Product.DoesNotExist:
        return JsonResponse(
            data={
                'status': 'error',
                'message': f'Product:{product_uuid} does not exist'
            }
        )
    except ProtectedError:
        return JsonResponse(
            data={
                'status': 'error',
                'message': 'Delete object is not aviaible'
            }
        )



