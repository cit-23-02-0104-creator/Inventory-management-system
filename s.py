import os
import re 
from typing import Dict, Any, List, Tuple
from datetime import datetime

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# --------------------------
# Page Configuration
# --------------------------

st.set_page_config(
    page_title="IMS Assistant",
    page_icon="📦",
    layout="centered"
)

# --------------------------
# Custom UI Theme
# --------------------------

st.markdown("""
<style>

/* MAIN BACKGROUND */
.main, body {
    background-color: #000000 !important;
}

/* HEADER */
.header-container {
    background: #414a58;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 20px;
    color: white;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.07);
}

/* BOT NAME */
.bot-name {
    font-size: 24px;
    font-weight: 600;
}

.bot-status {
    color: #b6ffb4;
    font-size: 13px;
}

/* CHAT MESSAGES */
.chat-message {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    font-size: 15px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.06);
}

/* BOT BUBBLE */
.bot-message {
    background-color: #414a58;
    border-left: 6px solid #0d6efd;
    margin-right: 50px;
    color: white;
}

/* USER BUBBLE */
.user-message {
    background-color: #ffffff;
    border-right: 6px solid #0d6efd;
    margin-left: 50px;
    color: #000000;
}

/* TIMESTAMP */
.message-time {
    font-size: 11px;
    margin-top: 5px;
    opacity: 0.7;
}

/* TABLE CONTAINER */
.table-container {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
    margin-bottom: 10px;
}

/* HIDE STREAMLIT FOOTER AND MENU */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* CHAT INPUT STYLING */
.stChatInput > div {
    background-color: #1e1e1e;
}

.stChatInput input {
    background-color: #2d2d2d !important;
    color: white !important;
    border: 2px solid #0d6efd !important;
    border-radius: 10px !important;
}

/* STREAMLIT CHAT MESSAGES */
.stChatMessage {
    background-color: transparent !important;
}
            
/* FIX FOOTER STICKED TO BOTTOM */
.custom-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #111;
    color: #aaa;
    text-align: center;
    padding: 10px;
    font-size: 12px;
    border-top: 1px solid #333;
    z-index: 9999;
}


</style>
""", unsafe_allow_html=True)

# --------------------------
# Firebase initialization
# --------------------------

@st.cache_resource
def init_firebase():
    """Initialize Firebase Realtime Database"""
    load_dotenv()

    # Fallback path for local testing (uses forward slashes for robustness)
    FALLBACK_CRED_PATH = r"C:\Users\acer\Desktop\TCC2 Project\invman-b8270-firebase-adminsdk-fbsvc-506094df77.json"
    
    if not firebase_admin._apps:
        # 1. Try environment variable (best practice)
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        
        if not cred_path:
            cred_path = FALLBACK_CRED_PATH
        
        if not os.path.exists(cred_path):
            st.error(f"❌ Firebase credentials not found at: {cred_path}")
            raise RuntimeError(f"Firebase credentials not found at {cred_path}.")

        try:
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://invman-b8270-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        except Exception as e:
            st.error(f"❌ Error initializing Firebase: {e}")
            raise

    return db.reference()



try:
    root_ref = init_firebase()
except RuntimeError as e:
    st.info("Configuration needed. Run 'set GOOGLE_APPLICATION_CREDENTIALS=...' in your terminal.")
    st.stop()
except Exception:
    st.stop()


# --------------------------
# Inventory helpers
# --------------------------

def list_all_items() -> List[Dict[str, Any]]:
    """Get all items from inventory"""
    try:
        inventory_ref = root_ref.child('inventory')
        data = inventory_ref.get()
        
        if not data:
            return []
        
        items = []
        for key, value in data.items():
            if isinstance(value, dict):
                # Ensure data types are correct on retrieval
                value['id'] = key
                try:
                    value['stock'] = int(value.get('stock', 0))
                except (ValueError, TypeError):
                    value['stock'] = 0
                
                items.append(value)
        return items
    except Exception as e:
        # Errors during fetching are usually due to network or rules issues
        st.error(f"Error fetching data: {e}")
        return []


def find_item_by_name_or_sku(query: str) -> List[Dict[str, Any]]:
    """Search items by name or SKU (case-insensitive)"""
    query_lower = query.lower()
    items = list_all_items()
    return [
        item for item in items
        if query_lower in str(item.get("name", "")).lower()
        or query_lower in str(item.get("sku", "")).lower()
    ]


def update_item_stock(doc_id: str, new_stock: int) -> bool:
    """Update stock quantity for an item"""
    try:
        inventory_ref = root_ref.child('inventory').child(doc_id)
        inventory_ref.update({"stock": int(new_stock)})
        return True
    except Exception as e:
        st.error(f"Error updating stock: {e}")
        return False


def add_new_item(name: str, sku: str, stock: int) -> bool:
    """Add a new item to inventory"""
    try:
        inventory_ref = root_ref.child('inventory')
        inventory_ref.push({
            'name': name.strip(),
            'sku': sku.strip(),
            'stock': int(stock)
        })
        return True
    except Exception as e:
        st.error(f"Error adding item: {e}")
        return False


