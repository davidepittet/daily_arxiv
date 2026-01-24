import arxiv
import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Grouping related concepts to avoid a "wall of text" and improve readability
RADAR_TYPES = 'ti:"FMCW" OR ti:"PMCW" OR ti:"MIMO" OR ti:"multistatic" OR ti:"virtual aperture"'
AUTOMOTIVE = 'ti:"automotive radar" OR ti:"77 GHz" OR ti:"79 GHz" OR ti:"ADAS"'
SIGNAL_PROC = 'ti:"signal processing" OR ti:"micro-Doppler" OR ti:"DoA estimation" OR ti:"beamforming"'
SPARSE_RECOVERY = 'ti:"compressive sensing" OR ti:"sparse signal recovery" OR ti:"sparse Bayesian learning" OR ti:"SBL"'
HYBRID_METHODS = 'ti:"hybrid modelling" OR ti:"physics-informed" OR ti:"deep unrolling" OR ti:"learned iterative"'

# Combine everything into one master query
KEYWORDS = f"({RADAR_TYPES} OR {AUTOMOTIVE} OR {SIGNAL_PROC} OR {SPARSE_RECOVERY} OR {HYBRID_METHODS})"
search = arxiv.Search(query=KEYWORDS, max_results=1000, sort_by=arxiv.SortCriterion.SubmittedDate)

now = datetime.datetime.now(datetime.timezone.utc)
yesterday = now - datetime.timedelta(days=1)

found_papers = []
for result in search.results():
    if result.published > yesterday:
        found_papers.append(result)

# 2. If papers are found, send the email
if found_papers:
    msg = MIMEMultipart()
    msg['Subject'] = f"Daily arXiv Digest: {now.strftime('%Y-%m-%d')}"
    msg['From'] = os.environ.get('EMAIL_USER')
    msg['To'] = os.environ.get('EMAIL_TO')

    html_content = "<h3>New Research Papers Found:</h3>"
    for p in found_papers:
        html_content += f"<p><strong>{p.title}</strong><br><a href='{p.pdf_url}'>View PDF</a></p><hr>"
    
    msg.attach(MIMEText(html_content, 'html'))

    # 3. Connect to Gmail SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASSWORD'))
            server.send_message(msg)
        print("Email sent successfully via Gmail!")
    except Exception as e:
        print(f"Failed to send email: {e}")
else:
    print("No new papers today.")