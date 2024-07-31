import logging

class FeatureTranslationError(Exception):
    def __init__(self, feature_name, context, message):
        self.feature_name = feature_name
        self.context  = context
        self.message = message

    # Define __str__ method to return the error message.
    def __str__(self) -> str:
        error_msg = f"{self.__class__.__name__}: Feature '{self.feature_name}' not found: {self.context}\n"
        return error_msg
    
    
