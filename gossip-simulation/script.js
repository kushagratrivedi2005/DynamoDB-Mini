// DynamoDB-MINI Gossip Protocol Visualization
// Based on the actual implementation in worker.py

class GossipNode {
    constructor(id, x, y) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.state = 'active'; // active, sending, receiving, down
        this.routingTable = new Map(); // node_id -> version_number
        this.downNodes = new Set();
        this.versionNumber = 1;
        this.stateTimer = 0;
    }

    resetState() {
        if (this.stateTimer > 0) {
            this.stateTimer--;
        } else if (this.state !== 'down') {
            this.state = 'active';
        }
    }
}

class GossipProtocolVisualization {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.nodes = [];
        this.running = false;
        this.gossipInterval = 3000; // 3 seconds as per config
        this.speedMultiplier = 1;
        this.rounds = 0;
        this.messageCount = 0;
        this.updateCount = 0;
        this.animatingMessages = [];
        this.logEntries = [];

        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    resizeCanvas() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.width = this.canvas.width;
        this.height = this.canvas.height;
        if (this.nodes.length > 0) {
            this.draw();
        }
    }

    initialize(nodeCount) {
        this.nodes = [];
        this.rounds = 0;
        this.messageCount = 0;
        this.updateCount = 0;
        this.animatingMessages = [];
        this.logEntries = [];
        this.clearLog();

        // Create nodes in a circle layout
        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const radius = Math.min(this.width, this.height) * 0.35;

        for (let i = 0; i < nodeCount; i++) {
            const angle = (i / nodeCount) * 2 * Math.PI - Math.PI / 2;
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            const node = new GossipNode(i, x, y);

            // Initialize routing table - each node knows about all others initially
            for (let j = 0; j < nodeCount; j++) {
                if (i !== j) {
                    node.routingTable.set(j, 1); // version 1
                }
            }

            this.nodes.push(node);
        }

        this.draw();
        this.updateStats();
        this.addLog('🔧', 'System initialized with ' + nodeCount + ' nodes');
    }

    startGossip() {
        if (this.running || this.nodes.length === 0) return;
        this.running = true;
        this.addLog('▶️', 'Gossip protocol started');
        this.gossipLoop();
    }

    gossipLoop() {
        if (!this.running) return;

        this.rounds++;
        const activeNodes = this.nodes.filter(n => n.state !== 'down');

        if (activeNodes.length < 2) {
            this.addLog('⚠️', 'Not enough active nodes for gossip');
            setTimeout(() => this.gossipLoop(), this.gossipInterval / this.speedMultiplier);
            return;
        }

        // Each active node picks a random peer to gossip with
        activeNodes.forEach(node => {
            // Get list of active peers (excluding self)
            const peers = activeNodes.filter(n => n.id !== node.id);
            if (peers.length === 0) return;

            // Pick random peer
            const randomPeer = peers[Math.floor(Math.random() * peers.length)];

            // Simulate gossip exchange
            this.performGossip(node, randomPeer);
        });

        this.updateStats();
        this.draw();

        setTimeout(() => this.gossipLoop(), this.gossipInterval / this.speedMultiplier);
    }

    performGossip(sender, receiver) {
        // Mark nodes as sending/receiving
        sender.state = 'sending';
        sender.stateTimer = 30;
        receiver.state = 'receiving';
        receiver.stateTimer = 30;

        this.messageCount++;
        this.animateMessage(sender.id, receiver.id);

        this.addLog('🗣️', `Node ${sender.id} → Node ${receiver.id}`);

        // Exchange routing tables (simulate the do_chit_chat function)
        let updates = 0;

        // Sender shares its routing table with receiver
        sender.routingTable.forEach((version, nodeId) => {
            const receiverVersion = receiver.routingTable.get(nodeId) || 0;
            if (version > receiverVersion) {
                receiver.routingTable.set(nodeId, version);
                updates++;
            }
        });

        // Receiver shares its routing table with sender
        receiver.routingTable.forEach((version, nodeId) => {
            const senderVersion = sender.routingTable.get(nodeId) || 0;
            if (version > senderVersion) {
                sender.routingTable.set(nodeId, version);
                updates++;
            }
        });

        // Exchange down node information
        sender.downNodes.forEach(nodeId => {
            if (!receiver.downNodes.has(nodeId)) {
                // Receiver verifies if node is actually down
                const node = this.nodes[nodeId];
                if (node && node.state === 'down') {
                    receiver.downNodes.add(nodeId);
                    updates++;
                }
            }
        });

        receiver.downNodes.forEach(nodeId => {
            if (!sender.downNodes.has(nodeId)) {
                const node = this.nodes[nodeId];
                if (node && node.state === 'down') {
                    sender.downNodes.add(nodeId);
                    updates++;
                }
            }
        });

        if (updates > 0) {
            this.updateCount += updates;
            this.addLog('✓', `  Updated ${updates} entries`);
        }
    }

    animateMessage(fromId, toId) {
        this.animatingMessages.push({
            from: fromId,
            to: toId,
            progress: 0,
            duration: (this.gossipInterval * 0.6) / this.speedMultiplier
        });
    }

    updateAnimations(deltaTime) {
        this.animatingMessages = this.animatingMessages.filter(msg => {
            msg.progress += deltaTime / msg.duration;
            return msg.progress < 1;
        });
    }

    simulateFailure() {
        const activeNodes = this.nodes.filter(n => n.state !== 'down');
        if (activeNodes.length <= 2) {
            this.addLog('⚠️', 'Cannot fail more nodes (minimum 2 required)');
            return;
        }

        const randomNode = activeNodes[Math.floor(Math.random() * activeNodes.length)];
        randomNode.state = 'down';
        randomNode.versionNumber++;

        this.addLog('❌', `Node ${randomNode.id} failed`);

        // Other nodes will discover this through gossip
        this.updateStats();
        this.draw();
    }

    stop() {
        this.running = false;
        this.addLog('⏸️', 'Gossip paused');
    }

    reset() {
        this.stop();
        const nodeCount = this.nodes.length;
        this.initialize(nodeCount);
        this.addLog('🔄', 'System reset');
    }

    calculateConvergence() {
        if (this.nodes.length === 0) return 0;

        const activeNodes = this.nodes.filter(n => n.state !== 'down');
        if (activeNodes.length === 0) return 0;

        // Check how many nodes have the same routing table knowledge
        let totalKnowledge = 0;
        let maxKnowledge = 0;

        activeNodes.forEach(node => {
            const knowledge = node.routingTable.size;
            totalKnowledge += knowledge;
            maxKnowledge = Math.max(maxKnowledge, knowledge);
        });

        const avgKnowledge = totalKnowledge / activeNodes.length;
        const convergence = maxKnowledge > 0 ? (avgKnowledge / maxKnowledge) * 100 : 0;

        return Math.min(100, convergence);
    }

    updateStats() {
        const activeCount = this.nodes.filter(n => n.state !== 'down').length;
        const downCount = this.nodes.filter(n => n.state === 'down').length;
        const convergence = this.calculateConvergence();

        document.getElementById('activeNodes').textContent = activeCount;
        document.getElementById('downNodes').textContent = downCount;
        document.getElementById('rounds').textContent = this.rounds;
        document.getElementById('messageCount').textContent = this.messageCount;
        document.getElementById('updateCount').textContent = this.updateCount;
        document.getElementById('convergence').textContent = convergence.toFixed(1) + '%';
    }

    addLog(emoji, message) {
        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        this.logEntries.push({ emoji, message, timestamp });

        // Keep only last 50 entries
        if (this.logEntries.length > 50) {
            this.logEntries.shift();
        }

        this.updateLogDisplay();
    }

    updateLogDisplay() {
        const logContainer = document.getElementById('gossipLog');
        logContainer.innerHTML = this.logEntries.map(entry =>
            `<div class="log-entry"><span class="timestamp">${entry.timestamp}</span><span class="emoji">${entry.emoji}</span>${entry.message}</div>`
        ).join('');

        // Auto-scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    clearLog() {
        this.logEntries = [];
        this.updateLogDisplay();
    }

    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Draw connections between active nodes
        const activeNodes = this.nodes.filter(n => n.state !== 'down');
        this.ctx.strokeStyle = 'rgba(255, 153, 0, 0.15)';
        this.ctx.lineWidth = 1.5;

        activeNodes.forEach((node1, i) => {
            activeNodes.slice(i + 1).forEach(node2 => {
                this.ctx.beginPath();
                this.ctx.moveTo(node1.x, node1.y);
                this.ctx.lineTo(node2.x, node2.y);
                this.ctx.stroke();
            });
        });

        // Draw animating messages
        this.animatingMessages.forEach(msg => {
            const from = this.nodes[msg.from];
            const to = this.nodes[msg.to];
            if (!from || !to) return;

            const x = from.x + (to.x - from.x) * msg.progress;
            const y = from.y + (to.y - from.y) * msg.progress;

            // Glowing message particle
            const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, 10);
            gradient.addColorStop(0, 'rgba(255, 153, 0, 1)');
            gradient.addColorStop(0.5, 'rgba(255, 153, 0, 0.6)');
            gradient.addColorStop(1, 'rgba(255, 153, 0, 0)');

            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 10, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Draw nodes
        this.nodes.forEach(node => {
            node.resetState();

            let color, glowColor, glowSize;

            switch (node.state) {
                case 'active':
                    color = '#00a8e1';
                    glowColor = 'rgba(0, 168, 225, 0.6)';
                    glowSize = 15;
                    break;
                case 'sending':
                    color = '#ff9900';
                    glowColor = 'rgba(255, 153, 0, 0.6)';
                    glowSize = 25;
                    break;
                case 'receiving':
                    color = '#7c3aed';
                    glowColor = 'rgba(124, 58, 237, 0.6)';
                    glowSize = 25;
                    break;
                case 'down':
                    color = '#6b7280';
                    glowSize = 0;
                    break;
            }

            // Glow effect
            if (glowSize > 0) {
                this.ctx.shadowBlur = glowSize;
                this.ctx.shadowColor = glowColor;
            } else {
                this.ctx.shadowBlur = 0;
            }

            // Node circle
            this.ctx.fillStyle = color;
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, 16, 0, Math.PI * 2);
            this.ctx.fill();

            // Node border
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            this.ctx.lineWidth = 2.5;
            this.ctx.stroke();

            this.ctx.shadowBlur = 0;

            // Node label
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = '700 13px Inter';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(node.id, node.x, node.y);

            // Version number below node
            this.ctx.fillStyle = 'rgba(255, 153, 0, 0.8)';
            this.ctx.font = '600 10px JetBrains Mono';
            this.ctx.fillText(`v${node.versionNumber}`, node.x, node.y + 28);
        });
    }

    animate() {
        const now = Date.now();
        const deltaTime = this.lastTime ? now - this.lastTime : 0;
        this.lastTime = now;

        if (this.animatingMessages.length > 0) {
            this.updateAnimations(deltaTime);
            this.draw();
        }

        requestAnimationFrame(() => this.animate());
    }
}

