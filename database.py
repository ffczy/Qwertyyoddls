from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import random
import secrets
import sqlite3
from typing import Iterator

from .catalog import (
    CARD_CATALOG,
    CardDefinition,
    card_by_id,
    localized_card_fields,
    rarity_appearance_weight,
    stock_for_rarity,
)


class Database:
    def __init__(self, path: str, starting_coins: int, shop_size: int, rotation_minutes: int) -> None:
        self.path = path
        self.starting_coins = starting_coins
        self.shop_size = shop_size
        self.rotation_minutes = rotation_minutes
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode = WAL;
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    username TEXT,
                    coins INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS cards (
                    card_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    set_name TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    emoji TEXT NOT NULL,
                    description TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS shop_slots (
                    slot_key INTEGER PRIMARY KEY,
                    starts_at TEXT NOT NULL,
                    ends_at TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS shop_items (
                    slot_key INTEGER NOT NULL,
                    card_id TEXT NOT NULL,
                    stock INTEGER NOT NULL,
                    PRIMARY KEY (slot_key, card_id),
                    FOREIGN KEY (slot_key) REFERENCES shop_slots(slot_key),
                    FOREIGN KEY (card_id) REFERENCES cards(card_id)
                );
                CREATE TABLE IF NOT EXISTS collection (
                    telegram_id INTEGER NOT NULL,
                    card_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (telegram_id, card_id),
                    FOREIGN KEY (telegram_id) REFERENCES users(telegram_id),
                    FOREIGN KEY (card_id) REFERENCES cards(card_id)
                );
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    card_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_price INTEGER NOT NULL,
                    purchased_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            user_columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }
            if "username" not in user_columns:
                connection.execute("ALTER TABLE users ADD COLUMN username TEXT")
            connection.executemany(
                """
                INSERT OR IGNORE INTO cards
                (card_id, name, set_name, rarity, price, emoji, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        card.card_id,
                        card.name,
                        card.set_name,
                        card.rarity,
                        card.price,
                        card.emoji,
                        card.description,
                    )
                    for card in CARD_CATALOG
                ],
            )
            # Keep existing card IDs and all relational data intact while
            # applying the current rarity and price balance to card metadata.
            connection.executemany(
                """
                UPDATE cards
                SET name = ?, set_name = ?, rarity = ?, price = ?, emoji = ?, description = ?
                WHERE card_id = ?
                """,
                [
                    (
                        card.name,
                        card.set_name,
                        card.rarity,
                        card.price,
                        card.emoji,
                        card.description,
                        card.card_id,
                    )
                    for card in CARD_CATALOG
                ],
            )
            connection.commit()

    def ensure_user(
        self,
        telegram_id: int,
        display_name: str,
        username: str | None = None,
    ) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO users (telegram_id, display_name, username, coins)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    username = COALESCE(excluded.username, users.username)
                """,
                (
                    telegram_id,
                    display_name[:80],
                    username.lower().strip() if username else None,
                    self.starting_coins,
                ),
            )
            connection.commit()

    def get_balance(self, telegram_id: int) -> int:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT coins FROM users WHERE telegram_id = ?", (telegram_id,)
            ).fetchone()
            return int(row["coins"]) if row else self.starting_coins

    def _slot_key(self, now_timestamp: int) -> int:
        return now_timestamp // (self.rotation_minutes * 60)

    def _create_shop_slot(
        self,
        connection: sqlite3.Connection,
        slot_key: int,
        selection_seed: int | None = None,
    ) -> None:
        starts_at = slot_key * self.rotation_minutes * 60
        ends_at = (slot_key + 1) * self.rotation_minutes * 60
        connection.execute(
            "INSERT INTO shop_slots (slot_key, starts_at, ends_at) VALUES (?, datetime(?, 'unixepoch'), datetime(?, 'unixepoch'))",
            (slot_key, starts_at, ends_at),
        )
        cards = list(CARD_CATALOG)
        rng = random.Random(slot_key if selection_seed is None else selection_seed)
        selected: list[CardDefinition] = []
        for _ in range(min(self.shop_size, len(cards))):
            total_weight = sum(
                rarity_appearance_weight(card.rarity) for card in cards
            )
            if total_weight <= 0:
                break
            target = rng.random() * total_weight
            running_weight = 0.0
            for index, card in enumerate(cards):
                running_weight += rarity_appearance_weight(card.rarity)
                if running_weight >= target:
                    selected.append(card)
                    cards.pop(index)
                    break
        connection.executemany(
            "INSERT INTO shop_items (slot_key, card_id, stock) VALUES (?, ?, ?)",
            [
                (
                    slot_key,
                    card.card_id,
                    stock_for_rarity(card.rarity),
                )
                for card in selected
            ],
        )

    def _shop_rows(
        self, connection: sqlite3.Connection, slot_key: int
    ) -> list[sqlite3.Row]:
        return list(
            connection.execute(
                """
                SELECT c.card_id, c.name, c.set_name, c.rarity, c.price, c.emoji,
                       c.description, i.stock
                FROM shop_items i
                JOIN cards c ON c.card_id = i.card_id
                WHERE i.slot_key = ?
                ORDER BY c.price ASC
                """,
                (slot_key,),
            ).fetchall()
        )

    def get_current_shop(self, now_timestamp: int) -> tuple[int, list[sqlite3.Row]]:
        slot_key = self._slot_key(now_timestamp)
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            slot = connection.execute(
                "SELECT slot_key FROM shop_slots WHERE slot_key = ?", (slot_key,)
            ).fetchone()
            if not slot:
                self._create_shop_slot(connection, slot_key)
            rows = self._shop_rows(connection, slot_key)
            connection.commit()
            return slot_key, rows

    def refresh_shop(self, now_timestamp: int) -> tuple[int, list[sqlite3.Row]]:
        """Replace the current shop inventory without changing its time slot."""
        slot_key = self._slot_key(now_timestamp)
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM shop_items WHERE slot_key = ?", (slot_key,))
            connection.execute("DELETE FROM shop_slots WHERE slot_key = ?", (slot_key,))
            self._create_shop_slot(connection, slot_key, secrets.randbits(64))
            rows = connection.execute(
                """
                SELECT c.card_id, c.name, c.set_name, c.rarity, c.price, c.emoji,
                       c.description, i.stock
                FROM shop_items i
                JOIN cards c ON c.card_id = i.card_id
                WHERE i.slot_key = ?
                ORDER BY c.price ASC
                """,
                (slot_key,),
            ).fetchall()
            connection.commit()
            return slot_key, list(rows)

    def buy_card(self, telegram_id: int, card_id: str, quantity: int, now_timestamp: int) -> tuple[bool, str, int]:
        if quantity < 1 or quantity > 99:
            return False, "اختر كمية بين 1 و99.", self.get_balance(telegram_id)
        slot_key = self._slot_key(now_timestamp)
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            shop = connection.execute(
                """
                SELECT c.name, c.price, i.stock
                FROM shop_items i JOIN cards c ON c.card_id = i.card_id
                WHERE i.slot_key = ? AND i.card_id = ?
                """,
                (slot_key, card_id),
            ).fetchone()
            user = connection.execute(
                "SELECT coins FROM users WHERE telegram_id = ?", (telegram_id,)
            ).fetchone()
            if not shop:
                connection.rollback()
                return False, "هذه البطاقة ليست في المتجر الحالي. استخدم /shop لرؤية مخزون هذه الساعة.", int(user["coins"]) if user else 0
            if not user:
                connection.rollback()
                return False, "يرجى استخدام /start أولًا.", 0
            total = int(shop["price"]) * quantity
            if int(shop["stock"]) < quantity:
                connection.rollback()
                return False, f"المتبقي في المخزون: {shop['stock']} نسخة فقط.", int(user["coins"])
            if int(user["coins"]) < total:
                connection.rollback()
                return False, f"تحتاج إلى {total:,} عملة، بينما رصيدك {user['coins']:,} عملة فقط.", int(user["coins"])
            connection.execute("UPDATE users SET coins = coins - ? WHERE telegram_id = ?", (total, telegram_id))
            connection.execute(
                "UPDATE shop_items SET stock = stock - ? WHERE slot_key = ? AND card_id = ?",
                (quantity, slot_key, card_id),
            )
            connection.execute(
                """
                INSERT INTO collection (telegram_id, card_id, quantity) VALUES (?, ?, ?)
                ON CONFLICT(telegram_id, card_id) DO UPDATE SET quantity = quantity + excluded.quantity
                """,
                (telegram_id, card_id, quantity),
            )
            connection.execute(
                "INSERT INTO purchases (telegram_id, card_id, quantity, total_price) VALUES (?, ?, ?, ?)",
                (telegram_id, card_id, quantity, total),
            )
            connection.commit()
            card_name = localized_card_fields(card_id)[0]
            return True, f"تم شراء {quantity} × {card_name} مقابل {total:,} عملة.", int(user["coins"]) - total

    def get_collection(self, telegram_id: int) -> list[sqlite3.Row]:
        with self.connection() as connection:
            return list(
                connection.execute(
                    """
                    SELECT c.name, c.rarity, c.emoji, c.card_id, col.quantity
                    FROM collection col JOIN cards c ON c.card_id = col.card_id
                    WHERE col.telegram_id = ? AND col.quantity > 0
                    ORDER BY c.price DESC
                    """,
                    (telegram_id,),
                ).fetchall()
            )

    def add_coins(self, telegram_id: int, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        with self.connection() as connection:
            connection.execute("UPDATE users SET coins = coins + ? WHERE telegram_id = ?", (amount, telegram_id))
            connection.commit()
            return self.get_balance(telegram_id)

    def transfer_coins(
        self,
        sender_id: int,
        receiver_username: str,
        amount: int,
    ) -> str:
        """Transfer coins atomically to a previously seen Telegram username."""
        normalized_username = receiver_username.strip().lstrip("@").lower()
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            sender = connection.execute(
                "SELECT coins FROM users WHERE telegram_id = ?", (sender_id,)
            ).fetchone()
            receiver = connection.execute(
                """
                SELECT telegram_id
                FROM users
                WHERE lower(username) = ?
                LIMIT 1
                """,
                (normalized_username,),
            ).fetchone()
            if not sender or not receiver:
                connection.rollback()
                return "receiver_not_found"
            if int(receiver["telegram_id"]) == sender_id:
                connection.rollback()
                return "self_transfer"
            if int(sender["coins"]) < amount:
                connection.rollback()
                return "insufficient_funds"
            connection.execute(
                "UPDATE users SET coins = coins - ? WHERE telegram_id = ?",
                (amount, sender_id),
            )
            connection.execute(
                "UPDATE users SET coins = coins + ? WHERE telegram_id = ?",
                (amount, int(receiver["telegram_id"])),
            )
            connection.commit()
            return "transferred"

    def card_exists(self, card_id: str) -> bool:
        return card_by_id(card_id) is not None
