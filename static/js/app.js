document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registrationForm');
    const steps = Array.from(document.querySelectorAll('.form-step'));
    const stepIndicators = Array.from(document.querySelectorAll('.progress-step'));
    const progressLine = document.getElementById('progressLine');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const hasLpgSelect = document.getElementById('has_lpg');
    const lpgFields = document.querySelectorAll('.lpg-field');

    let currentStep = 1;

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

    // Handle File Previews
    const fileInputs = [
        { inputId: 'aadhaar_file', previewId: 'aadhaarPreview' },
        { inputId: 'pan_file', previewId: 'panPreview' },
        { inputId: 'address_file', previewId: 'addressPreview' },
        { inputId: 'lpg_file', previewId: 'lpgPreview' },
        { inputId: 'cheque_file', previewId: 'chequePreview' }
    ];

    fileInputs.forEach(({ inputId, previewId }) => {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        if (input && preview) {
            input.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    preview.textContent = e.target.files[0].name;
                } else {
                    preview.textContent = 'No file chosen';
                }
            });
        }
    });

    // Toggle LPG Details fields
    function toggleLpgFields() {
        const hasLpg = hasLpgSelect.value === 'Yes';
        lpgFields.forEach(field => {
            if (hasLpg) {
                field.style.display = 'block';
                const input = field.querySelector('input, select');
                // Make LPG Customer No and OMC required if they have LPG
                if (input && (input.id === 'customer_no' || input.id === 'omc_name')) {
                    input.required = true;
                }
            } else {
                field.style.display = 'none';
                const input = field.querySelector('input, select');
                if (input) {
                    input.required = false;
                    input.value = '';
                }
                const preview = field.querySelector('.file-name-preview');
                if (preview) preview.textContent = 'No file chosen';
            }
        });
    }

    hasLpgSelect.addEventListener('change', toggleLpgFields);
    toggleLpgFields(); // Initial call

    // Multi-step Form Logic
    function updateFormProgress() {
        // Update Steps Visibility
        steps.forEach((step, idx) => {
            step.classList.toggle('active', idx === currentStep - 1);
        });

        // Update Progress Indicators
        stepIndicators.forEach((indicator, idx) => {
            const stepNum = idx + 1;
            indicator.classList.toggle('active', stepNum === currentStep);
            indicator.classList.toggle('completed', stepNum < currentStep);
        });

        // Update Progress Line Width
        const progressPct = ((currentStep - 1) / (stepIndicators.length - 1)) * 100;
        progressLine.style.width = `${progressPct}%`;

        // Update Navigation Buttons
        if (currentStep === 1) {
            prevBtn.style.visibility = 'hidden';
        } else {
            prevBtn.style.visibility = 'visible';
        }

        if (currentStep === steps.length) {
            nextBtn.innerHTML = `Submit Registration <i class="fa-solid fa-circle-check"></i>`;
            nextBtn.classList.remove('btn-primary');
            nextBtn.classList.add('btn-primary');
            nextBtn.style.background = 'linear-gradient(135deg, var(--success-green) 0%, #059669 100%)';
            nextBtn.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
        } else {
            nextBtn.innerHTML = `Next <i class="fa-solid fa-chevron-right"></i>`;
            nextBtn.style.background = '';
            nextBtn.style.boxShadow = '';
            nextBtn.classList.add('btn-primary');
        }
    }

    // Validate Current Form Step Inputs
    function validateStep(stepNum) {
        const stepContainer = steps[stepNum - 1];
        const requiredInputs = stepContainer.querySelectorAll('[required]');
        let isValid = true;

        requiredInputs.forEach(input => {
            // Check HTML5 validity
            if (!input.checkValidity()) {
                isValid = false;
                input.reportValidity();
            }
            
            // Custom validations
            if (input.id === 'aadhaar_num') {
                const cleanVal = input.value.replace(/[\s-]/g, '');
                if (cleanVal.length !== 12 || isNaN(cleanVal)) {
                    isValid = false;
                    showToast('Aadhaar number must be exactly 12 digits.', true);
                    input.focus();
                }
            }
            if (input.id === 'mobile_phone') {
                const cleanVal = input.value.replace(/[\s-]/g, '');
                if (cleanVal.length !== 10 || isNaN(cleanVal)) {
                    isValid = false;
                    showToast('Mobile number must be exactly 10 digits.', true);
                    input.focus();
                }
            }
        });

        return isValid;
    }

    nextBtn.addEventListener('click', async () => {
        if (!validateStep(currentStep)) return;

        if (currentStep < steps.length) {
            currentStep++;
            updateFormProgress();
        } else {
            // Submit Form
            await submitForm();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            updateFormProgress();
        }
    });

    // Make steps clickable if they have been completed
    stepIndicators.forEach((indicator, idx) => {
        indicator.addEventListener('click', () => {
            const stepNum = idx + 1;
            // Only allow jumping back, or jumping forward if the current step is valid
            if (stepNum < currentStep) {
                currentStep = stepNum;
                updateFormProgress();
            } else if (stepNum > currentStep) {
                // To go forward, we must validate steps in between
                let canGoForward = true;
                for (let s = currentStep; s < stepNum; s++) {
                    if (!validateStep(s)) {
                        canGoForward = false;
                        break;
                    }
                }
                if (canGoForward) {
                    currentStep = stepNum;
                    updateFormProgress();
                }
            }
        });
    });

    // Form Submission AJAX
    async function submitForm() {
        nextBtn.disabled = true;
        nextBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Submitting...`;

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                showToast(result.message || 'Registration saved successfully!', false);
                form.reset();
                // Reset previews
                fileInputs.forEach(({ previewId }) => {
                    document.getElementById(previewId).textContent = 'No file chosen';
                });
                
                // Go back to first step
                currentStep = 1;
                updateFormProgress();
                toggleLpgFields();
            } else {
                showToast(result.message || 'Error occurred during registration.', true);
            }
        } catch (err) {
            console.error(err);
            showToast('Network error, please try again.', true);
        } finally {
            nextBtn.disabled = false;
            updateFormProgress();
        }
    }
});
