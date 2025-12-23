# 🌐 Guía Completa de WebRTC

Una explicación profunda de cómo funciona WebRTC (Web Real-Time Communication).

---

## 📖 ¿Qué es WebRTC?

**WebRTC** (Web Real-Time Communication) es una tecnología que permite **comunicación en tiempo real** directamente entre navegadores sin necesidad de un servidor intermediario.

### Casos de Uso Comunes:
- 📞 Videollamadas (Zoom, Google Meet, Discord)
- 💬 Chat en tiempo real
- 🎮 Juegos multijugador
- 📁 Transferencia de archivos P2P
- 🎥 Streaming en vivo
- 👥 Conferencias virtuales

---

## 🏗️ Arquitectura de WebRTC

### Comunicación Tradicional (Cliente-Servidor)
```
[Navegador A] → [Servidor] → [Navegador B]
     ↓              ↓              ↓
  Subir        Almacenar       Descargar
  datos         datos           datos
```

**Problemas:**
- ❌ Latencia alta (datos pasan por servidor)
- ❌ Carga en el servidor
- ❌ Costos de ancho de banda
- ❌ Privacidad (servidor ve todos los datos)

### Comunicación WebRTC (Peer-to-Peer)
```
[Navegador A] ←→ DIRECTO ←→ [Navegador B]
     ↓                           ↓
  Audio/Video              Audio/Video
  Datos                    Datos
```

**Ventajas:**
- ✅ Latencia muy baja (comunicación directa)
- ✅ Sin carga en servidor (solo señalización)
- ✅ Escalable (cada conexión es P2P)
- ✅ Mayor privacidad (conexión cifrada)

---

## 🔧 Componentes de WebRTC

### 1. APIs Principales

#### a) MediaStream (getUserMedia)
Accede a cámara y micrófono.

```javascript
// Pedir permiso para acceder a cámara/micrófono
const stream = await navigator.mediaDevices.getUserMedia({
    video: true,  // Activar cámara
    audio: true   // Activar micrófono
});

// Mostrar video en elemento HTML
const videoElement = document.getElementById('myVideo');
videoElement.srcObject = stream;
```

**¿Qué hace?**
- Solicita permisos al usuario
- Captura video/audio del dispositivo
- Retorna un MediaStream

#### b) RTCPeerConnection
La conexión P2P entre navegadores.

```javascript
// Crear conexión
const pc = new RTCPeerConnection({
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
});

// Agregar stream local
stream.getTracks().forEach(track => {
    pc.addTrack(track, stream);
});

// Recibir stream remoto
pc.ontrack = (event) => {
    remoteVideo.srcObject = event.streams[0];
};
```

**¿Qué hace?**
- Establece conexión P2P
- Negocia códecs de audio/video
- Maneja ICE (descubrimiento de red)
- Transmite audio/video

#### c) RTCDataChannel
Canal de datos para enviar información.

```javascript
// Crear canal de datos
const dataChannel = pc.createDataChannel('chat');

// Enviar mensaje
dataChannel.send('Hola!');

// Recibir mensaje
dataChannel.onmessage = (event) => {
    console.log('Mensaje recibido:', event.data);
};
```

**¿Qué hace?**
- Envía datos arbitrarios (texto, archivos, JSON)
- Baja latencia
- Ordenado o no ordenado
- Confiable o no confiable

---

## 🔄 Proceso de Conexión WebRTC

WebRTC necesita **señalización** (signaling) para establecer la conexión inicial.

### El Problema: NAT
```
[Tu computadora]        [Router/Firewall]        [Internet]
   192.168.1.10    →    Firewall/NAT        →   IP pública
```

Tu navegador no conoce su IP pública directamente. **Necesita descubrirla.**

### Solución: Proceso de Señalización

```
Peer A                Servidor de              Peer B
                     Señalización
  |                       |                       |
  |--[1] Conectar------->|                       |
  |                       |<--[2] Conectar--------|
  |                       |                       |
  |--[3] Crear Offer---->|                       |
  |                       |--[4] Enviar Offer---->|
  |                       |                       |
  |                       |<--[5] Crear Answer----|
  |<--[6] Enviar Answer--|                       |
  |                       |                       |
  |--[7] ICE Candidates->|                       |
  |                       |--[8] ICE Candidates-->|
  |                       |                       |
  |<=============CONEXIÓN DIRECTA================>|
```

