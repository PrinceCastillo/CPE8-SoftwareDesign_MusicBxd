const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');
const btnPopup = document.querySelector('.btnLogin-popup');
const iconClose = document.querySelector('.icon-close');


registerLink.addEventListener('click', () => {
    wrapper.classList.add('active');
});


loginLink.addEventListener('click', () => {
    wrapper.classList.remove('active');
});

btnPopup.addEventListener('click', () => {
    wrapper.classList.add('active-popup');
});


iconClose.addEventListener('click', () => {
     wrapper.classList.remove('active-popup');
});
async function getUserProfile() {
    const token = localStorage.getItem("spotifyAccessToken");
    if (!token) {
        console.log("No access token found. Please log in.");
        return;
    }

    const response = await fetch("https://api.spotify.com/v1/me", {
        headers: { Authorization: `Bearer ${token}` }
    });

    const data = await response.json();
    console.log("User Profile:", data);
}

document.querySelector('.btnFetchProfile').addEventListener('click', getUserProfile);
