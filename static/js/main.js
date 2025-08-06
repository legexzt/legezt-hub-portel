// Main JavaScript file for Legezt Portal

// Dark mode functionality
function initDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    
    // Check for saved dark mode preference
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        html.classList.add('dark');
    }
    
    // Toggle dark mode
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            html.classList.toggle('dark');
            localStorage.setItem('darkMode', html.classList.contains('dark'));
        });
    }
}

// Sidebar functionality
function initSidebar() {
    const openSidebarBtn = document.getElementById('openSidebar');
    const closeSidebarBtn = document.getElementById('closeSidebar');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (openSidebarBtn && sidebar) {
        openSidebarBtn.addEventListener('click', () => {
            sidebar.classList.remove('collapsed');
            if (overlay) overlay.classList.remove('hidden');
        });
    }
    
    if (closeSidebarBtn && sidebar) {
        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.add('collapsed');
            if (overlay) overlay.classList.add('hidden');
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.add('collapsed');
            overlay.classList.add('hidden');
        });
    }
}

// View toggle functionality
function initViewToggle() {
    const gridViewBtn = document.getElementById('gridView');
    const listViewBtn = document.getElementById('listView');
    const filesContainer = document.getElementById('filesContainer');
    
    if (gridViewBtn && listViewBtn && filesContainer) {
        gridViewBtn.addEventListener('click', () => {
            filesContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6';
            localStorage.setItem('viewMode', 'grid');
            updateViewButtons('grid');
        });
        
        listViewBtn.addEventListener('click', () => {
            filesContainer.className = 'space-y-4';
            localStorage.setItem('viewMode', 'list');
            updateViewButtons('list');
        });
        
        // Load saved view mode
        const savedViewMode = localStorage.getItem('viewMode') || 'grid';
        if (savedViewMode === 'list') {
            listViewBtn.click();
        }
    }
}

function updateViewButtons(activeView) {
    const gridViewBtn = document.getElementById('gridView');
    const listViewBtn = document.getElementById('listView');
    
    if (activeView === 'grid') {
        gridViewBtn.classList.add('bg-blue-600', 'text-white');
        gridViewBtn.classList.remove('bg-gray-200', 'text-gray-700');
        listViewBtn.classList.add('bg-gray-200', 'text-gray-700');
        listViewBtn.classList.remove('bg-blue-600', 'text-white');
    } else {
        listViewBtn.classList.add('bg-blue-600', 'text-white');
        listViewBtn.classList.remove('bg-gray-200', 'text-gray-700');
        gridViewBtn.classList.add('bg-gray-200', 'text-gray-700');
        gridViewBtn.classList.remove('bg-blue-600', 'text-white');
    }
}

// Search and filter functionality
function initSearchAndFilter() {
    const searchInput = document.getElementById('searchInput');
    const branchFilter = document.getElementById('branchFilter');
    const subjectFilter = document.getElementById('subjectFilter');
    const yearFilter = document.getElementById('yearFilter');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterFiles, 300));
    }
    
    if (branchFilter) {
        branchFilter.addEventListener('change', filterFiles);
    }
    
    if (subjectFilter) {
        subjectFilter.addEventListener('change', filterFiles);
    }
    
    if (yearFilter) {
        yearFilter.addEventListener('change', filterFiles);
    }
}

