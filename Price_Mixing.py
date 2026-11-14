# -*- coding: utf-8 -*-
"""
Price_Mixing — Real-time Voice Changer
Works on Windows 7 / 8 / 8.1 / 10 / 11
"""
import sys
import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QSlider, QComboBox, QPushButton,
                              QGroupBox, QCheckBox, QSystemTrayIcon, QMenu,
                              QAction, QStyle, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# ================== الثوابت ==================
SR = 44100
BLOCK = 2048  # أكبر = أكثر استقرارًا

# ================== الثيمات ==================
DARK = """
QMainWindow, QWidget { background: #0A0E27; color: #FFF;
    font-family: 'Segoe UI', 'Tahoma', sans-serif; font-size: 12px; }
QTabWidget::pane { border: 2px solid #1E88E5; border-radius: 8px;
    background: #131A3A; padding: 8px; }
QTabBar::tab { background: #0D1738; color: #64B5F6; padding: 8px 18px;
    border: 2px solid #1E88E5; border-bottom: none;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
    font-weight: bold; margin-right: 3px; }
QTabBar::tab:selected { background: #1E88E5; color: #FFF; }
QTabBar::tab:hover { background: #1565C0; color: #FFF; }
QGroupBox { background: #131A3A; border: 2px solid #1E88E5;
    border-radius: 8px; margin-top: 10px; padding-top: 10px;
    font-weight: bold; color: #64B5F6; }
QGroupBox::title { subcontrol-origin: margin; left: 12px;
    padding: 0 5px; color: #42A5F5; }
QLabel { color: #E3F2FD; }
QSlider::groove:horizontal { height: 6px; background: #1A237E; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #42A5F5; border-radius: 3px; }
QSlider::handle:horizontal { background: #FFF; border: 2px solid #1E88E5;
    width: 14px; height: 14px; margin: -5px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { background: #64B5F6; }
QComboBox { background: #0D1738; border: 2px solid #1E88E5;
    border-radius: 6px; padding: 6px; color: #FFF; min-height: 20px; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox::down-arrow { image: none; border-left: 5px solid transparent;
    border-right: 5px solid transparent; border-top: 6px solid #42A5F5;
    margin-right: 6px; }
QComboBox QAbstractItemView { background: #0D1738; color: #FFF;
    selection-background-color: #1E88E5; border: 1px solid #1E88E5; }
QPushButton { background: #1E88E5; color: #FFF; border: 2px solid #42A5F5;
    border-radius: 8px; padding: 7px 14px; font-weight: bold; }
QPushButton:hover { background: #42A5F5; }
QPushButton:pressed { background: #0D47A1; }
QPushButton#startBtn { background: #00C853; border: 2px solid #69F0AE;
    font-size: 15px; padding: 12px; }
QPushButton#startBtn:hover { background: #69F0AE; }
QPushButton#stopBtn { background: #F44336; border: 2px solid #FF8A80;
    font-size: 15px; padding: 12px; }
QPushButton#toolBtn { background: #7E57C2; border: 2px solid #B39DDB; padding: 6px 12px; }
QPushButton#toolBtn:hover { background: #9575CD; }
QCheckBox { color: #E3F2FD; spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px;
    border: 2px solid #1E88E5; border-radius: 3px; background: #0D1738; }
QCheckBox::indicator:checked { background: #1E88E5; }
"""

LIGHT = """
QMainWindow, QWidget { background: #F5F7FA; color: #0A0E27;
    font-family: 'Segoe UI', 'Tahoma', sans-serif; font-size: 12px; }
QTabWidget::pane { border: 2px solid #1E88E5; border-radius: 8px;
    background: #FFF; padding: 8px; }
QTabBar::tab { background: #E3F2FD; color: #1565C0; padding: 8px 18px;
    border: 2px solid #1E88E5; border-bottom: none;
    border-top-left-radius: 8px; border-top-right-radius: 8px;
    font-weight: bold; margin-right: 3px; }
QTabBar::tab:selected { background: #1E88E5; color: #FFF; }
QTabBar::tab:hover { background: #42A5F5; color: #FFF; }
QGroupBox { background: #FFF; border: 2px solid #1E88E5;
    border-radius: 8px; margin-top: 10px; padding-top: 10px;
    font-weight: bold; color: #1565C0; }
QGroupBox::title { subcontrol-origin: margin; left: 12px;
    padding: 0 5px; color: #0D47A1; background: #F5F7FA; }
QLabel { color: #0A0E27; }
QSlider::groove:horizontal { height: 6px; background: #B0BEC5; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #1E88E5; border-radius: 3px; }
QSlider::handle:horizontal { background: #FFF; border: 2px solid #1E88E5;
    width: 14px; height: 14px; margin: -5px 0; border-radius: 8px; }
QSlider::handle:horizontal:hover { background: #64B5F6; }
QComboBox { background: #FFF; border: 2px solid #1E88E5;
    border-radius: 6px; padding: 6px; color: #0A0E27; min-height: 20px; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox::down-arrow { image: none; border-left: 5px solid transparent;
    border-right: 5px solid transparent; border-top: 6px solid #1565C0;
    margin-right: 6px; }
QComboBox QAbstractItemView { background: #FFF; color: #0A0E27;
    selection-background-color: #42A5F5; border: 1px solid #1E88E5; }
QPushButton { background: #1E88E5; color: #FFF; border: 2px solid #42A5F5;
    border-radius: 8px; padding: 7px 14px; font-weight: bold; }
QPushButton:hover { background: #42A5F5; }
QPushButton:pressed { background: #0D47A1; }
QPushButton#startBtn { background: #00C853; border: 2px solid #66BB6A;
    font-size: 15px; padding: 12px; }
QPushButton#stopBtn { background: #F44336; border: 2px solid #EF5350;
    font-size: 15px; padding: 12px; }
QPushButton#toolBtn { background: #7E57C2; border: 2px solid #B39DDB; padding: 6px 12px; }
QPushButton#toolBtn:hover { background: #9575CD; }
QCheckBox { color: #0A0E27; spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px;
    border: 2px solid #1E88E5; border-radius: 3px; background: #FFF; }
QCheckBox::indicator:checked { background: #1E88E5; }
"""

