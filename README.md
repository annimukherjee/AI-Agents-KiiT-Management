# KiiT-Agentic-AI
Contains code to make AI agents for KIIT


Currently `bonafide-agent` checkes my emails for emails with subject [BONAFIDE], downloads them, sends it to an LLM to get the Name & Roll-Num and then check a database if the student exists. If the student exists then generate a PDF and <to be implemented> email the student back.

## Roadmap:


### Compliance
- NOC Generation
- Bonafide Certificate Generation
- Wi-Fi password reset (ISHAAN)
- Rank Certficate
- Scholarship Certification (Check CGPA & Check Attendance)


### Placement Activites
- ⁠KIIT Event Summaries (Web-Scraping)
- KIIT Kareer Placement PDF’s summaries (PDF)

### Tutor Mentor
- Leave Cert (not seeing much value) 
- Scheduling G-Meet to meet Mentees one a week (mentor will give slots, we assume all students will be free post 6pm)

### Academic Activities
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
