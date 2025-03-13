# KiiT-Agentic-AI

Code to make AI agents for KIIT. These agents automate boring tasks using a mix of LLMs and smart Python code that are built to eliminate mundane tasks that are repeatable and can be replaced with a standard procedure to enhance efficiency and save time. 

We will have a Dummy Student DB with the Names, CGPAs and Attendance (consider one number for now). 

## Website screenshotS (v1)
![WhatsApp Image 2025-03-13 at 11 18 33_a574a15e](https://github.com/user-attachments/assets/7e833b9a-13bf-4c75-9084-a0f78f045fd5)

![WhatsApp Image 2025-03-13 at 11 18 38_66a17082](https://github.com/user-attachments/assets/52846285-6ee9-486c-974e-37edccdf52ca)



## Roadmap:


### Compliance


1. Certificate Generation (ADMIN ONLY)
  - NOC Generation
    - Same code as Bonafide one.
    - Just need to add a couple of "Dummy Checks" for CGPA, Attendance
    - TODO: Implement in FrontEnd
   
  - Bonafide Certificate Generation
    - Goes to Admin's email
    - Gets all emails with '[BONAFIDE]' in the Subject line
    - Display these emails in the FrontEnd (plain text)
    - Allow Admin to Click "Generate"
    - Then an email is sent from Admins email to Student
   
    - Backend is Done. Some tweaks need to be made to the frontend. 
      
  
- WiFi Reset Request Management
    - Admin Panel Integration

    - Access Admin’s email inbox.
        - Fetch all emails with [WIFI RESET] in the subject line.
        - Frontend Display

    - Show the list of reset requests (plain text).
        - Include details like student ID, name, and request timestamp.
        - Action Buttons

    - Admin can click a "Reset WiFi" button.
        - On click, trigger the backend to process the reset.
        - Email Confirmation
        - After reset, an automatic confirmation email is sent to the student.
        - Email content includes reset status and troubleshooting tips.
  
    - Current Status
        - Backend logic is complete.
        - Minor adjustments needed for frontend UI and email formatting.
    
- Rank Certficate
  - This agent processes requests for rank certificates. It updates student ranks based on CGPA, generates rank certificates, and emails them to students.

  - Features:
              - Email Retrieval: Connects to the admin's email and scans for unread emails with [RANK] in the subject line.
              - AI Extraction: Uses Gemini AI to extract student name and roll number from the email content.
              - Rank Calculation: Updates student ranks based on CGPA and sorts by name in case of ties.
              - Certificate Generation: Creates a PDF rank certificate including the student’s rank, CGPA, and department.
              - Email Notifications: Sends rank certificates or error notifications.
              - Logging: Logs all activities and errors.

  - Flow:
              - Admin receives a request email with [RANK] in the subject.
              - The agent extracts student information using AI.
              - It updates and retrieves the student’s rank from the database.
              - It generates and emails the certificate.
              - If an error occurs, it notifies the student.

- Scholarship Certification (Check CGPA & Check Attendance)
  - This agent handles scholarship certificate requests. It checks the admin's email for requests, verifies student eligibility, generates PDF certificates, and emails them to students.
  - Features:
              - Email Retrieval: Connects to the admin's email and scans for unread emails with [SCHOLARSHIP] in the subject line.
              - AI Extraction: Uses Gemini AI to extract student name and roll number from the email content.
              - Eligibility Check: Validates CGPA and attendance against scholarship criteria stored in a database.
              - Certificate Generation: Creates a PDF certificate for eligible students, including their rank, CGPA, and attendance.
              - Email Notifications: Sends certificates to eligible students or error/ineligibility notifications otherwise.
              - Logging: Logs all activities and errors.
  - Flow:
              - Admin receives a request email with [SCHOLARSHIP] in the subject.
              - The agent extracts student information using AI.
              - It validates eligibility from the database.
              - If eligible, it generates and sends the certificate.
              - If not eligible or there’s an error, it emails the student.

### Placement Activites (User Facing, must be a Chat Interface)
- ⁠KIIT Event Summaries (Web-Scraping)
- KIIT Kareer Placement PDF’s summaries (PDF)

### Tutor Mentor
- Leave Cert
  - <img width="250" alt="image" src="https://github.com/user-attachments/assets/0b16848f-530a-42df-91bb-b8a09a153bc2" />

- Scheduling G-Meet to meet Mentees one a week (mentor will give slots, we assume all students will be free post 6pm)
  - Should be simple to build. 

### Academic Activities (User facing, must be Chat Interface)
- Academic Calendar 
- Examination schedule
- Holiday List

  

### Conversational Workflow 

![WhatsApp Image 2025-03-12 at 20 48 41_a212c4c3](https://github.com/user-attachments/assets/aabfa62a-cd9f-4145-ac7c-3b8141770e8f)


### Sample env file:

Copy the example environment file:
```bash
cp .env.example .env
```

6. Edit the `.env` file with your preferred text editor and add your API keys:
```bash
EMAIL_PASSWORD=xxx
EMAIL=xxx@gmail.com
GROQ_API_KEY=""
GOOGLE_API_KEY=""
```
