from dataclasses import dataclass

@dataclass
class UserScheme:
    """
        Represents core user data for token generation.
        This class validates and structures user information.
    """
    id: int  # Using int since Django's default ID is AutoField
    first_name: str
    last_name: str
    email: str
    is_staff: bool = False
    is_confirmed: bool = False

    @classmethod
    def by_django_user(cls, user):
        """
            Generate a user scheme using django user model.
        """
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_staff=user.is_staff,
            is_confirmed=user.is_confirmed,
        ).to_dict()

    def to_dict(self) -> dict:
        """
           Converts UserData to a dictionary for JWT payload.
           Ensures consistent data structure in tokens.
       """
        return {
            'user_id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_staff': self.is_staff,
            'is_confirmed': self.is_confirmed
        }