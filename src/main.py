import streamlit as st

st.title("🎉 Hello World")
st.header("Welcome to Streamlit!")

st.write("This is a simple web app built with Python.")

name = st.text_input("What's your name?")
if name:
    st.write(f"Hello, {name}!")

st.button("Click me!")