def delete_item(doc_id: str) -> bool:
    """Delete an item from inventory"""
    try:
        inventory_ref = root_ref.child('inventory').child(doc_id)
        inventory_ref.delete()
        return True
    except Exception as e:
        st.error(f"Error deleting item: {e}")
        return False

# --------------------------
# Simple chatbot logic (Rule-based)
# --------------------------

def parse_user_message(message: str) -> Tuple[str, Dict[str, Any]]:
    """Parse user message and return (intent, params)"""
    text = message.strip().lower()

    # List all items
    if any(word in text for word in ["list", "all items", "show items", "inventory", "show all", "show me"]):
        return "list_items", {}

    
    if "add" in text:
        # Split by "add " to separate potential multiple commands.
        segments = text.split("add ")
        items_to_add = []

        for segment in segments:
            segment = segment.strip()
            if not segment: continue
            
            # Must contain 'sku' to be a valid add command
            if "sku" in segment:
                try:
                    # Extract Name
                    if "with sku" in segment:
                        parts = segment.split("with sku", 1)
                    elif "sku" in segment:
                        parts = segment.split("sku", 1)
                    else:
                        continue
                        
                    name_part = parts[0].strip()
                    rest = parts[1].strip()

                    # Extract Stock if present
                    if "stock" in rest:
                        sku_parts = rest.split("stock", 1)
                        sku_part = sku_parts[0].strip()
                        stock_part = sku_parts[1].strip()
                        
                       
                        stock_match = re.search(r'\d+', stock_part)
                        qty = int(stock_match.group()) if stock_match else 0
                    else:
                        sku_part = rest.strip()
                        qty = 0
                    
                    # Cleanup Name and SKU (remove trailing punctuation/conjunctions)
                    for junk in [",", ";", ".", " and", " &"]:
                         if name_part.endswith(junk): name_part = name_part[:-len(junk)].strip()
                         if sku_part.endswith(junk): sku_part = sku_part[:-len(junk)].strip()
                    
                   
                    if name_part and sku_part:
                        items_to_add.append({"name": name_part, "sku": sku_part, "quantity": qty})
                except Exception:
                    continue
        
        if items_to_add:
            return "add_multiple_items", {"items": items_to_add}

    # Update stock: "update stock of laptop to 5"
    if "update" in text and "stock" in text and "to" in text:
        try:
            # Using 'of' as separator
            after_of = text.split("of", 1)[1]
            name_part, qty_part = after_of.split("to", 1)
            item_query = name_part.strip()
            # Robust number extraction
            qty_match = re.search(r'\d+', qty_part)
            qty = int(qty_match.group()) if qty_match else 0
            return "update_stock", {"query": item_query, "quantity": qty}
        except Exception:
            return "unknown", {}

    
    if "delete" in text or "remove" in text:
        if "delete" in text:
            item_query = text.replace("delete", "").strip()
        else:
            item_query = text.replace("remove", "").strip()
        return "delete_item", {"query": item_query}

    # Get single item: "stock of laptop" / "how many laptops"
    if "stock of" in text or "how many" in text or "check" in text:
        if "stock of" in text:
            item_query = text.split("stock of", 1)[1].strip()
        elif "check" in text:
            item_query = text.replace("check", "").strip()
        else:
            item_query = text.replace("how many", "").strip()
        return "get_item", {"query": item_query}

    return "unknown", {}


