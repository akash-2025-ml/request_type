from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from prompt import prompt_1
import time

# Load models once (global)
print("Loading models...")

# Load tokenizer and model once
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small").to("cpu")
model.eval()  # no gradients needed

# Load Gemini model once
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    api_key="AIzaSyCpChkRD26kPW1u-tJJJkpBufJPWBfa4GQ",
)

print("Models loaded ✅")


# ----------- SUMMARY FUNCTION -----------
def summary(input_text):
    # Only tokenize and generate (no reload or compile)
    inputs = tokenizer(input_text, return_tensors="pt")
    with torch.no_grad():  # disable gradients for speed
        summary_ids = model.generate(inputs.input_ids, max_length=50, num_beams=3)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


# ----------- CLASSIFICATION FUNCTION -----------
def classification_email(email_text):
    t1 = time.time()

    # Summarize
    output = summary(email_text)

    # Gemini classification
    system_message = SystemMessage(content=prompt_1)
    human_message = HumanMessage(content=output)

    response = llm.invoke([system_message, human_message])

    t2 = time.time()
    print(f"Total time: {t2 - t1:.3f} seconds")

    return {"summary": output, "classification": response.content}


# ----------- TEST -----------
if __name__ == "__main__":
    email = """We need to send a wire transfer of $15,000 to our supplier in Singapore today 
    to avoid shipping delays. Please use the new account details provided in the attached document. 
    Confirm once the transfer is done."""

    start = time.time()
    result = classification_email(email)
    end = time.time()

    print(result)
    print(f"Overall time: {end - start:.3f} seconds")
