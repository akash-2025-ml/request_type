from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.llms import Ollama
from prompt import a1, a2  # , sm
import datetime

# from langchain_ollama import OllamaLLM

# llm = OllamaLLM(model="llama3.2")


# Qa server ip = base_url="http://207.180.193.215:11434"
# mistral:7b-instruct #"http://13.233.69.94:11434"
llm = Ollama(
    base_url="http://13.233.69.94:11434",
    model="qwen2.5:3b-instruct",
    temperature=0.0,
    top_p=0.05,
    num_predict=3,
)
llm.invoke("warmup")


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
    print("⏱️ Classification agent 1 time:", end_time - start_time)

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
    # start_time = datetime.datetime.now()
    # print(f"#summary_langchain_classification#start {start_time}")

    # Step 2: Classify the summarized text
    # messages = [SystemMessage(content=a2), HumanMessage(content=email_text)]
    flat_prompt = f"""{a2}

                    EMAIL:
                    {email_text}
                    """
    response = llm.invoke(flat_prompt)

    # end_time = datetime.datetime.now()
    # print(f"#summary_langchain#end_classification {end_time}")
    # print("⏱️ Classification agent 2 time:", end_time - start_time)

    # print("response == ", response)
    return response


def classify_email(email_text: str):
    # Step 1: Check if request is present
    # presence_result = agent1(email_text)

    # if presence_result == "none" or presence_result == "None":
    #     return "none"
    # else:
    #     # Step 2: If request present, classify its type
    type_result = agent2(email_text)
    return type_result


# print(
#     agent2(
#         """Hello Team,

# I hope you are doing well.

# This email is to request the required content needed to proceed with the next steps of our work. Kindly share the content along with any relevant details or supporting information at your convenience.

# If you need any clarification from my side, please feel free to reach out. Your timely support would be greatly appreciated.

# Best regards,
# Akash"""
#     )
# )


# def classify_email(email_text: str):
#     presence_result = agent1(email_text)

#     if presence_result in ["none", "no", "no request", "not present"]:
#         return "none"
#     else:
#         type_result = agent2(email_text)
#         return type_result
# # presence_result = agent2("i want your email crediensial")
# # print(presence_result)

# print(
#     agent2(
#         """Hello Meera,

# I hope you’re doing well. I’m applying for the internal Data Lead position opening this quarter and would be grateful if you could provide a professional reference highlighting my contributions during the ModelOps initiative.

# You were my reporting manager during that project, so your recommendation would mean a lot.

# Thanks in advance,
# Aditya Sharma
# """
#     )
# )

# print(
#     agent2(
#         """hello i am akash"""
#     )
# )
