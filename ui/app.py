import sys, os

_this_file = os.path.abspath(__file__)
_ui_dir    = os.path.dirname(_this_file)
_fa_dir    = os.path.dirname(_ui_dir)

if _fa_dir not in sys.path:
    sys.path.insert(0, _fa_dir)

import streamlit as st
st.set_page_config(
    page_title="Exp Analysis",
    page_icon=":bar_chart:",
)
import pandas as pd
from controller import DBManager, Config, DataManager
from ui.show_conversation import show_conversation_page
from ui.show_data import show_data_page


def main(cfg_name: str = "default.yaml"):
    if 'cfg' not in st.session_state:
        cfg = Config.from_yaml(DataManager.normalize_config_name(cfg_name))
        # override dataset sang STAR vì default.yaml trỏ vào "sample" không tồn tại
        cfg.workflow_dataset = "STAR"
        st.session_state.cfg = cfg
        st.session_state.data_manager = DataManager(st.session_state.cfg)

    page = st.sidebar.selectbox("Select Page", ["📊 Data", "🔍 Conversation"])
    st.sidebar.markdown("---")

    if page == "🔍 Conversation":
        show_conversation_page()
    elif page == "📊 Data":
        show_data_page()


if __name__ == "__main__":
    main()