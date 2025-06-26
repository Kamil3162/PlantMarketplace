from PlantMarketplace.permissions.core.permisions import (
    AccountPermissions,
    AppPermission,
    BargainPermission,
    ShippingPermission,
    ProductPermission,
    OrderPermission,
    ChatPermission,
    CommentPermission,
)

# Define role-based permission sets
ROLE_PERMISSIONS = {
    "ADMIN": [
        # Admin has all permissions
        AccountPermissions.MANAGE_USERS,
        AccountPermissions.MANAGE_STAFF,
        AccountPermissions.IMPERSONATE_USER,
        AppPermission.MANAGE_APPS,
        AppPermission.MANAGE_WEBHOOKS,
        BargainPermission.MANAGE_BARGAINS,
        BargainPermission.MANAGE_SALES,
        BargainPermission.MANAGE_VOUCHERS,
        ShippingPermission.MANAGE_SHIPPING,
        ProductPermission.MANAGE_PRODUCTS,
        ProductPermission.MANAGE_CATEGORIES,
        OrderPermission.MANAGE_ORDERS,
        OrderPermission.MANAGE_REFUNDS,
        OrderPermission.MANAGE_CHECKOUTS,
        OrderPermission.MANAGE_CANCELATIONS,
        ChatPermission.MANAGE_CHATS,
        ChatPermission.MANAGE_BLOCK,
        ChatPermission.MANAGE_UNLOCK,
        CommentPermission.MANAGE_COMMENTS,
    ],

    "MANAGER": [
        # Managers can manage most things except for staff and webhooks
        AccountPermissions.MANAGE_USERS,
        AccountPermissions.IMPERSONATE_USER,
        BargainPermission.MANAGE_BARGAINS,
        BargainPermission.MANAGE_SALES,
        BargainPermission.MANAGE_VOUCHERS,
        ShippingPermission.MANAGE_SHIPPING,
        ProductPermission.MANAGE_PRODUCTS,
        ProductPermission.MANAGE_CATEGORIES,
        OrderPermission.MANAGE_ORDERS,
        OrderPermission.MANAGE_REFUNDS,
        OrderPermission.MANAGE_CHECKOUTS,
        OrderPermission.MANAGE_CANCELATIONS,
        ChatPermission.MANAGE_CHATS,
        ChatPermission.MANAGE_BLOCK,
        CommentPermission.MANAGE_COMMENTS,
    ],

    "CUSTOMER_SERVICE": [
        # Customer service handles orders and customer interactions
        AccountPermissions.MANAGE_USERS,
        AccountPermissions.IMPERSONATE_USER,
        OrderPermission.MANAGE_ORDERS,
        OrderPermission.MANAGE_REFUNDS,
        OrderPermission.MANAGE_CHECKOUTS,
        OrderPermission.MANAGE_CANCELATIONS,
        ChatPermission.MANAGE_CHATS,
        CommentPermission.MANAGE_COMMENTS,
    ],

    "CONTENT_EDITOR": [
        # Content editors manage products and content
        ProductPermission.MANAGE_PRODUCTS,
        ProductPermission.MANAGE_CATEGORIES,
        BargainPermission.MANAGE_BARGAINS,
        BargainPermission.MANAGE_SALES,
        CommentPermission.MANAGE_COMMENTS,
    ],

    "CUSTOMER": [
        # Regular customers don't have admin permissions
        # in this case allow to visit urls and buy
    ],

    "ANONYMOUS": [
        # Anonymous users don't have admin permissions
        # in this case we allow to visit but all order and payment options
        # are denied
    ],
}
