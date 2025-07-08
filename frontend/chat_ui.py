import streamlit as st
from backend.github_integration import get_github_profile, get_pull_requests
from backend.memory_manager import get_chat_memory, add_to_memory, conversation_history
from ai_core.agent_router import route_message
from backend.file_processor import process_file
from backend.summarizer import summarize_text


def render_chat_ui():
    col1, col2, col3 = st.columns([2, 6, 2])

    # Chat Memory Sidebar
    with col1:
        st.header("🗂️ Chat Memory")

        memory = get_chat_memory()
        for idx, msg in enumerate(memory[-50:], 1):
            st.write(f"{idx}. {msg}")

        if st.button("🗑️ Clear Memory"):
            conversation_history.clear()
            st.session_state.conversation = []
            st.session_state.chat_memory = []
            st.rerun()

    # Main Chat Interface
    with col2:
        st.header("💬 AI Chat")

        if "conversation" not in st.session_state:
            st.session_state.conversation = []

        for msg in st.session_state.conversation:
            icon = "🧑" if msg["role"] == "user" else "🤖"
            st.markdown(f"{icon} **{msg['role'].capitalize()}:** {msg['content']}")

        user_input = st.chat_input("Ask me anything...")

        uploaded_file = st.file_uploader(
            "Upload File (txt/pdf/docx/xlsx/pptx/jpg/png)",
            type=["txt", "pdf", "docx", "xlsx", "pptx", "jpg", "png"]
        )

        if uploaded_file:
            st.info(f"📂 Processing: {uploaded_file.name}")
            file_text = process_file(uploaded_file)

            if len(file_text) > 5000:
                st.warning("Large file detected, summarizing...")
                file_text = summarize_text(file_text)

            st.success("File processed.")
            display_ai_response(file_text)

        if user_input:
            add_to_memory(user_input)
            display_ai_response(user_input)

    # GitHub Sidebar with Login
    with col3:
        st.header("🐙 GitHub Profile")

        github_username = st.text_input(
            "Enter GitHub Username",
            value=st.session_state.get("github_user", ""),
            placeholder="e.g., octocat"
        )

        if github_username:
            st.session_state.github_user = github_username
            profile = get_github_profile(github_username)
            prs = get_pull_requests(github_username)
        else:
            profile = get_github_profile()
            prs = get_pull_requests()

        token_present = bool(st.secrets.get("GITHUB_API_KEY"))
        st.caption(f"🔑 GitHub Token Loaded: {'✅' if token_present else '❌ Not Set'}")

        if profile:
            avatar_url = profile.get("avatar_url", "")
            if avatar_url:
                st.image(avatar_url, width=80)
            st.write(f"**{profile.get('name', 'N/A')}**")
            st.caption(profile.get("bio", "No bAio provided."))

            st.subheader("📁 Recent Repositories")
            for repo in profile.get("repos", []):
                st.write(f"[{repo.get('name', 'Repo')}]({repo.get('html_url', '')})")

            st.subheader("🔧 Pull Requests")
            for pr in prs:
                st.write(f"[{pr.get('title', '')}]({pr.get('html_url', '')}) - **{pr.get('state', '')}**")


def display_ai_response(prompt):
    """
    Unified AI Response Pipeline:
    - If prompt starts with 'research:', use deep research agent
    - Otherwise, use Groq for streaming + Blackbox for code + optional execution
    """
    st.session_state.conversation.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        if prompt.lower().strip().startswith("research:"):
            st.markdown("🔎 **Conducting Deep Research...**")
            research_prompt = prompt.replace("research:", "", 1).strip()
            result = route_message("deepresearch", research_prompt)
            st.markdown(result)
            st.session_state.conversation.append({"role": "assistant", "content": result})
            return

        # Standard Groq + Blackbox response
        streamed_reply = ""
        response_area = st.empty()

        for chunk in route_message("groq", prompt):
            streamed_reply += chunk
            response_area.markdown(streamed_reply)

        st.session_state.conversation.append({"role": "assistant", "content": streamed_reply})
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": streamed_reply})

        st.divider()

        with st.expander("💡 Blackbox Code Suggestion"):
            suggestion = route_message("blackbox", prompt)
            st.code(suggestion, language="python")

            with st.expander("⚡ Execute Suggested Code"):
                output = route_message("blackbox_exec", suggestion)
                st.text_area("Execution Output", output, height=150)

