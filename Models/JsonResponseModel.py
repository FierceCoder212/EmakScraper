from typing import Optional, Any

from pydantic import BaseModel

from Models.HierarchyItemModel import HierarchyItemModel
from Models.ProductDocumentModel import ProductDocumentModel


class JsonResponseModel(BaseModel):
    Hierarchy: list[HierarchyItemModel]
    ProductDocuments: Optional[list[ProductDocumentModel]]
    HomePage: Any
