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

document.addEventListener("DOMContentLoaded", () => {
    loginForm.addEventListener('submit', s => {
        s.preventDefault();
        data = {
            "username": document.getElementById("loginUsername").value,
            "password": document.getElementById("loginPassword").value,
            "role": document.querySelector('input[name="role"]:checked').value
        };
        postData('/auth/login', data)
            .then(data => {
                console.log(data.ok);
                if(data.ok)
                {
                    console.log('Login successfully!:');
                    window.location.href = "/auth/home"
                }
                else
                {
                    console.error('Login failed!:');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });
});