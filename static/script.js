// ============================================================
// DOM READY
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    setInterval(updateTime, 10000);
    setInterval(refreshStatus, 30000);
});

// ============================================================
// TIME
// ============================================================

function updateTime() {
    const now = new Date();
    const timeStr = now.toISOString().replace('T', ' ').slice(0, 19);
    const el = document.getElementById('current-time');
    if (el) el.textContent = timeStr;
}

// ============================================================
// POST NOW
// ============================================================

function postNow() {
    showStatus('postStatus', 'Posting...', 'info');
    
    fetch('/social_media/post_now', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('postStatus', '✅ ' + data.message, 'success');
            setTimeout(refreshStatus, 2000);
        } else {
            showStatus('postStatus', '❌ ' + data.message, 'error');
        }
    })
    .catch(error => {
        showStatus('postStatus', '❌ Error: ' + error, 'error');
    });
}

// ============================================================
// UPLOAD IMAGE
// ============================================================

document.getElementById('uploadForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    showStatus('uploadStatus', 'Uploading...', 'info');
    
    fetch('/social_media/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('uploadStatus', '✅ ' + data.message, 'success');
            this.reset();
            setTimeout(refreshStatus, 2000);
        } else {
            showStatus('uploadStatus', '❌ ' + data.message, 'error');
        }
    })
    .catch(error => {
        showStatus('uploadStatus', '❌ Error: ' + error, 'error');
    });
});

document.getElementById('uploadMultipleForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    showStatus('multiUploadStatus', 'Uploading...', 'info');
    
    fetch('/social_media/upload_multiple', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('multiUploadStatus', '✅ ' + data.message, 'success');
            this.reset();
        } else {
            showStatus('multiUploadStatus', '❌ ' + data.message, 'error');
        }
    })
    .catch(error => {
        showStatus('multiUploadStatus', '❌ Error: ' + error, 'error');
    });
});

// ============================================================
// PROMPTS
// ============================================================

document.getElementById('addPromptForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    showStatus('addPromptStatus', 'Adding...', 'info');
    
    fetch('/social_media/add_prompt', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('addPromptStatus', '✅ ' + data.message, 'success');
            this.reset();
            setTimeout(refreshStatus, 1000);
        } else {
            showStatus('addPromptStatus', '❌ ' + data.message, 'error');
        }
    })
    .catch(error => {
        showStatus('addPromptStatus', '❌ Error: ' + error, 'error');
    });
});

document.getElementById('addMultiplePromptsForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    showStatus('multiPromptStatus', 'Adding prompts...', 'info');
    
    fetch('/social_media/add_multiple_prompts', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus('multiPromptStatus', '✅ ' + data.message, 'success');
            this.reset();
            setTimeout(refreshStatus, 1000);
        } else {
            showStatus('multiPromptStatus', '❌ ' + data.message, 'error');
        }
    })
    .catch(error => {
        showStatus('multiPromptStatus', '❌ Error: ' + error, 'error');
    });
});

function deletePrompt(index) {
    if (!confirm('Delete this prompt?')) return;
    
    fetch(`/social_media/delete_prompt/${index}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('❌ ' + data.message);
        }
    });
}

function clearAllPrompts() {
    if (!confirm('⚠️ Delete ALL prompts? This cannot be undone!')) return;
    
    fetch('/social_media/clear_all_prompts', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('❌ ' + data.message);
        }
    });
}

// ============================================================
// STATUS
// ============================================================

function refreshStatus() {
    fetch('/social_media/api/status')
    .then(response => response.json())
    .then(data => {
        const nextEl = document.querySelector('.next-post-card strong');
        if (nextEl) {
            nextEl.textContent = data.next_post || 'Not scheduled';
        }
    })
    .catch(error => console.error('Status error:', error));
}

// ============================================================
// HELPERS
// ============================================================

function showStatus(id, message, type) {
    const el = document.getElementById(id);
    if (!el) return;
    
    el.className = `status-message ${type}`;
    el.textContent = message;
    el.style.display = 'block';
    
    clearTimeout(el._timeout);
    el._timeout = setTimeout(() => {
        el.style.display = 'none';
    }, 5000);
}