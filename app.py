import asyncio, aiohttp, re, time
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'hyper_v_ultra_2026'

# --- INTERFACE VISUAL PREMIUM ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>HYPER-V | Premium Interface</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        :root { 
            --primary: #007aff; 
            --bg: #050505; 
            --card-bg: #111111; 
            --text: #ffffff; 
            --text-dim: #888888;
            --glass: rgba(255, 255, 255, 0.03);
            --border: rgba(255, 255, 255, 0.08);
        }
        
        body { background: var(--bg); color: var(--text); font-family: 'Plus Jakarta Sans', sans-serif; margin: 0; overflow-x: hidden; }

        /* --- Custom Scrollbar --- */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: #222; border-radius: 0; }
        ::-webkit-scrollbar-thumb:hover { background: #333; }

        /* --- Nav --- */
        .nav { background: rgba(5,5,5,0.8); backdrop-filter: blur(20px); padding: 18px 5%; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; border-bottom: 1px solid var(--border); }
        .logo { font-weight: 800; font-size: 24px; color: var(--primary); text-decoration: none; letter-spacing: -1px; margin-right: 40px; }
        .nav-links { display: flex; gap: 30px; flex: 1; }
        .nav-link { text-decoration: none; color: var(--text-dim); font-weight: 600; font-size: 14px; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; }
        .nav-link:hover, .nav-link.active { color: #fff; }
        .nav-link.active { color: var(--primary); }

        .search-container { position: relative; }
        .search-input { background: var(--glass); border: 1px solid var(--border); color: #fff; padding: 12px 20px 12px 45px; border-radius: 0; width: 280px; outline: none; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        .search-input:focus { width: 380px; border-color: var(--primary); background: rgba(255,255,255,0.08); }
        .search-icon { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: var(--text-dim); }

        /* --- Grid de Filmes --- */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 30px; padding: 40px 5%; }
        
        .card { 
            position: relative; background: var(--card-bg); border-radius: 0; overflow: hidden; 
            transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1); cursor: pointer; border: 1px solid var(--border);
        }
        
        /* Efeito de Hover no Card */
        .card:hover { 
            transform: translateY(-10px) scale(1.02); 
            border-color: var(--primary); 
            box-shadow: 0 20px 40px rgba(0, 122, 255, 0.15); 
        }

        .card-img { width: 100%; height: 270px; object-fit: cover; transition: 0.5s; }
        .card:hover .card-img { filter: brightness(0.5) blur(2px); }

        .card-content { 
            position: absolute; bottom: 0; width: 100%; padding: 20px; box-sizing: border-box; 
            background: linear-gradient(to top, rgba(0,0,0,0.9) 20%, transparent);
            transform: translateY(10px); transition: 0.4s;
        }
        .card:hover .card-content { transform: translateY(0); }

        .card-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .card-type { font-size: 10px; font-weight: 800; color: var(--primary); text-transform: uppercase; letter-spacing: 1px; }

        /* Botão Download Flutuante no Card */
        .card-action { 
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) scale(0.5); 
            opacity: 0; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
        }
        .card:hover .card-action { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        .circle-btn { background: var(--primary); color: white; width: 50px; height: 50px; border-radius: 0; display: flex; align-items: center; justify-content: center; border: none; font-size: 18px; box-shadow: 0 10px 20px rgba(0, 122, 255, 0.4); }

        /* --- Modal Moderno --- */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 2000; align-items: center; justify-content: center; backdrop-filter: blur(15px); }
        .modal-content { background: #0f0f0f; width: 90%; max-width: 1100px; height: 85vh; border-radius: 0; border: 1px solid var(--border); overflow: hidden; display: flex; flex-direction: column; }
        
        .modal-body { display: flex; flex: 1; overflow: hidden; }
        .side-info { width: 350px; border-right: 1px solid var(--border); display: flex; flex-direction: column; background: #0a0a0a; }
        .main-view { flex: 1; background: #000; position: relative; display: flex; align-items: center; justify-content: center; }

        /* Temporadas e Episódios */
        .season-selector { padding: 20px; display: flex; gap: 10px; overflow-x: auto; border-bottom: 1px solid var(--border); }
        .s-btn { background: var(--glass); border: 1px solid var(--border); color: #fff; padding: 8px 16px; border-radius: 0; cursor: pointer; white-space: nowrap; font-size: 12px; font-weight: 600; }
        .s-btn.active { background: var(--primary); border-color: var(--primary); }

        .ep-list { flex: 1; overflow-y: auto; padding: 10px; }
        .ep-card { 
            display: flex; align-items: center; padding: 12px; border-radius: 0; margin-bottom: 8px; 
            transition: 0.3s; cursor: pointer; border: 1px solid transparent; 
        }
        .ep-card:hover { background: var(--glass); border-color: var(--border); }
        .ep-card.active { border-color: var(--primary); background: rgba(0, 122, 255, 0.05); }
        .ep-num { font-size: 12px; font-weight: 800; color: var(--primary); margin-right: 15px; width: 25px; }
        .ep-title { font-size: 13px; font-weight: 500; flex: 1; }
        .ep-dl { color: var(--text-dim); padding: 5px; }
        .ep-dl:hover { color: #fff; }

        /* --- Plyr Customization --- */
        :root {
            --plyr-color-main: var(--primary);
            --plyr-video-background: #000;
        }
        .plyr { border-radius: 12px; overflow: hidden; height: 100%; width: 100%; }
        .plyr--video { background: #000; }

        .close-modal { position: absolute; top: 20px; right: 20px; font-size: 24px; cursor: pointer; z-index: 100; color: #fff; background: rgba(0,0,0,0.5); width: 40px; height: 40px; border-radius: 0; display: flex; align-items: center; justify-content: center; transition: 0.3s; }
        .close-modal:hover { background: #ff4444; transform: rotate(90deg); }
    </style>
</head>
<body>

    {% if page == 'login' %}
    <div style="display:flex; justify-content:center; align-items:center; height:100vh;">
        <div style="background:var(--card-bg); padding:50px; border-radius:0; border:1px solid var(--border); width:350px; text-align:center;">
            <div style="color:var(--primary); font-size:40px; font-weight:900; margin-bottom:10px;">HYPER-V</div>
            <p style="color:var(--text-dim); font-size:12px; margin-bottom:30px; letter-spacing:3px;">PREMIUM ACCESS</p>
            
            {% if error %}
            <div style="background:rgba(255,0,0,0.1); color:#ff4444; padding:12px; border-radius:0; font-size:12px; margin-bottom:20px; border:1px solid rgba(255,0,0,0.2);">
                <i class="fas fa-exclamation-circle"></i> {{ error }}
            </div>
            {% endif %}

            <form method="POST">
                <input type="text" name="m3u" placeholder="Cole seu link M3U aqui..." style="width:100%; padding:15px; background:var(--bg); border:1px solid var(--border); color:#fff; border-radius:0; margin-bottom:20px; outline:none; box-sizing:border-box;" required>
                <button type="submit" style="width:100%; padding:15px; background:var(--primary); color:#fff; border:none; border-radius:0; font-weight:700; cursor:pointer; box-shadow: 0 10px 20px rgba(0,122,255,0.2);">CONECTAR AGORA</button>
            </form>
            <p style="color:var(--text-dim); font-size:10px; margin-top:20px;">Use o link completo gerado pelo seu provedor</p>
        </div>
    </div>
    {% else %}
    <nav class="nav">
        <a href="/dashboard" class="logo">HYPER-V</a>
        <div class="nav-links">
            <a href="/dashboard?cat=movie" class="nav-link {{ 'active' if active_cat == 'movie' }}">Filmes</a>
            <a href="/dashboard?cat=series" class="nav-link {{ 'active' if active_cat == 'series' }}">Séries</a>
        </div>
        <div class="search-container">
            <i class="fas fa-search search-icon"></i>
            <form method="GET" action="/dashboard">
                <input type="text" name="search" class="search-input" placeholder="Pesquisar filmes ou séries..." value="{{ search_term }}">
            </form>
        </div>
        <a href="/logout" style="color:var(--text-dim); transition: 0.3s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='var(--text-dim)'"><i class="fas fa-power-off"></i></a>
    </nav>

    <div class="grid">
        {% for item in content %}
        <div class="card" onclick="openMedia('{{ item.type }}', '{{ item.series_id or item.stream_id }}', '{{ item.name }}', '{{ item.container_extension }}')">
            <img src="{{ item.stream_icon or item.cover }}" class="card-img" loading="lazy" onerror="this.src='https://via.placeholder.com/200x300/111/fff?text=No+Cover'">
            <div class="card-action">
                <div class="circle-btn"><i class="fas fa-play"></i></div>
            </div>
            <div class="card-content">
                <div class="card-type">
                    {% if item.type == 'series' %}
                        <i class="fas fa-tv"></i> Série
                    {% else %}
                        <i class="fas fa-film"></i> Filme
                    {% endif %}
                </div>
                <div class="card-title">{{ item.name }}</div>
            </div>
        </div>
        {% endfor %}
        
        {% if not content %}
        <div style="grid-column: 1/-1; text-align: center; padding: 100px 0; color: var(--text-dim); opacity: 0.5;">
            <i class="fas fa-search" style="font-size: 40px; margin-bottom: 20px; display: block;"></i>
            <p>Nenhum conteúdo carregado.<br><small>Verifique se sua URL M3U é válida ou se o servidor está online.</small></p>
        </div>
        {% endif %}
    </div>

    <!-- Modal Premium -->
    <div id="mediaModal" class="modal">
        <div class="modal-content">
            <div class="close-modal" onclick="closeModal()">&times;</div>
            <div class="modal-body">
                <div class="main-view" id="playerView">
                    <div style="text-align:center; color:var(--text-dim);">
                        <i class="fas fa-play-circle" style="font-size:60px; margin-bottom:20px;"></i>
                        <p>Selecione um conteúdo para reproduzir</p>
                    </div>
                </div>
                <div class="side-info" id="sidePanel">
                    <div style="padding:25px; border-bottom:1px solid var(--border);">
                        <h2 id="mediaTitle" style="margin:0; font-size:18px;"></h2>
                        <p id="mediaStatus" style="font-size:11px; color:var(--primary); margin:5px 0 0 0; font-weight:800; text-transform:uppercase;"></p>
                    </div>
                    <div id="seasonContainer" class="season-selector"></div>
                    <div id="epArea" class="ep-list"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let playerInstance = null;

        function triggerDownload(url, filename) {
            const a = document.createElement('a');
            a.href = url;
            a.download = filename.replace(/[/\\?%*:|"<>]/g, '-') + ".mp4";
            a.click();
        }

        async function openMedia(type, id, name, ext) {
            if (type === 'live') {
                {% if user %}
                const url = `{{ user.dns }}/live/{{ user.user }}/{{ user.pass }}/${id}.ts`;
                playVideo(url, name);
                {% endif %}
                return;
            }
            
            if (type === 'movie') {
                {% if user %}
                const url = `{{ user.dns }}/movie/{{ user.user }}/{{ user.pass }}/${id}.${ext || 'mp4'}`;
                playVideo(url, name, id, 'movie');
                {% endif %}
                return;
            }

            const modal = document.getElementById('mediaModal');
            document.getElementById('mediaTitle').innerText = name;
            document.getElementById('mediaStatus').innerText = 'Série Multi-Season';
            modal.style.display = 'flex';
            
            const epArea = document.getElementById('epArea');
            const sContainer = document.getElementById('seasonContainer');
            const playerView = document.getElementById('playerView');
            
            epArea.innerHTML = ""; sContainer.innerHTML = "";
            playerView.innerHTML = `<div style="text-align:center; color:var(--text-dim);"><i class="fas fa-tv" style="font-size:60px; margin-bottom:20px;"></i><p>Escolha um episódio para assistir agora</p></div>`;
            
            const r = await fetch(`/series_info/${id}`);
            const data = await r.json();
            renderSeries(data, name);
        }

        function renderSeries(data, seriesName) {
            const sContainer = document.getElementById('seasonContainer');
            const epList = data.episodes || {};
            
            Object.keys(epList).forEach((s, index) => {
                const btn = document.createElement('button');
                btn.className = `s-btn ${index === 0 ? 'active' : ''}`;
                btn.innerText = `Temporada ${s}`;
                btn.onclick = () => {
                    document.querySelectorAll('.s-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    showEpisodes(epList[s], seriesName, s);
                };
                sContainer.appendChild(btn);
            });
            if(Object.keys(epList).length > 0) showEpisodes(epList[Object.keys(epList)[0]], seriesName, Object.keys(epList)[0]);
        }

        function showEpisodes(eps, seriesName, sNum) {
            const epArea = document.getElementById('epArea');
            epArea.innerHTML = "";
            eps.forEach(ep => {
                const ext = ep.container_extension || 'mp4';
                const epUrl = `{{ user.dns }}/series/{{ user.user }}/{{ user.pass }}/${ep.id}.${ext}`;
                const nameFinal = `${seriesName} S${String(sNum).padStart(2,'0')}E${String(ep.episode_num).padStart(2,'0')}`;
                
                const div = document.createElement('div');
                div.className = "ep-card";
                div.innerHTML = `
                    <div class="ep-num">${String(ep.episode_num).padStart(2,'0')}</div>
                    <div class="ep-title" onclick="playVideo('${epUrl}', '${nameFinal}', '${ep.id}', 'movie')">${ep.title || 'Episódio ' + ep.episode_num}</div>
                    <div class="ep-dl" onclick="triggerDownload('${epUrl}', '${nameFinal}')"><i class="fas fa-download"></i></div>
                `;
                epArea.appendChild(div);
            });
        }

        async function playVideo(url, name, id, type) {
            let subUrl = "";
            const modal = document.getElementById('mediaModal');
            const playerView = document.getElementById('playerView');
            
            // Tenta buscar informações extras (legendas)
            try {
                const action = type === 'series' ? 'get_series_info' : 'get_vod_info';
                const r = await fetch(`/${action}/${id}`);
                const data = await r.json();
                const subList = (data.info && data.info.subtitles) || (data.movie_data && data.movie_data.subtitles) || data.subtitles || [];
                if (subList.length > 0) {
                    const ptSub = subList.find(s => s.language && s.language.toLowerCase().includes('por'));
                    subUrl = ptSub ? ptSub.location : subList[0].location;
                }
            } catch(e) {}

            // Abre o modal se for filme (a série já abre o modal antes)
            if (type === 'movie') {
                document.getElementById('mediaTitle').innerText = name;
                document.getElementById('mediaStatus').innerText = 'Filme Premium';
                document.getElementById('seasonContainer').innerHTML = "";
                document.getElementById('epArea').innerHTML = "";
                modal.style.display = 'flex';
            }

            // Injeta o player na mesma tela via iFrame (mais seguro para layouts complexos)
            const playerUrl = `/watch?url=${encodeURIComponent(url)}&name=${encodeURIComponent(name)}&sub=${encodeURIComponent(subUrl)}`;
            playerView.innerHTML = `
                <iframe src="${playerUrl}" style="width:100%; height:100%; border:none;" allow="autoplay; fullscreen; picture-in-picture"></iframe>
            `;
        }

        function closeModal() {
            document.getElementById('mediaModal').style.display = 'none';
            document.getElementById('playerView').innerHTML = `
                <div style="text-align:center; color:var(--text-dim);">
                    <i class="fas fa-play-circle" style="font-size:60px; margin-bottom:20px;"></i>
                    <p>Selecione um conteúdo para reproduzir</p>
                </div>
            `;
    </script>
    {% endif %}
</body>
</html>
"""

PLAYER_LAYOUT = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>HYPER PLAYER | {{ name }}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        :root { --primary: #007aff; --bg: #000; }
        body, html { margin:0; padding:0; width:100%; height:100%; background:var(--bg); font-family: 'Plus Jakarta Sans', sans-serif; overflow:hidden; color:#fff; }
        
        #player-container { position:relative; width:100vw; height:100vh; display:flex; align-items:center; justify-content:center; }
        video { width:100%; height:100%; object-fit: contain; }

        /* --- Estilos do Player Reformulados --- */
        :root { --primary: #ff123c; --bg: #000; }
        body, html { margin:0; padding:0; width:100%; height:100%; background:var(--bg); font-family: 'Plus Jakarta Sans', sans-serif; overflow:hidden; color:#fff; }
        
        #player-container { 
            position:relative; width:100vw; height:100vh; background:#000;
            display:flex; align-items:center; justify-content:center;
            cursor: default;
        }
        video { max-width:100%; max-height:100%; width:auto; height:auto; }

        /* Camada de Interação (Clique p/ Play/Pause no vídeo todo) */
        .video-overlay { position:absolute; inset:0; z-index:2; }

        /* Controles Centrais (Aparecem no Hover) */
        .center-controls {
            position:absolute; top:50%; left:50%; transform:translate(-50%, -50%);
            display:flex; align-items:center; gap:60px; z-index:10;
            opacity:0; transition:0.3s; pointer-events:none;
        }
        #player-container:hover .center-controls { opacity:1; pointer-events:auto; }

        .c-btn { 
            background:none; border:none; 
            color:#fff; border-radius:0; width:80px; height:80px; 
            display:flex; align-items:center; justify-content:center; 
            font-size:45px; cursor:pointer; transition:0.2s;
        }
        .c-btn:hover { transform:scale(1.2); color:var(--primary); }
        .c-btn.play-btn { width:120px; height:120px; font-size:60px; }

        /* Barra Inferior */
        .bottom-bar {
            position:absolute; bottom:0; left:0; right:0; 
            padding:60px 4% 30px 4%;
            background: linear-gradient(transparent, rgba(0,0,0,0.95));
            z-index:20; opacity:0; transition:0.3s;
        }
        #player-container:hover .bottom-bar { opacity:1; }

        .progress-wrapper { width:100%; height:4px; background:rgba(255,255,255,0.2); border-radius:0; cursor:pointer; margin-bottom:25px; position:relative; }
        .progress-fill { height:100%; background:var(--primary); width:0%; border-radius:0; box-shadow: 0 0 10px rgba(255,18,60,0.5); }
        
        .controls-row { display:flex; align-items:center; gap:20px; }
        .icon-btn { background:none; border:none; color:#fff; font-size:22px; cursor:pointer; opacity:0.8; transition:0.3s; }
        .icon-btn:hover { opacity:1; color:var(--primary); }
        
        .time-info { font-size:16px; font-weight:500; color:#fff; flex:1; margin-left:10px; opacity:0.9; }

        /* Menu Config */
        .settings-menu {
            position:absolute; bottom:90px; right:4%; background:rgba(15,15,15,0.98); 
            border:1px solid rgba(255,255,255,0.1); border-radius:0; width:220px; 
            padding:10px; display:none; flex-direction:column; z-index:30; backdrop-filter:blur(20px);
        }
        .menu-opt { padding:12px 15px; border-radius:0; cursor:pointer; font-size:14px; display:flex; justify-content:space-between; }
        .menu-opt:hover { background:rgba(255,255,255,0.05); }
        .active-menu { display:flex; }

    </style>
</head>
<body>
    <div id="player-container">
        <video id="mainVideo" playsinline>
            {% if sub %}
            <track src="{{ sub }}" kind="subtitles" srclang="pt" label="Português" default showing>
            {% endif %}
        </video>
        
        <!-- Clique no vídeo -->
        <div class="video-overlay" onclick="togglePlay()"></div>

        <!-- Botões de Ação Central -->
        <div class="center-controls">
            <div class="c-btn" onclick="skip(-10)"><i class="fas fa-undo"></i></div>
            <div class="c-btn play-btn" id="playBtn" onclick="togglePlay()"><i class="fas fa-play"></i></div>
            <div class="c-btn" onclick="skip(10)"><i class="fas fa-redo"></i></div>
        </div>

        <!-- Barra Inferior -->
        <div class="bottom-bar">
            <div class="progress-wrapper" id="progWrap" onclick="seek(event)">
                <div class="progress-fill" id="progFill"></div>
            </div>
            
            <div class="controls-row">
                <button class="icon-btn" id="muteBtn" onclick="toggleMute()"><i class="fas fa-volume-up"></i></button>
                <div class="time-info">
                    <span id="curTime">00:00</span> / <span id="totalTime">00:00</span>
                </div>

                <button class="icon-btn" title="Legendas"><i class="far fa-closed-captioning"></i></button>
                <button class="icon-btn" onclick="toggleSettings()" title="Configurações"><i class="fas fa-cog"></i></button>
                <button class="icon-btn" onclick="video.requestPictureInPicture()" title="Miniatura"><i class="fas fa-clone"></i></button>
                <button class="icon-btn" onclick="toggleFS()" title="Tela Cheia"><i class="fas fa-expand"></i></button>
            </div>

            <div class="settings-menu" id="setMenu">
                <div class="menu-opt" onclick="setSpeed(1)">Velocidade <span>1x</span></div>
                <div class="menu-opt" onclick="setSpeed(1.5)">Velocidade <span>1.5x</span></div>
                <div class="menu-opt" onclick="setSpeed(2)">Velocidade <span>2x</span></div>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById('mainVideo');
        const playBtn = document.getElementById('playBtn');
        const progFill = document.getElementById('progFill');
        const progWrap = document.getElementById('progWrap');
        const curTimeEl = document.getElementById('curTime');
        const totalTimeEl = document.getElementById('totalTime');
        const setMenu = document.getElementById('setMenu');

        const url = "{{ url }}";
        if (url.includes('.m3u8') && Hls.isSupported()) {
            const hls = new Hls();
            hls.loadSource(url);
            hls.attachMedia(video);
        } else {
            video.src = url;
        }

        function formatTime(t) {
            const h = Math.floor(t / 3600);
            const m = Math.floor((t % 3600) / 60);
            const s = Math.floor(t % 60);
            return (h > 0 ? h + ':' : '') + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
        }

        function togglePlay() {
            if (video.paused) {
                video.play();
                playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            } else {
                video.pause();
                playBtn.innerHTML = '<i class="fas fa-play"></i>';
            }
        }

        function skip(v) { video.currentTime += v; }

        function seek(e) {
            const rect = progWrap.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            video.currentTime = pos * video.duration;
        }

        function toggleMute() {
            video.muted = !video.muted;
            document.getElementById('muteBtn').innerHTML = video.muted ? '<i class="fas fa-volume-mute"></i>' : '<i class="fas fa-volume-up"></i>';
        }

        function toggleSettings() {
            setMenu.classList.toggle('active-menu');
        }

        function setSpeed(s) {
            video.playbackRate = s;
            toggleSettings();
        }

        function toggleFS() {
            if (!document.fullscreenElement) {
                document.getElementById('player-container').requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }

        video.addEventListener('timeupdate', () => {
            const p = (video.currentTime / video.duration) * 100;
            progFill.style.width = p + '%';
            curTimeEl.innerText = formatTime(video.currentTime);
            
            // Salva o progresso a cada 5 segundos
            if (Math.floor(video.currentTime) % 5 === 0) {
                localStorage.setItem('resume_' + btoa(url), video.currentTime);
            }
        });

        video.addEventListener('loadedmetadata', () => {
            totalTimeEl.innerText = formatTime(video.duration);
            
            // Tenta retomar de onde parou
            const savedTime = localStorage.getItem('resume_' + btoa(url));
            if (savedTime && savedTime < video.duration - 10) {
                video.currentTime = parseFloat(savedTime);
            }
        });

        // Limpa o progresso se chegar no final
        video.addEventListener('ended', () => {
            localStorage.removeItem('resume_' + btoa(url));
        });

        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space') { e.preventDefault(); togglePlay(); }
            if (e.code === 'ArrowRight') skip(10);
            if (e.code === 'ArrowLeft') skip(-10);
        });

        video.play().catch(() => {});
    </script>
</body>
</html>
"""

# --- BACKEND ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

async def api_call(action, params=""):
    u = session.get('user_data')
    if not u: return []
    url = f"{u['dns']}/player_api.php?username={u['user']}&password={u['pass']}&action={action}{params}"
    async with aiohttp.ClientSession(headers=HEADERS) as s:
        try:
            async with s.get(url, ssl=False, timeout=15) as r:
                if r.status == 200:
                    return await r.json()
                return []
        except Exception as e:
            print(f"Erro na API ({action}): {e}")
            return []

@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
async def index():
    if request.method == 'POST':
        m3u = request.form.get('m3u', '')
        try:
            dns = re.findall(r'(https?://[^/]+)', m3u)[0]
            # Tenta pegar username ou user
            user_match = re.findall(r'username=([^&]*)', m3u) or re.findall(r'[?&]user=([^&]*)', m3u)
            pass_match = re.findall(r'password=([^&]*)', m3u) or re.findall(r'[?&]pass=([^&]*)', m3u)
            
            if not user_match or not pass_match:
                return render_template_string(HTML_LAYOUT, page='login', error="Formato de URL inválido")
                
            session['user_data'] = {
                'dns': dns.rstrip('/'), 
                'user': user_match[0], 
                'pass': pass_match[0]
            }
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Erro no login: {e}")
            return render_template_string(HTML_LAYOUT, page='login', error="Erro ao processar URL")
    return render_template_string(HTML_LAYOUT, page='login')

# --- CACHE GLOBAL PARA PERFORMANCE ---
CACHE = {"movies": [], "series": [], "timestamp": 0, "user": ""}

@app.route('/dashboard', strict_slashes=False)
async def dashboard():
    if 'user_data' not in session: return redirect(url_for('index'))
    search = request.args.get('search', '').lower()
    cat = request.args.get('cat', 'movie')
    u = session['user_data']
    
    # Atualiza o cache se estiver vazio ou se o usuário mudou
    current_time = time.time()
    if not CACHE["movies"] or CACHE["user"] != u['user'] or (current_time - CACHE["timestamp"] > 1800):
        m_task = api_call("get_vod_streams")
        s_task = api_call("get_series")
        m, s = await asyncio.gather(m_task, s_task)
        CACHE["movies"] = m if isinstance(m, list) else []
        CACHE["series"] = s if isinstance(s, list) else []
        CACHE["timestamp"] = current_time
        CACHE["user"] = u['user']
        for x in CACHE["movies"]: x['type'] = 'movie'
        for x in CACHE["series"]: x['type'] = 'series'

    # Filtragem ultra rápida em memória
    active_content = CACHE["movies"] if cat == 'movie' else CACHE["series"]
    
    if search:
        filtered_data = [x for x in active_content if search in x.get('name','').lower()]
    else:
        filtered_data = active_content[:200] # Mostra os primeiros 200 instantaneamente
        
    return render_template_string(HTML_LAYOUT, 
                                page='dash', 
                                content=filtered_data, 
                                user=u, 
                                search_term=search,
                                active_cat=cat)

@app.route('/series_info/<id>', strict_slashes=False)
async def series_info(id):
    res = await api_call("get_series_info", f"&series_id={id}")
    return jsonify(res if isinstance(res, dict) else {"episodes": {}})

@app.route('/vod_info/<id>', strict_slashes=False)
async def vod_info(id):
    res = await api_call("get_vod_info", f"&vod_id={id}")
    return jsonify(res if isinstance(res, dict) else {})

@app.route('/logout', strict_slashes=False)
def logout(): 
    session.clear()
    return redirect(url_for('index'))

@app.route('/watch', strict_slashes=False)
async def watch():
    if 'user_data' not in session: return "Acesso não autorizado", 403
    url = request.args.get('url')
    name = request.args.get('name', 'HYPER-V Stream')
    sub = request.args.get('sub', '')
    if not url: return redirect(url_for('dashboard'))
    return render_template_string(PLAYER_LAYOUT, url=url, name=name, sub=sub)

if __name__ == '__main__': 
    app.run(debug=True, port=5000)
