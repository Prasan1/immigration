/**
 * Global Logout Handler
 * Properly logs out from both Clerk and Flask session
 */

async function performLogout() {
    try {
        // First, logout from Flask session
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        // Then sign out from Clerk if it's loaded
        if (typeof Clerk !== 'undefined' && Clerk.signOut) {
            await Clerk.signOut();
        }

        // Redirect to home page
        window.location.href = '/';
    } catch (error) {
        console.error('Logout error:', error);
        // Even if there's an error, try to redirect
        window.location.href = '/';
    }
}
