"""
Report generation utilities
"""
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import json

from app.models import Student, TestResult, MLPrediction, Report

def generate_student_report(student_id: int, db: Session) -> Report:
    """
    Generate a comprehensive learning disability report for a student
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError("Student not found")
    
    # Get all test results
    test_results = db.query(TestResult).filter(TestResult.student_id == student_id).all()
    
    # Get all ML predictions
    predictions = db.query(MLPrediction).join(TestResult).filter(
        TestResult.student_id == student_id
    ).all()
    
    # Analyze results
    classification, risk_score, indicators = analyze_predictions(predictions, test_results)
    
    # Generate recommendations
    recommendations = generate_recommendations(classification, indicators)
    
    # Create report record
    report = Report(
        student_id=student_id,
        report_type="comprehensive",
        classification=classification,
        risk_score=risk_score,
        indicators=indicators,
        recommendations=recommendations
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Generate PDF (simplified - would use reportlab or similar)
    report_path = generate_pdf_report(student, report, test_results, predictions)
    report.report_path = report_path
    
    db.commit()
    db.refresh(report)
    
    return report

def analyze_predictions(predictions: list, test_results: list) -> tuple:
    """
    Analyze ML predictions to determine overall classification and risk
    """
    if not predictions:
        return "No assessment", 0.0, []
    
    # Count predictions by category
    category_counts = {
        "dyslexia": 0,
        "dysgraphia": 0,
        "dyscalculia": 0,
        "none": 0
    }
    
    category_confidence = {
        "dyslexia": [],
        "dysgraphia": [],
        "dyscalculia": [],
    }
    
    risk_levels = {
        "dyslexia": "low",
        "dysgraphia": "low",
        "dyscalculia": "low"
    }
    
    for pred in predictions:
        if pred.prediction_class in category_counts:
            category_counts[pred.prediction_class] += 1
            
            if pred.prediction_class != "none":
                category_confidence[pred.prediction_class].append(pred.confidence_score)
                
                # Track highest risk level
                risk_order = {"low": 1, "medium": 2, "high": 3}
                current_risk = risk_order.get(risk_levels[pred.prediction_class], 0)
                new_risk = risk_order.get(pred.risk_level, 0)
                
                if new_risk > current_risk:
                    risk_levels[pred.prediction_class] = pred.risk_level
    
    # Determine primary classification
    categories_with_predictions = {k: v for k, v in category_counts.items() if k != "none" and v > 0}
    
    if not categories_with_predictions:
        classification = "No learning disability detected"
        overall_risk_score = 0.0
    elif len(categories_with_predictions) == 1:
        classification = list(categories_with_predictions.keys())[0].capitalize()
        category = list(categories_with_predictions.keys())[0]
        overall_risk_score = sum(category_confidence[category]) / len(category_confidence[category]) if category_confidence[category] else 0
    else:
        # Multiple categories detected
        classification = "Multiple indicators: " + ", ".join([k.capitalize() for k in categories_with_predictions.keys()])
        all_confidences = []
        for cat in categories_with_predictions.keys():
            all_confidences.extend(category_confidence[cat])
        overall_risk_score = sum(all_confidences) / len(all_confidences) if all_confidences else 0
    
    # Build indicators list
    indicators = []
    
    for category, count in categories_with_predictions.items():
        avg_confidence = sum(category_confidence[category]) / len(category_confidence[category]) if category_confidence[category] else 0
        
        indicators.append({
            "category": category,
            "occurrences": count,
            "avg_confidence": round(avg_confidence, 3),
            "risk_level": risk_levels[category],
            "description": get_category_description(category, risk_levels[category])
        })
    
    return classification, round(overall_risk_score, 3), indicators

def get_category_description(category: str, risk_level: str) -> str:
    """Get description for a learning disability category"""
    descriptions = {
        "dyslexia": {
            "low": "Mild reading difficulties observed",
            "medium": "Moderate reading and word recognition challenges",
            "high": "Significant difficulties with reading, spelling, and phonological processing"
        },
        "dysgraphia": {
            "low": "Minor writing coordination issues",
            "medium": "Notable challenges with handwriting and written expression",
            "high": "Severe difficulties with writing, spelling, and fine motor coordination"
        },
        "dyscalculia": {
            "low": "Some difficulty with basic math concepts",
            "medium": "Moderate challenges with numerical operations and math reasoning",
            "high": "Significant struggles with number sense, calculations, and math concepts"
        }
    }
    
    return descriptions.get(category, {}).get(risk_level, "Indicators detected")

def generate_recommendations(classification: str, indicators: list) -> str:
    """
    Generate recommendations based on classification and indicators
    """
    recommendations = []
    
    # General recommendations
    recommendations.append("**General Recommendations:**")
    recommendations.append("- Schedule a comprehensive evaluation with a learning specialist")
    recommendations.append("- Consider one-on-one tutoring in areas of difficulty")
    recommendations.append("- Provide additional time for completing tasks")
    recommendations.append("")
    
    # Specific recommendations based on indicators
    for indicator in indicators:
        category = indicator["category"]
        risk_level = indicator["risk_level"]
        
        recommendations.append(f"**{category.capitalize()} Support:**")
        
        if category == "dyslexia":
            recommendations.append("- Implement multisensory reading programs (e.g., Orton-Gillingham)")
            recommendations.append("- Use audiobooks and text-to-speech technology")
            recommendations.append("- Practice phonemic awareness exercises")
            recommendations.append("- Break reading tasks into smaller segments")
            
            if risk_level in ["medium", "high"]:
                recommendations.append("- Consider specialized dyslexia intervention programs")
                recommendations.append("- Use colored overlays or specialized fonts")
        
        elif category == "dysgraphia":
            recommendations.append("- Allow use of computers for written work")
            recommendations.append("- Provide graph paper for math and writing alignment")
            recommendations.append("- Practice fine motor skills and occupational therapy")
            recommendations.append("- Accept oral responses in place of written work when appropriate")
            
            if risk_level in ["medium", "high"]:
                recommendations.append("- Use speech-to-text software")
                recommendations.append("- Reduce writing requirements, focus on quality over quantity")
        
        elif category == "dyscalculia":
            recommendations.append("- Use manipulatives and visual aids for math concepts")
            recommendations.append("- Allow use of calculators for complex operations")
            recommendations.append("- Break down math problems into step-by-step procedures")
            recommendations.append("- Provide extra practice with number lines and counting")
            
            if risk_level in ["medium", "high"]:
                recommendations.append("- Work with a math specialist or tutor")
                recommendations.append("- Use concrete examples to teach abstract concepts")
        
        recommendations.append("")
    
    # Classroom accommodations
    recommendations.append("**Classroom Accommodations:**")
    recommendations.append("- Preferential seating near the teacher")
    recommendations.append("- Extended time on tests and assignments")
    recommendations.append("- Provide written instructions along with verbal")
    recommendations.append("- Allow breaks during longer tasks")
    recommendations.append("- Use positive reinforcement and encouragement")
    
    return "\n".join(recommendations)

def generate_pdf_report(student: Student, report: Report, test_results: list, predictions: list) -> str:
    """
    Generate a PDF report (simplified version - would use reportlab)
    For now, creates a text file
    """
    storage_path = Path("storage/reports")
    storage_path.mkdir(parents=True, exist_ok=True)
    
    filename = f"report_{report.id}_{student.id}_{datetime.now().strftime('%Y%m%d')}.txt"
    filepath = storage_path / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("LEARNING DISABILITY SCREENING REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Student information
        f.write("STUDENT INFORMATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"Name: {student.first_name} {student.last_name}\n")
        f.write(f"Age: {student.age}\n")
        f.write(f"Grade: {student.grade}\n")
        f.write(f"Report Date: {report.generated_at.strftime('%Y-%m-%d %H:%M')}\n")
        f.write("\n")
        
        # Classification
        f.write("ASSESSMENT RESULTS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Classification: {report.classification}\n")
        f.write(f"Overall Risk Score: {report.risk_score:.2%}\n")
        f.write("\n")
        
        # Indicators
        if report.indicators:
            f.write("KEY INDICATORS\n")
            f.write("-" * 80 + "\n")
            for indicator in report.indicators:
                f.write(f"\n{indicator['category'].upper()}\n")
                f.write(f"  Risk Level: {indicator['risk_level'].upper()}\n")
                f.write(f"  Confidence: {indicator['avg_confidence']:.2%}\n")
                f.write(f"  Description: {indicator['description']}\n")
            f.write("\n")
        
        # Test summary
        f.write("TEST SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Tests Completed: {len(test_results)}\n")
        
        for test in test_results:
            f.write(f"\n{test.test_type.upper()} Test (ID: {test.id})\n")
            f.write(f"  Score: {test.score:.1f}%\n")
            f.write(f"  Errors: {test.errors}\n")
            f.write(f"  Date: {test.completed_at.strftime('%Y-%m-%d %H:%M')}\n")
        
        f.write("\n")
        
        # Recommendations
        f.write("RECOMMENDATIONS\n")
        f.write("-" * 80 + "\n")
        f.write(report.recommendations)
        f.write("\n\n")
        
        # Disclaimer
        f.write("DISCLAIMER\n")
        f.write("-" * 80 + "\n")
        f.write("This report is for screening purposes only and does not constitute a formal\n")
        f.write("diagnosis. A comprehensive evaluation by qualified professionals is recommended\n")
        f.write("for definitive diagnosis and treatment planning.\n")
        f.write("\n")
        f.write("=" * 80 + "\n")
    
    return str(filepath)
