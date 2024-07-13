from pydantic import BaseModel


class CatalogModel(BaseModel):
    modelId: int
    name: str
