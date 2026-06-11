document.addEventListener('DOMContentLoaded', () => {
    const macSelect = document.getElementById('mac-select');
    const newMacInput = document.getElementById('new-mac');
    const btnAddMac = document.getElementById('btn-add-mac');
    const btnDestello = document.getElementById('btn-destello');
    const btnSetpoint = document.getElementById('btn-setpoint');
    const setpointInput = document.getElementById('setpoint-value');
    
    // Local storage key
    const STORAGE_KEY = 'iot_saved_macs';

    // Load saved MACs
    function loadSavedMacs() {
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        
        // Clear except first option
        while(macSelect.options.length > 1) {
            macSelect.remove(1);
        }

        saved.forEach(mac => {
            const option = document.createElement('option');
            option.value = mac;
            option.textContent = mac;
            macSelect.appendChild(option);
        });

        updateButtonStates();
    }

    // Save a new MAC
    function saveMac(mac) {
        // Basic cleanup: remove colons, uppercase
        const cleanMac = mac.replace(/:/g, '').toUpperCase().trim();
        
        if (!cleanMac || cleanMac.length < 12) {
            showToast('Formato de MAC inválido', 'error');
            return;
        }

        let saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        if (!saved.includes(cleanMac)) {
            saved.push(cleanMac);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
            loadSavedMacs();
            macSelect.value = cleanMac;
            showToast('Nodo añadido correctamente', 'success');
            newMacInput.value = '';
            updateButtonStates();
        } else {
            showToast('El nodo ya existe en la lista', 'error');
            macSelect.value = cleanMac;
            updateButtonStates();
        }
    }

    // Enable/Disable buttons based on selection
    function updateButtonStates() {
        const hasSelection = macSelect.value !== '';
        btnDestello.disabled = !hasSelection;
        btnSetpoint.disabled = !hasSelection;
    }

    // Toast Notifications
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Trigger reflow
        void toast.offsetWidth;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400); // Wait for transition
        }, 3000);
    }

    // API Call
    async function sendCommand(command, value = null) {
        const mac_id = macSelect.value;
        if (!mac_id) return;

        const originalText = command === 'destello' ? btnDestello.innerHTML : btnSetpoint.innerHTML;
        const btn = command === 'destello' ? btnDestello : btnSetpoint;
        
        try {
            btn.innerHTML = '<span class="icon">⏳</span> Enviando...';
            btn.disabled = true;

            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mac_id, command, value })
            });

            const data = await response.json();

            if (response.ok) {
                showToast(data.message, 'success');
            } else {
                showToast(data.message, 'error');
            }
        } catch (error) {
            showToast('Error de conexión con el servidor', 'error');
            console.error(error);
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }

    // Event Listeners
    btnAddMac.addEventListener('click', () => {
        saveMac(newMacInput.value);
    });

    newMacInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveMac(newMacInput.value);
        }
    });

    macSelect.addEventListener('change', updateButtonStates);

    btnDestello.addEventListener('click', () => {
        sendCommand('destello');
    });

    btnSetpoint.addEventListener('click', () => {
        const value = parseFloat(setpointInput.value);
        if (isNaN(value)) {
            showToast('Ingresa un valor válido para el setpoint', 'error');
            setpointInput.focus();
            return;
        }
        sendCommand('setpoint', value);
    });

    // Init
    loadSavedMacs();
});
