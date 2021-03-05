import random
import secrets
from datetime import datetime

now = datetime.now() # current date and time
date_time = now.strftime("%Y/%m/%d, %H:%M:%S")

print(f"{date_time}: Start... ")

file_name = "xml_test_data.xml"
with open(file_name, 'w') as writer:
    for idx in range(0, 180_000):
        amount = str(random.randint(1, 100_000_000))
        
        b = secrets.token_urlsafe(12)
        p = str(random.randint(100_000, 900_000))
        q = <Ref>000000"+ str(random.randint(10, 99)) +"00000" + str(random.randint(100_000_000_000_000, 900_000_000_000_000)) + "</Ref>"

        xml_doc = b + p + q

        if idx % 10000 == 0:
            now = datetime.now() # current date and time
            date_time = now.strftime("%Y/%m/%d, %H:%M:%S")
            print(f"{date_time}: {idx} documents written...")

        writer.write(xml_doc+'\n')

now = datetime.now() # current date and time
date_time = now.strftime("%Y/%m/%d, %H:%M:%S")

print(f"{date_time}: Done... ")
