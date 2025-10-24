# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 23:39:19 2023

@author: Henry Cheung
"""


import smtplib
import ssl

ctx = ssl.create_default_context()
# password = "Trade1Analysis2For3Real4"    # Your app password goes here
password = "cajlaenspxzgxvwv"    # Your app password goes here
sender = "lostintokyo99@gmail.com"    # Your e-mail address
receiver = "henry.cheungkh@gmail.com" # Recipient's address
message = """
Hello from Python.
"""

with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
    server.login(sender, password)
    server.sendmail(sender, receiver, message)