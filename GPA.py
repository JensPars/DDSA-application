import json
import os

def convert_grade_to_gpa(grade):
    """Convert Danish grade to US GPA"""
    if not grade:
        return None
    
    # Handle "BE (P)" pass grades separately
    if "BE" in grade:
        return None  # Not counted in GPA
    
    # Extract the numeric part
    numeric_grade = grade.split()[0]
    
    # Convert Danish grade to US GPA
    grade_map = {
        "12": 4.0,  # A
        "10": 3.5,  # B
        "7": 3.0,   # C
        "4": 2.0,   # D
        "02": 1.0,  # E
        "00": 0.0,  # Fx
        "-3": 0.0   # F
    }
    
    return grade_map.get(numeric_grade, None)

def get_numeric_danish_grade(grade):
    """Extract the numeric Danish grade from the grade string"""
    if not grade or "BE" in grade:
        return None
    
    try:
        # Extract the numeric part before the space
        numeric_part = grade.split()[0]
        return float(numeric_part)
    except (ValueError, IndexError):
        return None

def calculate_gpa(grades_data):
    """Calculate both US GPA and Danish grade average from grades data"""
    total_weighted_gpa_points = 0
    total_weighted_danish_points = 0
    total_ects = 0
    
    for course in grades_data:
        # Extract ECTS credits and convert to float if possible
        try:
            ects = float(course.get("ECTS", 0))
        except ValueError:
            # Fix incomplete ECTS values like "5."
            ects_str = course.get("ECTS", "0")
            if ects_str.endswith('.'):
                try:
                    ects = float(ects_str + '0')
                except ValueError:
                    ects = 0
            else:
                ects = 0
        
        grade_str = course.get("Grade", "")
        
        # Convert grade to GPA points (US system)
        gpa_points = convert_grade_to_gpa(grade_str)
        
        # Get numeric Danish grade
        danish_points = get_numeric_danish_grade(grade_str)
        
        # Only count courses with valid points
        if gpa_points is not None and ects > 0:
            total_weighted_gpa_points += gpa_points * ects
            total_weighted_danish_points += danish_points * ects
            total_ects += ects
    
    # Calculate averages if there are valid courses
    if total_ects > 0:
        us_gpa = total_weighted_gpa_points / total_ects
        danish_avg = total_weighted_danish_points / total_ects
        return us_gpa, danish_avg, total_ects
    else:
        return 0.0, 0.0, 0

def main():
    # Get the path to the JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'bsc_grades.json')
    
    # Load the grades from the JSON file
    try:
        with open(json_path, 'r') as file:
            grades_data = json.load(file)
    except Exception as e:
        print(f"Error loading grades file: {e}")
        return
    
    # Calculate both GPA systems
    us_gpa, danish_avg, total_ects = calculate_gpa(grades_data)
    
    # Display results
    print(f"Total ECTS credits: {total_ects}")
    print(f"US GPA (4.0 scale): {us_gpa:.2f}")
    print(f"Danish Grade Average (12 scale): {danish_avg:.2f}")
    
    # Count grades by letter grade
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0, "P": 0}
    
    for course in grades_data:
        grade = course.get("Grade", "")
        if "12 (A)" in grade:
            grade_counts["A"] += 1
        elif "10 (B)" in grade:
            grade_counts["B"] += 1
        elif "7 (C)" in grade:
            grade_counts["C"] += 1
        elif "4 (D)" in grade:
            grade_counts["D"] += 1
        elif "02 (E)" in grade:
            grade_counts["E"] += 1
        elif "00" in grade or "-3" in grade:
            grade_counts["F"] += 1
        elif "BE (P)" in grade:
            grade_counts["P"] += 1
    
    # Display grade distribution
    print("\nGrade Distribution:")
    for grade, count in grade_counts.items():
        if count > 0:
            print(f"{grade}: {count}")
    
    # List all courses with their grades and points
    print("\nCourses:")
    print(f"{'Number':<10} {'Title':<60} {'Grade':<10} {'ECTS':<6}")
    print("-" * 86)
    
    for course in sorted(grades_data, key=lambda x: x.get("Date", ""), reverse=True):
        number = course.get("Number", "")
        title = course.get("Title", "")
        grade = course.get("Grade", "")
        ects = course.get("ECTS", "")
        
        # Truncate title if too long
        if len(title) > 57:
            title = title[:54] + "..."
            
        print(f"{number:<10} {title:<60} {grade:<10} {ects:<6}")
    
    # Display details of GPA calculations
    print("\nGPA Calculation Details:")
    print(f"{'Number':<10} {'Grade':<10} {'ECTS':<6} {'Danish Weight':<15} {'US GPA Weight':<15}")
    print("-" * 60)
    
    for course in sorted(grades_data, key=lambda x: x.get("Date", ""), reverse=True):
        grade_str = course.get("Grade", "")
        if "BE" in grade_str:  # Skip pass/fail courses
            continue
            
        try:
            ects = float(course.get("ECTS", "0").replace('.', '0') if course.get("ECTS", "0").endswith('.') else course.get("ECTS", "0"))
        except ValueError:
            ects = 0
            
        danish_grade = get_numeric_danish_grade(grade_str)
        gpa_points = convert_grade_to_gpa(grade_str)
        
        if danish_grade is not None and ects > 0:
            danish_weight = danish_grade * ects
            us_weight = gpa_points * ects
            print(f"{course.get('Number', ''):<10} {grade_str:<10} {ects:<6} {danish_weight:<15.1f} {us_weight:<15.1f}")

if __name__ == "__main__":
    main()
