import asyncio

import httpx
import pytest
from pydantic import ValidationError

from app.exceptions import MarketNotFound, MarketServiceUnavailable
from app.main import app
from app.models import Product


def test_lifespan_manages_http_client():
    async def verify_lifespan():
        async with app.router.lifespan_context(app):
            http_client = app.state.http_client
            assert isinstance(http_client, httpx.AsyncClient)
            assert not http_client.is_closed

        assert http_client.is_closed

    asyncio.run(verify_lifespan())


@pytest.fixture
def product_payload_factory():
    def build_payload(
        *,
        sku="PIXEL-10",
        price=799,
        stock=20,
        countries=None,
        country="US",
    ):
        return {
            "product": {
                "sku": sku,
                "price": price,
                "stock": stock,
                "countries": ["US", "CA"] if countries is None else countries,
            },
            "country": country,
        }

    return build_payload


def test_product_rejects_negative_stock(product_payload_factory):
    product_data = product_payload_factory(stock=-1)["product"]

    with pytest.raises(ValidationError) as error:
        Product(**product_data)

    assert error.value.errors()[0]["loc"] == ("stock",)


def test_product_rejects_blank_sku(product_payload_factory):
    product_data = product_payload_factory(sku="   ")["product"]

    with pytest.raises(ValidationError) as error:
        Product(**product_data)

    assert error.value.errors()[0]["loc"] == ("sku",)


def test_product_rejects_invalid_country_in_countries(product_payload_factory):
    product_data = product_payload_factory(countries=["US", "USA"])["product"]

    with pytest.raises(ValidationError) as error:
        Product(**product_data)

    assert error.value.errors()[0]["loc"] == ("countries",)


def test_product_is_ready_for_country(product_payload_factory):
    payload = product_payload_factory()
    product = Product(**payload["product"])

    result = product.is_ready_for(payload["country"])

    assert result is True


@pytest.mark.parametrize("country", ["us", " US ", "Us", "uS"])
def test_validate_product_normalizes_country(
    country,
    product_payload_factory,
    test_client,
):
    payload = product_payload_factory(country=country)

    response = test_client.post(
        "/products/validate",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "sku": "PIXEL-10",
        "status": "READY",
    }


def test_validate_product_not_ready(product_payload_factory, test_client):
    payload = product_payload_factory(sku="PIXEL-X", price=-10)

    response = test_client.post(
        "/products/validate",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "sku": "PIXEL-X",
        "status": "NOT_READY",
    }


@pytest.mark.parametrize("market_enabled", [False], indirect=True)
def test_validate_product_not_ready_when_market_is_disabled(
    product_payload_factory,
    test_client,
):
    payload = product_payload_factory()

    response = test_client.post(
        "/products/validate",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "sku": "PIXEL-10",
        "status": "NOT_READY",
    }


@pytest.mark.parametrize(
    ("market_error", "country", "status_code", "detail"),
    [
        (MarketNotFound("DE"), "DE", 404, "Market DE not found"),
        (
            MarketServiceUnavailable(),
            "US",
            503,
            "Market service is unavailable",
        ),
    ],
    indirect=["market_error"],
)
def test_validate_product_handles_market_errors(
    country,
    status_code,
    detail,
    product_payload_factory,
    test_client,
):
    payload = product_payload_factory(country=country)

    response = test_client.post(
        "/products/validate",
        json=payload,
    )

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}


def test_invalid_product_stock(product_payload_factory, test_client):
    payload = product_payload_factory(stock=-10)

    response = test_client.post(
        "/products/validate",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "country",
    [
        "USA",
        "CAN",
        "MEXICO",
        "",
        "   ",
    ],
)
def test_validate_product_rejects_invalid_country(
    country,
    product_payload_factory,
    test_client,
):
    payload = product_payload_factory(country=country)

    response = test_client.post(
        "/products/validate",
        json=payload,
    )

    assert response.status_code == 422


def test_validate_duplicated_product_countries(product_payload_factory, test_client):
    payload = product_payload_factory(
        sku="PIXEL-X",
        countries=["US", "US", "US", "CA", "CA"],
        country="CA",
    )

    response = test_client.post(
        "/products/validate",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "sku": "PIXEL-X",
        "status": "READY",
    }
