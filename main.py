from typing import Set

from backend.core import run_llm
import streamlit as st
from streamlit_chat import message

from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent
from third_parties.linkedin import scrape_linkedin_profile


def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string


st.header("RUN LLM Bot")
if (
    "chat_answers_history" not in st.session_state
    and "user_prompt_history" not in st.session_state
    and "chat_history" not in st.session_state
):
    st.session_state["chat_answers_history"] = []
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_history"] = []


prompt = st.text_input("Prompt", placeholder="Enter your message here...")

userLookup = st.text_input(
    "UserLookup", placeholder="Enter name to generate insights..."
)
name = userLookup

generalSearch = st.text_input("GenralSearch", placeholder="Enter your search here...")

if userLookup:
    with st.spinner("Generating response..."):
        linkedin_profile_url = linkedin_lookup_agent(name=name)
        linkedin_data = scrape_linkedin_profile(
            linkedin_profile_url=linkedin_profile_url
        )

        summary_template = """
         given the Linkedin information {linkedin_information} about a person from I want you to create:
         1. a short summary
         2. two interesting facts about them
         3. A topic that may interest them
         4. 2 creative Ice breakers to open a conversation with them 
        """
        summary_prompt_template = PromptTemplate(
            input_variables=["linkedin_information"],
            template=summary_template,
        )

        llm = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")
        chain = LLMChain(llm=llm, prompt=summary_prompt_template)

        generated_response = chain.run(linkedin_information=linkedin_data)

        st.session_state.chat_history.append((userLookup, generated_response))
        st.session_state.user_prompt_history.append(userLookup)
        st.session_state.chat_answers_history.append(generated_response)

if generalSearch:
    with st.spinner("Generating response..."):
       generated_response = run_llm(query=generalSearch, chat_history=st.session_state["chat_history"])
       
       st.session_state.chat_history.append((generalSearch, generated_response["answer"]))
       st.session_state.user_prompt_history.append(generalSearch)
       st.session_state.chat_answers_history.append(generated_response)

if prompt:
    with st.spinner("Generating response..."):
        generated_response = run_llm(
            query=prompt, chat_history=st.session_state["chat_history"]
        )

        sources = set(
            [doc.metadata["source"] for doc in generated_response["source_documents"]]
        )
        formatted_response = (
            f"{generated_response['answer']} \n\n {create_sources_string(sources)}"
        )

        st.session_state.chat_history.append((prompt, generated_response["answer"]))
        st.session_state.user_prompt_history.append(prompt)
        st.session_state.chat_answers_history.append(formatted_response)

if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(
        st.session_state["chat_answers_history"],
        st.session_state["user_prompt_history"],
    ):
        message(
            user_query,
            is_user=True,
        )
        message(generated_response)
