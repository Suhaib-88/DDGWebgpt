from pydantic import create_model
from src.utils.web_search import WebSearch
from langchain_google_genai import ChatGoogleGenerativeAI
import cohere
import json,os
from dotenv import find_dotenv,load_dotenv
from inspect import Parameter
import inspect
from typing import Dict,List, Any
# from langchain.agents import create

load_dotenv(find_dotenv())

class Apputils:
    @staticmethod
    def jsonschema(f) -> Dict:
        """
        Generate a JSON schema for the input parameters of the given function.

        Parameters:
            f (FunctionType): The function for which to generate the JSON schema.

        Returns:
            Dict: A dictionary containing the function name, description, and parameters schema.
        """
        # Replace inspect._empty with Any
        if not hasattr(f, '__name__'):
            raise ValueError(f"The object {f} does not have a '__name__' attribute.")
        
        kw = {n: (Any if o.annotation == inspect._empty else o.annotation, 
                ... if o.default == Parameter.empty else o.default)
            for n, o in inspect.signature(f).parameters.items()}
        
        # Create a custom Pydantic model with arbitrary types allowed
        class Config:
            arbitrary_types_allowed = True
        
        s = create_model(f'Input for `{f.__name__}`', **kw, __config__=Config).schema()
        return dict(name=f.__name__, description=f.__doc__, parameters=s)
    

    @staticmethod
    def wrap_functions():
        return [
            Apputils.jsonschema(WebSearch.retrieve_web_search_results),
            Apputils.jsonschema(WebSearch.web_search_text),
            Apputils.jsonschema(WebSearch.web_search_pdf),
            Apputils.jsonschema(WebSearch.web_search_image),
            Apputils.jsonschema(WebSearch.web_search_video),
            Apputils.jsonschema(WebSearch.web_search_news),
            Apputils.jsonschema(WebSearch.web_search_map)

        ]
    @staticmethod
    def execute_json_function(response):
        func_name=response.tool_calls[0].name
        print(func_name)
        func_args=response.tool_calls[0].parameters
        print(func_args)

        if func_name=="retrieve_web_search_results":
            result= WebSearch.retrieve_web_search_results(**func_args)
            print(f"res_search {result}")


        elif func_name=="web_search_text":
            result= WebSearch.web_search_text(**func_args)
            print(f"res_text {result}")

        
        elif func_name=="web_search_pdf":
            result= WebSearch.web_search_pdf(**func_args)
            print(f"res_pdf {result}")


        elif func_name=="web_search_image":
            result= WebSearch.web_search_image(**func_args)
            print(f"res_img {result}")

        
        elif func_name=="web_search_video":
            result= WebSearch.web_search_video(**func_args)
            print(f"res_vid {result}")

        
        elif func_name=="web_search_news":
            result= WebSearch.web_search_news(**func_args)

        elif func_name=="web_search_map":
            result= WebSearch.web_search_map(**func_args)
            print(f"res_map {result}")


        else:
            raise ValueError(f"Function: {func_name} not found")

        return result
    
    def ask_llm_func_caller(cohere_model,messages,tools,chat_history):
        co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
        response=co.chat(
                message=messages,
                model=cohere_model,
                tools=tools,
                chat_history=chat_history,
                force_single_step=True
            )

        
        return response


    @staticmethod
    def ask_llm_chatbot(gemini_model,messages):
        llm = ChatGoogleGenerativeAI(
            model=gemini_model,
            temperature=0,
        )
        ai_msg= llm.invoke(messages)
        return ai_msg