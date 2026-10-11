MISSING PERSON ALERT - LOCAL SERVER
===================================

WHY YOU NEED THIS
Opening the page inside Claude or a preview window makes WhatsApp and Gmail
refuse to load ("refused to connect"). Running it from this small server opens
it as a normal web page, so the buttons work. It can also email every agency
automatically, with the photos attached.

FILES (keep all in the SAME folder)
  server.py    the server
  index.html   the page
  README.txt   this file

SET UP (one time)
1) Install Python 3 from python.org. On Windows, tick "Add Python to PATH".
   No other packages are needed.
2) For auto email only: in your Google account turn on 2-Step Verification,
   then create an App Password at https://myaccount.google.com/apppasswords
   (use the App Password, NOT your normal Gmail password).

RUN
Open a terminal in the folder (Windows: Shift + right-click > Open PowerShell
window here. Mac: right-click folder > New Terminal at Folder).

  Windows PowerShell:
    $env:GMAIL_USER="yourname@gmail.com"
    $env:GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
    python server.py          (or: py server.py)

  Mac / Linux:
    export GMAIL_USER="yourname@gmail.com"
    export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
    python3 server.py

  Without email setup, just run: python server.py (WhatsApp/Gmail buttons still work).

Then open  http://localhost:8000  in Chrome, Edge or Safari.
Keep the terminal window open while you work. Stop with Ctrl+C.

HOW TO USE THE PAGE
Step 1 Details   Name, age, clothes, last seen place, contact phone, police
                 report no. Extra optional fields (weight, hair, glasses,
                 medicines, home address, alternate contact) appear in the
                 message only if you fill them in. Everything is saved on
                 this device.
Step 2 Photos    Choose up to 4 photos. Each is shrunk to under 1 MB.
                 "Save photo" saves the small copy so you can attach it.
                 Photos are not saved: choose them again if you reopen.
Step 3 Send      - "Test on my own number": sends the alert to your own
                   phone number first. Do this once before real sending.
                 - WhatsApp: opens each agency's chat with the message filled
                   in. YOU press Send, and attach the photo (clip icon).
                 - Gmail: on a computer opens Gmail compose; on a phone opens
                   your mail app. Attach the photo before sending.
                 - Call: calls the agency.
                 - "Email all agencies now": appears when the server is
                   running. Emails every agency that has an email address,
                   with photos attached, from your Gmail.
                 - Tick marks and "x of 8 sent" show who you have done. A card
                   is marked when you tap its button, so untick it if you did
                   not actually send.
                 - Add emails in the cards (only Swarg and Atman are known),
                   and "Add another agency" for more.

IMPORTANT
- First file a missing person report with the police (dial 112). Put the
  report number in the form.
- WhatsApp does not allow any page to send messages by itself. You press Send.
  Fully automatic WhatsApp needs the WhatsApp Business Cloud API (Meta account
  and approved templates).
- Some agency numbers may not be on WhatsApp. Call those.
- The server listens only on your own computer (127.0.0.1) and rejects
  requests from other websites. Do not change this: it holds your Gmail App
  Password. Delete the App Password when the case is over.

TROUBLESHOOTING
- "python is not recognized": try  py server.py  or reinstall Python with
  "Add Python to PATH" ticked.
- "Gmail login failed": use a Gmail App Password, not your normal password.
- Page says "cannot open inside this preview": you opened the file from inside
  Claude. Use http://localhost:8000 in a normal browser tab instead.
- Photo "could not be read": it is probably a HEIC photo. Use a JPG, or set
  the phone camera to "Most Compatible". HEIC conversion needs internet.
- Port 8000 busy: run with another port, e.g. (PowerShell)  $env:PORT="8001"
  then python server.py, and open http://localhost:8001
