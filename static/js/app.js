const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const checkoutPanel = document.getElementById('checkoutPanel');
const sendBtn = document.getElementById('sendBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const sessionId = Math.random().toString(36).substring(7);
let isThinking = false;
let currentOffer = null;

// ─── Helpers ───────────────────────────────────────────────────────────────

function setThinking(active) {
    isThinking = active;
    sendBtn.disabled = active;
    statusDot.className = active ? 'status-dot thinking' : 'status-dot';
    statusText.textContent = active ? 'Agent thinking…' : 'Agent Ready';
}

function scrollBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendUserMsg(text) {
    const wrap = document.createElement('div');
    wrap.className = 'message user';
    wrap.innerHTML = `<div class="msg-content">${escHtml(text)}</div>`;
    chatMessages.appendChild(wrap);
    scrollBottom();
}

function appendBotMsg(htmlContent) {
    const wrap = document.createElement('div');
    wrap.className = 'message bot';
    wrap.innerHTML = `
        <div class="bot-avatar">🤖</div>
        <div class="msg-content">${htmlContent}</div>`;
    chatMessages.appendChild(wrap);
    scrollBottom();
    return wrap;
}

function appendThinkingMsg(steps) {
    const lines = steps.map(s => `<div class="thinking-step">${markdownText(s)}</div>`).join('');
    const wrap = document.createElement('div');
    wrap.className = 'message bot thinking-msg';
    wrap.innerHTML = `
        <div class="bot-avatar">⚙️</div>
        <div class="msg-content">${lines || '<div class="dots-loader"><span></span><span></span><span></span></div>'}</div>`;
    chatMessages.appendChild(wrap);
    scrollBottom();
    return wrap;
}

function buildProductCard(offer) {
    if (!offer) return '';
    const hasDiscount = offer.discount > 0;
    const discountHtml = hasDiscount ? `
        <span class="original-price">$${offer.price.toFixed(2)}</span>
        <span class="discount-badge">-$${offer.discount.toFixed(2)} off</span>` : '';
    const imgHtml = offer.image_url
        ? `<img src="${offer.image_url}" alt="${escHtml(offer.product_name)}" loading="lazy">`
        : '';
    const isMultiple = (offer.quantity || 1) > 1;
    const finalPrice = offer.total_price || offer.unit_final_price || offer.final_price;
    const unitPrice = offer.unit_final_price || offer.final_price;

    return `
        <div class="product-card">
            ${imgHtml}
            <div class="card-info">
                <div class="card-name">${escHtml(offer.product_name)}</div>
                <div class="card-vendor">
                    📦 ${escHtml(offer.vendor)} · ${offer.size ? 'Size ' + offer.size : ''} ${offer.width || ''}
                    ${isMultiple ? `<br><small>Unit Price: $${unitPrice.toFixed(2)} x ${offer.quantity}</small>` : ''}
                </div>
                <div class="card-price">
                    <span class="final-price">$${finalPrice.toFixed(2)}</span>
                    ${discountHtml}
                    ${isMultiple && offer.unit_discount > 0 ? `<span class="discount-badge">Total saving: $${(offer.unit_discount * offer.quantity).toFixed(2)}</span>` : ''}
                </div>
            </div>
        </div>`;
}

function buildSearchResultCards(products) {
    if (!products || products.length === 0) return '';
    let html = '<div class="search-results-grid">';
    for (const p of products) {
        const imgHtml = p.image_url
            ? `<img src="${p.image_url}" alt="${escHtml(p.name)}" loading="lazy">`
            : '';
        html += `
            <div class="product-card search-result-card">
                ${imgHtml}
                <div class="card-info">
                    <div class="card-name">${escHtml(p.name)}</div>
                    <div class="card-vendor">🏷️ ${escHtml(p.brand)} · ${escHtml(p.category)}</div>
                    <div class="card-price">
                        <span class="final-price">$${p.base_price.toFixed(2)}</span>
                    </div>
                    <div class="card-desc">${escHtml(p.description)}</div>
                </div>
            </div>`;
    }
    html += '</div>';
    return html;
}

function markdownText(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/🔍|⚙️|✅|🎉|📦|💳|👟|📚/g, s => s) // emoji passthrough
        .replace(/\n/g, '<br>');
}

function escHtml(str) {
    return String(str || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// ─── Send ──────────────────────────────────────────────────────────────────

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text || isThinking) return;
    userInput.value = '';

    appendUserMsg(text);
    setThinking(true);

    // Show immediate thinking animation
    const thinkingEl = appendThinkingMsg([]);

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, session_id: sessionId }),
        });
        const data = await res.json();

        // Replace thinking animation with real thinking steps
        thinkingEl.remove();
        if (data.thinking_steps && data.thinking_steps.length > 0) {
            appendThinkingMsg(data.thinking_steps);
        }

        // Build bot reply
        let replyHtml = markdownText(data.reply);

        // Show search result cards with product images
        if (data.search_results && data.search_results.length > 0 && !data.offer_details) {
            replyHtml += buildSearchResultCards(data.search_results);
        }

        // Show product card if we have a NEW offer
        if (data.offer_details) {
            replyHtml += buildProductCard(data.offer_details);
        }

        // Always sync the current contextual offer from backend session
        if (data.current_context_offer) {
            currentOffer = data.current_context_offer;
        }

        const msgEl = appendBotMsg(replyHtml);

        // Auto-trigger checkout if signaled by agent
        if (data.trigger_checkout) {
            console.log('trigger_checkout signal received, data:', data);
            console.log('currentOffer before showCheckout:', currentOffer);
            showCheckout();
        }

    } catch (err) {
        thinkingEl.remove();
        appendBotMsg("Sorry, I'm having trouble reaching my backend. Please try again.");
    }

    setThinking(false);
}

