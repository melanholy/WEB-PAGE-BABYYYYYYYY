import React from "react";

function music() {
    var player = document.getElementById("player");
    if (player.paused) {
        player.play();
        return;
    }
    player.pause();
}

export default class Aside extends React.Component {
    render() {
        return <aside>
            <a href="/leave_feedback">
                <div className="top-stick feedback-link">Оставить отзыв</div>
            </a>
            <div className="top-stick music-button" onClick={e => music()}>
                <audio id="player">
                    <source src="/static/music.mp3" type="audio/mpeg" />
                </audio>
                <img src="/static/music.jpg" alt="Музыка" />
            </div>
        </aside>;
    }
}