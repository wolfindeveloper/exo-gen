import logging
from uuid import uuid4, UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException

from app.config.settings import settings
from app.domain.entities.transaction import Transaction, TransactionStatus
from app.infrastructure.messaging.telegram_bot_service import TelegramBotService
from app.infrastructure.persistence.uow import SQLAlchemyUnitOfWork
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.persistence.repositories.sqlalchemy_player_repository import (
    SQLAlchemyPlayerRepository,
)
from app.infrastructure.persistence.repositories.sqlalchemy_stars_repository import (
    SQLAlchemyStarsPackageRepository,
    SQLAlchemyTransactionRepository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/stars/webhook")
async def stars_webhook(request: Request):
    secret = request.headers.get("x-telegram-bot-api-secret-token")
    if not secret or secret != settings.TELEGRAM_WEBHOOK_SECRET:
        logger.warning(
            "Webhook intrusion attempt: invalid or missing X-Telegram-Bot-Api-Secret-Token "
            f"(ip={request.client.host if request.client else 'unknown'}, "
            f"headers={dict(request.headers)})"
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    body = await request.json()
    update = body or {}

    pre_checkout_query = update.get("pre_checkout_query")
    if pre_checkout_query:
        query_id = pre_checkout_query.get("id")
        if query_id:
            bot = TelegramBotService()
            await bot.answer_pre_checkout_query(query_id, ok=True)
            logger.info(f"Pre-checkout query {query_id} approved")
        return {"ok": True}

    successful_payment = update.get("successful_payment")
    if successful_payment:
        telegram_charge_id = successful_payment.get("telegram_payment_charge_id")
        payload = successful_payment.get("invoice_payload", "")
        total_amount = successful_payment.get("total_amount", 0)

        if not telegram_charge_id or not payload:
            logger.warning(f"Missing charge_id or payload: {successful_payment}")
            return {"ok": True}

        async with AsyncSessionLocal() as session:
            tx_repo = SQLAlchemyTransactionRepository(session)

            tx = Transaction(
                id=uuid4(),
                player_id=UUID("00000000-0000-0000-0000-000000000000"),
                telegram_charge_id=telegram_charge_id,
                stars_amount=total_amount,
                xgen_amount=0,
                status=TransactionStatus.COMPLETED,
                created_at=datetime.now(timezone.utc),
            )

            try:
                player_id_str, package_id_str = payload.split(":", 1)
                player_id = UUID(player_id_str)
                package_id = UUID(package_id_str)
            except (ValueError, AttributeError):
                logger.error(f"Invalid payload: {payload}")
                return {"ok": True}

            player_repo = SQLAlchemyPlayerRepository(session)
            player = await player_repo.get_by_id(player_id)
            if not player:
                logger.error(f"Player {player_id} not found for payment {telegram_charge_id}")
                return {"ok": True}

            package_repo = SQLAlchemyStarsPackageRepository(session)
            package = await package_repo.get_by_id(package_id)
            if not package:
                logger.error(f"Package {package_id} not found for payment {telegram_charge_id}")
                return {"ok": True}

            tx.player_id = player_id
            tx.xgen_amount = package.xgen_reward

            inserted = await tx_repo.insert_if_not_exists(tx)
            if not inserted:
                logger.info(f"Tx {telegram_charge_id} already processed, skipping")
                return {"ok": True}

            player.add_xgen(package.xgen_reward)

            uow = SQLAlchemyUnitOfWork(session)
            await uow.commit()

            logger.info(
                f"Payment {telegram_charge_id}: +{package.xgen_reward} XGen player={player_id}"
            )

        return {"ok": True}

    logger.debug(f"Unhandled update: {update.get('update_id')}")
    return {"ok": True}
