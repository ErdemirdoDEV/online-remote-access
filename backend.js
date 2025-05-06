
const express = require('express');
const WebSocket = require('ws');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let viewers = [];

wss.on('connection', (ws, req) => {
    ws.isStreamer = false;

    ws.on('message', (data, isBinary) => {
        if (isBinary) {
            viewers.forEach(viewer => {
                if (viewer.readyState === WebSocket.OPEN) viewer.send(data, { binary: true });
            });
        } else {
            const msg = data.toString();
            try {
                const parsedMsg = JSON.parse(msg);
                const controlEvents = ['keypress', 'mouseclick', 'mousemove'];

                if (controlEvents.includes(parsedMsg.type) && ws.isStreamer === false) {
                    wss.clients.forEach(client => {
                        if (client.isStreamer && client.readyState === WebSocket.OPEN) {
                            client.send(msg);
                        }
                    });
                }
            } catch {
                if (msg === "iamstreamer") {
                    ws.isStreamer = true;
                    console.log("[✔] Streamer connected.");
                }
            }
        }
    });

    ws.on('close', () => {
        if (!ws.isStreamer) {
            viewers = viewers.filter(v => v !== ws);
        } else {
            console.log("[✖] Streamer disconnected.");
        }
    });

    if (!ws.isStreamer) viewers.push(ws);
});

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

server.listen(process.env.PORT || 3000, () => {
    console.log("✅ Server running at http://localhost:3000");
});
