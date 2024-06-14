# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 20:53:14 2024

@author: gowtham.balachan
"""

import pandas as pd

class RecipeMatcher:
    def __init__(self, df):
        self.df = df

    def get_closest_matches(self, ingredients):
        try:
            if 'RecipeIngredientParts' not in self.df.columns:
                raise ValueError("DataFrame column 'RecipeIngredientParts' not found.")
            
            # Ensure 'RecipeIngredientParts' is converted to string type and handle potential NaNs
            self.df['RecipeIngredientParts'] = self.df['RecipeIngredientParts'].astype(str).fillna('')
            
            # Split input ingredients into a set
            input_ingredients_set = set(map(str.strip, ingredients.lower().split(',')))

            def jaccard_similarity(row_ingredients):
                row_ingredients_set = set(map(str.strip, row_ingredients.lower().split(',')))
                intersection = len(input_ingredients_set.intersection(row_ingredients_set))
                union = len(input_ingredients_set.union(row_ingredients_set))
                return intersection / union if union != 0 else 0
            
            # Calculate Jaccard similarity for each recipe
            self.df['Similarity'] = self.df['RecipeIngredientParts'].apply(jaccard_similarity)

            # Get indices of top matches
            top_indices = self.df.nlargest(3, 'Similarity').index

            # Return top matched records
            return self.df.iloc[top_indices]
        
        except Exception as e:
            raise ValueError(f"Error in similarity calculation process: {str(e)}")
