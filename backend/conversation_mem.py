from typing import List, Dict, Optional, Tuple
import aiosqlite
import json
import logging
from firebase_admin import db

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MAX_MEMORY = 100  # Maximum number of messages to keep in memory for a user

class ConversationStorage:
    def __init__(self, db_path: str):
        self.db_path: str = db_path
        self.firebase_ref = db.reference('conversations')

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    user_id TEXT PRIMARY KEY,
                    history TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    filename TEXT,
                    content BLOB
                )
            """)
            await db.commit()

    async def get_convo(self, user_id: str) -> List[Dict[str, any]]:
        # Essayez d'abord de récupérer depuis Firebase
        firebase_convo = self.firebase_ref.child(user_id).get()
        if firebase_convo:
            return firebase_convo
        
        # Si pas dans Firebase, récupérez depuis SQLite
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT history FROM conversations WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])
        return []

    async def update_convo(self, user_id: str, conversation: List[Dict[str, any]]) -> None:
        # Ensure we're not exceeding the maximum memory
        if len(conversation) > MAX_MEMORY:
            conversation = conversation[:1] + conversation[-(MAX_MEMORY - 1):]
        
        # Mettre à jour dans Firebase
        self.firebase_ref.child(user_id).set(conversation)
        
        # Mettre à jour dans SQLite
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO conversations (user_id, history) VALUES (?, ?)",
                (user_id, json.dumps(conversation))
            )
            await db.commit()
        logger.debug(f"Updated conversation for user {user_id}")

    async def store_attachment(self, user_id: str, filename: str, content: bytes) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO attachments (user_id, filename, content) VALUES (?, ?, ?)",
                (user_id, filename, content)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_attachment(self, attachment_id: int) -> Optional[Tuple[str, bytes]]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT filename, content FROM attachments WHERE id = ?", (attachment_id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    return result
        return None

    async def delete_user_convo(self, user_id: str) -> None:
        # Supprimer de Firebase
        self.firebase_ref.child(user_id).delete()
        
        # Supprimer de SQLite
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            await db.execute("DELETE FROM attachments WHERE user_id = ?", (user_id,))
            await db.commit()
        logger.debug(f"Deleted conversation history for user {user_id}")

    async def summarize_conversation(self, conversation: List[Dict[str, any]]) -> str:
        # This is a placeholder. In a real implementation, you might want to use
        # an AI model to generate a summary of the conversation.
        return f"Previous conversation summary: {len(conversation)} messages exchanged."