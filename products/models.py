import enum

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from account.models import CustomUser
from plant_marketplace import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.
import uuid
class Product(models.Model):
    SUNLIGHT_CHOICES = [
        ('full', 'Full Sun'),
        ('partial', 'Partial Sun'),
        ('shade', 'Shade')
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]

    WATER_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Plant Care Details
    sunlight = models.CharField(max_length=20, choices=SUNLIGHT_CHOICES, default='partial')
    water_needs = models.CharField(max_length=20, choices=WATER_CHOICES, default='medium')
    care_difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='easy'
    )

    # Physical Characteristics
    height = models.DecimalField(max_digits=5, decimal_places=2,
                                 help_text="Height in cm")
    spread = models.DecimalField(max_digits=5, decimal_places=2,
                                 help_text="Spread in cm")
    bloom_time = models.CharField(max_length=50, blank=True)
    flower_color = models.CharField(max_length=50)

    # Stock and Status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Optional Image field (requires Pillow package)
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Flower'
        verbose_name_plural = 'Flowers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('flower-detail', args=[str(self.id)])

    def modify_object(self, **kwargs):
        """
            Update instance fields using provided fields
        Args:
            **kwargs:
        Returns:
            self: Updated product instance

        Raises:
            KeyError: If any field doesn't exist on the model
        """
        model_fields = [self._meta.get_fields()]
        for field, value in kwargs.items():
            if field not in model_fields:
                raise KeyError(f'Model does not have field {field}')
            setattr(self, field, value)
        self.save()
        return self


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
    product = models.ForeignKey(
        'Product',  # Using string to avoid circular imports
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name=_("Product")
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
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
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
    reference = models.CharField(
        max_length=255,
        blank=True,
        null=True,
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
        Inventory,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_("Inventory")
    )
    user = models.ForeignKey(
        'CustomUser',  # Using string to avoid circular imports
        on_delete=models.CASCADE,
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
        null=True,
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