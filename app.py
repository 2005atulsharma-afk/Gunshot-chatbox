import streamlit as st
from pathlib import Path

from config import (
    DOCUMENT_FOLDER,
    SUPPORTED_EXTENSIONS,
)

from retrieval.search import DocumentSearch
from retrieval.reranker import rerank

from llm.qwen import Qwen

from security.permissions import (
    default_user,
    authorize_request,
)




BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"




st.set_page_config(
    page_title="Linearized Amplifier Technologies AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)




st.markdown(
    """
    <style>

    /* Main page */

    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
    }

    .company-name {
        font-size: 1.15rem;
        font-weight: 500;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }

    .assistant-subtitle {
        opacity: 0.70;
        margin-bottom: 1.5rem;
    }

    /* Sidebar */

    .sidebar-company {
        text-align: center;
        margin-bottom: 15px;
    }

    .sidebar-company-name {
        font-size: 1.05rem;
        font-weight: 650;
        line-height: 1.25;
        margin-top: 10px;
    }

    .sidebar-tagline {
        font-size: 0.82rem;
        opacity: 0.65;
        margin-top: 5px;
    }

    /* Source styling */

    .source-box {
        border-radius: 8px;
        padding: 8px 12px;
        margin-top: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)




@st.cache_resource
def load_search_engine():

    return DocumentSearch()


@st.cache_resource
def load_qwen():

    return Qwen()


@st.cache_resource
def load_user():

    return default_user()


search_engine = load_search_engine()
qwen = load_qwen()
user = load_user()




if "messages" not in st.session_state:

    st.session_state.messages = []



with st.sidebar:


    if LOGO_PATH.exists():

        st.image(
            str(LOGO_PATH),
            use_container_width=True
        )


    st.markdown(
    """
    <div class="sidebar-company">
        <div class="sidebar-company-name">
            LINEARIZED AMPLIFIER TECHNOLOGIES
        </div>
    </div>
    """,
    unsafe_allow_html=True,
    )

    st.caption("Private Local AI Assistant")

    st.divider()

    st.subheader("Knowledge Base")

    document_count = sum(
        1
        for path in DOCUMENT_FOLDER.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in SUPPORTED_EXTENSIONS
        )
    )

    st.write(
        f"📚 {document_count} supported files"
    )

    st.divider()


    st.subheader("User")

    st.write(
        user.get(
            "username",
            "Unknown"
        )
    )

    st.divider()


    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()



if LOGO_PATH.exists():

    header_col1, header_col2 = st.columns(
        [1, 5]
    )

    with header_col1:

        st.image(
            str(LOGO_PATH),
            width=110
        )

    with header_col2:

        st.markdown(
            '<div class="main-title">Company AI Assistant</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="company-name">'
            'LINEARIZED AMPLIFIER TECHNOLOGIES'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="assistant-subtitle">'
            'Private AI assistant for company documents, '
            'projects, and technical knowledge.'
            '</div>',
            unsafe_allow_html=True,
        )

else:

    st.markdown(
        '<div class="main-title">'
        'Company AI Assistant'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="company-name">'
        'LINEARIZED AMPLIFIER TECHNOLOGIES'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="assistant-subtitle">'
        'Private AI assistant for company documents, '
        'projects, and technical knowledge.'
        '</div>',
        unsafe_allow_html=True,
    )


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message.get("sources"):

            with st.expander(
                "📚 Sources"
            ):

                for source in message["sources"]:

                    st.write(
                        f"• {source}"
                    )




question = st.chat_input(
    "Ask something about your company knowledge..."
)




if question:



    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)



    with st.chat_message("assistant"):

        with st.spinner(
            "Checking request permissions..."
        ):

            security_result = (
                authorize_request(
                    user,
                    question
                )
            )



        if not security_result.get(
            "allowed",
            False
        ):

            st.error(
                "🔒 Access denied"
            )

            reason = security_result.get(
                "reason",
                "This request is not permitted."
            )

            st.write(reason)

            assistant_text = (
                "I can't provide that information."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_text,
                    "sources": [],
                }
            )



        else:



            with st.spinner(
                "Searching company knowledge..."
            ):

                candidates = (
                    search_engine.search(
                        question,
                        user=user
                    )
                )

                results = rerank(
                    candidates,
                    top_k=3
                )

            if not results:

                assistant_text = (
                    "I couldn't find relevant "
                    "information in the available "
                    "documents."
                )

                st.markdown(
                    assistant_text
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_text,
                        "sources": [],
                    }
                )

            else:

                with st.spinner(
                    "Qwen is preparing the answer..."
                ):

                    response = qwen.answer(
                        question,
                        results
                    )

                assistant_text = response.get(
                    "answer",
                    "No answer was returned."
                )

                st.markdown(
                    assistant_text
                )


                if response.get(
                    "thinking",
                    False
                ):

                    st.caption(
                        "🧠 Deep reasoning"
                    )

                else:

                    st.caption(
                        "⚡ Fast mode"
                    )



                sources = response.get(
                    "sources",
                    []
                )

                if sources:

                    with st.expander(
                        "📚 Sources"
                    ):

                        for source in sources:

                            st.write(
                                f"• {source}"
                            )


                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_text,
                        "sources": sources,
                    }
                )
                