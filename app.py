import streamlit as st
from streamlit_chat import message
from PIL import Image
from utils.load_config import LoadConfig
from utils.app_utils import Apputils

AppCfg= LoadConfig()

st.set_page_confgi(page_title="GPT web browser",layout='wide')

st.markdown("GPT Browsing")

if 'generated' not in st.session_state:
    st.session_state['generated']=[]
if 'chat_history' not in st.session_state:
    st.session_state['chat_history']=[]

if 'past' not in st.session_state:
    st.session_state['past']=[]
if 'model_name' not in st.session_state:
    st.session_state['model_name']=[]



counter_placejholder=st.sidebar.empty()
model_name= st.sidebar.radio('chose a model',("Groq", "Gemini"))
clear_button= st.sidebar.button("Clear conversation",key= 'clear')

if clear_button:
    st.session_state['generated']=[]
    st.session_state['chat_history']=[]
    st.session_state['past']=[]
    st.session_state['model_name']=[]



response_container=st.container()
container= st.container()

container.markdown("Containse",unsafe_allow_html=True)

with container:
    with st.form(key='my_form',clear_on_submit=True):
        user_input = st.text_area("Enter your message", height=100)
        submit_button= st.form_submit_button(label="submit")
    
    if submit_button and user_input:
        chat_history=f"Chat history:{st.session_state['chat_history'][-2:]}"

        query=f"User new question {user_input}"
        messages=[{'role':"system", "content": str(AppCfg.llm_function_caller_sys_role)}, {'role':"user","content": chat_history + query}]

        print(messages)

        first_llm_response=Apputils.ask_llm_func_caller(gpt_model=AppCfg.gpt_model,temperature= AppCfg.temperature,messages=messages,function_json_list= Apputils.wrap_functions())

        st.session_state["past"].append(user_input)

        if "function_call" in first_llm_response.choices[0].message.keys():
            try:
                print("Called function:",
                      first_llm_response.choices[0].message.function_call.name)

                web_search_result = Apputils.execute_json_function(
                    first_llm_response)
                web_search_results = f"\n\n# Web search results:\n{str(web_search_result)}"
                messages = [
                    {"role": "system", "content": AppCfg.llm_system_role},
                    {"role": "user", "content": chat_history +
                        web_search_results + query}
                ]
                print(messages)
                print(web_search_results)
                second_llm_response = Apputils.ask_llm_chatbot(
                    AppCfg.gpt_model, AppCfg.temperature, messages)
                st.session_state['generated'].append(
                    second_llm_response["choices"][0]["message"]["content"])
                chat_history = (
                    f"## User query: {user_input}", f"## Response: {second_llm_response['choices'][0]['message']['content']}")
                st.session_state['chat_history'].append(chat_history)

            except Exception as e:
                st.session_state['generated'].append(
                    "An error occured, please try again later.")
                chat_history = str(
                    (f"User query: {user_input}", f"Response: An error occured with function calling, please try again later."))
                st.session_state['generated'].append(chat_history)

    else: 
        try:
            chat_history=str((f"User query:{user_input}",f"Response:{first_llm_response['choices'][0]['message']['content']}"))
            st.session_state['generated'].append(chat_history)
            st.session_state['generated'].append(first_llm_response['choices'][0]['message']['content'])

        except Exception as e:
            st.session_state['generated'].append("An error occured, please try again later.")
            chat_history = str(
                    (f"User query: {user_input}", f"Response: An error occured with function calling, please try again later."))
            st.session_state['generated'].append(chat_history)

if st.session_state["generated"]:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True,key= str(i)+'user')

            message(st.session_state['generated'][i], key=str(i))