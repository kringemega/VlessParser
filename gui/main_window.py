import sys
import logging
import qrcode
import io
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QProgressBar, QTableWidget, 
    QTableWidgetItem, QHeaderView, QStatusBar, QMessageBox,
    QFrame, QStackedWidget, QButtonGroup, QGridLayout, QMenu, QDialog,
    QLineEdit, QPlainTextEdit, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSlot, QSize, QUrl
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap, QImage, QAction

from core.app_state import AppState
from gui.worker import Worker
from config.enterprise_config import EnterpriseConfig
from gui.styles import ModernStyles

class MainWindow(QMainWindow):
    """Main GUI Window with Modern Sidebar Layout."""
    
    def __init__(self, 
                 app_state: AppState, 
                 worker_factory, 
                 config: EnterpriseConfig,
                 logger: logging.Logger):
        super().__init__()
        self.app_state = app_state
        self.worker_factory = worker_factory
        self.config = config
        self.logger = logger
        self.worker = None
        self.visible_results = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the modern user interface."""
        self.setWindowTitle(f"{self.config.APP_NAME} v{self.config.APP_VERSION}")
        self.setGeometry(100, 100, 980, 720)
        self.setMinimumSize(820, 620)
        if self.config.ICON_PATH:
            self.setWindowIcon(QIcon(self.config.ICON_PATH))
            
        # Apply Dark Theme
        self.setStyleSheet(ModernStyles.DARK_THEME)
            
        # Main Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # 2. Content Area (Stacked Widget)
        self.content_area = QFrame()
        self.content_area.setObjectName("Content")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(18, 16, 18, 16)
        
        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages)
        
        # Create Pages
        self.dashboard_page = self.create_dashboard_page()
        self.scan_page = self.create_scan_page()
        self.results_page = self.create_results_page()
        
        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.scan_page)
        self.pages.addWidget(self.results_page)
        
        main_layout.addWidget(self.content_area)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_sidebar(self):
        """Creates the left navigation sidebar."""
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 18, 0, 18)
        layout.setSpacing(5)
        
        # App Title in Sidebar
        title = QLabel(self.config.APP_NAME)
        title.setObjectName("BrandTitle")
        title.setMinimumHeight(34)
        layout.addWidget(title)
        
        # Navigation Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        
        btn_dashboard = self.create_nav_btn("Dashboard", 0)
        btn_scan = self.create_nav_btn("ScanTest", 1)
        btn_results = self.create_nav_btn("Result Details", 2)
        
        layout.addWidget(btn_dashboard)
        layout.addWidget(btn_scan)
        layout.addWidget(btn_results)
        
        layout.addStretch()
        
        # Version Label
        user = QLabel("Admin User")
        user.setObjectName("UserTitle")
        layout.addWidget(user)

        version = QLabel(f"v{self.config.APP_VERSION}")
        version.setObjectName("VersionText")
        layout.addWidget(version)
        
        # Set default
        btn_dashboard.setChecked(True)
        
        return sidebar

    def create_nav_btn(self, text, index):
        """Helper to create sidebar buttons."""
        btn = QPushButton(text)
        btn.setObjectName("SidebarBtn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.pages.setCurrentIndex(index))
        self.nav_group.addButton(btn)
        return btn

    def create_dashboard_page(self):
        """Creates the Dashboard page with summary cards."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(16)
        
        layout.addLayout(self.create_page_header("Dashboard", "Overview and VLESS statistics"))
        
        # Cards Layout
        cards_layout = QGridLayout()
        cards_layout.setSpacing(18)
        
        self.card_total = self.create_info_card("Total Configs", "0", "queued for testing")
        self.card_working = self.create_info_card("Active / Working", "0", "all successful configs", True)
        self.card_avg_ping = self.create_info_card("Average Ping", "-", "visible results")
        
        cards_layout.addWidget(self.card_total, 0, 0)
        cards_layout.addWidget(self.card_working, 0, 1)
        cards_layout.addWidget(self.card_avg_ping, 0, 2)
        
        layout.addLayout(cards_layout)

        body_layout = QGridLayout()
        body_layout.setSpacing(18)
        body_layout.addWidget(self.create_quick_actions_panel(), 0, 0)
        body_layout.addWidget(self.create_activity_panel(), 0, 1)
        body_layout.addWidget(self.create_top_results_panel(), 1, 0, 1, 2)
        body_layout.setColumnStretch(0, 1)
        body_layout.setColumnStretch(1, 2)
        layout.addLayout(body_layout)
        layout.addStretch()
        return page

    def create_page_header(self, title_text, subtitle_text, trailing_widget=None):
        header = QHBoxLayout()
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel(title_text)
        title.setObjectName("PageTitle")
        subtitle = QLabel(subtitle_text)
        subtitle.setObjectName("PageSubtitle")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        header.addLayout(text_layout)
        header.addStretch()
        if trailing_widget:
            header.addWidget(trailing_widget)
        return header

    def create_info_card(self, title_text, value_text, hint_text="", accent=False):
        card = QFrame()
        card.setObjectName("MetricCardAlt" if accent else "MetricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        
        t = QLabel(title_text)
        t.setObjectName("CardTitle")
        v = QLabel(value_text)
        v.setObjectName("CardValue")
        hint = QLabel(hint_text)
        hint.setObjectName("CardHint")
        
        layout.addWidget(t)
        layout.addWidget(v)
        layout.addWidget(hint)
        return card

    def create_quick_actions_panel(self):
        panel = QFrame()
        panel.setObjectName("Card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("Quick Actions")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)

        scan_btn = QPushButton("New ScanTest")
        scan_btn.setObjectName("GhostBtn")
        scan_btn.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        results_btn = QPushButton("Open Result Details")
        results_btn.setObjectName("GhostBtn")
        results_btn.clicked.connect(lambda: self.pages.setCurrentIndex(2))

        layout.addWidget(scan_btn)
        layout.addWidget(results_btn)
        layout.addStretch()
        return panel

    def create_activity_panel(self):
        panel = QFrame()
        panel.setObjectName("Card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        title = QLabel("System Activity")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)
        self.activity_log = QPlainTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setPlainText("Ready. Start a scan to collect fresh telemetry.")
        layout.addWidget(self.activity_log)
        return panel

    def create_top_results_panel(self):
        panel = QFrame()
        panel.setObjectName("Card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("Top Performing Configs")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)

        self.top_table = self.create_results_table(max_height=190)
        layout.addWidget(self.top_table)
        return panel

    def create_scan_page(self):
        """Creates the Scan page with controls."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("ActionBtn")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setMinimumWidth(82)
        self.start_btn.clicked.connect(self.start_test)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("StopBtn")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setMinimumWidth(82)
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.setEnabled(False)

        controls = QWidget()
        c_layout = QHBoxLayout(controls)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(10)
        c_layout.addWidget(self.stop_btn)
        c_layout.addWidget(self.start_btn)
        layout.addLayout(self.create_page_header("ScanTest Workspace", "Test and validate configurations in real time", controls))

        scan_grid = QGridLayout()
        scan_grid.setSpacing(14)

        progress_panel = QFrame()
        progress_panel.setObjectName("Card")
        p_layout = QVBoxLayout(progress_panel)
        p_layout.setContentsMargins(18, 16, 18, 16)
        p_layout.setSpacing(10)

        progress_header = QHBoxLayout()
        progress_title = QLabel("Active Scan Progress")
        progress_title.setObjectName("PanelTitle")
        self.scan_status_pill = QLabel("Idle")
        self.scan_status_pill.setObjectName("StatusPill")
        progress_header.addWidget(progress_title)
        progress_header.addStretch()
        progress_header.addWidget(self.scan_status_pill)
        p_layout.addLayout(progress_header)
        
        self.status_label = QLabel("Ready to scan")
        self.status_label.setObjectName("MutedText")
        p_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(10)
        p_layout.addWidget(self.progress_bar)

        stats_layout = QGridLayout()
        stats_layout.setSpacing(10)
        self.scan_tested_card = self.create_small_stat("Tested / Total", "0/0")
        self.scan_working_card = self.create_small_stat("Working", "0")
        self.scan_failed_card = self.create_small_stat("Failed", "0", danger=True)
        stats_layout.addWidget(self.scan_tested_card, 0, 0)
        stats_layout.addWidget(self.scan_working_card, 0, 1)
        stats_layout.addWidget(self.scan_failed_card, 0, 2)
        p_layout.addLayout(stats_layout)

        scan_grid.addWidget(progress_panel, 0, 0)
        scan_grid.addWidget(self.create_scan_params_panel(), 0, 1)
        scan_grid.setColumnStretch(0, 2)
        scan_grid.setColumnStretch(1, 1)
        layout.addLayout(scan_grid)

        sources_panel = QFrame()
        sources_panel.setObjectName("Card")
        sources_layout = QVBoxLayout(sources_panel)
        sources_layout.setContentsMargins(18, 16, 18, 16)
        sources_layout.setSpacing(10)

        sources_header = QHBoxLayout()
        sources_title = QLabel("Config Source URLs")
        sources_title.setObjectName("PanelTitle")
        self.sources_status = QLabel("Saved")
        self.sources_status.setObjectName("StatusPill")
        save_sources_btn = QPushButton("Save")
        save_sources_btn.setObjectName("ActionBtn")
        save_sources_btn.setMinimumWidth(78)
        save_sources_btn.clicked.connect(self.save_sources_from_editor)
        reset_sources_btn = QPushButton("Reload")
        reset_sources_btn.setObjectName("GhostBtn")
        reset_sources_btn.setMinimumWidth(82)
        reset_sources_btn.clicked.connect(self.reload_sources_editor)
        sources_header.addWidget(sources_title)
        sources_header.addStretch()
        sources_header.addWidget(reset_sources_btn)
        sources_header.addWidget(save_sources_btn)
        sources_header.addWidget(self.sources_status)
        sources_layout.addLayout(sources_header)

        sources_hint = QLabel("Paste one subscription or raw config-list URL per line. These URLs are saved after exit.")
        sources_hint.setObjectName("MutedText")
        sources_layout.addWidget(sources_hint)

        self.sources_editor = QPlainTextEdit()
        self.sources_editor.setPlaceholderText("https://example.com/subscription.txt")
        self.sources_editor.setMinimumHeight(96)
        self.sources_editor.setMaximumHeight(125)
        self.sources_editor.setPlainText("\n".join(self.get_config_source_urls()))
        self.sources_editor.textChanged.connect(self.mark_sources_dirty)
        sources_layout.addWidget(self.sources_editor)
        layout.addWidget(sources_panel)

        log_panel = QFrame()
        log_panel.setObjectName("Card")
        log_layout = QVBoxLayout(log_panel)
        log_layout.setContentsMargins(18, 16, 18, 16)
        log_layout.setSpacing(10)
        log_title = QLabel("Live Telemetry Log")
        log_title.setObjectName("PanelTitle")
        log_layout.addWidget(log_title)
        self.live_log = QPlainTextEdit()
        self.live_log.setReadOnly(True)
        self.live_log.setMaximumBlockCount(200)
        self.live_log.setMinimumHeight(74)
        self.live_log.setMaximumHeight(105)
        self.live_log.setPlainText("[ready] Waiting for scan input...")
        log_layout.addWidget(self.live_log)
        layout.addWidget(log_panel)

        live_panel = QFrame()
        live_panel.setObjectName("Card")
        live_layout = QVBoxLayout(live_panel)
        live_layout.setContentsMargins(12, 12, 12, 12)
        live_layout.setSpacing(8)
        live_title = QLabel("Live Results")
        live_title.setObjectName("PanelTitle")
        live_layout.addWidget(live_title)
        self.live_table = self.create_results_table(max_height=180)
        live_layout.addWidget(self.live_table)
        layout.addWidget(live_panel)
        
        layout.addStretch()

        scroll = QScrollArea()
        scroll.setObjectName("PageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(page)
        return scroll

    def create_small_stat(self, title_text, value_text, danger=False):
        stat = QFrame()
        stat.setObjectName("Card")
        stat.setMinimumHeight(48)
        stat.setMaximumHeight(54)
        layout = QHBoxLayout(stat)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        title = QLabel(title_text)
        title.setObjectName("CardTitle")
        value = QLabel(value_text)
        value.setObjectName("CardValue")
        value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        value.setStyleSheet("font-size: 18px; color: #ff667c;" if danger else "font-size: 18px;")
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(value)
        return stat

    def create_scan_params_panel(self):
        panel = QFrame()
        panel.setObjectName("Card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("Scan Parameters")
        title.setObjectName("PanelTitle")
        layout.addWidget(title)
        timeout = QLabel(f"Timeout: {self.config.TEST_TIMEOUT} ms")
        timeout.setObjectName("MutedText")
        threads = QLabel(f"Concurrent threads: {self.config.MAX_CONCURRENT_TESTS}")
        threads.setObjectName("MutedText")
        filter_note = QLabel("Upload > 0.0 only")
        filter_note.setObjectName("StatusPill")
        layout.addWidget(timeout)
        layout.addWidget(threads)
        layout.addWidget(filter_note)
        layout.addStretch()
        return panel

    def get_config_source_urls(self):
        urls = []
        for url in self.config.AGGREGATOR_LINKS + self.config.DIRECT_CONFIG_SOURCES:
            if url and url not in urls:
                urls.append(url)
        return urls

    def parse_source_urls(self):
        raw_lines = self.sources_editor.toPlainText().splitlines()
        urls = []
        invalid = []
        for line in raw_lines:
            url = line.strip()
            if not url or url.startswith("#"):
                continue
            parsed = QUrl(url)
            if parsed.scheme() not in {"http", "https"} or not parsed.host():
                invalid.append(url)
                continue
            if url not in urls:
                urls.append(url)
        return urls, invalid

    def mark_sources_dirty(self):
        if hasattr(self, "sources_status"):
            self.sources_status.setText("Unsaved")

    def reload_sources_editor(self):
        self.sources_editor.blockSignals(True)
        self.sources_editor.setPlainText("\n".join(self.get_config_source_urls()))
        self.sources_editor.blockSignals(False)
        self.sources_status.setText("Saved")

    def save_sources_from_editor(self, silent=False):
        urls, invalid = self.parse_source_urls()
        if invalid:
            if not silent:
                QMessageBox.warning(
                    self,
                    "Invalid URLs",
                    "These lines are not valid source URLs:\n\n" + "\n".join(invalid[:10])
                )
            self.sources_status.setText("Invalid")
            return False
        if not urls:
            self.sources_status.setText("Empty")
            return False

        self.config.AGGREGATOR_LINKS = []
        self.config.DIRECT_CONFIG_SOURCES = urls
        self.config.ALL_SOURCES = urls[:]
        self.config._save_sources()

        self.sources_editor.blockSignals(True)
        self.sources_editor.setPlainText("\n".join(urls))
        self.sources_editor.blockSignals(False)
        self.sources_status.setText("Saved")
        self.status_bar.showMessage(f"Saved {len(urls)} source URLs", 3000)
        return True

    def create_results_page(self):
        """Creates the Results page with the table."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(24)

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)
        self.result_filter = QLineEdit()
        self.result_filter.setPlaceholderText("Filter results...")
        self.result_filter.textChanged.connect(self.apply_table_filter)
        toolbar_layout.addWidget(self.result_filter)
        export_btn = QPushButton("Copy Selected")
        export_btn.setObjectName("GhostBtn")
        export_btn.clicked.connect(self.copy_link)
        toolbar_layout.addWidget(export_btn)

        layout.addLayout(self.create_page_header("Result Details", "Only configs with upload speed above 0.0 are shown", toolbar))

        table_panel = QFrame()
        table_panel.setObjectName("Card")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(14, 14, 14, 14)
        table_layout.setSpacing(12)

        self.result_count_label = QLabel("Showing 0 upload-capable configs")
        self.result_count_label.setObjectName("MutedText")
        table_layout.addWidget(self.result_count_label)

        self.table = self.create_results_table()
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        table_layout.addWidget(self.table)
        layout.addWidget(table_panel)
        return page

    def create_results_table(self, max_height=None):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Protocol", "Address", "Ping", "Download", "Upload", "Country"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setShowGrid(False)
        table.setSortingEnabled(True)
        table.verticalHeader().setDefaultSectionSize(44)
        if max_height:
            table.setMaximumHeight(max_height)
            table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return table

    def show_context_menu(self, position):
        """Shows context menu for table rows."""
        menu = QMenu()
        copy_action = QAction("Copy Link", self)
        qr_action = QAction("Show QR Code", self)
        
        menu.addAction(copy_action)
        menu.addAction(qr_action)
        
        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == copy_action:
            self.copy_link()
        elif action == qr_action:
            self.show_qr_code()

    def get_selected_uri(self):
        """Helper to get URI from selected row."""
        row = self.table.currentRow()
        if row >= 0:
            item = self.table.item(row, 0)
            if item:
                return item.data(Qt.ItemDataRole.UserRole)
        return None

    def copy_link(self):
        uri = self.get_selected_uri()
        if uri:
            QApplication.clipboard().setText(uri)
            self.status_bar.showMessage("Link copied to clipboard!", 3000)

    def show_qr_code(self):
        uri = self.get_selected_uri()
        if not uri:
            return
            
        # Generate QR
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to QPixmap
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qimg = QImage.fromData(buffer.getvalue())
        pixmap = QPixmap.fromImage(qimg)
        
        # Show Dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("QR Code")
        dialog.setFixedSize(400, 400)
        layout = QVBoxLayout(dialog)
        
        label = QLabel()
        label.setPixmap(pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        dialog.exec()

    # --- Logic Methods ---

    def start_test(self):
        if self.app_state.is_running:
            return

        if not self.save_sources_from_editor(silent=True):
            QMessageBox.warning(
                self,
                "Invalid URLs",
                "Add at least one valid http:// or https:// source URL before scanning."
            )
            return
            
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.table.setRowCount(0)
        self.live_table.setRowCount(0)
        self.top_table.setRowCount(0)
        self.visible_results = 0
        self.result_count_label.setText("Showing 0 upload-capable configs")
        self.progress_bar.setValue(0)
        self.pages.setCurrentIndex(1) # Switch to Scan page
        self.scan_status_pill.setText("Scanning")
        self.live_log.setPlainText("[start] Scan started")
        self.activity_log.setPlainText("Batch scan started.")
        
        # Reset Dashboard
        self.update_dashboard_card(self.card_total, "0")
        self.update_dashboard_card(self.card_working, "0")
        self.update_dashboard_card(self.card_avg_ping, "-")
        self.update_small_stat(self.scan_tested_card, "0/0")
        self.update_small_stat(self.scan_working_card, "0")
        self.update_small_stat(self.scan_failed_card, "0")
        
        self.worker = self.worker_factory()
        self.worker.update_progress.connect(self.update_progress)
        self.worker.update_status.connect(self.update_status)
        self.worker.result_ready.connect(self.add_result)
        self.worker.finished.connect(self.on_finished)
        self.worker.current_test.connect(self.update_current_test)
        
        self.worker.start()
        
    def stop_test(self):
        if self.app_state.is_running:
            self.app_state.stop_signal.set()
            self.status_label.setText("Stopping...")
            self.scan_status_pill.setText("Stopping")
            self.stop_btn.setEnabled(False)
            
    @pyqtSlot(int)
    def update_progress(self, value):
        if self.app_state.total > 0:
            percent = int((value / self.app_state.total) * 100)
            self.progress_bar.setValue(percent)
            # Update Dashboard Total
            self.update_dashboard_card(self.card_total, str(self.app_state.total))
            self.update_small_stat(self.scan_tested_card, f"{value}/{self.app_state.total}")
            self.update_small_stat(self.scan_working_card, str(self.visible_results))
            self.update_small_stat(self.scan_failed_card, str(self.app_state.failed))
            
    @pyqtSlot(str)
    def update_status(self, text):
        self.status_label.setText(text)
        if hasattr(self, "live_log"):
            self.live_log.appendPlainText(f"[status] {text}")
        if hasattr(self, "activity_log"):
            self.activity_log.appendPlainText(text)
        
    @pyqtSlot(str)
    def update_current_test(self, text):
        self.status_bar.showMessage(f"Testing: {text}")
        
    @pyqtSlot(dict)
    def add_result(self, result):
        upload_speed = self.safe_float(result.get("upload_speed"))
        if upload_speed <= 0.0:
            self.live_log.appendPlainText(
                f"[skip] {result.get('address', 'Unknown')} upload={upload_speed:.2f}"
            )
            return

        self.visible_results += 1
        self.insert_result_row(self.table, result)
        self.insert_result_row(self.live_table, result)
        self.insert_result_row(self.top_table, result)
        self.limit_table_rows(self.live_table, 8)
        self.limit_table_rows(self.top_table, 5)
        self.apply_table_filter()

        ping = self.safe_float(result.get("ping"))
        upload = self.safe_float(result.get("upload_speed"))
        self.live_log.appendPlainText(
            f"[success] {result.get('protocol')} {result.get('address')} ping={ping:.0f}ms upload={upload:.2f}Mbps"
        )

        # Update Dashboard Working Count with visible upload-capable configs.
        self.update_dashboard_card(self.card_working, str(self.visible_results))
        self.update_small_stat(self.scan_working_card, str(self.visible_results))
        self.update_dashboard_card(self.card_avg_ping, f"{int(self.app_state.stats.get('avg_ping', 0))} ms")
        self.result_count_label.setText(f"Showing {self.visible_results} upload-capable configs")
        
    @pyqtSlot()
    def on_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Finished.")
        self.scan_status_pill.setText("Finished")
        self.status_bar.showMessage("Ready")
        
        QMessageBox.information(
            self,
            "Test Complete",
            f"Found {self.visible_results} configs with upload > 0.0 "
            f"out of {self.app_state.found} working configs."
        )
        
        # Switch to results page automatically
        self.pages.setCurrentIndex(2)

    def update_dashboard_card(self, card_widget, value):
        """Helper to update card value."""
        # Find the value label (2nd item in layout)
        value_label = card_widget.findChild(QLabel, "CardValue")
        if value_label:
            value_label.setText(value)

    def update_small_stat(self, card_widget, value):
        value_label = card_widget.findChild(QLabel, "CardValue")
        if value_label:
            value_label.setText(value)

    def insert_result_row(self, table, result):
        table.setSortingEnabled(False)
        row = table.rowCount()
        table.insertRow(row)

        protocol_item = QTableWidgetItem(str(result.get("protocol", "")))
        protocol_item.setData(Qt.ItemDataRole.UserRole, result.get("uri"))

        values = [
            protocol_item,
            QTableWidgetItem(str(result.get("address", ""))),
            QTableWidgetItem(f"{self.safe_float(result.get('ping')):.0f} ms"),
            QTableWidgetItem(f"{self.safe_float(result.get('download_speed')):.2f} Mbps"),
            QTableWidgetItem(f"{self.safe_float(result.get('upload_speed')):.2f} Mbps"),
            QTableWidgetItem(str(result.get("country", ""))),
        ]

        for column, item in enumerate(values):
            item.setData(Qt.ItemDataRole.UserRole + 1, result.get("uri"))
            if column in (2, 3, 4):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, column, item)
        table.setSortingEnabled(True)

    def limit_table_rows(self, table, max_rows):
        while table.rowCount() > max_rows:
            table.removeRow(table.rowCount() - 1)

    def apply_table_filter(self):
        if not hasattr(self, "table") or not hasattr(self, "result_filter"):
            return
        query = self.result_filter.text().strip().lower()
        visible = 0
        for row in range(self.table.rowCount()):
            row_text = " ".join(
                self.table.item(row, col).text().lower()
                for col in range(self.table.columnCount())
                if self.table.item(row, col)
            )
            hidden = query not in row_text
            self.table.setRowHidden(row, hidden)
            if not hidden:
                visible += 1
        self.result_count_label.setText(f"Showing {visible} upload-capable configs")

    def safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
