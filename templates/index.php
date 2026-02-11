<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Phishing Detection</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous">
    <link rel="stylesheet" href="../static/style.css">
    <script src="../static/index.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="#">
            <img src="../static/image/logo.png">
            <p>Phishing Email Detection</p>
        </a>
    </nav>

    
    <section id="Phishing">
        <h2>Detect Phishing Email and Domains</h2>

        <div>
            <!-- send post request to route '/'-->
            <form method="POST" action="/">
                <input type="text" id="domain" name="domain" placeholder="Whitelist: @google.com" autocomplete="off" pattern="^@.+" title="Domain must start with @" required>
            </form>

            <div class="filter">
                <!-- domains is the inputted domains ^ -->
                <!-- loop through the the list and display them -->
                {% for i in domains %}
                <div class="filter-button">
                    <p>{{ i }}</p>
                    <button onclick="removeDomain('{{ i }}')">x</button>
                </div>
                {% endfor %}

            </div>
        </div>
    </section>


    <section id="uploading">
        <!-- input box for uploading csv file, sends post request to /upload_csv in flask-->
        <form onclick="openUpload()" class="csvForm-ct" action="/upload_csv" method="POST" enctype="multipart/form-data">
            <!-- onchange: when file is uploaded -->
            <input name="csvFile" 
                onchange="upload_csv(this)" 
                type="file" 
                accept=".csv" 
                id="formFile" required>
            <div class="csvForm-text">
                <img src="../static/image/cloud.png">
                Click anywhere here to upload your CSV file
            </div>
        </form>
        <!-- empty table -->
        <form action="/rulebased" method="POST" id="phishform">
            <button id="checkbutton" style="display: none">Check Phishing</button>
        </form>

        <div id="histogram-container"></div>
        <div id="scatterplot-container"></div>
        <div id="grouped-container"></div>
        <div id="boxplot-container"></div>
        <div id="table" class="showTable mt-3" style="display: none;"></div>
    </section>

    <script>

        async function loadHistogram(){
            try {
                const response = await fetch('/get_histogram');
                const data = await response.json();
                const container = document.getElementById('histogram-container');

                if (data.plot_url){
                    container.innerHTML = `<img src="data:image/png;base64,${data.plot_url}" class="img-fluid" />`;
                }
                else {
                    console.error(data.error);
                }
            } catch (err) {
                console.log(err)
            }
        }

        async function loadScatterPlot(){
            try {
                const response = await fetch('/get_scatterplot');
                const data = await response.json();
                const container = document.getElementById('scatterplot-container');

                if (data.plot_url){
                    container.innerHTML = `<img src="data:image/png;base64,${data.plot_url}" class="img-fluid" />`;
                }
                else {
                    console.error(data.error);
                }
            } catch (err) {
                console.log(err)
            }
        }

        async function loadGroupedChart(){
            try {
                const response = await fetch('/get_grouped_chart');
                const data = await response.json();
                const container = document.getElementById('grouped-container');

                if (data.plot_url){
                    container.innerHTML = `<img src="data:image/png;base64,${data.plot_url}" class="img-fluid" />`;
                }
                else {
                    console.error(data.error);
                }
            } catch (err) {
                console.log(err)
            }
        }

        async function loadBoxPlot(){
            try {
                const response = await fetch('/get_boxplot');
                const data = await response.json();
                const container = document.getElementById('boxplot-container');

                if (data.plot_url){
                    container.innerHTML = `<img src="data:image/png;base64,${data.plot_url}" class="img-fluid" />`;
                }
                else {
                    console.error(data.error);
                }
            } catch (err) {
                console.log(err)
            }
        }
         
        document.getElementById("checkbutton").addEventListener("click", async function(event){
            //prevent the form from submitting the normal way where it just sends a request
            event.preventDefault();
            
            document.getElementById("checkbutton").style.display = "none";
            document.getElementById("table").style.display = "none";
            

            //makes sure rulebased is called first and finished
            try {
                
                const formData = new FormData();
                const response = await fetch('/rulebased', {
                    method: 'POST',
                    body: formData
                });
                //then download the csv from the response
                if (response.ok) {
                    //turn data into file
                    const blob = await response.blob();
                    //a location where the file will be at
                    const url = window.URL.createObjectURL(blob);
                    //new button created
                    const a = document.createElement('a');
                    //button has the location of the file link
                    a.href = url;
                    //download the file
                    a.download = 'rule_based_results.csv';
                    //click the link making it download
                    a.click();
                    //remove temporary url
                    window.URL.revokeObjectURL(url);
                    
                    // finally load the graph after retrieving the data
                    await loadHistogram();
                    await loadScatterPlot();
                    await loadGroupedChart();
                    await loadBoxPlot();
                } else {
                    console.error('Error processing data');
                    alert('Error processing data. Please try again.');
                }
            } catch (error) {
                console.error(error);
            }
        });

    </script>

</body>
</html>
