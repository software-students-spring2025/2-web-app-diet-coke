/* main.js - Handles frontend interactions for Travel Match */

document.addEventListener("DOMContentLoaded", () => {
    setupLoginForm();
    setupRegisterForm();
    setupPreferencesForm();
    setupLogoutButton();
    fetchMatches();
    setupProfileButtons();
    fetchNotifications();
});

// Handle login form submission
function setupLoginForm() {
    const loginForm = document.querySelector("form[action='/login']");
    if (loginForm) {
        loginForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            
            // Create JSON payload from form data
            const formData = new FormData(loginForm);
            const payload = {
                email: formData.get("email"),
                password: formData.get("password")
            };
            
            try {
                const response = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                
                if (response.ok && result.status === "success") {
                    window.location.href = "/profile";
                } else {
                    alert(result.message || "Login failed. Please try again.");
                }
            } catch (error) {
                console.error("Login error:", error);
                alert("An error occurred during login. Please try again.");
            }
        });
    }
}

// Handle registration form submission
function setupRegisterForm() {
    const registerForm = document.querySelector("form[action='/register']");
    if (registerForm) {
        registerForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            // Send data as FormData, not JSON
            const formData = new FormData(registerForm);
            
            try {
                const response = await fetch("/api/auth/register", {
                    method: "POST",
                    body: formData  
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    alert("Registration successful! Redirecting to login page.");
                    window.location.href = "/login"; 
                } else {
                    alert(result.message || "Registration failed. Please try again.");
                }
            } catch (error) {
                console.error("Registration error:", error);
                alert("An error occurred during registration. Please try again.");
            }
        });
    }
}

// Handle preferences form submission
function setupPreferencesForm() {
    const preferencesForm = document.querySelector("form[action='/preferences']");
    if (preferencesForm) {
        preferencesForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            
            // Create JSON payload from form data
            const formData = new FormData(preferencesForm);
            const payload = {
                destination: formData.get("destination"),
                budget: formData.get("budget"),
                travel_style: formData.get("travel_style") || "",
                food_preferences: formData.get("food_preferences") ? 
                    formData.get("food_preferences").split(",").map(item => item.trim()) : [],
                accommodation_type: formData.get("accommodation_type") || "",
                arrival_time: formData.get("arrival_time") || ""
            };
            
            try {
                const response = await fetch("/api/preferences", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                
                if (response.ok && result.status === "success") {
                    alert("Preferences updated successfully!");
                    // Refresh the page to show updated preferences
                    window.location.reload();
                } else {
                    alert(result.message || "Failed to update preferences.");
                }
            } catch (error) {
                console.error("Preferences update error:", error);
                alert("An error occurred while updating preferences. Please try again.");
            }
        });
    }
}

// Handle logout functionality
function setupLogoutButton() {
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
            try {
                const response = await fetch("/api/auth/logout", { method: "GET" });
                if (response.ok) {
                    window.location.href = "/login";
                } else {
                    alert("Logout failed. Please try again.");
                }
            } catch (error) {
                console.error("Logout error:", error);
                alert("An error occurred during logout. Please try again.");
            }
        });
    }
}

// Fetch and display matches dynamically
async function fetchMatches() {
    const matchesContainer = document.getElementById("matches-container");
    if (matchesContainer) {
        try {
            const response = await fetch("/api/matches");
            if (!response.ok) {
                throw new Error("Failed to fetch matches");
            }
            
            const result = await response.json();
            
            if (result.status === "success" && result.data) {
                matchesContainer.innerHTML = "";
                
                if (result.data.length === 0) {
                    matchesContainer.innerHTML = "<p>No matches found. Update your preferences to find travel partners!</p>";
                    return;
                }
                
                result.data.forEach(match => {
                    matchesContainer.innerHTML += `
                        <div class="card mt-3">
                            <div class="card-body">
                                <h5 class="card-title">${match.user.name}</h5>
                                <p class="card-text">
                                    <strong>Budget:</strong> ${match.preferences.budget}<br>
                                    <strong>Travel Style:</strong> ${match.preferences.travel_style}<br>
                                    <strong>Destination:</strong> ${match.preferences.destination}
                                </p>
                                <button class="btn btn-primary view-profile" data-user-id="${match.user.id}">View Profile</button>
                                <button class="btn btn-success bookmark-user" data-user-id="${match.user.id}">Bookmark</button>
                                <button class="btn btn-info message-user" data-user-id="${match.user.id}">Message</button>
                            </div>
                        </div>`;
                });
                
                // Set up event listeners after adding all matches to the DOM
                setupProfileButtons();
            } else {
                matchesContainer.innerHTML = "<p>Error loading matches. Please try again later.</p>";
            }
        } catch (error) {
            console.error("Error fetching matches:", error);
            matchesContainer.innerHTML = "<p>Error loading matches. Please try again later.</p>";
        }
    }
}

