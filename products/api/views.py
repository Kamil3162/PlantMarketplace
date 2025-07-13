import os
from pathlib import Path

from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import ProtectedError
import dotenv

from data.models import Product, ProductImage, ProductEvent
from redis_microservices import client
from forms.product_forms import CreateProductForm
from aws import S3Client

dotenv.load_dotenv()

log_path = Path(os.getcwd()).parent

S3Instance = S3Client(
    access_key=os.environ.get("AWS_ACCESS"),
    secret_key=os.environ.get("AWS_SECRET"),
    region=os.environ.get("AWS_REGION"),
    bucket_name=os.environ.get("AWS_BUCKET_NAME"),
    logs_path=str(log_path)
)

bucket_name = os.environ.get("AWS_BUCKET_NAME")

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

                generated_file_name = S3Instance.generate_file_name(
                    original_name=single_file.name
                )

                product.image = generated_file_name
                product.save()

                product_image = ProductImage.objects.create(
                    product=product,
                    file_name=generated_file_name,
                )

                s3_key = S3Instance.upload_image(
                    single_file,
                    file_name=generated_file_name
                )

                # dla testow wezmiemy generated file
                product_event = ProductEvent.objects.create(
                    product=product,
                    created_by=generated_file_name.split(".")[0]
                )

                product_dict = model_to_dict(product)
                product_uuid = product.id
                prepared_product_data = client()._prepare_product_for_redis(product_dict)

                prepared_product_data['key'] = product_uuid
                added_product = client().add_product(
                    **prepared_product_data
                )

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
    cache_product = client().get_product(product_uuid)
    image_url = S3Instance.get_presigned_url(cache_product['image'])

    if not cache_product:

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



