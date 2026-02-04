"""
Reassign student to a specific teacher
Run this with: python reassign_student.py
"""
from app.database import SessionLocal
from app.models import Student, User

def reassign_student():
    db = SessionLocal()
    
    try:
        # Show all teachers
        teachers = db.query(User).filter(User.role == "teacher").all()
        print("Available teachers:")
        for teacher in teachers:
            print(f"  {teacher.id}: {teacher.username} ({teacher.email})")
        
        # Get student info
        student_id = int(input("\nEnter student ID to reassign: "))
        student = db.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            print(f"❌ Student ID {student_id} not found!")
            return
        
        print(f"\nStudent: {student.first_name} {student.last_name}")
        print(f"Current teacher ID: {student.teacher_id}")
        
        # Get new teacher
        new_teacher_id = int(input("\nEnter new teacher ID: "))
        new_teacher = db.query(User).filter(User.id == new_teacher_id, User.role == "teacher").first()
        
        if not new_teacher:
            print(f"❌ Teacher ID {new_teacher_id} not found!")
            return
        
        # Update
        student.teacher_id = new_teacher_id
        db.commit()
        
        print(f"\n✅ Student {student.first_name} {student.last_name} reassigned to {new_teacher.username}")
        
    except ValueError:
        print("❌ Please enter valid numbers!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reassign_student()