// UI Controller
class UIController {
    constructor(visualization) {
        this.viz = visualization;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Range inputs
        document.getElementById('nodeCount').addEventListener('input', (e) => {
            const value = e.target.value;
            document.getElementById('nodeCountValue').textContent = value;
            document.getElementById('nodeCountDisplay').textContent = value;
        });

        document.getElementById('gossipSpeed').addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            document.getElementById('gossipSpeedValue').textContent = value + 'x';
            this.viz.speedMultiplier = value;
        });

        // Buttons
        document.getElementById('startBtn').addEventListener('click', () => {
            const nodeCount = parseInt(document.getElementById('nodeCount').value);
            if (this.viz.nodes.length === 0) {
                this.viz.initialize(nodeCount);
            }
            this.viz.startGossip();
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
        });

        document.getElementById('stopBtn').addEventListener('click', () => {
            this.viz.stop();
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            const nodeCount = parseInt(document.getElementById('nodeCount').value);
            this.viz.stop();
            this.viz.initialize(nodeCount);
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
        });

        document.getElementById('failNodeBtn').addEventListener('click', () => {
            this.viz.simulateFailure();
        });
    }
}

// Initialize application
const canvas = document.getElementById('networkCanvas');
const viz = new GossipProtocolVisualization(canvas);
const ui = new UIController(viz);

// Start animation loop
viz.animate();

// Initialize with default network
viz.initialize(8);
