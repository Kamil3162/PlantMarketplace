import uuid
from django.db import models
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.core.validators import ValidationError

class InventoryManager(models.Manager):
    """
        Custom manager for Inventory model providing inventory-specific operations.
    """

    def create_inventory(self, product, quantity=0, low_stock_threshold=5):
        """
        Creates a new inventory record with an associated creation event.

        Args:
            product: The product for this inventory
            quantity: Initial quantity (default: 0)
            low_stock_threshold: Threshold for low stock warnings (default: 5)

        Returns:
            The newly created Inventory instance
        """
        inventory = self.create(
            product=product,
            quantity=quantity,
            low_stock_threshold=low_stock_threshold
        )

        # Create the associated inventory event
        InventoryEvent.objects.create(
            inventory=inventory,
            user=product.user,  # Assuming product has a user association
            event=InventoryEvent.EVENT_CREATED
        )

        return inventory

    def block_reservations(self, inventory_id):
        """
        Blocks reservations on an inventory item if reserved quantity exceeds threshold.

        Args:
            inventory_id: UUID of the inventory to check

        Returns:
            The created InventoryEvent if reservations were blocked, None otherwise
        """
        inventory = self.get(id=inventory_id)

        # Prevent division by zero
        if inventory.reserved_quantity == 0:
            return None

        # Check if reserved quantity is more than 50% of available
        reservation_ratio = inventory.quantity / inventory.reserved_quantity

        if round(reservation_ratio, ndigits=0) > 0.5:
            inventory_event = InventoryEvent.objects.create(
                inventory=inventory,
                user=inventory.product.user,
                # Assuming product has a user association
                event=InventoryEvent.EVENT_BLOCKED_RESERVATIONS
            )
            return inventory_event

        return None


class Inventory(models.Model):
    """
    Represents product inventory with quantity tracking and reservation capabilities.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Inventory ID")
    )
    product = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Product"),
        null=False,
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Quantity")
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        verbose_name=_("Low Stock Threshold")
    )
    reserved_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reserved Quantity")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        null=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        null=True,
    )

    # Assign custom manager
    objects = InventoryManager()

    class Meta:
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventories")
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['product']),
        ]

    def __str__(self):
        """String representation of the inventory"""
        return f"Inventory: {self.product} - {self.quantity} units"

    def get_available_quantity(self):
        """Returns the quantity available for sale (not reserved)"""
        return self.quantity - self.reserved_quantity

    @property
    def available_quantity(self):
        """Property accessor for available quantity"""
        return self.get_available_quantity()

    @property
    def is_low_stock(self):
        """Returns True if the available quantity is below the threshold"""
        return self.available_quantity <= self.low_stock_threshold

    def clean(self):
        """Validate that reserved quantity doesn't exceed total quantity"""
        if self.reserved_quantity > self.quantity:
            raise ValidationError(
                _("Reserved quantity cannot exceed total quantity."))

    def save(self, *args, **kwargs):
        """Override save to ensure validation is always run"""
        self.clean()
        super().save(*args, **kwargs)

class ReservedInventoryManager(models.Manager):

    def create(
        self,
        user_uuid: uuid.uuid4,
        inventory: Inventory,
        quantity: int,
        reference: str = None,
        **kwargs
    ):
        reservations = self.filter_by_user(user=user_uuid)

        if reservations:
            raise ValidationError(
                "Reservations already exists"
            )

        inventory_free = inventory.get_available_quantity()
        inventory_threshold = not inventory.is_low_stock()

        if quantity in range(1, inventory_threshold) and inventory_threshold:
            reserve_inventory = self.model(
                inventory=inventory,
                quantity=quantity,
                user=user_uuid,
                reference=reference,
            )

            reserve_inventory.save()

            return reserve_inventory

    def update(self):
        pass

    def delete(self):pass

    def filter_by_user(self, user: uuid.uuid4):
        reservation = self.model.objects.filter(user__id=user)
        return reservation


