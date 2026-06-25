from app.domain.exceptions.base import DomainError


class ArticleNotFoundError(DomainError):
    pass


class ChapterNotFoundError(DomainError):
    pass


class ArticleAlreadyUnlockedError(DomainError):
    pass


class CannotBuySecretArticleError(DomainError):
    pass
