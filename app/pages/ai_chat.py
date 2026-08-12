import sys
from pathlib import Path

import streamlit as st

project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

sys.path.append(str(project_root))

from app.utils.data_manager import DataManager

from src.analytics.analytics_handler import (
    AnalyticsHandler
)

from src.rag.llm_handler import (
    LLMHandler
)

from src.rag.rag_engine import (
    RAGEngine
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="AI Data Analyst Chat",
    layout="wide"
)

st.title(
    "���������🤖 AI Data Analyst Chat"
)

# =====================================
# LOAD DATA
# =====================================

df = DataManager.get_data()

if df is None:

    st.warning(
        "Please upload and select a dataset first."
    )

    st.stop()

# =====================================
# DATASET INFO
# =====================================

dataset_name = (
    DataManager.get_active_dataset_name()
)

dataset_summary = (
    DataManager.get_dataset_summary()
)

dataset_fingerprint = (
    DataManager.get_dataset_fingerprint()
)

dataset_intelligence = DataManager.get_dataset_intelligence()

if dataset_fingerprint is None:

    st.error(
        "Dataset fingerprint not found."
    )

    st.stop()

# =====================================
# RESET CHAT IF DATASET CHANGES
# =====================================

previous_dataset = (
    st.session_state.get(
        "chat_dataset"
    )
)

if previous_dataset != dataset_fingerprint:

    st.session_state.messages = []

    st.session_state[
        "chat_dataset"
    ] = dataset_fingerprint

# =====================================
# DATASET HEADER
# =====================================

st.success(
    f"Active Dataset: {dataset_name}"
)

if dataset_summary:

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Rows",
            dataset_summary.get(
                "row_count",
                0
            )
        )

    with col2:

        st.metric(
            "Columns",
            dataset_summary.get(
                "column_count",
                0
            )
        )

# =====================================
# SUGGESTED QUESTIONS
# =====================================

if dataset_intelligence and dataset_intelligence.get('suggested_questions'):

    st.markdown(
        "### Suggested Questions"
    )

    for suggested_question in (
        dataset_intelligence.get(
            'suggested_questions',
            []
        )
    ):

        st.info(
            suggested_question
        )
elif dataset_summary:

    st.markdown(
        "### Suggested Questions"
    )

    for suggested_question in (
        dataset_summary.get(
            "suggested_questions",
            []
        )
    ):

        st.info(
            suggested_question
        )

# =====================================
# ANALYTICS ENGINE
# =====================================

analytics_handler = (
    AnalyticsHandler(
        df,
        dataset_summary
    )
)

# =====================================
# RAG ENGINE
# =====================================

@st.cache_resource
def load_rag_engine(
    fingerprint,
    dataframe
):

    return RAGEngine(
        dataframe
    )

with st.spinner(

    "Preparing your dataset..."

):

    rag_engine = load_rag_engine(

        dataset_fingerprint,

        df

    )

# =====================================
# LLM
# =====================================

llm = LLMHandler()

# =====================================
# CHAT HISTORY
# =====================================

if "messages" not in st.session_state:

    st.session_state.messages = []

# =====================================
# DISPLAY CHAT
# =====================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

# =====================================
# USER INPUT
# =====================================

question = st.chat_input(
    "Ask anything about your dataset..."
)

if question:

    st.session_state.messages.append(

        {
            "role": "user",
            "content": question
        }

    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Analyzing..."
        ):

            # ==========================
            # ANALYTICS FIRST
            # ==========================

            analytics_response = (

                analytics_handler
                .answer_question(
                    question
                )

            )

            if analytics_response:

                response = (
                    analytics_response
                )

                st.success(
                    "Answered using Analytics Engine"
                )

                st.markdown(
                    response
                )

            else:

                # ==========================
                # RAG FALLBACK
                # ==========================

                retrieved_docs = (
                    rag_engine.retrieve(
                        question
                    )
                )

                # Build context string from dataset summary and retrieved documents
                context_parts = []
                if dataset_summary:
                    context_parts.append("Dataset Summary:")
                    for key, value in dataset_summary.items():
                        context_parts.append(f"  {key}: {value}")
                context_parts.append("\nRetrieved Records:")
                context_parts.extend(retrieved_docs)
                context_string = "\n".join(context_parts)

                response = llm.ask_question(
                    context_string,
                    question
                )

                st.markdown(
                    response
                )

                with st.expander(
                    "Retrieved Context"
                ):

                    for i, doc in enumerate(
                        retrieved_docs,
                        start=1
                    ):

                        st.markdown(
                            f"### Document {i}"
                        )

                        st.text(
                            doc
                        )

    st.session_state.messages.append(

        {
            "role": "assistant",
            "content": response
        }

    )