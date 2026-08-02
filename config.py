from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    database_path: str
    shop_size: int
    rotation_minutes: int
    starting_coins: int
    admin_user_ids: frozenset[int]

    @classmethod
    def from_environment(cls) -> "Settings":
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN is missing. Add it to your environment before starting the bot."
            )

        admin_ids = frozenset(
            int(value.strip())
            for value in os.environ.get("ADMIN_USER_IDS", "").split(",")
            if value.strip()
        )
        return cls(
            telegram_bot_token=token,
            database_path=os.environ.get("CARD_SHOP_DATABASE", "data/card_shop.sqlite3"),
            shop_size=max(1, int(os.environ.get("SHOP_SIZE", "5"))),
            rotation_minutes=max(1, int(os.environ.get("ROTATION_MINUTES", "60"))),
            starting_coins=max(0, int(os.environ.get("STARTING_COINS", "1000"))),
            admin_user_ids=admin_ids,
        )
