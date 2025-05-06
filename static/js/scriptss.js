async function getRecommendation() {
    try {
        const res = await fetch('/recommend-random');
        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('song-title').innerText = `🎵 Title: ${data.title}`;
        document.getElementById('song-artist').innerText = `👤 Artist: ${data.artist}`;
        document.getElementById('audio-player').style.display = 'none';
        document.getElementById('song-display').style.display = 'block';

    } catch (err) {
        alert('Error fetching recommendation.');
    }
}
