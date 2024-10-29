let websocket;
let room;
let username;

function joinRoom() {
    const room = document.getElementById("roomInput").value;
    const username = document.getElementById("username").value;
    console.log(room, username);
    if (!room || !username) {
        alert("Please enter a room and username");
        logMessage("Please enter a room and username");
        return;
    }


    websocket = new WebSocket("ws://localhost:8001");
    let connectionEstablished = false;

    websocket.onopen = () => {
        connectionEstablished = true;
        websocket.send(JSON.stringify({ type: "join", username: username, room_id: room }));
        const chatbox = document.getElementById("chatbox");
        document.getElementById("connect").style.display = "none";
        document.getElementById("disconnect").style.display = "block";
        chatbox.innerHTML = "";
    };

    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.username && data.username === "System") {
            logMessage(`${data.username}: ${data.message}`);
        }
        else if (data.type === "error") {
            logMessage(`System: ${data.message}`);
            document.getElementById("connect").style.display = "block";
            document.getElementById("disconnect").style.display = "none";
        }
        else {
            logMessage(`Client ${data.username}: ${data.message}`);
        }
    };

    websocket.onclose = () => {
        const chatbox = document.getElementById("chatbox");
        chatbox.innerHTML = "";
        if (!connectionEstablished) {
            logMessage("Unable to connect to server");
        }
        disconnect(username);
        logMessage("Disconnected from server");
        document.getElementById("connect").style.display = "block";
        document.getElementById("disconnect").style.display = "none";
    };
}

function sendMessage() {
    const message = document.getElementById("messageInput").value;
    if (websocket.readyState !== WebSocket.OPEN) {
        alert("Not connected to server");
        logMessage("Not connected to server");
        return;
    }
    websocket.send(JSON.stringify({ type: "message", username: username, message: message }));
    document.getElementById("messageInput").value = "";
}
function disconnect(username) {
    websocket.send(JSON.stringify({ type: "quit", username: username }));
    websocket.close();
}

function logMessage(message) {
    const chatbox = document.getElementById("chatbox");
    chatbox.innerHTML += message + "<br>";
    chatbox.scrollTop = chatbox.scrollHeight;
}

window.addEventListener("beforeunload", () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ type: "quit", username: username }));
        websocket.close();
    }
});