def handle_user_message(message: str) -> Tuple[str, Any]:
    """Process user message and return (response_text, dataframe_or_none)"""
    intent, params = parse_user_message(message)
    query = params.get("query", "")
    
    if intent == "list_items":
        items = list_all_items()
        if not items:
            return "📦 Your inventory is currently empty. Try adding an item!", None
        
        df = pd.DataFrame(items)
        # Select and order columns for display
        df = df[['name', 'sku', 'stock']]
        df.columns = ['Item Name', 'SKU', 'Stock']
        return f"Here's your complete inventory ({len(items)} items):", df
    
    elif intent == "get_item":
        matches = find_item_by_name_or_sku(query)
        
        if not matches:
            return f"❌ I couldn't find any items matching '{query}' in your inventory.", None
        
        df = pd.DataFrame(matches)
        df = df[['name', 'sku', 'stock']]
        df.columns = ['Item Name', 'SKU', 'Stock']
        return f"Here's what I found for '{query}':", df
    
    elif intent == "update_stock":
        quantity = params.get("quantity", 0)
        matches = find_item_by_name_or_sku(query)
        
        if not matches:
            return f"❌ I couldn't find '{query}' in your inventory to update.", None
        
        if len(matches) > 1:
            return f"⚠️ Found multiple items matching '{query}'. Please be more specific (use SKU).", None
            
        item = matches[0]
        old_stock = item.get('stock', 0)
        success = update_item_stock(item["id"], quantity)
        
        if success:
            df = pd.DataFrame([{
                'Item Name': item.get('name', 'Unknown'),
                'SKU': item.get('sku', 'N/A'),
                'Old Stock': old_stock,
                'New Stock': quantity,
                'Change': quantity - old_stock
            }])
            return f"✅ Stock updated successfully!", df
        else:
            return "❌ Sorry, I couldn't update the stock. Please check the logs.", None
    
   
    elif intent == "add_multiple_items":
        items_to_add = params.get("items", [])
        results = []
        
        for item in items_to_add:
            success = add_new_item(item["name"], item["sku"], item["quantity"])
            status = "✅ Added" if success else "❌ Failed"
            results.append({
                'Status': status,
                'Item Name': item['name'],
                'SKU': item['sku'],
                'Initial Stock': item['quantity']
            })
        
        df = pd.DataFrame(results)
        return f"Processed {len(items_to_add)} item(s):", df
    
    elif intent == "delete_item":
        matches = find_item_by_name_or_sku(query)
        
        if not matches:
            return f"❌ I couldn't find '{query}' in your inventory to delete.", None
        
        if len(matches) > 1:
            return f"⚠️ Found multiple items matching '{query}'. Please be more specific (use SKU).", None
            
        item = matches[0]
        success = delete_item(item["id"])
        
        if success:
            df = pd.DataFrame([{
                'Deleted Item': item.get('name', 'Unknown'),
                'SKU': item.get('sku', 'N/A'),
                'Last Stock': item.get('stock', 0)
            }])
            return f"✅ Item deleted from inventory!", df
        else:
            return "❌ Sorry, I couldn't delete the item. Please try again.", None
    
    else: 
        return (
            "🤔 I'm not sure what you mean.\n\n"
            "**You can try:**\n"
            "• 'List all items'\n"
            "• 'Stock of Laptop'\n"
            "• 'Update stock of Laptop to 5'\n"
            "• 'Add item A sku 1 stock 10, add item B sku 2...'\n"
            "• 'Delete Laptop'"
        ), None


# --------------------------
# Header
# --------------------------

st.markdown("""
<div class="header-container">
    <div style="display:flex;align-items:center;">
        <div style="font-size:40px;margin-right:15px;">📦</div>
        <div>
            <div class="bot-name">IMS Assistant</div>
            <div class="bot-status">● Online</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Session State
# --------------------------

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    # Add welcome message
    st.session_state["messages"].append({
        "role": "assistant",
        "content": "Hello 👋 I'm your IMS Assistant. How can I help you ?",
        "time": datetime.now().strftime("%H:%M"),
        "df": None
    })

# --------------------------
# Chat Display
# --------------------------

for msg in st.session_state["messages"]:
    bubble = "bot-message" if msg["role"] == "assistant" else "user-message"
    sender = "🤖 Assistant:" if msg["role"] == "assistant" else "👤 You:"
    
    st.markdown(f"""
        <div class="chat-message {bubble}">
            <strong>{sender}</strong><br>
            {msg['content']}
            <div class="message-time">{msg['time']}</div>
        </div>
    """, unsafe_allow_html=True)
    
    if msg.get("df") is not None:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.dataframe(
            msg["df"],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Item Name": st.column_config.TextColumn("📦 Item Name", width="medium"),
                "SKU": st.column_config.TextColumn("🏷️ SKU", width="small"),
                "Stock": st.column_config.NumberColumn("📊 Stock", width="small"),
                "Old Stock": st.column_config.NumberColumn("📉 Old Stock", width="small"),
                "New Stock": st.column_config.NumberColumn("📈 New Stock", width="small"),
                "Change": st.column_config.NumberColumn("🔄 Change", width="small"),
                "Initial Stock": st.column_config.NumberColumn("📊 Initial Stock", width="small"),
                "Deleted Item": st.column_config.TextColumn("🗑️ Deleted Item", width="medium"),
                "Last Stock": st.column_config.NumberColumn("📊 Last Stock", width="small"),
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# Chat Input (Prevent Double Output Fix Applied)
# --------------------------

user_input = st.chat_input("Type your message here...")

if user_input:
   
    if (len(st.session_state["messages"]) > 0 and 
        st.session_state["messages"][-1]["role"] == "user" and 
        st.session_state["messages"][-1]["content"] == user_input):
        st.stop()


    st.session_state["messages"].append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%H:%M"),
        "df": None
    })
    

    with st.spinner("🤔 Processing..."):
        response, df = handle_user_message(user_input)
    

    st.session_state["messages"].append({
        "role": "assistant",
        "content": response,
        "time": datetime.now().strftime("%H:%M"),
        "df": df
    })
    
   
    st.rerun()

# --------------------------
# Footer
# --------------------------


st.markdown("""
<div class="custom-footer">
    📦 IMS Assistant — Manage stock smarter
</div>
""", unsafe_allow_html=True)