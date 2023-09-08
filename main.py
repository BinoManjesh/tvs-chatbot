import streamlit as st
from streamlit_chat import message
from model import get_response

st.set_page_config(
    page_title="Assistant",
    page_icon="🤖"
)
styl = f""" 
<style>
    .stTextInput {{
      position: fixed;
      bottom: 3rem;
    }}
</style>
"""
st.markdown("<h1 style='text-align: center;'>Welcome to TVS Credits Chatbot</h1>", unsafe_allow_html=True)
st.markdown(styl, unsafe_allow_html=True)
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
u=st.chat_input("Input Message: ")
if u:
    output=get_response(u)
    st.session_state.past.append(u)
    st.session_state.generated.append(output)
col1, temp,col2 = st.columns((2,8,2))
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][::-1][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][::-1][i], key=str(i))
