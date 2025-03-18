To use this script: 

You'll need to install these Python packages if you don't have them:

```
pip install pandas pyautogui
```

Make sure your CSV file has the correct format with columns for roll numbers, names, and attendance status (P/N).
Run the script - it will prompt you to:

- Enter the path to your CSV file
- Navigate to the SAP portal page with the checkboxes
- Position your cursor on the first checkbox and press Enter
- Position your cursor on the second checkbox to calculate the vertical distance


The script will then automatically mark attendance based on your CSV data.

