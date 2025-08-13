import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import uuid

# =========================
# 1. Cấu hình Supabase
# =========================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "n8n_chat_histories"

# =========================
# 2. Lấy user_id
# =========================
def get_current_user_id():
    session = st.session_state.get("supabase_session")
    if session and "user" in session:
        return session["user"]["id"]
    return None

# =========================
# 3. Tạo session_id
# =========================
def get_or_create_session_id():
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    return st.session_state["session_id"]

# =========================
# 4. Lưu tin nhắn
# =========================
def save_message(user_id: str, session_id: str, role: str, content: str):
    data = {
        "user_id": user_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table(TABLE_NAME).insert(data).execute()

# =========================
# 5. Lấy lịch sử tin nhắn
# =========================
def load_chat_history(user_id: str, session_id: str):
    response = supabase.table(TABLE_NAME) \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("session_id", session_id) \
        .order("created_at") \
        .execute()
    return response.data if response.data else []

# =========================
# 6. UI Streamlit
# =========================
st.set_page_config(page_title="Chatbot có lưu lịch sử", layout="wide")
st.title("💬 Chatbot có lưu lịch sử vào Supabase")

# --- Giả lập login ---
if "supabase_session" not in st.session_state:
    st.session_state["supabase_session"] = {
        "user": {"id": "00000000-0000-0000-0000-000000000000"}  # test ID
    }

user_id = get_current_user_id()
session_id = get_or_create_session_id()

if not user_id:
    st.warning("Bạn cần đăng nhập để chat.")
else:
    # Hiển thị lịch sử chat
    chat_history = load_chat_history(user_id, session_id)
    for msg in chat_history:
        if msg["role"] == "user":
            st.markdown(f"**🧑‍💻 Bạn:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Bot:** {msg['content']}")

    # Nhập tin nhắn
    message = st.text_input("Nhập tin nhắn:")
    role = st.selectbox("Vai trò", ["user", "assistant"])

    if st.button("Gửi"):
        if message.strip():
            save_message(user_id, session_id, role, message)
            st.experimental_rerun()
