from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================================
# 1. HTML & JAVASCRIPT FRONTEND (MONOPOLY CITY NIGHT VIDEO ANIMATION BG)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Tycoon Online</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            text-align: center; 
            background: #09090b; 
            color: #f8fafc; 
            margin: 0; 
            padding: 0; 
            position: relative;
            overflow-x: hidden;
        }

        /* Monopoly City Night Video Background Loop */
        .bg-video-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -10;
            overflow: hidden;
            pointer-events: none;
        }

        .bg-video-container video {
            position: absolute;
            top: 50%;
            left: 50%;
            min-width: 100%;
            min-height: 100%;
            width: auto;
            height: auto;
            transform: translate(-50%, -50%);
            object-fit: cover;
            filter: brightness(0.45) contrast(1.2);
        }

        .screen { display: none; min-height: 100vh; padding: 20px; box-sizing: border-box; }
        .active { display: block; }
        
        #done-turn-btn {
            position: fixed;
            top: 15px;
            right: 15px;
            background: linear-gradient(135deg, #d4af37, #aa771c);
            color: #000;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: 800;
            border-radius: 6px;
            cursor: pointer;
            z-index: 3000;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
            display: none;
        }
        #done-turn-btn:hover { filter: brightness(1.1); }

        /* Realistic 3D Card Effect Styling */
        .card { 
            display: inline-block; width: 95px; height: 135px; 
            border: 2px solid #d4af37; border-radius: 8px; margin: 6px; 
            background: #fbf6e2; color: #2c3e50; padding: 8px; cursor: pointer;
            vertical-align: top; box-sizing: border-box; 
            transition: transform 0.3s ease, box-shadow 0.3s ease; 
            position: relative;
            transform-style: preserve-3d;
            box-shadow: 0 6px 12px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.6);
        }
        .card:hover { 
            transform: translateY(-8px) scale(1.03) rotateX(2deg); 
            box-shadow: 0 12px 24px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.8); 
        }
        
        .board-card { 
            padding: 5px 10px; margin: 3px; border-radius: 6px; font-size: 13px; 
            display: inline-block; border: 1px solid #fff; 
            box-shadow: 0 3px 6px rgba(0,0,0,0.3); font-weight: bold;
        }
        .building-card { background: #c0392b; color: white; font-weight: bold; }
        
        .card-yellow { background-color: #f7f1bd !important; color: #2c3e50; }
        .card-green { background-color: #d4edbc !important; color: #2c3e50; }
        .card-purple { background-color: #e3d3e8 !important; color: #2c3e50; }
        .card-blue { background-color: #cce7e8 !important; color: #2c3e50; }
        .card-peach { background-color: #fce1d7 !important; color: #2c3e50; }
        .card-building { background-color: #eaf2f8 !important; color: #2c3e50; }
        .card-wildproperty { background-color: #ffffff !important; color: #2c3e50; border: 2px dashed #333; }

        .money-1 { background-color: #1b4d3e !important; color: #ffffff; } 
        .money-2 { background-color: #1b365d !important; color: #ffffff; } 
        .money-3 { background-color: #4a154b !important; color: #ffffff; } 
        .money-4 { background-color: #004d40 !important; color: #ffffff; } 
        .money-5 { background-color: #641e16 !important; color: #ffffff; } 
        .money-10 { background-color: #273746 !important; color: #ffffff; } 

        .prop-Brown { background-color: #8B4513 !important; color: #ffffff; }
        .prop-Light-Blue { background-color: #3498db !important; color: #ffffff; }
        .prop-Pink { background-color: #FF69B4 !important; color: #000000; }
        .prop-Orange { background-color: #FF8C00 !important; color: #000000; }
        .prop-Red { background-color: #FF0000 !important; color: #ffffff; }
        .prop-Yellow { background-color: #f1c40f !important; color: #000000; }
        .prop-Green { background-color: #2ecc71 !important; color: #ffffff; }
        .prop-Dark-Blue { background-color: #00008B !important; color: #ffffff; }
        .prop-Railroad { background-color: #333333 !important; color: #ffffff; }
        .prop-Utility { background-color: #7f8c8d !important; color: #ffffff; }
        .prop-Wild { background-color: #95a5a6 !important; color: #000000; }

        /* Elegant Luxury Frame with Glowing Gold Animated Border */
        .luxury-wrapper {
            max-width: 1200px;
            margin: 20px auto;
            border: 2px solid #d4af37;
            border-radius: 12px;
            background: rgba(10, 8, 6, 0.75);
            box-shadow: 0 0 50px rgba(212, 175, 55, 0.35), inset 0 0 40px rgba(0,0,0,0.9);
            position: relative;
            padding: 30px 20px 50px 20px;
            box-sizing: border-box;
            backdrop-filter: blur(12px);
            animation: borderGlow 6s ease-in-out infinite alternate;
        }

        @keyframes borderGlow {
            0% { box-shadow: 0 0 30px rgba(212, 175, 55, 0.2), inset 0 0 30px rgba(0,0,0,0.8); }
            100% { box-shadow: 0 0 60px rgba(212, 175, 55, 0.5), inset 0 0 50px rgba(0,0,0,0.9); }
        }

        /* Top Navbar Links */
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            padding-bottom: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
            gap: 15px;
        }

        .nav-brand {
            border: 1px solid #d4af37;
            padding: 6px 14px;
            font-family: 'Cinzel', serif;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
            color: #d4af37;
            background: rgba(0,0,0,0.5);
        }

        .nav-links {
            display: flex;
            gap: 25px;
            list-style: none;
            margin: 0;
            padding: 0;
            font-size: 13px;
            letter-spacing: 1.5px;
            font-weight: 600;
            color: #ccc;
        }

        .nav-links li { cursor: pointer; transition: color 0.3s; }
        .nav-links li:hover, .nav-links li.active-link { color: #d4af37; }

        /* Hero Section Styling */
        .hero-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 40px;
            text-align: left;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .hero-content {
            flex: 1;
            min-width: 300px;
        }

        .hero-subtitle {
            font-size: 13px;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: #d4af37;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .hero-title {
            font-family: 'Cinzel', serif;
            font-size: 3.5rem;
            line-height: 1.1;
            font-weight: 900;
            color: #f3e5ab;
            margin: 0 0 15px 0;
            text-shadow: 0 5px 15px rgba(0,0,0,0.5);
        }

        .hero-title span {
            display: block;
            font-size: 3.2rem;
            color: #d4af37;
            letter-spacing: 6px;
            margin-top: 5px;
        }

        .hero-tagline {
            font-size: 15px;
            color: #a1a1aa;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        /* Forms & Inputs inside Luxury Theme */
        .forms-grid {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }

        .auth-box {
            background: rgba(12, 10, 8, 0.85);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 8px;
            padding: 20px;
            flex: 1;
            min-width: 240px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }

        .auth-box h3 {
            font-family: 'Cinzel', serif;
            color: #d4af37;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 16px;
            letter-spacing: 1px;
        }

        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 12px;
            background: rgba(0,0,0,0.7);
            border: 1px solid rgba(212, 175, 55, 0.3);
            color: #fff;
            border-radius: 4px;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        input:focus { border-color: #d4af37; outline: none; box-shadow: 0 0 8px rgba(212, 175, 55, 0.3); }

        .luxury-btn {
            background: linear-gradient(135deg, #d4af37, #aa771c);
            color: #0b0907;
            border: none;
            padding: 12px 20px;
            font-weight: 800;
            font-size: 14px;
            letter-spacing: 1px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            transition: filter 0.2s, transform 0.2s;
            text-transform: uppercase;
        }
        .luxury-btn:hover { filter: brightness(1.1); transform: translateY(-1px); }

        .name-input-container {
            margin-bottom: 25px;
            max-width: 400px;
        }

        /* Elegant Playing Cards Deck Graphic Representation */
        .hero-cards-display {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            min-width: 280px;
            position: relative;
            height: 320px;
        }

        .showcase-card {
            width: 130px;
            height: 185px;
            background: #fbf6e2;
            border: 2px solid #d4af37;
            border-radius: 10px;
            position: absolute;
            box-shadow: 0 15px 35px rgba(0,0,0,0.7);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 12px;
            color: #1a1a1a;
            font-weight: bold;
            box-sizing: border-box;
        }

        .showcase-card.c1 { transform: rotate(-12deg) translateX(-40px); z-index: 1; background: #111; color: #d4af37; border-color: #d4af37; }
        .showcase-card.c2 { transform: rotate(0deg) scale(1.05); z-index: 3; }
        .showcase-card.c3 { transform: rotate(15deg) translateX(40px); z-index: 2; background: #8b0000; color: #fff; border-color: #d4af37; }

        .game-footer-info {
            display: flex;
            justify-content: space-around;
            margin-top: 50px;
            border-top: 1px solid rgba(212, 175, 55, 0.2);
            padding-top: 25px;
            color: #888;
            font-size: 13px;
            letter-spacing: 1px;
        }

        /* Modal Dialog Custom Theme */
        #modal-overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); z-index: 2500; justify-content: center; align-items: center;
            backdrop-filter: blur(5px);
        }
        .modal-content { 
            background: #14110e; 
            padding: 25px; 
            border-radius: 10px; 
            width: 90%; 
            max-width: 450px; 
            text-align: center; 
            border: 2px solid #d4af37; 
            max-height: 80vh; 
            overflow-y: auto; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.9); 
        }
        .modal-content h3 { font-family: 'Cinzel', serif; color: #d4af37; }
        .modal-btn { background: #d4af37; margin: 6px 0; width: 100%; cursor: pointer; padding: 12px; color: #000; font-weight: 800; border-radius: 4px; border: none; }
        .modal-btn:hover { background: #f3e5ab; }
        .target-prop-option { padding: 12px; margin: 6px 0; background: #1c1813; border: 1px solid rgba(212,175,55,0.4); border-radius: 6px; cursor: pointer; color: white; }
        .target-prop-option:hover { background: #d4af37; color: #000; font-weight: bold; }

        #player-list { list-style: none; padding: 0; font-size: 18px; }
        .turn-box { background: #d4af37; color: #000; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-size: 16px; font-weight: 800; box-shadow: 0 4px 15px rgba(212,175,55,0.3); }
        .sets-container { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 5px; }
        .set-column { border: 1px dashed rgba(212,175,55,0.4); padding: 6px; border-radius: 6px; background: rgba(0,0,0,0.4); min-width: 100px; text-align: center; }
    </style>
</head>
<body>

    <!-- Monopoly City Night Immersive Video Background Loop -->
    <div class="bg-video-container">
        <video autoplay muted loop playsinline>
            <source src="https://assets.mixkit.co/videos/preview/mixkit-flying-through-a-neon-futuristic-city-41480-large.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>

    <button id="done-turn-btn" onclick="endTurn()">✓ Done</button>

    <!-- CUSTOM MODAL DIALOG -->
    <div id="modal-overlay">
        <div class="modal-content">
            <h3 id="modal-title">Select Option</h3>
            <div id="modal-buttons"></div>
            <button onclick="closeModal()" style="background: #8b0000; margin-top: 15px; cursor:pointer; color: white; padding: 10px; border-radius: 4px; border:none; width:100%; font-weight:bold;">Cancel</button>
        </div>
    </div>

    <!-- LOBBY SCREEN -->
    <div id="lobby-screen" class="screen active">
        <div class="luxury-wrapper">
            <!-- Top Navbar -->
            <div class="top-nav">
                <div class="nav-brand">PROPERTY TYCOON</div>
                <ul class="nav-links">
                    <li class="active-link">HOME</li>
                    <li>ABOUT</li>
                    <li>RULES</li>
                    <li>CARDS</li>
                    <li>PLAY</li>
                    <li>CONTACT</li>
                </ul>
            </div>

            <!-- Hero Section -->
            <div class="hero-section">
                <div class="hero-content">
                    <div class="hero-subtitle">The Classic Card Game</div>
                    <h1 class="hero-title">PROPERTY <span>TYCOON</span></h1>
                    <div class="hero-tagline">Buy. Trade. Steal. Win!<br>The fast-paced card game of property, money and deals.</div>
                    
                    <div class="name-input-container">
                        <input type="text" id="player-name" placeholder="Enter Your Nickname" required>
                    </div>

                    <div class="forms-grid">
                        <div class="auth-box">
                            <h3>Host a Game</h3>
                            <input type="text" id="create-room-id" placeholder="Room ID">
                            <input type="password" id="create-room-pass" placeholder="Password">
                            <button onclick="goToModeSelect()" class="luxury-btn">Create Room</button>
                        </div>

                        <div class="auth-box">
                            <h3>Join a Friend</h3>
                            <input type="text" id="join-room-id" placeholder="Room ID">
                            <input type="password" id="join-room-pass" placeholder="Password">
                            <button onclick="joinRoom()" class="luxury-btn" style="background: #333; color: #d4af37; border: 1px solid #d4af37;">Join Room</button>
                        </div>
                    </div>
                </div>

                <!-- Showcase Cards Graphic -->
                <div class="hero-cards-display">
                    <div class="showcase-card c1">
                        <div style="font-size:10px;">ACTION CARD</div>
                        <div style="font-size:12px; font-family:'Cinzel',serif;">DEAL BREAKER</div>
                        <div style="font-size:9px; font-weight:normal;">Steal a complete property set from any player.</div>
                    </div>
                    <div class="showcase-card c2">
                        <div style="font-size:10px; color:#d4af37;">PROPERTY TYCOON</div>
                        <div style="font-size:14px; font-family:'Cinzel',serif; margin-top:20px;">PROPERTY CARD</div>
                        <div style="font-size:10px;">Valued Asset</div>
                    </div>
                    <div class="showcase-card c3">
                        <div style="font-size:10px;">BUILDING</div>
                        <div style="font-size:13px; font-family:'Cinzel',serif;">HOTEL CARD</div>
                        <div style="font-size:9px; font-weight:normal;">Add to full set for massive rent bonus!</div>
                    </div>
                </div>
            </div>

            <!-- Footer Meta Info -->
            <div class="game-footer-info">
                <div>👥 2-5 Players</div>
                <div>⏱️ 15 Min</div>
                <div>⭐ Ages 8+</div>
            </div>
        </div>
    </div>

    <!-- MODE SELECT SCREEN -->
    <div id="mode-select-screen" class="screen">
        <div class="luxury-wrapper" style="max-width: 600px;">
            <h2 style="font-family:'Cinzel',serif; color:#d4af37; margin-top:0;">Choose Game Mode</h2>
            <div class="forms-grid" style="flex-direction: column;">
                <div class="auth-box" style="width:100%; box-sizing:border-box;">
                    <h3>🤖 Play with AI Bot</h3>
                    <p style="font-size: 13px; color: #aaa; margin-bottom: 15px;">Select Difficulty Level:</p>
                    <button onclick="createRoomWithBot('easy')" class="luxury-btn" style="margin-bottom:8px; background:#16a34a; color:#fff;">🟢 Easy Bot</button>
                    <button onclick="createRoomWithBot('normal')" class="luxury-btn" style="margin-bottom:8px; background:#ca8a04; color:#fff;">🟡 Normal Bot</button>
                    <button onclick="createRoomWithBot('hard')" class="luxury-btn" style="background:#dc2626; color:#fff;">🔥 Hard Bot (EXTREME BOSS)</button>
                </div>
                <div class="auth-box" style="width:100%; box-sizing:border-box;">
                    <h3>👥 Play with Friends</h3>
                    <p style="font-size: 13px; color: #aaa; margin-bottom: 15px;">Host an online room for friends to join.</p>
                    <button onclick="createRoomWithMode('multiplayer')" class="luxury-btn">Play Multiplayer</button>
                </div>
            </div>
            <button onclick="backToLobby()" class="luxury-btn" style="background: #333; color: #ccc; margin-top: 20px; width: 150px;">Back</button>
        </div>
    </div>

    <!-- WAITING ROOM -->
    <div id="waiting-screen" class="screen">
        <div class="luxury-wrapper" style="max-width: 600px;">
            <h2 style="font-family:'Cinzel',serif; color:#d4af37;">Room ID: <span id="display-room-id" style="color:#fff;"></span></h2>
            <h3 style="color:#aaa; font-size:15px;">Players in Lobby:</h3>
            <ul id="player-list"></ul>
            <div id="host-controls" style="display: none; margin-top: 25px;">
                <button onclick="startGame()" class="luxury-btn" style="width: auto; padding: 15px 30px; font-size:16px;">▶ Start Game</button>
            </div>
        </div>
    </div>

    <!-- GAME BOARD SCREEN -->
    <div id="game-screen" class="screen">
        <div class="luxury-wrapper" style="max-width: 1400px; padding: 15px;">
            <div id="turn-info" class="turn-box" style="display:none;">
                <span id="turn-status">Waiting...</span>
            </div>

            <div style="background: rgba(10, 8, 6, 0.78); padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(212,175,55,0.3); box-shadow: inset 0 0 15px rgba(212,175,55,0.1);">
                <h3 style="font-family:'Cinzel',serif; color:#d4af37; margin-top:0;">Opponents Table</h3>
                <div id="opponents-area"></div>
            </div>

            <div style="background: rgba(10, 8, 6, 0.78); padding: 15px; border-radius: 8px; border: 1px solid rgba(212,175,55,0.3); box-shadow: inset 0 0 15px rgba(212,175,55,0.1);">
                <h3 style="font-family:'Cinzel',serif; color:#d4af37; margin-top:0;">Your Hand</h3>
                <div id="my-hand"></div>
            </div>
        </div>
    </div>

    <script>
        const socket = io(window.location.origin);
        let currentRoom = "";
        let isHost = false;
        let selectedMode = "";
        
        let myTurn = false;
        let actionsLeft = 0;
        let myHandData = [];
        let latestPlayersData = [];
        let isDiscardMode = false;
        let turnDeadline = 0;
        let currentTurnName = "";
        let timerInterval = null;
        let knownPlayers = [];
        let myPropertiesData = [];

        const setSizes = {
            'Brown': 2, 'Light Blue': 3, 'Pink': 3, 'Orange': 3,
            'Red': 3, 'Yellow': 3, 'Green': 3, 'Dark Blue': 2,
            'Railroad': 4, 'Utility': 2
        };

        const allColors = ['Brown', 'Light Blue', 'Pink', 'Orange', 'Red', 'Yellow', 'Green', 'Dark Blue', 'Railroad', 'Utility'];

        function toTitleCase(str) {
            if (!str) return '';
            return str.toLowerCase().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        }

        function closeModal() {
            document.getElementById('modal-overlay').style.display = 'none';
        }

        function showModal(title, contentHtml) {
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-buttons').innerHTML = contentHtml;
            document.getElementById('modal-overlay').style.display = 'flex';
        }

        function showOpponentModal(actionName, callback) {
            let myName = document.getElementById('player-name').value.trim();
            let opponents = latestPlayersData.filter(p => p.name.toLowerCase() !== myName.toLowerCase());
            
            if (opponents.length === 0) {
                alert("No opponents available!");
                return;
            }

            showModal(`Select Target for [${actionName}]`, "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";
            opponents.forEach(op => {
                let btn = document.createElement('button');
                btn.className = "modal-btn";
                btn.innerText = op.name;
                btn.onclick = () => {
                    closeModal();
                    callback(op);
                };
                container.appendChild(btn);
            });
        }

        function startSlyDeal(cardIdx, useType) {
            let myName = document.getElementById('player-name').value.trim();
            let opponents = latestPlayersData.filter(p => p.name.toLowerCase() !== myName.toLowerCase());
            
            if (opponents.length === 0) { alert("No opponents available!"); return; }

            showModal("Sly Deal: Choose Opponent (Incomplete Sets Only)", "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            opponents.forEach(op => {
                let btn = document.createElement('button');
                btn.className = "modal-btn";
                btn.innerText = op.name;
                btn.onclick = () => {
                    closeModal();
                    showSlyDealPropertyPicker(cardIdx, useType, op);
                };
                container.appendChild(btn);
            });
        }

        function showSlyDealPropertyPicker(cardIdx, useType, targetPlayer) {
            if (!targetPlayer.properties || targetPlayer.properties.length === 0) {
                alert(`${targetPlayer.name} has no properties to steal!`);
                return;
            }

            let colorCounts = {};
            targetPlayer.properties.forEach(p => {
                let col = p.color || 'Wild';
                colorCounts[col] = (colorCounts[col] || 0) + 1;
            });

            let validProps = targetPlayer.properties.map((prop, idx) => {
                let col = prop.color || 'Wild';
                let req = setSizes[col] || 99;
                let isComplete = colorCounts[col] >= req;
                return { prop, idx, isComplete };
            }).filter(item => !item.isComplete);

            if (validProps.length === 0) {
                alert(`${targetPlayer.name} only has properties in complete sets! Sly Deal cannot target complete sets.`);
                return;
            }

            showModal(`Steal from ${targetPlayer.name} (Click Incomplete Set Property)`, "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            validProps.forEach(item => {
                let div = document.createElement('div');
                div.className = "target-prop-option";
                div.innerHTML = `<strong>${item.prop.name}</strong> (${item.prop.value}M) [Color: ${item.prop.color || 'Wild'}]`;
                div.onclick = () => {
                    closeModal();
                    let extraData = { target_name: targetPlayer.name, target_prop_idx: item.idx };
                    socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                };
                container.appendChild(div);
            });
        }

        function startForcedDeal(cardIdx, useType) {
            if (!myPropertiesData || myPropertiesData.length === 0) {
                alert("You have no properties to trade!");
                return;
            }

            showModal("Forced Deal: Select YOUR Property to trade (Incomplete Sets Only)", "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            let myColorCounts = {};
            myPropertiesData.forEach(p => {
                let col = p.color || 'Wild';
                myColorCounts[col] = (myColorCounts[col] || 0) + 1;
            });

            let validMyProps = myPropertiesData.map((prop, idx) => {
                let col = prop.color || 'Wild';
                let req = setSizes[col] || 99;
                let isComplete = myColorCounts[col] >= req;
                return { prop, idx, isComplete };
            }).filter(item => !item.isComplete);

            if (validMyProps.length === 0) {
                alert("You only own properties in complete sets! Forced Deal cannot trade complete sets.");
                return;
            }

            validMyProps.forEach(item => {
                let div = document.createElement('div');
                div.className = "target-prop-option";
                div.innerHTML = `Give Your: <strong>${item.prop.name}</strong> (${item.prop.value}M)`;
                div.onclick = () => {
                    closeModal();
                    showForcedDealOpponentPicker(cardIdx, useType, item.idx);
                };
                container.appendChild(div);
            });
        }

        function showForcedDealOpponentPicker(cardIdx, useType, myPropIdx) {
            let myName = document.getElementById('player-name').value.trim();
            let opponents = latestPlayersData.filter(p => p.name.toLowerCase() !== myName.toLowerCase());
            
            if (opponents.length === 0) { alert("No opponents available!"); return; }

            showModal("Forced Deal: Choose Opponent", "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            opponents.forEach(op => {
                let btn = document.createElement('button');
                btn.className = "modal-btn";
                btn.innerText = op.name;
                btn.onclick = () => {
                    closeModal();
                    showForcedDealTargetPropertyPicker(cardIdx, useType, myPropIdx, op);
                };
                container.appendChild(btn);
            });
        }

        function showForcedDealTargetPropertyPicker(cardIdx, useType, myPropIdx, targetPlayer) {
            if (!targetPlayer.properties || targetPlayer.properties.length === 0) {
                alert(`${targetPlayer.name} has no properties to take!`);
                return;
            }

            let colorCounts = {};
            targetPlayer.properties.forEach(p => {
                let col = p.color || 'Wild';
                colorCounts[col] = (colorCounts[col] || 0) + 1;
            });

            let validProps = targetPlayer.properties.map((prop, idx) => {
                let col = prop.color || 'Wild';
                let req = setSizes[col] || 99;
                let isComplete = colorCounts[col] >= req;
                return { prop, idx, isComplete };
            }).filter(item => !item.isComplete);

            if (validProps.length === 0) {
                alert(`${targetPlayer.name} only has properties in complete sets! Forced Deal cannot target complete sets.`);
                return;
            }

            showModal(`Take from ${targetPlayer.name} (Incomplete Set Only)`, "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            validProps.forEach(item => {
                let div = document.createElement('div');
                div.className = "target-prop-option";
                div.innerHTML = `Take: <strong>${item.prop.name}</strong> (${item.prop.value}M)`;
                div.onclick = () => {
                    closeModal();
                    let extraData = { my_prop_idx: myPropIdx, target_name: targetPlayer.name, target_prop_idx: item.idx };
                    socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                };
                container.appendChild(div);
            });
        }

        function startDealBreaker(cardIdx, useType) {
            let myName = document.getElementById('player-name').value.trim();
            let opponents = latestPlayersData.filter(p => p.name.toLowerCase() !== myName.toLowerCase());
            
            if (opponents.length === 0) { alert("No opponents available!"); return; }

            showModal("Deal Breaker: Choose Opponent", "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            opponents.forEach(op => {
                let btn = document.createElement('button');
                btn.className = "modal-btn";
                btn.innerText = op.name;
                btn.onclick = () => {
                    closeModal();
                    showDealBreakerSetPicker(cardIdx, useType, op);
                };
                container.appendChild(btn);
            });
        }

        function showDealBreakerSetPicker(cardIdx, useType, targetPlayer) {
            if (!targetPlayer.properties || targetPlayer.properties.length === 0) {
                alert(`${targetPlayer.name} has no properties at all!`);
                return;
            }

            let colorCounts = {};
            targetPlayer.properties.forEach(p => {
                let col = p.color || 'Wild';
                colorCounts[col] = (colorCounts[col] || 0) + 1;
            });

            let completeSets = [];
            for (let col in colorCounts) {
                let req = setSizes[col] || 99;
                if (colorCounts[col] >= req) {
                    completeSets.push(col);
                }
            }

            if (completeSets.length === 0) {
                alert(`${targetPlayer.name} does not have any complete sets to steal!`);
                return;
            }

            showModal(`Steal Set from ${targetPlayer.name} (Click Set)`, "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            completeSets.forEach(col => {
                let div = document.createElement('div');
                div.className = "target-prop-option";
                div.innerHTML = `<strong>Complete Set: ${col}</strong>`;
                div.onclick = () => {
                    closeModal();
                    let extraData = { target_name: targetPlayer.name, color_group: col };
                    socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                };
                container.appendChild(div);
            });
        }

        function handleWildPropertyPlacement(cardIdx, useType, cardName) {
            let allowedColors = allColors;
            if (cardName && cardName.includes("&")) {
                allowedColors = allColors.filter(col => cardName.toLowerCase().includes(col.toLowerCase()));
            }

            showModal(`${cardName || "Wild Property"}: Choose Color Group`, "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            allowedColors.forEach(col => {
                let btn = document.createElement('button');
                btn.className = "modal-btn";
                btn.innerText = `Assign to ${col} Set`;
                btn.onclick = () => {
                    closeModal();
                    let extraData = { assigned_color: col };
                    socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                };
                container.appendChild(btn);
            });
        }

        function startRentAction(cardIdx, useType, cardName) {
            let ownedColors = [...new Set(myPropertiesData.map(p => p.color).filter(c => c))];
            
            if (ownedColors.length === 0) {
                alert("You don't own any properties to charge rent!");
                return;
            }

            let allowedColors = [];
            let title = "";

            if (cardName.includes("Wild All Colors")) {
                title = "Wild Rent: Choose Any Color You Own";
                allowedColors = ownedColors;
            } else {
                title = `Rent (${cardName}): Choose Color`;
                let cardLower = cardName.toLowerCase();
                allowedColors = ownedColors.filter(col => cardLower.includes(col.toLowerCase()));
            }

            if (allowedColors.length === 0) {
                alert("You do not own any properties matching this Rent card's colors!");
                return;
            }

            showModal(title, "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";

            allowedColors.forEach(col => {
                let btn = document.createElement('button');
                btn.className = "modal-btn";
                btn.innerText = col;
                btn.onclick = () => {
                    closeModal();
                    showRentTargetPicker(cardIdx, useType, col);
                };
                container.appendChild(btn);
            });
        }

        function showRentTargetPicker(cardIdx, useType, rentColor) {
            let chargeAll = confirm("Charge rent to ALL players? (OK = All, Cancel = Specific player)");
            let hasDoubleRent = myHandData.some(c => c.name === "Double Rent");
            let isDouble = false;
            if (hasDoubleRent) {
                isDouble = confirm("You have a Double Rent card in your hand! Do you want to use it with this rent? (OK = Yes, Cancel = No)");
            }

            if (chargeAll) {
                let extraData = { rent_color: rentColor, target_name: "", double_rent: isDouble };
                socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
            } else {
                showOpponentModal("Rent Target", (targetOp) => {
                    let extraData = { rent_color: rentColor, target_name: targetOp.name, double_rent: isDouble };
                    socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                });
            }
        }

        function goToModeSelect() {
            let n = document.getElementById('player-name').value;
            let r = document.getElementById('create-room-id').value;
            let p = document.getElementById('create-room-pass').value;
            if(!n || !r || !p) {
                alert("Please fill in your Name, Room ID, and Password first!");
                return;
            }
            document.getElementById('lobby-screen').classList.remove('active');
            document.getElementById('mode-select-screen').classList.add('active');
        }

        function backToLobby() {
            document.getElementById('mode-select-screen').classList.remove('active');
            document.getElementById('lobby-screen').classList.add('active');
        }

        function createRoomWithBot(difficulty) {
            let n = document.getElementById('player-name').value;
            let r = document.getElementById('create-room-id').value;
            let p = document.getElementById('create-room-pass').value;
            socket.emit('create_room', { room_id: r, password: p, player_name: n, game_mode: 'bot', bot_difficulty: difficulty });
        }

        function createRoomWithMode(mode) {
            let n = document.getElementById('player-name').value;
            let r = document.getElementById('create-room-id').value;
            let p = document.getElementById('create-room-pass').value;
            socket.emit('create_room', { room_id: r, password: p, player_name: n, game_mode: mode });
        }

        socket.on('connect', () => { console.log("Connected!"); });
        socket.on('error', (data) => { alert("Error: " + data.message); });
        socket.on('alert', (data) => { alert(data.message); });

        socket.on('request_payment_choice', (data) => {
            let options = data.options;
            let remainingDue = data.remaining_due;

            showModal(`Pay Debt (${remainingDue}M Left)`, "");
            let container = document.getElementById('modal-buttons');
            container.innerHTML = "";
            options.forEach((opt) => {
                let btn = document.createElement('button');
                btn.className = "modal-btn";
                btn.innerText = `${opt.label} (${opt.value}M)`;
                btn.onclick = () => {
                    closeModal();
                    socket.emit('submit_payment_choice', { room_id: currentRoom, source: opt.source, real_idx: opt.real_idx });
                };
                container.appendChild(btn);
            });
        });

        socket.on('request_just_say_no', (data) => {
            let hasJSN = data.has_jsn;
            let msg = data.message;
            if (hasJSN) {
                let wantBlock = confirm(`${msg}\\n\\nYou hold 'Just Say No!' in your hand! Do you want to play it to block this action?`);
                socket.emit('respond_just_say_no', { room_id: currentRoom, action_id: data.action_id, block: wantBlock });
            } else {
                socket.emit('respond_just_say_no', { room_id: currentRoom, action_id: data.action_id, block: false });
            }
        });

        socket.on('game_over', (data) => {
            if (timerInterval) clearInterval(timerInterval);
            document.getElementById('done-turn-btn').style.display = 'none';
            alert("🎉 GAME OVER! Winner: " + data.winner + "\\n\\nThe game has ended.");
            location.reload();
        });

        socket.on('room_joined', (data) => {
            currentRoom = data.room_id;
            isHost = data.is_host;
            document.getElementById('mode-select-screen').classList.remove('active');
            document.getElementById('lobby-screen').classList.remove('active');
            document.getElementById('waiting-screen').classList.add('active');
            document.getElementById('display-room-id').innerText = currentRoom;
            if (isHost) document.getElementById('host-controls').style.display = 'block';
        });

        function getCardColorClass(card) {
            if (card.type === 'Money') {
                return `money-${card.value}`;
            } else if (card.type === 'Property') {
                let colClass = card.color ? card.color.replace(/ /g, '-') : 'Wild';
                return `prop-${colClass}`;
            } else if (card.type === 'Building') {
                return 'building-card';
            }
            return '';
        }

        function getActionCardTheme(cardName) {
            if (cardName === "Pass Go" || cardName.startsWith("Rent") || cardName === "Double Rent") return "card-yellow";
            if (cardName === "Sly Deal" || cardName === "Forced Deal" || cardName === "Debt Collector") return "card-green";
            if (cardName === "Deal Breaker") return "card-purple";
            if (cardName === "Just Say No!") return "card-blue";
            if (cardName === "It's My Birthday") return "card-peach";
            if (cardName === "House" || cardName === "Hotel") return "card-building";
            if (cardName === "Property Wild Card" || cardName.includes("Wild (")) return "card-wildproperty";
            return "card-yellow";
        }

        function updateTimerDisplay() {
            if (!turnDeadline) return;
            let now = Math.floor(Date.now() / 1000);
            let timeLeft = Math.max(0, Math.floor(turnDeadline - now));
            let statusElem = document.getElementById('turn-status');

            if (myTurn) {
                if (isDiscardMode) {
                    statusElem.innerText = `🗑️ DISCARD MODE - You have > 7 cards! Click cards to throw away!`;
                } else {
                    statusElem.innerText = `👉 Your Turn (${actionsLeft}/3 actions) | ⏱️ ${timeLeft}s left`;
                }
            } else {
                statusElem.innerText = `⏳ Waiting for ${currentTurnName}... | ⏱️ ${timeLeft}s left`;
            }
        }

        socket.on('update_state', (data) => {
            document.getElementById('player-list').innerHTML = data.players.map(p => `<li>👤 ${p.name}</li>`).join('');
            knownPlayers = data.players.map(p => p.name);
            latestPlayersData = data.players;
            
            let myName = document.getElementById('player-name').value.trim();
            let meObj = data.players.find(p => p.name.toLowerCase() === myName.toLowerCase());
            if (meObj) {
                myPropertiesData = meObj.properties;
            }
            
            myTurn = data.is_my_turn;
            actionsLeft = data.actions_left;
            myHandData = data.my_hand;
            isDiscardMode = data.is_discard_mode;
            turnDeadline = data.turn_deadline;
            currentTurnName = data.current_turn_name;
            
            if (timerInterval) clearInterval(timerInterval);

            if (data.started && !data.game_over) {
                document.getElementById('waiting-screen').classList.remove('active');
                document.getElementById('game-screen').classList.add('active');

                document.getElementById('turn-info').style.display = 'block';
                if (myTurn) {
                    document.getElementById('turn-info').style.background = isDiscardMode ? "#ef4444" : "#d4af37";
                    document.getElementById('done-turn-btn').style.display = isDiscardMode ? 'none' : 'block';
                } else {
                    document.getElementById('turn-info').style.background = "#222";
                    document.getElementById('turn-info').style.color = "#d4af37";
                    document.getElementById('done-turn-btn').style.display = 'none';
                }
                
                updateTimerDisplay();
                timerInterval = setInterval(updateTimerDisplay, 1000);
            }

            let oppHtml = "";
            data.players.forEach(p => {
                let bankHtml = p.bank.map(c => `<span class="board-card ${getCardColorClass(c)}">${c.name} (${c.value}M)</span>`).join('');
                
                let propGroups = {};
                p.properties.forEach((c, idx) => {
                    let col = c.color || 'Wild';
                    if (!propGroups[col]) propGroups[col] = [];
                    propGroups[col].push({ card: c, index: idx });
                });

                let sortedColors = Object.keys(propGroups).sort((a, b) => {
                    let completeA = propGroups[a].length >= (setSizes[a] || 99) ? 1 : 0;
                    let completeB = propGroups[b].length >= (setSizes[b] || 99) ? 1 : 0;
                    return completeB - completeA;
                });

                let propHtml = sortedColors.map(col => {
                    let cardsList = propGroups[col].map(item => 
                        `<div style="margin: 2px 0;"><span class="board-card ${getCardColorClass(item.card)}">[${item.index}] ${item.card.name} (${item.card.value}M)</span></div>`
                    ).join('');
                    
                    let bldgs = (p.buildings[col] || []).map(b => `<div style="margin: 2px 0;"><span class="board-card building-card">🏠 ${b.name} (${b.value}M)</span></div>`).join('');
                    
                    let required = setSizes[col] || 99;
                    let isComplete = propGroups[col].length >= required;
                    let completeBadge = isComplete ? ' <br><span style="color: #22c55e; font-weight: bold; font-size: 10px;">(COMPLETE!)</span>' : '';

                    return `<div class="set-column">
                                <div style="font-size: 12px; font-weight: bold; margin-bottom: 4px; color: #d4af37;">${col}${completeBadge}</div>
                                ${cardsList} ${bldgs}
                            </div>`;
                }).join('');
                
                let activeStyle = p.is_turn ? "border: 2px solid #d4af37; background: rgba(212, 175, 55, 0.1);" : "border-bottom: 1px solid rgba(255,255,255,0.1);";
                
                let isYou = (myName && p.name.toLowerCase() === myName.toLowerCase());
                let titleLabel = isYou ? `⭐ You (${p.name})` : `👤 ${p.name}`;

                oppHtml += `
                    <div style="padding: 12px; margin-bottom: 12px; border-radius: 8px; ${activeStyle}">
                        <strong>${titleLabel}</strong> (Cards: ${p.card_count})<br>
                        💰 <strong>Bank:</strong> ${p.bank_total}M <br> ${bankHtml || "<i>Empty</i>"}<br>
                        🏠 <strong>Properties:</strong>
                        <div class="sets-container">${propHtml || "<i>Empty</i>"}</div>
                    </div>`;
            });
            document.getElementById('opponents-area').innerHTML = oppHtml;

            let handHtml = "";
            let baseCardClass = (myTurn) ? "card" : "card disabled-card";
            
            data.my_hand.forEach((c, idx) => {
                let colorClass = getCardColorClass(c);
                let themeClass = (c.type === 'Action' || c.type === 'Building' || c.name === 'Property Wild Card' || c.name.includes("Wild (")) ? getActionCardTheme(c.name) : colorClass;
                let discardStyle = isDiscardMode ? " discard-mode" : "";
                handHtml += `
                    <div class="${baseCardClass} ${themeClass}${discardStyle}" onclick="handleCardClick(${idx})" id="card-${idx}">
                        <strong>${c.name}</strong><br><br>
                        Value: ${c.value}M<br>
                        <small style="opacity: 0.9;">${c.type}</small>
                    </div>`;
            });
            document.getElementById('my-hand').innerHTML = handHtml;
        });

        function joinRoom() {
            let n = document.getElementById('player-name').value, r = document.getElementById('join-room-id').value, p = document.getElementById('join-room-pass').value;
            if(n && r && p) socket.emit('join_room', { room_id: r, password: p, player_name: n });
            else alert("Fill all Join details!");
        }

        function handleCardClick(idx) { 
            if (!myTurn) { alert("Please wait for your turn!"); return; }
            
            if (isDiscardMode) {
                socket.emit('discard_card', { room_id: currentRoom, card_index: idx });
                return;
            }

            if (actionsLeft <= 0) { alert("You have used all 3 actions! Click '✓ Done' to end your turn."); return; }
            
            let card = myHandData[idx];
            let useType = "";
            let extraData = {};

            if (card.type === "Property") {
                if (card.name === "Property Wild Card" || card.name.includes("&")) {
                    handleWildPropertyPlacement(idx, "property", card.name);
                } else {
                    useType = "property";
                    socket.emit('play_card', { room_id: currentRoom, card_index: idx, use_type: useType, extra_data: extraData });
                }
            } else if (card.type === "Money") {
                useType = "bank";
                socket.emit('play_card', { room_id: currentRoom, card_index: idx, use_type: useType, extra_data: extraData });
            } else if (card.type === "Building") {
                let colorGroup = prompt("Enter Color Group of your completed set (e.g., Light Blue, Red):");
                if (!colorGroup) return;
                useType = "building";
                extraData = { color_group: toTitleCase(colorGroup.trim()) };
                socket.emit('play_card', { room_id: currentRoom, card_index: idx, use_type: useType, extra_data: extraData });
            } else if (card.type === "Action") {
                let cardChoice = prompt(`What do you want to do with '${card.name}'?\n\nType '1' = Play as Action\nType '2' = Deposit to Bank (${card.value}M)`, "1");
                if (cardChoice === "2") {
                    useType = "bank";
                    socket.emit('play_card', { room_id: currentRoom, card_index: idx, use_type: useType, extra_data: extraData });
                    return;
                } else if (cardChoice !== "1") {
                    return;
                }

                useType = "action";
                if (card.name === "Sly Deal") {
                    startSlyDeal(idx, useType);
                }
                else if (card.name === "Forced Deal") {
                    startForcedDeal(idx, useType);
                }
                else if (card.name === "Deal Breaker") {
                    startDealBreaker(idx, useType);
                }
                else if (card.name.startsWith("Rent")) {
                    startRentAction(idx, useType, card.name);
                }
                else if (card.name === "Debt Collector") {
                    showOpponentModal("Debt Collector", (targetOp) => {
                        extraData = { target_name: targetOp.name.trim() };
                        socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                    });
                }
                else if (card.name === "It's My Birthday") {
                    socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                }
                else {
                    socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
                }
            }
        }

        function endTurn() {
            socket.emit('end_turn', { room_id: currentRoom });
        }

        function startGame() { socket.emit('start_game', { room_id: currentRoom }); }
    </script>
</body>
</html>
"""

# ==========================================
# 2. PYTHON BACKEND (ROBUST COLOR & TURN LOGIC)
# ==========================================
SET_SIZES = {
    'Brown': 2, 'Light Blue': 3, 'Pink': 3, 'Orange': 3,
    'Red': 3, 'Yellow': 3, 'Green': 3, 'Dark Blue': 2,
    'Railroad': 4, 'Utility': 2
}

RENT_TABLE = {
    'Brown': [1, 2],
    'Light Blue': [1, 2, 3],
    'Pink': [1, 2, 4],
    'Orange': [1, 3, 5],
    'Red': [2, 3, 6],
    'Yellow': [2, 4, 8],
    'Green': [2, 4, 7],
    'Dark Blue': [3, 8],
    'Railroad': [1, 2, 3, 4],
    'Utility': [1, 2]
}

def normalize_color(color_str):
    if not color_str:
        return 'Wild'
    cleaned = color_str.strip().title()
    for valid_col in SET_SIZES.keys():
        if valid_col.lower() == cleaned.lower():
            return valid_col
    return cleaned

class Card:
    def __init__(self, card_type, name, value, color=None):
        self.card_type = card_type
        self.name = name
        self.value = value
        self.color = normalize_color(color) if color else None

    def to_dict(self):
        return {"type": self.card_type, "name": self.name, "value": self.value, "color": self.color}

def create_deck():
    deck = []
    for _ in range(6): deck.append(Card('Money', '1M Money', 1))
    for _ in range(5): deck.append(Card('Money', '2M Money', 2))
    for _ in range(3): deck.append(Card('Money', '3M Money', 3))
    for _ in range(3): deck.append(Card('Money', '4M Money', 4))
    for _ in range(2): deck.append(Card('Money', '5M Money', 5))
    for _ in range(1): deck.append(Card('Money', '10M Money', 10))
    
    properties_data = [
        ('Brown', 1, 2),
        ('Light Blue', 1, 3),
        ('Pink', 2, 3),
        ('Orange', 2, 3),
        ('Red', 3, 3),
        ('Yellow', 3, 3),
        ('Green', 4, 3),
        ('Dark Blue', 4, 2),
        ('Railroad', 2, 4),
        ('Utility', 2, 2)
    ]
    for color, value, count in properties_data:
        for _ in range(count):
            card_name = f"{color} Property"
            deck.append(Card('Property', card_name, value, color))
            
    for _ in range(2):
        deck.append(Card('Property', 'Property Wild Card', 0, None))

    dual_wilds = [
        ("Brown & Light Blue Wild", 1),
        ("Pink & Orange Wild", 2),
        ("Red & Yellow Wild", 3),
        ("Green & Dark Blue Wild", 4),
        ("Railroad & Utility Wild", 2)
    ]
    for wild_name, val in dual_wilds:
        deck.append(Card('Property', wild_name, val, None))
            
    for _ in range(3): deck.append(Card('Building', 'House', 3))
    for _ in range(2): deck.append(Card('Building', 'Hotel', 4))

    actions = [
        ("Pass Go", 1, 10),
        ("Sly Deal", 3, 3), 
        ("Forced Deal", 3, 3), 
        ("Deal Breaker", 5, 2),
        ("Debt Collector", 5, 3), 
        ("It's My Birthday", 2, 3),
        ("Rent (Brown & Light Blue)", 1, 2),
        ("Rent (Pink & Orange)", 1, 2),
        ("Rent (Red & Yellow)", 1, 2),
        ("Rent (Green & Dark Blue)", 1, 2),
        ("Rent (Railroad & Utility)", 1, 2),
        ("Rent (Wild All Colors)", 3, 3), 
        ("Double Rent", 1, 2),
        ("Just Say No!", 4, 3)
    ] 
    for name, value, count in actions:
        for _ in range(count):
            deck.append(Card('Action', name, value))
            
    random.shuffle(deck)
    return deck

rooms = {} 

class GameRoom:
    def __init__(self, room_id, password, game_mode='multiplayer', bot_difficulty='normal'):
        self.room_id = room_id
        self.password = password
        self.game_mode = game_mode
        self.bot_difficulty = bot_difficulty
        self.players = {} 
        self.turn_order = []
        self.current_turn_index = 0
        self.actions_left = 3
        self.deck = create_deck()
        self.discard_pile = []
        self.started = False
        self.game_over = False
        self.turn_deadline = 0
        self.pending_actions = {}
        self.pending_payments = {}
        self.is_discard_phase = False

    def add_player(self, sid, name):
        self.players[sid] = {"name": name, "hand": [], "bank": [], "properties": [], "buildings": {}, "is_ai": False}
        self.turn_order.append(sid)
        
        if self.game_mode == 'bot' and len(self.players) == 1:
            bot_sid = "ai_bot_sid"
            self.players[bot_sid] = {"name": f"Bot (Extreme Pro) 🤖", "hand": [], "bank": [], "properties": [], "buildings": {}, "is_ai": True}
            self.turn_order.append(bot_sid)

    def draw_cards(self, sid, count):
        for _ in range(count):
            if not self.deck and self.discard_pile:
                self.deck = self.discard_pile.copy()
                self.discard_pile.clear()
                random.shuffle(self.deck)
            if self.deck:
                self.players[sid]["hand"].append(self.deck.pop().to_dict())

    def deal_initial_cards(self):
        for sid in self.players:
            self.draw_cards(sid, 5)
        self.started = True
        self.current_turn_index = 0
        self.start_turn()

    def start_turn(self):
        if self.game_over:
            return
        self.actions_left = 3
        self.is_discard_phase = False
        current_sid = self.turn_order[self.current_turn_index]
        player = self.players[current_sid]
        
        if len(player["hand"]) == 0:
            self.draw_cards(current_sid, 5)
        else:
            self.draw_cards(current_sid, 2)
            
        self.turn_deadline = time.time() + 60
        
        if player.get("is_ai"):
            socketio.start_background_task(self.run_bot_turn)

    def run_bot_turn(self):
        socketio.sleep(1.2)
        if self.game_over or not self.started:
            return
        bot_sid = self.turn_order[self.current_turn_index]
        if bot_sid not in self.players or not self.players[bot_sid].get("is_ai"):
            return
        
        bot = self.players[bot_sid]
        human_sid = next((s for s in self.turn_order if s != bot_sid), None)
        human_player = self.players.get(human_sid)

        if self.bot_difficulty == 'easy':
            while self.actions_left > 0 and bot["hand"]:
                card = bot["hand"].pop(0)
                if card["type"] == "Money":
                    bot["bank"].append(card)
                elif card["type"] == "Property":
                    bot["properties"].append(card)
                else:
                    self.discard_pile.append(card)
                self.actions_left -= 1
                socketio.sleep(0.5)

        elif self.bot_difficulty == 'normal':
            while self.actions_left > 0 and bot["hand"]:
                prop_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Property"), -1)
                money_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Money"), -1)
                
                if prop_idx != -1:
                    card = bot["hand"].pop(prop_idx)
                    bot["properties"].append(card)
                elif money_idx != -1:
                    card = bot["hand"].pop(money_idx)
                    bot["bank"].append(card)
                else:
                    card = bot["hand"].pop(0)
                    self.discard_pile.append(card)
                self.actions_left -= 1
                socketio.sleep(0.5)

        elif self.bot_difficulty == 'hard':
            while self.actions_left > 0 and bot["hand"]:
                action_played = False
                
                db_idx = next((i for i, c in enumerate(bot["hand"]) if c["name"] == "Deal Breaker"), -1)
                if db_idx != -1 and human_player:
                    human_counts = {}
                    for p in human_player["properties"]:
                        col = normalize_color(p.get('color'))
                        human_counts[col] = human_counts.get(col, 0) + 1
                    
                    complete_col = next((col for col, cnt in human_counts.items() if cnt >= SET_SIZES.get(col, 99)), None)
                    if complete_col:
                        card = bot["hand"].pop(db_idx)
                        self.discard_pile.append(card)
                        
                        def execute_extreme_db():
                            to_steal = [p for p in human_player["properties"] if normalize_color(p.get('color')) == complete_col]
                            for p in to_steal:
                                human_player["properties"].remove(p)
                                bot["properties"].append(p)
                            socketio.emit('alert', {'message': f"🔥 Extreme Bot snatched your complete {complete_col} set with Deal Breaker!"}, room=self.room_id)

                        trigger_action_with_jsn(self, bot_sid, [human_sid], "Deal Breaker", execute_extreme_db)
                        action_played = True

                if not action_played:
                    sly_idx = next((i for i, c in enumerate(bot["hand"]) if c["name"] == "Sly Deal"), -1)
                    if sly_idx != -1 and human_player and human_player["properties"]:
                        card = bot["hand"].pop(sly_idx)
                        self.discard_pile.append(card)
                        
                        def execute_extreme_sly():
                            stolen = human_player["properties"].pop(0)
                            bot["properties"].append(stolen)
                            socketio.emit('alert', {'message': f"🔥 Extreme Bot used Sly Deal to steal your {stolen['name']}!"}, room=self.room_id)

                        trigger_action_with_jsn(self, bot_sid, [human_sid], "Sly Deal", execute_extreme_sly)
                        action_played = True

                if not action_played:
                    bot_colors = [normalize_color(p.get('color')) for p in bot["properties"] if p.get('color')]
                    rent_idx = -1
                    matched_col = None
                    
                    if bot_colors:
                        for i, c in enumerate(bot["hand"]):
                            if "Rent" in c["name"]:
                                c_lower = c["name"].lower()
                                match = next((col for col in bot_colors if col.lower() in c_lower or "wild all colors" in c_lower), None)
                                if match:
                                    rent_idx = i
                                    matched_col = match
                                    break
                    
                    if rent_idx != -1 and matched_col:
                        card = bot["hand"].pop(rent_idx)
                        self.discard_pile.append(card)
                        
                        tier = RENT_TABLE.get(matched_col, [1])
                        count = sum(1 for p in bot["properties"] if normalize_color(p.get('color')) == matched_col)
                        amt = tier[min(count-1, len(tier)-1)]
                        process_payment(human_sid, human_player, bot, amt, self)
                        socketio.emit('alert', {'message': f"🔥 Extreme Bot charged you {amt}M rent on {matched_col}!"}, room=self.room_id)
                        action_played = True

                if not action_played:
                    prop_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Property"), -1)
                    money_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Money" or c["type"] == "Action"), -1)

                    if prop_idx != -1:
                        card = bot["hand"].pop(prop_idx)
                        if card['name'] == 'Property Wild Card' or "&" in card['name']:
                            card['color'] = 'Brown'
                            card['name'] = 'Wild (Brown)'
                        bot["properties"].append(card)
                    elif money_idx != -1:
                        card = bot["hand"].pop(money_idx)
                        bot["bank"].append(card)
                    else:
                        card = bot["hand"].pop(0)
                        self.discard_pile.append(card)

                self.actions_left -= 1
                socketio.sleep(0.5)

        while len(bot["hand"]) > 7:
            discarded = bot["hand"].pop()
            self.discard_pile.append(discarded)

        if self.check_win(bot_sid):
            self.game_over = True
            socketio.emit('game_over', {'winner': bot['name']}, room=self.room_id)
            broadcast_room_state(self.room_id)
            return
            
        self.next_turn()
        broadcast_room_state(self.room_id)

    def next_turn(self):
        if self.game_over:
            return
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        self.start_turn()

    def check_win(self, sid):
        player = self.players[sid]
        color_counts = {}
        for p in player["properties"]:
            col = normalize_color(p.get("color"))
            if col != 'Wild':
                color_counts[col] = color_counts.get(col, 0) + 1
        
        full_sets = 0
        for color, count in color_counts.items():
            if count >= SET_SIZES.get(color, 99):
                full_sets += 1
                
        return full_sets >= 3

def check_and_demolish_buildings(player):
    for color, bldgs in list(player["buildings"].items()):
        if not bldgs:
            continue
        current_count = sum(1 for p in player["properties"] if normalize_color(p.get("color")) == color)
        req_size = SET_SIZES.get(color, 99)
        if current_count < req_size:
            player["bank"].extend(bldgs)
            player["buildings"][color] = []

def process_payment(debtor_sid, debtor_player, creditor_player, amount_due, room):
    remaining_due = amount_due
    
    while remaining_due > 0 and (debtor_player["bank"] or debtor_player["properties"]):
        if debtor_player.get("is_ai"):
            paid_value = 0
            while debtor_player["bank"] and paid_value < remaining_due:
                card = debtor_player["bank"].pop(0)
                creditor_player["bank"].append(card)
                paid_value += card['value']
            
            while debtor_player["properties"] and paid_value < remaining_due:
                card = debtor_player["properties"].pop(0)
                creditor_player["properties"].append(card)
                paid_value += card['value']
                check_and_demolish_buildings(debtor_player)

            change = paid_value - remaining_due
            if change > 0:
                creditor_player["bank"].append({'type': 'Money', 'name': f'{change}M Money', 'value': change, 'color': None})
            break

        options = []
        for i, b in enumerate(debtor_player["bank"]):
            options.append({'source': 'bank', 'real_idx': i, 'label': f"Bank: {b['name']}", 'value': b['value']})
        for i, p in enumerate(debtor_player["properties"]):
            options.append({'source': 'prop', 'real_idx': i, 'label': f"Property: {p['name']}", 'value': p['value']})

        if not options:
            break

        payment_id = str(random.randint(10000, 99999))
        room.pending_payments[debtor_sid] = {
            'payment_id': payment_id,
            'debtor_player': debtor_player,
            'creditor_player': creditor_player,
            'remaining_due': remaining_due,
            'total_paid': 0
        }

        socketio.emit('request_payment_choice', {
            'payment_id': payment_id,
            'remaining_due': remaining_due,
            'options': options
        }, room=debtor_sid)
        break

@socketio.on('submit_payment_choice')
def handle_payment_choice(data):
    room_id = data['room_id']
    source = data['source']
    real_idx = data['real_idx']
    sid = request.sid

    if room_id in rooms:
        room = rooms[room_id]
        if sid in room.pending_payments:
            pay_info = room.pending_payments[sid]
            debtor = pay_info['debtor_player']
            creditor = pay_info['creditor_player']
            
            card_value = 0
            if source == 'bank' and 0 <= real_idx < len(debtor["bank"]):
                card = debtor["bank"].pop(real_idx)
                creditor["bank"].append(card)
                card_value = card['value']
            elif source == 'prop' and 0 <= real_idx < len(debtor["properties"]):
                card = debtor["properties"].pop(real_idx)
                creditor["properties"].append(card)
                card_value = card['value']
                check_and_demolish_buildings(debtor)

            pay_info['total_paid'] += card_value
            pay_info['remaining_due'] -= card_value

            if pay_info['remaining_due'] > 0 and (debtor["bank"] or debtor["properties"]):
                process_payment(sid, debtor, creditor, pay_info['remaining_due'], room)
            else:
                if pay_info['remaining_due'] < 0:
                    change_amount = abs(pay_info['remaining_due'])
                    creditor["bank"].append({'type': 'Money', 'name': f'{change_amount}M Money', 'value': change_amount, 'color': None})
                    socketio.emit('alert', {'message': f"Returned {change_amount}M change to {debtor['name']}!"}, room=room_id)

                del room.pending_payments[sid]
                broadcast_room_state(room_id)

def trigger_action_with_jsn(room, attacker_sid, target_sids, action_name, execute_callback):
    action_id = str(random.randint(10000, 99999))
    valid_targets = []
    for tsid in target_sids:
        t_player = room.players[tsid]
        if t_player.get("is_ai"):
            continue
        has_jsn = any(c['name'] == "Just Say No!" for c in t_player["hand"])
        if has_jsn:
            valid_targets.append(tsid)

    room.pending_actions[action_id] = {
        'attacker': attacker_sid,
        'targets': valid_targets,
        'name': action_name,
        'callback': execute_callback,
        'blocked': False,
        'current_target_idx': 0
    }
    
    ask_next_jsn(room, action_id)

def ask_next_jsn(room, action_id):
    act = room.pending_actions[action_id]
    targets = act['targets']
    idx = act['current_target_idx']
    
    if idx >= len(targets):
        if not act['blocked']:
            act['callback']()
        if action_id in room.pending_actions:
            del room.pending_actions[action_id]
        broadcast_room_state(room.room_id)
        return

    tsid = targets[idx]
    t_player = room.players[tsid]
    
    has_jsn = any(c['name'] == "Just Say No!" for c in t_player["hand"])
    if not has_jsn:
        act['current_target_idx'] += 1
        ask_next_jsn(room, action_id)
        return

    socketio.emit('request_just_say_no', {
        'action_id': action_id,
        'has_jsn': has_jsn,
        'message': f"{room.players[act['attacker']]['name']} played {act['name']} against you!"
    }, room=tsid)

@socketio.on('respond_just_say_no')
def handle_jsn_response(data):
    room_id = data['room_id']
    action_id = data['action_id']
    block = data['block']
    sid = request.sid
    
    if room_id in rooms:
        room = rooms[room_id]
        if action_id in room.pending_actions:
            act = room.pending_actions[action_id]
            if block:
                player = room.players[sid]
                jsn_idx = next((i for i, c in enumerate(player["hand"]) if c['name'] == "Just Say No!"), -1)
                if jsn_idx != -1:
                    jsn_card = player["hand"].pop(jsn_idx)
                    room.discard_pile.append(jsn_card)
                    act['blocked'] = not act['blocked']
                    socketio.emit('alert', {'message': f"{player['name']} played 'Just Say No!' counter-action!"}, room=room_id)
            
            act['current_target_idx'] += 1
            ask_next_jsn(room, action_id)

def background_turn_timer():
    while True:
        socketio.sleep(1)
        now = time.time()
        for room_id, room in list(rooms.items()):
            if room.started and not room.game_over and room.turn_deadline > 0:
                if now >= room.turn_deadline:
                    current_sid = room.turn_order[room.current_turn_index]
                    player = room.players.get(current_sid)
                    if player:
                        if player.get("is_ai"):
                            room.next_turn()
                            broadcast_room_state(room_id)
                            continue

                        while len(player["hand"]) > 7:
                            discarded = player["hand"].pop()
                            room.discard_pile.append(discarded)
                        room.next_turn()
                        broadcast_room_state(room_id)

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@socketio.on('create_room')
def handle_create_room(data):
    room_id = data['room_id']
    if room_id in rooms:
        emit('error', {'message': 'Room ID already exists!'})
        return
    game_mode = data.get('game_mode', 'multiplayer')
    bot_difficulty = data.get('bot_difficulty', 'normal')
    rooms[room_id] = GameRoom(room_id, data['password'], game_mode=game_mode, bot_difficulty=bot_difficulty)
    rooms[room_id].add_player(request.sid, data['player_name'])
    join_room(room_id)
    emit('room_joined', {'room_id': room_id, 'is_host': True})
    
    if game_mode == 'bot':
        rooms[room_id].deal_initial_cards()
        socketio.emit('game_started', room=room_id)
        
    broadcast_room_state(room_id)

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id']
    if room_id not in rooms or rooms[room_id].password != data['password']:
        emit('error', {'message': 'Invalid Room ID or Password!'})
        return
    
    room = rooms[room_id]
    if room.started or room.game_over:
        emit('error', {'message': 'Cannot join! Game has already started or ended.'})
        return

    room.add_player(request.sid, data['player_name'])
    join_room(room_id)
    emit('room_joined', {'room_id': room_id, 'is_host': False})
    broadcast_room_state(room_id)

@socketio.on('start_game')
def handle_start_game(data):
    room_id = data['room_id']
    if room_id in rooms:
        rooms[room_id].deal_initial_cards()
        socketio.emit('game_started', room=room_id)
        broadcast_room_state(room_id)

@socketio.on('play_card')
def handle_play_card(data):
    room_id = data['room_id']
    card_index = data['card_index']
    use_type = data['use_type'] 
    extra_data = data.get('extra_data', {})
    sid = request.sid
    
    if room_id in rooms and sid in rooms[room_id].players:
        room = rooms[room_id]
        if room.game_over:
            return
        
        if sid == room.turn_order[room.current_turn_index]:
            if room.is_discard_phase:
                emit('alert', {'message': 'You must discard excess cards from your hand first!'}, room=sid)
                return

            if room.actions_left > 0:
                player = room.players[sid]
                if 0 <= card_index < len(player["hand"]):
                    played_card = player["hand"].pop(card_index)
                    
                    if use_type == 'bank':
                        player["bank"].append(played_card)
                    elif use_type == 'property':
                        if played_card['name'] == 'Property Wild Card' or "&" in played_card['name']:
                            assigned_color = normalize_color(extra_data.get('assigned_color', 'Wild'))
                            played_card['color'] = assigned_color
                            played_card['name'] = f"Wild ({assigned_color})"
                        else:
                            played_card['color'] = normalize_color(played_card.get('color'))
                        player["properties"].append(played_card)
                    elif use_type == 'building':
                        color_group = normalize_color(extra_data.get('color_group', ''))
                        current_props = [p for p in player["properties"] if normalize_color(p.get("color")) == color_group]
                        current_count = len(current_props)
                        req_size = SET_SIZES.get(color_group, 99)
                        
                        if current_count >= req_size and color_group not in ['Railroad', 'Utility']:
                            if color_group not in player["buildings"]:
                                player["buildings"][color_group] = []
                            
                            bldgs = player["buildings"][color_group]
                            has_house = any(b['name'] == 'House' for b in bldgs)
                            has_hotel = any(b['name'] == 'Hotel' for b in bldgs)
                            
                            if played_card['name'] == 'House':
                                if has_house:
                                    emit('alert', {'message': "Maximum 1 House per set!"}, room=sid)
                                    player["hand"].append(played_card)
                                    return
                                bldgs.append(played_card)
                                emit('alert', {'message': f"Added House to {color_group}!"}, room=sid)
                            elif played_card['name'] == 'Hotel':
                                if not has_house or has_hotel:
                                    emit('alert', {'message': "Requires a House first, and max 1 Hotel per set!"}, room=sid)
                                    player["hand"].append(played_card)
                                    return
                                bldgs.append(played_card)
                                emit('alert', {'message': f"Added Hotel to {color_group}!"}, room=sid)
                        else:
                            emit('alert', {'message': "Must have complete set to build!"}, room=sid)
                            player["hand"].append(played_card)
                            return

                    elif use_type == 'action':
                        room.discard_pile.append(played_card)
                        
                        if played_card['name'] == "Pass Go":
                            room.draw_cards(sid, 2)
                        
                        elif played_card['name'] == "Sly Deal":
                            target_name = extra_data.get('target_name')
                            target_prop_idx = extra_data.get('target_prop_idx')
                            target_sid = next((tsid for tsid, pdata in room.players.items() if pdata['name'].lower() == str(target_name).lower() and tsid != sid), None)
                            
                            if target_sid:
                                def execute_sly():
                                    target_props = room.players[target_sid]["properties"]
                                    color_counts = {}
                                    for p in target_props:
                                        col = normalize_color(p.get('color'))
                                        color_counts[col] = color_counts.get(col, 0) + 1
                                    
                                    if 0 <= target_prop_idx < len(target_props):
                                        target_prop = target_props[target_prop_idx]
                                        t_col = normalize_color(target_prop.get('color'))
                                        if color_counts.get(t_col, 0) >= SET_SIZES.get(t_col, 99):
                                            emit('alert', {'message': "Sly Deal cannot steal from a complete set!"}, room=sid)
                                            return
                                        stolen = target_props.pop(target_prop_idx)
                                        player["properties"].append(stolen)
                                        check_and_demolish_buildings(room.players[target_sid])
                                        emit('alert', {'message': f"Stole {stolen['name']} successfully!"}, room=sid)
                                    else:
                                        emit('alert', {'message': "Invalid property index!"}, room=sid)
                                
                                all_other_sids = [s for s in room.players if s != sid]
                                trigger_action_with_jsn(room, sid, all_other_sids, "Sly Deal", execute_sly)
                            else:
                                emit('alert', {'message': "Target not found!"}, room=sid)

                        elif played_card['name'] == "Forced Deal":
                            my_prop_idx = extra_data.get('my_prop_idx')
                            target_name = extra_data.get('target_name')
                            target_prop_idx = extra_data.get('target_prop_idx')
                            target_sid = next((tsid for tsid, pdata in room.players.items() if pdata['name'].lower() == str(target_name).lower() and tsid != sid), None)
                            
                            if target_sid:
                                def execute_forced():
                                    my_props = player["properties"]
                                    target_props = room.players[target_sid]["properties"]
                                    
                                    my_color_counts = {}
                                    for p in my_props:
                                        col = normalize_color(p.get('color'))
                                        my_color_counts[col] = my_color_counts.get(col, 0) + 1
                                    
                                    target_color_counts = {}
                                    for p in target_props:
                                        col = normalize_color(p.get('color'))
                                        target_color_counts[col] = target_color_counts.get(col, 0) + 1

                                    if 0 <= my_prop_idx < len(my_props) and 0 <= target_prop_idx < len(target_props):
                                        my_card = my_props[my_prop_idx]
                                        their_card = target_props[target_prop_idx]
                                        
                                        my_col = normalize_color(my_card.get('color'))
                                        their_col = normalize_color(their_card.get('color'))

                                        if my_color_counts.get(my_col, 0) >= SET_SIZES.get(my_col, 99) or target_color_counts.get(their_col, 0) >= SET_SIZES.get(their_col, 99):
                                            emit('alert', {'message': "Forced Deal cannot involve properties from a complete set!"}, room=sid)
                                            return

                                        my_card_popped = my_props.pop(my_prop_idx)
                                        their_card_popped = target_props.pop(target_prop_idx)
                                        my_props.append(their_card_popped)
                                        target_props.append(my_card_popped)
                                        check_and_demolish_buildings(player)
                                        check_and_demolish_buildings(room.players[target_sid])
                                        emit('alert', {'message': "Forced deal completed successfully!"}, room=sid)
                                    else:
                                        emit('alert', {'message': "Invalid property index for trade!"}, room=sid)
                                
                                all_other_sids = [s for s in room.players if s != sid]
                                trigger_action_with_jsn(room, sid, all_other_sids, "Forced Deal", execute_forced)
                            else:
                                emit('alert', {'message': "Target player not found for Forced Deal!"}, room=sid)

                        elif played_card['name'] == "Deal Breaker":
                            target_name = extra_data.get('target_name')
                            color_group = normalize_color(extra_data.get('color_group', ''))
                            target_sid = next((tsid for tsid, pdata in room.players.items() if pdata['name'].lower() == str(target_name).lower() and tsid != sid), None)
                            
                            if target_sid:
                                def execute_db():
                                    target_player = room.players[target_sid]
                                    target_props_in_color = [p for p in target_player["properties"] if normalize_color(p.get("color")) == color_group]
                                    if len(target_props_in_color) >= SET_SIZES.get(color_group, 99):
                                        for p in target_props_in_color:
                                            target_player["properties"].remove(p)
                                            player["properties"].append(p)
                                        if color_group in target_player["buildings"]:
                                            if color_group not in player["buildings"]:
                                                player["buildings"][color_group] = []
                                            player["buildings"][color_group].extend(target_player["buildings"][color_group])
                                            target_player["buildings"][color_group] = []
                                        emit('alert', {'message': f"Stole complete {color_group} set successfully!"}, room=sid)
                                    else:
                                        emit('alert', {'message': f"{target_name} does not have a complete {color_group} set!"}, room=sid)
                                
                                all_other_sids = [s for s in room.players if s != sid]
                                trigger_action_with_jsn(room, sid, all_other_sids, "Deal Breaker", execute_db)
                            else:
                                emit('alert', {'message': "Target player not found for Deal Breaker!"}, room=sid)

                        elif played_card['name'] == "Debt Collector":
                            target_name = extra_data.get('target_name', '').strip()
                            target_sid = next((tsid for tsid, pdata in room.players.items() if pdata['name'].lower() == str(target_name).lower() and tsid != sid), None)
                            
                            if target_sid:
                                def execute_dc():
                                    debtor = room.players[target_sid]
                                    process_payment(target_sid, debtor, player, 5, room)
                                    emit('alert', {'message': "Collected 5M debt successfully!"}, room=sid)
                                trigger_action_with_jsn(room, sid, [target_sid], "Debt Collector", execute_dc)
                            else:
                                emit('alert', {'message': "Target player not found for Debt Collector!"}, room=sid)

                        elif played_card['name'] == "It's My Birthday":
                            all_opponents = [tsid for tsid in room.players if tsid != sid]
                            def execute_birthday():
                                for tsid in all_opponents:
                                    debtor = room.players[tsid]
                                    process_payment(tsid, debtor, player, 2, room)
                                emit('alert', {'message': "Collected 2M birthday gift from all players successfully!"}, room=sid)
                            trigger_action_with_jsn(room, sid, all_opponents, "It's My Birthday", execute_birthday)

                        elif "Rent" in played_card['name']:
                            raw_rent_color = extra_data.get('rent_color', '').strip()
                            target_name = extra_data.get('target_name', '').strip()
                            rent_color = normalize_color(raw_rent_color)

                            double_rent_requested = extra_data.get('double_rent', False)
                            multiplier = 1
                            if double_rent_requested:
                                dr_idx = next((i for i, c in enumerate(player["hand"]) if c['name'] == "Double Rent"), -1)
                                if dr_idx != -1:
                                    dr_card = player["hand"].pop(dr_idx)
                                    room.discard_pile.append(dr_card)
                                    multiplier = 2
                                else:
                                    emit('alert', {'message': "You do not have a Double Rent card in your hand! Standard rent applied."}, room=sid)

                            owned_count = sum(1 for p in player["properties"] if normalize_color(p.get("color")) == rent_color)
                            
                            if owned_count > 0:
                                tier_list = RENT_TABLE.get(rent_color, [1])
                                level_index = min(owned_count - 1, len(tier_list) - 1)
                                rent_amount = tier_list[max(0, level_index)] * multiplier
                                
                                if rent_color in player["buildings"]:
                                    for b in player["buildings"][rent_color]:
                                        if b['name'] == 'House': rent_amount += 3 * multiplier
                                        elif b['name'] == 'Hotel': rent_amount += 4 * multiplier

                                targets = [tsid for tsid, pdata in room.players.items() if pdata['name'].lower() == target_name.lower() and tsid != sid] if target_name else [tsid for tsid in room.players if tsid != sid]
                                
                                def execute_rent():
                                    for tsid in targets:
                                        debtor = room.players[tsid]
                                        process_payment(tsid, debtor, player, rent_amount, room)
                                    emit('alert', {'message': f"Charged {rent_amount}M rent successfully!"}, room=sid)
                                
                                trigger_action_with_jsn(room, sid, targets, "Rent Card", execute_rent)
                            else:
                                emit('alert', {'message': f"You do not own any properties in the {rent_color} set to charge rent!"}, room=sid)

                room.actions_left -= 1
                if len(player["hand"]) == 0:
                    room.draw_cards(sid, 5)

                if room.check_win(sid):
                    room.game_over = True
                    socketio.emit('game_over', {'winner': player['name']}, room=room_id)
                    broadcast_room_state(room_id)
                    return

                if room.actions_left <= 0:
                    if len(player["hand"]) > 7:
                        room.is_discard_phase = True
                        emit('alert', {'message': 'You have more than 7 cards! Please discard down to 7.'}, room=sid)
                    else:
                        room.next_turn()
                        
                broadcast_room_state(room_id)

@socketio.on('discard_card')
def handle_discard(data):
    room_id = data['room_id']
    card_index = data['card_index']
    sid = request.sid
    if room_id in rooms and sid in rooms[room_id].players:
        room = rooms[room_id]
        if room.game_over: return
        if sid == room.turn_order[room.current_turn_index]:
            player = room.players[sid]
            if 0 <= card_index < len(player["hand"]):
                discarded = player["hand"].pop(card_index)
                room.discard_pile.append(discarded)
                
                if len(player["hand"]) <= 7:
                    room.is_discard_phase = False
                    room.next_turn()
                
                broadcast_room_state(room_id)

@socketio.on('end_turn')
def handle_end_turn(data):
    room_id = data['room_id']
    sid = request.sid
    if room_id in rooms:
        room = rooms[room_id]
        if room.game_over: return
        if sid == room.turn_order[room.current_turn_index]:
            player = room.players[sid]
            room.is_discard_phase = False
            if len(player["hand"]) > 7:
                room.is_discard_phase = True
                emit('alert', {'message': 'You have more than 7 cards! You must discard down to 7 before ending turn.'}, room=sid)
                broadcast_room_state(room_id)
            else:
                room.next_turn()
                broadcast_room_state(room_id)

def broadcast_room_state(room_id):
    if room_id not in rooms: return
    room = rooms[room_id]
    current_turn_sid = room.turn_order[room.current_turn_index] if (room.started and not room.game_over) else None

    public_players = []
    for sid, p_data in room.players.items():
        bank_total = sum(c['value'] for c in p_data["bank"])
        public_players.append({
            "name": p_data["name"], "card_count": len(p_data["hand"]), 
            "bank": p_data["bank"], "bank_total": bank_total,
            "properties": p_data["properties"], "buildings": p_data["buildings"],
            "is_turn": sid == current_turn_sid
        })
        
    for sid, p_data in room.players.items():
        socketio.emit('update_state', {
            'players': public_players, 'my_hand': p_data["hand"],
            'started': room.started, 'game_over': room.game_over,
            'turn_deadline': room.turn_deadline, 'is_my_turn': sid == current_turn_sid,
            'actions_left': room.actions_left if sid == current_turn_sid else 0,
            'is_discard_mode': room.is_discard_phase if (sid == current_turn_sid) else False,
            'current_turn_name': room.players[current_turn_sid]['name'] if (current_turn_sid and current_turn_sid in room.players) else ""
        }, room=sid)

if __name__ == '__main__':
    socketio.start_background_task(background_turn_timer)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)