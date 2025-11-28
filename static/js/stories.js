// Stories Component - Frontend Only
class StoryManager {
    constructor() {
        this.stories = this.loadStories();
        this.currentUser = 'current_user'; // In a real app, this would come from authentication
        this.initializeEventListeners();
        this.renderStories();
    }

    loadStories() {
        const savedStories = localStorage.getItem('sisterhood_stories');
        return savedStories ? JSON.parse(savedStories) : [];
    }

    saveStories() {
        localStorage.setItem('sisterhood_stories', JSON.stringify(this.stories));
    }

    initializeEventListeners() {
        // Add Story Button
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-story-btn')) {
                this.openAddStoryModal();
            } else if (e.target.closest('.story-close-btn')) {
                this.closeViewer();
            } else if (e.target.closest('.story-prev-btn')) {
                this.navigateStory('prev');
            } else if (e.target.closest('.story-next-btn')) {
                this.navigateStory('next');
            }
        });

        // Handle file input changes
        document.addEventListener('change', (e) => {
            if (e.target.matches('#story-media-upload')) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    }

    renderStories() {
        const storiesContainer = document.querySelector('.stories-container');
        if (!storiesContainer) return;

        // Filter out expired stories (24 hours)
        const now = new Date().getTime();
        const validStories = this.stories.filter(story => {
            return (now - new Date(story.createdAt).getTime()) < 24 * 60 * 60 * 1000;
        });

        // Group stories by user
        const storiesByUser = {};
        validStories.forEach(story => {
            if (!storiesByUser[story.userId]) {
                storiesByUser[story.userId] = [];
            }
            storiesByUser[story.userId].push(story);
        });

        // Render stories
        let html = `
            <div class="story-item add-story">
                <button class="add-story-btn">
                    <div class="story-avatar">
                        <span>+</span>
                    </div>
                    <div class="story-username">Add Story</div>
                </button>
            </div>
        `;

        // Add user stories
        Object.entries(storiesByUser).forEach(([userId, stories]) => {
            const latestStory = stories[0];
            const hasUnseen = stories.some(s => !s.seen);
            
            html += `
                <div class="story-item" data-user-id="${userId}">
                    <div class="story-avatar ${hasUnseen ? 'unseen' : ''}">
                        <img src="${latestStory.userAvatar || '/static/images/default-avatar.png'}" alt="${latestStory.username}">
                    </div>
                    <div class="story-username">${latestStory.username}</div>
                </div>
            `;
        });

        storiesContainer.innerHTML = html;
    }

    openAddStoryModal() {
        const modal = `
            <div class="story-modal" id="addStoryModal">
                <div class="story-modal-content">
                    <div class="story-modal-header">
                        <h3>Create New Story</h3>
                        <button class="close-btn">&times;</button>
                    </div>
                    <div class="story-modal-body">
                        <div class="story-options">
                            <label class="story-option">
                                <input type="radio" name="story-type" value="photo" checked>
                                <div class="option-icon">📷</div>
                                <span>Photo</span>
                            </label>
                            <label class="story-option">
                                <input type="radio" name="story-type" value="video">
                                <div class="option-icon">🎥</div>
                                <span>Video</span>
                            </label>
                            <label class="story-option">
                                <input type="radio" name="story-type" value="text">
                                <div class="option-icon">✏️</div>
                                <span>Text</span>
                            </label>
                        </div>
                        
                        <div class="story-upload-area" id="storyUploadArea">
                            <input type="file" id="story-media-upload" accept="image/*,video/*" style="display: none;">
                            <div class="upload-prompt">
                                <div class="upload-icon">+</div>
                                <p>Click to upload or drag and drop</p>
                                <p class="small">Supports JPG, PNG, MP4, or create a text story</p>
                            </div>
                            <div class="preview-container" id="storyPreview" style="display: none;"></div>
                        </div>
                        
                        <div class="story-caption">
                            <textarea placeholder="Add a caption..."></textarea>
                        </div>
                    </div>
                    <div class="story-modal-footer">
                        <button class="btn btn-outline" id="cancelStory">Cancel</button>
                        <button class="btn btn-primary" id="postStory" disabled>Post Story</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modal);
        this.initializeModalEvents();
    }

    initializeModalEvents() {
        const modal = document.getElementById('addStoryModal');
        if (!modal) return;

        // Close modal
        modal.querySelector('.close-btn').addEventListener('click', () => {
            modal.remove();
        });

        // Handle file upload area click
        const uploadArea = document.getElementById('storyUploadArea');
        uploadArea.addEventListener('click', () => {
            document.getElementById('story-media-upload').click();
        });

        // Handle file upload
        const fileInput = document.getElementById('story-media-upload');
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Enable/disable post button based on content
        const captionInput = modal.querySelector('textarea');
        const postButton = document.getElementById('postStory');
        
        const updatePostButton = () => {
            const hasMedia = document.querySelector('.preview-container img, .preview-container video');
            const hasText = captionInput.value.trim() !== '';
            postButton.disabled = !(hasMedia || hasText);
        };

        captionInput.addEventListener('input', updatePostButton);

        // Handle post button click
        postButton.addEventListener('click', () => {
            this.saveStory();
            modal.remove();
            this.renderStories();
        });

        // Cancel button
        document.getElementById('cancelStory').addEventListener('click', () => {
            modal.remove();
        });
    }

    handleFileUpload(file) {
        if (!file) return;

        const reader = new FileReader();
        const preview = document.getElementById('storyPreview');
        
        reader.onload = (e) => {
            const isVideo = file.type.startsWith('video/');
            const isImage = file.type.startsWith('image/');
            
            if (isImage) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Story preview">`;
            } else if (isVideo) {
                preview.innerHTML = `
                    <video controls>
                        <source src="${e.target.result}" type="${file.type}">
                        Your browser does not support the video tag.
                    </video>
                `;
            }
            
            preview.style.display = 'block';
            document.querySelector('.upload-prompt').style.display = 'none';
            document.getElementById('postStory').disabled = false;
        };

        reader.readAsDataURL(file);
    }

    saveStory() {
        const preview = document.getElementById('storyPreview');
        const caption = document.querySelector('.story-caption textarea').value;
        const mediaElement = preview.querySelector('img, video');
        
        if (!mediaElement) return;

        const newStory = {
            id: Date.now().toString(),
            userId: this.currentUser,
            username: 'You', // In a real app, this would come from user data
            userAvatar: '/static/images/default-avatar.png',
            type: mediaElement.tagName.toLowerCase(),
            dataUrl: mediaElement.tagName === 'IMG' ? mediaElement.src : mediaElement.querySelector('source').src,
            caption: caption,
            createdAt: new Date().toISOString(),
            seen: false
        };

        this.stories.unshift(newStory);
        this.saveStories();
    }

    openViewer(storyId) {
        // Implementation for viewing stories
    }

    closeViewer() {
        const viewer = document.querySelector('.story-viewer');
        if (viewer) viewer.remove();
    }

    navigateStory(direction) {
        // Implementation for navigating between stories
    }
}

// Initialize the Story Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.storyManager = new StoryManager();
});
