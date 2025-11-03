from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="moondream")

response = llm.invoke("What is LangChain?")
print(response)
