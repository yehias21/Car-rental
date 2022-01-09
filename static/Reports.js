function displaynone() {
    document.getElementById("allReservForm").style.display = "none";
    document.getElementById("carReservForm").style.display = "none";
    document.getElementById("cusReservForm").style.display = "none";
    document.getElementById("payments").style.display = "none";
    document.getElementById("statusForm").style.display = "none";
    document.getElementById("avaibForm").style.display = "none";
}

function showform(formNUM) {
    displaynone();
    switch (formNUM) {
        case 1:
            document.getElementById("allReservForm").style.display = "block";
            break;
        case 2:
            document.getElementById("carReservForm").style.display = "block";
            break;
        case 3:
            document.getElementById("cusReservForm").style.display = "block";
            break;
        case 4:
            document.getElementById("payments").style.display = "block";

            break;
        case 5:
            document.getElementById("statusForm").style.display = "block";
            break;
        case 6:
            document.getElementById("avaibForm").style.display = "block";
            break;
    }
}

function postData(url = '', data = {}) {
    // Default options are marked with *
    const response = fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
}

document.addEventListener("DOMContentLoaded", () => {
    displaynone();
    document.getElementById("allReservForm").style.display = "block";
    allReservForm.addEventListener('submit', s => {
        s.preventDefault();
        data = {
            'start_date':document.getElementById("arDate1").value,
            'end_date': document.getElementById("arDate2").value
        };
        postData('/admin/reports/reservations', data)
    });
    carReservForm.addEventListener('submit', s => {
        s.preventDefault();
         data = {
             'car':document.getElementById("crId").value,
            'start_date':document.getElementById("crDate1").value,
            'end_date': document.getElementById("crDate2").value
        };
        postData('/admin/reports/car_reservations', data)
    });
    cusReservForm.addEventListener('submit', s => {
        s.preventDefault();
          data = {
             'customer':document.getElementById("cusrID").value
        };
        postData('/admin/reports/customer_reservations', data)
    });
    payments.addEventListener('submit', s => {
        s.preventDefault();
      data = {
             'customer':document.getElementById("pID").value
        };
        postData('/admin/reports/payments', data)
    });
    statusForm.addEventListener('submit', s => {
        s.preventDefault();
          data = {
             'date':document.getElementById("sfDate").value
        };
        postData('/admin/reports/status', data)
    });
    avaibForm.addEventListener('submit', s => {
        s.preventDefault();
           data = {
             'date':document.getElementById("afDate").value
        };
        postData('/admin/reports/available_cars', data)
    });
});