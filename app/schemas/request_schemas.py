from pydantic import BaseModel, ConfigDict, Field


class PortfolioCreateSchema(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')

    name: str = Field(..., min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=500)

class AccessGrantSchema(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')

    username: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(Viewer|Manager)$")

class TradeSchema(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')

    ticker: str = Field(..., min_length=1)
    portfolio_id: int = Field(..., gt=0)
    quantity: int | float = Field(..., gt=0)
