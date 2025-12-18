// Create Database Modal JavaScript Functions

// Global state
let selectedFiles = [];
let validationResult = null;

/**
 * Open the create database modal
 */
function openCreateDatabaseModal() {
    const modal = document.getElementById('createDatabaseModal');
    modal.style.display = 'flex';
    resetModal();
}

/**
 * Close the create database modal
 */
function closeCreateDatabaseModal() {
    const modal = document.getElementById('createDatabaseModal');
    modal.style.display = 'none';
    resetModal();
}

/**
 * Reset modal to initial state
 */
function resetModal() {
    // Reset form
    document.getElementById('createDatabaseForm').reset();
    
    // Reset file selection
    selectedFiles = [];
    validationResult = null;
    document.getElementById('fileList').style.display = 'none';
    document.getElementById('fileList').innerHTML = '';
    document.getElementById('uploadInfo').textContent = 'No files selected';
    
    // Hide validation and results sections
    document.getElementById('validationResults').style.display = 'none';
    document.getElementById('ingestionProgress').style.display = 'none';
    document.getElementById('finalResults').style.display = 'none';
    
    // Reset buttons
    document.getElementById('validateButton').disabled = true;
    document.getElementById('createButton').style.display = 'none';
    document.getElementById('createButton').disabled = true;
    
    // Reset mode selection
    updateModeSelection();
}

/**
 * Update UI based on selected ingest mode
 */
function updateModeSelection() {
    const mode = document.querySelector('input[name="ingest_mode"]:checked').value;
    
    const columnConfig = document.getElementById('columnConfig');
    const textColumnGroup = document.getElementById('textColumnGroup');
    const imageColumnGroup = document.getElementById('imageColumnGroup');
    const textEmbedderConfig = document.getElementById('textEmbedderConfig');
    const imageEmbedderConfig = document.getElementById('imageEmbedderConfig');
    
    // Show/hide column configuration based on mode
    if (mode === 'text') {
        columnConfig.style.display = 'block';
        textColumnGroup.style.display = 'block';
        imageColumnGroup.style.display = 'none';
        textEmbedderConfig.style.display = 'block';
        imageEmbedderConfig.style.display = 'none';
        document.getElementById('textColumn').required = true;
        document.getElementById('imageColumn').required = false;
    } else if (mode === 'image') {
        columnConfig.style.display = 'block';
        textColumnGroup.style.display = 'none';
        imageColumnGroup.style.display = 'block';
        textEmbedderConfig.style.display = 'none';
        imageEmbedderConfig.style.display = 'block';
        document.getElementById('textColumn').required = false;
        document.getElementById('imageColumn').required = true;
    } else if (mode === 'hybrid') {
        columnConfig.style.display = 'block';
        textColumnGroup.style.display = 'block';
        imageColumnGroup.style.display = 'block';
        textEmbedderConfig.style.display = 'block';
        imageEmbedderConfig.style.display = 'block';
        document.getElementById('textColumn').required = true;
        document.getElementById('imageColumn').required = true;
    }
    
    // Update file input accept attribute
    const fileInput = document.getElementById('fileInput');
    if (mode === 'text') {
        fileInput.accept = '.csv,.txt,.json';
    } else if (mode === 'image') {
        fileInput.accept = '.jpg,.jpeg,.png,.webp';
    } else {
        fileInput.accept = '.csv,.txt,.json,.jpg,.jpeg,.png,.webp';
    }
}

/**
 * Toggle advanced configuration section
 */
function toggleAdvancedConfig() {
    const advancedConfig = document.getElementById('advancedConfig');
    const icon = document.getElementById('advancedToggleIcon');
    
    if (advancedConfig.style.display === 'none') {
        advancedConfig.style.display = 'block';
        icon.textContent = '▼';
    } else {
        advancedConfig.style.display = 'none';
        icon.textContent = '▶';
    }
}

/**
 * Handle file selection from input
 */
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    addFiles(files);
}

/**
 * Handle drag over event
 */
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('fileUploadArea').classList.add('drag-over');
}

/**
 * Handle drag leave event
 */
function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('fileUploadArea').classList.remove('drag-over');
}

/**
 * Handle file drop event
 */
function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    document.getElementById('fileUploadArea').classList.remove('drag-over');
    
    const files = Array.from(event.dataTransfer.files);
    addFiles(files);
}

/**
 * Add files to selection and update UI
 */
function addFiles(files) {
    selectedFiles = [...selectedFiles, ...files];
    updateFileList();
    updateUploadInfo();
    document.getElementById('validateButton').disabled = selectedFiles.length === 0;
}

