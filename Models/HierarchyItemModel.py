from typing import Any

from pydantic import BaseModel


class HierarchyItemModel(BaseModel):
    Id: int
    ParentId: int
    SortPosition: int
    ProductId: int
    ProductCatalogOrderingCodes: Any
    ProductModel: str
    ProductSerialNumber: str
    DocumentId: int
    Description: str
    ImageFileName: str
    IsEmptyFolder: bool
    IsSelected: bool
    IsChildOfSelectedNode: bool
    IsFeaturedProducts: bool
    UserNotes: Any
    EnbOrders: bool
    EnbWarranty: bool
    EnbProdReg: bool
    Promotions: Any
    NewProducts: Any
    CompanyNews: Any
    HasTpRestrictions: bool
    FromTp: bool
