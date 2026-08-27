import json
import ollama

from config import (
    OLLAMA_MODEL,
    OLLAMA_HOST,
)


class SecurityGuard:

    def __init__(self):

        self.client = ollama.Client(
            host=OLLAMA_HOST
        )

    def classify(self, question):
        """
        Analyze the user's intent.

        The guard does NOT answer the question.

        It determines whether the request is:

            ALLOW
            DENY_SENSITIVE
            DENY_CODE
            UNCERTAIN

        UNCERTAIN is treated as denied.
        """

        system_prompt = """
You are the policy and security guard for a private
company AI assistant.

Your ONLY job is to analyze the user's REQUEST and
determine what the user is trying to obtain.

DO NOT answer the user's question.

Use your intelligence to understand the meaning,
intent, wording, and context of the request.

Do NOT rely on keyword lists.

============================================================
POLICY 1 — SENSITIVE COMPANY INFORMATION
============================================================

Sensitive information includes information that an
ordinary employee should not receive unless explicitly
authorized.

Examples include, but are not limited to:

- confidential company financial information
- revenue, turnover, sales, profit, earnings
- company valuation or financial performance
- employee compensation and payroll
- employee or customer personal information
- bank account information
- passwords and credentials
- API keys, access tokens and secrets
- private security information
- confidential management or board information
- legal privileged information
- other confidential or restricted company information

The exact wording is irrelevant.

Judge the MEANING and PURPOSE of the request.

For example:

"What is our turnover?"
"How much money did we make?"
"How did the business perform?"
"What is the company worth?"

are all requests for potentially sensitive financial
information even though the wording is different.

============================================================
POLICY 2 — SOURCE CODE OUTPUT
============================================================

The company AI may READ, UNDERSTAND, ANALYZE and EXPLAIN
source-code files.

The company AI must NOT PROVIDE SOURCE CODE to employees.

This means:

ALLOW requests that ask to understand code, such as:

- explain what a program does
- explain a function
- explain an algorithm
- explain a class
- explain the architecture
- explain data flow
- explain why code behaves a certain way
- identify a possible bug
- describe an implementation concept

DENY requests whose purpose is to obtain executable or
reproducible source code, including requests to:

- provide source code
- show source code
- reproduce source code
- write an implementation
- generate a program
- recreate a function
- provide a code snippet
- paste the implementation
- convert the described algorithm into code
- modify existing code and return the modified code

Again, judge the INTENT rather than exact wording.

For example, these may all mean the same thing:

"Give me the Python implementation."
"How would I write this in C++?"
"Show me the actual function."
"Can you reproduce the code?"
"Give me a working version."

They should be classified as a source-code request.

============================================================
POLICY 3 — NORMAL QUESTIONS
============================================================

Normal project, technical, engineering and documentation
questions should be ALLOWED.

Examples:

"Explain this circuit."
"How does the algorithm work?"
"Why is the sensor behaving this way?"
"Explain the Python module."
"Compare these two designs."
"Summarize this document."

============================================================
IMPORTANT
============================================================

A request can be BOTH sensitive and a code request.

When that happens, classify it as the most restrictive
applicable category.

If the request is clearly sensitive:
    DENY_SENSITIVE

If the request is asking for source code:
    DENY_CODE

If the request is normal:
    ALLOW

If you cannot confidently determine the intent:
    UNCERTAIN

UNCERTAIN must not be allowed.

Return ONLY valid JSON.

Required format:

{
  "decision": "ALLOW",
  "category": "normal",
  "reason": "brief explanation"
}

Allowed decisions:

ALLOW
DENY_SENSITIVE
DENY_CODE
UNCERTAIN

Possible categories include:

normal
financial
personal_data
credentials
confidential
source_code
unknown

Do not output anything except JSON.
"""

        user_prompt = f"""
Employee request:

{question}
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

                # Security classification should be fast.
                think=False,

                options={
                    "temperature": 0,
                    "num_predict": 150,
                },

                stream=False,
            )

            raw = (
                response["message"]["content"]
                .strip()
            )

            result = json.loads(raw)

            decision = str(
                result.get(
                    "decision",
                    "UNCERTAIN"
                )
            ).upper()

            category = str(
                result.get(
                    "category",
                    "unknown"
                )
            )

            reason = str(
                result.get(
                    "reason",
                    ""
                )
            )

            if decision not in {
                "ALLOW",
                "DENY_SENSITIVE",
                "DENY_CODE",
                "UNCERTAIN",
            }:
                decision = "UNCERTAIN"

            return {
                "decision": decision,
                "category": category,
                "reason": reason,
            }

        except Exception as error:
            return {
                "decision": "UNCERTAIN",
                "category": "unknown",
                "reason": (
                    "The security guard could not "
                    "reliably classify this request."
                ),
            }