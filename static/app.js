// Global state management
window.VideoRetriever = {
    state: {
        isSearching: false,
        currentSession: null,
        searchHistory: [],
        lastSearchTime: null
    },
    
    // Enhanced animations
    animations: {
        // Animate result cards appearing
        animateResults: function(container) {
            const cards = container.querySelectorAll('.result-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        },
        
        // Animate progress bar updates
        animateProgress: function(element, targetWidth) {
            element.style.transition = 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            element.style.width = targetWidth + '%';
        },
        
        // Pulse animation for important elements
        pulseElement: function(element) {
            element.classList.add('animate-pulse');
            setTimeout(() => {
                element.classList.remove('animate-pulse');
            }, 2000);
        }
    },
    
    // Utility functions
    utils: {
        // Format time duration
        formatDuration: function(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = Math.floor(seconds % 60);
            
            if (hours > 0) {
                return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            } else {
                return `${minutes}:${secs.toString().padStart(2, '0')}`;
            }
        },
        
        // Validate YouTube URL
        isValidYouTubeUrl: function(url) {
            const regex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/;
            return regex.test(url) || /^[a-zA-Z0-9_-]{11}$/.test(url);
        },
        
        // Extract video ID from URL
        extractVideoId: function(url) {
            const match = url.match(/(?:v=|youtu\.be\/|embed\/)([a-zA-Z0-9_-]{11})/);
            return match ? match[1] : url;
        },
        
        // Debounce function for search input
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Copy text to clipboard
        copyToClipboard: function(text) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Copied to clipboard!', 'success');
            });
        },
        
        // Show toast notification
        showToast: function(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
            
            const colors = {
                success: 'bg-green-500 text-white',
                error: 'bg-red-500 text-white',
                warning: 'bg-yellow-500 text-black',
                info: 'bg-blue-500 text-white'
            };
            
            toast.className += ` ${colors[type] || colors.info}`;
            toast.textContent = message;
            
            document.body.appendChild(toast);
            
            // Animate in
            setTimeout(() => {
                toast.style.transform = 'translateX(0)';
            }, 100);
            
            // Animate out
            setTimeout(() => {
                toast.style.transform = 'translateX(full)';
                setTimeout(() => {
                    document.body.removeChild(toast);
                }, 300);
            }, 3000);
        }
    },
    
    // Keyboard shortcuts
    shortcuts: {
        init: function() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + Enter to search
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    if (typeof startSearch === 'function') {
                        startSearch();
                    }
                }
                
                // Escape to clear results
                if (e.key === 'Escape') {
                    if (typeof clearResults === 'function') {
                        clearResults();
                    }
                }
                
                // Ctrl/Cmd + K to focus search
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    const searchInput = document.getElementById('search-query');
                    if (searchInput) {
                        searchInput.focus();
                        searchInput.select();
                    }
                }
            });
        }
    },
    
    // Performance monitoring
    performance: {
        startTime: null,
        
        startTimer: function() {
            this.startTime = performance.now();
        },
        
        endTimer: function(label = 'Operation') {
            if (this.startTime) {
                const endTime = performance.now();
                const duration = endTime - this.startTime;
                console.log(`${label} took ${duration.toFixed(2)} milliseconds`);
                this.startTime = null;
                return duration;
            }
        }
    },
    
    // Initialize all enhancements
    init: function() {
        console.log('🚀 Video Retriever Enhanced Frontend Loaded');
        this.shortcuts.init();
        
        // Add smooth scrolling to all anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Add loading state to forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.classList.add('loading-shimmer');
                }
            });
        });
        
        // Enhanced input validation
        this.setupInputValidation();
        
        // Initialize tooltips
        this.initializeTooltips();
    },
    
    setupInputValidation: function() {
        // Real-time YouTube URL validation
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('video-url-input')) {
                const input = e.target.querySelector('input');
                if (input) {
                    const isValid = this.utils.isValidYouTubeUrl(input.value.trim());
                    
                    if (input.value.trim() === '') {
                        input.classList.remove('border-red-500', 'border-green-500');
                    } else if (isValid) {
                        input.classList.remove('border-red-500');
                        input.classList.add('border-green-500');
                    } else {
                        input.classList.remove('border-green-500');
                        input.classList.add('border-red-500');
                    }
                }
            }
        });
    },
    
    initializeTooltips: function() {
        // Add tooltips to relevant elements
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip-popup';
                tooltip.textContent = this.getAttribute('data-tooltip');
                document.body.appendChild(tooltip);
                
                // Position tooltip
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + 'px';
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            });
            
            element.addEventListener('mouseleave', function() {
                const tooltip = document.querySelector('.tooltip-popup');
                if (tooltip) {
                    tooltip.remove();
                }
            });
        });
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    VideoRetriever.init();
});

// Export for global access
window.VR = VideoRetriever;
