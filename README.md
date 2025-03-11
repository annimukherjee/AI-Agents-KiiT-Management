# KiiT-Agentic-AI

Code to make AI agents for KIIT. These agents automate boring tasks using a mix of LLMs and smart Python code that are built to eliminate mundane tasks that are repeatable and can be replaced with a standard procedure to enhance efficiency and save time. 

We will have a Dummy Student DB with the Names, CGPAs and Attendance (consider one number for now). 

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
      
- Wi-Fi password reset
  - Ishaan is doing this. Ishaan, please update sub-points in a manner similar to the above.
    
- Rank Certficate
  - Very similar to the above. 

- Scholarship Certification (Check CGPA & Check Attendance)
  - Also very similar. Can copy paste the code above and make changes to the headings and small places in the code. 

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




## File Structure:

```
.
├── -academic-activities
│   └── academic-cal.py
├── -compliance-agents
│   ├── Wifi_reset.py
│   ├── bonafide-emails.py
│   ├── create_db.py
│   ├── noc.py
│   └── students.db
├── -placement-agent
│   ├── PlacementQueries.py
│   ├── kiit-pdfs-kareer
│   ├── kiit-pdfs-kareer-markdown
│   └── pdf_emails
├── -tutor-mentor
│   └── leave-cert.py
└── README.md
```
