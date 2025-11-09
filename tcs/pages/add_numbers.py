import streamlit as st


def main():
    st.set_page_config(page_title="Add Two Numbers", page_icon="➕")
    st.title("Add Two Numbers")
    st.write("Enter two numbers and press Add to see the result.")

    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Number A", value=0.0, format="%.6f")
    with col2:
        b = st.number_input("Number B", value=0.0, format="%.6f")

    if st.button("Add"):
        result = a + b
        st.success(f"Result: {result}")
    else:
        st.info("Click Add to compute the sum.")
        st.info("This project is designed by Shrabani.")


if __name__ == "__main__":
    main()