---

## 📝 Paso a Paso Detallado

### Paso 1: Crear Offer (Peer A)

```javascript
// Peer A crea una oferta de conexión
const offer = await pc.createOffer();

// Establecer la descripción local
await pc.setLocalDescription(offer);

// Enviar offer a Peer B vía servidor de señalización
sendToSignalingServer({
    type: 'offer',
    offer: offer,
    target: 'peer-b-id'
});
```

**¿Qué contiene el Offer?**
```json
{
  "type": "offer",
  "sdp": "v=0\no=- ... // Descripción de medios soportados
         m=audio 9 UDP/TLS/RTP/SAVPF 111 103 ...
         m=video 9 UDP/TLS/RTP/SAVPF 96 97 ..."
}
```

El **SDP** (Session Description Protocol) incluye:
- Códecs de audio/video soportados
- Formatos de medios
- Configuración de encriptación
- Información de red

### Paso 2: Recibir Offer y Crear Answer (Peer B)

```javascript
// Peer B recibe el offer
signalingServer.on('offer', async (offer, fromPeer) => {
    // Establecer descripción remota
    await pc.setRemoteDescription(offer);

    // Crear respuesta
    const answer = await pc.createAnswer();

    // Establecer descripción local
    await pc.setLocalDescription(answer);

    // Enviar answer de vuelta a Peer A
    sendToSignalingServer({
        type: 'answer',
        answer: answer,
        target: fromPeer
    });
});
```

### Paso 3: Recibir Answer (Peer A)

```javascript
// Peer A recibe el answer
signalingServer.on('answer', async (answer) => {
    await pc.setRemoteDescription(answer);
    // ¡Ya tienen las descripciones de ambos lados!
});
```

### Paso 4: Intercambiar ICE Candidates

```javascript
// Cuando se descubren candidatos de red
pc.onicecandidate = (event) => {
    if (event.candidate) {
        // Enviar candidato al otro peer
        sendToSignalingServer({
            type: 'ice-candidate',
            candidate: event.candidate,
            target: 'other-peer-id'
        });
    }
};

// Recibir candidatos del otro peer
signalingServer.on('ice-candidate', async (candidate) => {
    await pc.addIceCandidate(candidate);
});
```

**¿Qué es un ICE Candidate?**
```javascript
{
    candidate: "candidate:1 1 UDP 2122260223 192.168.1.10 54321 typ host",
    sdpMLineIndex: 0,
    sdpMid: "0"
}
```

Contiene:
- IP y puerto del peer
- Tipo (host, srflx, relay)
- Prioridad
- Protocolo

---

## 🌐 NAT Traversal (Cómo Conectarse a Través de Firewalls)

### Tipos de Candidatos ICE:

#### 1. Host Candidate (IP Local)
```
Tipo: host
IP: 192.168.1.10:54321
```
Tu IP privada en la red local. Solo funciona si ambos peers están en la misma red.

#### 2. Server Reflexive (srflx) - STUN
```
Tipo: srflx
IP: 203.0.113.45:12345
```
Tu IP pública descubierta por STUN server.

**¿Qué es STUN?**
```
[Tu Navegador] → STUN Server → "Tu IP pública es 203.0.113.45:12345"
```

STUN (Session Traversal Utilities for NAT):
- Servidor público que te dice tu IP pública
- Gratis (Google, Mozilla tienen servidores STUN)
- Funciona para ~70% de casos

#### 3. Relay Candidate - TURN
```
Tipo: relay
IP: turn-server.com:3478
```
Cuando STUN falla, usar servidor relay (TURN).

**¿Qué es TURN?**
```
[Peer A] → TURN Server ← [Peer B]
```

TURN (Traversal Using Relays around NAT):
- Servidor que retransmite los datos
- Funciona siempre (100%)
- Cuesta dinero (consume ancho de banda)
- Usado como último recurso

