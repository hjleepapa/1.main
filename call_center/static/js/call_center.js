/**
 * Call Center Agent Dashboard - SIP Phone Integration
 * Supports ACD features and SIP-based call handling
 */

class CallCenterAgent {
    constructor() {
        this.agent = null;
        this.sipUser = null;
        this.currentCall = null;
        this.currentSession = null;
        this.statusTimer = null;
        this.statusStartTime = null;
        this.callDurationTimer = null;
        this.callStartTime = null;
        
        this.init();
    }
    
    init() {
        // Initialize UI elements
        this.initElements();
        this.attachEventListeners();
        this.checkLoginStatus();
    }
    
    initElements() {
        // Screens
        this.loginScreen = document.getElementById('loginScreen');
        this.dashboardScreen = document.getElementById('dashboardScreen');
        
        // Login form
        this.loginForm = document.getElementById('loginForm');
        
        // Agent info displays
        this.agentNameDisplay = document.getElementById('agentNameDisplay');
        this.agentExtension = document.getElementById('agentExtension');
        this.currentStatus = document.getElementById('currentStatus');
        this.statusTimerDisplay = document.getElementById('statusTimer');
        this.sipStatus = document.getElementById('sipStatus');
        
        // Buttons
        this.logoutBtn = document.getElementById('logoutBtn');
        this.readyBtn = document.getElementById('readyBtn');
        this.notReadyBtn = document.getElementById('notReadyBtn');
        this.answerBtn = document.getElementById('answerBtn');
        this.holdBtn = document.getElementById('holdBtn');
        this.unholdBtn = document.getElementById('unholdBtn');
        this.hangupBtn = document.getElementById('hangupBtn');
        this.transferBtn = document.getElementById('transferBtn');
        this.dialCallBtn = document.getElementById('dialCallBtn');
        this.dialClearBtn = document.getElementById('dialClearBtn');
        
        // Call info
        this.callInfo = document.getElementById('callInfo');
        
        // Dialpad
        this.dialInput = document.getElementById('dialInput');
        this.dialButtons = document.querySelectorAll('.dial-btn');
        
        // Transfer panel
        this.transferPanel = document.getElementById('transferPanel');
        this.transferNumber = document.getElementById('transferNumber');
        this.blindTransferBtn = document.getElementById('blindTransferBtn');
        this.attendedTransferBtn = document.getElementById('attendedTransferBtn');
        this.cancelTransferBtn = document.getElementById('cancelTransferBtn');
        
        // Customer popup
        this.customerPopup = document.getElementById('customerPopup');
        this.customerData = document.getElementById('customerData');
        this.closeCustomerPopup = document.getElementById('closeCustomerPopup');
        this.acceptCallFromPopup = document.getElementById('acceptCallFromPopup');
        
        // Audio
        this.ringTone = document.getElementById('ringTone');
        this.remoteAudio = document.getElementById('remoteAudio');
    }
    
