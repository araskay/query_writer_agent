import streamlit as st
from backend import QueryWriter
from streamlit_chat import message
from sample_db.bike_store import BikeStoreDb

@st.cache_resource
def get_query_writer():
    '''
    Helper function to instantiate QueryWriter with duckdb.
    Used to cache the query writer.
    This is a workaround to avoid re-initializing the query writer on every rerun,
    which is causes a duckdb error, since duckdb enforces a single connection.
    '''
    return QueryWriter(BikeStoreDb().get_engine())

query_writer = get_query_writer()

st.title("Query Writer")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("How can I help?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_writer.generate_query(prompt)
            st.markdown('To answer this question, I will run the following SQL query:')
            st.markdown("```\n{}\n```".format(query_writer.response_parser(response)))
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "To answer this question, I will run the following SQL query:"
                }
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "```\n{}\n```".format(query_writer.response_parser(response))
                }
            )
            st.button('Looks good, run it!', on_click=click_button)

if st.session_state.clicked:
    st.session_state.clicked = False
    with st.chat_message("assistant"):
        response = st.session_state.messages[-1]["content"]
        st.markdown('Here are the results:')
        results = query_writer.run_query(response.replace('```', ''))
        st.markdown(results)          
        st.session_state.messages.append({"role": "assistant", "content": "Here are the results:"})
        st.session_state.messages.append({"role": "assistant", "content": results})
            
