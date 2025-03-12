
def generate_permission_name(permission_enum):
    permission_name = permission_enum.name
    permission_name.replace('_', ' ')
    permission_name.title()

    return permission_name

def get_permission_codenames(role_permissions, key):
    # we will use admin key because this user have all access to each feature of our application
    admin_codenames = role_permissions[key]
    return [
        x.codename for x in admin_codenames
    ]

