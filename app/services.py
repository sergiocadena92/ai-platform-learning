from app.models import Product, ProductStatus, ReadinessStatus
from app.protocols import MarketClientProtocol


async def get_product_status(
    product: Product, country: str, market_client: MarketClientProtocol
) -> ProductStatus:
    market = await market_client.get_market_status(country)
    return ProductStatus(
        sku=product.sku,
        status=(
            ReadinessStatus.READY
            if product.is_ready_for(country) and market.enabled
            else ReadinessStatus.NOT_READY
        ),
    )
