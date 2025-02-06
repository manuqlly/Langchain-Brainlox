from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain_openai import ChatOpenAI  # Updated import
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

load_dotenv() 
app = Flask(__name__)
api = Api(app)

# Load embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# Initialize language model and QA chain
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4o-mini")
qa = RetrievalQA.from_chain_type(llm, retriever=vector_store.as_retriever())

class Chat(Resource):
    def post(self):
        data = request.get_json()
        query = data.get("query")
        if not query:
            return {"error": "No query provided"}, 400
        try:
            result = qa.invoke(query)  # Ensure invoke() is used instead of run()
            return {"response": result}, 200
        except Exception as e:
            return {"error": str(e)}, 500

api.add_resource(Chat, "/chat")

if __name__ == "__main__":
    app.run(debug=True)
