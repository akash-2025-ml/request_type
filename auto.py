from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.llms import Ollama
from prompt import a1, a2  # , sm
import datetime

# from langchain_ollama import OllamaLLM

# llm = OllamaLLM(model="llama3.2")


llm = Ollama(
    base_url="http://207.180.193.215:11434",
    model="deepseek-r1",
)


def agent1(email_text):
    """Classify email content after summarization."""

    # Step 1: Summarize first (reusing the same LLM instance)
    # summary_output = summary(email_text)
    start_time = datetime.datetime.now()
    print(f"#summary_langchain_classification#start {start_time}")

    # Step 2: Classify the summarized text
    messages = [SystemMessage(content=a1), HumanMessage(content=email_text)]
    response = llm.invoke(messages)

    end_time = datetime.datetime.now()
    print(f"#summary_langchain#end_classification {end_time}")
    print("⏱️ Classification agent time:", end_time - start_time)

    # print("response == ", response)
    return response


# print(
#     agent1(
#         "Hi,Please join the project update meeting at 3:00 PM today. Details are in the calendar invite."
#     )
# )


def agent2(email_text):
    """Classify email content after summarization."""

    # Step 1: Summarize first (reusing the same LLM instance)
    # summary_output = summary(email_text)
    start_time = datetime.datetime.now()
    print(f"#summary_langchain_classification#start {start_time}")

    # Step 2: Classify the summarized text
    messages = [SystemMessage(content=a2), HumanMessage(content=email_text)]
    response = llm.invoke(messages)

    end_time = datetime.datetime.now()
    print(f"#summary_langchain#end_classification {end_time}")
    print("⏱️ Classification agent time:", end_time - start_time)

    # print("response == ", response)
    return response


def classify_email(email_text: str):
    # Step 1: Check if request is present
    presence_result = agent1(email_text)

    if presence_result == "none" or presence_result == "None":
        return "none"
    else:
        # Step 2: If request present, classify its type
        type_result = agent2(email_text)
        return type_result
