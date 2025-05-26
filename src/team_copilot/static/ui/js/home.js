let accessToken = null;

function updateChatState() {
    // DOM elements
    const chatMain = document.getElementById("chat-main");

    if (accessToken) {
        chatMain.classList.remove("disabled");
    } else {
        chatMain.classList.add("disabled");
    }
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

        // Disable the button
        sendButton.disabled = true;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // DOM elements
    const messageInput = document.getElementById("message-input");
    const sendButton = document.getElementById("send-button");

    // Set the chat initial state based on the access token
    updateChatState();

    // Set the initial Send Button state
    sendButton.disabled = !messageInput.value.trim();

    // Add an input event listener to enable/disable the Send Button based on the value
    // of the Message Input.
    messageInput.addEventListener("input", function () {
        sendButton.disabled = !messageInput.value.trim();
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
    sendButton.addEventListener("click", function () {
        sendMessage();
    });
});