### Configuración Típica:

```javascript
const pc = new RTCPeerConnection({
    iceServers: [
        // STUN servers (gratis)
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },

        // TURN server (de pago)
        {
            urls: 'turn:turn.example.com:3478',
            username: 'user',
            credential: 'pass'
        }
    ]
});
```

---

## 🔐 Seguridad en WebRTC

### Encriptación Automática

WebRTC **siempre** está encriptado:

```
DTLS (Datagram Transport Layer Security)
  ↓
SRTP (Secure Real-time Transport Protocol)
  ↓
Audio/Video cifrado
```

**No se puede desactivar.** Esto garantiza:
- ✅ Confidencialidad (nadie puede espiar)
- ✅ Integridad (datos no pueden ser modificados)
- ✅ Autenticación (verificas con quién hablas)

### Perfect Forward Secrecy

Cada sesión usa claves únicas. Si una sesión se compromete, las demás están seguras.

---

## 📊 Flujo Completo de una Videollamada

### 1. Usuario A inicia llamada

```javascript
// 1. Obtener cámara y micrófono
const localStream = await navigator.mediaDevices.getUserMedia({
    video: true,
    audio: true
});

// 2. Crear conexión
const pc = new RTCPeerConnection(config);

// 3. Agregar stream local
localStream.getTracks().forEach(track => {
    pc.addTrack(track, localStream);
});

// 4. Crear offer
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

// 5. Enviar offer a servidor de señalización
socket.send(JSON.stringify({
    type: 'offer',
    offer: offer,
    to: 'user-b'
}));
```

### 2. Usuario B recibe y responde

```javascript
// Recibir offer
socket.on('offer', async (data) => {
    // 1. Configurar descripción remota
    await pc.setRemoteDescription(data.offer);

    // 2. Obtener propio stream
    const localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
    });

    // 3. Agregar a conexión
    localStream.getTracks().forEach(track => {
        pc.addTrack(track, localStream);
    });

    // 4. Crear respuesta
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    // 5. Enviar answer
    socket.send(JSON.stringify({
        type: 'answer',
        answer: answer,
        to: 'user-a'
    }));
});
```

### 3. Intercambio ICE

```javascript
// Ambos lados
pc.onicecandidate = (event) => {
    if (event.candidate) {
        socket.send(JSON.stringify({
            type: 'ice-candidate',
            candidate: event.candidate,
            to: 'other-user'
        }));
    }
};

socket.on('ice-candidate', async (data) => {
    await pc.addIceCandidate(data.candidate);
});
```

### 4. Conexión Establecida

```javascript
pc.ontrack = (event) => {
    // Recibir stream remoto
    const remoteVideo = document.getElementById('remote-video');
    remoteVideo.srcObject = event.streams[0];
};

pc.onconnectionstatechange = () => {
    console.log('Estado:', pc.connectionState);
    // "connecting" → "connected" → "disconnected"
};
```

---

## 💬 Data Channels en Detalle

### Crear Canal de Datos

```javascript
// Peer A crea el canal
const dataChannel = pc.createDataChannel('chat', {
    ordered: true,        // Mensajes en orden
    maxRetransmits: 3    // Reintentos
});

// Peer B recibe el canal
pc.ondatachannel = (event) => {
    const dataChannel = event.channel;

    dataChannel.onmessage = (e) => {
        console.log('Mensaje:', e.data);
    };
};
```

### Configuraciones del Canal

```javascript
const channel = pc.createDataChannel('myChannel', {
    // Ordenado
    ordered: true,          // true = SCTP, false = UDP-like

    // Confiabilidad
    maxRetransmits: 3,      // Máximo 3 reintentos
    // O usar:
    maxPacketLifeTime: 3000, // Máximo 3 segundos

    // Protocolo
    protocol: 'json',       // Opcional, para apps

    // Negociación
    negotiated: false,      // Automático
    id: 1                   // ID manual si negotiated=true
});
```

### Tipos de Datos Soportados

