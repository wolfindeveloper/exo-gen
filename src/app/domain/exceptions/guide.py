from app.domain.exceptions.base import DomainError


class ArticleNotFoundError(DomainError):
    pass


class ChapterNotFoundError(DomainError):
    pass


class ArticleAlreadyUnlockedError(DomainError):
    pass


class CannotBuySecretArticleError(DomainError):
    pass


class SeasonExpiredError(DomainError):
    def __init__(self, season_name: str):
        super().__init__(f"Season '{season_name}' has ended")


class KeyItemRequiredError(DomainError):
    def __init__(self, item_name: str | None = None):
        msg = f"Key item required: {item_name}" if item_name else "Required item not found in inventory"
        super().__init__(msg)
