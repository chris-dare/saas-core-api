from .crud_otp import otp
from .crud_user import user
from .crud_organization import organization
from .crud_organization_member import organization_member
from .crud_event import event
from .crud_bill import bill
from .crud_transaction import transaction
from .crud_subaccount import subaccount
# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
