from pydantic import BaseModel


class FormattedDocumentModel(BaseModel):
    Catalog: str
    ImageName: str
    ProductName: str
    Section: str
    ItemNumber: str
    PartNumber: str
    Description: str
