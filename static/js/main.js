/**
 * Notes Management Application - Main JavaScript
 * Handles Theme Toggling, Modals, Dynamic Character/Word Count,
 * Favorite Star AJAX Toggling, and Responsive Sidebar.
 */

document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------
    // 1. Theme Management (Dark / Light Mode)
    // -------------------------------------------------------------
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('notes_theme', theme);
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
        if (themeToggleBtn) {
            themeToggleBtn.setAttribute('title', theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode');
        }
    }

    // Initialize theme from storage or system preference
    const savedTheme = localStorage.getItem('notes_theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? 'dark' : 'light');
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }

    // -------------------------------------------------------------
    // 2. Mobile Sidebar Navigation
    // -------------------------------------------------------------
    const menuToggleBtn = document.getElementById('menu-toggle-btn');
    const appSidebar = document.getElementById('app-sidebar');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');

    function openSidebar() {
        if (appSidebar) appSidebar.classList.add('open');
        if (sidebarBackdrop) sidebarBackdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
        if (appSidebar) appSidebar.classList.remove('open');
        if (sidebarBackdrop) sidebarBackdrop.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (menuToggleBtn) {
        menuToggleBtn.addEventListener('click', openSidebar);
    }
    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', closeSidebar);
    }

    // -------------------------------------------------------------
    // 3. View Note Modal
    // -------------------------------------------------------------
    const viewModalOverlay = document.getElementById('view-modal-overlay');
    const viewModalCloseBtn = document.getElementById('view-modal-close-btn');
    const viewModalCloseFooterBtn = document.getElementById('view-modal-close-footer');
    const viewModalTitle = document.getElementById('view-modal-title');
    const viewModalBadge = document.getElementById('view-modal-badge');
    const viewModalContent = document.getElementById('view-modal-content');
    const viewModalDate = document.getElementById('view-modal-date');
    const viewModalWords = document.getElementById('view-modal-words');
    const viewModalEditBtn = document.getElementById('view-modal-edit-btn');
    const viewModalDeleteBtn = document.getElementById('view-modal-delete-btn');

    function openViewModal(data) {
        if (!viewModalOverlay) return;

        if (viewModalTitle) viewModalTitle.textContent = data.title || 'Untitled Note';
        if (viewModalContent) viewModalContent.textContent = data.content || '';
        if (viewModalDate) viewModalDate.textContent = data.created || '';
        if (viewModalWords) viewModalWords.textContent = `${data.words || 0} words • ${data.reading || 1} min read`;

        if (viewModalBadge) {
            const cat = (data.category || 'Other').toLowerCase();
            viewModalBadge.className = `category-badge ${cat}`;
            viewModalBadge.textContent = data.category || 'Other';
        }

        if (viewModalEditBtn && data.editUrl) {
            viewModalEditBtn.setAttribute('href', data.editUrl);
        }

        if (viewModalDeleteBtn && data.id) {
            viewModalDeleteBtn.dataset.noteId = data.id;
            viewModalDeleteBtn.dataset.noteTitle = data.title;
        }

        viewModalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeViewModal() {
        if (!viewModalOverlay) return;
        viewModalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Attach click listeners to all note "View" buttons
    document.querySelectorAll('.open-view-modal').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const data = {
                id: this.dataset.id,
                title: this.dataset.title,
                category: this.dataset.category,
                content: this.dataset.content,
                created: this.dataset.created,
                updated: this.dataset.updated,
                words: this.dataset.words,
                chars: this.dataset.chars,
                reading: this.dataset.reading,
                editUrl: this.dataset.editUrl
            };
            openViewModal(data);
        });
    });

    if (viewModalCloseBtn) {
        viewModalCloseBtn.addEventListener('click', closeViewModal);
    }
    if (viewModalCloseFooterBtn) {
        viewModalCloseFooterBtn.addEventListener('click', closeViewModal);
    }
    if (viewModalOverlay) {
        viewModalOverlay.addEventListener('click', function (e) {
            if (e.target === viewModalOverlay) {
                closeViewModal();
            }
        });
    }

    // -------------------------------------------------------------
    // 4. Delete Confirmation Modal
    // -------------------------------------------------------------
    const deleteModalOverlay = document.getElementById('delete-modal-overlay');
    const deleteModalCancelBtn = document.getElementById('delete-modal-cancel-btn');
    const deleteModalCloseBtn = document.getElementById('delete-modal-close-btn');
    const deleteNoteTitleDisplay = document.getElementById('delete-note-title-display');
    const deleteConfirmForm = document.getElementById('delete-confirm-form');

    function openDeleteModal(noteId, noteTitle) {
        if (!deleteModalOverlay) return;
        if (deleteNoteTitleDisplay) {
            deleteNoteTitleDisplay.textContent = `"${noteTitle || 'this note'}"`;
        }
        if (deleteConfirmForm) {
            deleteConfirmForm.setAttribute('action', `/delete/${noteId}/`);
        }
        deleteModalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeDeleteModal() {
        if (!deleteModalOverlay) return;
        deleteModalOverlay.classList.remove('active');
        if (!viewModalOverlay || !viewModalOverlay.classList.contains('active')) {
            document.body.style.overflow = '';
        }
    }

    // Attach click listener to card delete buttons
    document.querySelectorAll('.open-delete-modal').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const id = this.dataset.noteId;
            const title = this.dataset.noteTitle;
            openDeleteModal(id, title);
        });
    });

    // Also support delete triggered from inside the View modal
    if (viewModalDeleteBtn) {
        viewModalDeleteBtn.addEventListener('click', function () {
            const id = this.dataset.noteId;
            const title = this.dataset.noteTitle;
            closeViewModal();
            openDeleteModal(id, title);
        });
    }

    if (deleteModalCancelBtn) {
        deleteModalCancelBtn.addEventListener('click', closeDeleteModal);
    }
    if (deleteModalCloseBtn) {
        deleteModalCloseBtn.addEventListener('click', closeDeleteModal);
    }
    if (deleteModalOverlay) {
        deleteModalOverlay.addEventListener('click', function (e) {
            if (e.target === deleteModalOverlay) {
                closeDeleteModal();
            }
        });
    }

    // -------------------------------------------------------------
    // 5. Global Keyboard Shortcuts (Escape to close modals)
    // -------------------------------------------------------------
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeViewModal();
            closeDeleteModal();
            closeSidebar();
        }
    });

    // -------------------------------------------------------------
    // 6. Real-time Live Word & Character Counter
    // -------------------------------------------------------------
    const contentTextarea = document.getElementById('note-content-input');
    const wordCounterEl = document.getElementById('word-count-badge');
    const charCounterEl = document.getElementById('char-count-badge');

    function updateCounters() {
        if (!contentTextarea) return;
        const text = contentTextarea.value || '';
        const chars = text.length;
        const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).filter(Boolean).length;

        if (wordCounterEl) wordCounterEl.textContent = `${words} words`;
        if (charCounterEl) charCounterEl.textContent = `${chars} characters`;
    }

    if (contentTextarea) {
        contentTextarea.addEventListener('input', updateCounters);
        // Initial run
        updateCounters();
    }

    // -------------------------------------------------------------
    // 7. Dynamic Favorite Star Toggle (AJAX)
    // -------------------------------------------------------------
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    document.querySelectorAll('.fav-toggle-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const noteId = this.dataset.noteId;
            const starIcon = this.querySelector('.star-icon') || this;

            fetch(`/toggle-favorite/${noteId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.is_favorite) {
                        this.classList.add('active');
                        this.setAttribute('title', 'Remove from Favorites');
                        starIcon.textContent = '★';
                        showToast(`"${data.title}" added to favorites!`, 'success');
                    } else {
                        this.classList.remove('active');
                        this.setAttribute('title', 'Add to Favorites');
                        starIcon.textContent = '☆';
                        showToast(`"${data.title}" removed from favorites.`, 'info');
                    }
                }
            })
            .catch(err => {
                console.error('Favorite toggle error:', err);
                // Fallback to normal navigation if AJAX fails
                window.location.href = `/toggle-favorite/${noteId}/`;
            });
        });
    });

    // -------------------------------------------------------------
    // 8. Toast Notifications Auto-Dismiss & Dynamic Creator
    // -------------------------------------------------------------
    function showToast(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const iconMap = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };

        toast.innerHTML = `
            <div class="toast-content">
                <span>${iconMap[type] || 'ℹ'}</span>
                <span>${message}</span>
            </div>
            <button class="toast-close-btn" aria-label="Close">&times;</button>
        `;

        container.appendChild(toast);

        // Auto dismiss after 3.5s
        const timer = setTimeout(() => {
            dismissToast(toast);
        }, 3500);

        toast.querySelector('.toast-close-btn').addEventListener('click', () => {
            clearTimeout(timer);
            dismissToast(toast);
        });
    }

    function dismissToast(toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    // Auto-dismiss Django server-rendered toasts
    document.querySelectorAll('.toast').forEach(toast => {
        setTimeout(() => {
            dismissToast(toast);
        }, 4000);

        const closeBtn = toast.querySelector('.toast-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => dismissToast(toast));
        }
    });

    // -------------------------------------------------------------
    // 9. Search Bar Clear Action
    // -------------------------------------------------------------
    const searchInput = document.getElementById('search-input');
    const searchClearBtn = document.getElementById('search-clear-btn');

    if (searchInput && searchClearBtn) {
        searchInput.addEventListener('input', function () {
            searchClearBtn.style.display = this.value.length > 0 ? 'flex' : 'none';
        });

        searchClearBtn.addEventListener('click', function () {
            searchInput.value = '';
            searchClearBtn.style.display = 'none';
            // Submit form to clear search results
            searchInput.form.submit();
        });
    }
});
