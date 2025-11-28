/**
 * Home Page UI Functionality
 * Handles stories, posts, and interactions
 */

// Mock data for stories
const mockStories = [
    { id: 1, username: 'user1', avatar: 'https://randomuser.me/api/portraits/women/1.jpg' },
    { id: 2, username: 'user2', avatar: 'https://randomuser.me/api/portraits/women/2.jpg' },
    { id: 3, username: 'user3', avatar: 'https://randomuser.me/api/portraits/women/3.jpg' },
    { id: 4, username: 'user4', avatar: 'https://randomuser.me/api/portraits/women/4.jpg' },
    { id: 5, username: 'user5', avatar: 'https://randomuser.me/api/portraits/women/5.jpg' },
];

// Mock data for posts
const mockPosts = [
    {
        id: 1,
        username: 'jane_doe',
        avatar: 'https://randomuser.me/api/portraits/women/10.jpg',
        image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
        caption: 'Beautiful day at the beach! 🏖️ #summer #vacation',
        likes: 42,
        timestamp: '2 HOURS AGO',
        comments: [
            { username: 'user1', text: 'Looks amazing! 😍' },
            { username: 'user2', text: 'Wish I was there!' }
        ],
        isLiked: false,
        isSaved: false
    },
    {
        id: 2,
        username: 'sarah_smith',
        avatar: 'https://randomuser.me/api/portraits/women/15.jpg',
        image: 'https://images.unsplash.com/photo-1517486808906-6ca8b3b0d486?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80',
        caption: 'Morning coffee and a good book. Perfect start to the day! ☕📚',
        likes: 28,
        timestamp: '5 HOURS AGO',
        comments: [
            { username: 'user3', text: 'What are you reading?' }
        ],
        isLiked: true,
        isSaved: false
    }
];

// Initialize the UI when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load stories
    loadStories();
    
    // Load posts
    loadPosts();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize story viewer modal
    initStoryViewer();
    
    // Initialize modals
    initModals();
});

/**
 * Load and display stories
 */
function loadStories() {
    const storiesContainer = document.getElementById('storiesContainer');
    if (!storiesContainer) return;
    
    // Clear existing content
    storiesContainer.innerHTML = '';
    
    // Add "Add Story" button
    const addStoryItem = document.createElement('div');
    addStoryItem.className = 'story-item add-story';
    addStoryItem.innerHTML = `
        <div class="story-avatar">
            <i class="fas fa-plus"></i>
        </div>
        <div class="story-username">Your Story</div>
    `;
    addStoryItem.addEventListener('click', () => {
        const modal = new bootstrap.Modal(document.getElementById('addStoryModal'));
        modal.show();
    });
    storiesContainer.appendChild(addStoryItem);
    
    // Add mock stories
    mockStories.forEach(story => {
        const storyElement = document.createElement('div');
        storyElement.className = 'story-item';
        storyElement.innerHTML = `
            <div class="story-avatar">
                <img src="${story.avatar}" alt="${story.username}">
            </div>
            <div class="story-username">${story.username}</div>
        `;
        storyElement.addEventListener('click', () => {
            openStoryViewer(story);
        });
        storiesContainer.appendChild(storyElement);
    });
}

/**
 * Load and display posts
 */