class ReservedInventory(models.Model):
    """
    Tracks reserved inventory items that are not yet sold but temporarily unavailable.
    Used for items in shopping carts, pending orders, etc.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Reservation ID")
    )
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_("Inventory")
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Reserved Quantity")
    )
    user = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("User Id")
    )

    reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Reference"),
        help_text=_("Optional reference (order ID, cart ID, etc.)")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )

    class Meta:
        verbose_name = _("Reserved Inventory")
        verbose_name_plural = _("Reserved Inventories")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """String representation of the reservation"""
        return f"Reservation: {self.quantity} units of {self.inventory.product}"

    def clean(self):
        """Validate that the reservation is possible"""
        if self.pk is None:  # New reservation
            if self.quantity > self.inventory.available_quantity:
                raise ValidationError(
                    _("Cannot reserve more than available quantity."))
        else:  # Existing reservation being updated
            original = ReservedInventory.objects.get(pk=self.pk)
            additional = self.quantity - original.quantity
            if additional > 0 and additional > self.inventory.available_quantity:
                raise ValidationError(
                    _("Cannot reserve more than available quantity."))

    def save(self, *args, **kwargs):
        """Override save to ensure validation and update inventory reserved quantity"""
        original_quantity = 0
        is_new = self.pk is None

        if not is_new:
            # Get the original quantity for existing reservations
            original_quantity = ReservedInventory.objects.get(
                pk=self.pk).quantity

        # Validate
        self.clean()

        # Save the reservation
        super().save(*args, **kwargs)

        # Update the inventory's reserved quantity
        inventory = self.inventory
        if is_new:
            inventory.reserved_quantity += self.quantity
        else:
            inventory.reserved_quantity = inventory.reserved_quantity - original_quantity + self.quantity

        inventory.save(update_fields=['reserved_quantity', 'updated_at'])

        # Create an event record
        event_type = InventoryEvent.EVENT_RESERVED
        InventoryEvent.objects.create(
            inventory=inventory,
            quantity=self.quantity,
            event=event_type,
            user_id=inventory.product.user_id
            # Using user_id to avoid loading the user object
        )


class InventoryEvent(models.Model):
    """
    Tracks all events related to inventory movements for auditing purposes.
    """
    # Event type constants
    EVENT_CREATED = 'created'
    EVENT_UPLOADED = 'uploaded'
    EVENT_BLOCKED = 'blocked'
    EVENT_BLOCKED_RESERVATIONS = 'blocked_reservations'
    EVENT_RESERVED = 'reserved'
    EVENT_SUBTRACTED = 'subtracted'

    EVENT_CHOICES = (
        (EVENT_CREATED, _('Created')),
        (EVENT_UPLOADED, _('Uploaded')),
        (EVENT_BLOCKED, _('Blocked')),
        (EVENT_BLOCKED_RESERVATIONS, _('Blocked Reservations')),
        (EVENT_RESERVED, _('Reserved')),
        (EVENT_SUBTRACTED, _('Subtracted')),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Event ID")
    )
    inventory = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_("Inventory")
    )
    user = models.UUIDField(
        verbose_name=_("User")
    )
    event = models.CharField(
        max_length=25,
        choices=EVENT_CHOICES,
        default=EVENT_CREATED,
        verbose_name=_("Event Type")
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Quantity"),
        help_text=_("Quantity affected by this event")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )

    class Meta:
        verbose_name = _("Inventory Event")
        verbose_name_plural = _("Inventory Events")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory']),
            models.Index(fields=['event']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """String representation of the event"""
        return f"{self.get_event_display()} - {self.inventory.product} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

# # learning
# from django.db import models
#
# class Question(models.Model):
#     question = models.CharField(max_length=250, verbose_name=_("Question"))
#     product = models.ForeignKey(
#         Inventory,
#         on_delete=models.CASCADE,
#     )
#
#     published_at = models.DateTimeField(
#
#     )
#     objects = models.Manager()
#     objects.bulk_update()
#     def __str__(self):
#         pass
#
#     class Meta:
#         verbose_name = _("Question")
#         verbose_name_plural = _("Questions")
#
# question = Question("data")
# question.save()
#
# print(question.objects)
#
#
# from django.utils import timezone
# current_year = timezone.now()
#
# from django.contrib import admin
#
# admin.register(Question)
#
# from django.urls import include, path
#
# Question.object.filter
#
# urlpatterns = [
#     path('<int:question_id>/', detail, name="detail"),
# ]
# def detail(request, question_id):
#     return HttpResponse(f"<h1>{question_id}</h1>")
#
# # tworzac template w django dodajemy directory template
# # wewnatrz nazwe apki jezeli to jest globalna i w srokdu nazwa tempalte
#
# from django.template import loader
# from django.shortcuts import render
#
# def render_elements(request, question_id):
#     template = loader.get_template('pools/index.html')
#     context = {
#         'latest_question_list': [1, 2, 3]
#     }
#     return HttpResponse(template.render(context, request))
#
#
#
# # zamiana
#     return render(request=request, template_name='esa', context={})
#
#
# """
# {% if latest_question_list %}
#     <ul>
#     {% for question in latest_question_list %}
#         <li><a href="/polls/{{ question.id }}/">{{ question.question_text }}</a></li>
#     {% endfor %}
#     </ul>
# {% else %}
#     <p>No polls are available.</p>
# {% endif %}
# """
#
# from django.shortcuts import render, get_object_or_404
# from django.http import Http404
#
# from django.core.exceptions import PermissionDenied
#
# def response_error_handler(request, excpetion=None):
#     return HttpResponse("error", status=403)
#
# from django.views.decorators.http import require_POST, require_safe
#
# require_safe - tylko bierze get i head method jako cos co wyciagamy dane
#
# @require_POST
# def my_post(request):
#     pass
#
# # <a href="/pools"/{{question.id}}/> {{content}}
# # <a href={% url 'name' argument}> name
#
# # namepsace in urls patterms
# from django.urls import path, include
# app_name = "data"
# urlpatters = [
#     path, name='esa'
# ]
#
# # url data:esa
# # from action="{% 'data:esa' argument}" method="post">
# # {% csrf_token %} in form
#
# while True:
#     try:
#         value = int(input(" Enter a valid number"))
#     except ValueError:
#         print("esa")
#     else:
#         "esa"
#     finally:
#         "esa"
#
#
# def f():
#     exxc = [OSError("operating system error"), SystemError("operating system error")]
#     raise ExceptionGroup("group exception", exxc)
#
#
# def f():
#     try:
#         raise TypeError("type error")
#     except Exception as e:
#         e.add_note("Rnadom note")
#         e.add_note("Rnadom note")
#         raise
#
# excs = []
# for i in range(3):
#     try:
#         f()
#     except Exception as e:
#         e.add_note(f'Happened in Iteration {i+1}')
#         excs.append(e)
#
# raise ExceptionGroup('We have some problems', excs)
#
# i = 5
# def f(args=i):
#     print(args)
#
# i = 6
# f() # it will print a 5
# list(range(0, 32, 5))
# list(range(-10, -100, -30))
# # for loop with else will not execute else block when we make a break or return
# match value:
#     case (0,0):
#         print
#
#     case _:
#         raise ValueError("esa")
#
# class Point:
#     __match_args = ("x", "y")
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#
#     # musimy opdawac tak jak jest podane w match args x=1 y=1 jezeli nie to mzinnie nigy nie beda przypiosane
#     from enum import Enum
#     class Color(Enum):
#         N1 = "f1"
#         N2 = "esa"
#
#
#
# class LowerCaseTuple(tuple):
#     def __new__(cls, *args):
#         new_elements = (x.lower() for x in args)
#         return super().__new__(cls, new_elements)
#
# variable = 1
# print(variable.__class__)
# int