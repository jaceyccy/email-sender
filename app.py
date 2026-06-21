import smtplib
import pandas as pd
import mimetypes
from pathlib import Path
from email.message import EmailMessage
from tkinter import *
from tkinter import filedialog, messagebox


def choose_csv():
    file_path = filedialog.askopenfilename(
        title="Choose CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    csv_path.set(file_path)


def choose_folder():
    folder = filedialog.askdirectory(title="Choose Card Image Folder")
    folder_path.set(folder)


def find_card_file(folder, name):
    folder = Path(folder)

    allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]

    for file in folder.iterdir():

        if file.suffix.lower() not in allowed_extensions:
            continue

        if name.lower() in file.stem.lower():
            return file

    return None


def check_matches():
    csv_file = csv_path.get()
    card_folder = folder_path.get()

    if not csv_file or not card_folder:
        messagebox.showerror("Error", "Please choose CSV file and card folder first.")
        return

    try:
        df = pd.read_csv(csv_file)

        if "name" not in df.columns or "email" not in df.columns:
            messagebox.showerror("CSV Error", "CSV must contain columns: name,email")
            return

        log.delete("1.0", END)
        log.insert(END, "Checking matches...\n\n")

        missing_count = 0

        for _, row in df.iterrows():
            name = str(row["name"]).strip()
            email = str(row["email"]).strip()

            card_file = find_card_file(card_folder, name)

            if card_file:
                log.insert(END, f"✅ {name} <{email}>  →  {card_file.name}\n")
            else:
                log.insert(END, f"❌ {name} <{email}>  →  No card found\n")
                missing_count += 1

        log.insert(END, f"\nCheck complete. Missing cards: {missing_count}\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def send_emails():
    sender = sender_entry.get().strip()
    password = password_entry.get().strip().replace(" ", "")
    subject = subject_entry.get().strip()
    csv_file = csv_path.get()
    card_folder = folder_path.get()
    email_body = body_text.get("1.0", END).strip()

    if not sender or not password or not subject or not csv_file or not card_folder or not email_body:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    try:
        df = pd.read_csv(csv_file)

        if "name" not in df.columns or "email" not in df.columns:
            messagebox.showerror(
                "CSV Error",
                "CSV file must contain columns: name,email"
            )
            return

        log.delete("1.0", END)
        log.insert(END, "Starting email sending...\n\n")
        root.update()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)

            for index, row in df.iterrows():
                name = str(row["name"]).strip()
                recipient = str(row["email"]).strip()

                card_file = find_card_file(card_folder, name)

                if card_file is None:
                    log.insert(END, f"Missing card for: {name}\n")
                    root.update()
                    continue

                msg = EmailMessage()
                msg["From"] = sender
                msg["To"] = recipient
                msg["Subject"] = subject

                msg.set_content(email_body)

                mime_type, _ = mimetypes.guess_type(card_file)
                if mime_type is None:
                    mime_type = "application/octet-stream"

                main_type, sub_type = mime_type.split("/", 1)

                with open(card_file, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=main_type,
                        subtype=sub_type,
                        filename=card_file.name
                    )

                smtp.send_message(msg)

                log.insert(END, f"Sent to {name} <{recipient}> with {card_file.name}\n")
                root.update()

        messagebox.showinfo("Done", "All emails have been sent!")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ================= GUI =================

root = Tk()
root.title("Digital Card Email Sender")
root.geometry("650x650")

csv_path = StringVar()
folder_path = StringVar()

Label(root, text="Digital Card Email Sender", font=("Arial", 18, "bold")).pack(pady=10)

Label(root, text="Gmail Address").pack()
sender_entry = Entry(root, width=60)
sender_entry.pack()

Label(root, text="Gmail App Password").pack()
password_entry = Entry(root, width=60, show="*")
password_entry.pack()

Label(root, text="Paste Gmail App Password. Spaces are OK.", fg="gray").pack()

Label(root, text="Email Subject").pack()
subject_entry = Entry(root, width=60)
subject_entry.insert(0, "Your Digital Card")
subject_entry.pack()

Button(root, text="Choose Recipient CSV", command=choose_csv).pack(pady=5)
Label(root, textvariable=csv_path, wraplength=600, fg="blue").pack()

Button(root, text="Choose Card Image Folder", command=choose_folder).pack(pady=5)
Label(root, textvariable=folder_path, wraplength=600, fg="blue").pack()

Label(root, text="Email Message").pack(pady=5)
body_text = Text(root, height=8, width=70)
body_text.insert(
    END,
    "Please find your digital card attached.\n\nBest,\nYour Name"
)
body_text.pack()

Button(
    root,
    text="Check Matches Before Sending",
    command=check_matches,
    bg="orange",
    fg="black",
    font=("Arial", 12, "bold"),
    width=30
).pack(pady=10)


Button(
    root,
    text="Send Emails",
    command=send_emails,
    bg="green",
    fg="white",
    font=("Arial", 14, "bold"),
    width=20
).pack(pady=15)

Label(root, text="Sending Log").pack()
log = Text(root, height=12, width=75)
log.pack()

root.mainloop()