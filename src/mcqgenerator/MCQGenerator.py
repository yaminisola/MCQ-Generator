# -*- coding: utf-8 -*-
"""
MCQ Generator using LangChain 1.1.2 (Modern LCEL Syntax)
"""

import os
import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

class MCQGenerator:
    """Generate Multiple Choice Questions using LangChain and Groq"""
    
    def __init__(self, api_key, model="llama-3.3-70b-versatile"):
        """Initialize the MCQ Generator with Groq API key"""
        self.api_key = api_key
        self.llm = ChatGroq(
            model=model,  # Using llama-3.3-70b-versatile (latest supported model)
            temperature=0.3,
            groq_api_key=api_key
        )
    
    def generate_evaluate_chain(self, text, number, subject, tone, response_json):
        """
        Generate and evaluate MCQs from the given text
        
        Args:
            text: Source text to generate questions from
            number: Number of MCQs to generate
            subject: Subject/topic of the questions
            tone: Difficulty level (Easy, Medium, Hard)
            response_json: JSON template for response format
            
        Returns:
            dict: Contains 'quiz' and 'review' keys with generated content
        """
        
        # Quiz generation prompt
        quiz_generation_prompt = PromptTemplate(
            input_variables=["text", "number", "subject", "tone", "response_json"],
            template="""
Text: {text}
You are an expert MCQ maker. Given the above text, create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming to the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide. Ensure to make {number} MCQs.

### RESPONSE_JSON
{response_json}

Your response should be a valid JSON object with the same structure as RESPONSE_JSON.
"""
        )
        
        # Quiz evaluation prompt
        quiz_evaluation_prompt = PromptTemplate(
            input_variables=["subject", "quiz"],
            template="""
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students,
evaluate the complexity of the questions and provide a complete analysis. Use at most 50 words for the complexity analysis.

### QUIZ:
{quiz}

### ANALYSIS:
"""
        )
        
        # Build the chains using LCEL (pipe operator)
        output_parser = StrOutputParser()
        
        # First chain: Generate quiz
        quiz_chain = quiz_generation_prompt | self.llm | output_parser
        
        # Generate the quiz
        quiz_output = quiz_chain.invoke({
            "text": text,
            "number": number,
            "subject": subject,
            "tone": tone,
            "response_json": response_json
        })
        
        # Second chain: Evaluate quiz
        review_chain = quiz_evaluation_prompt | self.llm | output_parser
        
        # Evaluate the quiz
        review_output = review_chain.invoke({
            "subject": subject,
            "quiz": quiz_output
        })
        
        return {
            "quiz": quiz_output,
            "review": review_output
        }
    
    def get_table_data(self, quiz_str):
        """
        Parse the quiz string into a structured dictionary
        
        Args:
            quiz_str: String containing the quiz in JSON format
            
        Returns:
            dict: Parsed quiz data or None if parsing fails
        """
        try:
            # Clean the string - remove markdown code blocks if present
            quiz_str = quiz_str.strip()
            
            # Remove markdown code block markers
            if quiz_str.startswith("```json"):
                quiz_str = quiz_str[7:]
            if quiz_str.startswith("```"):
                quiz_str = quiz_str[3:]
            if quiz_str.endswith("```"):
                quiz_str = quiz_str[:-3]
            
            quiz_str = quiz_str.strip()
            
            # Try to find JSON object in the string
            json_match = re.search(r'\{.*\}', quiz_str, re.DOTALL)
            if json_match:
                quiz_str = json_match.group(0)
            
            # Parse JSON
            quiz_dict = json.loads(quiz_str)
            return quiz_dict
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"Error parsing quiz data: {e}")
            return None


# Standalone functions for functional programming style
def generate_evaluate_chain(text, number, subject, tone, response_json, api_key):
    """
    Generate and evaluate MCQs (functional approach)
    """
    generator = MCQGenerator(api_key)
    return generator.generate_evaluate_chain(text, number, subject, tone, response_json)


def get_table_data(quiz_str):
    """
    Parse quiz string into structured data (functional approach)
    """
    generator = MCQGenerator("")  # Dummy instance for parsing
    return generator.get_table_data(quiz_str)
