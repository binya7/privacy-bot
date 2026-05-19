import sys
import threading
import imaplib
import smtplib
import email
from email.mime.text import MIMEText

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

class PrivacyBotApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.root.add_widget(Label(text="Data Deletion Bot", font_size=24, size_hint_y=None, height=50))
        self.root.add_widget(Label(text="Enter Your Gmail:", size_hint_y=None, height=30))
        self.email_input = TextInput(text="binyamin99780@gmail.com", multiline=False, size_hint_y=None, height=40)
        self.root.add_widget(self.email_input)
        self.root.add_widget(Label(text="Enter App Password:", size_hint_y=None, height=30))
        self.pass_input = TextInput(text="mcuumrlhyldleyya", password=True, multiline=False, size_hint_y=None, height=40)
        self.root.add_widget(self.pass_input)
        self.start_btn = Button(text="Start Scan & Delete", background_color=(0, 0.9, 0.5, 1), font_size=18, size_hint_y=None, height=50)
        self.start_btn.bind(on_press=self.start_bot)
        self.root.add_widget(self.start_btn)
        self.scroll = ScrollView()
        self.log_area = Label(text="🤖 App Ready...\n", size_hint_y=None, halign='left', valign='top')
        self.log_area.bind(texture_size=self.log_area.setter('size'))
        self.scroll.add_widget(self.log_area)
        self.root.add_widget(self.scroll)
        return self.root

    def log_message(self, msg):
        def update_label(dt):
            self.log_area.text += msg + "\n"
        Clock.schedule_once(update_label)

    def start_bot(self, instance):
        self.start_btn.disabled = True
        self.log_message("🤖 Process shuru ho raha hai...")
        threading.Thread(target=self.run_scanner).start()

    def run_scanner(self):
        user_email = self.email_input.text.strip()
        user_pass = self.pass_input.text.strip()
        try:
            self.log_message("📡 Connecting to Email server...")
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(user_email, user_pass)
            mail.select("inbox")
            status, messages = mail.search(None, '(SUBJECT "Welcome")')
            email_ids = messages[0].split()
            companies_found = []
            self.log_message(f"🔍 Found {len(email_ids)} emails. Scanning...")
            for e_id in email_ids[:20]:
                res, msg_data = mail.fetch(e_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        sender = msg.get('From')
                        if sender and "@" in sender:
                            domain = sender.split("@")[-1].replace(">", "").strip()
                            if domain not in companies_found:
                                companies_found.append(domain)
            mail.logout()
            self.log_message(f"🏢 Total {len(companies_found)} companies detected.")
            self.log_message("\n✉️ Sending Deletion Requests...")
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(user_email, user_pass)
            for domain in companies_found:
                target_email = f"privacy@{domain}"
                subject = f"Official Data Deletion Request - {user_email}"
                body = f"Hello {domain} Team,\n\nI am requesting the deletion of my account associated with {user_email}.\n\nRegards"
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = user_email
                msg['To'] = target_email
                try:
                    server.sendmail(user_email, target_email, msg.as_string()) 
                    self.log_message(f"✅ Sent to: {target_email}")
                except:
                    pass 
            server.quit()
            self.log_message("\n🎉 Done! Process complete!")
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
        finally:
            def re_enable(dt):
                self.start_btn.disabled = False
            Clock.schedule_once(re_enable)

if __name__ == '__main__':
    PrivacyBotApp().run()
