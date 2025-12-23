// Estado global de la aplicación
const state = {
    ws: null,
    peerId: generatePeerId(),
    roomId: null,
    peers: new Map(), // peer_id -> RTCPeerConnection
    items: []
};

// Configuración de WebRTC
const rtcConfig = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
};

// ==================== UTILIDADES ====================

function generatePeerId() {
    return 'peer-' + Math.random().toString(36).substr(2, 9);
}

function log(message, type = 'info') {
    const messagesDiv = document.getElementById('messages');
    const timestamp = new Date().toLocaleTimeString();
    const messageEl = document.createElement('div');
    messageEl.className = `message ${type}`;
    messageEl.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;
    messagesDiv.appendChild(messageEl);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ==================== CRUD OPERATIONS ====================

async function createItem() {
    const title = document.getElementById('itemTitle').value;
    const description = document.getElementById('itemDescription').value;
    const status = document.getElementById('itemStatus').value;

    if (!title) {
        alert('El título es requerido');
        return;
    }

    try {
        const response = await fetch('/api/items/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, status })
        });

        if (response.ok) {
            const item = await response.json();
            log(`Item creado: ${item.title}`, 'success');
            document.getElementById('itemTitle').value = '';
            document.getElementById('itemDescription').value = '';
            loadItems();
        } else {
            log('Error al crear item', 'error');
        }
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
}

async function createBulkItems() {
    const items = [];
    for (let i = 1; i <= 5; i++) {
        items.push({
            title: `Item Bulk ${i} - ${Date.now()}`,
            description: `Creado en bulk para demostrar concurrencia`,
            status: ['active', 'inactive', 'pending'][Math.floor(Math.random() * 3)]
        });
    }

    try {
        log('Creando 5 items en paralelo...', 'info');
        const response = await fetch('/api/items/bulk', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(items)
        });

        if (response.ok) {
            const createdItems = await response.json();
            log(`✓ ${createdItems.length} items creados en paralelo`, 'success');
            loadItems();
        } else {
            log('Error al crear items en bulk', 'error');
        }
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
}

async function loadItems() {
    const filterStatus = document.getElementById('filterStatus').value;
    let url = '/api/items/?limit=50';
    if (filterStatus) {
        url += `&status=${filterStatus}`;
    }

    try {
        const response = await fetch(url);
        const items = await response.json();
        state.items = items;
        displayItems(items);
        log(`${items.length} items cargados`, 'info');
    } catch (error) {
        log(`Error al cargar items: ${error.message}`, 'error');
    }
}

function displayItems(items) {
    const listDiv = document.getElementById('itemsList');
    listDiv.innerHTML = '';

    if (items.length === 0) {
        listDiv.innerHTML = '<p>No hay items</p>';
        return;
    }

    items.forEach(item => {
        const itemEl = document.createElement('div');
        itemEl.className = `item item-${item.status}`;
        itemEl.innerHTML = `
            <div class="item-header">
                <strong>${item.title}</strong>
                <span class="item-status">${item.status}</span>
            </div>
            <p>${item.description || 'Sin descripción'}</p>
            <div class="item-actions">
                <button onclick="updateItemStatus(${item.id}, 'active')">Active</button>
                <button onclick="updateItemStatus(${item.id}, 'inactive')">Inactive</button>
                <button onclick="updateItemStatus(${item.id}, 'pending')">Pending</button>
                <button onclick="deleteItem(${item.id})" class="delete-btn">Eliminar</button>
            </div>
            <small>ID: ${item.id} | Creado: ${new Date(item.created_at).toLocaleString()}</small>
        `;
        listDiv.appendChild(itemEl);
    });
}

async function updateItemStatus(itemId, newStatus) {
    try {
        const response = await fetch(`/api/items/${itemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            log(`Item ${itemId} actualizado a ${newStatus}`, 'success');
            loadItems();
        }
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
}

async function bulkUpdateStatus() {
    if (state.items.length === 0) {
        alert('No hay items cargados');
        return;
    }

    const itemIds = state.items.slice(0, 5).map(item => item.id);
    const newStatus = prompt('Nuevo status (active/inactive/pending):', 'active');

    if (!['active', 'inactive', 'pending'].includes(newStatus)) {
        alert('Status inválido');
        return;
    }

    try {
        log(`Actualizando ${itemIds.length} items en paralelo...`, 'info');
        const response = await fetch(`/api/items/bulk/status?new_status=${newStatus}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(itemIds)
        });

        if (response.ok) {
            const result = await response.json();
            log(`✓ ${result.updated_count} items actualizados`, 'success');
            loadItems();
        }
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
}

async function deleteItem(itemId) {
    if (!confirm('¿Eliminar este item?')) return;

    try {
        const response = await fetch(`/api/items/${itemId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            log(`Item ${itemId} eliminado`, 'success');
            loadItems();
        }
    } catch (error) {
        log(`Error: ${error.message}`, 'error');
    }
}

// ==================== WEBSOCKET & WEBRTC ====================

function connectToRoom() {
    const roomInput = document.getElementById('roomInput').value;
    if (!roomInput) {
        alert('Ingresa un Room ID');
        return;
    }

    state.roomId = roomInput;
    document.getElementById('roomId').textContent = state.roomId;
    document.getElementById('peerId').textContent = state.peerId;

    // Conectar WebSocket
    const wsUrl = `ws://localhost:8000/ws/${state.roomId}?peer_id=${state.peerId}`;
    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => {
        log('✓ Conectado al servidor WebSocket', 'success');
        document.getElementById('connectionStatus').textContent = 'Conectado';
        document.getElementById('connectionStatus').className = 'status-connected';
        document.getElementById('connectBtn').disabled = true;
        document.getElementById('disconnectBtn').disabled = false;
        document.getElementById('sendBroadcastBtn').disabled = false;
    };

    state.ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        await handleWebSocketMessage(message);
    };

    state.ws.onclose = () => {
        log('Desconectado del servidor', 'warning');
        document.getElementById('connectionStatus').textContent = 'Desconectado';
        document.getElementById('connectionStatus').className = 'status-disconnected';
        document.getElementById('connectBtn').disabled = false;
        document.getElementById('disconnectBtn').disabled = true;
        document.getElementById('sendBroadcastBtn').disabled = true;

        // Cerrar todas las conexiones peer
        state.peers.forEach(pc => pc.close());
        state.peers.clear();
        updatePeersList();
    };

    state.ws.onerror = (error) => {
        log(`Error WebSocket: ${error}`, 'error');
    };
}

function disconnectFromRoom() {
    if (state.ws) {
        state.ws.close();
        state.ws = null;
    }
}

async function handleWebSocketMessage(message) {
    console.log('Mensaje recibido:', message);

    switch (message.type) {
        case 'room_state':
            log(`Room iniciado. Peers disponibles: ${message.peers.length}`, 'info');
            // Iniciar conexión con cada peer existente
            for (const peerId of message.peers) {
                await createPeerConnection(peerId, true);
            }
            updatePeersList();
            break;

        case 'peer_joined':
            log(`Peer ${message.peer_id} se unió al room`, 'info');
            document.getElementById('peerCount').textContent = message.total_peers;
            break;

        case 'peer_left':
            log(`Peer ${message.peer_id} salió del room`, 'warning');
            if (state.peers.has(message.peer_id)) {
                state.peers.get(message.peer_id).close();
                state.peers.delete(message.peer_id);
            }
            document.getElementById('peerCount').textContent = message.total_peers;
            updatePeersList();
            break;

        case 'webrtc_signal':
            await handleWebRTCSignal(message);
            break;

        case 'broadcast_message':
            log(`📢 Mensaje de ${message.from_peer_id}: ${message.data}`, 'broadcast');
            break;
    }
}

async function createPeerConnection(remotePeerId, isInitiator) {
    if (state.peers.has(remotePeerId)) {
        return state.peers.get(remotePeerId);
    }

    const pc = new RTCPeerConnection(rtcConfig);
    state.peers.set(remotePeerId, pc);

    // Crear data channel
    const dataChannel = pc.createDataChannel('chat');
    setupDataChannel(dataChannel, remotePeerId);

    // Manejar data channel entrante
    pc.ondatachannel = (event) => {
        setupDataChannel(event.channel, remotePeerId);
    };

    // Manejar ICE candidates
    pc.onicecandidate = (event) => {
        if (event.candidate) {
            state.ws.send(JSON.stringify({
                type: 'ice_candidate',
                target_peer_id: remotePeerId,
                candidate: event.candidate
            }));
        }
    };

    pc.onconnectionstatechange = () => {
        log(`Conexión con ${remotePeerId}: ${pc.connectionState}`, 'info');
        updatePeersList();
    };

    // Si somos el iniciador, crear offer
    if (isInitiator) {
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        state.ws.send(JSON.stringify({
            type: 'offer',
            target_peer_id: remotePeerId,
            offer: offer
        }));
    }

    updatePeersList();
    return pc;
}

async function handleWebRTCSignal(message) {
    const remotePeerId = message.from_peer_id;
    const signal = message.signal;

    let pc = state.peers.get(remotePeerId);

    if (signal.type === 'offer') {
        if (!pc) {
            pc = await createPeerConnection(remotePeerId, false);
        }

        await pc.setRemoteDescription(new RTCSessionDescription(signal.offer));
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        state.ws.send(JSON.stringify({
            type: 'answer',
            target_peer_id: remotePeerId,
            answer: answer
        }));

        log(`Offer recibida de ${remotePeerId}, answer enviada`, 'info');
    } else if (signal.type === 'answer') {
        await pc.setRemoteDescription(new RTCSessionDescription(signal.answer));
        log(`Answer recibida de ${remotePeerId}`, 'info');
    } else if (signal.type === 'ice_candidate') {
        await pc.addIceCandidate(new RTCIceCandidate(signal.candidate));
    }
}

function setupDataChannel(channel, remotePeerId) {
    channel.onopen = () => {
        log(`✓ Data channel abierto con ${remotePeerId}`, 'success');
    };

    channel.onmessage = (event) => {
        log(`💬 Mensaje P2P de ${remotePeerId}: ${event.data}`, 'p2p');
    };

    channel.onclose = () => {
        log(`Data channel cerrado con ${remotePeerId}`, 'warning');
    };
}

function sendBroadcast() {
    const message = document.getElementById('broadcastMessage').value;
    if (!message) {
        alert('Ingresa un mensaje');
        return;
    }

    if (state.ws && state.ws.readyState === WebSocket.OPEN) {
        state.ws.send(JSON.stringify({
            type: 'broadcast',
            data: message
        }));
        log(`📤 Broadcast enviado: ${message}`, 'sent');
        document.getElementById('broadcastMessage').value = '';
    }
}

function updatePeersList() {
    const peersListDiv = document.getElementById('peersList');
    peersListDiv.innerHTML = '';

    if (state.peers.size === 0) {
        peersListDiv.innerHTML = '<p>No hay peers conectados</p>';
        document.getElementById('peerCount').textContent = '0';
        return;
    }

    document.getElementById('peerCount').textContent = state.peers.size;

    state.peers.forEach((pc, peerId) => {
        const peerEl = document.createElement('div');
        peerEl.className = 'peer-item';
        peerEl.innerHTML = `
            <strong>${peerId}</strong>
            <span class="peer-status peer-${pc.connectionState}">${pc.connectionState}</span>
        `;
        peersListDiv.appendChild(peerEl);
    });
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    log('Aplicación iniciada', 'info');
    loadItems();
});