function handleKeyPress(e) {
    if (e.key === 'Enter') sendMessage();
}

// ─── Checkout ──────────────────────────────────────────────────────────────

function showCheckout() {
    console.log('showCheckout called, currentOffer:', currentOffer);
    if (!currentOffer) {
        console.error('No current offer available for checkout');
        // Create a dummy offer for testing purposes
        currentOffer = {
            product_name: 'Test Product',
            vendor: 'Test Vendor',
            quantity: 1,
            total_price: 99.99,
            final_price: 99.99
        };
        console.log('Created dummy offer for testing:', currentOffer);
    }
    const summary = document.getElementById('checkoutProductSummary');
    const isMultiple = (currentOffer.quantity || 1) > 1;
    const total = currentOffer.total_price || currentOffer.unit_final_price || currentOffer.final_price;
    const totalDiscount = (currentOffer.unit_discount || currentOffer.discount || 0) * (currentOffer.quantity || 1);

    summary.innerHTML = `
        <strong>${escHtml(currentOffer.product_name)}</strong><br>
        Vendor: ${escHtml(currentOffer.vendor)}<br>
        ${isMultiple ? `Quantity: ${currentOffer.quantity}<br>` : ''}
        Total: <strong style="color:#10b981">$${total.toFixed(2)}</strong>
        ${totalDiscount > 0 ? ` (saving $${totalDiscount.toFixed(2)}!)` : ''}`;
    checkoutPanel.classList.remove('hidden');
    console.log('Checkout panel should now be visible');
}

// Global function for manual testing (accessible from browser console)
window.triggerCheckoutPopup = function() {
    console.log('Manual checkout popup trigger called');
    showCheckout();
};

function cancelCheckout() {
    checkoutPanel.classList.add('hidden');
}

async function processCheckout() {
    // Shipping address
    const shipName = document.getElementById('shipName').value.trim();
    const shipStreet = document.getElementById('shipStreet').value.trim();
    const shipCity = document.getElementById('shipCity').value.trim();
    const shipState = document.getElementById('shipState').value.trim();
    const shipZip = document.getElementById('shipZip').value.trim();
    const shipCountry = document.getElementById('shipCountry').value.trim();

    if (!shipName || !shipStreet || !shipCity || !shipState || !shipZip) {
        alert('Please fill in all shipping address fields.');
        return;
    }

    // Payment details
    const cardType = document.querySelector('input[name="cardType"]:checked').value;
    const cardNumber = document.getElementById('cardNumber').value.replace(/\s/g, '');
    const cardExpiry = document.getElementById('cardExpiry').value.replace(/\s/g, '');
    const cardCvc = document.getElementById('cardCvc').value.trim();

    if (!cardNumber || cardNumber.length !== 16 || isNaN(cardNumber)) {
        alert('Please enter a valid 16-digit card number.');
        return;
    }
    if (!cardExpiry || !/^\d{2}\/\d{2}$/.test(cardExpiry)) {
        alert('Please enter a valid expiry date (MM/YY).');
        return;
    }
    if (!cardCvc || !/^\d{3,4}$/.test(cardCvc)) {
        alert('Please enter a valid 3 or 4 digit CVC.');
        return;
    }

    // Disable pay button to prevent double-submit
    const payBtn = document.querySelector('.pay-btn');
    payBtn.disabled = true;
    payBtn.textContent = '⏳ Processing…';

    try {
        const res = await fetch('/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                card_type: cardType,
                card_number: cardNumber,
                card_expiry: cardExpiry,
                card_cvc: cardCvc,
                shipping_address: {
                    name: shipName,
                    street: shipStreet,
                    city: shipCity,
                    state: shipState,
                    zip: shipZip,
                    country: shipCountry || 'United States',
                },
            }),
        });
        const data = await res.json();
        cancelCheckout();
        appendBotMsg(markdownText(data.message));
        if (data.success) currentOffer = null;
    } catch {
        alert('Payment service unavailable. Please try again.');
    } finally {
        payBtn.disabled = false;
        payBtn.textContent = 'Confirm & Pay';
    }
}

// ─── Card number formatting ─────────────────────────────────────────────────

document.getElementById('cardNumber').oninput = function () {
    this.value = this.value.replace(/[^\d]/g, '').replace(/(.{4})/g, '$1 ').trim().substring(0, 19);
};

document.getElementById('cardExpiry').oninput = function () {
    let v = this.value.replace(/[^\d]/g, '');
    if (v.length >= 2) v = v.substring(0, 2) + ' / ' + v.substring(2, 4);
    this.value = v;
};

// ─── Clear Chat ─────────────────────────────────────────────────────────────

function clearChat() {
    chatMessages.innerHTML = '';
    currentOffer = null;
    appendBotMsg('Chat cleared. What are you looking for?');
}

// ─── Sidebar hints ──────────────────────────────────────────────────────────

document.querySelectorAll('.sidebar-hint p').forEach(el => {
    el.addEventListener('click', () => {
        userInput.value = el.textContent.replace(/['"]/g, '');
        userInput.focus();
    });
});

// ─── Sidebar Capabilities Navigation ───────────────────────────────────────
function updateActiveNavItem(id) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

document.getElementById('navChat').addEventListener('click', () => {
    clearChat();
    updateActiveNavItem('navChat');
});

document.getElementById('navShoes').addEventListener('click', () => {
    userInput.value = "Show me some shoes";
    sendMessage();
    updateActiveNavItem('navShoes');
});

document.getElementById('navBooks').addEventListener('click', () => {
    userInput.value = "Show me some books";
    sendMessage();
    updateActiveNavItem('navBooks');
});
