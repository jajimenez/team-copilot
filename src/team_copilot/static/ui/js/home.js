const loginUrl = "/api/auth/login";
const chatUrl = "/api/chat";

let accessToken = null;
let accessTokenUsername = null;
let loginError = null;
let lastBotMessageIndex = 0;

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

function addUserMessage(message) {
    // DOM elements
    const chatMessages = document.getElementById("chat-messages");

    // Get current date and time
    const now = new Date();
    const formattedNow = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Create a new message element given the HTML text
    const messageElement = document.createElement("div");

    messageElement.innerHTML = `
        <div class="message user-message">
            <div class="message-content">
                <i class="bi bi-person me-2"></i>
                <span>${message}</span>
            </div>
            <div class="message-timestamp text-end">
                ${formattedNow}
            </div>
        </div>
    `;

    // Append the new message element to the chat messages container
    chatMessages.appendChild(messageElement);

    // Scroll to the bottom of the chat messages container
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addBotMessage() {
    // DOM elements
    const chatMessages = document.getElementById("chat-messages");

    // Update the last bot message index
    lastBotMessageIndex++;

    // Create a new message element given the HTML text
    const messageElement = document.createElement("div");

    messageElement.innerHTML = `
        <div class="message bot-message" id="bot-message-${lastBotMessageIndex}">
            <div class="message-content">
                <i class="bi bi-robot me-2"></i>
                <span id="bot-message-message-${lastBotMessageIndex}">...</span>
            </div>
            <div class="message-timestamp" id="bot-message-timestamp-${lastBotMessageIndex}">
                Thinking...
            </div>
        </div>
    `;

    // Append the new message element to the chat messages container
    chatMessages.appendChild(messageElement);

    // Scroll to the bottom of the chat messages container
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendBotMessage(text, last) {
    // DOM elements
    const botMessageMessageElement = document.getElementById(`bot-message-message-${lastBotMessageIndex}`);

    // Remove the last "..." characters at the end of the message
    if (botMessageMessageElement.innerText.endsWith("...")) {
        botMessageMessageElement.innerText = botMessageMessageElement.innerText.slice(0, -3);
    }

    // Replace trailing spaces with non-breaking spaces to preserve them
    const nbsText = text.replace(/ +$/, match => '\u00A0'.repeat(match.length));

    // Append the text to the last bot message element
    botMessageMessageElement.innerText += nbsText;

    // If this is the last message, add "..." back at the end
    if (!last) {
        botMessageMessageElement.innerText += "...";
    }
}

function markBotMessageAsError(error = null) {
    // DOM elements
    const botMessageElement = document.getElementById(`bot-message-${lastBotMessageIndex}`);
    const botMessageMessageElement = document.getElementById(`bot-message-message-${lastBotMessageIndex}`);

    botMessageElement.classList.remove("bot-message");
    botMessageElement.classList.add("bot-error-message");

    if (error) botMessageMessageElement.innerText = error;
}

function updateBotMessageTimestamp() {
    // DOM elements
    const botMessageTimestampElement = document.getElementById(`bot-message-timestamp-${lastBotMessageIndex}`);

    // Get current date and time
    const now = new Date();
    const formattedNow = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Update the timestamp of the last bot message
    botMessageTimestampElement.innerText = formattedNow;
}

function sendMessage() {
    // DOM elements
    const messageInput = document.getElementById("message-input");

    // Get the trimmed value of the Message Input field
    const message = messageInput.value.trim();

    // Add a user message to the chat messages container
    addUserMessage(message);

    // Add a bot message placeholder to the chat messages container
    addBotMessage();

    if (message) {
        // Send the message to the API
        fetch(chatUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${accessToken}`
            },
            body: JSON.stringify({ text: message })
        })
        .then(async response => {
            if (!response.body) throw new Error("No response body.");

            // Read streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            let buffer = "";
            let streamingEnd = false;

            while (!streamingEnd) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Process complete SSE events (separated by double newlines)
                let eventEnd;

                while ((eventEnd = buffer.indexOf("\n\n")) !== -1) {
                    const rawEvent = buffer.slice(0, eventEnd).trim();
                    buffer = buffer.slice(eventEnd + 2);

                    // Only process lines starting with "data: "
                    if (rawEvent.startsWith("data: ")) {
                        const eventDataJsonStr = rawEvent.slice(6);

                        try {
                            const eventData = JSON.parse(eventDataJsonStr);

                            // Append the text to the last bot message element
                            appendBotMessage(eventData.text, eventData.last);

                            // Check if this is the last event
                            if (eventData.last) {
                                streamingEnd = true;

                                // If the last event indicates an error, mark the bot message as an error
                                if (eventData.error) markBotMessageAsError(eventData.error);

                                break;
                            }
                        } catch (e) {
                            markBotMessageAsError(e.message)
                        }
                    }
                }
            }
        })
        .catch(error => {
            const errorMsg = error?.message || "Network error";
            markBotMessageAsError(errorMsg);
        })
        .finally(() => {
            // Enable the input field again
            messageInput.disabled = false;

            // Update the timestamp of the bot message
            updateBotMessageTimestamp();
        });

        // Disable and clear the input field after sending
        messageInput.disabled = true;
        messageInput.value = "";

        // Update the UI
        updateChatMain();
    }
}

function updateLoginModal() {
    // DOM elements
    const loginModalError = document.getElementById("login-modal-error");

    if (loginError) {
        loginModalError.textContent = loginError;
        loginModalError.hidden = false;
    } else {
        loginModalError.textContent = "";
        loginModalError.hidden = true;
    }
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

function logout() {
    // DOM elements
    const chatMessages = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");

    // Clear the access token and username
    accessToken = null;
    accessTokenUsername = null;

    // Clear the chat messages
    chatMessages.innerHTML = "";

    // Clear the message input field
    messageInput.value = "";

    // Update the UI
    updateMain();
    updateChatMain();
}

function onLogin() {
    // DOM elements
    const loginModalUsername = document.getElementById("login-modal-username");
    const loginModalPassword = document.getElementById("login-modal-password");

    const username = loginModalUsername.value.trim();
    const password = loginModalPassword.value;

    if (username && password) {
        login(username, password);
    } else {
        loginError = "Username and password cannot be empty.";
        updateLoginModal();
    }
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
        logout();
    });

    // Add an input event listener to enable/disable the Send button based on the value
    // of the Message Input field.
    messageInput.addEventListener("input", function () {
        updateChatMain();
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

    // Add a keypress event listener to the Username and Password fields of the Login
    // form to log in when pressing the Enter key.
    loginModalUsername.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            // Prevent the default behavior (like form submission)
            event.preventDefault();

            onLogin();
        }
    });

    loginModalPassword.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            // Prevent the default behavior (like form submission)
            event.preventDefault();

            onLogin();
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
        onLogin();
    });
});
