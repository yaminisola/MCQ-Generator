"""
Utility functions for MCQ Generator
"""

import os
import PyPDF2
import json
import traceback

def read_file(file):
    """Read file content"""
    if file.name.endswith(".pdf"):
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")
    
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception("Unsupported file format")


def get_table_data(quiz_str):
    """Convert quiz string to table data"""
    try:
        quiz_str = quiz_str.strip()
        if quiz_str.startswith("```json"):
            quiz_str = quiz_str[7:]
        if quiz_str.startswith("```"):
            quiz_str = quiz_str[3:]
        if quiz_str.endswith("```"):
            quiz_str = quiz_str[:-3]
        quiz_str = quiz_str.strip()
        
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []
        
        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " | ".join([
                f"{option}: {option_value}"
                for option, option_value in value["options"].items()
            ])
            correct = value["correct"]
            quiz_table_data.append({
                "MCQ": mcq,
                "Choices": options,
                "Correct": correct
            })
        
        return quiz_table_data
    
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False

