from .crud_otp import otp
from .crud_user import user
from .crud_organization import organization
from .crud_organization_member import organization_member

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