// Handle profile action buttons (view, bookmark, message)
function setupProfileButtons() {
    // Handle view profile buttons
    document.querySelectorAll('.view-profile').forEach(button => {
        button.addEventListener('click', () => {
            const userId = button.getAttribute('data-user-id');
            window.location.href = `/profile/${userId}`;
        });
    });
    
    // Handle bookmark buttons
    document.querySelectorAll('.bookmark-user').forEach(button => {
        button.addEventListener('click', async () => {
            const userId = button.getAttribute('data-user-id');
            try {
                const response = await fetch(`/api/bookmarks/${userId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (response.ok && result.status === "success") {
                    alert("User bookmarked successfully!");
                } else {
                    alert(result.message || "Failed to bookmark user.");
                }
            } catch (error) {
                console.error("Bookmark error:", error);
                alert("An error occurred while bookmarking. Please try again.");
            }
        });
    });
    
    // Handle message buttons
    document.querySelectorAll('.message-user').forEach(button => {
        button.addEventListener('click', () => {
            const userId = button.getAttribute('data-user-id');
            window.location.href = `/messages/${userId}`;
        });
    });
}

// Fetch and display notifications
async function fetchNotifications() {
    const notificationsContainer = document.getElementById("notifications-container");
    if (notificationsContainer) {
        try {
            const response = await fetch("/api/notifications");
            if (!response.ok) {
                throw new Error("Failed to fetch notifications");
            }
            
            const result = await response.json();
            
            if (result.status === "success" && result.data) {
                notificationsContainer.innerHTML = "";
                
                if (result.data.length === 0) {
                    notificationsContainer.innerHTML = "<p>No notifications</p>";
                    return;
                }
                
                result.data.forEach(notification => {
                    // Create notification element with appropriate styling based on read status
                    const notifClass = notification.read ? "notification" : "notification unread";
                    
                    // Check if notification has related user_id (for messages)
                    const isMessageNotification = notification.related_user_id && notification.type === 'message';
                    const notificationContent = isMessageNotification ? 
                        `<div class="notification-content clickable" data-user-id="${notification.related_user_id}">
                            <p>${notification.content}</p>
                            <small>${new Date(notification.created_at).toLocaleString()}</small>
                        </div>` :
                        `<div class="notification-content">
                            <p>${notification.content}</p>
                            <small>${new Date(notification.created_at).toLocaleString()}</small>
                        </div>`;
                    
                    notificationsContainer.innerHTML += `
                        <div class="${notifClass}" data-notification-id="${notification.id}">
                            ${notificationContent}
                            ${!notification.read ? '<button class="mark-read-btn">Mark as Read</button>' : ''}
                        </div>`;
                });
                
                // Add event listeners for "Mark as Read" buttons
                document.querySelectorAll('.mark-read-btn').forEach(button => {
                    button.addEventListener('click', async (event) => {
                        const notificationElement = event.target.closest('.notification');
                        const notificationId = notificationElement.getAttribute('data-notification-id');
                        
                        try {
                            const response = await fetch(`/api/notifications/${notificationId}`, {
                                method: 'PUT',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({ read: true })
                            });
                            
                            if (response.ok) {
                                // Update UI to reflect read status
                                notificationElement.classList.remove('unread');
                                event.target.remove();
                            }
                        } catch (error) {
                            console.error("Error marking notification as read:", error);
                        }
                    });
                });
                
                // Add event listeners for clickable notifications (messages)
                document.querySelectorAll('.notification-content.clickable').forEach(content => {
                    content.addEventListener('click', () => {
                        const userId = content.getAttribute('data-user-id');
                        if (userId) {
                            window.location.href = `/messages/${userId}`;
                        }
                    });
                });
            } else {
                notificationsContainer.innerHTML = "<p>Error loading notifications</p>";
            }
        } catch (error) {
            console.error("Error fetching notifications:", error);
            notificationsContainer.innerHTML = "<p>Error loading notifications</p>";
        }
    }
}
