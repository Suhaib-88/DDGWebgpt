import streamlit as st
from streamlit_chat import message
from PIL import Image
from src.utils.load_config import LoadConfig
from src.utils.app_utils import Apputils

APPCFG = LoadConfig()

# ===================================
# Setting page title and header
# ===================================


st.set_page_config(
    page_title="WebGPT",
    layout="wide"
)
st.markdown("<h1 style='text-align: center;'>WebGPT</h1>",
            unsafe_allow_html=True)
# ===================================
# Initialise session state variables
# ===================================
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []
# ==================================
# Sidebar:
# ==================================
counter_placeholder = st.sidebar.empty()
st.sidebar.title(
    "WebGPT: GPT agent with access to the internet")
# st.sidebar.image("images/AI_RT.png", use_column_width=True)
model_name = st.sidebar.radio("Choose a model:",("Cohere", "Gemini"))
clear_button = st.sidebar.button("Clear Conversation", key="clear")
# ==================================
# Reset everything (Clear button)
# ==================================
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['model_name'] = []
    st.session_state['chat_history'] = []
# ===================================
# containers:
# ===================================
response_container = st.container()  # for chat history
container = st.container()  # for text box
container.markdown("""
    <style>
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 10px;
            background-color: #f5f5f5;
            border-top: 1px solid #ddd;
        }
    </style>
""", unsafe_allow_html=True)

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input')
        submit_button = st.form_submit_button(label='Submit')

    if submit_button and user_input:
        # Simplify: Only keep two chat history
        chat_history = f"# Chat history:\n{st.session_state['chat_history'][-2:]}\n\n"
        query = f"# User new question:\n {user_input}"
        messages = [
            {"role": "system", "content": str(
                APPCFG.llm_system_role)},
            {"role": "user", "content": chat_history + query}
        ]
        print(messages)
        first_llm_response = Apputils.ask_llm_func_caller(
            cohere_model=APPCFG.gpt_model, messages=query, tools=Apputils.wrap_functions(),chat_history=st.session_state['chat_history'])
        print(first_llm_response,file=open('writer.txt','w'))
        st.session_state['past'].append(user_input)
        if hasattr(first_llm_response,"tool_calls"):
            try:
                print("Called function:",
                      first_llm_response.tool_calls[0].name)

                web_search_result = Apputils.execute_json_function(
                    first_llm_response)
                web_search_results = f"\n\n# Web search results:\n{str(web_search_result)}"
                messages = [
                    {"role": "system", "content": APPCFG.llm_system_role},
                    {"role": "user", "content": chat_history +
                        web_search_results + query}
                ]
                print(messages)
                print(web_search_results)
                second_llm_response = Apputils.ask_llm_chatbot(
                    APPCFG.gpt_model, APPCFG.temperature, messages)
                st.session_state['generated'].append(
                    second_llm_response["choices"][0]["message"]["content"])
                chat_history = (
                    f"## User query: {user_input}", f"## Response: {second_llm_response['choices'][0]['message']['content']}")
                st.session_state['chat_history'].append(chat_history)
            except Exception as e:
                print(e)
                st.session_state['generated'].append(
                    "An error occured with the function calling, please try again later.")
                chat_history = str(
                    (f"User query: {user_input}", f"Response: An error occured with function calling, please try again later."))
                st.session_state['chat_history'].append(chat_history)

        else:  # The first model used its own knowledge
            try:
                chat_history = str(
                    (f"User query: {user_input}", f"Response: {first_llm_response['choices'][0]['message']['content']}"))
                st.session_state['chat_history'].append(chat_history)
                st.session_state['generated'].append(
                    first_llm_response["choices"][0]["message"]["content"])
            except:
                st.session_state['generated'].append(
                    "An error occured, please try again later.")
                chat_history = str(
                    (f"User query: {user_input}", f"Response: An error occured, please try again later."))
                st.session_state['chat_history'].append(chat_history)


if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i],
                    is_user=True,
                    key=str(i) + '_user',
                    # avatar_style=str(here("images/openai.png"))
                    )
            message(st.session_state["generated"][i],
                    key=str(i),
                    # avatar_style=str(here("images/AI_RT.png")),
                    )