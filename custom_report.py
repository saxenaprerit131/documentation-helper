from typing import Set
import streamlit as st
import json
import pandas as pd

from langchain import OpenAI
from langchain.agents import create_pandas_dataframe_agent
from dotenv import load_dotenv
from agents.visualize_agent import visualize_agent

load_dotenv()

def csv_tool(filename : str):

    df = pd.read_csv(filename)
    return create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True)

def decode_response(response: str) -> dict:
    """This function converts the string response from the model to a dictionary object.

    Args:
        response (str): response from the model

    Returns:
        dict: dictionary with response data
    """
    return json.loads(response)


def write_answer(response_dict: dict):
    """
    Write a response from an agent to a Streamlit app.

    Args:
        response_dict: The response from the agent.

    Returns:
        None.
    """

    # Check if the response is an answer.
    if "answer" in response_dict:
        st.write(response_dict["answer"])

    # Check if the response is a bar chart.
    # Check if the response is a bar chart.
    if "bar" in response_dict:
        data = response_dict["bar"]
        try:
            df_data = {
                    col: [x[i] if isinstance(x, list) else x for x in data['data']]
                    for i, col in enumerate(data['columns'])
                }       
            df = pd.DataFrame(df_data)
            #df.set_index("Products", inplace=True)
            st.bar_chart(df)
        except ValueError:
            print(f"Couldn't create DataFrame from data: {data}")

# Check if the response is a line chart.
    if "line" in response_dict:
        data = response_dict["line"]
        try:
            df_data = {col: [x[i] for x in data['data']] for i, col in enumerate(data['columns'])}
            df = pd.DataFrame(df_data)
            #df.set_index("Products", inplace=True)
            st.line_chart(df)
        except ValueError:
            print(f"Couldn't create DataFrame from data: {data}")


    # Check if the response is a table.
    if "table" in response_dict:
        data = response_dict["table"]
        df = pd.DataFrame(data["data"], columns=data["columns"])
        st.table(df)

st.set_page_config(page_title="👨‍💻 Talk with your CSV")
st.title("👨‍💻 Talk with your CSV")

st.write("Please upload your CSV file below.")

data = st.file_uploader("Upload a CSV" , type="csv")

query = st.text_area("Send a Message")

if st.button("Submit Query", type="primary"):
    # Create an agent from the CSV file.
    agent = csv_tool(data)

    # Query the agent.
    response = visualize_agent(agent=agent, query=query)

    # Decode the response.
    decoded_response = decode_response(response)

    # Write the response to the Streamlit app.
    write_answer(decoded_response)