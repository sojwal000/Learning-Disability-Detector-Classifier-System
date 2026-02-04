"""
Quick script to check and fix student teacher_id assignments
Run this with: python fix_student_teacher.py
"""
from app.database import SessionLocal
from app.models import Student, User

def fix_student_assignments():
    db = SessionLocal()
    
    try:
        # Get all students
        students = db.query(Student).all()
        
        print(f"\nFound {len(students)} students:")
        for student in students:
            print(f"  - Student ID {student.id}: {student.first_name} {student.last_name}")
            print(f"    Teacher ID: {student.teacher_id}")
        
        # Get all teachers
        teachers = db.query(User).filter(User.role == "teacher").all()
        print(f"\nFound {len(teachers)} teachers:")
        for teacher in teachers:
            print(f"  - Teacher ID {teacher.id}: {teacher.username} ({teacher.email})")
        
        # Find students without teacher_id
        unassigned = [s for s in students if s.teacher_id is None]
        
        if unassigned:
            print(f"\n⚠️  Found {len(unassigned)} students without teacher assignment:")
            for student in unassigned:
                print(f"  - Student ID {student.id}: {student.first_name} {student.last_name}")
            
            if teachers:
                print(f"\nAssigning all unassigned students to teacher ID {teachers[0].id} ({teachers[0].username})...")
                for student in unassigned:
                    student.teacher_id = teachers[0].id
                    print(f"  ✓ Assigned student {student.id} to teacher {teachers[0].id}")
                
                db.commit()
                print("\n✅ All students now have teacher assignments!")
            else:
                print("\n❌ No teachers found to assign students to!")
        else:
            print("\n✅ All students have teacher assignments!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_student_assignments()