    attachEventListeners() {
        // Login
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        
        // Logout
        this.logoutBtn.addEventListener('click', () => this.handleLogout());
        
        // Agent status
        this.readyBtn.addEventListener('click', () => this.setReady());
        this.notReadyBtn.addEventListener('click', () => this.setNotReady());
        
        // Call controls
        this.answerBtn.addEventListener('click', () => this.answerCall());
        this.holdBtn.addEventListener('click', () => this.holdCall());
        this.unholdBtn.addEventListener('click', () => this.unholdCall());
        this.hangupBtn.addEventListener('click', () => this.hangupCall());
        this.transferBtn.addEventListener('click', () => this.showTransferPanel());
        
        // Transfer
        this.blindTransferBtn.addEventListener('click', () => this.transferCall('blind'));
        this.attendedTransferBtn.addEventListener('click', () => this.transferCall('attended'));
        this.cancelTransferBtn.addEventListener('click', () => this.hideTransferPanel());
        
        // Dialpad
        this.dialButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const digit = btn.getAttribute('data-digit');
                this.dialInput.value += digit;
                this.updateDialCallButton();
            });
        });
        
        this.dialClearBtn.addEventListener('click', () => {
            this.dialInput.value = '';
            this.updateDialCallButton();
        });
        
        this.dialCallBtn.addEventListener('click', () => this.makeCall());
        
        // Customer popup
        this.closeCustomerPopup.addEventListener('click', () => this.hideCustomerPopup());
        this.acceptCallFromPopup.addEventListener('click', () => {
            this.hideCustomerPopup();
            this.answerCall();
        });
    }
    
    async handleLogin(e) {
        e.preventDefault();
        
        const formData = new FormData(this.loginForm);
        const data = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch('/call-center/api/agent/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.agent = result.agent;
                this.initSIPClient(data.sip_username, data.sip_password, data.sip_domain);
                this.showDashboard();
            } else {
                alert('Login failed: ' + result.error);
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Login failed. Please try again.');
        }
    }
    
    async handleLogout() {
        if (!confirm('Are you sure you want to logout?')) {
            return;
        }
        
        try {
            // Disconnect SIP
            if (this.sipUser) {
                await this.sipUser.stop();
            }
            
            // Logout from backend
            await fetch('/call-center/api/agent/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            this.agent = null;
            this.showLogin();
            this.stopStatusTimer();
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    async setReady() {
        try {
            const response = await fetch('/call-center/api/agent/ready', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateAgentStatus('ready');
            }
        } catch (error) {
            console.error('Set ready error:', error);
        }
    }
    
    async setNotReady() {
        const reason = prompt('Reason for not ready:', 'Break');
        if (!reason) return;
        
        try {
            const response = await fetch('/call-center/api/agent/not-ready', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateAgentStatus('not-ready');
            }
        } catch (error) {
            console.error('Set not ready error:', error);
        }
    }
    
    initSIPClient(username, password, domain) {
        // Initialize JsSIP User Agent
        console.log(`Initializing SIP client for ${username}@${domain}`);
        
        const socket = new JsSIP.WebSocketInterface(`wss://${domain}:7443`);
        
        const configuration = {
            sockets: [socket],
            uri: `sip:${username}@${domain}`,
            password: password,
            display_name: username,
            register: true
        };
        
        this.sipUser = new JsSIP.UA(configuration);
        
        // Event handlers
        this.sipUser.on('connected', (e) => {
            console.log('✓ SIP connected');
            this.updateSIPStatus(true);
        });
        
        this.sipUser.on('disconnected', (e) => {
            console.log('✗ SIP disconnected');
            this.updateSIPStatus(false);
        });
        
        this.sipUser.on('registered', (e) => {
            console.log('✓ SIP registered');
            this.updateSIPStatus(true);
        });
        
        this.sipUser.on('unregistered', (e) => {
            console.log('SIP unregistered');
        });
        
        this.sipUser.on('registrationFailed', (e) => {
            console.error('✗ SIP registration failed:', e);
            this.updateSIPStatus(false);
            alert('Failed to register with SIP server. Please check your credentials.');
        });
        
        this.sipUser.on('newRTCSession', (e) => {
            console.log('New RTC session');
            this.handleIncomingCall(e.session);
        });
        
        // Start the User Agent
        try {
            this.sipUser.start();
            console.log('SIP User Agent started');
        } catch (error) {
            console.error('Failed to start SIP User Agent:', error);
            this.updateSIPStatus(false);
            alert('Failed to connect to SIP server: ' + error.message);
        }
    }
    
    handleIncomingCall(session) {
        console.log('Incoming call:', session);
        
        this.currentSession = session;
        
        // Extract caller information (JsSIP API)
        const remoteIdentity = session.remote_identity;
        const callerNumber = remoteIdentity.uri.user;
        const callerName = remoteIdentity.display_name || callerNumber;
        
        // Generate call ID
        const callId = session.id;
        
        // Mock customer data (in production, fetch from CRM)
        const customerId = callerNumber;
        
        this.currentCall = {
            call_id: callId,
            caller_number: callerNumber,
            caller_name: callerName,
            customer_id: customerId,
            direction: 'inbound'
        };
        
        // Notify backend
        fetch('/call-center/api/call/ringing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.currentCall)
        });
        
        // Update UI
        this.showIncomingCall(callerName, callerNumber);
        
        // Show customer popup
        this.showCustomerPopup(customerId);
        
        // Play ringtone
        this.ringTone.play();
        
        // Setup session state listeners
        invitation.stateChange.addListener((state) => {
            console.log('Call state changed:', state);
            
            switch (state) {
                case SIP.SessionState.Establishing:
                    console.log('Call establishing...');
                    break;
                case SIP.SessionState.Established:
                    this.ringTone.pause();
                    this.ringTone.currentTime = 0;
                    this.onCallEstablished();
                    break;
                case SIP.SessionState.Terminated:
                    this.onCallEnded();
                    break;
            }
        });
        
        // Setup remote media
        const remoteStream = new MediaStream();
        invitation.sessionDescriptionHandler.peerConnection.getReceivers().forEach((receiver) => {
            if (receiver.track) {
                remoteStream.addTrack(receiver.track);
            }
        });
        this.remoteAudio.srcObject = remoteStream;
        this.remoteAudio.play();
    }
    
    async answerCall() {
        if (!this.currentSession) return;
        
        try {
            const options = {
                sessionDescriptionHandlerOptions: {
                    constraints: {
                        audio: true,
                        video: false
                    }
                }
            };
            
            await this.currentSession.accept(options);
            
            // Notify backend
            await fetch('/call-center/api/call/answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ call_id: this.currentCall.call_id })
            });
            
            this.ringTone.pause();
            this.ringTone.currentTime = 0;
        } catch (error) {
            console.error('Answer call error:', error);
        }
    }
    
    async hangupCall() {
        if (!this.currentSession) return;
        
        try {
            await this.currentSession.bye();
            
            // Notify backend
            await fetch('/call-center/api/call/drop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ call_id: this.currentCall.call_id })
            });
        } catch (error) {
            console.error('Hangup call error:', error);
        }
    }
    
    async holdCall() {
        if (!this.currentSession) return;
        
        try {
            await this.currentSession.sessionDescriptionHandler.hold();
            
            // Notify backend
            await fetch('/call-center/api/call/hold', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ call_id: this.currentCall.call_id })
            });
            
            this.holdBtn.style.display = 'none';
            this.unholdBtn.style.display = 'block';
        } catch (error) {
            console.error('Hold call error:', error);
        }
    }
    
    async unholdCall() {
        if (!this.currentSession) return;
        
        try {
            await this.currentSession.sessionDescriptionHandler.unhold();
            
            // Notify backend
            await fetch('/call-center/api/call/unhold', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ call_id: this.currentCall.call_id })
            });
            
            this.holdBtn.style.display = 'block';
            this.unholdBtn.style.display = 'none';
        } catch (error) {
            console.error('Unhold call error:', error);
        }
    }
    
    async makeCall() {
        const number = this.dialInput.value;
        if (!number) return;
        
        try {
            const target = SIP.UserAgent.makeURI(`sip:${number}@${this.agent.sip_domain}`);
            const inviter = new SIP.Inviter(this.sipUser, target);
            
            this.currentSession = inviter;
            
            const options = {
                sessionDescriptionHandlerOptions: {
                    constraints: {
                        audio: true,
                        video: false
                    }
                }
            };
            
            await inviter.invite(options);
            
            // Setup session state listeners
            inviter.stateChange.addListener((state) => {
                console.log('Call state:', state);
                
                switch (state) {
                    case SIP.SessionState.Establishing:
                        this.showOutgoingCall(number);
                        break;
                    case SIP.SessionState.Established:
                        this.onCallEstablished();
                        break;
                    case SIP.SessionState.Terminated:
                        this.onCallEnded();
                        break;
                }
            });
            
            this.dialInput.value = '';
            this.updateDialCallButton();
        } catch (error) {
            console.error('Make call error:', error);
            alert('Failed to make call');
        }
    }
    
    showTransferPanel() {
        this.transferPanel.style.display = 'block';
    }
    
    hideTransferPanel() {
        this.transferPanel.style.display = 'none';
        this.transferNumber.value = '';
    }
    
    async transferCall(type) {
        const transferTo = this.transferNumber.value;
        if (!transferTo) {
            alert('Please enter transfer destination');
            return;
        }
        
        try {
            // Notify backend
            await fetch('/call-center/api/call/transfer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    call_id: this.currentCall.call_id,
                    transfer_to: transferTo,
                    transfer_type: type
                })
            });
            
            // Perform SIP REFER for blind transfer
            if (type === 'blind' && this.currentSession) {
                const referTo = `sip:${transferTo}@${this.agent.sip_domain}`;
                await this.currentSession.refer(SIP.UserAgent.makeURI(referTo));
            }
            
            this.hideTransferPanel();
            alert(`Call ${type} transferred to ${transferTo}`);
        } catch (error) {
            console.error('Transfer call error:', error);
            alert('Transfer failed');
        }
    }
    
    async showCustomerPopup(customerId) {
        this.customerPopup.classList.add('active');
        this.customerData.innerHTML = '<div class="customer-info loading"><i class="fas fa-spinner fa-spin"></i> Loading customer data...</div>';
        
        try {
            const response = await fetch(`/call-center/api/customer/${customerId}`);
            const customer = await response.json();
            
            this.displayCustomerData(customer);
        } catch (error) {
            console.error('Fetch customer data error:', error);
            this.customerData.innerHTML = '<div class="customer-info"><p>Failed to load customer data</p></div>';
        }
    }
    
    displayCustomerData(customer) {
        const html = `
            <div class="customer-info">
                <div class="customer-field">
                    <label>Customer ID:</label>
                    <span>${customer.customer_id}</span>
                </div>
                <div class="customer-field">
                    <label>Name:</label>
                    <span>${customer.name}</span>
                </div>
                <div class="customer-field">
                    <label>Email:</label>
                    <span>${customer.email}</span>
                </div>
                <div class="customer-field">
                    <label>Phone:</label>
                    <span>${customer.phone}</span>
                </div>
                <div class="customer-field">
                    <label>Account Status:</label>
                    <span>${customer.account_status}</span>
                </div>
                <div class="customer-field">
                    <label>Tier:</label>
                    <span>${customer.tier}</span>
                </div>
                <div class="customer-field">
                    <label>Last Contact:</label>
                    <span>${customer.last_contact}</span>
                </div>
                <div class="customer-field">
                    <label>Open Tickets:</label>
                    <span>${customer.open_tickets}</span>
                </div>
                <div class="customer-field">
                    <label>Lifetime Value:</label>
                    <span>${customer.lifetime_value}</span>
                </div>
                <div class="customer-field">
                    <label>Notes:</label>
                    <span>${customer.notes}</span>
                </div>
            </div>
        `;
        
        this.customerData.innerHTML = html;
    }
    
    hideCustomerPopup() {
        this.customerPopup.classList.remove('active');
    }
    
    showIncomingCall(callerName, callerNumber) {
        this.callInfo.innerHTML = `
            <div class="active-call ringing">
                <div class="caller-info">
                    <div class="caller-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="caller-details">
                        <h4>${callerName}</h4>
                        <p>${callerNumber}</p>
                    </div>
                </div>
                <div class="call-status">
                    <i class="fas fa-phone-volume"></i> Incoming Call
                </div>
            </div>
        `;
        
        this.answerBtn.disabled = false;
        this.hangupBtn.disabled = false;
    }
    
    showOutgoingCall(number) {
        this.callInfo.innerHTML = `
            <div class="active-call">
                <div class="caller-info">
                    <div class="caller-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="caller-details">
                        <h4>Calling...</h4>
                        <p>${number}</p>
                    </div>
                </div>
            </div>
        `;
        
        this.hangupBtn.disabled = false;
    }
    
    onCallEstablished() {
        console.log('Call established');
        
        this.callStartTime = Date.now();
        this.startCallDurationTimer();
        
        this.answerBtn.disabled = true;
        this.holdBtn.disabled = false;
        this.transferBtn.disabled = false;
        this.hangupBtn.disabled = false;
        
        this.updateAgentStatus('on-call');
        
        // Update call info
        const callerName = this.currentCall.caller_name || this.currentCall.caller_number;
        this.callInfo.innerHTML = `
            <div class="active-call">
                <div class="caller-info">
                    <div class="caller-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="caller-details">
                        <h4>${callerName}</h4>
                        <p>${this.currentCall.caller_number}</p>
                    </div>
                </div>
                <div class="call-duration" id="callDuration">00:00:00</div>
            </div>
        `;
    }
    
    onCallEnded() {
        console.log('Call ended');
        
        this.stopCallDurationTimer();
        
        this.callInfo.innerHTML = `
            <div class="no-call">
                <i class="fas fa-phone-slash"></i>
                <p>No active call</p>
            </div>
        `;
        
        this.answerBtn.disabled = true;
        this.holdBtn.disabled = true;
        this.unholdBtn.disabled = true;
        this.transferBtn.disabled = true;
        this.hangupBtn.disabled = true;
        
        this.currentCall = null;
        this.currentSession = null;
        
        this.setReady();
    }
    
    startCallDurationTimer() {
        this.callDurationTimer = setInterval(() => {
            const duration = Math.floor((Date.now() - this.callStartTime) / 1000);
            const hours = Math.floor(duration / 3600).toString().padStart(2, '0');
            const minutes = Math.floor((duration % 3600) / 60).toString().padStart(2, '0');
            const seconds = (duration % 60).toString().padStart(2, '0');
            
            const durationEl = document.getElementById('callDuration');
            if (durationEl) {
                durationEl.textContent = `${hours}:${minutes}:${seconds}`;
            }
        }, 1000);
    }
    
    stopCallDurationTimer() {
        if (this.callDurationTimer) {
            clearInterval(this.callDurationTimer);
            this.callDurationTimer = null;
        }
    }
    
    updateAgentStatus(status) {
        const statusMap = {
            'logged-out': 'Logged Out',
            'logged-in': 'Logged In',
            'ready': 'Ready',
            'not-ready': 'Not Ready',
            'on-call': 'On Call'
        };
        
        this.currentStatus.textContent = statusMap[status] || status;
        this.currentStatus.className = 'status-badge ' + status;
        
        // Enable/disable buttons based on status
        if (status === 'ready') {
            this.readyBtn.disabled = true;
            this.notReadyBtn.disabled = false;
            this.dialCallBtn.disabled = false;
        } else if (status === 'not-ready') {
            this.readyBtn.disabled = false;
            this.notReadyBtn.disabled = true;
            this.dialCallBtn.disabled = true;
        } else {
            this.readyBtn.disabled = false;
            this.notReadyBtn.disabled = false;
        }
        
        // Restart status timer
        this.statusStartTime = Date.now();
        this.startStatusTimer();
    }
    
    startStatusTimer() {
        this.stopStatusTimer();
        
        this.statusTimer = setInterval(() => {
            const duration = Math.floor((Date.now() - this.statusStartTime) / 1000);
            const hours = Math.floor(duration / 3600).toString().padStart(2, '0');
            const minutes = Math.floor((duration % 3600) / 60).toString().padStart(2, '0');
            const seconds = (duration % 60).toString().padStart(2, '0');
            
            this.statusTimerDisplay.textContent = `${hours}:${minutes}:${seconds}`;
        }, 1000);
    }
    
    stopStatusTimer() {
        if (this.statusTimer) {
            clearInterval(this.statusTimer);
            this.statusTimer = null;
        }
    }
    
    updateSIPStatus(connected) {
        if (connected) {
            this.sipStatus.innerHTML = '<i class="fas fa-circle"></i><span>Connected</span>';
            this.sipStatus.classList.add('connected');
        } else {
            this.sipStatus.innerHTML = '<i class="fas fa-circle"></i><span>Disconnected</span>';
            this.sipStatus.classList.remove('connected');
        }
    }
    
    updateDialCallButton() {
        this.dialCallBtn.disabled = !this.dialInput.value || this.currentCall !== null;
    }
    
    showDashboard() {
        this.loginScreen.classList.remove('active');
        this.dashboardScreen.classList.add('active');
        
        this.agentNameDisplay.textContent = this.agent.name;
        this.agentExtension.textContent = `Ext: ${this.agent.sip_extension}`;
        
        this.updateAgentStatus('logged-in');
        
        this.readyBtn.disabled = false;
        this.notReadyBtn.disabled = false;
    }
    
    showLogin() {
        this.dashboardScreen.classList.remove('active');
        this.loginScreen.classList.add('active');
        this.loginForm.reset();
    }
    
    async checkLoginStatus() {
        try {
            const response = await fetch('/call-center/api/agent/status');
            const result = await response.json();
            
            if (result.logged_in) {
                this.agent = result.agent;
                this.showDashboard();
                this.initSIPClient(
                    this.agent.sip_username,
                    '', // Password not returned
                    this.agent.sip_domain
                );
            }
        } catch (error) {
            console.error('Check login status error:', error);
        }
    }
}

// Initialize the call center agent dashboard
document.addEventListener('DOMContentLoaded', () => {
    new CallCenterAgent();
});

