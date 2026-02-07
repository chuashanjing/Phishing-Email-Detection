import re
import pandas as pd
from flask import Response, Flask, render_template, request, redirect, url_for, jsonify, session
import matplotlib
#allow writing to memory buffer
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

from convert import convert_email_to_json
from rulebased import keyword, keyword_positioning, distance_check, url_detection
from ml import mlpreprocess, mlpredict

app = Flask(__name__)
# need put secret key. for storing session data
app.secret_key = "abc"

#domain whitelist
whitelist = set(['@enron.com'])
#filter it from a@bob.com to @bob.com
DOMAIN_PATTERN = re.compile(r'^@.+')
storage = {}

#route /, triggered by action='/' in php
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        #retrieves domain from input
        domain = request.form.get("domain")

        #prevent duplicate domains in array
        if domain not in whitelist:
            whitelist.add(domain)

        return redirect(url_for("index"))

    #renders index.php as the webpage. passes domains=whitelist to phpfile
    #format: {% for i in domain %}
    return render_template("index.php", domains=whitelist)

#remove_domain route
@app.route("/remove_domain", methods=["POST"])
def remove_domain():
    #retrieve the data send by request
    data = request.get_json()
    #gets domain from ["domain": "domain"]
    domain = data.get("domain")

    #if domain in whitelist, remove the domain
    if domain in whitelist:
        whitelist.remove(domain)
    return jsonify(success=True)

#upload_csv route
@app.route('/upload_csv', methods=["POST"])
def upload_csv():

    #gets the csvFile sent by request
    file = request.files['csvFile']
    #use pandas to read the csv file
    df = pd.read_csv(file)

    #send the csv to process_email()
    emails_json = process_email(df)

    #things to filter are stored in here
    rows_to_hide = []
    #idx = index, email is just the content
    for idx, email in enumerate(emails_json):
        #strip email
        to_email = email["From"].strip()
        #if @ exist
        if '@' in to_email:
            #split the username and domain by @ + @ = e.g.@google.com
            domain = "@" + to_email.split("@")[1]
            #double confirm if domain in whitelist
            if domain in whitelist:
                #add index to rowstohide array
                rows_to_hide.append(idx)
    #drop the csv row by index
    #if rows_to_hide array empty, it will just drop nothing
    df_filtered = df.drop(rows_to_hide)

    #store df_filtered in this global dictionary
    storage['df_filtered'] = df_filtered

    if emails_json:
        #put in table
        table_html = df_filtered.to_html(classes="table table-bordered table-striped", index=False)
    else:
        #if csv file not in correct format, invalid email
        table_html = "<p>Not valid email csv</p>"
    return jsonify({"table": table_html})

#converts email to json to allow data to be plugged out easily
def process_email(df):
    """
    1. converts the email csv to dictionary/json format
    2. emails_json is now a list of dictionary
    """
    try:
        #call function
        emails_json = convert_email_to_json(df)
        return emails_json
    except Exception:
        return []

