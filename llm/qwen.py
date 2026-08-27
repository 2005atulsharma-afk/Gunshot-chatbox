import ollama

from config import (
    OLLAMA_MODEL,
    OLLAMA_HOST,
)


class Qwen:

    def __init__(self):

        self.client = ollama.Client(
            host=OLLAMA_HOST
        )



    @staticmethod
    def should_think(question):

        question_lower = (
            question.lower().strip()
        )

        deep_keywords = [
            "explain in detail",
            "detailed explanation",
            "analyze",
            "analyse",
            "compare",
            "comparison",
            "why",
            "derive",
            "derivation",
            "step by step",
            "troubleshoot",
            "evaluate",
            "difference",
            "differences",
            "relationship",
            "prove",
            "calculate",
            "reason",
            "reasoning",
            "advantages",
            "disadvantages",
            "limitations",
            "working principle",
            "explain the working",
            "explain the operation",
        ]

        return any(
            keyword in question_lower
            for keyword in deep_keywords
        )


    def answer(
        self,
        question,
        retrieved_documents
    ):

        if not retrieved_documents:

            return {
                "answer": (
                    "I could not find relevant "
                    "information in the available "
                    "documents."
                ),
                "thinking": False,
                "sources": [],
            }



        context_parts = []

        for index, item in enumerate(
            retrieved_documents,
            start=1
        ):

            metadata = item.get(
                "metadata",
                {}
            )

            source = metadata.get(
                "source",
                "Unknown"
            )

            page = metadata.get(
                "page",
                ""
            )

            location = metadata.get(
                "location",
                ""
            )

            file_type = metadata.get(
                "file_type",
                ""
            )

            language = metadata.get(
                "language",
                ""
            )

            if page:

                location_text = (
                    f"Page {page}"
                )

            elif location:

                location_text = location

            else:

                location_text = (
                    "Unknown location"
                )

            extra = ""

            if file_type:
                extra += (
                    f"\nFile type: {file_type}"
                )

            if language:
                extra += (
                    f"\nLanguage: {language}"
                )

            context_parts.append(
                f"""
[S{index}]
Document: {source}
Location: {location_text}{extra}

{item["text"]}
"""
            )

        context = "\n".join(
            context_parts
        )



        think = self.should_think(
            question
        )

        if think:

            print(
                "\n🧠 Deep reasoning mode..."
            )

        else:

            print(
                "\n⚡ Fast mode..."
            )



        system_prompt = """
You are a private company technical assistant.

The supplied company documents and source-code
files are your PRIMARY source of information.

Your goal is to help employees understand projects,
systems, designs, documents, algorithms, and
source-code concepts clearly.

Use the information supplied from the documents
as the foundation of your answer.

You are encouraged to use your intelligence,
reasoning, and technical knowledge to:

- explain difficult concepts clearly
- simplify technical material
- summarize documents
- compare concepts
- connect related information
- explain why something works
- derive reasonable conclusions
- provide useful examples
- explain architecture and data flow
- explain algorithms
- analyze source-code logic
- explain functions, classes, modules, and systems
- identify possible bugs or design issues
- answer follow-up questions naturally

DOCUMENT-FIRST PRINCIPLES:

1. Give priority to the supplied documents.

2. Do not knowingly contradict information contained
   in the supplied documents.

3. You may use general knowledge to explain or clarify
   information from the documents.

4. Do not invent company-specific facts, numbers,
   specifications, policies, procedures, or other
   details.

5. If information in the documents is incomplete or
   ambiguous, acknowledge that.

6. Do not simply copy large portions of the documents.
   Understand and explain them.

CODE-SPECIFIC RULES:

7. Source-code files are knowledge sources only.

8. You may explain:
   - what the code does
   - how the code works
   - algorithms
   - architecture
   - data flow
   - relationships between functions/classes
   - possible bugs
   - implementation logic
   - design decisions

9. DO NOT output source code.

10. DO NOT generate new source code.

11. DO NOT provide replacement code.

12. DO NOT reproduce source code from the supplied
    files.

13. If the user asks for code, explain the concept,
    algorithm, architecture, or implementation approach
    in natural language instead.

14. Function names, class names, file names, variable
    names, and other identifiers may be mentioned when
    necessary, but do not reproduce the source code.

The goal is:

DOCUMENT KNOWLEDGE FIRST
+
MODEL INTELLIGENCE FOR EXPLANATION
+
NO SOURCE-CODE OUTPUT
=
A useful company technical assistant.
"""



        user_prompt = f"""
Relevant information retrieved from the company's
knowledge base:

{context}

Employee question:

{question}

Answer using the supplied information as the
PRIMARY source.

Use your intelligence to make the explanation
clear, accurate, and useful.

If the question concerns source code, explain
the code and its concepts, but DO NOT output code.
"""



        try:

            response = self.client.chat(

                model=OLLAMA_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],

                think=think,

                stream=False,
            )

        except Exception as error:

            return {
                "answer": (
                    "Error communicating with "
                    f"Qwen/Ollama: {error}"
                ),
                "thinking": think,
                "sources": [],
            }

        answer = (
            response["message"]["content"]
            .strip()
        )



        sources = []

        for index, item in enumerate(
            retrieved_documents,
            start=1
        ):

            metadata = item.get(
                "metadata",
                {}
            )

            source = metadata.get(
                "source",
                "Unknown"
            )

            page = metadata.get(
                "page",
                ""
            )

            location = metadata.get(
                "location",
                ""
            )

            if page:

                source_text = (
                    f"[S{index}] {source} "
                    f"(Page {page})"
                )

            elif location:

                source_text = (
                    f"[S{index}] {source} "
                    f"({location})"
                )

            else:

                source_text = (
                    f"[S{index}] {source}"
                )

            sources.append(
                source_text
            )

        return {
            "answer": answer,
            "thinking": think,
            "sources": sources,
        }