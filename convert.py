import csv

csv.field_size_limit(1024 * 1024 * 1024)

def parse_email(message: str):

    headers = {}
    body = ""

    #splits headers and body
    #header ends at x-filename
    if "\n\n" in message:
        header_part, body = message.split("\n\n", 1)
        body = body.strip()
    else:
        header_part = message

    #split line by line 
    for line in header_part.split("\n"):
        #To: tim.belden@enron.com splits into {"To": "tim...."}
        if ":" in line:
            #From: bob@bob.com, key=From: value=bob@bob.com, 
            key, value = line.split(":", 1)
            #makes it become headers["From"] = bob@bob.com
            headers[key.strip()] = value.strip()

    #create dictionary
    #headers["From"] = bob@bob.com -> headers.get("From", retrieve bob@bob.com)
    return {
        "From": headers.get("From", ""),
        "To": headers.get("To", ""),
        "Subject": headers.get("Subject", ""),
        "Body": body
    }


def convert_email_to_json(df):
    emails_json = []

    #ignore _, iterrows read the rows
    for _, row in df.iterrows():
        #read column 1
        message = row.iloc[1]
        parsed_email = parse_email(message)
        #e.g. parsed_email: inbox.001.
        parsed_email["File"] = row["file"]
        emails_json.append(parsed_email)
    
    return emails_json