function loadPosts() {
    const postsContainer = document.getElementById('postsContainer');
    if (!postsContainer) return;
    
    // Clear existing content
    postsContainer.innerHTML = '';
    
    // Add mock posts
    mockPosts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.className = 'post-card';
        postElement.dataset.postId = post.id;
        
        // Build post HTML
        postElement.innerHTML = `
            <div class="post-header">
                <img src="${post.avatar}" alt="${post.username}" class="post-avatar">
                <div class="post-user-info">
                    <h4 class="post-username">${post.username}</h4>
                    <span class="post-time">${post.timestamp}</span>
                </div>
                <div class="post-more">
                    <i class="fas fa-ellipsis-h"></i>
                </div>
            </div>
            <img src="${post.image}" alt="Post by ${post.username}" class="post-image">
            <div class="post-actions">
                <div class="post-action like-btn ${post.isLiked ? 'liked' : ''}">
                    <i class="${post.isLiked ? 'fas' : 'far'} fa-heart"></i>
                </div>
                <div class="post-action comment-btn">
                    <i class="far fa-comment"></i>
                </div>
                <div class="post-action share-btn">
                    <i class="far fa-paper-plane"></i>
                </div>
                <div class="post-action save-btn">
                    <i class="${post.isSaved ? 'fas' : 'far'} fa-bookmark"></i>
                </div>
            </div>
            <div class="post-likes">
                <span class="like-count">${post.likes.toLocaleString()}</span> likes
            </div>
            <p class="post-caption"><strong>${post.username}</strong> ${post.caption}</p>
            <div class="post-comments">
                ${post.comments.map(comment => `
                    <div class="post-comment">
                        <strong>${comment.username}</strong> ${comment.text}
                    </div>
                `).join('')}
            </div>
            <span class="post-timestamp">${post.timestamp}</span>
            <div class="post-add-comment">
                <input type="text" class="post-comment-input" placeholder="Add a comment...">
                <button class="post-comment-btn" disabled>Post</button>
            </div>
        `;
        
        // Add event listeners
        const likeBtn = postElement.querySelector('.like-btn');
        const likeIcon = likeBtn.querySelector('i');
        const likeCount = postElement.querySelector('.like-count');
        
        likeBtn.addEventListener('click', function() {
            post.isLiked = !post.isLiked;
            likeIcon.className = post.isLiked ? 'fas fa-heart' : 'far fa-heart';
            likeBtn.classList.toggle('liked', post.isLiked);
            likeCount.textContent = post.isLiked 
                ? (post.likes + 1).toLocaleString() 
                : post.likes.toLocaleString();
        });
        
        const saveBtn = postElement.querySelector('.save-btn');
        const saveIcon = saveBtn.querySelector('i');
        
        saveBtn.addEventListener('click', function() {
            post.isSaved = !post.isSaved;
            saveIcon.className = post.isSaved ? 'fas fa-bookmark' : 'far fa-bookmark';
        });
        
        const commentInput = postElement.querySelector('.post-comment-input');
        const commentBtn = postElement.querySelector('.post-comment-btn');
        const commentsContainer = postElement.querySelector('.post-comments');
        
        commentInput.addEventListener('input', function() {
            const hasText = commentInput.value.trim() !== '';
            commentBtn.disabled = !hasText;
            commentBtn.classList.toggle('active', hasText);
        });
        
        commentBtn.addEventListener('click', function() {
            const commentText = commentInput.value.trim();
            if (!commentText) return;
            
            // In a real app, this would be an API call
            const newComment = document.createElement('div');
            newComment.className = 'post-comment';
            newComment.innerHTML = `
                <strong>current_user</strong> ${commentText}
            `;
            
            commentsContainer.appendChild(newComment);
            commentInput.value = '';
            commentBtn.disabled = true;
            commentBtn.classList.remove('active');
            
            // Scroll to show the new comment
            newComment.scrollIntoView({ behavior: 'smooth' });
        });
        
        // Allow pressing Enter to post a comment
        commentInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !commentBtn.disabled) {
                commentBtn.click();
            }
        });
        
        postsContainer.appendChild(postElement);
    });
}

/**
 * Initialize tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize modals
 */
function initModals() {
    // Handle story media upload
    const storyMediaInput = document.getElementById('storyMediaInput');
    const addStoryBtn = document.querySelector('.add-story-btn');
    
    if (addStoryBtn) {
        addStoryBtn.addEventListener('click', function() {
            storyMediaInput.click();
        });
    }
    
    if (storyMediaInput) {
        storyMediaInput.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                // In a real app, you would upload the file here
                alert('Story created successfully!');
                const modal = bootstrap.Modal.getInstance(document.getElementById('addStoryModal'));
                if (modal) modal.hide();
            }
        });
    }
}

/**
 * Initialize story viewer
 */
function initStoryViewer() {
    // This would be implemented to show full-screen stories
    // Similar to Instagram's story viewer
}

/**
 * Open story viewer for a specific story
 * @param {Object} story - The story to view
 */
function openStoryViewer(story) {
    // In a real app, this would open a full-screen story viewer
    console.log('Viewing story:', story.username);
    // For now, just show an alert
    alert(`Viewing ${story.username}'s story`);
}

// Make functions available globally
window.initHomeUI = function() {
    loadStories();
    loadPosts();
    initTooltips();
    initStoryViewer();
    initModals();
};
