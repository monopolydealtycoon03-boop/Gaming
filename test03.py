from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================================
# 1. HTML & JAVASCRIPT FRONTEND (LUXURY UI + SFX & ANIMATIONS)
# ==========================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Tycoon - Luxury Card Game</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        gold: {
                            100: '#fbf6e2',
                            300: '#f3e5ab',
                            500: '#d4af37',
                            600: '#aa771c',
                            700: '#855812',
                        },
                        darkbg: '#09090b',
                        cardbg: '#14110e',
                    },
                    fontFamily: {
                        cinzel: ['Cinzel', 'serif'],
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                    }
                }
            }
        }
    </script>

    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: #09090b;
            color: #f8fafc;
            overflow-x: hidden;
            user-select: none;
        }

        /* Custom Scrollbars */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #09090b; }
        ::-webkit-scrollbar-thumb { background: #d4af37; border-radius: 3px; }

        /* Luxury Glow Effects */
        .gold-border-glow {
            border: 1px solid #d4af37;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.25), inset 0 0 15px rgba(212, 175, 55, 0.1);
        }
        .gold-text-glow { text-shadow: 0 0 10px rgba(212, 175, 55, 0.5); }

        /* ==============================
           CARD ANIMATIONS ENGINE
           ============================== */
        @keyframes dealIn {
            0% { transform: translateY(-80px) scale(0.6) rotateX(-90deg); opacity: 0; }
            100% { transform: translateY(0) scale(1) rotateX(0); opacity: 1; }
        }
        .animate-deal {
            animation: dealIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            transform-origin: center center;
            opacity: 0;
        }

        @keyframes popIn {
            0% { transform: scale(0.5); opacity: 0; }
            70% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(1); opacity: 1; }
        }
        .animate-pop { 
            animation: popIn 0.3s ease-out forwards; 
            opacity: 0;
        }

        @keyframes glowingBorder {
            0% { box-shadow: 0 0 5px #d4af37, inset 0 0 5px #d4af37; border-color: #d4af37; }
            50% { box-shadow: 0 0 25px #f3e5ab, inset 0 0 15px #f3e5ab; border-color: #fbf6e2; }
            100% { box-shadow: 0 0 5px #d4af37, inset 0 0 5px #d4af37; border-color: #d4af37; }
        }
        .player-active-glow {
            animation: glowingBorder 1.5s infinite alternate;
            border-width: 2px !important;
            transform: scale(1.01);
            transition: all 0.3s ease;
        }

        /* 3D Realistic Card Styling */
        .game-card {
            width: 100px;
            height: 145px;
            border-radius: 8px;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.25s;
            cursor: grab;
            box-shadow: 0 6px 12px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.4);
            flex-shrink: 0;
            display: inline-block;
            z-index: 10;
        }
        
        .game-card:active { cursor: grabbing; }

        .game-card:hover {
            transform: translateY(-12px) scale(1.06) rotateX(4deg);
            box-shadow: 0 16px 28px rgba(0,0,0,0.8), 0 0 12px rgba(212, 175, 55, 0.6);
            z-index: 50;
        }
        
        .game-card.disabled-card { opacity: 0.7; cursor: not-allowed; } 
        .game-card.discard-mode { border: 2px solid #ef4444; animation: shake 0.5s infinite; cursor: pointer; }
        @keyframes shake { 0%, 100% {transform: rotate(-2deg);} 50% {transform: rotate(2deg);} }

        /* Card Color Badges & Themes */
        .card-inner {
            width: 100%; height: 100%; border-radius: 6px; padding: 6px;
            display: flex; flex-direction: column; justify-content: space-between;
            box-sizing: border-box; background: #1c1813; border: 2px solid #d4af37;
            pointer-events: none; /* Helps with drag drop events */
        }

        .prop-Brown { background-color: #795548; color: #fff; }
        .prop-Light-Blue { background-color: #03a9f4; color: #000; }
        .prop-Pink { background-color: #e91e63; color: #fff; }
        .prop-Orange { background-color: #ff9800; color: #000; }
        .prop-Red { background-color: #f44336; color: #fff; }
        .prop-Yellow { background-color: #fbc02d; color: #000; }
        .prop-Green { background-color: #4caf50; color: #fff; }
        .prop-Dark-Blue { background-color: #1a237e; color: #fff; }
        .prop-Railroad { background-color: #37474f; color: #fff; }
        .prop-Utility { background-color: #009688; color: #fff; }
        .prop-Wild { background: linear-gradient(135deg, #d4af37, #aa771c, #fbf6e2); color: #000; }
        .building-card { background: #8b0000; color: white; border: 1px solid #d4af37; }

        /* Card Header Strips */
        .color-strip {
            height: 22px; border-radius: 4px; width: 100%;
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; font-size: 10px; text-transform: uppercase;
            letter-spacing: 0.5px; box-shadow: inset 0 1px 2px rgba(255,255,255,0.3);
        }

        .action-bg { background: linear-gradient(135deg, #1f1a14 0%, #2a2218 100%); border: 2px solid #d4af37; }
        .money-bg { background: linear-gradient(135deg, #0d2818 0%, #05190e 100%); border: 2px solid #2ecc71; }

        @keyframes activePulse {
            0% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.7); }
            70% { box-shadow: 0 0 0 12px rgba(212, 175, 55, 0); }
            100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }
        }
        .active-turn-indicator { animation: activePulse 2s infinite; }
        
        .modal-btn { @apply w-full py-2.5 bg-cardbg hover:bg-gold-900 border border-gold-500/50 hover:border-gold-500 text-white font-bold rounded-lg transition-colors text-sm; }
    </style>
</head>
<body class="bg-darkbg min-h-screen text-slate-100 flex flex-col justify-between">

    <!-- INTERACTIVE MODAL DIALOG -->
    <div id="modal-overlay" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[1000] hidden items-center justify-center p-4">
        <div class="bg-cardbg border-2 border-gold-500 rounded-xl p-6 max-w-lg w-full text-center shadow-2xl relative gold-border-glow max-h-[85vh] flex flex-col">
            <h3 id="modal-title" class="font-cinzel text-xl text-gold-500 font-bold mb-3 border-b border-gold-500/30 pb-2">Select Target</h3>
            <div id="modal-buttons" class="overflow-y-auto my-3 flex-1 space-y-2 pr-1 text-left"></div>
            <div id="modal-actions" class="mt-4 pt-2 border-t border-gold-500/30 flex gap-2 justify-center">
                <button onclick="closeModal()" class="w-full py-2.5 bg-red-900/80 hover:bg-red-800 text-white font-bold rounded-lg border border-red-500 transition-colors">Cancel</button>
            </div>
        </div>
    </div>

    <!-- NOTIFICATION TOAST OVERLAY -->
    <div id="toast-container" class="fixed top-20 right-5 z-[900] space-y-2 pointer-events-none max-w-sm"></div>

    <!-- 1. LOBBY SCREEN -->
    <div id="lobby-screen" class="p-4 md:p-8 block">
        <div class="max-w-5xl mx-auto border-2 border-gold-500/80 rounded-2xl bg-gradient-to-b from-[#18150f] to-[#0b0907] p-6 md:p-12 gold-border-glow my-4">
            
            <div class="flex justify-between items-center border-b border-gold-500/30 pb-6 mb-8">
                <div class="border border-gold-500 px-4 py-1.5 font-cinzel text-gold-500 font-bold tracking-widest bg-black/50 rounded">
                    PROPERTY TYCOON
                </div>
                <div class="text-xs tracking-widest text-slate-400 font-semibold uppercase">Luxury Edition Pro</div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                <div class="text-left space-y-4">
                    <p class="text-xs uppercase tracking-[0.3em] text-gold-500 font-bold">The Ultimate Deal-Making Game</p>
                    <h1 class="font-cinzel text-4xl md:text-5xl font-extrabold text-gold-300 leading-tight">
                        PROPERTY <span class="block text-gold-500 text-5xl md:text-6xl gold-text-glow">TYCOON</span>
                    </h1>
                    
                    <div class="pt-4 space-y-3">
                        <label class="block text-xs uppercase text-gold-500 font-bold tracking-wider">Your Nickname</label>
                        <input type="text" id="player-name" placeholder="Tycoon Baron" required class="w-full bg-black/60 border border-gold-500/50 rounded-lg p-3 text-white focus:outline-none focus:border-gold-500 font-semibold">
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4">
                        <div class="bg-cardbg p-4 border border-gold-500/30 rounded-xl space-y-3">
                            <h3 class="font-cinzel text-gold-500 font-bold border-b border-gold-500/30 pb-1">Host Game</h3>
                            <input type="text" id="create-room-id" placeholder="Room ID" class="w-full bg-black/60 border border-gold-500/30 rounded p-2 text-sm text-white">
                            <input type="password" id="create-room-pass" placeholder="Password" class="w-full bg-black/60 border border-gold-500/30 rounded p-2 text-sm text-white">
                            <button onclick="goToModeSelect()" class="w-full py-2 bg-gradient-to-r from-gold-600 to-gold-500 text-black font-extrabold rounded uppercase text-xs hover:brightness-110">Create Room</button>
                        </div>
                        <div class="bg-cardbg p-4 border border-gold-500/30 rounded-xl space-y-3">
                            <h3 class="font-cinzel text-gold-500 font-bold border-b border-gold-500/30 pb-1">Join Game</h3>
                            <input type="text" id="join-room-id" placeholder="Room ID" class="w-full bg-black/60 border border-gold-500/30 rounded p-2 text-sm text-white">
                            <input type="password" id="join-room-pass" placeholder="Password" class="w-full bg-black/60 border border-gold-500/30 rounded p-2 text-sm text-white">
                            <button onclick="joinRoom()" class="w-full py-2 bg-transparent border border-gold-500 text-gold-500 font-extrabold rounded uppercase text-xs hover:bg-gold-500/10">Join Room</button>
                        </div>
                    </div>
                </div>

                <div class="relative h-80 flex items-center justify-center hidden lg:flex">
                    <div class="game-card absolute -rotate-12 -translate-x-12 z-10 border-gold-500"><div class="card-inner action-bg"><div class="color-strip bg-gold-500 text-black">ACTION</div><div class="text-center my-auto font-cinzel text-xs font-bold text-gold-300">DEAL BREAKER</div></div></div>
                    <div class="game-card absolute rotate-0 z-20 scale-110"><div class="card-inner prop-Dark-Blue"><div class="color-strip prop-Dark-Blue border border-white/20">DARK BLUE</div><div class="text-center my-auto font-cinzel text-xs font-bold text-white">BOARDWALK</div></div></div>
                    <div class="game-card absolute rotate-12 translate-x-12 z-10"><div class="card-inner money-bg"><div class="color-strip bg-emerald-600 text-white">CASH</div><div class="text-center my-auto font-cinzel text-xl font-extrabold text-emerald-400">10M</div></div></div>
                </div>
            </div>
        </div>
    </div>

    <!-- 2. MODE SELECT SCREEN -->
    <div id="mode-select-screen" class="hidden p-4 md:p-8">
        <div class="max-w-2xl mx-auto border-2 border-gold-500/80 rounded-2xl bg-cardbg p-8 gold-border-glow my-4 text-center">
            <h2 class="font-cinzel text-3xl font-bold text-gold-500 mb-6">Choose Game Mode</h2>
            <div class="space-y-4">
                <div class="bg-black/50 p-5 rounded-xl border border-gold-500/30">
                    <h3 class="text-gold-300 font-bold uppercase tracking-widest mb-3">Play with AI Bot</h3>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <button onclick="createRoomWithBot('easy')" class="p-3 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-500/50 rounded-xl transition-all"><div class="font-bold text-white text-sm">🟢 Easy Bot</div></button>
                        <button onclick="createRoomWithBot('normal')" class="p-3 bg-amber-950/80 hover:bg-amber-900 border border-amber-500/50 rounded-xl transition-all"><div class="font-bold text-white text-sm">🟡 Normal Bot</div></button>
                        <button onclick="createRoomWithBot('hard')" class="p-3 bg-red-950/80 hover:bg-red-900 border border-red-500/50 rounded-xl transition-all"><div class="font-bold text-white text-sm">🔥 Hard Bot</div></button>
                    </div>
                </div>
                <div class="bg-black/50 p-5 rounded-xl border border-gold-500/30">
                    <h3 class="text-gold-300 font-bold uppercase tracking-widest mb-3">Play Multiplayer</h3>
                    <button onclick="createRoomWithMode('multiplayer')" class="w-full p-3.5 bg-gradient-to-r from-gold-600 to-gold-500 text-black font-extrabold rounded-xl uppercase shadow-lg hover:brightness-110">Host Online Match</button>
                </div>
            </div>
            <button onclick="switchScreen('lobby-screen')" class="mt-6 px-6 py-2 bg-transparent border border-slate-500 text-slate-400 font-bold rounded-lg hover:bg-slate-800">Go Back</button>
        </div>
    </div>

    <!-- 3. WAITING ROOM -->
    <div id="waiting-screen" class="hidden p-4 md:p-8">
        <div class="max-w-xl mx-auto border-2 border-gold-500/80 rounded-2xl bg-cardbg p-8 gold-border-glow my-4 text-center">
            <h2 class="font-cinzel text-2xl font-bold text-gold-500 mb-2">Room: <span id="display-room-id" class="text-white"></span></h2>
            <p class="text-sm text-slate-400 mb-6">Waiting for players to join...</p>
            <ul id="player-list" class="space-y-2 mb-8 text-lg font-bold"></ul>
            <div id="host-controls" style="display: none;">
                <button onclick="startGame()" class="w-full py-3 bg-gradient-to-r from-gold-600 to-gold-500 text-black font-extrabold rounded-xl uppercase text-lg shadow-lg hover:brightness-110">▶ Start Game Now</button>
            </div>
        </div>
    </div>

    <!-- 4. GAME BOARD SCREEN -->
    <div id="game-screen" class="hidden p-2 md:p-4 max-w-[1600px] mx-auto w-full flex-col justify-between space-y-4 min-h-screen">
        
        <div class="bg-cardbg border border-gold-500/40 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 shadow-lg">
            <div class="flex items-center gap-3">
                <span class="font-cinzel text-gold-500 font-extrabold text-lg tracking-wider">TYCOON ARENA</span>
                <span id="turn-badge" class="px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-gold-500 text-black">Waiting...</span>
            </div>
            <div class="flex items-center gap-4">
                <div class="bg-black/60 border border-gold-500/30 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2">
                    <span class="text-slate-400 uppercase font-bold">Actions Left:</span>
                    <span id="actions-left-count" class="text-gold-500 font-extrabold text-base">0</span>
                    <span class="text-slate-500">/ 3</span>
                </div>
                <button id="end-turn-btn" onclick="endTurn()" class="hidden px-5 py-2 bg-gradient-to-r from-gold-600 to-gold-500 hover:brightness-110 text-black font-extrabold rounded-lg text-sm uppercase tracking-wider transition-all shadow-md">
                    ✓ Done Turn
                </button>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 flex-1">
            <div class="lg:col-span-3 space-y-4 flex flex-col justify-between">
                
                <!-- OPPONENTS AREA -->
                <div id="opponents-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 min-h-[220px]"></div>

                <!-- PLAYER BOARD AREA -->
                <div id="my-board-container" class="bg-black/50 border border-gold-500/40 rounded-xl p-4 flex-1 flex flex-col justify-between min-h-[260px] transition-all relative">
                    <div class="flex justify-between items-center mb-2">
                        <h3 class="font-cinzel text-gold-300 text-sm font-extrabold uppercase tracking-widest flex items-center gap-2">
                            <i class="fa-solid fa-crown text-gold-500"></i>
                            <span>Your Managed Assets & Bank</span>
                        </h3>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-4 gap-3 flex-1">
                        <!-- Player Bank -->
                        <div class="md:col-span-1 relative bg-cardbg/80 border border-emerald-500/30 rounded-lg p-2.5 flex flex-col">
                            <!-- DRAG DROP OVERLAY FOR BANK -->
                            <div id="bank-dropzone" class="absolute inset-0 rounded-lg hidden z-50 flex items-center justify-center bg-black/70 border-2 border-dashed border-emerald-400 text-emerald-300 font-bold uppercase tracking-widest text-xs transition-colors backdrop-blur-sm"
                                 ondragover="event.preventDefault(); this.classList.add('bg-emerald-900/80');" 
                                 ondragleave="this.classList.remove('bg-emerald-900/80');" 
                                 ondrop="handleDrop(event, 'bank')">
                                 💰 Drop Cash Here
                            </div>
                            
                            <div class="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-2 flex justify-between">
                                <span>Bank Account</span>
                                <span id="my-bank-total" class="text-white">0M</span>
                            </div>
                            <div id="my-bank-cards" class="flex flex-wrap gap-1.5 overflow-y-auto max-h-[160px] p-1 content-start"></div>
                        </div>

                        <!-- Player Properties -->
                        <div class="md:col-span-3 relative bg-cardbg/80 border border-gold-500/30 rounded-lg p-2.5 flex flex-col">
                            <!-- DRAG DROP OVERLAY FOR PROPERTY/ACTION -->
                            <div id="property-dropzone" class="absolute inset-0 rounded-lg hidden z-50 flex items-center justify-center bg-black/70 border-2 border-dashed border-gold-400 text-gold-300 font-bold uppercase tracking-widest text-xs transition-colors backdrop-blur-sm"
                                 ondragover="event.preventDefault(); this.classList.add('bg-gold-900/80');" 
                                 ondragleave="this.classList.remove('bg-gold-900/80');" 
                                 ondrop="handleDrop(event, 'property')">
                                 🏢 Drop Property or ⚡ Action Here
                            </div>

                            <div class="flex justify-between items-center mb-2">
                                <div class="text-[11px] font-bold text-gold-500 uppercase tracking-wider">Property Sets</div>
                                <div class="text-[9px] text-slate-400 italic">★ Click your Wild Cards to rearrange them for free!</div>
                            </div>
                            <div id="my-property-sets" class="flex flex-wrap gap-2 overflow-x-auto p-1 flex-1 items-start"></div>
                        </div>
                    </div>
                </div>

                <!-- PLAYER HAND AREA -->
                <div class="bg-cardbg border-2 border-gold-500/60 rounded-xl p-3 shadow-xl">
                    <div class="flex justify-between items-center mb-2 px-1">
                        <div class="text-xs font-bold text-gold-300 uppercase tracking-wider flex items-center gap-2">
                            <span>Your Cards in Hand</span>
                        </div>
                        <div class="text-[10px] text-slate-400">Click or Drag a card to play</div>
                    </div>
                    <div id="my-hand-cards" class="flex gap-2 overflow-x-auto pb-2 pt-1 min-h-[160px] items-center px-1"></div>
                </div>
            </div>

            <!-- Turn Log & Chat System -->
            <div class="bg-cardbg border border-gold-500/30 rounded-xl p-3 flex flex-col h-full gap-3 max-h-[85vh]">
                
                <!-- Action Log -->
                <div class="flex-1 flex flex-col min-h-[120px] max-h-[40%]">
                    <div class="text-xs font-bold text-gold-500 uppercase tracking-widest mb-1 border-b border-gold-500/20 pb-1 flex items-center gap-1.5">
                        <i class="fa-solid fa-scroll"></i>
                        <span>Live Action Log</span>
                    </div>
                    <div id="game-log" class="flex-1 bg-black/80 border border-slate-800 rounded-lg p-2 overflow-y-auto font-mono text-[10px] space-y-1.5"></div>
                </div>
                
                <!-- Chat & Emotes System -->
                <div class="flex-1 flex flex-col min-h-[220px] border-t border-gold-500/30 pt-3">
                    <div class="text-xs font-bold text-emerald-400 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                        <i class="fa-solid fa-comments"></i>
                        <span>Live Chat</span>
                    </div>
                    
                    <!-- Chat Messages Area -->
                    <div id="chat-box" class="flex-1 bg-black/80 border border-slate-800 rounded-lg p-2.5 overflow-y-auto text-[11px] space-y-2 mb-2 flex flex-col">
                        <div class="text-center text-slate-500 italic text-[10px]">Welcome to the chat! Emote away!</div>
                    </div>
                    
                    <!-- Quick Emotes Row -->
                    <div class="flex justify-between gap-1 mb-2">
                        <button onclick="sendChat('😠')" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-base py-1 transition-colors hover:scale-110">😠</button>
                        <button onclick="sendChat('💸')" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-base py-1 transition-colors hover:scale-110">💸</button>
                        <button onclick="sendChat('🤝')" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-base py-1 transition-colors hover:scale-110">🤝</button>
                        <button onclick="sendChat('😭')" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-base py-1 transition-colors hover:scale-110">😭</button>
                        <button onclick="sendChat('😈')" class="flex-1 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded text-base py-1 transition-colors hover:scale-110">😈</button>
                    </div>

                    <!-- Chat Input -->
                    <div class="flex gap-2">
                        <input type="text" id="chat-input" placeholder="Type a message..." class="flex-1 bg-black/60 border border-slate-600 rounded px-2 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500" onkeypress="if(event.key === 'Enter') submitChatText()">
                        <button onclick="submitChatText()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded text-xs font-bold transition-colors"><i class="fa-solid fa-paper-plane"></i></button>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        // =====================================
        // SOUND EFFECTS ENGINE (MIXKIT SFX)
        // =====================================
        const sfx = {
            draw: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-playing-cards-falling-2025.mp3'),
            cash: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-cash-register-purchase-873.mp3'),
            alert: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-alert-alarm-1005.mp3'),
            deal: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-fast-small-sweep-transition-166.mp3'),
            error: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-game-show-wrong-answer-buzz-950.mp3'),
            pop: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-modern-click-box-check-1120.mp3') // Chat sound
        };

        function playSound(type) {
            try {
                let sound = sfx[type].cloneNode();
                sound.volume = 0.4;
                sound.play().catch(e => console.log('Audio prevented by browser policy'));
            } catch(e){}
        }

        const socket = io(window.location.origin);
        let currentRoom = "";
        let isHost = false;
        let myPlayerName = "";
        
        let myTurn = false;
        let actionsLeft = 0;
        let myHandData = [];
        let prevHandCount = 0;
        let latestPlayersData = [];
        let isDiscardMode = false;
        let turnDeadline = 0;
        let currentTurnName = "";
        let timerInterval = null;
        let jsnTimerInterval = null;
        let myPropertiesData = [];
        
        let activeModalOpponentCallback = null;
        let draggedCardIndex = -1; // Added for Drag & Drop Feature

        const setSizes = { 'Brown': 2, 'Light Blue': 3, 'Pink': 3, 'Orange': 3, 'Red': 3, 'Yellow': 3, 'Green': 3, 'Dark Blue': 2, 'Railroad': 4, 'Utility': 2 };
        const allColors = ['Brown', 'Light Blue', 'Pink', 'Orange', 'Red', 'Yellow', 'Green', 'Dark Blue', 'Railroad', 'Utility'];

        function toTitleCase(str) { return (str || '').toLowerCase().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '); }
        function getCssColorClass(col) { return col ? col.replace(/ /g, '-') : 'Wild'; }
        function escapeStr(str) { return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;'); }
        function escapeHTML(str) {
            return (str || '').replace(/[&<>'"]/g, tag => ({
                '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
            }[tag]));
        }

        function switchScreen(screenId) {
            ['lobby-screen', 'mode-select-screen', 'waiting-screen', 'game-screen'].forEach(id => {
                const el = document.getElementById(id);
                el.classList.add('hidden');
                if(id === 'game-screen') el.classList.remove('flex');
            });
            const target = document.getElementById(screenId);
            target.classList.remove('hidden');
            if (screenId === 'game-screen') target.classList.add('flex');
        }

        function showToast(title, text, isError=false) {
            if (isError) playSound('error');
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `bg-cardbg border-l-4 ${isError ? 'border-red-500' : 'border-gold-500'} text-white p-3 rounded shadow-xl pointer-events-auto transform transition-all duration-300 translate-x-10 opacity-0 flex flex-col`;
            toast.innerHTML = `<div class="font-cinzel text-xs ${isError ? 'text-red-400' : 'text-gold-500'} font-bold uppercase">${title}</div><div class="text-xs text-slate-300">${text}</div>`;
            container.appendChild(toast);
            setTimeout(() => toast.classList.remove('translate-x-10', 'opacity-0'), 10);
            setTimeout(() => { toast.classList.add('opacity-0'); setTimeout(() => toast.remove(), 300); }, 3500);
        }

        function logMessage(msg) {
            const logContainer = document.getElementById('game-log');
            const entry = document.createElement('div');
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            entry.className = `text-slate-300 leading-snug border-b border-slate-800/40 pb-1`;
            entry.innerHTML = `<span class="text-slate-600 font-sans">[${time}]</span> ${msg}`;
            logContainer.appendChild(entry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        // =====================================
        // CHAT & EMOTE SYSTEM
        // =====================================
        function submitChatText() {
            const input = document.getElementById('chat-input');
            const msg = input.value.trim();
            if (msg) {
                sendChat(msg);
                input.value = '';
            }
        }

        function sendChat(msg) {
            if (!currentRoom || !myPlayerName) return;
            socket.emit('send_chat', { room_id: currentRoom, sender: myPlayerName, message: msg });
        }

        socket.on('receive_chat', (data) => {
            const chatBox = document.getElementById('chat-box');
            const entry = document.createElement('div');
            const isMe = data.sender.toLowerCase() === myPlayerName.toLowerCase();
            
            entry.className = `flex flex-col ${isMe ? 'items-end' : 'items-start'} animate-pop`;
            
            let nameTag = isMe 
                ? `<span class="text-[9px] text-emerald-500/70 mb-0.5 px-1">You</span>` 
                : `<span class="text-[9px] text-gold-500/70 mb-0.5 px-1">${escapeHTML(data.sender)}</span>`;
            
            // Check if message is a single emote
            const emotesList = ['😠', '💸', '🤝', '😭', '😈'];
            const isEmote = emotesList.includes(data.message.trim());
            
            let msgStyle = isEmote 
                ? `text-3xl drop-shadow-lg` 
                : `px-2.5 py-1.5 rounded-lg max-w-[90%] break-words shadow-md ${isMe ? 'bg-emerald-900/60 text-emerald-100 border border-emerald-500/30 rounded-br-none' : 'bg-slate-800 text-slate-200 border border-slate-600/50 rounded-bl-none'}`;

            entry.innerHTML = `${nameTag}<div class="${msgStyle}">${escapeHTML(data.message)}</div>`;
            
            chatBox.appendChild(entry);
            chatBox.scrollTop = chatBox.scrollHeight;

            if (!isMe) playSound('pop');
        });

        // =====================================
        // DRAG AND DROP MECHANICS
        // =====================================
        function handleDragStart(e, idx) {
            if (!myTurn || isDiscardMode || actionsLeft <= 0) {
                e.preventDefault();
                return;
            }
            draggedCardIndex = idx;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', idx);
            
            // Show Drop Zones with a slight delay to ensure browser captures card image correctly
            setTimeout(() => {
                document.getElementById('bank-dropzone').classList.remove('hidden');
                document.getElementById('property-dropzone').classList.remove('hidden');
            }, 10);
        }

        function handleDragEnd(e) {
            document.getElementById('bank-dropzone').classList.add('hidden');
            document.getElementById('property-dropzone').classList.add('hidden');
            document.getElementById('bank-dropzone').classList.remove('bg-emerald-900/80');
            document.getElementById('property-dropzone').classList.remove('bg-gold-900/80');
            draggedCardIndex = -1;
        }

        function handleDrop(e, type) {
            e.preventDefault();
            
            // Reset Dropzones UI
            document.getElementById('bank-dropzone').classList.add('hidden');
            document.getElementById('property-dropzone').classList.add('hidden');
            document.getElementById('bank-dropzone').classList.remove('bg-emerald-900/80');
            document.getElementById('property-dropzone').classList.remove('bg-gold-900/80');

            let idx = draggedCardIndex;
            draggedCardIndex = -1;

            if (idx === -1) return;
            if (actionsLeft <= 0) return;

            let card = myHandData[idx];
            
            if (card.name === "Just Say No!") {
                showToast("Defense Card", "You can only play this when someone attacks you!", true);
                return;
            }

            if (type === 'bank') {
                if (card.value > 0) {
                    submitPlayAction(idx, 'bank');
                } else {
                    showToast("Cannot Bank", "This card has no monetary value!", true);
                }
            } else if (type === 'property') {
                if (card.type === 'Money') {
                    showToast("Invalid Move", "Money cards must be placed in the Bank!", true);
                } else if (card.type === 'Property') {
                    if (card.name === "Property Wild Card" || card.name.includes("&")) {
                        handleWildPropertyPlacement(idx, escapeStr(card.name));
                    } else {
                        submitPlayAction(idx, 'property');
                    }
                } else if (card.type === 'Building') {
                    handleBuildingPlacement(idx);
                } else if (card.type === 'Action') {
                    routeActionCard(idx);
                }
            }
        }

        function closeModal() {
            document.getElementById('modal-overlay').classList.add('hidden');
            document.getElementById('modal-overlay').classList.remove('flex');
        }

        function showModal(title, contentHtml, hideCancel = false) {
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-buttons').innerHTML = contentHtml;
            if(hideCancel) {
                document.getElementById('modal-actions').classList.add('hidden');
            } else {
                document.getElementById('modal-actions').classList.remove('hidden');
            }
            document.getElementById('modal-overlay').classList.remove('hidden');
            document.getElementById('modal-overlay').classList.add('flex');
        }

        function showRearrangeModal(propIdx, origName, currentColor) {
            if (!myTurn) { showToast("Wait", "You can only rearrange on your turn!", true); return; }
            if (isDiscardMode) return;
            
            let allowedColors = allColors;
            if (origName && origName.includes("&")) {
                allowedColors = allColors.filter(col => origName.toLowerCase().includes(col.toLowerCase()));
            }
            
            let html = `<p class="text-xs text-slate-300 mb-4 text-center">Rearranging a Wild Card is a <b class="text-emerald-400">FREE ACTION</b>.</p><div class="grid grid-cols-2 gap-2">`;
            allowedColors.forEach(col => {
                if (col !== currentColor) {
                    html += `<button onclick="closeModal(); socket.emit('rearrange_wild', {room_id: currentRoom, prop_idx: ${propIdx}, new_color: '${col}'})" class="modal-btn prop-${getCssColorClass(col)}">Move to ${col}</button>`;
                }
            });
            html += `</div>`;
            showModal("Rearrange Wild Card", html);
        }

        // ANIMATED CARD RENDERER
        function createCardDOM(card, index, clickable, delay = 0) {
            const cardEl = document.createElement('div');
            cardEl.className = 'game-card animate-deal';
            cardEl.style.animationDelay = `${delay}ms`;
            
            if (isDiscardMode) {
                cardEl.classList.add('discard-mode');
            } else if (!myTurn) {
                cardEl.classList.add('disabled-card'); 
            }

            if (clickable) {
                cardEl.onclick = () => handleCardClick(index);
                
                // Add Drag Events
                if (!isDiscardMode) {
                    cardEl.draggable = true;
                    cardEl.ondragstart = (e) => handleDragStart(e, index);
                    cardEl.ondragend = handleDragEnd;
                }
            }

            let cardThemeClass = 'action-bg';
            let headerBg = 'bg-gold-500 text-black';
            let categoryTitle = 'ACTION';

            if (card.type === 'Property') {
                const colClass = getCssColorClass(card.color);
                cardThemeClass = `prop-${colClass}`;
                headerBg = `prop-${colClass} border border-white/20`;
                categoryTitle = card.color ? card.color.toUpperCase() : 'WILD PROP';
            } else if (card.type === 'Money') {
                cardThemeClass = 'money-bg';
                headerBg = 'bg-emerald-600 text-white';
                categoryTitle = 'CASH';
            } else if (card.type === 'Building') {
                cardThemeClass = 'building-card';
                headerBg = 'bg-black text-white border border-gold-500';
                categoryTitle = 'BUILDING';
            } else if (card.name.startsWith('Rent') || card.name === 'Double Rent' || card.name === 'Just Say No!') {
                cardThemeClass = 'action-bg';
                headerBg = 'bg-amber-600 text-white';
                categoryTitle = card.name === 'Just Say No!' ? 'DEFENSE' : 'RENT';
            }

            cardEl.innerHTML = `
                <div class="card-inner ${cardThemeClass}">
                    <div class="color-strip ${headerBg}">${categoryTitle}</div>
                    <div class="text-center my-auto font-cinzel text-[10px] font-bold ${card.type === 'Property' ? 'text-white' : 'text-gold-300'} leading-tight">
                        ${card.name}
                    </div>
                    <div class="flex justify-between items-center text-[9px] font-bold text-gold-500 border-t border-gold-500/20 pt-1 mt-1">
                        <span>VALUE</span>
                        <span>${card.value || 0}M</span>
                    </div>
                </div>
            `;
            return cardEl;
        }

        // ANIMATED MINI CARD RENDERER
        function createMiniCardDOM(card, boardIdx = -1, isMine = false, delay = 0) {
            const mini = document.createElement('div');
            let bg = 'bg-black/70 border-gold-500/40 text-slate-200';
            if (card.type === 'Property') bg = `prop-${getCssColorClass(card.color)} text-white font-bold`;
            else if (card.type === 'Money') bg = 'money-bg border-emerald-500 text-emerald-100 font-bold';
            else if (card.type === 'Building') bg = 'building-card font-bold';
            
            let extraClasses = 'animate-pop';
            if (isMine && card.is_wild && boardIdx !== -1) {
                extraClasses += ' cursor-pointer hover:ring-2 hover:ring-white transition-all';
                mini.setAttribute('onclick', `showRearrangeModal(${boardIdx}, '${escapeStr(card.original_name)}', '${escapeStr(card.color)}')`);
                mini.setAttribute('title', 'Click to rearrange (Free Action)');
            }
            
            let displayName = card.name;
            if (card.is_wild) {
                displayName = `<span class="text-amber-300 text-[10px] mr-1">★</span>` + displayName;
            }
            
            mini.className = `border rounded px-1.5 py-0.5 text-[9px] flex justify-between items-center w-full shadow-sm mb-1 ${bg} ${extraClasses}`;
            mini.style.animationDelay = `${delay}ms`;
            mini.innerHTML = `<span class="truncate max-w-[80px] font-semibold flex items-center">${displayName}</span><span class="text-gold-300 font-bold ml-1">${card.value || 0}M</span>`;
            return mini;
        }

        socket.on('alert', (data) => {
            showToast("Notification", data.message);
            logMessage(`<b>System:</b> ${data.message}`);
            
            // Smart Audio Routing
            let msg = data.message.toLowerCase();
            if (msg.includes('just say no') || msg.includes('deal breaker') || msg.includes('stole') || msg.includes('snatched') || msg.includes('shattered')) {
                playSound('alert');
            } else if (msg.includes('rent') || msg.includes('paid') || msg.includes('debt') || msg.includes('birthday') || msg.includes('bank') || msg.includes('settled')) {
                playSound('cash');
            } else {
                playSound('deal');
            }
        });

        function goToModeSelect() {
            let n = document.getElementById('player-name').value.trim();
            let r = document.getElementById('create-room-id').value.trim();
            let p = document.getElementById('create-room-pass').value.trim();
            if(!n || !r || !p) { showToast("Error", "Please fill in your Name, Room ID, and Password!", true); return; }
            myPlayerName = n;
            switchScreen('mode-select-screen');
        }

        function createRoomWithBot(difficulty) {
            let n = document.getElementById('player-name').value.trim();
            let r = document.getElementById('create-room-id').value.trim();
            let p = document.getElementById('create-room-pass').value.trim();
            myPlayerName = n;
            socket.emit('create_room', { room_id: r, password: p, player_name: n, game_mode: 'bot', bot_difficulty: difficulty });
        }

        function createRoomWithMode(mode) {
            let n = document.getElementById('player-name').value.trim();
            let r = document.getElementById('create-room-id').value.trim();
            let p = document.getElementById('create-room-pass').value.trim();
            myPlayerName = n;
            socket.emit('create_room', { room_id: r, password: p, player_name: n, game_mode: mode });
        }
        
        function joinRoom() {
            let n = document.getElementById('player-name').value.trim(); 
            let r = document.getElementById('join-room-id').value.trim(); 
            let p = document.getElementById('join-room-pass').value.trim();
            if(n && r && p) {
                myPlayerName = n;
                socket.emit('join_room', { room_id: r, password: p, player_name: n });
            } else {
                showToast("Error", "Fill all Join details!", true);
            }
        }

        socket.on('error', (data) => { showToast("Error", data.message, true); });
        
        socket.on('room_joined', (data) => {
            currentRoom = data.room_id;
            isHost = data.is_host;
            switchScreen('waiting-screen');
            document.getElementById('display-room-id').innerText = currentRoom;
            if (isHost) document.getElementById('host-controls').style.display = 'block';
        });

        // =====================================
        // GAME OVER & REMATCH HANDLING
        // =====================================
        socket.on('game_over', (data) => {
            if (timerInterval) clearInterval(timerInterval);
            document.getElementById('end-turn-btn').classList.add('hidden');
            let winHtml = `
                <div class="text-center space-y-4 py-4">
                    <i class="fa-solid fa-trophy text-6xl text-gold-500 gold-text-glow"></i>
                    <h2 class="font-cinzel text-3xl font-extrabold text-gold-300">${data.winner} Wins!</h2>
                    <p class="text-sm text-slate-400">What would you like to do next?</p>
                    <div class="flex gap-3 mt-6">
                        <button onclick="requestRematch()" class="flex-1 py-3 bg-emerald-700 hover:bg-emerald-600 text-white font-bold rounded-lg border border-emerald-500 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.4)]">🔄 Play Again</button>
                        <button onclick="location.reload()" class="flex-1 py-3 bg-red-900/80 hover:bg-red-800 text-white font-bold rounded-lg border border-red-500 transition-colors">🚪 Exit Lobby</button>
                    </div>
                </div>
            `;
            showModal("GAME OVER", winHtml, true);
        });

        function requestRematch() {
            socket.emit('request_rematch', { room_id: currentRoom });
        }

        socket.on('game_restarted', () => {
            closeModal();
            showToast("New Game", "The match has been restarted! Let the best Tycoon win.", false);
            playSound('deal');
            document.getElementById('game-log').innerHTML = ''; // Clear old logs
            document.getElementById('chat-box').innerHTML = '<div class="text-center text-slate-500 italic text-[10px]">Welcome to the chat! Emote away!</div>'; // Clear old chat
        });

        function updateTimerDisplay() {
            if (!turnDeadline) return;
            let now = Math.floor(Date.now() / 1000);
            let timeLeft = Math.max(0, Math.floor(turnDeadline - now));
            let badge = document.getElementById('turn-badge');

            if (myTurn) {
                if (isDiscardMode) {
                    badge.innerText = `DISCARD MODE`;
                    badge.className = "px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-red-600 text-white active-turn-indicator";
                } else {
                    badge.innerText = `YOUR TURN (${timeLeft}s)`;
                    badge.className = "px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-gold-500 text-black active-turn-indicator";
                }
            } else {
                badge.innerText = `Waiting for ${currentTurnName}... (${timeLeft}s)`;
                badge.className = "px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-slate-800 text-slate-400";
            }
        }

        socket.on('update_state', (data) => {
            document.getElementById('player-list').innerHTML = data.players.map(p => `<li>👤 ${p.name}</li>`).join('');
            latestPlayersData = data.players;
            
            let meObj = data.players.find(p => p.name.toLowerCase() === myPlayerName.toLowerCase());
            if (meObj) myPropertiesData = meObj.properties;
            
            myTurn = data.is_my_turn;
            actionsLeft = data.actions_left;
            myHandData = data.my_hand;
            isDiscardMode = data.is_discard_mode;
            turnDeadline = data.turn_deadline;
            currentTurnName = data.current_turn_name;
            
            // Hand Draw Animation SFX Trigger
            if (myHandData.length > prevHandCount && prevHandCount !== 0) {
                playSound('draw');
            }
            prevHandCount = myHandData.length;

            if (timerInterval) clearInterval(timerInterval);

            if (data.started && !data.game_over) {
                if(document.getElementById('game-screen').classList.contains('hidden')) {
                    switchScreen('game-screen');
                    playSound('draw'); // Initial draw sound
                }

                if (myTurn) {
                    document.getElementById('end-turn-btn').classList.remove('hidden');
                    if(isDiscardMode) document.getElementById('end-turn-btn').classList.add('hidden');
                } else {
                    document.getElementById('end-turn-btn').classList.add('hidden');
                }
                
                document.getElementById('actions-left-count').innerText = actionsLeft;
                updateTimerDisplay();
                timerInterval = setInterval(updateTimerDisplay, 1000);
            }

            // --- Glowing Turn Indicator Logic ---
            const myBoard = document.getElementById('my-board-container');
            if (myTurn) myBoard.classList.add('player-active-glow');
            else myBoard.classList.remove('player-active-glow');

            // Render Opponents
            let oppHtml = "";
            data.players.forEach(p => {
                if (p.name.toLowerCase() === myPlayerName.toLowerCase()) return; 
                
                let bankHtml = p.bank.map(c => createMiniCardDOM(c).outerHTML).join('');
                
                let propGroups = {};
                p.properties.forEach((c, idx) => {
                    let col = c.color || 'Wild';
                    if (!propGroups[col]) propGroups[col] = [];
                    propGroups[col].push({ card: c, index: idx });
                });

                let sortedColors = Object.keys(propGroups).sort((a, b) => (propGroups[b].length >= (setSizes[b]||99)?1:0) - (propGroups[a].length >= (setSizes[a]||99)?1:0));

                let propHtml = sortedColors.map(col => {
                    let required = setSizes[col] || 99;
                    let isComplete = propGroups[col].length >= required;
                    // Mini animation delays for opponent cards
                    let cardsList = propGroups[col].map((item, i) => createMiniCardDOM(item.card, -1, false, i * 40).outerHTML).join('');
                    let bldgs = (p.buildings[col] || []).map(b => createMiniCardDOM(b).outerHTML).join('');
                    
                    return `
                        <div class="bg-black/60 border border-slate-700 rounded p-1 text-center min-w-[75px]">
                            <div class="text-[8px] font-bold uppercase rounded px-1 mb-1 prop-${getCssColorClass(col)} ${isComplete ? 'ring-2 ring-gold-500' : ''}">
                                ${col} (${propGroups[col].length}/${required})
                            </div>
                            <div class="flex flex-col">${cardsList} ${bldgs}</div>
                        </div>`;
                }).join('');
                
                // Active Player Glow for Opponent
                let activeStyle = p.is_turn ? "player-active-glow" : "border-gold-500/30";
                
                oppHtml += `
                    <div class="bg-cardbg border rounded-lg p-3 space-y-2 ${activeStyle}">
                        <div class="flex justify-between items-center text-xs border-b border-gold-500/20 pb-1">
                            <span class="font-bold text-gold-300">${p.name}</span>
                            <div class="flex gap-3 text-[11px]">
                                <span class="text-slate-400">Cards: <b class="text-white">${p.card_count}</b></span>
                                <span class="text-emerald-400">Bank: <b class="text-white">${p.bank_total}M</b></span>
                            </div>
                        </div>
                        <div class="flex flex-wrap gap-2 pt-1">${propHtml || '<span class="text-slate-500 text-xs italic">No properties yet</span>'}</div>
                    </div>`;
            });
            document.getElementById('opponents-container').innerHTML = oppHtml;

            // Render My Hand with Deal Animations
            const handContainer = document.getElementById('my-hand-cards');
            handContainer.innerHTML = "";
            data.my_hand.forEach((c, idx) => {
                handContainer.appendChild(createCardDOM(c, idx, true, idx * 50));
            });

            // Render My Bank & Properties
            if (meObj) {
                document.getElementById('my-bank-total').innerText = `${meObj.bank_total}M`;
                document.getElementById('my-bank-cards').innerHTML = meObj.bank.map((c, i) => createMiniCardDOM(c, -1, false, i*40).outerHTML).join('');

                let myPropGroups = {};
                meObj.properties.forEach((c, idx) => {
                    let col = c.color || 'Wild';
                    if (!myPropGroups[col]) myPropGroups[col] = [];
                    myPropGroups[col].push({card: c, idx: idx});
                });

                let myPropHtml = "";
                for (let col in myPropGroups) {
                    let req = setSizes[col] || 99;
                    let isComplete = myPropGroups[col].length >= req;
                    
                    let cardsList = myPropGroups[col].map((item, i) => createMiniCardDOM(item.card, item.idx, true, i*40).outerHTML).join('');
                    let bldgs = (meObj.buildings[col] || []).map(b => createMiniCardDOM(b).outerHTML).join('');

                    myPropHtml += `
                        <div class="bg-black/50 border border-gold-500/20 rounded p-1.5 flex flex-col items-center min-w-[85px]">
                            <div class="text-[9px] font-bold px-2 py-0.5 rounded w-full text-center mb-1 prop-${getCssColorClass(col)} ${isComplete ? 'ring-2 ring-gold-500' : ''}">
                                ${col} (${myPropGroups[col].length}/${req})
                            </div>
                            <div class="space-y-1 w-full">${cardsList} ${bldgs}</div>
                        </div>`;
                }
                document.getElementById('my-property-sets').innerHTML = myPropHtml || '<span class="text-slate-500 text-xs italic p-2">Lay down properties here</span>';
            }
        });

        // ----------------------------------------------------
        // ACTION LOGIC
        // ----------------------------------------------------
        function handleCardClick(idx) { 
            if (!myTurn) { showToast("Wait", "Please wait for your opponent to finish!", true); return; }
            if (isDiscardMode) {
                playSound('deal');
                socket.emit('discard_card', { room_id: currentRoom, card_index: idx });
                return;
            }
            if (actionsLeft <= 0) { showToast("No Actions", "Used all 3 actions! Click 'Done Turn'.", true); return; }
            
            let card = myHandData[idx];
            if (card.name === "Just Say No!") { showToast("Defense Card", "You can only play this when someone attacks you!", true); return; }

            let optionsHtml = `<p class="text-xs text-slate-300 mb-4 text-center">Choose how to play <b class="text-gold-500">${card.name}</b>:</p><div class="space-y-2">`;
            
            if (card.type === 'Money') {
                optionsHtml += `<button onclick="submitPlayAction(${idx}, 'bank')" class="w-full py-3 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-500 rounded-lg text-emerald-300 font-bold text-sm">💰 Deposit to Bank (${card.value}M)</button>`;
            } else if (card.type === 'Property') {
                if (card.name === "Property Wild Card" || card.name.includes("&")) {
                    optionsHtml += `<button onclick="handleWildPropertyPlacement(${idx}, '${escapeStr(card.name)}')" class="w-full py-3 bg-gold-950/80 hover:bg-gold-900 border border-gold-500 rounded-lg text-gold-300 font-bold text-sm">🏢 Lay on Property Board</button>`;
                } else {
                    optionsHtml += `<button onclick="submitPlayAction(${idx}, 'property')" class="w-full py-3 bg-gold-950/80 hover:bg-gold-900 border border-gold-500 rounded-lg text-gold-300 font-bold text-sm">🏢 Lay on Property Board</button>`;
                }
                if (card.value > 0) optionsHtml += `<button onclick="submitPlayAction(${idx}, 'bank')" class="w-full py-2.5 bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-500/50 rounded-lg text-emerald-400 text-xs font-bold">💰 Deposit as Cash (${card.value}M)</button>`;
            } else if (card.type === 'Building') {
                optionsHtml += `<button onclick="handleBuildingPlacement(${idx})" class="w-full py-3 bg-red-950/80 hover:bg-red-900 border border-red-500 rounded-lg text-white font-bold text-sm">🏠 Build on Complete Set</button>`;
                if (card.value > 0) optionsHtml += `<button onclick="submitPlayAction(${idx}, 'bank')" class="w-full py-2.5 bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-500/50 rounded-lg text-emerald-400 text-xs font-bold">💰 Deposit as Cash (${card.value}M)</button>`;
            } else if (card.type === 'Action') {
                optionsHtml += `<button onclick="routeActionCard(${idx})" class="w-full py-3 bg-gold-600 hover:bg-gold-500 text-black font-extrabold rounded-lg text-sm uppercase">⚡ Execute Action Power</button>`;
                if (card.value > 0) optionsHtml += `<button onclick="submitPlayAction(${idx}, 'bank')" class="w-full py-2.5 bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-500/50 rounded-lg text-emerald-400 text-xs font-bold">💰 Deposit as Cash (${card.value}M)</button>`;
            }
            optionsHtml += `</div>`;
            showModal(`Play Card`, optionsHtml);
        }

        function submitPlayAction(cardIdx, useType, extraData = {}) {
            closeModal();
            playSound('deal');
            socket.emit('play_card', { room_id: currentRoom, card_index: cardIdx, use_type: useType, extra_data: extraData });
        }

        function routeActionCard(idx) {
            closeModal();
            let card = myHandData[idx];
            let useType = "action";
            
            if (card.name === "Sly Deal") startSlyDeal(idx, useType);
            else if (card.name === "Forced Deal") startForcedDeal(idx, useType);
            else if (card.name === "Deal Breaker") startDealBreaker(idx, useType);
            else if (card.name.startsWith("Rent")) startRentAction(idx, useType, card.name);
            else if (card.name === "Debt Collector") {
                showOpponentPickerModal("Debt Collector", (targetOp) => {
                    submitPlayAction(idx, useType, { target_name: targetOp.name.trim() });
                });
            }
            else submitPlayAction(idx, useType); 
        }

        function handleBuildingPlacement(idx) {
            let card = myHandData[idx];
            let isHotel = card.name === 'Hotel';
            
            let meObj = latestPlayersData.find(p => p.name.toLowerCase() === myPlayerName.toLowerCase());
            if (!meObj) return;

            let myPropGroups = {};
            meObj.properties.forEach(p => {
                let col = p.color || 'Wild';
                if (!myPropGroups[col]) myPropGroups[col] = [];
                myPropGroups[col].push(p);
            });
            
            let validSets = [];
            for (let col in myPropGroups) {
                if (col === 'Railroad' || col === 'Utility' || col === 'Wild') continue;
                
                let req = setSizes[col] || 99;
                if (myPropGroups[col].length >= req) {
                    let bldgs = meObj.buildings[col] || [];
                    let hasHouse = bldgs.some(b => b.name === 'House');
                    let hasHotel = bldgs.some(b => b.name === 'Hotel');
                    
                    if (isHotel) {
                        if (hasHouse && !hasHotel) validSets.push(col);
                    } else {
                        if (!hasHouse) validSets.push(col);
                    }
                }
            }
            
            if (validSets.length === 0) {
                let msg = isHotel ? "Requires a Complete Set that already has a House!" : "Requires a Complete Set (Excluding Railroad/Utility)!";
                showToast("Cannot Build", msg, true);
                return;
            }
            
            let html = `<div class="space-y-2">`;
            validSets.forEach(col => {
                html += `<button onclick="submitPlayAction(${idx}, 'building', {color_group: '${col}'})" class="modal-btn prop-${getCssColorClass(col)}">Build on ${col} Set</button>`;
            });
            html += `</div>`;
            showModal(`Place ${card.name}`, html);
        }

        function handleWildPropertyPlacement(cardIdx, cardName) {
            let allowedColors = allColors;
            if (cardName && cardName.includes("&")) {
                allowedColors = allColors.filter(col => cardName.toLowerCase().includes(col.toLowerCase()));
            }

            let html = `<div class="grid grid-cols-2 gap-2">`;
            allowedColors.forEach(col => {
                html += `<button onclick="submitPlayAction(${cardIdx}, 'property', {assigned_color: '${col}'})" class="modal-btn prop-${getCssColorClass(col)}">Assign to ${col}</button>`;
            });
            html += `</div>`;
            showModal("Choose Color Group", html);
        }

        function resolveOpponentModalSelection(index) {
            closeModal();
            let targetOp = latestPlayersData.filter(p => p.name.toLowerCase() !== myPlayerName.toLowerCase())[index];
            if (activeModalOpponentCallback) activeModalOpponentCallback(targetOp);
        }

        function showOpponentPickerModal(actionName, callback) {
            activeModalOpponentCallback = callback;
            let opponents = latestPlayersData.filter(p => p.name.toLowerCase() !== myPlayerName.toLowerCase());
            if (opponents.length === 0) { showToast("Error", "No opponents available!", true); return; }

            let html = `<div class="space-y-2">`;
            opponents.forEach((op, index) => {
                html += `<button class="modal-btn" onclick="resolveOpponentModalSelection(${index})">${op.name}</button>`;
            });
            html += `</div>`;
            showModal(`Select Target for [${actionName}]`, html);
        }

        function startSlyDeal(cardIdx, useType) {
            showOpponentPickerModal("Sly Deal", (op) => { showSlyDealPropertyPicker(cardIdx, useType, op); });
        }
        function showSlyDealPropertyPicker(cardIdx, useType, targetPlayer) {
            if (!targetPlayer.properties || targetPlayer.properties.length === 0) { showToast("Error", "No properties to steal!", true); return; }
            let colorCounts = {};
            targetPlayer.properties.forEach(p => { let col = p.color || 'Wild'; colorCounts[col] = (colorCounts[col] || 0) + 1; });
            
            let validProps = targetPlayer.properties.map((prop, idx) => {
                let col = prop.color || 'Wild';
                return { prop, idx, isComplete: colorCounts[col] >= (setSizes[col] || 99) };
            }).filter(item => !item.isComplete);

            if (validProps.length === 0) { showToast("Error", "Sly Deal cannot target complete sets.", true); return; }
            let html = `<div class="space-y-2">`;
            validProps.forEach(item => {
                html += `<button onclick="submitPlayAction(${cardIdx}, '${useType}', {target_name: '${escapeStr(targetPlayer.name)}', target_prop_idx: ${item.idx}})" class="modal-btn">Steal: ${item.prop.name} (${item.prop.value}M)</button>`;
            });
            html += `</div>`;
            showModal(`Steal from ${targetPlayer.name}`, html);
        }

        function startDealBreaker(cardIdx, useType) {
            showOpponentPickerModal("Deal Breaker", (op) => { showDealBreakerSetPicker(cardIdx, useType, op); });
        }
        function showDealBreakerSetPicker(cardIdx, useType, targetPlayer) {
            if (!targetPlayer.properties || targetPlayer.properties.length === 0) { showToast("Error", "No properties!", true); return; }
            let colorCounts = {}; targetPlayer.properties.forEach(p => { let col = p.color || 'Wild'; colorCounts[col] = (colorCounts[col] || 0) + 1; });
            let completeSets = Object.keys(colorCounts).filter(col => colorCounts[col] >= (setSizes[col] || 99));

            if (completeSets.length === 0) { showToast("Error", "No complete sets to steal!", true); return; }
            let html = `<div class="space-y-2">`;
            completeSets.forEach(col => {
                html += `<button onclick="submitPlayAction(${cardIdx}, '${useType}', {target_name: '${escapeStr(targetPlayer.name)}', color_group: '${col}'})" class="modal-btn prop-${getCssColorClass(col)}">Steal Complete ${col} Set</button>`;
            });
            html += `</div>`;
            showModal(`Deal Breaker: ${targetPlayer.name}`, html);
        }
        
        function startForcedDeal(cardIdx, useType) {
            if (!myPropertiesData || myPropertiesData.length === 0) { showToast("Error", "You have no properties to trade!", true); return; }
            let myColorCounts = {}; myPropertiesData.forEach(p => { let col = p.color || 'Wild'; myColorCounts[col] = (myColorCounts[col] || 0) + 1; });
            let validMyProps = myPropertiesData.map((prop, idx) => ({ prop, idx, isComplete: myColorCounts[prop.color || 'Wild'] >= (setSizes[prop.color || 'Wild'] || 99) })).filter(item => !item.isComplete);
            
            if (validMyProps.length === 0) { showToast("Error", "Cannot trade complete sets!", true); return; }
            let html = `<div class="space-y-2">`;
            validMyProps.forEach(item => {
                html += `<button onclick="closeModal(); showOpponentPickerModal('Forced Deal Target', (op) => showForcedDealTargetPropertyPicker(${cardIdx}, '${useType}', ${item.idx}, op))" class="modal-btn">Give: ${item.prop.name}</button>`;
            });
            html += `</div>`;
            showModal("Select YOUR Property to Trade", html);
        }
        
        function showForcedDealTargetPropertyPicker(cardIdx, useType, myPropIdx, targetPlayer) {
            if (!targetPlayer.properties || targetPlayer.properties.length === 0) { showToast("Error", "They have no properties!", true); return; }
            let colorCounts = {}; targetPlayer.properties.forEach(p => { let col = p.color || 'Wild'; colorCounts[col] = (colorCounts[col] || 0) + 1; });
            let validProps = targetPlayer.properties.map((prop, idx) => ({ prop, idx, isComplete: colorCounts[prop.color || 'Wild'] >= (setSizes[prop.color || 'Wild'] || 99) })).filter(item => !item.isComplete);

            if (validProps.length === 0) { showToast("Error", "Cannot trade complete sets.", true); return; }
            let html = `<div class="space-y-2">`;
            validProps.forEach(item => {
                html += `<button onclick="submitPlayAction(${cardIdx}, '${useType}', {my_prop_idx: ${myPropIdx}, target_name: '${escapeStr(targetPlayer.name)}', target_prop_idx: ${item.idx}})" class="modal-btn">Take: ${item.prop.name}</button>`;
            });
            html += `</div>`;
            showModal(`Take from ${targetPlayer.name}`, html);
        }

        function startRentAction(cardIdx, useType, cardName) {
            let ownedColors = [...new Set(myPropertiesData.map(p => p.color).filter(c => c))];
            if (ownedColors.length === 0) { showToast("Error", "You don't own any properties to charge rent!", true); return; }
            
            let allowedColors = cardName.includes("Wild All Colors") ? ownedColors : ownedColors.filter(col => cardName.toLowerCase().includes(col.toLowerCase()));
            if (allowedColors.length === 0) { showToast("Error", "You do not own properties matching this Rent card's colors!", true); return; }

            let html = `<div class="space-y-2">`;
            allowedColors.forEach(col => {
                html += `<button onclick="closeModal(); showRentTargetPicker(${cardIdx}, '${useType}', '${col}')" class="modal-btn prop-${getCssColorClass(col)}">${col} Set</button>`;
            });
            html += `</div>`;
            showModal("Charge Rent: Choose Color", html);
        }

        function showRentTargetPicker(cardIdx, useType, rentColor) {
            let chargeAll = confirm("Charge rent to ALL players? (OK = All, Cancel = Specific player)");
            let hasDoubleRent = myHandData.some(c => c.name === "Double Rent");
            let isDouble = hasDoubleRent ? confirm("You have a Double Rent card! Use it now? (OK = Yes)") : false;

            if (chargeAll) {
                submitPlayAction(cardIdx, useType, { rent_color: rentColor, target_name: "", double_rent: isDouble });
            } else {
                showOpponentPickerModal("Rent Target", (targetOp) => {
                    submitPlayAction(cardIdx, useType, { rent_color: rentColor, target_name: targetOp.name, double_rent: isDouble });
                });
            }
        }

        // =====================================
        // STRICT DEBT SELECTION MODAL
        // =====================================
        socket.on('request_payment_choice', (data) => {
            playSound('alert');
            let html = `<div class="text-sm text-slate-300 mb-3 text-center">You owe <b class="text-red-400">${data.remaining_due}M</b>. Choose an asset to hand over:</div>`;
            html += `<div class="max-h-[40vh] overflow-y-auto space-y-2 pr-2">`;
            
            let bankOpts = data.options.filter(o => o.source === 'bank');
            let propOpts = data.options.filter(o => o.source === 'prop');
            
            if (bankOpts.length > 0) {
                html += `<div class="text-[10px] font-bold text-emerald-400 uppercase tracking-widest mt-2 border-b border-emerald-500/30 pb-1">From Bank</div>`;
                bankOpts.forEach(opt => {
                    html += `<button onclick="closeModal(); playSound('cash'); socket.emit('submit_payment_choice', {room_id: '${currentRoom}', source: '${opt.source}', real_idx: ${opt.real_idx}});" class="w-full py-2 bg-emerald-950/40 hover:bg-emerald-900 border border-emerald-500/50 text-emerald-100 font-bold rounded flex justify-between px-3"><span>${opt.label}</span><span class="text-emerald-400">${opt.value}M</span></button>`;
                });
            }
            if (propOpts.length > 0) {
                html += `<div class="text-[10px] font-bold text-gold-500 uppercase tracking-widest mt-3 border-b border-gold-500/30 pb-1">From Properties</div>`;
                propOpts.forEach(opt => {
                    html += `<button onclick="closeModal(); playSound('deal'); socket.emit('submit_payment_choice', {room_id: '${currentRoom}', source: '${opt.source}', real_idx: ${opt.real_idx}});" class="w-full py-2 bg-gold-950/40 hover:bg-gold-900 border border-gold-500/50 text-gold-100 font-bold rounded flex justify-between px-3"><span>${opt.label}</span><span class="text-gold-400">${opt.value}M</span></button>`;
                });
            }
            html += `</div>`;
            
            showModal(`Debt Payment Required!`, html, true);
        });

        // =====================================
        // REAL-TIME 10-SEC "JUST SAY NO!" MODAL
        // =====================================
        socket.on('request_just_say_no', (data) => {
            playSound('alert');
            if (data.has_jsn) {
                let timeLeft = 10;
                let html = `
                    <div class="text-center text-slate-300">
                        <p class="text-sm font-bold text-red-400 mb-2">⚡ INCOMING ATTACK ⚡</p>
                        <p class="text-lg">${data.message}</p>
                        <div class="my-5">
                            <span class="text-5xl font-black text-gold-500 gold-text-glow" id="jsn-timer-display">10</span>
                            <span class="text-xs text-slate-400 block mt-1">SECONDS TO RESPOND</span>
                        </div>
                        <div class="space-y-3">
                            <button onclick="respondJSN('${data.action_id}', true)" class="w-full py-3.5 bg-red-900/90 hover:bg-red-800 text-white font-black tracking-widest rounded-lg border-2 border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)] transition-all transform hover:scale-[1.02]">🛑 PLAY JUST SAY NO!</button>
                            <button onclick="respondJSN('${data.action_id}', false)" class="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 font-bold rounded-lg border border-slate-700">Accept Fate</button>
                        </div>
                    </div>
                `;
                showModal("Defend Yourself!", html, true);
                
                if (jsnTimerInterval) clearInterval(jsnTimerInterval);
                jsnTimerInterval = setInterval(() => {
                    timeLeft--;
                    let el = document.getElementById('jsn-timer-display');
                    if (el) el.innerText = timeLeft;
                    if (timeLeft <= 0) {
                        clearInterval(jsnTimerInterval);
                        closeModal();
                    }
                }, 1000);
            } else {
                socket.emit('respond_just_say_no', { room_id: currentRoom, action_id: data.action_id, block: false });
            }
        });

        function respondJSN(actionId, block) {
            if (jsnTimerInterval) clearInterval(jsnTimerInterval);
            closeModal();
            if (block) playSound('deal');
            socket.emit('respond_just_say_no', { room_id: currentRoom, action_id: actionId, block: block });
        }

        function endTurn() { 
            if (!myTurn) { showToast("Wait", "It's not your turn!", true); return; }
            socket.emit('end_turn', { room_id: currentRoom }); 
        }
        function startGame() { socket.emit('start_game', { room_id: currentRoom }); }
    </script>
</body>
</html>
"""

# ==========================================
# 2. PYTHON BACKEND (AI ENGINE + ALL FEATURES)
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
    if not color_str: return 'Wild'
    cleaned = color_str.strip().title()
    for valid_col in SET_SIZES.keys():
        if valid_col.lower() == cleaned.lower(): return valid_col
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
    for _ in range(5): deck.append(Card('Money', '1M Money', 1))
    for _ in range(5): deck.append(Card('Money', '2M Money', 2))
    for _ in range(5): deck.append(Card('Money', '3M Money', 3))
    for _ in range(5): deck.append(Card('Money', '4M Money', 4))
    for _ in range(5): deck.append(Card('Money', '5M Money', 5))
    for _ in range(2): deck.append(Card('Money', '10M Money', 10))
    
    properties_data = [
        ('Brown', 1, 2), ('Light Blue', 1, 3), ('Pink', 2, 3),
        ('Orange', 2, 3), ('Red', 3, 3), ('Yellow', 3, 3),
        ('Green', 4, 3), ('Dark Blue', 4, 2), ('Railroad', 2, 4), ('Utility', 2, 2)
    ]
    for color, value, count in properties_data:
        for _ in range(count): deck.append(Card('Property', f"{color} Property", value, color))
            
    for _ in range(2): deck.append(Card('Property', 'Property Wild Card', 0, None))
    dual_wilds = [("Brown & Light Blue Wild", 1), ("Pink & Orange Wild", 2), ("Red & Yellow Wild", 3), ("Green & Dark Blue Wild", 4), ("Railroad & Utility Wild", 2)]
    for wild_name, val in dual_wilds: deck.append(Card('Property', wild_name, val, None))
            
    for _ in range(3): deck.append(Card('Building', 'House', 3))
    for _ in range(2): deck.append(Card('Building', 'Hotel', 4))

    actions = [
        ("Pass Go", 1, 10), ("Sly Deal", 3, 3), ("Forced Deal", 3, 3), 
        ("Deal Breaker", 5, 2), ("Debt Collector", 5, 3), ("It's My Birthday", 2, 3),
        ("Rent (Brown & Light Blue)", 1, 2), ("Rent (Pink & Orange)", 1, 2), ("Rent (Red & Yellow)", 1, 2),
        ("Rent (Green & Dark Blue)", 1, 2), ("Rent (Railroad & Utility)", 1, 2), ("Rent (Wild All Colors)", 3, 3), 
        ("Double Rent", 1, 2), ("Just Say No!", 4, 3)
    ] 
    for name, value, count in actions:
        for _ in range(count): deck.append(Card('Action', name, value))
            
    random.shuffle(deck)
    return deck

rooms = {} 
sid_to_room = {}  # Global mapping for quick disconnect processing

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

    def reset_game(self):
        self.deck = create_deck()
        self.discard_pile = []
        self.actions_left = 3
        self.started = False
        self.game_over = False
        self.turn_deadline = 0
        self.pending_actions = {}
        self.pending_payments = {}
        self.is_discard_phase = False
        for sid in self.players:
            self.players[sid]["hand"] = []
            self.players[sid]["bank"] = []
            self.players[sid]["properties"] = []
            self.players[sid]["buildings"] = {}

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
            if self.deck: self.players[sid]["hand"].append(self.deck.pop().to_dict())

    def deal_initial_cards(self):
        for sid in self.players: self.draw_cards(sid, 5)
        self.started = True
        self.current_turn_index = random.randint(0, len(self.turn_order) - 1)  # Randomized start for fairness
        self.start_turn()

    def start_turn(self):
        if self.game_over: return
        self.actions_left = 3
        self.is_discard_phase = False
        current_sid = self.turn_order[self.current_turn_index]
        player = self.players[current_sid]
        
        if len(player["hand"]) == 0: self.draw_cards(current_sid, 5)
        else: self.draw_cards(current_sid, 2)
            
        self.turn_deadline = time.time() + 60
        if player.get("is_ai"): socketio.start_background_task(self.run_bot_turn)

    def run_bot_turn(self):
        socketio.sleep(1.5)
        if self.game_over or not self.started: return
        bot_sid = self.turn_order[self.current_turn_index]
        if bot_sid not in self.players or not self.players[bot_sid].get("is_ai"): return
        
        bot = self.players[bot_sid]
        human_sid = next((s for s in self.turn_order if s != bot_sid), None)
        human_player = self.players.get(human_sid)

        if self.bot_difficulty == 'easy':
            while self.actions_left > 0 and bot["hand"]:
                card = bot["hand"].pop(0)
                if card["type"] == "Money": bot["bank"].append(card)
                elif card["type"] == "Property": bot["properties"].append(card)
                else: self.discard_pile.append(card)
                self.actions_left -= 1
                socketio.sleep(0.5)

        elif self.bot_difficulty == 'normal':
            while self.actions_left > 0 and bot["hand"]:
                prop_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Property"), -1)
                money_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Money"), -1)
                if prop_idx != -1: bot["properties"].append(bot["hand"].pop(prop_idx))
                elif money_idx != -1: bot["bank"].append(bot["hand"].pop(money_idx))
                else: self.discard_pile.append(bot["hand"].pop(0))
                self.actions_left -= 1
                socketio.sleep(0.5)

        elif self.bot_difficulty == 'hard':
            while self.actions_left > 0 and bot["hand"]:
                action_played = False
                
                bot_colors = [normalize_color(p.get('color')) for p in bot["properties"] if p.get('color')]
                bot_counts = {}
                for col in bot_colors: bot_counts[col] = bot_counts.get(col, 0) + 1
                
                human_counts = {}
                if human_player:
                    for p in human_player["properties"]:
                        c = normalize_color(p.get('color'))
                        human_counts[c] = human_counts.get(c, 0) + 1

                db_idx = next((i for i, c in enumerate(bot["hand"]) if c["name"] == "Deal Breaker"), -1)
                if db_idx != -1 and human_player:
                    complete_sets = [col for col, cnt in human_counts.items() if cnt >= SET_SIZES.get(col, 99)]
                    if complete_sets:
                        best_set = max(complete_sets, key=lambda c: RENT_TABLE.get(c, [0])[-1])
                        card = bot["hand"].pop(db_idx)
                        self.discard_pile.append(card)
                        
                        def execute_extreme_db(unblocked):
                            if human_sid not in unblocked: return
                            to_steal = [p for p in human_player["properties"] if normalize_color(p.get('color')) == best_set]
                            for p in to_steal:
                                human_player["properties"].remove(p)
                                bot["properties"].append(p)
                            if best_set in human_player["buildings"]:
                                if best_set not in bot["buildings"]: bot["buildings"][best_set] = []
                                bot["buildings"][best_set].extend(human_player["buildings"][best_set])
                                human_player["buildings"][best_set] = []
                            socketio.emit('alert', {'message': f"🔥 Pro Bot shattered your complete {best_set} set!"}, room=self.room_id)

                        trigger_action_with_jsn(self, bot_sid, [human_sid], "Deal Breaker", execute_extreme_db)
                        action_played = True

                if not action_played and human_player:
                    sly_idx = next((i for i, c in enumerate(bot["hand"]) if c["name"] == "Sly Deal"), -1)
                    fd_idx = next((i for i, c in enumerate(bot["hand"]) if c["name"] == "Forced Deal"), -1)
                    
                    if sly_idx != -1 or fd_idx != -1:
                        human_incompletes = [p for p in human_player["properties"] if human_counts.get(normalize_color(p.get("color")), 0) < SET_SIZES.get(normalize_color(p.get("color")), 99)]
                        
                        if human_incompletes:
                            best_prop = None
                            best_score = -1
                            
                            for p in human_incompletes:
                                col = normalize_color(p.get("color"))
                                score = 0
                                if bot_counts.get(col, 0) == SET_SIZES.get(col, 99) - 1:
                                    score = 100 
                                elif human_counts.get(col, 0) == SET_SIZES.get(col, 99) - 1:
                                    score = 50  
                                else:
                                    score = p.get("value", 0) 
                                    
                                if score > best_score:
                                    best_score = score
                                    best_prop = p
                                    
                            if best_prop:
                                if sly_idx != -1:
                                    card = bot["hand"].pop(sly_idx)
                                    self.discard_pile.append(card)
                                    
                                    def execute_extreme_sly(unblocked):
                                        if human_sid not in unblocked: return
                                        if best_prop in human_player["properties"]:
                                            human_player["properties"].remove(best_prop)
                                            bot["properties"].append(best_prop)
                                            check_and_demolish_buildings(human_player)
                                            socketio.emit('alert', {'message': f"🔥 Pro Bot cleverly stole your {best_prop['name']}!"}, room=self.room_id)
                                            
                                    trigger_action_with_jsn(self, bot_sid, [human_sid], "Sly Deal", execute_extreme_sly)
                                    action_played = True
                                
                                elif fd_idx != -1 and bot["properties"]:
                                    bot_incompletes = [p for p in bot["properties"] if bot_counts.get(normalize_color(p.get("color")), 0) < SET_SIZES.get(normalize_color(p.get("color")), 99)]
                                    if bot_incompletes:
                                        worst_bot_prop = min(bot_incompletes, key=lambda p: p.get("value", 0))
                                        
                                        card = bot["hand"].pop(fd_idx)
                                        self.discard_pile.append(card)
                                        
                                        def execute_extreme_forced(unblocked):
                                            if human_sid not in unblocked: return
                                            if best_prop in human_player["properties"] and worst_bot_prop in bot["properties"]:
                                                human_player["properties"].remove(best_prop)
                                                bot["properties"].append(best_prop)
                                                bot["properties"].remove(worst_bot_prop)
                                                human_player["properties"].append(worst_bot_prop)
                                                check_and_demolish_buildings(bot); check_and_demolish_buildings(human_player)
                                                socketio.emit('alert', {'message': f"🔥 Pro Bot swapped its {worst_bot_prop['name']} for your {best_prop['name']}!"}, room=self.room_id)
                                                
                                        trigger_action_with_jsn(self, bot_sid, [human_sid], "Forced Deal", execute_extreme_forced)
                                        action_played = True

                if not action_played and bot_colors:
                    best_rent_amt = 0
                    best_rent_idx = -1
                    best_rent_col = None
                    
                    for i, c in enumerate(bot["hand"]):
                        if "Rent" in c["name"] and "Double" not in c["name"]:
                            c_lower = c["name"].lower()
                            allowed_cols = [col for col in bot_counts.keys() if col.lower() in c_lower or "wild all colors" in c_lower]
                            
                            for col in allowed_cols:
                                tier = RENT_TABLE.get(col, [1])
                                count = bot_counts[col]
                                amt = tier[min(count-1, len(tier)-1)]
                                
                                b_bonus = 0
                                if col in bot["buildings"]:
                                    for b in bot["buildings"][col]:
                                        if b['name'] == 'House': b_bonus += 3
                                        elif b['name'] == 'Hotel': b_bonus += 4
                                amt += b_bonus
                                
                                if amt > best_rent_amt:
                                    best_rent_amt = amt
                                    best_rent_idx = i
                                    best_rent_col = col
                                    
                    if best_rent_idx != -1 and best_rent_col and best_rent_amt >= 2: 
                        card = bot["hand"].pop(best_rent_idx)
                        self.discard_pile.append(card)
                        
                        dr_idx = next((i for i, c in enumerate(bot["hand"]) if c['name'] == "Double Rent"), -1)
                        multiplier = 1
                        if dr_idx != -1 and best_rent_amt >= 3: 
                            multiplier = 2
                            self.discard_pile.append(bot["hand"].pop(dr_idx))
                            
                        total_amt = best_rent_amt * multiplier
                        
                        def execute_extreme_rent(unblocked):
                            if human_sid not in unblocked: return
                            process_payment(human_sid, human_player, bot, total_amt, self)
                            msg = f"🔥 Pro Bot charged {total_amt}M rent on {best_rent_col}! x{multiplier}"
                            socketio.emit('alert', {'message': msg}, room=self.room_id)

                        trigger_action_with_jsn(self, bot_sid, [human_sid], f"Rent ({best_rent_col})", execute_extreme_rent)
                        action_played = True

                if not action_played:
                    bldg_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Building"), -1)
                    if bldg_idx != -1:
                        card = bot["hand"][bldg_idx]
                        is_hotel = card['name'] == 'Hotel'
                        
                        valid_sets = []
                        for col, count in bot_counts.items():
                            if col in ['Railroad', 'Utility', 'Wild']: continue
                            if count >= SET_SIZES.get(col, 99):
                                bldgs = bot["buildings"].get(col, [])
                                has_house = any(b['name'] == 'House' for b in bldgs)
                                has_hotel = any(b['name'] == 'Hotel' for b in bldgs)
                                if is_hotel and has_house and not has_hotel: valid_sets.append(col)
                                elif not is_hotel and not has_house: valid_sets.append(col)
                                
                        if valid_sets:
                            best_build_col = max(valid_sets, key=lambda c: RENT_TABLE.get(c, [0])[-1])
                            c = bot["hand"].pop(bldg_idx)
                            if best_build_col not in bot["buildings"]: bot["buildings"][best_build_col] = []
                            bot["buildings"][best_build_col].append(c)
                            socketio.emit('alert', {'message': f"🤖 Pro Bot built a {c['name']} on {best_build_col}!"}, room=self.room_id)
                            action_played = True

                if not action_played:
                    prop_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Property"), -1)
                    money_idx = next((i for i, c in enumerate(bot["hand"]) if c["type"] == "Money" or (c["type"] == "Action" and c["name"] != "Just Say No!")), -1)

                    if prop_idx != -1:
                        card = bot["hand"].pop(prop_idx)
                        if card['name'] == 'Property Wild Card' or "&" in card['name']:
                            card['is_wild'] = True
                            card['original_name'] = card['name']
                            allowed_colors = list(SET_SIZES.keys())
                            if "&" in card['name']:
                                allowed_colors = [c for c in allowed_colors if c.lower() in card['name'].lower()]
                            
                            best_col = allowed_colors[0]
                            best_score = -1
                            for c in allowed_colors:
                                current = bot_counts.get(c, 0)
                                needed = SET_SIZES.get(c, 99)
                                if current >= needed: continue
                                score = current / needed
                                if score > best_score:
                                    best_score = score
                                    best_col = c
                                    
                            card['color'] = best_col
                            card['name'] = f"Wild ({best_col})"
                            
                        bot["properties"].append(card)
                    elif money_idx != -1:
                        bot["bank"].append(bot["hand"].pop(money_idx))
                    else:
                        self.discard_pile.append(bot["hand"].pop(0))

                self.actions_left -= 1
                socketio.sleep(0.5)

        while len(bot["hand"]) > 7: self.discard_pile.append(bot["hand"].pop())

        if self.check_win(bot_sid):
            self.game_over = True
            socketio.emit('game_over', {'winner': bot['name']}, room=self.room_id)
            broadcast_room_state(self.room_id)
            return
            
        self.next_turn()
        broadcast_room_state(self.room_id)

    def next_turn(self):
        if self.game_over: return
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        self.start_turn()

    def check_win(self, sid):
        player = self.players[sid]
        color_counts = {}
        for p in player["properties"]:
            col = normalize_color(p.get("color"))
            if col != 'Wild': color_counts[col] = color_counts.get(col, 0) + 1
        full_sets = sum(1 for color, count in color_counts.items() if count >= SET_SIZES.get(color, 99))
        return full_sets >= 3

def check_and_demolish_buildings(player):
    for color, bldgs in list(player["buildings"].items()):
        if not bldgs: continue
        current_count = sum(1 for p in player["properties"] if normalize_color(p.get("color")) == color)
        if current_count < SET_SIZES.get(color, 99):
            player["bank"].extend(bldgs)
            player["buildings"][color] = []

def process_payment(debtor_sid, debtor_player, creditor_player, amount_due, room):
    if not debtor_player["bank"] and not debtor_player["properties"]:
        socketio.emit('alert', {'message': f"{debtor_player['name']} has no assets on the table and cannot pay the debt!"}, room=room.room_id)
        return

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
            break

        options = []
        for i, b in enumerate(debtor_player["bank"]): options.append({'source': 'bank', 'real_idx': i, 'label': f"{b['name']}", 'value': b['value']})
        for i, p in enumerate(debtor_player["properties"]): options.append({'source': 'prop', 'real_idx': i, 'label': f"{p['name']}", 'value': p['value']})

        if not options: break

        payment_id = str(random.randint(10000, 99999))
        room.pending_payments[debtor_sid] = {
            'payment_id': payment_id, 'debtor_player': debtor_player, 'creditor_player': creditor_player,
            'remaining_due': remaining_due, 'total_paid': 0
        }
        socketio.emit('request_payment_choice', {'payment_id': payment_id, 'remaining_due': remaining_due, 'options': options}, room=debtor_sid)
        break

@socketio.on('submit_payment_choice')
def handle_payment_choice(data):
    room_id = data['room_id']
    sid = request.sid
    if room_id in rooms:
        room = rooms[room_id]
        if sid in room.pending_payments:
            pay_info = room.pending_payments[sid]
            debtor, creditor = pay_info['debtor_player'], pay_info['creditor_player']
            source, real_idx = data['source'], data['real_idx']
            
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
                    overpaid = abs(pay_info['remaining_due'])
                    socketio.emit('alert', {'message': f"No change given! {debtor['name']} overpaid by {overpaid}M."}, room=room_id)
                else:
                    socketio.emit('alert', {'message': f"{debtor['name']} successfully paid off their debt."}, room=room_id)
                del room.pending_payments[sid]
                broadcast_room_state(room_id)

def trigger_action_with_jsn(room, attacker_sid, target_sids, action_name, execute_callback):
    action_id = str(random.randint(10000, 99999))
    room.pending_actions[action_id] = {
        'attacker': attacker_sid,
        'targets': target_sids.copy(),
        'unblocked_targets': [],
        'name': action_name,
        'callback': execute_callback,
        'current_target_idx': 0,
        'current_jsn_turn': None,
        'last_jsn_player': None,
        'jsn_deadline': 0
    }
    process_next_jsn_target(room, action_id)

def process_next_jsn_target(room, action_id):
    act = room.pending_actions.get(action_id)
    if not act: return
    
    if act['current_target_idx'] >= len(act['targets']):
        act['callback'](act['unblocked_targets'])
        del room.pending_actions[action_id]
        broadcast_room_state(room.room_id)
        return
    
    tsid = act['targets'][act['current_target_idx']]
    act['current_jsn_turn'] = tsid
    act['last_jsn_player'] = None
    ask_jsn(room, action_id)

def ask_jsn(room, action_id):
    act = room.pending_actions.get(action_id)
    if not act: return
    
    current_askee = act['current_jsn_turn']
    target_sid = act['targets'][act['current_target_idx']]
    attacker_sid = act['attacker']
    player = room.players[current_askee]
    
    has_jsn = any(c['name'] == "Just Say No!" for c in player["hand"])
    
    if player.get("is_ai"):
        if has_jsn:
            act['jsn_deadline'] = time.time() + 10 
            
            def ai_jsn_task(r_id, a_id):
                socketio.sleep(2.5) 
                room_ref = rooms.get(r_id)
                if room_ref and a_id in room_ref.pending_actions:
                    ac = room_ref.pending_actions[a_id]
                    if ac['current_jsn_turn'] == current_askee:
                        jsn_idx = next((i for i, c in enumerate(player["hand"]) if c['name'] == "Just Say No!"), -1)
                        if jsn_idx != -1:
                            room_ref.discard_pile.append(player["hand"].pop(jsn_idx))
                            socketio.emit('alert', {'message': f"🤖 {player['name']} suddenly played 'Just Say No!'"}, room=room_ref.room_id)
                            ac['last_jsn_player'] = current_askee
                            ac['current_jsn_turn'] = attacker_sid if current_askee == target_sid else target_sid
                            ask_jsn(room_ref, a_id)
                        else:
                            resolve_jsn_chain(room_ref, a_id)
            
            socketio.start_background_task(ai_jsn_task, room.room_id, action_id)
        else:
            resolve_jsn_chain(room, action_id)
    else:
        if not has_jsn:
            resolve_jsn_chain(room, action_id)
        else:
            act['jsn_deadline'] = time.time() + 10
            msg = f"<b>{room.players[attacker_sid]['name']}</b> played <b>{act['name']}</b> against you!" if current_askee == target_sid else f"<b>{room.players[target_sid]['name']}</b> countered your attack with Just Say No!"
            socketio.emit('request_just_say_no', {'action_id': action_id, 'has_jsn': True, 'message': msg}, room=current_askee)

@socketio.on('respond_just_say_no')
def handle_jsn_response(data):
    room_id = data['room_id']
    sid = request.sid
    if room_id in rooms:
        room = rooms[room_id]
        act = room.pending_actions.get(data['action_id'])
        if act and act['current_jsn_turn'] == sid:
            act['jsn_deadline'] = 0 
            if data['block']:
                player = room.players[sid]
                jsn_idx = next((i for i, c in enumerate(player["hand"]) if c['name'] == "Just Say No!"), -1)
                if jsn_idx != -1:
                    room.discard_pile.append(player["hand"].pop(jsn_idx))
                    act['last_jsn_player'] = sid
                    socketio.emit('alert', {'message': f"💥 {player['name']} played 'Just Say No!'"}, room=room_id)
                    act['current_jsn_turn'] = act['attacker'] if sid == act['targets'][act['current_target_idx']] else act['targets'][act['current_target_idx']]
                    ask_jsn(room, data['action_id'])
                    return
            resolve_jsn_chain(room, data['action_id'])

def resolve_jsn_chain(room, action_id):
    act = room.pending_actions.get(action_id)
    if not act: return
    target_sid = act['targets'][act['current_target_idx']]
    if act['last_jsn_player'] != target_sid:
        act['unblocked_targets'].append(target_sid)
    act['current_target_idx'] += 1
    process_next_jsn_target(room, action_id)

def background_turn_timer():
    while True:
        socketio.sleep(1)
        now = time.time()
        for room_id, room in list(rooms.items()):
            for action_id, act in list(room.pending_actions.items()):
                if act.get('jsn_deadline', 0) > 0 and now >= act['jsn_deadline']:
                    act['jsn_deadline'] = 0
                    resolve_jsn_chain(room, action_id)
                    
            if room.started and not room.game_over and room.turn_deadline > 0:
                if len(room.pending_actions) > 0 or len(room.pending_payments) > 0:
                    room.turn_deadline += 1 
                    continue
                    
                if now >= room.turn_deadline:
                    current_sid = room.turn_order[room.current_turn_index]
                    player = room.players.get(current_sid)
                    if player:
                        if player.get("is_ai"):
                            room.next_turn()
                            broadcast_room_state(room_id)
                            continue
                        while len(player["hand"]) > 7: room.discard_pile.append(player["hand"].pop())
                        room.next_turn()
                        broadcast_room_state(room_id)

@app.route('/')
def index(): return render_template_string(HTML_PAGE)

@socketio.on('create_room')
def handle_create_room(data):
    room_id = data['room_id']
    if room_id in rooms: return emit('error', {'message': 'Room ID already exists!'})
    game_mode, bot_diff = data.get('game_mode', 'multiplayer'), data.get('bot_difficulty', 'normal')
    rooms[room_id] = GameRoom(room_id, data['password'], game_mode, bot_diff)
    rooms[room_id].add_player(request.sid, data['player_name'])
    sid_to_room[request.sid] = room_id  # Track room for disconnects
    join_room(room_id)
    emit('room_joined', {'room_id': room_id, 'is_host': True})
    if game_mode == 'bot':
        rooms[room_id].deal_initial_cards()
        socketio.emit('game_started', room=room_id)
    broadcast_room_state(room_id)

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id']
    if room_id not in rooms or rooms[room_id].password != data['password']: return emit('error', {'message': 'Invalid Room ID or Password!'})
    if rooms[room_id].started or rooms[room_id].game_over: return emit('error', {'message': 'Game already started!'})
    rooms[room_id].add_player(request.sid, data['player_name'])
    sid_to_room[request.sid] = room_id  # Track room for disconnects
    join_room(room_id)
    emit('room_joined', {'room_id': room_id, 'is_host': False})
    broadcast_room_state(room_id)

@socketio.on('send_chat')
def handle_send_chat(data):
    room_id = data.get('room_id')
    sender = data.get('sender', 'Unknown')
    message = data.get('message', '').strip()
    
    if room_id in rooms and message:
        socketio.emit('receive_chat', {
            'sender': sender,
            'message': message
        }, room=room_id)

def auto_resolve_bot_state(room, sid):
    # 1. Resolve pending payments if the disconnected player owed money
    if sid in room.pending_payments:
        pay_info = room.pending_payments.pop(sid)
        debtor = pay_info['debtor_player']
        creditor = pay_info['creditor_player']
        remaining_due = pay_info['remaining_due']
        
        paid_value = 0
        while debtor["bank"] and paid_value < remaining_due:
            card = debtor["bank"].pop(0)
            creditor["bank"].append(card)
            paid_value += card['value']
        
        while debtor["properties"] and paid_value < remaining_due:
            card = debtor["properties"].pop(0)
            creditor["properties"].append(card)
            paid_value += card['value']
            check_and_demolish_buildings(debtor)
        
        socketio.emit('alert', {'message': f"🤖 {debtor['name']} automatically settled their debt."}, room=room.room_id)

    # 2. Resolve pending Just Say No chain if waiting on disconnected player
    for action_id, act in list(room.pending_actions.items()):
        if act['current_jsn_turn'] == sid:
            act['jsn_deadline'] = 0
            resolve_jsn_chain(room, action_id)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    room_id = sid_to_room.get(sid)
    if room_id and room_id in rooms:
        room = rooms[room_id]
        if sid in room.players:
            if not room.started:
                # Remove player from lobby
                del room.players[sid]
                if sid in room.turn_order:
                    room.turn_order.remove(sid)
                if not room.players:
                    del rooms[room_id]
                else:
                    broadcast_room_state(room_id)
            else:
                # Game has started, convert player to Bot instantly
                player = room.players[sid]
                if not player.get('is_ai'):
                    player['is_ai'] = True
                    original_name = player['name']
                    player['name'] += " (Auto-Bot)"
                    socketio.emit('alert', {'message': f"⚠️ {original_name} disconnected! A Bot took over their assets."}, room=room_id)
                    
                    # Auto resolve any blocked states
                    auto_resolve_bot_state(room, sid)
                    
                    # Check if it was their turn
                    if room.turn_order[room.current_turn_index] == sid:
                        socketio.start_background_task(room.run_bot_turn)
                        
                    broadcast_room_state(room_id)
        if sid in sid_to_room:
            del sid_to_room[sid]

@socketio.on('start_game')
def handle_start_game(data):
    if data['room_id'] in rooms:
        rooms[data['room_id']].deal_initial_cards()
        socketio.emit('game_started', room=data['room_id'])
        broadcast_room_state(data['room_id'])

# =====================================
# REMATCH REQUEST LISTENER
# =====================================
@socketio.on('request_rematch')
def handle_rematch(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        room = rooms[room_id]
        if room.game_over:  # Sirf tab jab game completely over ho chuka ho
            room.reset_game()
            room.deal_initial_cards()
            socketio.emit('game_restarted', room=room_id)
            broadcast_room_state(room_id)

@socketio.on('rearrange_wild')
def handle_rearrange_wild(data):
    room_id, sid = data['room_id'], request.sid
    if room_id in rooms:
        room = rooms[room_id]
        if room.game_over: return
        if sid == room.turn_order[room.current_turn_index]:
            player = room.players[sid]
            prop_idx = data.get('prop_idx', -1)
            new_color = normalize_color(data.get('new_color', 'Wild'))
            
            if 0 <= prop_idx < len(player["properties"]):
                card = player["properties"][prop_idx]
                
                if card.get('is_wild'):
                    allowed_colors = list(SET_SIZES.keys())
                    if "&" in card['original_name']:
                        allowed_colors = [c for c in allowed_colors if c.lower() in card['original_name'].lower()]
                    
                    if new_color in allowed_colors:
                        card['color'] = new_color
                        card['name'] = f"Wild ({new_color})"
                        check_and_demolish_buildings(player)
                        emit('alert', {'message': f"Rearranged Wild Card to {new_color}!"}, room=sid)
                        if room.check_win(sid):
                            room.game_over = True
                            socketio.emit('game_over', {'winner': player['name']}, room=room_id)
                        broadcast_room_state(room_id)
                    else:
                        emit('alert', {'message': "Invalid color for this Wild Card!"}, room=sid)

@socketio.on('play_card')
def handle_play_card(data):
    room_id, card_index, use_type, extra_data = data['room_id'], data['card_index'], data['use_type'], data.get('extra_data', {})
    sid = request.sid
    if room_id in rooms and sid in rooms[room_id].players:
        room = rooms[room_id]
        if room.game_over: return
        if sid == room.turn_order[room.current_turn_index]:
            if room.is_discard_phase: return emit('alert', {'message': 'You must discard excess cards first!'}, room=sid)
            if room.actions_left > 0:
                player = room.players[sid]
                if 0 <= card_index < len(player["hand"]):
                    played_card = player["hand"].pop(card_index)
                    if use_type == 'bank': player["bank"].append(played_card)
                    
                    elif use_type == 'property':
                        if played_card['name'] == 'Property Wild Card' or "&" in played_card['name']:
                            played_card['is_wild'] = True
                            played_card['original_name'] = played_card['name']
                            assigned_color = normalize_color(extra_data.get('assigned_color', 'Wild'))
                            played_card['color'] = assigned_color
                            played_card['name'] = f"Wild ({assigned_color})"
                        else: 
                            played_card['color'] = normalize_color(played_card.get('color'))
                        player["properties"].append(played_card)
                        
                    elif use_type == 'building':
                        color_group = normalize_color(extra_data.get('color_group', ''))
                        current_props = [p for p in player["properties"] if normalize_color(p.get("color")) == color_group]
                        
                        if color_group in ['Railroad', 'Utility']:
                            player["hand"].append(played_card)
                            return emit('alert', {'message': f"Cannot build on {color_group}!"}, room=sid)
                            
                        if len(current_props) >= SET_SIZES.get(color_group, 99):
                            if color_group not in player["buildings"]: player["buildings"][color_group] = []
                            bldgs = player["buildings"][color_group]
                            has_house = any(b['name'] == 'House' for b in bldgs)
                            has_hotel = any(b['name'] == 'Hotel' for b in bldgs)
                            
                            if played_card['name'] == 'House':
                                if has_house:
                                    player["hand"].append(played_card)
                                    return emit('alert', {'message': "Maximum 1 House per complete set!"}, room=sid)
                            elif played_card['name'] == 'Hotel':
                                if not has_house or has_hotel:
                                    player["hand"].append(played_card)
                                    return emit('alert', {'message': "Hotel requires a House first, and max 1 Hotel!"}, room=sid)
                                    
                            bldgs.append(played_card)
                            emit('alert', {'message': f"Added {played_card['name']} to your {color_group} set!"}, room=sid)
                        else:
                            player["hand"].append(played_card)
                            return emit('alert', {'message': "Must have a complete set to build!"}, room=sid)

                    elif use_type == 'action':
                        room.discard_pile.append(played_card)
                        
                        if played_card['name'] == "Pass Go": room.draw_cards(sid, 2)
                        
                        elif played_card['name'] == "Sly Deal":
                            target_sid = next((tsid for tsid, p in room.players.items() if p['name'].lower() == extra_data.get('target_name', '').lower() and tsid != sid), None)
                            if target_sid:
                                def execute_sly(unblocked):
                                    if target_sid not in unblocked: return
                                    target_props = room.players[target_sid]["properties"]
                                    color_counts = {}
                                    for p in target_props: color_counts[normalize_color(p.get('color'))] = color_counts.get(normalize_color(p.get('color')), 0) + 1
                                    prop_idx = extra_data.get('target_prop_idx', -1)
                                    if 0 <= prop_idx < len(target_props):
                                        t_col = normalize_color(target_props[prop_idx].get('color'))
                                        if color_counts.get(t_col, 0) >= SET_SIZES.get(t_col, 99): return emit('alert', {'message': "Cannot steal from a complete set!"}, room=sid)
                                        stolen = target_props.pop(prop_idx)
                                        player["properties"].append(stolen)
                                        check_and_demolish_buildings(room.players[target_sid])
                                        emit('alert', {'message': f"Stole {stolen['name']} successfully!"}, room=sid)
                                trigger_action_with_jsn(room, sid, [target_sid], "Sly Deal", execute_sly)
                            else: emit('alert', {'message': "Target not found!"}, room=sid)

                        elif played_card['name'] == "Forced Deal":
                            target_sid = next((tsid for tsid, p in room.players.items() if p['name'].lower() == extra_data.get('target_name', '').lower() and tsid != sid), None)
                            if target_sid:
                                def execute_forced(unblocked):
                                    if target_sid not in unblocked: return
                                    my_props, target_props = player["properties"], room.players[target_sid]["properties"]
                                    my_idx, target_idx = extra_data.get('my_prop_idx'), extra_data.get('target_prop_idx')
                                    if 0 <= my_idx < len(my_props) and 0 <= target_idx < len(target_props):
                                        my_col, their_col = normalize_color(my_props[my_idx].get('color')), normalize_color(target_props[target_idx].get('color'))
                                        my_counts = sum(1 for p in my_props if normalize_color(p.get('color')) == my_col)
                                        their_counts = sum(1 for p in target_props if normalize_color(p.get('color')) == their_col)
                                        if my_counts >= SET_SIZES.get(my_col, 99) or their_counts >= SET_SIZES.get(their_col, 99): return emit('alert', {'message': "Cannot trade from complete sets!"}, room=sid)
                                        my_props.append(target_props.pop(target_idx))
                                        target_props.append(my_props.pop(my_idx))
                                        check_and_demolish_buildings(player); check_and_demolish_buildings(room.players[target_sid])
                                        emit('alert', {'message': "Forced deal completed successfully!"}, room=sid)
                                trigger_action_with_jsn(room, sid, [target_sid], "Forced Deal", execute_forced)

                        elif played_card['name'] == "Deal Breaker":
                            target_sid = next((tsid for tsid, p in room.players.items() if p['name'].lower() == extra_data.get('target_name', '').lower() and tsid != sid), None)
                            if target_sid:
                                def execute_db(unblocked):
                                    if target_sid not in unblocked: return
                                    color_group = normalize_color(extra_data.get('color_group', ''))
                                    target_player = room.players[target_sid]
                                    t_props = [p for p in target_player["properties"] if normalize_color(p.get("color")) == color_group]
                                    if len(t_props) >= SET_SIZES.get(color_group, 99):
                                        for p in t_props: target_player["properties"].remove(p); player["properties"].append(p)
                                        if color_group in target_player["buildings"]:
                                            if color_group not in player["buildings"]: player["buildings"][color_group] = []
                                            player["buildings"][color_group].extend(target_player["buildings"][color_group])
                                            target_player["buildings"][color_group] = []
                                        emit('alert', {'message': f"Stole complete {color_group} set!"}, room=sid)
                                trigger_action_with_jsn(room, sid, [target_sid], "Deal Breaker", execute_db)

                        elif played_card['name'] == "Debt Collector":
                            target_sid = next((tsid for tsid, p in room.players.items() if p['name'].lower() == extra_data.get('target_name', '').strip().lower() and tsid != sid), None)
                            if target_sid:
                                def execute_dc(unblocked):
                                    if target_sid not in unblocked: return
                                    process_payment(target_sid, room.players[target_sid], player, 5, room)
                                    emit('alert', {'message': "Demanded 5M debt successfully!"}, room=sid)
                                trigger_action_with_jsn(room, sid, [target_sid], "Debt Collector", execute_dc)

                        elif played_card['name'] == "It's My Birthday":
                            targets = [tsid for tsid in room.players if tsid != sid]
                            def execute_birthday(unblocked):
                                for tsid in unblocked: process_payment(tsid, room.players[tsid], player, 2, room)
                                if unblocked: emit('alert', {'message': "Collected Birthday gifts!"}, room=sid)
                            trigger_action_with_jsn(room, sid, targets, "It's My Birthday", execute_birthday)

                        elif "Rent" in played_card['name']:
                            rent_color = normalize_color(extra_data.get('rent_color', '').strip())
                            
                            multiplier = 2 if extra_data.get('double_rent', False) else 1
                            if multiplier == 2:
                                dr_idx = next((i for i, c in enumerate(player["hand"]) if c['name'] == "Double Rent"), -1)
                                if dr_idx != -1: 
                                    room.discard_pile.append(player["hand"].pop(dr_idx))
                                else: 
                                    multiplier = 1

                            owned_count = sum(1 for p in player["properties"] if normalize_color(p.get("color")) == rent_color)
                            
                            if owned_count > 0:
                                tier_list = RENT_TABLE.get(rent_color, [1])
                                base_rent = tier_list[min(owned_count - 1, len(tier_list) - 1)]
                                
                                building_bonus = 0
                                if rent_color in player["buildings"]:
                                    for b in player["buildings"][rent_color]:
                                        if b['name'] == 'House': building_bonus += 3
                                        elif b['name'] == 'Hotel': building_bonus += 4
                                        
                                total_rent = (base_rent + building_bonus) * multiplier
                                
                                target_name = extra_data.get('target_name', '').strip()
                                targets = [tsid for tsid, p in room.players.items() if p['name'].lower() == target_name.lower() and tsid != sid] if target_name else [tsid for tsid in room.players if tsid != sid]
                                
                                def execute_rent(unblocked):
                                    for tsid in unblocked: 
                                        process_payment(tsid, room.players[tsid], player, total_rent, room)
                                    if unblocked: 
                                        msg = f"Charged {total_rent}M rent! (Base: {base_rent}M, Buildings: {building_bonus}M) x{multiplier}"
                                        emit('alert', {'message': msg}, room=sid)
                                        
                                trigger_action_with_jsn(room, sid, targets, "Rent Card", execute_rent)

                room.actions_left -= 1
                if len(player["hand"]) == 0: room.draw_cards(sid, 5)

                if room.check_win(sid):
                    room.game_over = True
                    socketio.emit('game_over', {'winner': player['name']}, room=room_id)
                    return broadcast_room_state(room_id)

                if room.actions_left <= 0:
                    if len(player["hand"]) > 7:
                        room.is_discard_phase = True
                        emit('alert', {'message': 'Please discard down to 7 cards.'}, room=sid)
                    else: room.next_turn()
                broadcast_room_state(room_id)

@socketio.on('discard_card')
def handle_discard(data):
    room_id, sid = data['room_id'], request.sid
    if room_id in rooms and sid in rooms[room_id].players:
        room = rooms[room_id]
        if room.game_over: return
        if sid == room.turn_order[room.current_turn_index]:
            player = room.players[sid]
            if 0 <= data['card_index'] < len(player["hand"]):
                room.discard_pile.append(player["hand"].pop(data['card_index']))
                if len(player["hand"]) <= 7:
                    room.is_discard_phase = False
                    room.next_turn()
                broadcast_room_state(room_id)

@socketio.on('end_turn')
def handle_end_turn(data):
    room_id, sid = data['room_id'], request.sid
    if room_id in rooms:
        room = rooms[room_id]
        if room.game_over: return
        if sid == room.turn_order[room.current_turn_index]:
            player = room.players[sid]
            room.is_discard_phase = False
            if len(player["hand"]) > 7:
                room.is_discard_phase = True
                emit('alert', {'message': 'You must discard down to 7 before ending turn.'}, room=sid)
            else: room.next_turn()
            broadcast_room_state(room_id)

def broadcast_room_state(room_id):
    if room_id not in rooms: return
    room = rooms[room_id]
    current_turn_sid = room.turn_order[room.current_turn_index] if (room.started and not room.game_over) else None

    public_players = []
    for sid, p_data in room.players.items():
        public_players.append({
            "name": p_data["name"], "card_count": len(p_data["hand"]), 
            "bank": p_data["bank"], "bank_total": sum(c['value'] for c in p_data["bank"]),
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
            'current_turn_name': room.players[current_turn_sid]['name'] if current_turn_sid else ""
        }, room=sid)

if __name__ == '__main__':
    socketio.start_background_task(background_turn_timer)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)