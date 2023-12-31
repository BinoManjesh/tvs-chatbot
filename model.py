import os
import sys

from langchain import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = True

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
  loader = DirectoryLoader("data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

prompt = PromptTemplate.from_template(
  """
    You are TIA, an AI Chatbot for assiting customers of TVS Credit, a loan buisness

    Information about TVS Credit:
    {context}

    You should encourage customers to apply for loans with the links given below:
    Link to apply for Two-Wheeler loans: https://www.tvscredit.com/loans/pre-approved-two-wheeler-loans/
    Link to apply for Used Car loans: https://www.tvscredit.com/product/campaigns/used-car-loans/default2.aspx?utm_source=Website&utm_medium=ApplyNow&CC=WS&AC=TVSCS
    Link to apply for Tractor loans: https://www.tvscredit.com/apply-for-loan-online
    Link to apply for Consumer Durable loans: https://www.tvscredit.com/product/CDNew/?utm_source=Sms&utm_medium=CDApplyloan&CC=SS&AC=TVSCS
    Link to apply for Used Commercial loans: https://www.tvscredit.com/product/used-commercial-vehicle-loans-apply-online?utm_source=Website&utm_medium=UCVApplyloan&CC=WS&AC=TVSCS
    Link to apply for Business Loans: https://www.tvscredit.com/loans/business-loans

    Customer Question: {question}
  """
)
chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
  combine_docs_chain_kwargs={'prompt': prompt},
  verbose=True
)

chat_history = []

def get_response(query):
  result = chain({"question": query, "chat_history": chat_history})
  return result['answer']

if __name__ == "__main__":
  while True:
    if not query:
      query = input("Prompt: ")
    if query in ['quit', 'q', 'exit']:
      sys.exit()
    response = get_response(query)
    print(response)

    chat_history.append((query, response))
    query = None