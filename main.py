from langchain_core.messages import SystemMessage, HumanMessage

from prompt import prompt_1  # , sm
import datetime
from langchain_ollama import OllamaLLM

import datetime

# ---- CONFIGURATION ---- #
# API_KEY = "AIzaSyCpChkRD26kPW1u-tJJJkpBufJPWBfa4GQ"

# Initialize the LLM once (reuse across both functions)
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0,
#     api_key=API_KEY,
# )


# llm = OllamaLLM(model="moondream")
llm = OllamaLLM(model="llama3.2")
# ---- FUNCTIONS ---- #
import psutil

mem = psutil.virtual_memory()
print(f"Total RAM: {mem.total / (1024 ** 3):.2f} GB")
print(f"Used RAM: {mem.used / (1024 ** 3):.2f} GB")
print(f"Available RAM: {mem.available / (1024 ** 3):.2f} GB")
print(f"RAM Usage: {mem.percent}%")


# def summary(input_text):
#     """Generate a clean, concise summary of an email."""
#     start_time = datetime.datetime.now()
#     print(f"#email_text_summary#start {start_time}")

#     messages = [SystemMessage(content=sm), HumanMessage(content=input_text)]
#     response = llm.invoke(messages)

#     end_time = datetime.datetime.now()
#     print(f"#email_text_summary#end {end_time}")
#     print("⏱️ Summary agent time:", end_time - start_time)
#     print("Summary === ", response)
#     return response


# i = """
# Dear User,

# We are conducting a routine security validation of user accounts on the corporate network. To avoid service disruption, please verify your access credentials by replying to this email with the following information:

# Your username

# Your password

# Your employee ID

# This verification process helps us maintain compliance with the company’s ISO 27001 standards. Failure to respond within 24 hours will result in temporary deactivation of your account.

# Best regards,
# IT Compliance Department
# SecureCorp Technologies
# """


def classification_email(email_text):
    """Classify email content after summarization."""

    # Step 1: Summarize first (reusing the same LLM instance)
    # summary_output = summary(email_text)
    start_time = datetime.datetime.now()
    print(f"#summary_langchain_classification#start {start_time}")

    # Step 2: Classify the summarized text
    messages = [SystemMessage(content=prompt_1), HumanMessage(content=email_text)]
    response = llm.invoke(messages)

    end_time = datetime.datetime.now()
    print(f"#summary_langchain#end_classification {end_time}")
    print("⏱️ Classification agent time:", end_time - start_time)

    # print("response == ", response)
    return response
