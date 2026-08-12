import os
from dotenv import load_dotenv

# Try to use the new Google GenAI API, fallback to legacy if needed
try:
    from google import genai
    from google.genai import types
    USE_NEW_API = True
except ImportError:
    import google.generativeai as genai
    USE_NEW_API = False

load_dotenv()


class LLMHandler:

    def __init__(self):

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "GEMINI_API_KEY not found in .env file"
            )

        if USE_NEW_API:
            # New Google GenAI API
            self.client = genai.Client(api_key=api_key)
            self.model_name = "gemini-2.5-flash"
        else:
            # Legacy API
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

    # ==========================================
    # QUESTION TYPE DETECTION
    # ==========================================

    def get_question_type(
        self,
        question
    ):

        question = question.lower()

        analysis_keywords = [

            "why",
            "recommend",
            "recommendation",
            "improve",
            "strategy",
            "insight",
            "analyze",
            "analysis",
            "root cause",
            "opportunity",
            "risk",
            "forecast"
        ]

        for keyword in analysis_keywords:

            if keyword in question:

                return "analysis"

        return "fact"

    # ==========================================
    # SUMMARY CONTEXT QA
    # ==========================================

    def ask_question(
        self,
        context,
        question
    ):

        question_type = (
            self.get_question_type(
                question
            )
        )

        if question_type == "fact":

            prompt = f"""
You are an AI Data Analyst.

Answer ONLY using the dataset context. Do not use any external knowledge or make assumptions.

DATASET CONTEXT

{context}

QUESTION

{question}

Rules:

1. Give a short direct answer based ONLY on the provided context.
2. If information is not available in the context, clearly say: "This information is not available in the dataset."
3. Do not provide recommendations unless asked.
4. Do not provide business interpretation unless asked.
5. Do not invent information, names, values, or columns that are not in the context.
6. If uncertain, state uncertainty rather than guessing.
"""

        else:

            prompt = f"""
You are a Senior Business Analyst.

Answer ONLY using the dataset context. Do not use any external knowledge or make assumptions.

DATASET CONTEXT

{context}

QUESTION

{question}

Rules:

1. Answer the question based ONLY on the provided context.
2. Explain the business meaning using only information from the context.
3. Give recommendations if relevant, based only on the context.
4. Do not invent information, names, values, or columns that are not in the context.
5. If information is unavailable in the context, clearly state it.
6. If uncertain, state uncertainty rather than guessing.
"""

        try:
            if USE_NEW_API:
                # New Google GenAI API
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            else:
                # Legacy API
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            return (
                f"Error generating response: "
                f"{str(e)}"
            )

    # ==========================================
    # RAG QA
    # ==========================================

    def ask_rag_question(
        self,
        retrieved_docs,
        question
    ):

        # Extract text content from retrieved documents
        if retrieved_docs and isinstance(retrieved_docs[0], dict) and 'text' in retrieved_docs[0]:
            doc_texts = [doc['text'] for doc in retrieved_docs]
        else:
            doc_texts = retrieved_docs

        context = "\n".join(
            doc_texts
        )

        question_type = (
            self.get_question_type(
                question
            )
        )

        if question_type == "fact":

            prompt = f"""
You are an AI Data Analyst.

Use ONLY the retrieved records. Do not use any external knowledge or make assumptions.

RETRIEVED RECORDS

{context}

QUESTION

{question}

Rules:

1. Answer directly based ONLY on the provided records.
2. Be concise.
3. If the requested information does not exist in the records, say:
   "This information is not available in the dataset."
4. Never guess or invent information.
5. Never invent names, values, or columns that are not in the records.
6. Do not provide recommendations unless asked.
7. Do not provide business interpretation unless asked.

Examples:

Question:
How many employees are in Sales?

Answer:
25 employees are in the Sales department.

Question:
List employee names.

Answer:
This information is not available in the dataset because no employee name field exists.
"""

        else:

            prompt = f"""
You are a Senior Business Analyst.

Use ONLY the retrieved records. Do not use any external knowledge or make assumptions.

RETRIEVED RECORDS

{context}

QUESTION

{question}

Rules:

1. Answer the question based ONLY on the provided records.
2. Explain the business meaning using only information from the records.
3. Give recommendations if relevant, based only on the records.
4. Use only the retrieved records.
5. If information is unavailable in the records, clearly state it.
6. Do not invent information, names, values, or columns that are not in the records.
7. If uncertain, state uncertainty rather than guessing.
"""

        try:
            if USE_NEW_API:
                # New Google GenAI API
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            else:
                # Legacy API
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            return (
                f"Error generating RAG response: "
                f"{str(e)}"
            )

    # ==========================================
    # EXECUTIVE SUMMARY
    # ==========================================

    def summarize_dataset(
        self,
        context
    ):

        prompt = f"""
You are a Senior Business Analyst.

Create an executive summary based ONLY on the provided dataset context. Do not use any external knowledge or make assumptions.

DATASET CONTEXT

{context}

Provide:

1. Dataset Overview - factual description of the dataset
2. Key Findings - insights derived strictly from the data
3. Risks - potential issues or concerns evident in the data
4. Opportunities - potential areas for improvement or growth suggested by the data
5. Recommendations - actionable suggestions based only on the data

Important: Base all statements solely on the provided context. Do not invent information, statistics, or facts not present in the context.
"""

        try:
            if USE_NEW_API:
                # New Google GenAI API
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            else:
                # Legacy API
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            return (
                f"Error generating summary: "
                f"{str(e)}"
            )

    # ==========================================
    # BUSINESS ANALYSIS
    # ==========================================

    def analyze_business_problem(
        self,
        context,
        problem_statement
    ):

        prompt = f"""
You are a Business Strategy Consultant.

Analyze the business problem based ONLY on the provided dataset context. Do not use any external knowledge or make assumptions.

DATASET CONTEXT

{context}

BUSINESS PROBLEM

{problem_statement}

Provide:

1. Problem Analysis - analysis based only on the data
2. Root Cause - root causes evident in or suggested by the data
3. Impact - impacts that can be inferred from the data
4. Recommendations - actionable recommendations based only on the data
5. Next Actions - suggested next steps based on the data

Important: Base all statements solely on the provided context. Do not invent information, statistics, or facts not present in the context. If the data does not contain sufficient information to answer a section, state that the information is not available in the dataset.
"""

        try:
            if USE_NEW_API:
                # New Google GenAI API
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            else:
                # Legacy API
                response = self.model.generate_content(prompt)
                return response.text
        except Exception as e:
            return (
                f"Error generating analysis: "
                f"{str(e)}"
            )