
class ModernStyles:
    DARK_THEME = """
    QMainWindow {
        background-color: #090d16;
        color: #ffffff;
    }
    QWidget {
        background-color: #090d16;
        color: #f7f7fb;
        font-family: "Segoe UI", "Roboto", sans-serif;
        font-size: 14px;
    }
    QLabel {
        background-color: transparent;
    }
    
    /* Sidebar */
    QFrame#Sidebar {
        background-color: #111020;
        border-right: 1px solid #24213a;
        min-width: 190px;
        max-width: 190px;
    }
    QLabel#BrandTitle {
        color: #ffffff;
        font-size: 15px;
        font-weight: 800;
        padding-left: 18px;
    }
    QLabel#VersionText {
        color: #77778c;
        font-size: 11px;
        padding-left: 20px;
    }
    QLabel#UserTitle {
        color: #ffffff;
        font-weight: 700;
        padding-left: 20px;
    }
    QPushButton#SidebarBtn {
        background-color: transparent;
        color: #a4a3b8;
        border: none;
        text-align: left;
        padding: 12px 14px;
        margin: 2px 8px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 650;
        border-left: 3px solid transparent;
    }
    QPushButton#SidebarBtn:hover {
        background-color: #1b1830;
        color: #ffffff;
    }
    QPushButton#SidebarBtn:checked {
        background-color: #251b49;
        color: #ffffff;
        border-left: 3px solid #9b6cff;
        font-weight: bold;
    }
    
    /* Content Area */
    QFrame#Content {
        background-color: #090d16;
    }
    QScrollArea#PageScroll {
        background-color: transparent;
        border: none;
    }
    QScrollArea#PageScroll > QWidget > QWidget {
        background-color: #090d16;
    }
    QScrollBar:vertical {
        background-color: #0b0e18;
        width: 10px;
        margin: 0;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background-color: #34285d;
        min-height: 36px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #7f56e8;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
        border: none;
        background: none;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }
    QLabel#PageTitle {
        color: #ffffff;
        font-size: 23px;
        font-weight: 850;
    }
    QLabel#PageSubtitle {
        color: #b9d6ff;
        font-size: 13px;
    }
    QLabel#PanelTitle {
        color: #ffffff;
        font-size: 15px;
        font-weight: 800;
    }
    QLabel#MutedText {
        color: #77778c;
        font-size: 12px;
    }
    QLabel#StatusPill {
        background-color: #0c3145;
        border: 1px solid #155d7a;
        border-radius: 5px;
        color: #28d9f2;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
    }
    QLabel#DangerPill {
        background-color: #3b1422;
        border: 1px solid #76233a;
        border-radius: 5px;
        color: #ff667c;
        font-size: 11px;
        font-weight: 700;
        padding: 5px 9px;
    }
    
    /* Buttons */
    QPushButton#ActionBtn {
        background-color: #925dff;
        color: white;
        border: none;
        padding: 8px 14px;
        border-radius: 8px;
        font-weight: 800;
    }
    QPushButton#ActionBtn:hover {
        background-color: #a573ff;
    }
    QPushButton#ActionBtn:disabled {
        background-color: #252235;
        color: #706f82;
    }
    QPushButton#StopBtn {
        background-color: transparent;
        color: #ff667c;
        border: 1px solid #652038;
        padding: 8px 14px;
        border-radius: 8px;
        font-weight: 800;
    }
    QPushButton#StopBtn:hover {
        background-color: #24111d;
    }
    QPushButton#GhostBtn {
        background-color: #151827;
        color: #bdbbd1;
        border: 1px solid #252943;
        padding: 7px 12px;
        border-radius: 7px;
        font-weight: 700;
    }
    QPushButton#GhostBtn:hover {
        background-color: #1d2135;
        color: #ffffff;
    }
    QLineEdit {
        background-color: #141427;
        color: #d9d8e8;
        border: 1px solid #2b2541;
        border-radius: 8px;
        padding: 8px 12px;
        selection-background-color: #7e55e8;
    }
    QPlainTextEdit {
        background-color: #10111e;
        color: #c4c7dc;
        border: 1px solid #2a2840;
        border-radius: 8px;
        padding: 9px;
        font-family: "Cascadia Mono", "Consolas", monospace;
        font-size: 12px;
    }
    
    /* Table */
    QTableWidget {
        background-color: #121324;
        alternate-background-color: #15172a;
        gridline-color: #23233a;
        border: 1px solid #25233b;
        border-radius: 8px;
        selection-background-color: #251b49;
        selection-color: white;
        color: #e8e7f5;
    }
    QHeaderView::section {
        background-color: #161528;
        color: #77778c;
        padding: 9px;
        border: none;
        border-bottom: 1px solid #25233b;
        font-size: 11px;
        font-weight: 800;
    }
    QTableCornerButton::section {
        background-color: #11101e;
        border: none;
    }
    
    /* Progress Bar */
    QProgressBar {
        border: none;
        background-color: #0d1020;
        height: 8px;
        border-radius: 5px;
        text-align: center;
        color: transparent;
    }
    QProgressBar::chunk {
        background-color: #36d7f4;
        border-radius: 5px;
    }
    
    /* Cards/Panels */
    QFrame#Card {
        background-color: #131225;
        border: 1px solid #272340;
        border-radius: 8px;
    }
    QFrame#MetricCard {
        background-color: #141427;
        border: 1px solid #282440;
        border-radius: 12px;
    }
    QFrame#MetricCardAlt {
        background-color: #101d2c;
        border: 1px solid #1d3447;
        border-radius: 12px;
    }
    QLabel#CardTitle {
        font-size: 12px;
        color: #a4a3b8;
        font-weight: bold;
    }
    QLabel#CardValue {
        font-size: 26px;
        color: #ffffff;
        font-weight: 850;
    }
    QLabel#CardHint {
        color: #77778c;
        font-size: 12px;
    }
    QStatusBar {
        background-color: #111020;
        color: #a4a3b8;
        border-top: 1px solid #24213a;
    }
    """