# ================== الترجمات ==================
T = {
    "ar": {
        "title": "🎤  Price_Mixing",
        "sub": "غيّر صوتك • نقي • واقعي",
        "tab_main": "🎤  رئيسي",
        "tab_eq": "🎚️  معادل",
        "tab_fx": "🎛️  تأثيرات",
        "tab_set": "⚙️  إعدادات",
        # الأجهزة
        "devices": "🎧  الأجهزة",
        "mic": "الميكروفون:",
        "out": "المخرج:",
        "refresh": "🔄 تحديث",
        # الصوت
        "voice": "👤  الصوت",
        "pitch": "نبرة الصوت",
        "presets": "أصوات جاهزة",
        "girl": "👧 بنت", "man": "👨 رجل", "child": "👶 طفل",
        "old": "👴 عجوز", "alien": "👽 فضائي", "robot": "🤖 روبوت",
        # التحسين
        "enhance": "🎛️  التحسين",
        "gain": "التضخيم",
        "nr": "✨ إزالة الضوضاء",
        "cut": "فلتر الترددات",
        "noise": "ضجيج إضافي",
        # EQ
        "eq_box": "🎚️  Equalizer",
        "eq_en": "تفعيل Equalizer",
        "bass": "Bass", "mid": "Mid", "treble": "Treble",
        # FX
        "fx_box": "🎛️  التأثيرات",
        "echo": "الصدى",
        "fb": "تكرار الصدى",
        "reverb": "ريفيرب بسيط",
        "rv_pro": "🏟️  ريفيرب احترافي",
        "rv_en": "تفعيل",
        "rv_type": "النوع:",
        "rv_mix": "المزج",
        "rv_room": "غرفة", "rv_hall": "قاعة", "rv_cathedral": "كاتدرائية",
        "chorus": "🌊  Chorus",
        "chorus_en": "تفعيل",
        "chorus_d": "العمق",
        "chorus_r": "السرعة",
        "duck": "🦆  صوت بطة",
        "duck_en": "تفعيل",
        "duck_a": "الشدة",
        # Settings
        "settings": "⚙️  الإعدادات",
        "theme": "المظهر:",
        "theme_dark": "🌙 ليلي", "theme_light": "☀️ نهاري",
        "language": "اللغة:",
        "tray_info": "البرنامج يعمل في الخلفية\nكليك يمين على الأيقونة للتحكم",
        # Buttons
        "start": "▶️  تشغيل الصوت",
        "stop": "⏹️  إيقاف الصوت",
        "show": "📱 إظهار", "hide": "📱 إخفاء",
        "quit": "❌ خروج",
        "toggle": "▶️ تشغيل/إيقاف",
        # Status
        "ready": "✅ جاهز",
        "running": "🟢 يعمل",
        "error": "❌ خطأ",
        "natural": "طبيعي",
        "man_p": "رجل", "girl_p": "بنت",
    },
    "en": {
        "title": "🎤  Price_Mixing",
        "sub": "Change voice • Clean • Realistic",
        "tab_main": "🎤  Main",
        "tab_eq": "🎚️  EQ",
        "tab_fx": "🎛️  Effects",
        "tab_set": "⚙️  Settings",
        "devices": "🎧  Devices",
        "mic": "Microphone:",
        "out": "Output:",
        "refresh": "🔄 Refresh",
        "voice": "👤  Voice",
        "pitch": "Pitch",
        "presets": "Presets",
        "girl": "👧 Girl", "man": "👨 Man", "child": "👶 Child",
        "old": "👴 Old", "alien": "👽 Alien", "robot": "🤖 Robot",
        "enhance": "🎛️  Enhance",
        "gain": "Gain",
        "nr": "✨ Noise Reduction",
        "cut": "Cutoff Filter",
        "noise": "Extra Noise",
        "eq_box": "🎚️  Equalizer",
        "eq_en": "Enable Equalizer",
        "bass": "Bass", "mid": "Mid", "treble": "Treble",
        "fx_box": "🎛️  Effects",
        "echo": "Echo",
        "fb": "Feedback",
        "reverb": "Simple Reverb",
        "rv_pro": "🏟️  Pro Reverb",
        "rv_en": "Enable",
        "rv_type": "Type:",
        "rv_mix": "Mix",
        "rv_room": "Room", "rv_hall": "Hall", "rv_cathedral": "Cathedral",
        "chorus": "🌊  Chorus",
        "chorus_en": "Enable",
        "chorus_d": "Depth",
        "chorus_r": "Rate",
        "duck": "🦆  Donald Duck",
        "duck_en": "Enable",
        "duck_a": "Amount",
        "settings": "⚙️  Settings",
        "theme": "Theme:",
        "theme_dark": "🌙 Dark", "theme_light": "☀️ Light",
        "language": "Language:",
        "tray_info": "Running in background\nRight-click icon to control",
        "start": "▶️  Start Audio",
        "stop": "⏹️  Stop Audio",
        "show": "📱 Show", "hide": "📱 Hide",
        "quit": "❌ Quit",
        "toggle": "▶️ Start/Stop",
        "ready": "✅ Ready",
        "running": "🟢 Running",
        "error": "❌ Error",
        "natural": "Normal",
        "man_p": "Man", "girl_p": "Girl",
    }
}


