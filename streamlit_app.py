
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# Set page config
st.set_page_config(page_title="Prompt Library", layout="wide")

# Theme toggle
if "theme" not in st.session_state:
    st.session_state.theme = "light"
theme = st.sidebar.radio("Theme", ["light", "dark"])
st.session_state.theme = theme

# User roles (simplified)
users = {"admin": "admin123", "viewer": "viewer123"}
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username in users and users[username] == password:
                st.session_state.user = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid credentials")
    st.stop()

# Load or initialize prompt database
db_path = os.path.join("..", "database", "prompt_library.db")
if not os.path.exists(db_path):
    df = pd.DataFrame(columns=["id", "title", "prompt", "application", "type", "tags", "version", "created_at", "updated_at", "notes", "screenshot_path", "rating"])
    df.to_csv(db_path, index=False)
else:
    df = pd.read_csv(db_path)

# Sidebar navigation
page = st.sidebar.selectbox("Navigation", ["Add Prompt", "View Prompts", "Export Prompts"])

# Add Prompt
if page == "Add Prompt":
    st.header("➕ Add New Prompt")
    with st.form("prompt_form"):
        title = st.text_input("Title")
        prompt = st.text_area("Prompt")
        application = st.selectbox("Application", ["ChatGPT", "Copilot", "Gemini"])
        ptype = st.selectbox("Type", ["Writing", "Coding", "Image Generation"])
        tags = st.text_input("Tags (comma-separated)")
        version = st.text_input("Version", value="v1.0")
        notes = st.text_area("Notes")
        screenshot = st.file_uploader("Upload Screenshot", type=["png", "jpg"])
        rating = st.slider("Rating", 1, 5, 3)
        submitted = st.form_submit_button("Save Prompt")
        if submitted:
            pid = f"{title.lower().replace(' ', '_')}_{version}"
            created_at = datetime.now().strftime("%Y-%m-%d")
            updated_at = created_at
            screenshot_path = ""
            if screenshot:
                screenshot_path = os.path.join("..", "screenshots", screenshot.name)
                with open(screenshot_path, "wb") as f:
                    f.write(screenshot.read())
            new_row = {
                "id": pid,
                "title": title,
                "prompt": prompt,
                "application": application,
                "type": ptype,
                "tags": tags,
                "version": version,
                "created_at": created_at,
                "updated_at": updated_at,
                "notes": notes,
                "screenshot_path": screenshot_path,
                "rating": rating
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(db_path, index=False)
            st.success("Prompt saved successfully!")

# View Prompts
elif page == "View Prompts":
    st.header("📚 Prompt Library")
    app_filter = st.multiselect("Filter by Application", df["application"].unique())
    type_filter = st.multiselect("Filter by Type", df["type"].unique())
    filtered_df = df.copy()
    if app_filter:
        filtered_df = filtered_df[filtered_df["application"].isin(app_filter)]
    if type_filter:
        filtered_df = filtered_df[filtered_df["type"].isin(type_filter)]
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['title']} ({row['application']})"):
            st.markdown(f"**Prompt:** {row['prompt']}")
            st.markdown(f"**Tags:** {row['tags']}")
            st.markdown(f"**Version:** {row['version']}")
            st.markdown(f"**Rating:** {'⭐' * int(row['rating'])}")
            st.markdown(f"**Notes:** {row['notes']}")
            if row["screenshot_path"] and os.path.exists(row["screenshot_path"]):
                st.image(row["screenshot_path"])

# Export Prompts
elif page == "Export Prompts":
    st.header("📤 Export Prompts")
    export_md = ""
    export_json = []
    for _, row in df.iterrows():
        export_md += f"# {row['title']}
"
        export_md += f"**Application**: {row['application']}

"
        export_md += f"**Type**: {row['type']}

"
        export_md += f"**Tags**: {row['tags']}

"
        export_md += f"**Version**: {row['version']}

"
        export_md += f"**Prompt**:
> {row['prompt']}

"
        export_md += f"**Notes**:
{row['notes']}

"
        export_md += f"**Rating**: {'⭐' * int(row['rating'])}

"
        export_md += "---

"
        export_json.append(row.to_dict())
    st.download_button("Download Markdown", export_md, file_name="prompts.md")
    st.download_button("Download JSON", json.dumps(export_json, indent=2), file_name="prompts.json")
