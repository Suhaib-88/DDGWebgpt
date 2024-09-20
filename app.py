import streamlit as st
from streamlit_chat import message
from PIL import Image
from src.utils.load_config import LoadConfig
from src.utils.app_utils import Apputils
from langchain.agents import AgentExecutor, create_tool_calling_agent

APPCFG = LoadConfig()

# ===================================
# Setting page title and header
# ===================================

st.set_page_config(
    page_title="WebGPT",
    layout="wide"
)
st.markdown("<h1 style='text-align: center;'>WebGPT</h1>", unsafe_allow_html=True)

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
if 'web_search_results' not in st.session_state:
    st.session_state['web_search_results'] = []

if 'web_search_video' not in st.session_state:
    st.session_state['web_search_video'] = []
if 'web_search_news' not in st.session_state: 
    st.session_state['web_search_news'] = []
# ==================================
# Sidebar:
# ==================================
counter_placeholder = st.sidebar.empty()
st.sidebar.title("WebGPT: GPT agent with access to the internet")
model_name = st.sidebar.radio("Choose a model:", ("Cohere", "Gemini"))
clear_button = st.sidebar.button("Clear Conversation", key="clear")

# ==================================
# Reset everything (Clear button)
# ==================================
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['model_name'] = []
    st.session_state['chat_history'] = []
    st.session_state['web_search_results'] = []
    st.session_state['web_search_video'] = []
    st.session_state['web_search_news'] = []



# ===================================
# Containers:
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

        first_llm_response = Apputils.ask_llm_func_caller(
            cohere_model=APPCFG.gpt_func_caller_model,
            messages=chat_history + query,
            tools=Apputils.wrap_functions(),
            chat_history=st.session_state['chat_history']
        )

        st.session_state['past'].append(user_input)
        if hasattr(first_llm_response, "tool_calls"):
            try:
                
                if first_llm_response.tool_calls[0].name=="web_search_video":
                    web_search_result = Apputils.execute_json_function(first_llm_response)
                    # Extract and store the YouTube video details
                    st.session_state['web_search_video'] = [
                        {
                            "title": result.get("title", ""),
                            "url": result.get("content", ""),  # Assuming 'content' is the video link
                            "description": result.get("description", ""),
                            "uploader": result.get("uploader", ""),
                            "published": result.get("published", "")
                        }
                        for result in web_search_result
                    ]
                    print("1",st.session_state['web_search_video'])



                elif first_llm_response.tool_calls[0].name=="web_search_news":
                    web_search_result = Apputils.execute_json_function(first_llm_response)
                    # Extract and store the web search results
                    st.session_state['web_search_news'] = [
                        {
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "image": result.get("image", ""),
                            "body": result.get("body", "")
                        }
                        for result in web_search_result
                    ]
                    

                web_search_result = Apputils.execute_json_function(first_llm_response)
                web_search_results = f"\n\n# Web search results:\n{str(web_search_result)}"
                messages = [
                    ("system", APPCFG.llm_system_role),
                    ("human", chat_history + web_search_results + query)
                ]
                
                second_llm_response = Apputils.ask_llm_chatbot(
                    gemini_model=APPCFG.gpt_model, messages=messages)
                st.session_state['generated'].append(second_llm_response.content)
                
                chat_history = {"role": 'User', "message": user_input}
                st.session_state['chat_history'].append(chat_history)
                
                chat_history = {"role": "Chatbot", "message": second_llm_response.content}
                st.session_state['chat_history'].append(chat_history)
                
            except Exception as e:
                print(e)
                st.session_state['generated'].append(
                    "An error occurred with the function calling, please try again later.")
                chat_history = str((f"User query: {user_input}", 
                                    "Response: An error occurred with function calling, please try again later."))
                st.session_state['chat_history'].append(chat_history)
                
        else:  # The first model used its own knowledge
            try:
                chat_history = {"role": 'User', "message": user_input}
                st.session_state['chat_history'].append(chat_history)
                
                chat_history = {"role": "Chatbot", "message": first_llm_response['text']}
                st.session_state['chat_history'].append(chat_history)
                
                st.session_state['generated'].append(first_llm_response['text'])
            except:
                st.session_state['generated'].append(
                    "An error occurred, please try again later.")
                chat_history = str((f"User query: {user_input}", 
                                    "Response: An error occurred, please try again later."))
                st.session_state['chat_history'].append(chat_history)



# Display the extracted web search results
if st.session_state['web_search_news']:
    with response_container:
        st.markdown("### Web Search News:")
        for result in st.session_state['web_search_results']:
            st.markdown(f"**Title:** {result['title']}")
            st.markdown(f"**URL:** [Link]({result['url']})")
            st.image(result['image'], use_column_width=True)
            st.markdown(f"**Summary:** {result['body']}")
            st.markdown("---")


if st.session_state['web_search_video']:
    print("2",st.session_state['web_search_video'])

    with response_container:
        st.markdown("### YouTube Video Details:")
        for result in st.session_state['web_search_results']:
            st.markdown(f"**Title:** {result['title']}")
            st.markdown(f"**URL:** [Watch Video]({result['url']})")
            st.markdown(f"**Description:** {result['description']}")
            st.markdown(f"**Uploader:** {result['uploader']}")
            st.markdown(f"**Published Date:** {result['published']}")
            st.markdown("---")


# Display the chat messages
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