@app.route('/rulebased', methods=["POST"])
def rulebased():
    """
    1. Get csv and convert to json
    2. Get each content from the email
    3. Send it to rule base check
    4. Average it to get score
    5. Store in session to merge with machine learning
    """
    #get the csv from the list
    df = storage.get('df_filtered')
    #if df contains csv
    if df is not None:

        #create a dictionary for the results
        results = {}
        #process email to json
        emails_json = process_email(df)
        #pos is the counter e.g. the 'i' in for i in range
        #idx is the row within the dataframe
        #df.index is the row in csv

        #so we are essentially using the counter to loop properly
        #based of the index of the dataframe to make it loop accurately
        # instead of skipping steps
        for pos, idx in enumerate(df.index):
            #now we can plug out the email based off the new 'index'
            content = emails_json[pos]

            #get the From, Body and Subject of email
            to_email = str(content.get("From", "")).strip()
            body_email = content.get("Body", "")
            subject_email = content.get("Subject", "")

            topredict = mlpreprocess(body_email)
            prediction = mlpredict(topredict)

            #check if its a valid email
            if '@' not in to_email:
                continue

            #split the @ to get the domain
            domain = to_email.split("@")[1]

            #call distance check.
            distance_score = distance_check(domain) or 0.0
            
            #call url detection
            urldetection_score = url_detection(body_email, domain) or 0.0
            #call keyword check
            keyword_score = keyword(subject_email, body_email)
            #call keyword positioning check
            keyword_position_score = keyword_positioning(text=body_email, bscore=keyword_score[0], sscore=keyword_score[1]) or 0.0
            rulebased_score = (distance_score + urldetection_score + keyword_position_score) / 3

            #get average of 3 checks, keyword_positioning is a multiplier factor and keyword check is the score
            final_score = round(0.4*(rulebased_score) + (0.6 * prediction), 2)

            if final_score >= 0.75:
                phishing = 'Phishing'
            elif 0.35 <= final_score < 0.75:
                phishing = 'Suspicious'
            else:
                phishing = 'Legitimate'

            #results are placed in a dictionary
            results[idx] = {
                "distance_score": distance_score,
                "url_detection_score": urldetection_score,
                "keyword_position_score": round(keyword_position_score,2),
                "Rule Based Score": round(rulebased_score,2),
                "ML Prediction": prediction,
                "Final Score": final_score,
                "Classification": phishing
                }
            
            #adds a new column distance score, based on index, add its respective scorings
            df.loc[idx, "distance_score"] = distance_score
            df.loc[idx, "url_detection_score"] = urldetection_score
            df.loc[idx, "keyword_position_score"] = round(keyword_position_score,2)
            df.loc[idx, "Rule Based Score"] = round(rulebased_score,2)
            df.loc[idx, "ML Prediction"] = prediction
            df.loc[idx, "Final Score"] = final_score
            df.loc[idx, "Classification"] = phishing
        
        
        #convert dataframe to csv
        csv_data = df.to_csv(index=False)
        storage['csv_data'] = csv_data

        #returns the csv that is in text/csv format as an attachment named rule_based_results.csv
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=rule_based_results.csv"}
        )
    #if no df found
    return "No data found", 404


@app.route('/get_histogram', methods=["GET"])
def get_histogram():
    #retrieve csvdata from storage list
    df = storage.get('csv_data')

    #checking if df exist
    if df is None:
        return jsonify({"error": "No data available to plot."})
    
    try:
        #converts python string to filetype object so that pandas can read it
        df = pd.read_csv(io.StringIO(df))

        #checking for final score column
        if 'Final Score' not in df.columns:
            return jsonify({"error": "Column 'Final Score' not found in the processed CSV."})
        
        #checks if there is any errors when converting to NaN. then it drops the error row
        data = pd.to_numeric(df['Final Score'], errors='coerce').dropna()
        if data.empty:
            return jsonify({"error": "No valid numeric data to plot."})
        
        
        plt.figure(figsize=(10, 5))
        plt.hist(data, bins=10, color='blue', alpha=0.7)
        plt.title('Distribution of Final Scores')
        plt.xlabel('Final Score')
        plt.ylabel('Frequency')
        plt.grid(axis='y', alpha=0.5)

        #store inside memory buffer
        img = io.BytesIO()
        #save the plot into the memory buffer as png format
        plt.savefig(img, format='png')
        #get bytes of image, encode it to base64
        #then decode to utf8 to allow json to accept
        plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
        #remove plot from memory
        plt.close()
        return jsonify({"plot_url": plot_url})
    except Exception as e:
        plt.close()
        return jsonify({"error": "Failed to generate graph"})

