# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 19:53:42 2024

@author: gowtham.balachan
"""

import pandas as pd
import streamlit as st

class DataLoader:
    @st.cache_data
    def load_data(_self, file_path):
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            raise ValueError(f"Error loading data from {file_path}: {str(e)}")
