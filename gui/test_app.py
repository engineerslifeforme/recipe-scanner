import sqlite3
from typing import Optional

import streamlit as st
import yaml
from pydantic import BaseModel
from bs4 import BeautifulSoup

from database import database_connect

con = database_connect()

class TestCls(BaseModel):
    name: Optional[str] = "default"

st.markdown("test")
yaml.safe_load("a:1")
thing = TestCls()
soup = BeautifulSoup("<html><h1>Hello</h1></html>", "html.parser")