import streamlit as st
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from groq import Groq


def connectDatabase(username, port, host, password, database):
    mysql_uri = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
    st.session_state.db = SQLDatabase.from_uri(mysql_uri)


def runQuery(query):
    return st.session_state.db.run(query) if st.session_state.db else "Please connect to database"


def getDatabaseSchema():
    return st.session_state.db.get_table_info() if st.session_state.db else "Please connect to database"

llm = groq.ChatGroq(model="Llama-3.1-70b-Versatile", api_key="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")


def getQueryFromLLM(question):
    template = """below is the schema of MYSQL database, read the schema carefully about the table and column names. Also take care of table or column name case sensitivity.
    Finally answer user's question in the form of SQL query.

    {schema}

    please only provide the SQL query and nothing else

    for example:
    question: how many employees we have in database
    SQL query: SELECT COUNT(*) FROM  emp_info
    question: how many customers are from 東京都 in the database ?
    SQL query: SELECT COUNT(*) FROM customer WHERE customerpref='東京都'

    your turn :
    question: {question}
    SQL query :
    please only provide the SQL query and nothing else
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm

    response = chain.invoke({
        "question": question,
        "schema": getDatabaseSchema()
    })
    return response.content


def getResponseForQueryResult(question, query, result):
    template2 = """below is the schema of MYSQL database, read the schema carefully about the table and column names of each table.
    Also look into the conversation if available
    Finally write a response in natural language by looking into the conversation and result.

    {schema}

    Here are some example for you:
    question: how many employees we have in database
    SQL query: SELECT COUNT(*) FROM emp_info;
    Result : [(6,)]
    Response: There are 6 employees in the database.

    question: how many users we have in database
    SQL query: SELECT COUNT(*) FROM customer;
    Result : [(4,)]
    Response: There are 4 amazing users in the database.

    question: how many users above are from india we have in database
    SQL query: SELECT COUNT(*) FROM customer WHERE customerpref='東京都';
    Result : [(3,)]
    Response: There are 3 amazing users in the database.

    your turn to write response in natural language from the given result :
    question: {question}
    SQL query : {query}
    Result : {result}
    Response:
    """

    prompt2 = ChatPromptTemplate.from_template(template2)
    chain2 = prompt2 | llm

    response = chain2.invoke({
        "question": question,
        "schema": getDatabaseSchema(),
        "query": query,
        "result": result
    })

    return response.content


st.set_page_config(
    page_icon="🤖",
    page_title="Chat with MYSQL DB",
    layout="centered"
)

question = st.chat_input('Chat with your mysql database')

if "chat" not in st.session_state:
    st.session_state.chat = []

if question:
    if "db" not in st.session_state:
        st.error('Please connect database first.')
    else:
        st.session_state.chat.append({
            "role": "user",
            "content": question
        })

        query = getQueryFromLLM(question)
        print(query)
        result = runQuery(query)
        print(result)
        response = getResponseForQueryResult(question, query, result)
        st.session_state.chat.append({
            "role": "assistant",
            "content": response
        })

for chat in st.session_state.chat:
    st.chat_message(chat['role']).markdown(chat['content'])

with st.sidebar:
    st.title('Connect to database')
    st.text_input(label="Host", key="host", value="www.ryhintl.com")
    st.text_input(label="Port", key="port", value="36000")
    st.text_input(label="Username", key="username", value="smairuser")
    st.text_input(label="Password", key="password", value="smairuser", type="password")
    st.text_input(label="Database", key="database", value="smair")
    connectBtn = st.button("Connect")


if connectBtn:
    connectDatabase(
        username=st.session_state.username,
        port=st.session_state.port,
        host=st.session_state.host,
        password=st.session_state.password,
        database=st.session_state.database,
    )

    st.success("Database connected")
