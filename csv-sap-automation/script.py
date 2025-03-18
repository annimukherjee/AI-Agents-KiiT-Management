import pandas as pd
import pyautogui
import time

def mark_attendance_from_csv(csv_path, delay_between_actions=0.5):
    """
    Reads attendance data from CSV and automates marking in SAP portal
    
    Parameters:
    csv_path (str): Path to the CSV file with attendance data
    delay_between_actions (float): Delay in seconds between mouse actions
    """
    # Read the CSV file
    try:
        df = pd.read_csv(csv_path)
        print(f"Successfully loaded {len(df)} student records")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return
    
    # Pause to give user time to navigate to the SAP portal attendance page
    print("Please navigate to the SAP portal attendance page.")
    print("The script will begin in 5 seconds...")
    time.sleep(5)
    
    # Get the starting position of the first checkbox
    print("Move your cursor to the first checkbox and press Enter")
    input()
    first_checkbox_pos = pyautogui.position()
    
    # Get the vertical distance between checkboxes
    print("Now move your cursor to the second checkbox and press Enter")
    input()
    second_checkbox_pos = pyautogui.position()
    vertical_distance = second_checkbox_pos[1] - first_checkbox_pos[1]
    
    # Mark attendance for each student
    current_pos = first_checkbox_pos
    for index, row in df.iterrows():
        roll_number = row.get('Roll Number', 'N/A')
        name = row.get('Name', 'N/A')
        attendance = row.get('Attendance', 'N')  # Use actual column name from your CSV
        
        # Move to the current checkbox position
        pyautogui.moveTo(current_pos)
        
        # Click if the student is present (P)
        if attendance.upper() == 'P':
            print(f"Marking present for {roll_number} - {name}")
            pyautogui.click()
        else:
            print(f"Marking absent for {roll_number} - {name}")
        
        # Short delay to avoid issues
        time.sleep(delay_between_actions)
        
        # Update position for next student
        current_pos = (current_pos[0], current_pos[1] + vertical_distance)
    
    print("Attendance marking completed!")

if __name__ == "__main__":
    csv_path = input("Enter the path to your attendance CSV file: ")
    mark_attendance_from_csv(csv_path)