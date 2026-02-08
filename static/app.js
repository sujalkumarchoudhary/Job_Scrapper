/**
 * Job Scraper Application - Frontend JavaScript
 */

// ==========================================
// DOM Elements
// ==========================================
const searchForm = document.getElementById('searchForm');
const jobTitleInput = document.getElementById('jobTitle');
const locationInput = document.getElementById('location');
const remoteOnlyCheck = document.getElementById('remoteOnly');
const numJobsSelect = document.getElementById('numJobs');
const searchBtn = document.getElementById('searchBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsCount = document.getElementById('resultsCount');
const resultsQuery = document.getElementById('resultsQuery');
const jobsGrid = document.getElementById('jobsGrid');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorToast = document.getElementById('errorToast');
const errorMessage = document.getElementById('errorMessage');
const summaryModal = document.getElementById('summaryModal');
const summaryContent = document.getElementById('summaryContent');

// Store jobs data for AI summarization
let jobsData = [];

// ==========================================
// Initialize
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    searchForm.addEventListener('submit', handleSearch);
});

// ==========================================
// Particle Animation
// ==========================================
function initParticles() {
    const container = document.getElementById('particles');
    const particleCount = 30;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.top = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 15}s`;
        particle.style.animationDuration = `${15 + Math.random() * 10}s`;
        container.appendChild(particle);
    }
}

// ==========================================
// Search Handler
// ==========================================
async function handleSearch(e) {
    e.preventDefault();

    const query = jobTitleInput.value.trim();
    const location = locationInput.value.trim();
    const remoteOnly = remoteOnlyCheck.checked;
    const numJobs = parseInt(numJobsSelect.value);

    if (!query || !location) {
        showError('Please enter both job title and location');
        return;
    }

    showLoading(true);
    setButtonLoading(true);

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                location,
                num_jobs: numJobs,
                remote_only: remoteOnly
            })
        });

        if (!response.ok) {
            const error = await response.json();
            if (response.status === 429) {
                throw new Error('Rate limit exceeded. Please wait a minute before searching again.');
            }
            throw new Error(error.detail || 'Search failed');
        }

        const data = await response.json();
        jobsData = data.jobs;
        displayResults(data);

    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
        setButtonLoading(false);
    }
}

// ==========================================
// Display Results
// ==========================================
function displayResults(data) {
    resultsCount.textContent = data.total;
    resultsQuery.textContent = `Showing results for "${data.search_query}" in ${data.location}`;

    jobsGrid.innerHTML = '';

    if (data.jobs.length === 0) {
        jobsGrid.innerHTML = `
            <div class="no-results">
                <p>No jobs found. Try different keywords or location.</p>
            </div>
        `;
    } else {
        data.jobs.forEach((job, index) => {
            const card = createJobCard(job, index);
            jobsGrid.appendChild(card);
        });
    }

    resultsSection.classList.add('active');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ==========================================
// Create Job Card
// ==========================================
function createJobCard(job, index) {
    const card = document.createElement('div');
    card.className = 'job-card';
    card.style.animationDelay = `${index * 0.05}s`;

    const logoContent = job.thumbnail
        ? `<img src="${job.thumbnail}" alt="${job.company}" onerror="this.parentElement.innerHTML='💼'">`
        : '💼';

    const tags = [];
    if (job.location) tags.push(`<span class="job-tag">📍 ${job.location}</span>`);
    if (job.work_from_home) tags.push(`<span class="job-tag remote">🏠 Remote</span>`);
    if (job.salary) tags.push(`<span class="job-tag salary">💰 ${job.salary}</span>`);
    if (job.schedule) tags.push(`<span class="job-tag">⏰ ${job.schedule}</span>`);
    if (job.posted) tags.push(`<span class="job-tag">📅 ${job.posted}</span>`);

    const applyLink = job.apply_links && job.apply_links.length > 0
        ? job.apply_links[0].url
        : '#';

    card.innerHTML = `
        <div class="job-header">
            <div class="job-logo">${logoContent}</div>
            <div class="job-info">
                <h3 class="job-title">${escapeHtml(job.title)}</h3>
                <p class="job-company">${escapeHtml(job.company)}</p>
            </div>
        </div>
        <div class="job-meta">
            ${tags.join('')}
        </div>
        <p class="job-description">${escapeHtml(job.description || 'No description available')}</p>
        <div class="job-actions">
            <button class="btn btn-ai" onclick="summarizeJob(${index})">
                ✨ AI Summary
            </button>
            <a href="${applyLink}" target="_blank" rel="noopener" class="btn btn-secondary">
                Apply Now →
            </a>
        </div>
    `;

    return card;
}

// ==========================================
// AI Summarization
// ==========================================
async function summarizeJob(index) {
    const job = jobsData[index];
    if (!job) return;

    openModal();
    showSummaryLoading();

    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: job.description
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Summarization failed');
        }

        const data = await response.json();
        displaySummary(job, data);

    } catch (error) {
        summaryContent.innerHTML = `
            <div class="summary-loading">
                <span style="font-size: 2rem;">⚠️</span>
                <p>${error.message}</p>
                <p style="font-size: 0.9rem; color: var(--text-muted);">
                    Make sure GROQ_API_KEY is configured in your .env file
                </p>
            </div>
        `;
    }
}

function displaySummary(job, data) {
    const skillsList = data.key_skills && data.key_skills.length > 0
        ? data.key_skills.map(skill => `<li>${escapeHtml(skill)}</li>`).join('')
        : '<li>No specific skills extracted</li>';

    const benefitsList = data.benefits && data.benefits.length > 0
        ? data.benefits.map(benefit => `<li>${escapeHtml(benefit)}</li>`).join('')
        : '<li>No benefits mentioned</li>';

    summaryContent.innerHTML = `
        <div class="summary-section">
            <h4>Job Title</h4>
            <p><strong>${escapeHtml(job.title)}</strong> at ${escapeHtml(job.company)}</p>
        </div>
        <div class="summary-section">
            <h4>Summary</h4>
            <p>${escapeHtml(data.summary || 'No summary available')}</p>
        </div>
        <div class="summary-section">
            <h4>Key Skills Required</h4>
            <ul class="summary-list">${skillsList}</ul>
        </div>
        <div class="summary-section">
            <h4>Benefits</h4>
            <ul class="summary-list">${benefitsList}</ul>
        </div>
    `;
}

function showSummaryLoading() {
    summaryContent.innerHTML = `
        <div class="summary-loading">
            <div class="loading-spinner small"></div>
            <p>Analyzing job with AI...</p>
        </div>
    `;
}

// ==========================================
// Modal Functions
// ==========================================
function openModal() {
    summaryModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    summaryModal.classList.add('hidden');
    document.body.style.overflow = '';
}

// Close modal on backdrop click
summaryModal.addEventListener('click', (e) => {
    if (e.target === summaryModal) {
        closeModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !summaryModal.classList.contains('hidden')) {
        closeModal();
    }
});

// ==========================================
// UI Helpers
// ==========================================
function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

function setButtonLoading(loading) {
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoader = searchBtn.querySelector('.btn-loader');

    if (loading) {
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        searchBtn.disabled = true;
    } else {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
        searchBtn.disabled = false;
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorToast.classList.remove('hidden');

    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    errorToast.classList.add('hidden');
}

// ==========================================
// Utilities
// ==========================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
