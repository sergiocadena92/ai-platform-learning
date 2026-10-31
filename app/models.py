from pydantic import BaseModel, Field, field_validator
from enum import StrEnum
from typing import Any


def normalize_country(country: str) -> str:
    cleaned = country.strip().upper()

    if not cleaned:
        raise ValueError("Country cannot be empty")

    if len(cleaned) != 2 or not cleaned.isascii() or not cleaned.isalpha():
        raise ValueError("Country must contain exactly two letters")

    return cleaned


class ReadinessStatus(StrEnum):
    READY = "READY"
    NOT_READY = "NOT_READY"


class Product(BaseModel):
    sku: str = Field(min_length=1)
    price: int
    stock: int = Field(ge=0)
    countries: list[str] = Field(min_length=1)

    def is_ready_for(self, country: str) -> bool:
        return self.price > 0 and self.stock > 0 and country in self.countries

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("SKU cannot be empty")

        return value

    @field_validator("countries", mode="before")
    @classmethod
    def parse_countries_format(cls, countries: Any) -> list[Any]:
        if isinstance(countries, list):
            return countries
        if isinstance(countries, str):
            return countries.split(",")
        raise ValueError("Unexpected format for countries")

    @field_validator("countries", mode="after")
    @classmethod
    def validate_countries(cls, countries: list[str]) -> list[str]:
        unique_countries = []
        seen = set()

        for country in countries:
            cleaned = normalize_country(country)

            if cleaned not in seen:
                seen.add(cleaned)
                unique_countries.append(cleaned)

        return unique_countries


class ProductStatus(BaseModel):
    sku: str
    status: ReadinessStatus


class ProductValidationRequest(BaseModel):
    product: Product
    country: str

    @field_validator("country")
    @classmethod
    def validate_country(cls, country: str) -> str:
        return normalize_country(country)


class MarketStatus(BaseModel):
    country: str
    enabled: bool


class LLMResponse(BaseModel):
    text: str
    model: str

    input_tokens: int | None = None
    output_tokens: int | None = None

    done_reason: str | None = None

    total_duration_ns: int | None = None
    load_duration_ns: int | None = None
    prompt_eval_duration_ns: int | None = None
    eval_duration_ns: int | None = None

class ProductExplanation(BaseModel):
    sku: str
    market: str
    status: ReadinessStatus
    reason: str
    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )