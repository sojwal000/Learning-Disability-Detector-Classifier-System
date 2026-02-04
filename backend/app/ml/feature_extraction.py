"""
Feature extraction for different test types
"""
import re
from typing import Dict, Any, Optional
import numpy as np

def extract_reading_features(test_data: Dict[str, Any], audio_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract features from reading test data
    Features include: reading speed, accuracy, common error patterns
    """
    text_provided = test_data.get("text_provided", "")
    text_read = test_data.get("text_read", "")
    time_taken = test_data.get("time_taken", 0)
    
    # Calculate basic metrics
    words_provided = len(text_provided.split())
    words_read = len(text_read.split())
    
    # Reading speed (words per minute)
    reading_speed = (words_read / max(time_taken, 1)) * 60 if time_taken > 0 else 0
    
    # Calculate errors using simple word-level comparison
    provided_words = text_provided.lower().split()
    read_words = text_read.lower().split()
    
    errors = 0
    substitutions = 0
    omissions = 0
    additions = 0
    
    # Simple error counting
    max_len = max(len(provided_words), len(read_words))
    for i in range(max_len):
        if i >= len(provided_words):
            additions += 1
            errors += 1
        elif i >= len(read_words):
            omissions += 1
            errors += 1
        elif provided_words[i] != read_words[i]:
            substitutions += 1
            errors += 1
    
    # Accuracy calculation
    accuracy = ((words_provided - errors) / max(words_provided, 1)) * 100
    accuracy = max(0, min(100, accuracy))
    
    # Error rate
    error_rate = (errors / max(words_provided, 1)) * 100
    
    # Check for specific dyslexia indicators
    reversed_letters = count_reversed_letters(text_provided, text_read)
    letter_confusions = count_letter_confusions(text_provided, text_read)
    
    features = {
        "words_provided": words_provided,
        "words_read": words_read,
        "reading_speed": round(reading_speed, 2),
        "accuracy": round(accuracy, 2),
        "score": round(accuracy, 2),
        "errors": errors,
        "error_rate": round(error_rate, 2),
        "substitutions": substitutions,
        "omissions": omissions,
        "additions": additions,
        "reversed_letters": reversed_letters,
        "letter_confusions": letter_confusions,
        "time_taken": time_taken
    }
    
    return features

def extract_writing_features(test_data: Dict[str, Any], handwriting_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract features from writing test data
    Features include: spelling errors, grammar issues, handwriting quality
    """
    text_written = test_data.get("text_written", "")
    prompt = test_data.get("prompt", "")
    time_taken = test_data.get("time_taken", 0)
    
    # Basic metrics
    word_count = len(text_written.split())
    char_count = len(text_written)
    sentence_count = len(re.split(r'[.!?]+', text_written)) - 1
    
    # Writing speed
    writing_speed = (word_count / max(time_taken, 1)) * 60 if time_taken > 0 else 0
    
    # Spelling and grammar analysis (simplified)
    spelling_errors = count_spelling_errors(text_written)
    grammar_errors = count_grammar_errors(text_written)
    capitalization_errors = count_capitalization_errors(text_written)
    punctuation_errors = count_punctuation_errors(text_written)
    
    # Total errors
    total_errors = spelling_errors + grammar_errors + capitalization_errors + punctuation_errors
    
    # Error rate
    error_rate = (total_errors / max(word_count, 1)) * 100
    
    # Accuracy score
    accuracy = max(0, 100 - error_rate)
    
    # Dysgraphia indicators
    letter_reversals = count_writing_reversals(text_written)
    inconsistent_spacing = analyze_spacing(text_written)
    letter_formation_issues = 0  # Would require image analysis
    
    features = {
        "word_count": word_count,
        "char_count": char_count,
        "sentence_count": sentence_count,
        "writing_speed": round(writing_speed, 2),
        "spelling_errors": spelling_errors,
        "grammar_errors": grammar_errors,
        "capitalization_errors": capitalization_errors,
        "punctuation_errors": punctuation_errors,
        "errors": total_errors,
        "error_rate": round(error_rate, 2),
        "accuracy": round(accuracy, 2),
        "score": round(accuracy, 2),
        "letter_reversals": letter_reversals,
        "inconsistent_spacing": inconsistent_spacing,
        "time_taken": time_taken
    }
    
    return features

def extract_math_features(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract features from math test data
    Features include: accuracy, error types, problem-solving approach
    """
    problems = test_data.get("problems", [])
    time_taken = test_data.get("time_taken", 0)
    
    total_problems = len(problems)
    correct_answers = 0
    calculation_errors = 0
    concept_errors = 0
    procedure_errors = 0
    number_reversals = 0
    
    for problem in problems:
        is_correct = problem.get("is_correct", False)
        error_type = problem.get("error_type", None)
        student_answer = str(problem.get("student_answer", ""))
        correct_answer = str(problem.get("correct_answer", ""))
        
        if is_correct:
            correct_answers += 1
        else:
            # Categorize error
            if error_type == "calculation":
                calculation_errors += 1
            elif error_type == "concept":
                concept_errors += 1
            elif error_type == "procedure":
                procedure_errors += 1
            
            # Check for number reversals (e.g., 21 instead of 12)
            if is_number_reversal(student_answer, correct_answer):
                number_reversals += 1
    
    # Calculate metrics
    accuracy = (correct_answers / max(total_problems, 1)) * 100
    error_count = total_problems - correct_answers
    
    # Problem-solving speed
    avg_time_per_problem = time_taken / max(total_problems, 1) if total_problems > 0 else 0
    
    features = {
        "total_problems": total_problems,
        "correct_answers": correct_answers,
        "accuracy": round(accuracy, 2),
        "score": round(accuracy, 2),
        "errors": error_count,
        "calculation_errors": calculation_errors,
        "concept_errors": concept_errors,
        "procedure_errors": procedure_errors,
        "number_reversals": number_reversals,
        "avg_time_per_problem": round(avg_time_per_problem, 2),
        "time_taken": time_taken
    }
    
    return features

# Helper functions

def count_reversed_letters(original: str, read: str) -> int:
    """Count common letter reversals (b/d, p/q, etc.)"""
    reversals = [('b', 'd'), ('p', 'q'), ('n', 'u'), ('m', 'w')]
    count = 0
    
    original_lower = original.lower()
    read_lower = read.lower()
    
    for i, char in enumerate(original_lower):
        if i < len(read_lower):
            for pair in reversals:
                if (char == pair[0] and read_lower[i] == pair[1]) or \
                   (char == pair[1] and read_lower[i] == pair[0]):
                    count += 1
    
    return count

def count_letter_confusions(original: str, read: str) -> int:
    """Count common letter confusions"""
    confusions = [('a', 'e'), ('i', 'e'), ('o', 'a'), ('u', 'o')]
    count = 0
    
    original_lower = original.lower()
    read_lower = read.lower()
    
    for i, char in enumerate(original_lower):
        if i < len(read_lower):
            for pair in confusions:
                if (char == pair[0] and read_lower[i] == pair[1]) or \
                   (char == pair[1] and read_lower[i] == pair[0]):
                    count += 1
    
    return count

def count_spelling_errors(text: str) -> int:
    """Simple spelling error detection (can be enhanced with spell checker)"""
    # For now, use a simple heuristic
    words = text.split()
    errors = 0
    
    for word in words:
        # Check for obvious issues
        if len(word) > 2 and word.lower() == word.lower()[::-1]:  # Palindrome check
            continue
        if re.search(r'(.)\1{3,}', word):  # Repeated letters
            errors += 1
    
    return errors

def count_grammar_errors(text: str) -> int:
    """Simple grammar error detection"""
    errors = 0
    
    # Check for missing spaces after punctuation
    if re.search(r'[.!?,][a-zA-Z]', text):
        errors += 1
    
    # Check for double spaces
    if '  ' in text:
        errors += 1
    
    return errors

def count_capitalization_errors(text: str) -> int:
    """Check capitalization errors"""
    errors = 0
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence[0].islower():
            errors += 1
    
    return errors

def count_punctuation_errors(text: str) -> int:
    """Check punctuation errors"""
    errors = 0
    
    # Check for missing end punctuation
    if text and text[-1] not in '.!?':
        errors += 1
    
    return errors

def count_writing_reversals(text: str) -> int:
    """Count letter reversals in writing"""
    return count_reversed_letters(text, text)

def analyze_spacing(text: str) -> int:
    """Analyze spacing inconsistencies"""
    spaces = re.findall(r' +', text)
    if not spaces:
        return 0
    
    # Check for varying space lengths
    space_lengths = [len(s) for s in spaces]
    if len(set(space_lengths)) > 1:
        return 1
    
    return 0

def is_number_reversal(student: str, correct: str) -> bool:
    """Check if student answer is a reversal of correct answer"""
    student_digits = ''.join(filter(str.isdigit, student))
    correct_digits = ''.join(filter(str.isdigit, correct))
    
    if len(student_digits) == len(correct_digits) and len(student_digits) > 0:
        return student_digits == correct_digits[::-1]
    
    return False
