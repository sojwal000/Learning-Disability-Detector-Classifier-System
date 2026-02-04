"""
Quick fix: Assign all students to teacher ID 3 (teachy)
This will allow the currently logged in user to access all students
"""
from app.database import SessionLocal
from app.models import Student

def assign_all_to_teacher_3():
    db = SessionLocal()
    
    try:
        students = db.query(Student).all()
        
        print("Reassigning all students to teacher ID 3 (teachy)...")
        for student in students:
            print(f"  - Student {student.id}: {student.first_name} {student.last_name} (was teacher_id={student.teacher_id})")
            student.teacher_id = 3
        
        db.commit()
        print("\n✅ All students now assigned to teacher ID 3!")
        print("You should now be able to access all students in the UI.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    assign_all_to_teacher_3()
