/**
 * ContentHub — Core JS
 */

// ═══ TOAST ═══
function showToast(msg, type='success') {
    const c = document.getElementById('toastContainer');
    const t = document.createElement('div');
    t.className = 'toast ' + type;
    const icons = {success:'fa-check-circle', error:'fa-exclamation-circle', warning:'fa-exclamation-triangle'};
    t.innerHTML = `<i class="fas ${icons[type]||icons.success}"></i><span>${msg}</span>`;
    c.appendChild(t);
    setTimeout(() => { t.style.opacity='0'; t.style.transform='translateX(16px)'; t.style.transition='all .2s'; setTimeout(()=>t.remove(),200); }, 3500);
}

// ═══ LOADING ═══
function showLoading(text='Processing...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').style.display = 'flex';
}
function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// ═══ MODAL ═══
function openModal(id) {
    document.getElementById(id).style.display = 'flex';
    if (id === 'accountsModal') loadAccountsModal();
}
function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

// Close modal on backdrop click
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.style.display = 'none';
    }
});

// ═══ ACCOUNTS MODAL ═══
function loadAccountsModal() {
    const platforms = [
        {key:'youtube', name:'YouTube', icon:'youtube', color:'#FF0000'},
        {key:'tiktok', name:'TikTok', icon:'tiktok', color:'#00f2ea'},
        {key:'instagram', name:'Instagram', icon:'instagram', color:'#E4405F'},
        {key:'facebook', name:'Facebook', icon:'facebook', color:'#1877F2'},
    ];

    fetch('/api/accounts').then(r=>r.json()).then(accounts => {
        let html = '<div class="acc-grid">';
        platforms.forEach(p => {
            const acc = accounts.find(a => a.platform === p.key);
            const connected = acc && acc.access_token;
            html += `<div class="acc-card">
                <div class="acc-card-head">
                    <div class="acc-icon" style="background:${p.color}20;color:${p.color}">
                        <i class="fab fa-${p.icon}"></i>
                    </div>
                    <div>
                        <div class="acc-card-name">${p.name}</div>
                        <div class="acc-card-status ${connected ? 'acc-connected' : 'acc-disconnected'}">
                            ${connected ? '<i class="fas fa-check-circle"></i> Connected' : '<i class="fas fa-times-circle"></i> Not connected'}
                        </div>
                    </div>
                </div>`;

            if (connected) {
                html += `<div class="acc-btn-row">
                    <button class="btn-ghost" onclick="disconnectAccount('${p.key}')"><i class="fas fa-unlink"></i> Disconnect</button>
                </div>`;
            } else {
                html += `<div class="acc-card-form">
                    <input class="acc-input" id="acc-token-${p.key}" placeholder="Access Token *">
                    <input class="acc-input" id="acc-name-${p.key}" placeholder="Account Name">
                    ${p.key === 'instagram' || p.key === 'facebook' ? `<input class="acc-input" id="acc-id-${p.key}" placeholder="Page/Account ID *">` : ''}
                    <div class="acc-btn-row">
                        <button class="btn-main" style="padding:6px 14px;font-size:12px" onclick="connectAccount('${p.key}')"><i class="fas fa-link"></i> Connect</button>
                    </div>
                </div>`;
            }
            html += '</div>';
        });
        html += '</div>';
        document.getElementById('accountsModalBody').innerHTML = html;
    });
}

async function connectAccount(platform) {
    const token = document.getElementById(`acc-token-${platform}`)?.value.trim();
    if (!token) { showToast('Enter an access token','error'); return; }
    const name = document.getElementById(`acc-name-${platform}`)?.value.trim() || '';
    const id = document.getElementById(`acc-id-${platform}`)?.value.trim() || '';

    try {
        const res = await fetch(`/api/accounts/connect/${platform}`, {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({access_token:token, account_name:name, account_id:id})
        });
        const data = await res.json();
        if (data.success) { showToast(data.message,'success'); loadAccountsModal(); }
        else showToast(data.error,'error');
    } catch(e) { showToast('Failed','error'); }
}

async function disconnectAccount(platform) {
    if (!confirm('Disconnect ' + platform + '?')) return;
    try {
        const res = await fetch(`/api/accounts/delete/${platform}`, {method:'DELETE'});
        const data = await res.json();
        if (data.success) { showToast('Disconnected','success'); loadAccountsModal(); }
    } catch(e) { showToast('Failed','error'); }
}
