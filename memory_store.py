from typing import Any, Dict, List, Optional
from datetime import datetime
from langchain_core.memory import BaseMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from supabase import Client
import json

class SupabaseMessageHistory(BaseChatMessageHistory):
    def __init__(self, supabase: Client, table_name: str, session_id: str, user_id: Optional[str] = None):
        self.supabase = supabase
        self.table_name = table_name
        self.session_id = session_id
        self.user_id = user_id

    def get_messages(self) -> List[Dict[str, Any]]:
        response = self.supabase.table(self.table_name).select("*").eq("session_id", self.session_id).execute()
        return response.data

    def add_message(self, message: Dict[str, Any]) -> None:
        self.supabase.table(self.table_name).insert({**message, "session_id": self.session_id}).execute()

    def clear(self) -> None:
        self.supabase.table(self.table_name).delete().eq("session_id", self.session_id).execute()

class SupabaseMemory(BaseMemory):
    def __init__(
        self,
        supabase_client: Client,
        table_name: str,
        session_id: str = "default",
        user_id: Optional[str] = None,
        memory_key: str = "chat_history",
        input_key: str = "input",
        output_key: str = "output",
        return_messages: bool = False
    ):
        super().__init__()
        object.__setattr__(self, 'session_id', session_id)
        object.__setattr__(self, 'memory_key', memory_key)
        object.__setattr__(self, 'input_key', input_key)
        object.__setattr__(self, 'output_key', output_key)
        object.__setattr__(self, 'return_messages', return_messages)
        object.__setattr__(self, 'message_history', SupabaseMessageHistory(
            supabase=supabase_client,
            table_name=table_name,
            session_id=session_id,
            user_id=user_id
        ))

    @property
    def memory_variables(self) -> List[str]:
        """Define the memory variables."""
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables from Supabase."""
        messages = self.message_history.get_messages()
        if self.return_messages:
            return {self.memory_key: messages}
        
        # Convert messages to string format
        string_messages = []
        for message in messages:
            role = message["role"]
            content = message["content"]
            string_messages.append(f"{role}: {content}")
        
        return {self.memory_key: "\n".join(string_messages)}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """Save context from this conversation to Supabase."""
        input_str = inputs.get(self.input_key, "")
        output_str = outputs.get(self.output_key, "")

        self.message_history.add_message({"role": "human", "content": input_str})
        self.message_history.add_message({"role": "assistant", "content": output_str})

    def clear(self) -> None:
        """Clear memory contents."""
        self.message_history.clear()
        
        
class SimpleConversationStore:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def store_conversation(self, human_input, assistant_response):
        try:
            self.supabase.table("conversations").insert({
                "human_input": human_input,
                "assistant_response": assistant_response,
                "timestamp": datetime.now().isoformat(),
            }).execute()
        except Exception as e:
            print(f"Error storing conversation: {str(e)}")
            # Continue even if storage fails
            pass