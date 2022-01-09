async function postData(url = '', data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        headers: {
            'Content-Type': 'application/json'
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
}
function verifyPassword() {
    var pass = document.getElementById("pass").value;
    var confirm_pass = document.getElementById("confPass").value;
    var validation = pass.localeCompare(confirm_pass);
    if (validation === 0) {
        return true;
    } else {
        alert("Passwords Do Not Match");
        return false;
    }
}
document.addEventListener("DOMContentLoaded", () => {
    registerForm.addEventListener('submit', s => {
        s.preventDefault();
        if(verifyPassword()) {
            data = {
                "name": document.getElementById("fname").value,
                "lname": document.getElementById("lname").value,
                "username": document.getElementById("username").value,
                "email": document.getElementById("email").value,
                "password": document.getElementById("pass").value,
                "country": document.getElementById("country").value,
                "city": document.getElementById("city").value,
                "address": document.getElementById("address").value
            };
            postData('/auth/register', data)
                .then(data => {
                    console.log(data.ok);
                    if (data.ok) {
                        console.log('Registered successfully!:');
                        window.location.href = "/auth/login"
                    } else {
                        console.error('Register failed!:');
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    });
});