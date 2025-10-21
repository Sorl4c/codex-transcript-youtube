"""
Centralized Qt Style Sheet used to showcase theming capabilities.
"""

DARK_STYLESHEET = """
QWidget {
    background-color: #1e1f22;
    color: #f0f0f0;
    font-family: "Segoe UI", "Roboto", sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #3a3b3f;
    border-radius: 6px;
    margin-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #9acbff;
    font-weight: bold;
}

QTabWidget::pane {
    border: 1px solid #3a3b3f;
    border-radius: 6px;
    background-color: #24262a;
}

QTabBar::tab {
    background-color: #24262a;
    border: 1px solid #3a3b3f;
    border-bottom-color: #24262a;
    border-radius: 6px 6px 0 0;
    padding: 8px 14px;
    margin-right: 4px;
    color: #b5b8be;
}

QTabBar::tab:selected {
    background-color: #2f3237;
    color: #ffffff;
}

QPushButton {
    background-color: #2d82cc;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    color: #ffffff;
    font-weight: 600;
}

QPushButton:disabled {
    background-color: #4c4f55;
    color: #8f9196;
}

QPushButton:hover {
    background-color: #3991de;
}

QPushButton:pressed {
    background-color: #1f5f99;
}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    background-color: #24262a;
    border: 1px solid #3a3b3f;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #2d82cc;
    selection-color: #ffffff;
}

QTableView {
    gridline-color: #34363a;
    background-color: #24262a;
    alternate-background-color: #292b30;
    border: 1px solid #3a3b3f;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #2f3237;
    color: #c8cbd0;
    padding: 6px;
    border: none;
}

QProgressBar {
    background-color: #2b2d31;
    border: 1px solid #3a3b3f;
    border-radius: 6px;
    text-align: center;
    color: #f0f0f0;
}

QProgressBar::chunk {
    border-radius: 6px;
    background-color: #2d82cc;
}

QScrollBar:vertical {
    background-color: #1e1f22;
    width: 12px;
    margin: 12px 0 12px 0;
}

QScrollBar::handle:vertical {
    background-color: #3c3e44;
    min-height: 24px;
    border-radius: 6px;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    background: none;
    height: 0;
}

QMessageBox {
    background-color: #24262a;
}
"""
