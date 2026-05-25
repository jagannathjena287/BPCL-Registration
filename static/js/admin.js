document.addEventListener('DOMContentLoaded', () => {
    // Auth Check
    async function checkAuth() {
        try {
            const response = await fetch('/api/auth-check');
            if (!response.ok) {
                window.location.href = '/login';
            }
        } catch (err) {
            window.location.href = '/login';
        }
    }
    checkAuth();

    // DOM Elements
    const statTotal = document.getElementById('statTotal');
    const statMetered = document.getElementById('statMetered');
    const statUnmetered = document.getElementById('statUnmetered');
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const exportBtn = document.getElementById('exportBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const consumerTableBody = document.getElementById('consumerTableBody');
    const detailModal = document.getElementById('detailModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const updateMeterForm = document.getElementById('updateMeterForm');
    const updateConsumerId = document.getElementById('updateConsumerId');
    const updateMeterNo = document.getElementById('updateMeterNo');

    // Modal Details Elements
    const detailAppNo = document.getElementById('detailAppNo');
    const detName = document.getElementById('detName');
    const detNameSplit = document.getElementById('detNameSplit');
    const detFather = document.getElementById('detFather');
    const detDobGender = document.getElementById('detDobGender');
    const detContact = document.getElementById('detContact');
    const detProfession = document.getElementById('detProfession');
    const detAddress = document.getElementById('detAddress');
    const detLocality = document.getElementById('detLocality');
    const detProperty = document.getElementById('detProperty');
    const detAadhaar = document.getElementById('detAadhaar');
    const detPan = document.getElementById('detPan');
    const detLpg = document.getElementById('detLpg');
    const detLpgDistributor = document.getElementById('detLpgDistributor');
    const detCheque = document.getElementById('detCheque');
    const detChequeBank = document.getElementById('detChequeBank');
    const docLinkList = document.getElementById('docLinkList');

    let currentConsumers = [];

    // Show toast message
    function showToast(message, isError = false) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${isError ? 'toast-error' : 'toast-success'}`;
        toast.innerHTML = `<i class="fa-solid ${isError ? 'fa-circle-xmark' : 'fa-circle-check'}"></i> <span>${message}</span>`;
        container.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 50);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Load Stats
    async function loadStats() {
        try {
            const response = await fetch('/api/dashboard');
            if (response.ok) {
                const stats = await response.json();
                statTotal.textContent = stats.total;
                statMetered.textContent = stats.metered;
                statUnmetered.textContent = stats.unmetered;
            }
        } catch (err) {
            console.error('Error loading stats:', err);
        }
    }

    // Load Consumers List
    async function loadConsumers() {
        const search = searchInput.value;
        const status = statusFilter.value;
        
        consumerTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Loading...</td></tr>`;

        try {
            const url = `/api/consumers?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`;
            const response = await fetch(url);
            if (response.ok) {
                const consumers = await response.json();
                currentConsumers = consumers;
                renderConsumersTable(consumers);
            } else {
                consumerTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--error-red);">Failed to fetch consumer data.</td></tr>`;
            }
        } catch (err) {
            console.error('Error loading consumers:', err);
            consumerTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--error-red);">Network error.</td></tr>`;
        }
    }

    // Render Table
    function renderConsumersTable(consumers) {
        if (consumers.length === 0) {
            consumerTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No matching registrations found.</td></tr>`;
            return;
        }

        consumerTableBody.innerHTML = '';
        consumers.forEach(c => {
            const tr = document.createElement('tr');
            
            const hasMeter = c.meter_no && c.meter_no.trim() !== '';
            const statusBadge = hasMeter 
                ? `<span class="badge badge-success">Meter Installed</span>` 
                : `<span class="badge badge-warning">Pending Installation</span>`;
                
            tr.innerHTML = `
                <td style="font-weight: 600; color: var(--bpcl-blue);">${c.application_form_no}</td>
                <td>${c.name}</td>
                <td>${c.mobile_phone}</td>
                <td>${c.locality || '-'}</td>
                <td style="font-family: monospace;">${c.meter_no || '<span style="color: var(--text-muted);">None</span>'}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-secondary btn-sm view-btn" data-id="${c.id}" style="padding: 6px 12px; font-size: 0.8rem;">
                        <i class="fa-solid fa-eye"></i> View
                    </button>
                </td>
            `;
            consumerTableBody.appendChild(tr);
        });

        // Add Event Listeners to View Buttons
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.currentTarget.getAttribute('data-id');
                openDetailsModal(id);
            });
        });
    }

    // Open Detail Modal
    async function openDetailsModal(id) {
        try {
            const response = await fetch(`/api/consumers/${id}`);
            if (response.ok) {
                const c = await response.json();
                
                // Set application header
                detailAppNo.textContent = `Form Ref: ${c.application_form_no}`;
                
                // Populate fields
                detName.textContent = c.name;
                detNameSplit.textContent = `${c.contact_title} ${c.first_name} ${c.middle_name || ''} ${c.last_name || ''}`.trim();
                detFather.textContent = c.father_name || '-';
                detDobGender.textContent = `${c.date_of_birth || '-'} / ${c.gender || '-'}`;
                detContact.textContent = `${c.mobile_phone || '-'} / ${c.email || '-'}`;
                detProfession.textContent = `${c.profession || '-'} / ${c.designation || '-'}`;
                
                detAddress.textContent = c.address || '-';
                detLocality.textContent = `${c.locality || '-'} / ${c.postal_code || '-'}`;
                detProperty.textContent = `${c.type_of_property || '-'} / ${c.type_of_ownership || '-'}`;
                
                const aadhaarStr = [c.aadhaar1, c.aadhaar2, c.aadhaar3].filter(Boolean).join('-');
                detAadhaar.textContent = `${aadhaarStr || '-'} (Name: ${c.aadhar_name || '-'})`;
                detPan.textContent = c.pan || '-';

                detLpg.textContent = c.customer_no ? `${c.omc_name || '-'} - Cust No: ${c.customer_no}` : 'No LPG details';
                detLpgDistributor.textContent = c.distributor_name || '-';

                detCheque.textContent = c.cheque_no ? `Cheque/DD No: ${c.cheque_no} (Rs. ${c.cheque_amount || '0'})` : 'No cheque details';
                detChequeBank.textContent = `${c.bank_name || '-'} (Dt: ${c.cheque_date || '-'})`;

                // Update form values
                updateConsumerId.value = c.id;
                updateMeterNo.value = c.meter_no || '';

                // Documents List
                docLinkList.innerHTML = '';
                const docs = [
                    { name: 'Aadhaar Card', file: c.aadhaar_file, icon: 'fa-address-card' },
                    { name: 'PAN Card', file: c.pan_file, icon: 'fa-id-card' },
                    { name: 'Address Proof', file: c.address_file, icon: 'fa-house-chimney' },
                    { name: 'LPG Copy', file: c.lpg_file, icon: 'fa-book-open' },
                    { name: 'Cheque Photo', file: c.cheque_file, icon: 'fa-money-check-dollar' }
                ];

                let hasDocs = false;
                docs.forEach(doc => {
                    if (doc.file) {
                        hasDocs = true;
                        const link = document.createElement('a');
                        link.href = `/uploads/${doc.file}`;
                        link.target = '_blank';
                        link.className = 'btn btn-secondary';
                        link.style.fontSize = '0.8rem';
                        link.style.padding = '8px 12px';
                        link.innerHTML = `<i class="fa-solid ${doc.icon}"></i> View ${doc.name}`;
                        docLinkList.appendChild(link);
                    }
                });

                if (!hasDocs) {
                    docLinkList.innerHTML = '<span style="color: var(--text-muted); font-size: 0.85rem;">No documents uploaded.</span>';
                }

                // Show modal
                detailModal.classList.add('active');
            } else {
                showToast('Failed to load consumer details.', true);
            }
        } catch (err) {
            console.error(err);
            showToast('Error loading details.', true);
        }
    }

    // Close Modal
    function closeModal() {
        detailModal.classList.remove('active');
    }
    closeModalBtn.addEventListener('click', closeModal);
    detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) closeModal();
    });

    // Update Meter Submission
    updateMeterForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const id = updateConsumerId.value;
        const meter_no = updateMeterNo.value;

        try {
            const response = await fetch(`/api/consumers/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ meter_no })
            });

            const result = await response.json();
            if (response.ok && result.success) {
                showToast('Meter details updated successfully!', false);
                closeModal();
                loadStats();
                loadConsumers();
            } else {
                showToast(result.error || 'Failed to update details.', true);
            }
        } catch (err) {
            console.error(err);
            showToast('Network error, could not save details.', true);
        }
    });

    // Search and Filter Events
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(loadConsumers, 300);
    });

    statusFilter.addEventListener('change', loadConsumers);

    // Excel Export Trigger
    exportBtn.addEventListener('click', () => {
        if (currentConsumers.length === 0) {
            showToast('No records available to export.', true);
            return;
        }
        
        const ids = currentConsumers.map(c => c.id).join(',');
        window.location.href = `/api/export?ids=${ids}`;
        showToast('Initiating download...', false);
    });

    // Logout Action
    logoutBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/logout');
            if (response.ok) {
                window.location.href = '/login';
            }
        } catch (err) {
            console.error('Logout error:', err);
            window.location.href = '/login';
        }
    });

    // Initial Load
    loadStats();
    loadConsumers();
});
