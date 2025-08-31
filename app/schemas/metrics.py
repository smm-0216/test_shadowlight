from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class MetricsParams(BaseModel):
    start: date = Field(..., description="Start date in format YYYY-MM-DD")
    end: date = Field(..., description="End date in format YYYY-MM-DD")
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(50, ge=1, le=1000, description="Rows per page")

    @model_validator(mode="after")
    def validate_order(self) -> "MetricsParams":
        if self.start > self.end:
            raise ValueError("end date must be greater than or equal to start date")
        return self

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def render_base_query(self) -> str:
        return


class MetricsResponse(BaseModel):
    count: int = Field(..., description="Number of rows in this page")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size used")
    total: int = Field(..., description="Total number of rows in the full query")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")
    data: List[Dict[str, Any]] = Field(..., description="List of row records")
    message: Optional[str] = Field(None, description="Optional message when no data is found")