/**
 * Remove file from selection
 */
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    updateUploadInfo();
    document.getElementById('validateButton').disabled = selectedFiles.length === 0;
    
    // Hide validation results if files changed
    document.getElementById('validationResults').style.display = 'none';
    document.getElementById('createButton').style.display = 'none';
    validationResult = null;
}

/**
 * Update file list display
 */
function updateFileList() {
    const fileList = document.getElementById('fileList');
    
    if (selectedFiles.length === 0) {
        fileList.style.display = 'none';
        return;
    }
    
    fileList.style.display = 'block';
    fileList.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${formatFileSize(file.size)}</span>
            <button type="button" class="btn-icon" onclick="removeFile(${index})">
                ×
            </button>
        </div>
    `).join('');
}

/**
 * Update upload info text
 */
function updateUploadInfo() {
    const info = document.getElementById('uploadInfo');
    if (selectedFiles.length === 0) {
        info.textContent = 'No files selected';
    } else {
        const totalSize = selectedFiles.reduce((sum, file) => sum + file.size, 0);
        info.textContent = `${selectedFiles.length} file(s) selected (${formatFileSize(totalSize)})`;
    }
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Validate files before creating database
 */
async function validateFiles() {
    if (selectedFiles.length === 0) return;
    
    const validateButton = document.getElementById('validateButton');
    validateButton.disabled = true;
    validateButton.textContent = 'Validating...';
    
    try {
        const formData = new FormData();
        const mode = document.querySelector('input[name="ingest_mode"]:checked').value;
        formData.append('ingest_mode', mode);
        
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch('/api/databases/validate', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Validation failed');
        }
        
        validationResult = await response.json();
        displayValidationResults(validationResult);
        
    } catch (error) {
        console.error('Validation error:', error);
        showToast('Validation failed: ' + error.message, 'error');
    } finally {
        validateButton.disabled = false;
        validateButton.textContent = 'Validate Files';
    }
}

/**
 * Display validation results
 */
function displayValidationResults(result) {
    const resultsSection = document.getElementById('validationResults');
    const summaryDiv = document.getElementById('validationSummary');
    const detailsDiv = document.getElementById('validationDetails');
    
    resultsSection.style.display = 'block';
    
    // Display summary
    const statusClass = result.overall_status === 'VALID' ? 'success' : 
                       result.overall_status === 'WARNING' ? 'warning' : 'error';
    
    summaryDiv.innerHTML = `
        <div class="validation-summary-${statusClass}">
            <h4>${result.summary_message}</h4>
            <div class="validation-stats">
                <span class="stat"><strong>${result.valid_count}</strong> Valid</span>
                <span class="stat"><strong>${result.warning_count}</strong> Warnings</span>
                <span class="stat"><strong>${result.invalid_count}</strong> Invalid</span>
            </div>
        </div>
    `;
    
    // Display per-file details if there are any issues
    if (result.warning_count > 0 || result.invalid_count > 0) {
        detailsDiv.style.display = 'block';
        detailsDiv.innerHTML = '<h4>File Details</h4>' + result.file_results.map(fileResult => {
            if (fileResult.status === 'VALID') return '';
            
            const statusIcon = fileResult.status === 'WARNING' ? '⚠️' : '❌';
            return `
                <div class="file-validation-item">
                    <div class="file-validation-header">
                        ${statusIcon} <strong>${fileResult.filename}</strong>
                        <span class="file-size">${formatFileSize(fileResult.file_size || 0)}</span>
                    </div>
                    ${fileResult.errors && fileResult.errors.length > 0 ? `
                        <ul class="validation-errors">
                            ${fileResult.errors.map(err => `<li class="error">${err}</li>`).join('')}
                        </ul>
                    ` : ''}
                    ${fileResult.warnings && fileResult.warnings.length > 0 ? `
                        <ul class="validation-warnings">
                            ${fileResult.warnings.map(warn => `<li class="warning">${warn}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        }).join('');
    } else {
        detailsDiv.style.display = 'none';
    }
    
    // Enable/disable create button based on validation
    const createButton = document.getElementById('createButton');
    if (result.can_proceed) {
        createButton.style.display = 'inline-block';
        createButton.disabled = false;
    } else {
        createButton.style.display = 'none';
        createButton.disabled = true;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Reuse existing toast partial from HTMX responses
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Initialize modal on page load
document.addEventListener('DOMContentLoaded', function() {
    updateModeSelection();
});