@app.route('/get_scatterplot', methods=["GET"])
def get_scatterplot():
    plt.clf()
    df = storage.get('csv_data')

    #checking if df exist
    if df is None:
        return jsonify({"error": "No data available to plot."})
    
    try:
        #converts python string to filetype object so that pandas can read it
        df = pd.read_csv(io.StringIO(df))

        df['Rule Based Score'] = pd.to_numeric(df['Rule Based Score'], errors='coerce')
        df['ML Prediction'] = pd.to_numeric(df['ML Prediction'], errors='coerce')
        #drop NaN columns
        df.dropna(subset=['ML Prediction', 'Rule Based Score'])

        if df.empty:
            return jsonify({"error": "No data to plot."})
        
        plt.figure(figsize=(10, 5))
        plt.scatter(df['Rule Based Score'], df['ML Prediction'], color='blue', alpha=0.7)
        plt.title('ML Prediction vs Rule Based')
        plt.ylabel('ML Prediction')
        plt.xlabel('Rule Based Score')
        plt.grid(True, linestyle='--', alpha=0.5)

        #store inside memory buffer
        img = io.BytesIO()
        #save the plot into the memory buffer as png format
        plt.savefig(img, format='png')
        #get bytes of image, encode it to base64
        #then decode to utf8 to allow json to accept
        plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
        #remove plot from memory
        plt.close()
        return jsonify({"plot_url": plot_url})
    except Exception as e:
        plt.close()
        return jsonify({"error": "Failed to generate graph"})

@app.route('/get_grouped_chart', methods=["GET"])
def get_grouped_chart():
    plt.clf()
    df = storage.get('csv_data')

    if df is None:
        return jsonify({"error": "No data available to plot."})
    
    try:
        #converts python string to filetype object so that pandas can read it
        df = pd.read_csv(io.StringIO(df))

        column_mapping = {
            'url_detection_score': 'url_detection_score',
            'distance_score': 'distance_score',
            'keyword_position_score': 'keyword_position_score',
            'ML Prediction': 'ML Prediction'
        }
        features = list(column_mapping.values())
        #convert all columns to numeric
        for col in features:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        #group each classification(phshing, legit, suspicous)
        #then get the average of each feature
        grouped_df = df.groupby('Classification')[features].mean()

        #setting the order
        new_order = ['Legitimate', 'Suspicious', 'Phishing']

        #checks if new order exist in group_df.index then keep it
        current_order = [i for i in new_order if i in grouped_df.index]

        #change the order of index to new order
        grouped_df = grouped_df.reindex(current_order)

        #bar chart
        grouped_df.plot(kind='bar', figsize=(10, 6), width=0.8)
        plt.title('Average Feature Scores by Classification')
        plt.ylabel('Score')
        plt.xticks(rotation=0)
        plt.legend(loc='upper left')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        img=io.BytesIO()
        plt.savefig(img, format='png')

        plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()

        return jsonify({"plot_url": plot_url})
    
    except Exception as e:
        plt.close()
        return jsonify({"error": "Failed to generate graph"})

@app.route('/get_boxplot', methods=["GET"])
def get_boxplot():
    plt.clf()
    df = storage.get('csv_data')

    if df is None:
        return jsonify({"error": "No data available to plot."})
    
    try:
        #converts python string to filetype object so that pandas can read it
        df = pd.read_csv(io.StringIO(df))

        target_order = ['Legitimate', 'Suspicious', 'Phishing']
        plot_data = [df[df['Classification'] == i]['Final Score'].dropna() for i in target_order]
        
        #boxplot
        fig, ax = plt.subplots(figsize=(8, 6))
        box = ax.boxplot(plot_data, labels=target_order, patch_artist=True)

        ax.set_title('Final Score by Classification')
        ax.set_ylabel('Final Score')
        ax.set_xlabel('Classification')
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        img = io.BytesIO()
        plt.savefig(img, format='png')
        plot_url = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()

        return jsonify({"plot_url": plot_url})
    except Exception as e:
        plt.close()
        return jsonify({"error": "Failed to generate graph"})

if __name__ == '__main__':
    app.run(debug=True, port=5500)