class PriceMixing(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "ar"
        self.dark = True
        self.setWindowTitle("Price_Mixing — Voice Changer")
        self.resize(620, 720)

        # Audio state
        self.stream = None
        self.running = False

        # Effects state (all safe defaults)
        self.gain = 1.0
        self.pitch = 1.0
        self.echo_delay = 0.0
        self.echo_fb = 0.0
        self.noise_level = 0.0
        self.noise_reduction = False
        self.lowpass_cut = 16000.0
        self.reverb_simple = 0.0
        # EQ
        self.eq_enabled = False
        self.bass_g = 1.0
        self.mid_g = 1.0
        self.treb_g = 1.0
        # Reverb Pro
        self.rv_pro_on = False
        self.rv_type = "room"
        self.rv_mix = 0.3
        # Chorus
        self.chorus_on = False
        self.chorus_depth = 0.3
        self.chorus_rate = 1.5
        self.chorus_phase = 0.0
        # Duck
        self.duck_on = False
        self.duck_amt = 0.5

        # Buffers (safe sizes)
        self.echo_buf = np.zeros(SR, dtype=np.float32)
        self.rv_buf = np.zeros(SR // 2, dtype=np.float32)
        self.chorus_buf = np.zeros(SR // 4, dtype=np.float32)
        self.noise_prof = None
        self.calib = 0

        # Indices
        self.in_idx_list = []
        self.out_idx_list = []

        self._build_ui()
        self._refresh_devices()
        self._setup_tray()
        self._apply_lang()
        self._apply_theme()

    # ==================== UI BUILD ====================
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(8)
        root.setContentsMargins(10, 10, 10, 10)

        # Header
        head = QHBoxLayout()
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title.setStyleSheet("color: #42A5F5;")
        head.addWidget(self.title, 1)
        root.addLayout(head)

        self.sub = QLabel()
        self.sub.setAlignment(Qt.AlignCenter)
        self.sub.setStyleSheet("color: #90CAF9; font-size: 11px;")
        root.addWidget(self.sub)

        # Tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        self.tab_main = self._make_tab_main()
        self.tab_eq = self._make_tab_eq()
        self.tab_fx = self._make_tab_fx()
        self.tab_set = self._make_tab_settings()

        self.tabs.addTab(self.tab_main, "")
        self.tabs.addTab(self.tab_eq, "")
        self.tabs.addTab(self.tab_fx, "")
        self.tabs.addTab(self.tab_set, "")

        # Start button (fixed at bottom, always visible)
        self.start_btn = QPushButton()
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self._toggle_stream)
        root.addWidget(self.start_btn)

        # Status bar
        self.status = QLabel()
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("color: #64B5F6; font-size: 11px; padding: 4px;")
        root.addWidget(self.status)

    def _make_tab_main(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(8)

        # Devices
        self.g_dev = QGroupBox()
        dv = QVBoxLayout(self.g_dev)
        self.l_mic = QLabel()
        dv.addWidget(self.l_mic)
        self.in_combo = QComboBox()
        dv.addWidget(self.in_combo)
        self.l_out = QLabel()
        dv.addWidget(self.l_out)
        self.out_combo = QComboBox()
        dv.addWidget(self.out_combo)
        self.refresh_btn = QPushButton()
        self.refresh_btn.clicked.connect(self._refresh_devices)
        dv.addWidget(self.refresh_btn)
        lay.addWidget(self.g_dev)

        # Voice
        self.g_voice = QGroupBox()
        vv = QVBoxLayout(self.g_voice)
        self.l_pitch = QLabel()
        self.l_pitch.setStyleSheet("color: #64B5F6; font-weight: bold;")
        vv.addWidget(self.l_pitch)
        self.pitch_sl = QSlider(Qt.Horizontal)
        self.pitch_sl.setRange(50, 200)
        self.pitch_sl.setValue(100)
        self.pitch_sl.valueChanged.connect(self._on_pitch)
        vv.addWidget(self.pitch_sl)

        self.l_pre = QLabel()
        vv.addWidget(self.l_pre)
        preset_row = QHBoxLayout()
        self.preset_btns = {}
        for k, v, pk in [("girl", 155, "girl"), ("man", 78, "man"),
                          ("child", 175, "child"), ("old", 70, "old"),
                          ("alien", 130, "alien"), ("robot", 100, "robot")]:
            b = QPushButton()
            b.clicked.connect(lambda _, val=v, key=pk: self._preset(val, key))
            self.preset_btns[k] = b
            preset_row.addWidget(b)
        vv.addLayout(preset_row)
        lay.addWidget(self.g_voice)

        # Enhance
        self.g_enh = QGroupBox()
        en = QVBoxLayout(self.g_enh)
        self.l_gain = QLabel()
        self.l_gain.setStyleSheet("color: #64B5F6; font-weight: bold;")
        en.addWidget(self.l_gain)
        self.gain_sl = QSlider(Qt.Horizontal)
        self.gain_sl.setRange(0, 300)
        self.gain_sl.setValue(100)
        self.gain_sl.valueChanged.connect(self._on_gain)
        en.addWidget(self.gain_sl)

        self.nr_check = QCheckBox()
        self.nr_check.toggled.connect(self._on_nr)
        en.addWidget(self.nr_check)

        self.l_cut = QLabel()
        en.addWidget(self.l_cut)
        self.cut_sl = QSlider(Qt.Horizontal)
        self.cut_sl.setRange(2000, 16000)
        self.cut_sl.setValue(16000)
        self.cut_sl.valueChanged.connect(self._on_cut)
        en.addWidget(self.cut_sl)

        self.l_noise = QLabel()
        en.addWidget(self.l_noise)
        self.noise_sl = QSlider(Qt.Horizontal)
        self.noise_sl.setRange(0, 100)
        self.noise_sl.setValue(0)
        self.noise_sl.valueChanged.connect(self._on_noise)
        en.addWidget(self.noise_sl)
        lay.addWidget(self.g_enh)

        lay.addStretch()
        return w

    def _make_tab_eq(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(8)

        self.g_eq = QGroupBox()
        el = QVBoxLayout(self.g_eq)
        self.eq_check = QCheckBox()
        self.eq_check.toggled.connect(self._on_eq_toggle)
        el.addWidget(self.eq_check)

        self.l_bass = QLabel()
        self.l_bass.setStyleSheet("color: #64B5F6;")
        el.addWidget(self.l_bass)
        self.bass_sl = QSlider(Qt.Horizontal)
        self.bass_sl.setRange(0, 200)
        self.bass_sl.setValue(100)
        self.bass_sl.valueChanged.connect(self._on_bass)
        el.addWidget(self.bass_sl)

        self.l_mid = QLabel()
        self.l_mid.setStyleSheet("color: #64B5F6;")
        el.addWidget(self.l_mid)
        self.mid_sl = QSlider(Qt.Horizontal)
        self.mid_sl.setRange(0, 200)
        self.mid_sl.setValue(100)
        self.mid_sl.valueChanged.connect(self._on_mid)
        el.addWidget(self.mid_sl)

        self.l_treb = QLabel()
        self.l_treb.setStyleSheet("color: #64B5F6;")
        el.addWidget(self.l_treb)
        self.treb_sl = QSlider(Qt.Horizontal)
        self.treb_sl.setRange(0, 200)
        self.treb_sl.setValue(100)
        self.treb_sl.valueChanged.connect(self._on_treb)
        el.addWidget(self.treb_sl)
        lay.addWidget(self.g_eq)

        lay.addStretch()
        return w

    def _make_tab_fx(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(8)

        # Echo
        self.g_fx = QGroupBox()
        fl = QVBoxLayout(self.g_fx)
        self.l_echo = QLabel()
        self.l_echo.setStyleSheet("color: #64B5F6;")
        fl.addWidget(self.l_echo)
        self.echo_sl = QSlider(Qt.Horizontal)
        self.echo_sl.setRange(0, 100)
        self.echo_sl.setValue(0)
        self.echo_sl.valueChanged.connect(self._on_echo)
        fl.addWidget(self.echo_sl)

        self.l_fb = QLabel()
        fl.addWidget(self.l_fb)
        self.fb_sl = QSlider(Qt.Horizontal)
        self.fb_sl.setRange(0, 80)
        self.fb_sl.setValue(30)
        self.fb_sl.valueChanged.connect(self._on_fb)
        fl.addWidget(self.fb_sl)

        self.l_rv = QLabel()
        fl.addWidget(self.l_rv)
        self.rv_sl = QSlider(Qt.Horizontal)
        self.rv_sl.setRange(0, 100)
        self.rv_sl.setValue(0)
        self.rv_sl.valueChanged.connect(self._on_rv_simple)
        fl.addWidget(self.rv_sl)
        lay.addWidget(self.g_fx)

        # Reverb Pro
        self.g_rvp = QGroupBox()
        rl = QVBoxLayout(self.g_rvp)
        self.rvp_check = QCheckBox()
        self.rvp_check.toggled.connect(self._on_rvp_toggle)
        rl.addWidget(self.rvp_check)

        self.l_rvt = QLabel()
        rl.addWidget(self.l_rvt)
        self.rvt_combo = QComboBox()
        self.rvt_combo.currentIndexChanged.connect(self._on_rvt)
        rl.addWidget(self.rvt_combo)

        self.l_rvm = QLabel()
        rl.addWidget(self.l_rvm)
        self.rvm_sl = QSlider(Qt.Horizontal)
        self.rvm_sl.setRange(0, 100)
        self.rvm_sl.setValue(30)
        self.rvm_sl.valueChanged.connect(self._on_rvm)
        rl.addWidget(self.rvm_sl)
        lay.addWidget(self.g_rvp)

        # Chorus
        self.g_ch = QGroupBox()
        cl = QVBoxLayout(self.g_ch)
        self.ch_check = QCheckBox()
        self.ch_check.toggled.connect(self._on_ch_toggle)
        cl.addWidget(self.ch_check)

        self.l_chd = QLabel()
        cl.addWidget(self.l_chd)
        self.chd_sl = QSlider(Qt.Horizontal)
        self.chd_sl.setRange(0, 100)
        self.chd_sl.setValue(30)
        self.chd_sl.valueChanged.connect(self._on_chd)
        cl.addWidget(self.chd_sl)

        self.l_chr = QLabel()
        cl.addWidget(self.l_chr)
        self.chr_sl = QSlider(Qt.Horizontal)
        self.chr_sl.setRange(1, 50)
        self.chr_sl.setValue(15)
        self.chr_sl.valueChanged.connect(self._on_chr)
        cl.addWidget(self.chr_sl)
        lay.addWidget(self.g_ch)

        # Duck
        self.g_duck = QGroupBox()
        dl = QVBoxLayout(self.g_duck)
        self.duck_check = QCheckBox()
        self.duck_check.toggled.connect(self._on_duck_toggle)
        dl.addWidget(self.duck_check)

        self.l_ducka = QLabel()
        dl.addWidget(self.l_ducka)
        self.ducka_sl = QSlider(Qt.Horizontal)
        self.ducka_sl.setRange(0, 100)
        self.ducka_sl.setValue(50)
        self.ducka_sl.valueChanged.connect(self._on_ducka)
        dl.addWidget(self.ducka_sl)
        lay.addWidget(self.g_duck)

        lay.addStretch()
        return w

    def _make_tab_settings(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(12)

        self.g_set = QGroupBox()
        sl = QVBoxLayout(self.g_set)

        self.l_theme = QLabel()
        sl.addWidget(self.l_theme)
        theme_row = QHBoxLayout()
        self.theme_dark_btn = QPushButton()
        self.theme_dark_btn.setObjectName("toolBtn")
        self.theme_dark_btn.clicked.connect(lambda: self._set_theme(True))
        theme_row.addWidget(self.theme_dark_btn)
        self.theme_light_btn = QPushButton()
        self.theme_light_btn.setObjectName("toolBtn")
        self.theme_light_btn.clicked.connect(lambda: self._set_theme(False))
        theme_row.addWidget(self.theme_light_btn)
        sl.addLayout(theme_row)

        self.l_lang = QLabel()
        sl.addWidget(self.l_lang)
        lang_row = QHBoxLayout()
        ar_btn = QPushButton("🌐 عربي")
        ar_btn.setObjectName("toolBtn")
        ar_btn.clicked.connect(lambda: self._set_lang("ar"))
        lang_row.addWidget(ar_btn)
        en_btn = QPushButton("🌐 English")
        en_btn.setObjectName("toolBtn")
        en_btn.clicked.connect(lambda: self._set_lang("en"))
        lang_row.addWidget(en_btn)
        sl.addLayout(lang_row)
        lay.addWidget(self.g_set)

        info = QLabel("Price_Mixing v5\nStable • Windows 7/8/8.1/10/11")
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #64B5F6; font-size: 11px; padding: 20px;")
        lay.addWidget(info)
        lay.addStretch()
        return w

    # ==================== LANGUAGE ====================
    def _t(self, k):
        return T[self.lang].get(k, k)

    def _set_lang(self, lang):
        self.lang = lang
        self._apply_lang()

    def _apply_lang(self):
        t = self._t
        self.title.setText(t("title"))
        self.sub.setText(t("sub"))
        self.tabs.setTabText(0, t("tab_main"))
        self.tabs.setTabText(1, t("tab_eq"))
        self.tabs.setTabText(2, t("tab_fx"))
        self.tabs.setTabText(3, t("tab_set"))
        self.g_dev.setTitle(t("devices"))
        self.l_mic.setText(t("mic"))
        self.l_out.setText(t("out"))
        self.refresh_btn.setText(t("refresh"))
        self.g_voice.setTitle(t("voice"))
        self.l_pre.setText(t("presets"))
        for k, b in self.preset_btns.items():
            b.setText(t(k))
        self.g_enh.setTitle(t("enhance"))
        self.nr_check.setText(t("nr"))
        self.g_eq.setTitle(t("eq_box"))
        self.eq_check.setText(t("eq_en"))
        self.g_fx.setTitle(t("fx_box"))
        self.g_rvp.setTitle(t("rv_pro"))
        self.rvp_check.setText(t("rv_en"))
        self.l_rvt.setText(t("rv_type"))
        # reverb combo
        self.rvt_combo.blockSignals(True)
        cur = self.rvt_combo.currentIndex()
        self.rvt_combo.clear()
        self.rvt_combo.addItems([t("rv_room"), t("rv_hall"), t("rv_cathedral")])
        self.rvt_combo.setCurrentIndex(max(0, cur))
        self.rvt_combo.blockSignals(False)
        self.g_ch.setTitle(t("chorus"))
        self.ch_check.setText(t("chorus_en"))
        self.g_duck.setTitle(t("duck"))
        self.duck_check.setText(t("duck_en"))
        self.g_set.setTitle(t("settings"))
        self.l_theme.setText(t("theme"))
        self.theme_dark_btn.setText(t("theme_dark"))
        self.theme_light_btn.setText(t("theme_light"))
        self.l_lang.setText(t("language"))
        self.start_btn.setText(t("stop") if self.running else t("start"))

        # Dynamic labels refresh
        self._on_pitch(self.pitch_sl.value())
        self._on_gain(self.gain_sl.value())
        self._on_echo(self.echo_sl.value())
        self._on_fb(self.fb_sl.value())
        self._on_noise(self.noise_sl.value())
        self._on_cut(self.cut_sl.value())
        self._on_rv_simple(self.rv_sl.value())
        self._on_bass(self.bass_sl.value())
        self._on_mid(self.mid_sl.value())
        self._on_treb(self.treb_sl.value())
        self._on_rvm(self.rvm_sl.value())
        self._on_chd(self.chd_sl.value())
        self._on_chr(self.chr_sl.value())
        self._on_ducka(self.ducka_sl.value())

        if hasattr(self, 'tray_show_act'):
            self.tray_show_act.setText(t("show"))
            self.tray_toggle_act.setText(t("toggle"))
            self.tray_quit_act.setText(t("quit"))

        if not self.running:
            self.status.setText(t("ready"))

    # ==================== THEME ====================
    def _set_theme(self, dark):
        self.dark = dark
        self._apply_theme()

    def _apply_theme(self):
        app = QApplication.instance()
        app.setStyleSheet(DARK if self.dark else LIGHT)

    # ==================== DEVICES ====================
    def _refresh_devices(self):
        try:
            devices = sd.query_devices()
            cur_in = self.in_combo.currentText()
            cur_out = self.out_combo.currentText()
            self.in_combo.clear()
            self.out_combo.clear()
            self.in_idx_list = []
            self.out_idx_list = []

            for i, d in enumerate(devices):
                try:
                    if d['max_input_channels'] > 0:
                        self.in_combo.addItem(f"{i}: {d['name']}")
                        self.in_idx_list.append(i)
                    if d['max_output_channels'] > 0:
                        self.out_combo.addItem(f"{i}: {d['name']}")
                        self.out_idx_list.append(i)
                except Exception:
                    continue

            if cur_in:
                idx = self.in_combo.findText(cur_in)
                if idx >= 0:
                    self.in_combo.setCurrentIndex(idx)
            if cur_out:
                idx = self.out_combo.findText(cur_out)
                if idx >= 0:
                    self.out_combo.setCurrentIndex(idx)

            # Auto-select CABLE for output
            for i in range(self.out_combo.count()):
                if "CABLE" in self.out_combo.itemText(i).upper():
                    self.out_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            self.status.setText(f"Device error: {e}")

    # ==================== SLIDER HANDLERS ====================
    def _on_pitch(self, v):
        self.pitch = v / 100.0
        t = self._t
        if v < 90:
            name = f"{t('man_p')} ({self.pitch:.2f}x)"
        elif v > 110:
            name = f"{t('girl_p')} ({self.pitch:.2f}x)"
        else:
            name = f"{t('natural')} ({self.pitch:.2f}x)"
        self.l_pitch.setText(f"{t('pitch')}: {name}")

    def _on_gain(self, v):
        self.gain = v / 100.0
        self.l_gain.setText(f"{self._t('gain')}: {v}%")

    def _on_echo(self, v):
        self.echo_delay = (v / 100.0) * 0.6
        self.l_echo.setText(f"{self._t('echo')}: {v}%")

    def _on_fb(self, v):
        self.echo_fb = v / 100.0
        self.l_fb.setText(f"{self._t('fb')}: {v}%")

    def _on_noise(self, v):
        self.noise_level = v / 100.0
        self.l_noise.setText(f"{self._t('noise')}: {v}%")

    def _on_cut(self, v):
        self.lowpass_cut = float(v)
        self.l_cut.setText(f"{self._t('cut')}: {v} Hz")

    def _on_rv_simple(self, v):
        self.reverb_simple = v / 100.0
        self.l_rv.setText(f"{self._t('reverb')}: {v}%")

    def _on_nr(self, checked):
        self.noise_reduction = checked
        if checked:
            self.noise_prof = None
            self.calib = 0

    # EQ
    def _on_eq_toggle(self, c):
        self.eq_enabled = c

    def _on_bass(self, v):
        self.bass_g = v / 100.0
        self.l_bass.setText(f"{self._t('bass')}: {v}%")

    def _on_mid(self, v):
        self.mid_g = v / 100.0
        self.l_mid.setText(f"{self._t('mid')}: {v}%")

    def _on_treb(self, v):
        self.treb_g = v / 100.0
        self.l_treb.setText(f"{self._t('treble')}: {v}%")

    # Reverb Pro
    def _on_rvp_toggle(self, c):
        self.rv_pro_on = c

    def _on_rvt(self, i):
        self.rv_type = ["room", "hall", "cathedral"][i] if 0 <= i < 3 else "room"

    def _on_rvm(self, v):
        self.rv_mix = v / 100.0
        self.l_rvm.setText(f"{self._t('rv_mix')}: {v}%")

    # Chorus
    def _on_ch_toggle(self, c):
        self.chorus_on = c

    def _on_chd(self, v):
        self.chorus_depth = v / 100.0
        self.l_chd.setText(f"{self._t('chorus_d')}: {v}%")

    def _on_chr(self, v):
        self.chorus_rate = v / 10.0
        self.l_chr.setText(f"{self._t('chorus_r')}: {self.chorus_rate:.1f} Hz")

    # Duck
    def _on_duck_toggle(self, c):
        self.duck_on = c

    def _on_ducka(self, v):
        self.duck_amt = v / 100.0
        self.l_ducka.setText(f"{self._t('duck_a')}: {v}%")

    def _preset(self, pitch_val, key):
        self.pitch_sl.setValue(pitch_val)
        if key == "girl":
            self.rv_sl.setValue(10); self.cut_sl.setValue(12000)
        elif key == "man":
            self.rv_sl.setValue(5); self.cut_sl.setValue(10000)
        elif key == "child":
            self.rv_sl.setValue(15); self.cut_sl.setValue(14000)
        elif key == "old":
            self.rv_sl.setValue(25); self.cut_sl.setValue(7000)

    # ==================== DSP ====================
    def _lowpass(self, audio, cutoff):
        try:
            if cutoff >= SR / 2 - 200:
                return audio
            b, a = butter(2, cutoff / (SR / 2), btype='low')
            return lfilter(b, a, audio).astype(np.float32)
        except Exception:
            return audio

    def _highpass(self, audio, cutoff=80):
        try:
            if cutoff <= 20:
                return audio
            b, a = butter(2, cutoff / (SR / 2), btype='high')
            return lfilter(b, a, audio).astype(np.float32)
        except Exception:
            return audio

    def _pitch_shift(self, audio, factor):
        try:
            if abs(factor - 1.0) < 0.02:
                return audio
            n = len(audio)
            new_n = max(int(n / factor), 2)
            idx_old = np.arange(n, dtype=np.float32)
            idx_new = np.linspace(0, n - 1, new_n).astype(np.float32)
            shifted = np.interp(idx_new, idx_old, audio).astype(np.float32)
            if len(shifted) < n:
                shifted = np.pad(shifted, (0, n - len(shifted)))
            else:
                shifted = shifted[:n]
            return shifted
        except Exception:
            return audio

    def _noise_reduce(self, audio):
        try:
            if self.noise_prof is None:
                self.noise_prof = np.abs(np.fft.rfft(audio))
                return audio
            spec = np.fft.rfft(audio)
            mag = np.abs(spec)
            phase = np.angle(spec)
            reduced = np.maximum(mag - self.noise_prof * 0.7, mag * 0.15)
            out = np.fft.irfft(reduced * np.exp(1j * phase), n=len(audio))
            self.noise_prof = 0.95 * self.noise_prof + 0.05 * mag
            return out.astype(np.float32)
        except Exception:
            return audio

    def _apply_eq(self, audio):
        try:
            if abs(self.bass_g - 1.0) < 0.02 and \
               abs(self.mid_g - 1.0) < 0.02 and \
               abs(self.treb_g - 1.0) < 0.02:
                return audio
            bass = self._lowpass(audio, 300)
            treble = self._highpass(audio, 3000)
            mid = audio - bass - treble
            return (bass * self.bass_g +
                    mid * self.mid_g +
                    treble * self.treb_g).astype(np.float32)
        except Exception:
            return audio

    def _apply_chorus(self, audio):
        try:
            n = len(audio)
            buf_len = len(self.chorus_buf)
            if n >= buf_len:
                self.chorus_buf = np.concatenate([self.chorus_buf[n:], audio])
                return audio
            t = np.arange(n) / SR
            lfo = np.sin(2 * np.pi * self.chorus_rate * t + self.chorus_phase)
            self.chorus_phase = (self.chorus_phase +
                                 2 * np.pi * self.chorus_rate * n / SR) % (2 * np.pi)
            base = int(0.02 * SR)
            depth = int(self.chorus_depth * 0.008 * SR)
            delays = np.clip(base + (lfo * depth).astype(int),
                             1, buf_len - 1)
            delayed = self.chorus_buf[buf_len - delays]
            self.chorus_buf = np.concatenate([self.chorus_buf[n:], audio])
            return (audio * 0.7 + delayed * 0.5).astype(np.float32)
        except Exception:
            return audio

    def _apply_duck(self, audio):
        try:
            audio = self._pitch_shift(audio, 1.7)
            t = np.arange(len(audio)) / SR
            tremolo = 1.0 - self.duck_amt * 0.4 * (
                0.5 + 0.5 * np.sin(2 * np.pi * 25 * t))
            audio = audio * tremolo
            return self._highpass(audio, 500)
        except Exception:
            return audio

    def _apply_reverb_pro(self, audio):
        try:
            if self.rv_type == "room":
                decay, d = 0.4, int(0.029 * SR)
            elif self.rv_type == "hall":
                decay, d = 0.65, int(0.05 * SR)
            else:
                decay, d = 0.82, int(0.09 * SR)
            n = len(audio)
            bl = len(self.rv_buf)
            if n >= bl:
                return audio
            delayed = self.rv_buf[:n].copy()
            out = audio + delayed * decay * self.rv_mix
            self.rv_buf[:n] = audio + delayed * decay
            self.rv_buf = np.roll(self.rv_buf, -n)
            return out.astype(np.float32)
        except Exception:
            return audio

    # ==================== MAIN CALLBACK ====================
    def _callback(self, indata, outdata, frames, time_info, status):
        try:
            audio = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()
            audio = audio.astype(np.float32, copy=False)

            # Highpass
            audio = self._highpass(audio, 80)

            # Noise reduction
            if self.noise_reduction:
                if self.calib < 10:
                    self._noise_reduce(audio)
                    self.calib += 1
                else:
                    audio = self._noise_reduce(audio)

            # Pitch or Duck
            if self.duck_on:
                audio = self._apply_duck(audio)
            elif abs(self.pitch - 1.0) > 0.02:
                audio = self._pitch_shift(audio, self.pitch)

            # EQ
            if self.eq_enabled:
                audio = self._apply_eq(audio)

            # Lowpass
            if self.lowpass_cut < SR / 2 - 200:
                audio = self._lowpass(audio, self.lowpass_cut)

            # Gain
            audio = audio * self.gain

            # Extra noise
            if self.noise_level > 0.001:
                audio = audio + np.random.randn(len(audio)).astype(
                    np.float32) * self.noise_level * 0.2

            # Echo
            if self.echo_delay > 0.01:
                n = len(audio)
                bl = len(self.echo_buf)
                if n < bl:
                    delayed = self.echo_buf[:n].copy()
                    audio = audio + delayed * 0.6
                    self.echo_buf[:n] = audio + delayed * self.echo_fb
                    self.echo_buf = np.roll(self.echo_buf, -n)

            # Simple reverb
            if self.reverb_simple > 0.01:
                n = len(audio)
                bl = len(self.rv_buf)
                if n < bl:
                    rev = self.rv_buf[:n].copy()
                    audio = audio + rev * self.reverb_simple * 0.5
                    self.rv_buf[:n] = audio * self.reverb_simple
                    self.rv_buf = np.roll(self.rv_buf, -n)

            # Pro reverb
            if self.rv_pro_on:
                audio = self._apply_reverb_pro(audio)

            # Chorus
            if self.chorus_on:
                audio = self._apply_chorus(audio)

            # Safe clip
            audio = np.clip(audio, -1.0, 1.0).astype(np.float32)

            # Output stereo
            if outdata.ndim > 1:
                outdata[:, 0] = audio
                outdata[:, 1] = audio
            else:
                outdata[:, 0] = audio

        except Exception:
            # On error, pass through silence (never crash the stream)
            outdata.fill(0)

    # ==================== STREAM ====================
    def _toggle_stream(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        try:
            if not self.in_idx_list or not self.out_idx_list:
                self._refresh_devices()
                if not self.in_idx_list or not self.out_idx_list:
                    self.status.setText(self._t("error") + ": no devices")
                    return

            in_idx = self.in_idx_list[max(0, self.in_combo.currentIndex())]
            out_idx = self.out_idx_list[max(0, self.out_combo.currentIndex())]

            self.stream = sd.Stream(
                samplerate=SR,
                blocksize=BLOCK,
                device=(in_idx, out_idx),
                channels=(1, 2),
                dtype='float32',
                callback=self._callback,
                latency='high'  # أكثر استقرارًا
            )
            self.stream.start()
            self.running = True
            self.start_btn.setText(self._t("stop"))
            self.start_btn.setObjectName("stopBtn")
            self.start_btn.setStyleSheet("")
            self.start_btn.style().unpolish(self.start_btn)
            self.start_btn.style().polish(self.start_btn)
            self.status.setText(self._t("running"))

            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Price_Mixing",
                    self._t("tray_info"),
                    QSystemTrayIcon.Information, 2000)
        except Exception as e:
            self.running = False
            self.status.setText(f"{self._t('error')}: {str(e)[:50]}")
            self.start_btn.setText(self._t("start"))
            self.start_btn.setObjectName("startBtn")
            self.start_btn.setStyleSheet("")
            self.start_btn.style().unpolish(self.start_btn)
            self.start_btn.style().polish(self.start_btn)

    def _stop(self):
        try:
            if self.stream is not None:
                self.stream.stop()
                self.stream.close()
        except Exception:
            pass
        self.stream = None
        self.running = False
        self.start_btn.setText(self._t("start"))
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setStyleSheet("")
        self.start_btn.style().unpolish(self.start_btn)
        self.start_btn.style().polish(self.start_btn)
        self.status.setText(self._t("ready"))

    # ==================== TRAY ====================
    def _setup_tray(self):
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(
                self.style().standardIcon(QStyle.SP_ComputerIcon))
            self.tray_icon.setToolTip("Price_Mixing")

            self.tray_menu = QMenu()
            self.tray_show_act = QAction(self._t("show"), self)
            self.tray_show_act.triggered.connect(self._show_window)
            self.tray_menu.addAction(self.tray_show_act)

            self.tray_toggle_act = QAction(self._t("toggle"), self)
            self.tray_toggle_act.triggered.connect(self._toggle_stream)
            self.tray_menu.addAction(self.tray_toggle_act)

            self.tray_menu.addSeparator()

            self.tray_quit_act = QAction(self._t("quit"), self)
            self.tray_quit_act.triggered.connect(self._real_quit)
            self.tray_menu.addAction(self.tray_quit_act)

            self.tray_icon.setContextMenu(self.tray_menu)
            self.tray_icon.activated.connect(self._tray_click)
            self.tray_icon.show()
        except Exception:
            self.tray_icon = None

    def _tray_click(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        if self.tray_icon is not None:
            self.tray_icon.showMessage(
                "Price_Mixing",
                self._t("tray_info"),
                QSystemTrayIcon.Information, 2000)

    def _real_quit(self):
        self._stop()
        if self.tray_icon is not None:
            self.tray_icon.hide()
        QApplication.quit()


# ==================== MAIN ====================
def main():
    QApplication.setQuitOnLastWindowClosed(False)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PriceMixing()
    window.show()
    QTimer.singleShot(1500, window._start)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()