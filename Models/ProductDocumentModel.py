from typing import Any, Optional

from pydantic import BaseModel


class ProductDocumentModel(BaseModel):
    Id: int
    Description: str
    DisplayPoBar: bool
    LayoutId: int
    LayoutDisplayMode: int
    LanguageId: int
    DocumentTypeId: int
    DocumentTypeDesc: str
    FileName: str
    FileNameForIpl: str
    FileExtension: str
    FileIsVector: bool
    FileHotSpot: str
    FileHotSpot5Mp: str
    FileNameFullPath: Optional[str]
    Url: str
    NavId: int
    NavParentId: int
    AvailableLanguages: Any
    FromTp: bool
    Children: Any
    UserNotes: str
    HtmlContent: str