function filterFiles() {
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const branchFilter = document.getElementById('branchFilter')?.value || '';
    const subjectFilter = document.getElementById('subjectFilter')?.value || '';
    const yearFilter = document.getElementById('yearFilter')?.value || '';
    
    const fileCards = document.querySelectorAll('.file-card');
    
    fileCards.forEach(card => {
        const title = card.querySelector('.file-title')?.textContent.toLowerCase() || '';
        const description = card.querySelector('.file-description')?.textContent.toLowerCase() || '';
        const branch = card.dataset.branch || '';
        const subject = card.dataset.subject || '';
        const year = card.dataset.year || '';
        
        const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
        const matchesBranch = !branchFilter || branch === branchFilter;
        const matchesSubject = !subjectFilter || subject === subjectFilter;
        const matchesYear = !yearFilter || year === yearFilter;
        
        if (matchesSearch && matchesBranch && matchesSubject && matchesYear) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
    
    // Password strength indicator
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const strengthIndicator = document.getElementById('passwordStrength');
    
    if (passwordInput && strengthIndicator) {
        passwordInput.addEventListener('input', checkPasswordStrength);
    }
    
    if (passwordInput && confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    }
}

function checkPasswordStrength() {
    const password = document.getElementById('password').value;
    const strengthIndicator = document.getElementById('passwordStrength');
    
    if (!strengthIndicator) return;
    
    let strength = 0;
    let feedback = '';
    
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    switch (strength) {
        case 0:
        case 1:
            feedback = '<span class="text-red-500">Very Weak</span>';
            break;
        case 2:
            feedback = '<span class="text-orange-500">Weak</span>';
            break;
        case 3:
            feedback = '<span class="text-yellow-500">Fair</span>';
            break;
        case 4:
            feedback = '<span class="text-blue-500">Good</span>';
            break;
        case 5:
            feedback = '<span class="text-green-500">Strong</span>';
            break;
    }
    
    strengthIndicator.innerHTML = feedback;
}

function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const matchIndicator = document.getElementById('passwordMatch');
    
    if (!matchIndicator) return;
    
    if (confirmPassword === '') {
        matchIndicator.innerHTML = '';
    } else if (password === confirmPassword) {
        matchIndicator.innerHTML = '<span class="text-green-500">Passwords match</span>';
    } else {
        matchIndicator.innerHTML = '<span class="text-red-500">Passwords do not match</span>';
    }
}

function validateForm(event) {
    const form = event.target;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.classList.add('border-red-500');
        } else {
            input.classList.remove('border-red-500');
        }
    });
    
    if (!isValid) {
        event.preventDefault();
        showAlert('Please fill in all required fields.', 'error');
    }
}

// Alert system
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-custom alert-${type}-custom fade-in`;
    alertDiv.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

// File upload functionality
function initFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect();
            }
        });
        
        fileInput.addEventListener('change', handleFileSelect);
    }
}

function handleFileSelect() {
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');
    
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileNameDisplay.textContent = file.name;
        fileNameDisplay.classList.remove('hidden');
    }
}

// Access code input functionality
function initAccessCodeInput() {
    const accessCodeInput = document.getElementById('accessCode');
    
    if (accessCodeInput) {
        accessCodeInput.addEventListener('input', (e) => {
            // Only allow numbers
            e.target.value = e.target.value.replace(/[^0-9]/g, '');
            
            // Auto-submit when 6 digits are entered
            if (e.target.value.length === 6) {
                e.target.form.submit();
            }
        });
    }
}

// Settings toggle functionality
function initSettingsToggles() {
    const toggles = document.querySelectorAll('.toggle-switch input');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', (e) => {
            const settingName = e.target.name;
            const isEnabled = e.target.checked;
            
            // Save setting to localStorage
            localStorage.setItem(settingName, isEnabled);
            
            // Show feedback
            showAlert(`${settingName.replace(/([A-Z])/g, ' $1').toLowerCase()} ${isEnabled ? 'enabled' : 'disabled'}`, 'success');
        });
        
        // Load saved settings
        const savedValue = localStorage.getItem(toggle.name);
        if (savedValue !== null) {
            toggle.checked = savedValue === 'true';
        }
    });
}

// Counter animation
function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        updateCounter();
    });
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initDarkMode();
    initSidebar();
    initViewToggle();
    initSearchAndFilter();
    initFormValidation();
    initFileUpload();
    initAccessCodeInput();
    initSettingsToggles();
    
    // Animate counters on homepage
    if (document.querySelector('.counter')) {
        animateCounters();
    }
    
    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Export functions for use in templates
window.LegeztPortal = {
    showAlert,
    filterFiles,
    checkPasswordStrength,
    checkPasswordMatch
}; 