import smtplib
import pandas as pd
from pathlib import Path
from email.message import EmailMessage
from tkinter import *
from tkinter import filedialog, messagebox

def send_emails():
    sender = sender_entry.get()
    password = password_entry.get()
    subject = subject_entry.get()
    email_body = body_text.get("1.0", END).strip()
    csv_file = csv_path.get()
    card_folder = folder_path.get()

    if not sender or not password or not email_body or not csv_file or not card_folder:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
    df = pd.read_csv(csv_file)

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:
        smtp.login(sender, password)

        for _, row in df.iterrows():
            recipient = row['email']
            file_name = row['file']

            card_path = Path(card_folder) / file_name

            if not card_path.exists():
                log.insert(END, f"Missing file: {file_name}\n")
                continue

            msg = EmailMessage()
            msg["From"] = sender
            msg["To"] = recipient
            msg["Subject"] = subject

            personalized_body = email_body.format(**row)
            msg.set_content(personalized_body)
                            
            with open(card_path, "rb") as f:
                file_data = f.read()

            ext = card_path.suffix.lower()

            if ext == ".pdf":
                msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)
            elif ext in [".jpg", ".jpeg"]:
                msg.add_attachment(file_data, maintype="image", subtype="jpeg", filename=file_name)
            elif ext == ".png":
                msg.add_attachment(file_data, maintype="image", subtype="png", filename=file_name)
            else:
                log.insert(END, f"Unsupported file type: {file_name}\n")
                continue

            smtp.send_message(msg)
            log.insert(END, f"Sent to {recipient}\n")
            root.update()

    messagebox.showinfo("Done", "All emails sent!")           

def choose_csv():
    csv_path.set(filedialog.askopenfilename(
        title = "Choose Recipient CSV",
        filetypes=[("CSV Files", "*.csv")]))

def choose_folder():
    folder_path.set(filedialog.askdirectory(
        title = "Choose Card Folder"
    ))

root = Tk()
root.title("Digital Card Email Sender")
root.geometry("500x500")

csv_path = StringVar()
folder_path = StringVar()

Label(root, text="Gmail Address").pack()
sender_entry = Entry(root, width=50)
sender_entry.pack()

Label(root, text="Gmail App Password").pack()
password_entry = Entry(root, width=50, show="*")
password_entry.pack()

Label(root, text="Email Subject").pack()
subject_entry = Entry(root, width=50)
subject_entry.insert(0, "Your Digital Card")
subject_entry.pack()

Label(root, text = "Email Content").pack()

body_text = Text(root, height=10, width=65)
body_text.pack()

body_text.insert(
    "1.0",
    """Hi {name},

Please find your digital card attached.

Best regards,
"""
)

Button(root, text="Choose Recipient CSV", command=choose_csv).pack(pady=5)
Label(root, textvariable=csv_path, wraplength=450).pack()

Button(root, text="Choose Card Folder", command=choose_folder).pack(pady=5)
Label(root, textvariable=folder_path, wraplength=450).pack()

Button(root, text="Send Emails", command=send_emails, bg="green", fg="white").pack(pady=15)

log = Text(root, height=10, width=60)
log.pack()

root.mainloop()