```javascript
// Texto
dataChannel.send('Hola!');

// Binario (ArrayBuffer)
const buffer = new ArrayBuffer(8);
dataChannel.send(buffer);

// Blob
const blob = new Blob(['datos'], { type: 'text/plain' });
dataChannel.send(blob);

// JSON (serializar primero)
dataChannel.send(JSON.stringify({ msg: 'Hola' }));
```

### Transferir Archivos

```javascript
// Enviar archivo
const file = document.getElementById('fileInput').files[0];
const chunkSize = 16384; // 16KB por chunk
let offset = 0;

const readNextChunk = () => {
    const slice = file.slice(offset, offset + chunkSize);
    const reader = new FileReader();

    reader.onload = (e) => {
        dataChannel.send(e.target.result);
        offset += chunkSize;

        if (offset < file.size) {
            readNextChunk();
        } else {
            dataChannel.send('EOF'); // Fin del archivo
        }
    };

    reader.readAsArrayBuffer(slice);
};

readNextChunk();
```

---

## 🎯 Servidor de Señalización

WebRTC necesita un servidor solo para **señalización** (intercambiar offer/answer/ICE).

### Opción 1: WebSocket (Nuestro Proyecto)

```python
# FastAPI + WebSocket
from fastapi import WebSocket

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    # Agregar a room
    connections[room_id].append(websocket)

    try:
        while True:
            # Recibir mensaje
            data = await websocket.receive_json()

            # Retransmitir a otros en el room
            for conn in connections[room_id]:
                if conn != websocket:
                    await conn.send_json(data)

    except WebSocketDisconnect:
        connections[room_id].remove(websocket)
```

### Opción 2: Socket.IO

```javascript
// Servidor Node.js
const io = require('socket.io')(3000);

io.on('connection', (socket) => {
    socket.on('join-room', (roomId) => {
        socket.join(roomId);
        socket.to(roomId).emit('user-connected');
    });

    socket.on('offer', (data) => {
        socket.to(data.room).emit('offer', data);
    });

    socket.on('answer', (data) => {
        socket.to(data.room).emit('answer', data);
    });
});
```

### Opción 3: Servicios de Terceros

- **Twilio**: API completa de WebRTC
- **Agora**: Plataforma de video/audio
- **PeerJS**: Librería simplificada
- **LiveKit**: Open source

---

## 📈 Monitoreo y Debugging

### Ver Estadísticas

```javascript
setInterval(async () => {
    const stats = await pc.getStats();

    stats.forEach(report => {
        if (report.type === 'inbound-rtp') {
            console.log('Bytes recibidos:', report.bytesReceived);
            console.log('Paquetes perdidos:', report.packetsLost);
        }

        if (report.type === 'outbound-rtp') {
            console.log('Bytes enviados:', report.bytesSent);
        }
    });
}, 1000);
```

### Chrome DevTools

```
chrome://webrtc-internals
```

Muestra:
- Todas las conexiones activas
- Estadísticas en tiempo real
- Gráficas de bitrate
- ICE candidates
- Logs detallados

### Estados de Conexión

```javascript
pc.onconnectionstatechange = () => {
    console.log(pc.connectionState);
    // "new" → "connecting" → "connected" → "disconnected" → "closed"
};

pc.oniceconnectionstatechange = () => {
    console.log(pc.iceConnectionState);
    // "new" → "checking" → "connected" → "completed"
};

pc.onicegatheringstatechange = () => {
    console.log(pc.iceGatheringState);
    // "new" → "gathering" → "complete"
};
```

---

## ⚠️ Limitaciones y Desafíos

### 1. Escalabilidad

**Problema:** WebRTC es P2P, cada conexión adicional multiplica el costo.

```
3 personas: A↔B, A↔C, B↔C = 3 conexiones
4 personas: = 6 conexiones
5 personas: = 10 conexiones
n personas: = n(n-1)/2 conexiones
```

**Solución:** SFU (Selective Forwarding Unit)

```
[Peer A] →
[Peer B] → [SFU Server] → Distribuye a todos
[Peer C] →
```

El servidor redistribuye sin decodificar (eficiente).

### 2. NAT Traversal

- ~10-30% de conexiones requieren TURN
- TURN cuesta dinero
- Configurar TURN es complejo

