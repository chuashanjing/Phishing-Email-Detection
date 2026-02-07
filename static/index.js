//remove specific domains when x is clicked
function removeDomain(domain){
    // gets all the buttons with class filter-button
    const filterButtons = document.querySelectorAll('.filter-button')
    // loop through the array
    filterButtons.forEach(button => {
        //check if button <p> contains the domain text, if include remove entire button
        if (button.querySelector('p').innerText === domain) {
            button.remove();
        }
    });

    //sends post request to route '/remove_domain'
    fetch('/remove_domain', {
        method: 'POST',
        //tells it that it is in json format
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ domain: domain }) //e.g domain:@google.com
    })
    .then(response => response.json())
    .then(data => {
        //reloads page after removing filter
        if(data.success){
            console.log(domain + "removed from whitelist");
            location.reload();
        }
    });
}

//input is the csv uploaded
function upload_csv(input){
    //use formdata to send csv file to server
    const formData = new FormData();
    formData.append('csvFile', input.files[0])

    fetch('/upload_csv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        //remove upload box
        document.querySelector(".csvForm-ct").remove()
        //add tables into the table container
        document.getElementById("checkbutton").style.display = "block";
        document.getElementById("table").style.display = "block";
        document.querySelector(".showTable").innerHTML = data.table;
    })
    .catch(err => console.log(err));

}

function openUpload(){
    const fileInput = document.getElementById('formFile');

    fileInput.click()
}


