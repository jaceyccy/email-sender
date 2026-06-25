import smtplib
import pandas as pd
import mimetypes
from pathlib import Path
from email.message import EmailMessage
from email.header import Header
from tkinter import *
from tkinter import filedialog, messagebox
from email.utils import formataddr




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
    sender_name = sender_name_entry.get().strip()
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
                msg["From"] = formataddr((str(Header(sender_name, "utf-8")), sender))
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

# Make whole window scrollable
main_canvas = Canvas(root)
scrollbar = Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollable_frame = Frame(main_canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)

main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
main_canvas.configure(yscrollcommand=scrollbar.set)

main_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


# Mouse wheel scrolling
def _on_mousewheel(event):
    main_canvas.yview_scroll(int(-event.delta / 120), "units")


main_canvas.bind(
    "<Enter>",
    lambda e: main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
)

main_canvas.bind(
    "<Leave>",
    lambda e: main_canvas.unbind_all("<MouseWheel>")
)

# Use scrollable_frame instead of root below

csv_path = StringVar()
folder_path = StringVar()

Label(scrollable_frame, text="Digital Card Email Sender", font=("Arial", 18, "bold")).pack(pady=10)

Label(scrollable_frame, text="Sender Name").pack()

sender_name_entry = Entry(scrollable_frame, width=60)
sender_name_entry.insert(0, "OCAC Los Angeles")
sender_name_entry.pack()

Label(scrollable_frame, text="Gmail Address").pack()

sender_entry = Entry(scrollable_frame, width=60)
sender_entry.pack()

Label(scrollable_frame, text="Gmail App Password").pack()
password_entry = Entry(scrollable_frame, width=60, show="*")
password_entry.pack()

Label(scrollable_frame, text="Paste Gmail App Password. Spaces are OK.", fg="gray").pack()

Label(scrollable_frame, text="Email Subject").pack()
subject_entry = Entry(scrollable_frame, width=60)
subject_entry.insert(0, "Your Digital Card")
subject_entry.pack()

Button(scrollable_frame, text="Choose Recipient CSV", command=choose_csv).pack(pady=5)
Label(scrollable_frame, textvariable=csv_path, wraplength=600, fg="blue").pack()

Button(scrollable_frame, text="Choose Card Image Folder", command=choose_folder).pack(pady=5)
Label(scrollable_frame, textvariable=folder_path, wraplength=600, fg="blue").pack()

Label(scrollable_frame, text="Email Message").pack(pady=5)
body_text = Text(scrollable_frame, height=6, width=70)
body_text.insert(
    END,
    "Please find your digital card attached.\n\nBest,\nYour Name"
)
body_text.pack()

Button(
    scrollable_frame,
    text="Check Matches Before Sending",
    command=check_matches,
    bg="orange",
    fg="black",
    font=("Arial", 12, "bold"),
    width=30
).pack(pady=10)

Button(
    scrollable_frame,
    text="Send Emails",
    command=send_emails,
    bg="green",
    fg="white",
    font=("Arial", 14, "bold"),
    width=20
).pack(pady=10)

Label(scrollable_frame, text="Sending Log").pack()
log = Text(scrollable_frame, height=12, width=75)
log.pack(pady=10)

root.mainloop()