### 3. Compatibilidad

- Safari tiene limitaciones
- Móviles consumen batería
- Codecs diferentes entre navegadores

### 4. Calidad de Red

```javascript
// Adaptar calidad según red
pc.getSenders().forEach(sender => {
    const params = sender.getParameters();
    params.encodings[0].maxBitrate = 500000; // 500kbps
    sender.setParameters(params);
});
```

---

## 🎓 Comparación de Tecnologías

| Aspecto | WebSocket | WebRTC |
|---------|-----------|--------|
| **Tipo** | Cliente-Servidor | P2P |
| **Latencia** | Media (100-300ms) | Muy baja (10-50ms) |
| **Uso** | Chat, notificaciones | Video, audio, gaming |
| **Ancho de banda servidor** | Alto | Bajo (solo señalización) |
| **Complejidad** | Simple | Compleja |
| **Encriptación** | Opcional (WSS) | Obligatoria (DTLS) |

---

## 🚀 Ejemplo Completo: Chat con Video

```javascript
// 1. Obtener elementos
const localVideo = document.getElementById('local-video');
const remoteVideo = document.getElementById('remote-video');
const messageInput = document.getElementById('message');
const sendBtn = document.getElementById('send');
const messagesDiv = document.getElementById('messages');

// 2. Configuración
const config = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};

let pc;
let dataChannel;
let localStream;

// 3. Iniciar
async function start() {
    // Obtener stream local
    localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
    });
    localVideo.srcObject = localStream;

    // Crear conexión
    pc = new RTCPeerConnection(config);

    // Agregar tracks
    localStream.getTracks().forEach(track => {
        pc.addTrack(track, localStream);
    });

    // Recibir stream remoto
    pc.ontrack = (event) => {
        remoteVideo.srcObject = event.streams[0];
    };

    // Crear data channel para chat
    dataChannel = pc.createDataChannel('chat');

    dataChannel.onmessage = (event) => {
        showMessage(event.data, 'remote');
    };

    // Manejar ICE
    pc.onicecandidate = (event) => {
        if (event.candidate) {
            sendToServer({
                type: 'ice',
                candidate: event.candidate
            });
        }
    };

    // Crear offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    sendToServer({
        type: 'offer',
        offer: offer
    });
}

// 4. Enviar mensaje de chat
sendBtn.onclick = () => {
    const message = messageInput.value;
    dataChannel.send(message);
    showMessage(message, 'local');
    messageInput.value = '';
};

function showMessage(text, from) {
    const div = document.createElement('div');
    div.className = from;
    div.textContent = text;
    messagesDiv.appendChild(div);
}

// Iniciar cuando se carga la página
document.getElementById('start-btn').onclick = start;
```

---

## 📚 Recursos Adicionales

### Documentación Oficial
- [MDN WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [WebRTC.org](https://webrtc.org/)
- [Google WebRTC Samples](https://webrtc.github.io/samples/)

### Librerías y Frameworks
- **Simple-Peer**: Simplifica WebRTC
- **PeerJS**: Abstracción completa
- **MediaSoup**: SFU server
- **Jitsi**: Plataforma completa open-source

### Servicios
- **Twilio Video**: API comercial
- **Agora**: Plataforma global
- **Daily.co**: Video API simple

---

## 🎯 Resumen

### WebRTC en 5 Puntos:

1. **P2P directo** entre navegadores
2. **Señalización** necesaria para conectar (WebSocket/HTTP)
3. **NAT Traversal** con STUN/TURN
4. **Encriptación** obligatoria
5. **Múltiples usos**: video, audio, datos

### Flujo Típico:

```
1. getUserMedia()     → Obtener cámara/micrófono
2. createOffer()      → Crear oferta
3. setLocalDescription() → Guardar oferta local
4. [Señalización]     → Enviar offer via WebSocket
5. setRemoteDescription() → Recibir answer
6. ICE Candidates     → Descubrir red
7. ¡CONEXIÓN!         → Audio/video fluye directamente
```

---

**WebRTC es poderoso pero complejo. Este proyecto (`grtc`) es un excelente punto de partida para aprender.** 🚀
