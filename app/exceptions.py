class MarketServiceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class MarketServiceUnavailable(MarketServiceError):
    def __init__(self):
        super().__init__("Market service is unavailable")


class MarketNotFound(MarketServiceError):
    def __init__(self, country: str):
        self.country = country
        super().__init__(f"Market {country} not found")