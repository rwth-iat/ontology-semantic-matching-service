from pydantic import BaseModel
from typing import List


class UploadQuery(BaseModel):
    """
    The necessary query parameters for uploading ontologies into
    the matching service.
    """
    ontologies: List[str]
