from fastapi import APIRouter, Depends

from app.market_client import get_market_client
from app.models import ProductStatus, ProductValidationRequest
from app.protocols import MarketClientProtocol
from app.services import get_product_status

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.post("/validate", response_model=ProductStatus)
async def validate_product(
    request: ProductValidationRequest,
    market_client: MarketClientProtocol = Depends(get_market_client),
) -> ProductStatus:
    return await get_product_status(request.product, request.country, market_client)
