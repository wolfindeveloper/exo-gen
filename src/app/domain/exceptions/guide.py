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
