async function runMatchScore(appId) {
    const btn = document.getElementById('matchBtn');
    const resultDiv = document.getElementById('matchResult');
    btn.disabled = true;
    btn.textContent = 'Analyzing...';
    resultDiv.innerHTML = '<p>Calling AI model, please wait...</p>';

    try {
        const res = await fetch(`/api/match-score/${appId}`, { method: 'POST' });
        const data = await res.json();

        if (data.error) {
            resultDiv.innerHTML = `<p class="warning-text">${data.error}</p>`;
        } else {
            resultDiv.innerHTML = `
                <div class="score-circle">${data.match_score}%</div>
                ${data.mock ? '<p class="warning-text">(Mock response — add API key for real results)</p>' : ''}
                <p><strong>Matched:</strong> ${data.matched_skills.join(', ') || 'None'}</p>
                <p><strong>Missing:</strong> ${data.missing_skills.join(', ') || 'None'}</p>
                <p><strong>Tip:</strong> ${data.suggestions}</p>
            `;
        }
    } catch (err) {
        resultDiv.innerHTML = `<p class="warning-text">Something went wrong: ${err.message}</p>`;
    }

    btn.disabled = false;
    btn.textContent = 'Analyze Match';
}

async function generateEmail(appId) {
    const btn = document.getElementById('emailBtn');
    const resultDiv = document.getElementById('emailResult');
    btn.disabled = true;
    btn.textContent = 'Generating...';
    resultDiv.innerHTML = '<p>Calling AI model, please wait...</p>';

    try {
        const res = await fetch(`/api/generate-email/${appId}`, { method: 'POST' });
        const data = await res.json();

        if (data.error) {
            resultDiv.innerHTML = `<p class="warning-text">${data.error}</p>`;
        } else {
            resultDiv.innerHTML = `
                ${data.mock ? '<p class="warning-text">(Mock response — add API key for real results)</p>' : ''}
                <p><strong>Subject:</strong> ${data.subject}</p>
                <div class="email-box">${data.body}</div>
            `;
        }
    } catch (err) {
        resultDiv.innerHTML = `<p class="warning-text">Something went wrong: ${err.message}</p>`;
    }

    btn.disabled = false;
    btn.textContent = 'Generate Follow-up Email';
}
