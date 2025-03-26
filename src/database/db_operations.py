import sqlite3
import os
import json
import uuid
from datetime import datetime
import streamlit as st

class ChatArchive:
    def __init__(self, db_path="chat_archive.db"):
        """
        Initialize the SQLite database connection and ensure the conversations table exists.
        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        """
        Create the conversations table if it does not already exist.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            user_id TEXT,
            user_name TEXT,
            timestamp TEXT,
            mode TEXT,
            messages TEXT
        )
        """
        self.connection.execute(create_table_query)
        self.connection.commit()

    def archive_conversation(self, messages, mode, user_info):
        """
        Archive a conversation:
          - If a conversation with the current session_id exists for the user, update it.
          - Otherwise, insert a new conversation.
        """
        try:
            session_id = st.session_state.get('current_chat_id', None)
            if session_id is None:
                session_id = str(uuid.uuid4())
                st.session_state.current_chat_id = session_id
            now = datetime.utcnow().isoformat()
            messages_json = json.dumps(messages)

            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id FROM conversations WHERE session_id = ? AND user_id = ?",
                (session_id, user_info['username'])
            )
            result = cursor.fetchone()
            if result:
                # Update the existing conversation.
                conversation_id = result[0]
                update_query = """
                UPDATE conversations
                SET messages = ?, timestamp = ?
                WHERE id = ?
                """
                cursor.execute(update_query, (messages_json, now, conversation_id))
            else:
                # Insert a new conversation record.
                conversation_id = str(uuid.uuid4())
                insert_query = """
                INSERT INTO conversations (id, session_id, user_id, user_name, timestamp, mode, messages)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(
                    insert_query,
                    (
                        conversation_id,
                        session_id,
                        user_info['username'],
                        user_info['name'],
                        now,
                        mode,
                        messages_json
                    )
                )
            self.connection.commit()
            return session_id
        except Exception as e:
            st.error(f"Error archiving conversation: {str(e)}")
            return None

    def get_user_conversations(self, user_id):
        """
        Retrieve all conversations for a specific user, ordered by timestamp (most recent first).
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM conversations WHERE user_id = ? ORDER BY timestamp DESC"
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            conversations = []
            for row in rows:
                conv = {
                    'id': row[0],
                    'session_id': row[1],
                    'user_id': row[2],
                    'user_name': row[3],
                    'timestamp': row[4],
                    'mode': row[5],
                    'messages': json.loads(row[6])
                }
                conversations.append(conv)
            return conversations
        except Exception as e:
            st.error(f"Error retrieving conversations: {str(e)}")
            return []

    def get_conversation(self, session_id, user_id):
        """
        Retrieve a specific conversation by session_id and user_id.
        """
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM conversations WHERE session_id = ? AND user_id = ?"
            cursor.execute(query, (session_id, user_id))
            row = cursor.fetchone()
            if row:
                conv = {
                    'id': row[0],
                    'session_id': row[1],
                    'user_id': row[2],
                    'user_name': row[3],
                    'timestamp': row[4],
                    'mode': row[5],
                    'messages': json.loads(row[6])
                }
                return conv
            return None
        except Exception as e:
            st.error(f"Error retrieving conversation: {str(e)}")
            return None

    def delete_chat(self, session_id):
        """
        Delete a conversation from the database by session_id.
        """
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM conversations WHERE session_id = ?"
            cursor.execute(query, (session_id,))
            self.connection.commit()
        except Exception as e:
            st.error(f"Error deleting conversation: {str(e)}")
