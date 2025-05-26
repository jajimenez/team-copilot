const loginUrl = "/auth/login";
let accessToken = null;
let accessTokenUsername = null;
let loginError = null;

function updateMain() {
    // DOM elements
    const statusText = document.getElementById("status-text");
    const loginButton = document.getElementById("login-button");
    const logoutButton = document.getElementById("logout-button");
    const chatMain = document.getElementById("chat-main");

    if (accessToken) {
        statusText.textContent = `Welcome, ${accessTokenUsername}`;
        loginButton.hidden = true;
        logoutButton.hidden = false;
        chatMain.classList.remove("disabled");
    } else {
        statusText.textContent = "Please log in to chat";
        loginButton.hidden = false;
        logoutButton.hidden = true;
        chatMain.classList.add("disabled");
    }
}

function updateChatMain() {
    // DOM elements
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");

    sendButton.disabled = !messageInput.value.trim();
}

function sendMessage() {
    // DOM elements
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");

    // Get the trimmed value of the Message Input
    const message = messageInput.value.trim();

    if (message) {
        // TO-DO: Implement the logic to send the message to the API
        console.log("Message sent:", message);

        // Clear the input field after sending
        messageInput.value = "";

        // Update the UI
        updateChatMain();
    }
}

function updateLoginModal() {
    // DOM elements
    const loginModalUsername = document.getElementById("login-modal-username");
    const loginModalPassword = document.getElementById("login-modal-password");
    const loginModalError = document.getElementById("login-modal-error");
    const loginModalLoginButton = document.getElementById("login-modal-login-button");

    if (loginError) {
        loginModalError.textContent = loginError;
        loginModalError.hidden = false;
    } else {
        loginModalError.textContent = "";
        loginModalError.hidden = true;
    }

    loginModalLoginButton.disabled = !(
        loginModalUsername.value.trim() &&
        loginModalPassword.value.trim()
    );
}

function login(username, password) {
    // DOM elements
    const loginModal = document.getElementById("login-modal");
    const loginModalPassword = document.getElementById("login-modal-password");

    accessToken = null;
    accessTokenUsername = null;
    loginError = null;

    // Request datas
    const data = new FormData();

    data.append("username", username);
    data.append("password", password);

    // Make HTTP request
    fetch(loginUrl, {
        method: "POST",
        body: data,
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(data => {
                const message = data?.data?.[0]?.message || "Authentication error.";
                throw new Error(message);
            });
        }
    })
    .then(data => {
        // Save the access token
        accessToken = data["access_token"];
        accessTokenUsername = username;

        // Close the login modal
        const modal = bootstrap.Modal.getInstance(loginModal);
        modal.hide();
    })
    .catch(error => {
        loginError = error.message || "An error occurred during login.";
    })
    .finally(() => {
        loginModalPassword.value = "";

        // Update the UI
        updateMain();
        updateChatMain();
        updateLoginModal();
    });
}

document.addEventListener("DOMContentLoaded", function () {
    // DOM elements
    const loginButton = document.getElementById("login-button");
    const logoutButton = document.getElementById("logout-button");
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");
    const loginModal = document.getElementById("login-modal");
    const loginModalUsername = document.getElementById("login-modal-username");
    const loginModalPassword = document.getElementById("login-modal-password");
    const loginModalLoginButton = document.getElementById("login-modal-login-button");

    // Set the UI
    updateMain();
    updateChatMain();

    // Add a click event listener to the Login button to update the modal. The modal
    // will be opened automatically by Bootstrap when the button is clicked.
    loginButton.addEventListener("click", function () {
        // Update the login modal UI
        updateLoginModal();
    });

    // Add a click event listener to the Logout button to log out
    logoutButton.addEventListener("click", function () {
        // Clear the access token and username
        accessToken = null;
        accessTokenUsername = null;

        // Update the UI
        updateMain();
        updateChatMain();
    });

    // Add an input event listener to enable/disable the Send button based on the value
    // of the Message Input field.
    messageInput.addEventListener("input", function () {
        //sendButton.disabled = !messageInput.value.trim();
        updateMain();
    });

    // Add a keypress event listener to the Message Input to send the message when
    // pressing the Enter key.
    messageInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            // Prevent the default behavior (like form submission)
            event.preventDefault();

            // Only send the message if the button is enabled (i.e. there is text)
            if (!sendButton.disabled) {
                sendMessage();
            }
        }
    });

    // Add a click event listener to the Send Button to send the message
    sendButton.addEventListener("click", function () { sendMessage(); });

    // Add an event listener for when the Login modal is dismissed
    loginModal.addEventListener("hidden.bs.modal", function () {
        // Clear the input fields
        loginModalUsername.value = "";
        loginModalPassword.value = "";
        loginError = null;

        // Update the UI
        updateLoginModal();
    });

    // Add an input event listener to enable/disable the Log In button of the Login form
    // based on the value of the username and password fields.
    loginModalUsername.addEventListener("input", function () { updateLoginModal(); });
    loginModalPassword.addEventListener("input", function () { updateLoginModal(); });

    // Add a click event listener to the Log In button of the Login form to log in
    loginModalLoginButton.addEventListener("click", function () {
        // DOM elements
        const loginModalUsername = document.getElementById("login-modal-username");
        const loginModalPassword = document.getElementById("login-modal-password");

        const username = loginModalUsername.value.trim();
        const password = loginModalPassword.value;

        if (username && password) {
            loginError = null;
            login(username, password);
        } else {
            loginError = "Username and password cannot be empty.";
            updateLoginModal();
        }
    });
});
