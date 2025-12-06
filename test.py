
# -*- coding: utf-8 -*-
"""
Testing script for MCQ Generator
"""

import os
import json
from src.mcqgenerator import MCQGenerator
from src.logger import logging

def test_mcq_generator():
    """Test the MCQ Generator"""
    
    # Load API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = input("Enter Groq API Key: ")
        if not api_key:
            print("ERROR: API Key is required!")
            return
    
    # Load sample text
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            print("ERROR: data.txt is empty!")
            return
        print(f"✓ Loaded text from data.txt ({len(text)} characters)")
    except FileNotFoundError:
        print("ERROR: data.txt not found!")
        print("Please create a data.txt file with sample text in the project folder.")
        return
    except Exception as e:
        print(f"ERROR reading data.txt: {e}")
        return
    
    # Load response template (with fallback)
    try:
        with open("Response.json", "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                raise ValueError("Response.json is empty")
            response_json = json.loads(content)
        print("✓ Loaded Response.json template")
    except FileNotFoundError:
        print("⚠ Response.json not found. Creating default template...")
        response_json = {
            "1": {
                "mcq": "sample question",
                "options": {
                    "a": "option 1",
                    "b": "option 2",
                    "c": "option 3",
                    "d": "option 4"
                },
                "correct": "a"
            }
        }
        # Save the default template
        try:
            with open("Response.json", "w", encoding="utf-8") as f:
                json.dump(response_json, f, indent=4)
            print("✓ Created default Response.json")
        except Exception as e:
            print(f"⚠ Could not create Response.json: {e}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in Response.json: {e}")
        print("Using default template instead...")
        response_json = {
            "1": {
                "mcq": "sample question",
                "options": {
                    "a": "option 1",
                    "b": "option 2",
                    "c": "option 3",
                    "d": "option 4"
                },
                "correct": "a"
            }
        }
    except Exception as e:
        print(f"ERROR loading Response.json: {e}")
        return
    
    # Initialize generator
    try:
        print("\n" + "="*70)
        print("Initializing MCQ Generator...")
        generator = MCQGenerator(api_key)
        print("✓ Generator initialized")
    except Exception as e:
        print(f"ERROR initializing generator: {e}")
        return
    
    # Generate MCQs
    try:
        print("\nGenerating MCQs...")
        print("This may take a few moments...")
        response = generator.generate_evaluate_chain(
            text=text,
            number=5,
            subject="Machine Learning",
            tone="Medium",
            response_json=json.dumps(response_json)
        )
        print("✓ MCQs generated successfully")
    except Exception as e:
        print(f"ERROR generating MCQs: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "="*70)
    print("QUIZ:")
    print("="*70)
    quiz_content = response.get("quiz", "")
    if quiz_content:
        print(quiz_content)
    else:
        print("No quiz generated")
    
    print("\n" + "="*70)
    print("REVIEW:")
    print("="*70)
    review_content = response.get("review", "")
    if review_content:
        print(review_content)
    else:
        print("No review generated")
    
    # Parse and display table
    try:
        quiz_data = generator.get_table_data(response.get("quiz", ""))
        if quiz_data:
            print("\n" + "="*70)
            print("PARSED QUESTIONS:")
            print("="*70)
            for i, (key, value) in enumerate(quiz_data.items(), 1):
                print(f"\nQuestion {i}:")
                print(f"Q: {value.get('mcq', 'N/A')}")
                options = value.get('options', {})
                for opt_key, opt_val in options.items():
                    print(f"  {opt_key}) {opt_val}")
                print(f"Correct: {value.get('correct', 'N/A')}")
        else:
            print("\n⚠ Could not parse quiz data into table format")
    except Exception as e:
        print(f"\n⚠ Error parsing quiz data: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)

if __name__ == "__main__":
    try:
        test_mcq_generator()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()