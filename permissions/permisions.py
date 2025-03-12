# permissions.py

from enum import Enum


class BasePermissionEnum(str, Enum):
    """Base class for permission enums"""

    @property
    def codename(self):
        return self.value.split('.')[1]


class AccountPermissions(BasePermissionEnum):
    MANAGE_USERS = "account.manage_users"
    MANAGE_STAFF = "account.manage_staff"
    IMPERSONATE_USER = "account.impersonate_user"


class AppPermission(BasePermissionEnum):
    MANAGE_APPS = "app.manage_apps"
    MANAGE_WEBHOOKS = "app.manage_webhooks"


class BargainPermission(BasePermissionEnum):
    MANAGE_BARGAINS = "bargain.manage_bargains"
    MANAGE_SALES = "discount.manage_sales"
    MANAGE_VOUCHERS = "discount.manage_vouchers"


class ShippingPermission(BasePermissionEnum):
    MANAGE_SHIPPING = "shipping.manage_shipping"


class ProductPermission(BasePermissionEnum):
    MANAGE_PRODUCTS = "product.manage_products"
    MANAGE_CATEGORIES = "product.manage_categories"


class OrderPermission(BasePermissionEnum):
    MANAGE_ORDERS = "order.manage_orders"
    MANAGE_REFUNDS = "order.manage_refunds"
    MANAGE_CHECKOUTS = "order.manage_checkouts"
    MANAGE_CANCELATIONS = "order.manage_cancels"


class ChatPermission(BasePermissionEnum):
    MANAGE_CHATS = "chat.manage_chats"
    MANAGE_BLOCK = "chat.manage_block"
    MANAGE_UNLOCK = "chat.manage_unlock"


class CommentPermission(BasePermissionEnum):
    MANAGE_COMMENTS = "comments.manage_comments"


# All permission enums
PERMISSIONS = [
    AccountPermissions,
    AppPermission,
    ShippingPermission,
    ProductPermission,
    OrderPermission,
    BargainPermission,
    ChatPermission,
    CommentPermission,
]

# Flat list of all permission enum values
PERMISSIONS_ENUMS = [
    permission
    for permission_group in PERMISSIONS
    for permission in permission_group
]

# Map of codenames to full permissions
PERMISSIONS_CODENAME_MAP = {
    permission.codename: permission
    for permission in PERMISSIONS_ENUMS
}

# Map of full permission values to enums
PERMISSIONS_ENUM_DICT = {
    permission.value: permission
    for permission in PERMISSIONS_ENUMS
}