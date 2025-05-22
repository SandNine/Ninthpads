# -*- coding: utf-8 -*-
import sys
import os
import json # Para o formato .nxt
from PyQt6.QtCore import Qt, QSize, QTimer, QEvent, QSettings, QByteArray, QStandardPaths, pyqtSignal, QPointF, QRect, QRectF, QPoint, QRect
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QHBoxLayout,  
    QLabel, QTabWidget, QLineEdit, QToolBar, QMenuBar, QStatusBar, QFileDialog,
    QMessageBox, QFontDialog, QColorDialog, QMenu, QToolButton, QTabBar, QComboBox,
    QSpinBox, QDialog, QScrollArea, QFrame, QPushButton, QStyleFactory, QSplitter,
    QSizePolicy, QInputDialog, QCheckBox, QSlider, QFontComboBox, QWidget, QTextEdit, QRadioButton, QButtonGroup,
    QStackedWidget, QStackedLayout, QStyle, QStyleOptionTab
)
from PyQt6.QtGui import (
    QAction, QFont, QIcon, QColor, QPalette, QTextCursor, QTextCharFormat, QTextDocument,
    QFontDatabase, QLinearGradient, QPainter, QSyntaxHighlighter, QGuiApplication, QPen, QPainterPath,
    QTextFormat, QTextOption, QActionGroup, QBrush, QTextBlockFormat, QGradient
)

import vcolorpicker
import uuid
from uuid import uuid4
import shutil
from datetime import datetime

# --- Constants ---
APP_NAME = "Ninthpads" # Nome atualizado
ORG_NAME = "Diversion Studios"

# Caminhos absolutos do executável
import sys
from pathlib import Path

if hasattr(sys, "_MEIPASS"):
    BASE_PATH = Path(sys._MEIPASS)
else:
    BASE_PATH = Path(sys.argv[0]).resolve().parent

ICON_PATH = str(BASE_PATH / "icons")
LIGHT_ICON_PATH = str(BASE_PATH / "light_icons")
UNSAVED_DIR = str(BASE_PATH / "unsaved_files")
SESSION_FILE = str(BASE_PATH / "session.json")
USER_SETTINGS_FILE = str(BASE_PATH / "user_settings.json")

# --- Constants ---
SETTING_GEOMETRY = "geometry"
SETTING_THEME = "ui/theme"
SETTING_TOOLBAR_VISIBLE = "ui/toolbarVisible"
SETTING_STATUSBAR_VISIBLE = "ui/statusbarVisible"
SETTING_SEARCHBAR_VISIBLE = "ui/searchBarVisible"
SETTING_DEFAULT_FONT = "editor/defaultFont"
SETTING_DEFAULT_WORDWRAP = "editor/defaultWordWrap"
SETTING_SHOW_WORD_COUNT = "ui/showWordCount"
SETTING_SHOW_LINE_COUNT = "ui/showLineCount"
SETTING_SHOW_CHAR_COUNT = "ui/showCharCount"
SETTING_LAST_OPEN_DIR = "io/lastOpenDir"
SETTING_LAST_SAVE_DIR = "io/lastSaveDir"
SETTING_HIGHLIGHT_CURSOR_ONLY = "editor/highlightCursorOnly"
SETTING_ACTIVE_HIGHLIGHT_ID = "editor/activeHighlightId"
SETTING_HIGHLIGHT_MODE = "editor/highlightMode"
SETTING_DEFAULT_DATA_DIR = "io/defaultDataDir"

# Default Font
DEFAULT_FONT_FAMILY = "Consolas"
DEFAULT_FONT_SIZE = 11
DEFAULT_FONT_WEIGHT = QFont.Weight.Normal

# Constante para propriedade de ID
USER_ID_PROPERTY = QTextFormat.Property.UserProperty + 1
STRIKETHROUGH_PROPERTY = QTextFormat.Property.UserProperty + 2
GRADIENT_ACTIVE_PROPERTY = QTextFormat.Property.UserProperty + 3
GRADIENT_COLOR1_PROPERTY = QTextFormat.Property.UserProperty + 4
GRADIENT_COLOR2_PROPERTY = QTextFormat.Property.UserProperty + 5

# Aumenta o limite máximo para IDs
MAX_HIGHLIGHT_ID = 65536

# --- Funções Auxiliares ---
def calculate_dim_color(text_color, bg_color):
    """Calcula uma cor 'dim' misturando a cor do texto com a do fundo."""
    r = int((text_color.red() * 0.5) + (bg_color.red() * 0.5))
    g = int((text_color.green() * 0.5) + (bg_color.green() * 0.5))
    b = int((text_color.blue() * 0.5) + (bg_color.blue() * 0.5))
    return QColor(r, g, b)

# --- Widgets Customizados ---



class TextFormatPopup(QFrame):
    # ... (código existente, incluindo __init__ e show_extras_popup que agora funciona) ...
    # Note: a implementação de show_extras_popup agora usa self.main_window.extras_popup
    # ... (código existente) ...
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.main_window = parent # Guarda referência à janela principal
        self.text_edit = QTextEdit() # Inicializa text_edit corretamente

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # --- Botões de Formatação Padrão ---
        self.bold_btn = QToolButton()
        self.bold_btn.setIcon(self.parent().get_themed_icon("bold"))
        self.bold_btn.setCheckable(True)
        self.bold_btn.setToolTip("Negrito (Ctrl+B)")
        self.bold_btn.setStyleSheet("""
            QToolButton {
                padding: 2px;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
            QToolButton:checked {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
        """)

        self.italic_btn = QToolButton()
        self.italic_btn.setIcon(self.parent().get_themed_icon("italic"))
        self.italic_btn.setCheckable(True)
        self.italic_btn.setToolTip("Itálico (Ctrl+I)")
        self.italic_btn.setStyleSheet("""
            QToolButton {
                padding: 2px;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
            QToolButton:checked {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
        """)

        self.underline_btn = QToolButton()
        self.underline_btn.setIcon(self.parent().get_themed_icon("underline"))
        self.underline_btn.setCheckable(True)
        self.underline_btn.setToolTip("Sublinhado (Ctrl+U)")
        self.underline_btn.setStyleSheet("""
            QToolButton {
                padding: 2px;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
            QToolButton:checked {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
        """)

        self.strikethrough_btn = QToolButton()
        self.strikethrough_btn.setIcon(self.parent().get_themed_icon("strikethrough"))
        self.strikethrough_btn.setCheckable(True)
        self.strikethrough_btn.setToolTip("Tachado (Ctrl+T)")
        self.strikethrough_btn.setStyleSheet("""
            QToolButton {
                padding: 2px;
                border: 1px solid transparent;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
            QToolButton:checked {
                background-color: palette(highlight);
                border: 1px solid palette(highlight);
            }
        """)

        # --- Controles de Fonte ---
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(150)
        self.font_combo.setToolTip("Fonte")
        self.font_combo.setCurrentFont(QFont(self.main_window.default_editor_font.family() if hasattr(self.main_window, 'default_editor_font') else DEFAULT_FONT_FAMILY))

        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(self.main_window.default_editor_font.pointSize() if hasattr(self.main_window, 'default_editor_font') else DEFAULT_FONT_SIZE)
        self.size_spin.setMaximumWidth(50)
        self.size_spin.setToolTip("Tamanho da Fonte")

        # --- Botão Resetar Cor ---
        self.reset_color_btn = QToolButton()
        self.reset_color_btn._base_icon_name = "reset_colors"
        if self.main_window and hasattr(self.main_window, 'get_themed_icon'):
             self.reset_color_btn.setIcon(self.main_window.get_themed_icon("reset_colors"))
        self.reset_color_btn.setToolTip("Resetar para Cor Padrão do Tema")
        
        # Adiciona método para obter cor padrão do tema
        def get_default_text_color():
            theme = self.main_window.current_theme
            if theme == "light_xt10":
                return QColor(0, 0, 0)  # Preto para tema light
            else:  # dark themes
                return QColor(255, 255, 255)  # Branco para temas escuros
        
        self.default_text_color = get_default_text_color()

        # --- Botão Selecionar Cor ---
        self.color_btn = QPushButton()
        self.color_btn.setMaximumWidth(30)
        self.color_btn.setToolTip("Cor da Fonte")
        # Define cor inicial baseada no tema
        def get_default_text_color():
            theme = self.main_window.current_theme if self.main_window else "light_xt10"
            if theme == "light_xt10":
                return QColor(0, 0, 0)
            else:
                return QColor(255, 255, 255)
        self.default_text_color = get_default_text_color()
        outline_color = calculate_dim_color(self.default_text_color, self.palette().color(QPalette.ColorRole.Base))
        hover_outline = calculate_dim_color(self.default_text_color, self.palette().color(QPalette.ColorRole.Base))
        color_style = f"""
            QPushButton {{
                background-color: {self.default_text_color.name()};
                border: 1px solid {outline_color.name()};
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 1px solid {hover_outline.name()};
            }}
        """
        self.color_btn.setStyleSheet(color_style)

        # --- Controles de ID --- CORREÇÃO ÍCONE e TRIGGER
        self.id_btn = QToolButton()
        self.id_btn._base_icon_name = "id_button" # Nome base para atualização
        # Tenta definir o ícone inicial (pode depender do tema já carregado no parent)
        if self.main_window and hasattr(self.main_window, 'get_themed_icon'):
             self.id_btn.setIcon(self.main_window.get_themed_icon("id_button"))
        self.id_btn.setToolTip("Aplicar ID ao texto selecionado") # Tooltip atualizado
        self.id_btn.setObjectName("idButtonPopup") # Nome de objeto específico para CSS se necessário

        self.id_spin = QSpinBox()
        self.id_spin.setRange(0, MAX_HIGHLIGHT_ID)  # IDs de 0 a MAX_HIGHLIGHT_ID
        self.id_spin.setValue(0)
        self.id_spin.setMaximumWidth(60) # Aumenta um pouco a largura para 4 dígitos
        self.id_spin.setToolTip(f"ID para o texto selecionado (0 = sem ID, 1-{MAX_HIGHLIGHT_ID})")
        # Aplica o tema atual nas cores dos campos de texto
        self.setStyleSheet(f"color: {self.main_window.palette().color(QPalette.ColorRole.Text).name()};")

        # --- Layout ---
        layout.addWidget(self.bold_btn)
        layout.addWidget(self.italic_btn)
        layout.addWidget(self.underline_btn)
        layout.addWidget(self.strikethrough_btn)
        layout.addWidget(self.font_combo)
        layout.addWidget(self.size_spin)
        layout.addWidget(self.reset_color_btn) # Adicionado antes de color_btn
        layout.addWidget(self.color_btn)
        # Adiciona os widgets de ID
        layout.addWidget(self.id_btn)
        layout.addWidget(self.id_spin)

        # --- Conexões ---
        self.bold_btn.clicked.connect(self.format_bold)
        self.italic_btn.clicked.connect(self.format_italic)
        self.underline_btn.clicked.connect(self.format_underline)
        self.strikethrough_btn.clicked.connect(self.format_strikethrough)
        self.font_combo.currentFontChanged.connect(self.change_font_family)
        self.size_spin.valueChanged.connect(self.change_size)
        self.color_btn.clicked.connect(self.change_color)
        self.reset_color_btn.clicked.connect(self.reset_color) # Conecta o novo botão

        # Conecta APENAS o botão de ID à função apply_id - CORREÇÃO TRIGGER
        self.id_btn.clicked.connect(self.apply_id)
        # Removido: self.id_spin.valueChanged.connect(self.apply_id)

        self.update_theme() # Aplica cores/ícones iniciais baseados no tema atual

    def format_strikethrough(self):
        """Alterna o tachado no texto selecionado."""
        if self.text_edit:
            fmt = QTextCharFormat()
            fmt.setFontStrikeOut(self.strikethrough_btn.isChecked())
            self.apply_format(fmt)


    def reset_color(self):
        if not hasattr(self, 'text_edit') or self.text_edit is None:
            raise ValueError("text_edit não está definido ou é None.")
        
        cursor = self.text_edit.textCursor()  # Use o editor de texto associado
        if cursor.hasSelection():  # Verifica se há texto selecionado
            fmt = QTextCharFormat()
            fmt.setForeground(QBrush())  # Remove a cor de primeiro plano
            cursor.mergeCharFormat(fmt)  # Aplica a remoção da formatação de cor
            self.text_edit.setTextCursor(cursor)  # Atualiza o cursor
            # Atualiza o botão de cor para a cor padrão do tema
            default_color = self.text_edit.palette().color(QPalette.ColorRole.Text)
            self.color_btn.setStyleSheet(f"background-color: {default_color.name()};")
        else:
            print("Nenhum texto selecionado para resetar.")  # Mensagem de depuração

        # Não aplica uma cor específica, permitindo que o texto use a cor padrão do tema

    def show_at(self, pos, text_edit: QTextEdit):
        print("DEBUG: show_at chamado", pos, text_edit)
        self.text_edit = text_edit
        if self.text_edit:
            print("DEBUG: update_format_buttons antes")
            self.update_format_buttons()
            print("DEBUG: update_format_buttons depois")
            self.move(pos)
            print("DEBUG: move feito")
            self.show()
            print("DEBUG: show feito")

    def update_format_buttons(self):
        """Atualiza o estado dos botões do popup com base na seleção atual ou no cursor."""
        if not self.text_edit:
            print("DEBUG: text_edit não definido")
            self.hide() # Esconde o popup se não houver editor
            return

        try:
            cursor = self.text_edit.textCursor()
            # Obtém o formato padrão do editor para comparação
            default_editor_font = self.text_edit.font()
            default_editor_palette = self.text_edit.palette()
            default_text_color = default_editor_palette.color(QPalette.ColorRole.Text)


            if cursor.hasSelection():
                # Lógica para seleção: Verifica se TODA a seleção tem a mesma formatação
                selection_start = cursor.selectionStart()
                selection_end = cursor.selectionEnd()

                # Inicializa os estados como None para detectar o primeiro fragmento
                all_bold = None
                all_italic = None
                all_underline = None
                all_strike = None
                all_font = None
                all_size = None
                all_color = None
                all_id = None
                all_neutral_color = None # Adicionado para neutral_color

                temp_cursor = QTextCursor(self.text_edit.document())

                # Move um cursor temporário para o início da seleção
                temp_cursor.setPosition(selection_start)

                # Obtém o formato do primeiro caractere/fragmento da seleção
                first_fmt = temp_cursor.charFormat()
                all_bold = first_fmt.fontWeight() >= QFont.Weight.Bold
                all_italic = first_fmt.fontItalic()
                all_underline = first_fmt.fontUnderline()
                all_strike = first_fmt.fontStrikeOut() if hasattr(first_fmt, 'fontStrikeOut') else False
                all_font = first_fmt.fontFamily()
                all_size = int(first_fmt.fontPointSize()) if first_fmt.fontPointSize() > 0 else default_editor_font.pointSize()
                all_color = first_fmt.foreground().color().name() if first_fmt.foreground().color().isValid() else default_text_color.name()
                all_id = first_fmt.property(USER_ID_PROPERTY) or 0
                all_neutral_color = bool(first_fmt.property(QTextFormat.UserProperty + 100)) # Adicionado

                # Move o cursor temporário para a frente para comparar com o resto da seleção
                temp_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, selection_end - selection_start) # Seleciona o resto
                # Agora iteramos SOBRE os fragmentos DENTRO dessa seleção temporária
                iterator = temp_cursor.block().begin()
                while not iterator.atEnd():
                     fragment = iterator.fragment()
                     if fragment.isValid() and fragment.position() < selection_end: # Processa apenas fragmentos dentro da seleção
                         if fragment.position() + fragment.length() > selection_start: # Garante que o fragmento está dentro ou toca a seleção
                            # Obtém a formatação do fragmento
                            fmt = fragment.charFormat()
                            
                            # Verifica se a formatação do fragmento difere da primeira formatação encontrada
                            # e atualiza os flags 'all_...'
                            if all_bold != (fmt.fontWeight() >= QFont.Weight.Bold): all_bold = False
                            if all_italic != fmt.fontItalic(): all_italic = False
                            if all_underline != fmt.fontUnderline(): all_underline = False
                            if all_strike != (fmt.fontStrikeOut() if hasattr(fmt, 'fontStrikeOut') else False): all_strike = False
                            if all_font != fmt.fontFamily(): all_font = '' # Use string vazia para indicar diferença
                            # Para tamanho, verifica se o tamanho do fragmento é diferente do tamanho do primeiro fragmento
                            current_size = int(fmt.fontPointSize()) if fmt.fontPointSize() > 0 else default_editor_font.pointSize()
                            if all_size != current_size: all_size = 0 # Use 0 para indicar diferença
                            # Para cor, verifica se a cor do fragmento difere da cor do primeiro fragmento
                            current_color_name = fmt.foreground().color().name() if fmt.foreground().color().isValid() else default_text_color.name()
                            if all_color != current_color_name: all_color = '' # Use string vazia para indicar diferença
                            
                            current_id = fmt.property(USER_ID_PROPERTY) or 0
                            if all_id != current_id: all_id = -1 # Use -1 para indicar ID misturado

                            current_neutral_color = bool(fmt.property(QTextFormat.UserProperty + 100))
                            if all_neutral_color != current_neutral_color: all_neutral_color = None # Use None para indicar misturado


                     # Move para o próximo fragmento
                     iterator += 1

                # Define os estados dos botões com base nos flags 'all_...'
                self.bold_btn.setChecked(bool(all_bold))
                self.italic_btn.setChecked(bool(all_italic))
                self.underline_btn.setChecked(bool(all_underline))
                if hasattr(self, "strikethrough_btn"):
                    self.strikethrough_btn.setChecked(bool(all_strike))

                # Atualiza FontComboBox e SpinBox apenas se a formatação for uniforme
                if all_font:
                    self.font_combo.setCurrentFont(QFont(all_font))
                # Else: mantém a fonte atual do combo, indicando formatação mista ou padrão

                if all_size:
                    self.size_spin.setValue(all_size)
                # Else: mantém o tamanho atual do spinbox

                # Atualiza botão de cor
                if all_color:
                    self.color_btn.setStyleSheet(f"background-color: {all_color};")
                # Else: pode resetar para uma cor neutra ou padrão

                # Atualiza o ID spinbox
                if all_id != -1: # Se não for misturado
                    self.id_spin.setValue(all_id)
                # Else: mantém o valor atual ou define um valor neutro (e.g., 0)
                else:
                     self.id_spin.setValue(0) # Reset para 0 se houver IDs misturados

                return # Sair da função após processar a seleção

            else: # Sem seleção: Obtém o formato no cursor e compara com o padrão
                fmt = self.text_edit.currentCharFormat()

                # Obtém a formatação padrão do editor (ou da paleta)
                default_editor_font = self.text_edit.font()
                default_text_color = self.text_edit.palette().color(QPalette.ColorRole.Text)
                default_bg_color = self.text_edit.palette().color(QPalette.ColorRole.Base)


                # Verifica se a formatação no cursor é diferente da formatação padrão do editor
                # Importante: Use comparações robustas que considerem QFont.Weight.Normal e outros padrões
                is_bold = fmt.fontWeight() > QFont.Weight.Normal
                is_italic = fmt.fontItalic()
                is_underline = fmt.fontUnderline()
                is_strikethrough = fmt.fontStrikeOut() if hasattr(fmt, 'fontStrikeOut') else False

                # Compara com os valores padrão do editor
                # A formatação é considerada explícita APENAS se for diferente do padrão do editor
                # (para as propriedades relevantes)
                bold_explicit = is_bold != (default_editor_font.weight() > QFont.Weight.Normal)
                italic_explicit = is_italic != default_editor_font.italic()
                underline_explicit = is_underline != default_editor_font.underline()
                strikethrough_explicit = is_strikethrough # Não há strikethrough padrão na fonte, então sempre é explícito se True

                font_family_explicit = fmt.fontFamily() != "" and fmt.fontFamily() != default_editor_font.family()
                font_size_explicit = fmt.fontPointSize() > 0 and fmt.fontPointSize() != default_editor_font.pointSize()

                text_color_explicit = fmt.foreground().color().isValid() and fmt.foreground().color() != default_text_color
                bg_color_explicit = fmt.background().color().isValid() and fmt.background().color() != default_bg_color

                id_value = fmt.property(USER_ID_PROPERTY) or 0
                id_explicit = id_value != 0 # ID 0 significa sem ID

                neutral_color_explicit = bool(fmt.property(QTextFormat.UserProperty + 100)) # True se a propriedade estiver definida


                # Atualiza botões com base nas verificações explícitas
                self.bold_btn.setChecked(bold_explicit or is_bold) # Ligue se explícito OU se for negrito (em caso de dúvida)
                self.italic_btn.setChecked(italic_explicit or is_italic) # Ligue se explícito OU se for itálico
                self.underline_btn.setChecked(underline_explicit or is_underline) # Ligue se explícito OU se for sublinhado
                if hasattr(self, "strikethrough_btn"):
                    self.strikethrough_btn.setChecked(strikethrough_explicit or is_strikethrough) # Ligue se explícito OU se for tachado


                # Atualiza FontComboBox e SpinBox
                if font_family_explicit:
                    self.font_combo.setCurrentFont(QFont(fmt.fontFamily()))
                else:
                    # Se não for explícito, mostra a fonte padrão do editor
                    self.font_combo.setCurrentFont(default_editor_font)

                if font_size_explicit:
                    self.size_spin.setValue(int(fmt.fontPointSize()))
                else:
                    # Se não for explícito, mostra o tamanho padrão do editor
                    self.size_spin.setValue(default_editor_font.pointSize())


                # Atualiza botão de cor
                if text_color_explicit:
                    self.color_btn.setStyleSheet(f"background-color: {fmt.foreground().color().name()};")
                else:
                    # Se não for explícito, mostra a cor padrão do texto
                    self.color_btn.setStyleSheet(f"background-color: {default_text_color.name()};")


                # Atualiza o ID spinbox
                self.id_spin.setValue(id_value)


        except Exception as e:
            print(f"Error updating format buttons: {e}")
            # Em caso de erro, reseta todos os botões para o estado desligado e esconde o popup
            self.bold_btn.setChecked(False)
            self.italic_btn.setChecked(False)
            self.underline_btn.setChecked(False)
            if hasattr(self, "strikethrough_btn"):
                self.strikethrough_btn.setChecked(False)
            # Reset FontComboBox/SpinBox para os valores padrão do editor
            if self.text_edit:
                 default_font = self.text_edit.font()
                 self.font_combo.setCurrentFont(default_font)
                 self.size_spin.setValue(default_font.pointSize())
            # Reset color button to default text color
            default_text_color = self.text_edit.palette().color(QPalette.ColorRole.Text)
            self.color_btn.setStyleSheet(f"background-color: {default_text_color.name()};")
            self.id_spin.setValue(0) # Reset ID
            # self.hide() # Não esconda em caso de erro, apenas resete a UI

    def format_bold(self):
        if self.text_edit:
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold if self.bold_btn.isChecked() else QFont.Weight.Normal)
            self.apply_format(fmt)

    def format_italic(self):
        if self.text_edit:
            fmt = QTextCharFormat()
            fmt.setFontItalic(self.italic_btn.isChecked())
            self.apply_format(fmt)

    def format_underline(self):
        if self.text_edit:
            fmt = QTextCharFormat()
            fmt.setFontUnderline(self.underline_btn.isChecked())
            self.apply_format(fmt)

    def change_font_family(self, font):
        if self.text_edit:
            fmt = QTextCharFormat()
            fmt.setFontFamily(font.family())
            self.apply_format(fmt)

    def change_size(self, size):
        if self.text_edit:
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            self.apply_format(fmt)

    def change_color(self):
        if self.text_edit:
            current_format = self.text_edit.currentCharFormat()
            current_color = current_format.foreground().color()
            if not current_color.isValid():
                current_color = self.text_edit.palette().color(QPalette.ColorRole.Text)

            # Store the current color before opening color picker
            original_color = current_color
            
            color_rgb = vcolorpicker.getColor(current_color.getRgb()[:3] if current_color.isValid() else None)
            
            # If user canceled the color picker (returns None)
            if color_rgb is None:
                # Reset to original color
                fmt = QTextCharFormat()
                fmt.setForeground(original_color)
                self.apply_format(fmt)
                self.color_btn.setStyleSheet(f"background-color: {original_color.name()}; border: 1px solid grey;")
                return
            
            # If user selected a color
            qcolor = QColor(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]))
            fmt = QTextCharFormat()
            fmt.setForeground(qcolor)
            self.apply_format(fmt)
            self.color_btn.setStyleSheet(f"background-color: {qcolor.name()}; border: 1px solid grey;")
    

    def apply_id(self):
        """Aplica o ID do spinbox ao texto selecionado (disparado pelo id_btn)."""
        if self.text_edit:
            fmt = QTextCharFormat()
            id_value = self.id_spin.value()
            fmt.setProperty(USER_ID_PROPERTY, id_value)
            self.apply_format(fmt)

            # Dispara atualização do estado do cursor na janela principal
            # Isso vai indiretamente atualizar os highlighters, se necessário.
            if self.main_window and hasattr(self.main_window, 'update_cursor_state'):
                self.main_window.update_cursor_state()

        # Atualiza ícone do botão de ID
        if hasattr(self.main_window, 'get_themed_icon'):
            self.id_btn.setIcon(self.main_window.get_themed_icon("id_button"))
            # Atualiza ícones dos novos botões
            self.reset_color_btn.setIcon(self.main_window.get_themed_icon("reset_colors"))

        # Atualiza ícone do botão de ID
        if hasattr(self.main_window, 'get_themed_icon'):
            self.id_btn.setIcon(self.main_window.get_themed_icon("id_button"))
            self.reset_color_btn.setIcon(self.main_window.get_themed_icon("reset_colors"))

    def apply_format(self, fmt):
        if not self.text_edit: return
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.beginEditBlock()
            cursor.mergeCharFormat(fmt)
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.endEditBlock()
            self.text_edit.setTextCursor(cursor)
        else:
            self.text_edit.mergeCurrentCharFormat(fmt)
        self.text_edit.textCursor().mergeCharFormat(fmt)
        self.text_edit.setFocus()


    def update_theme(self):
        if not self.main_window: 
            return

        # Atualiza paleta
        self.setPalette(self.main_window.palette())
        palette = self.palette()

        # Determina cores baseado no tema
        is_light_theme = self.main_window.current_theme == "light_xt10"
        
        if is_light_theme:
            # Tema Light
            popup_bg = QColor(230, 230, 230)         # Background mais escuro que os botões
            button_bg = QColor(245, 245, 245)        # Botões mais claros que o fundo
            input_bg = QColor(255, 255, 255)         # Inputs brancos
            input_border = QColor(180, 180, 180)     # Bordas mais visíveis
            outline_color = QColor(180, 180, 180)    # Outline dos botões
            hover_outline = QColor(140, 140, 140)    # Outline hover mais escuro
        else:
            # Temas Dark
            if self.main_window.current_theme == "dark_xt10":
                popup_bg = QColor(25, 25, 25)        # Background mais escuro que os botões
                button_bg = QColor(45, 45, 45)       # Botões mais claros que o fundo
                input_bg = QColor(45, 45, 45)        # Inputs
                input_border = QColor(70, 70, 70)    # Bordas
                outline_color = QColor(70, 70, 70)   # Outline dos botões
                hover_outline = QColor(90, 90, 90)   # Outline hover mais claro
            else: # dark_xt7
                popup_bg = QColor(45, 50, 58)        # Background mais escuro
                button_bg = QColor(65, 70, 78)       # Botões mais claros
                input_bg = QColor(65, 69, 79)        # Inputs ajustados para Midtones
                input_border = QColor(137, 142, 163)    # Bordas ajustadas
                outline_color = QColor(137, 142, 163)   # Outline ajustado
                hover_outline = QColor(100, 100, 100) # Outline hover ajustado

        # Define text color based on theme
        text_color = QColor()
        if self.main_window.current_theme.startswith('dark'):
            text_color = QColor(255, 255, 255)  # White for dark themes
        else:
            text_color = QColor(0, 0, 0)  # Black for light themes

        format_btn_style = f"""
            QToolButton {{
                border-radius: 3px;
                padding: 2px;
            }}
            QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
                color: {text_color.name()};
                border: 1px solid {hover_outline.name()};
            }}
            
            QToolButton:checked {{
                background-color: palette(highlight);
                color: {text_color.name()};
                border: 1px solid {hover_outline.name()};
            }}
        """

        for btn in [self.bold_btn, self.italic_btn, self.underline_btn, self.strikethrough_btn]:
            btn.setStyleSheet(format_btn_style)

        # Atualiza estilo dos botões de ID
        id_btn_style = f"""
            QToolButton {{
                border: 1px solid {outline_color.name()};
                border-radius: 3px;
                padding: 2px;
            }}
            QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
                color: palette(highlighted-text);
                border: 1px solid {hover_outline.name()};
            }}
            
            QToolButton:checked {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: 1px solid {hover_outline.name()};
            }}
        """

        self.id_btn.setStyleSheet(id_btn_style)

        reset_color_btn_style = f"""
            QToolButton {{
                border: 1px solid {outline_color.name()};
                border-radius: 3px;
                padding: 2px;
            }}
            QToolButton:hover {{
                background-color: rgba(255, 255, 255, 0.15);
                color: palette(highlighted-text);
                border: 1px solid {hover_outline.name()};
            }}
            
            QToolButton:checked {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border: 1px solid {hover_outline.name()};
            }}
        """


        self.reset_color_btn.setStyleSheet(reset_color_btn_style)

        # Aplica stylesheet com as novas cores
        self.setStyleSheet(f"""
            TextFormatPopup {{
                background-color: {popup_bg.name()};
                border: 1px solid {outline_color.name()};
                border-radius: 6px;
            }}
            
            TextFormatPopup QWidget {{
                background-color: {popup_bg.name()};
            }}
            
            TextFormatPopup QToolButton {{
                background-color: {button_bg.name()};
                color: {palette.color(QPalette.ColorRole.WindowText).name()};
                border: 1px solid {outline_color.name()};
                border-radius: 3px;
                padding: 3px;
            }}
            
            TextFormatPopup QToolButton:hover {{
                background-color: {palette.color(QPalette.ColorRole.Highlight).name()};
                color: {palette.color(QPalette.ColorRole.HighlightedText).name()};
                border: 1px solid {hover_outline.name()};
            }}
            
            TextFormatPopup QToolButton:checked {{
                background-color: {palette.color(QPalette.ColorRole.Highlight).name()};
                border: 1px solid {hover_outline.name()};
                color: {palette.color(QPalette.ColorRole.HighlightedText).name()};
            }}
            
            TextFormatPopup QSpinBox, 
            TextFormatPopup QFontComboBox {{
                background-color: {input_bg.name()};
                color: {palette.color(QPalette.ColorRole.Text).name()};
                border: 1px solid {input_border.name()};
                border-radius: 4px;
                padding: 2px 4px;
            }}
            
            TextFormatPopup QSpinBox:focus, 
            TextFormatPopup QFontComboBox:focus {{
                border: 2px solid {palette.color(QPalette.ColorRole.Highlight).name()};
            }}
            
            TextFormatPopup QPushButton {{
                background-color: {button_bg.name()};
                border: 1px solid {outline_color.name()};
                padding: 2px;
                min-height: 16px;
            }}
            
            TextFormatPopup QPushButton:hover {{
                background-color: {QColor(button_bg.red() + 10, button_bg.green() + 10, button_bg.blue() + 10).name()};
                border: 1px solid {hover_outline.name()};
            }}
        """)
        
        # Atualiza ícones se necessário
        if self.main_window and hasattr(self.main_window, 'get_themed_icon'):
            if hasattr(self, 'extras_btn'):
                self.extras_btn.setIcon(self.main_window.get_themed_icon("extras_features"))  

    def update_theme_colors(self):
        """Atualiza as cores dos textos que foram resetados para seguir o tema."""
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        # Percorre todos os blocos de texto
        doc = self.text_edit.document()
        block = doc.begin()
        while block.isValid():
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            text = block.text()
            
            # Get formatting for each character
            for j in range(len(text)):
                cursor.setPosition(block.position() + j)
                char_format = cursor.charFormat()
                
                # Check if this text was reset to theme color
                if char_format.property(QTextFormat.UserProperty + 100):
                    # Update to current theme color
                    char_format.setForeground(self.default_text_color)
                    cursor.mergeCharFormat(char_format)
                    
        self.text_edit.textChanged.disconnect(self.update_theme_colors)

    def focusOutEvent(self, event):
        main_window = getattr(self, 'main_window', None)
        if main_window and getattr(main_window, 'format_popup_mode', '') == 'statusbar':
            event.ignore()
            self.setFocus()
            return
        super().focusOutEvent(event)

    def show_format_popup_statusbar(self):
        if not self.current_editor:
            return
        sb_rect = self.status_bar.rect()
        sb_top_left = self.status_bar.mapToGlobal(sb_rect.topLeft())
        sb_width = sb_rect.width()
        popup_width = self.format_popup.width() if self.format_popup.width() > 0 else 300
        x = sb_top_left.x() + (sb_width - popup_width) // 2
        y = sb_top_left.y() - self.format_popup.height() - 2
        self.format_popup.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self.format_popup.setMinimumSize(300, 40)
        self.format_popup.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Plain)
        self.format_popup.setLineWidth(0)
        self.format_popup.show_at(QPoint(int(x), int(y)), self.current_editor)
        self.format_popup.show()

    def hide(self):
        main_window = getattr(self, 'main_window', None)
        if main_window and getattr(main_window, 'format_popup_mode', '') == 'statusbar':
            return  # Nunca esconda no modo statusbar
        super().hide()


class SearchBarWidget(QWidget):
    # ... (código inalterado) ...
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.setClearButtonEnabled(True)
        layout.addWidget(self.search_input)
        
        # Add match counter label
        self.match_counter = QLabel()
        self.match_counter.setStyleSheet("color: rgba(128, 128, 128, 180);")  # Semi-transparent gray
        layout.addWidget(self.match_counter)
        
        # Track if search is active
        self.search_active = False

        self.case_sensitive_btn = QToolButton()
        self.case_sensitive_btn.setText("Aa")
        self.case_sensitive_btn.setToolTip("Diferenciar maiúsculas/minúsculas")
        self.case_sensitive_btn.setCheckable(True)
        self.case_sensitive_btn.toggled.connect(lambda: self.refresh_search_highlights())
        layout.addWidget(self.case_sensitive_btn)

        self.whole_word_btn = QToolButton()
        self.whole_word_btn.setText("⚹*") # Consider changing the icon/text
        self.whole_word_btn.setToolTip("Coincidir palavra inteira")
        self.whole_word_btn.setCheckable(True)
        self.whole_word_btn.toggled.connect(lambda: self.refresh_search_highlights())
        layout.addWidget(self.whole_word_btn)

        self.prev_btn = QToolButton()
        self.prev_btn.setToolTip("Localizar anterior (Shift+Enter)")
        self.prev_btn._base_icon_name = "arrow_up"
        layout.addWidget(self.prev_btn)

        self.next_btn = QToolButton()
        self.next_btn.setToolTip("Localizar próximo (Enter)")
        self.next_btn._base_icon_name = "arrow_down"
        layout.addWidget(self.next_btn)

        self.search_input.returnPressed.connect(self.find_next)
        self.search_input.installEventFilter(self)
        self.prev_btn.clicked.connect(self.find_previous)
        self.next_btn.clicked.connect(self.find_next)
        self.search_input.textChanged.connect(self.update_button_state)
        self.update_button_state("")
        self.set_contents_visible(False)
        self.setLayout(layout)

    def set_contents_visible(self, visible):
        self.search_input.setVisible(visible)
        self.case_sensitive_btn.setVisible(visible)
        self.whole_word_btn.setVisible(visible)
        self.prev_btn.setVisible(visible)
        self.next_btn.setVisible(visible)
        self.match_counter.setVisible(visible)
        self.search_active = visible
        
        # Clear highlights when search bar is hidden
        if not visible and self.main_window and self.main_window.current_editor:
            self.main_window.current_editor.setExtraSelections([])
            self.search_input.clear()  # Also clear the search text
            # Remove our connection to text changed
            try:
                self.main_window.current_editor.textChanged.disconnect(self.on_editor_text_changed)
            except:
                pass

    def eventFilter(self, obj, event):
        if obj == self.search_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.find_previous()
                    return True
        return super().eventFilter(obj, event)

    def update_button_state(self, text):
        enabled = bool(text)
        self.prev_btn.setEnabled(enabled)
        self.next_btn.setEnabled(enabled)
        
        if self.main_window and self.main_window.current_editor:
            if enabled:
                self.highlight_matches(text)
            else:
                self.main_window.current_editor.setExtraSelections([])

    def highlight_matches(self, text):
        """Updates search highlights in the editor with different opacities"""
        if not self.main_window or not self.main_window.current_editor:
            return
            
        editor = self.main_window.current_editor
        
        if not text:
            editor.setExtraSelections([])
            self.match_counter.setText("")
            return
        
        flags = self.get_find_flags()
        
        # Prepare search highlight format with 35% opacity for regular matches
        regular_fmt = QTextCharFormat()
        highlight_color = QColor("#FFC300")
        highlight_color.setAlpha(89)  # ~35% opacity
        regular_fmt.setBackground(QBrush(highlight_color))
        regular_fmt.setProperty(QTextFormat.Property.FullWidthSelection, False)
        
        # Format for current selection with ~70% opacity
        current_fmt = QTextCharFormat()
        current_color = QColor("#FFC300")
        current_color.setAlpha(178)  # ~70% opacity
        current_fmt.setBackground(QBrush(current_color))
        current_fmt.setProperty(QTextFormat.Property.FullWidthSelection, False)
        
        # Find all matches and create extra selections
        extra_selections = []
        self.matches = []  # Store all match positions
        if not hasattr(self, 'current_match_index'):
            self.current_match_index = -1
        
        doc_cursor = editor.document().find(text, 0, flags)
        while not doc_cursor.isNull():
            selection = QTextEdit.ExtraSelection()
            # All matches start with regular format
            selection.format = regular_fmt
            selection.cursor = doc_cursor
            extra_selections.append(selection)
            # Store match position
            self.matches.append((doc_cursor.selectionStart(), doc_cursor.selectionEnd()))
            
            # Find next occurrence
            doc_cursor = editor.document().find(text, doc_cursor, flags)
            
        # If we have matches and there's a current selection, find which one it is
        if self.matches:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                current_pos = cursor.selectionStart()
                for i, (start, end) in enumerate(self.matches):
                    if start == current_pos:
                        self.current_match_index = i
                        extra_selections[i].format = current_fmt
                        break
            
            if self.current_match_index == -1:
                # No current match, start with first one
                self.current_match_index = 0
                extra_selections[0].format = current_fmt
                
            # This part was causing duplicate selections
            # Removed redundant selection addition and find operation
        
        # Apply highlights all at once
        editor.setExtraSelections(extra_selections)
        
        # Update match counter and highlight current match
        total_matches = len(extra_selections)
        if total_matches > 0:
            # Reset all matches to regular format first
            for i in range(len(extra_selections)):
                extra_selections[i].format = regular_fmt
            
            # If this is a first search (no current match), start with the first one
            if self.current_match_index == -1:
                self.current_match_index = 0
            
            # Highlight current match with current format
            if 0 <= self.current_match_index < len(extra_selections):
                extra_selections[self.current_match_index].format = current_fmt
                current_match = self.current_match_index + 1  # 1-based index for display
                self.match_counter.setText(f"{current_match} of {total_matches}")
            else:
                self.match_counter.setText(f"0 of {total_matches}")
        else:
            self.match_counter.setText("")
            
        # Apply all highlights
        editor.setExtraSelections(extra_selections)

    def on_editor_text_changed(self):
        """Called when the editor text changes to update search highlights"""
        if self.search_active and self.main_window and self.main_window.current_editor:
            self.highlight_matches(self.search_input.text())

    def connect_to_editor(self, editor):
        """Connect to the text changed signal of the editor"""
        if editor:
            editor.textChanged.connect(self.on_editor_text_changed)

    def get_find_flags(self):
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive_btn.isChecked(): flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word_btn.isChecked(): flags |= QTextDocument.FindFlag.FindWholeWords
        return flags

    def find_next(self):
        if not self.main_window or not self.main_window.current_editor:
            return
        
        term = self.search_input.text()
        if not term or not hasattr(self, 'matches') or not self.matches:
            return
            
        editor = self.main_window.current_editor
        
        if len(self.matches) == 0:
            return
            
        # Move to next match or wrap around
        next_index = (self.current_match_index + 1) % len(self.matches)
        self.current_match_index = next_index
        
        # Prepare formats for highlights
        regular_fmt = QTextCharFormat()
        highlight_color = QColor("#FFC300")
        highlight_color.setAlpha(89)  # ~35% opacity
        regular_fmt.setBackground(QBrush(highlight_color))
        regular_fmt.setProperty(QTextFormat.Property.FullWidthSelection, False)
        
        current_fmt = QTextCharFormat()
        current_color = QColor("#FFC300")
        current_color.setAlpha(178)  # ~70% opacity
        current_fmt.setBackground(QBrush(current_color))
        current_fmt.setProperty(QTextFormat.Property.FullWidthSelection, False)

        # Move cursor to next match position
        cursor = editor.textCursor()
        start, end = self.matches[next_index]
        
        # Move cursor to the match without selection
        cursor.setPosition(end)  # Move to end of match
        editor.setTextCursor(cursor)
        
        # Show wrap message if needed
        if next_index == 0 and len(self.matches) > 1:
            if self.main_window and self.main_window.statusBar():
                self.main_window.statusBar().showMessage("Busca voltou ao início do documento", 2000)
        
        # Update highlights
        extra_selections = []
        for i, (match_start, match_end) in enumerate(self.matches):
            selection = QTextEdit.ExtraSelection()
            selection.format = regular_fmt if i != next_index else current_fmt
            cursor = QTextCursor(editor.document())
            cursor.setPosition(match_start)
            cursor.setPosition(match_end, QTextCursor.MoveMode.KeepAnchor)
            selection.cursor = cursor
            extra_selections.append(selection)
            
        editor.setExtraSelections(extra_selections)
        self.match_counter.setText(f"{next_index + 1} of {len(self.matches)}")
        editor.ensureCursorVisible()

    def find_previous(self):
        if not self.main_window or not self.main_window.current_editor:
            return
            
        term = self.search_input.text()
        if not term or not hasattr(self, 'matches') or not self.matches:
            return
            
        editor = self.main_window.current_editor
        
        if len(self.matches) == 0:
            return
            
        # Move to previous match or wrap around to end
        prev_index = (self.current_match_index - 1) if self.current_match_index > 0 else len(self.matches) - 1
        self.current_match_index = prev_index
        
        # Prepare formats for highlights
        regular_fmt = QTextCharFormat()
        highlight_color = QColor("#FFC300")
        highlight_color.setAlpha(89)  # ~35% opacity
        regular_fmt.setBackground(QBrush(highlight_color))
        regular_fmt.setProperty(QTextFormat.Property.FullWidthSelection, False)
        
        current_fmt = QTextCharFormat()
        current_color = QColor("#FFC300")
        current_color.setAlpha(178)  # ~70% opacity
        current_fmt.setBackground(QBrush(current_color))
        current_fmt.setProperty(QTextFormat.Property.FullWidthSelection, False)

        # Move cursor to match position without selecting
        cursor = editor.textCursor()
        start, end = self.matches[prev_index]
        
        # Move cursor to the match without selection
        cursor.setPosition(end)  # Move to end of match
        editor.setTextCursor(cursor)
        
        # Show wrap message if needed
        if prev_index == len(self.matches) - 1 and len(self.matches) > 1:
            if self.main_window and self.main_window.statusBar():
                self.main_window.statusBar().showMessage("Busca voltou ao final do documento", 2000)
        
        # Update highlights
        extra_selections = []
        for i, (match_start, match_end) in enumerate(self.matches):
            selection = QTextEdit.ExtraSelection()
            selection.format = regular_fmt if i != prev_index else current_fmt
            cursor = QTextCursor(editor.document())
            cursor.setPosition(match_start)
            cursor.setPosition(match_end, QTextCursor.MoveMode.KeepAnchor)
            selection.cursor = cursor
            extra_selections.append(selection)
            
        editor.setExtraSelections(extra_selections)
        self.match_counter.setText(f"{prev_index + 1} of {len(self.matches)}")
        editor.ensureCursorVisible()

    def focus_input(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def refresh_search_highlights(self):
        """Atualiza os highlights de busca quando as opções (case sensitive, whole word) são alteradas"""
        if self.search_active and self.main_window and self.main_window.current_editor:
            self.update_button_state(self.search_input.text())

    def _apply_theme(self, palette, stylesheet, theme_name):
        # ... (código inalterado - já chama update_icons_for_theme no final) ...
        QApplication.setPalette(palette)
        # Removido: self.format_popup.setPalette(palette)
        # A paleta e o stylesheet do popup são atualizados por update_theme agora
        # Popup Stylesheet...
        # Removido: self.format_popup.setStyleSheet(...)
        # Chamada para o novo método de atualização do popup
        self.format_popup.update_theme()
        if self.extras_popup: self.extras_popup.update_theme()

        # if self.format_popup.text_edit: self.format_popup.update_format_buttons() # update_theme já chama isso

        self.current_theme = "dark_xt10"

# --- Classe IdHighlighter ---
class IdHighlighter(QSyntaxHighlighter):
    def __init__(self, document, main_window):
        super().__init__(document)
        self.main_window = main_window
        self.active_id = 0 # ID ativo globalmente (definido pelo botão/janela)
        self.cursor_id = 0 # ID sob o cursor (usado no modo cursor-only)
        self.highlight_cursor_only = False # Modo: True = cursor determina, False = global determina
        # self.cursor_position = -1 # Não mais necessário rastrear posição aqui
        self.normal_text_color = QColor()
        self.dim_text_color = QColor()
        self.update_colors() # Define cores iniciais]

    def set_active_id(self, id_value):
        """Define o ID ativo globalmente (usado quando highlight_cursor_only=False)."""
        if self.active_id != id_value:
            self.active_id = id_value
            self.rehighlight() # Rehighlight é necessário se o ID ativo global mudar

    def set_cursor_id(self, id_value):
        """Define o ID atualmente sob o cursor (usado quando highlight_cursor_only=True)."""
        if self.cursor_id != id_value:
            self.cursor_id = id_value
            # Rehighlight só é necessário se estivermos no modo cursor-only
            if self.highlight_cursor_only:
                self.rehighlight()

    # def set_cursor_position(self, position): # Removido
    #     if self.highlight_cursor_only and self.cursor_position != position:
    #         self.cursor_position = position
    #         self.rehighlight() # Precisa re-highlight quando o cursor muda no modo cursor-only

    def set_cursor_only(self, enabled):
        """Ativa/desativa o modo de highlight baseado no cursor."""
        if self.highlight_cursor_only != enabled:
            self.highlight_cursor_only = enabled
            # self.cursor_position = -1 # Removido
            self.rehighlight() # Sempre rehighlight ao mudar de modo

    def update_colors(self):
        """Recalcula as cores normal e 'dim' baseado no tema."""
        if not self.main_window: return
        palette = self.main_window.palette()
        self.normal_text_color = palette.color(QPalette.ColorRole.Text)
        bg_color = palette.color(QPalette.ColorRole.Base)
        # Calcula cor dim misturando 50% texto e 50% fundo
        self.dim_text_color = calculate_dim_color(self.normal_text_color, bg_color)
        self.rehighlight() # Re-aplica com as novas cores

    def highlightBlock(self, text):
        """Aplica a formatação ao bloco de texto."""
        current_block = self.currentBlock()
        if not current_block.isValid(): return

        # ID que determina qual texto será destacado (não 'dim') neste bloco.
        # Decide qual ID usar baseado no modo (cursor ou global).
        highlight_determining_id = 0

        if self.highlight_cursor_only:
            # Modo Cursor: Usa o ID que foi passado pela janela principal (cursor_id)
            highlight_determining_id = self.cursor_id
        else:
            # Modo Global: Usa o ID ativo globalmente (active_id)
            highlight_determining_id = self.active_id

        # --- Itera sobre os fragmentos de formatação no bloco ---
        iterator = current_block.begin()
        while not iterator.atEnd():
            fragment = iterator.fragment()
            # Processa apenas se o fragmento for válido e tiver texto
            if fragment.isValid() and fragment.length() > 0:
                start_pos = fragment.position()
                length = fragment.length()
                block_pos = current_block.position() # Posição inicial do bloco

                original_format = fragment.charFormat()
                fragment_id = original_format.property(USER_ID_PROPERTY) or 0 # 0 se não definido

                # Começa com o formato original para preservar outras formatações
                apply_format = QTextCharFormat(original_format)

                # --- Lógica de Escurecimento (Dimming) Revisada ---
                is_dimmed = False
                if fragment_id == 0:
                    # Regra 3: ID 0 nunca é 'dim'
                    pass
                elif highlight_determining_id == 0:
                    # Nenhum ID ativo (global ou cursor).
                    # **NOVO:** Escurece *todos* os fragmentos com ID > 0.
                    is_dimmed = True
                elif fragment_id == highlight_determining_id:
                    # Regra 1: Fragmento corresponde ao ID ativo (global ou cursor).
                    # Não escurece.
                    pass
                else: # fragment_id != 0 AND highlight_determining_id > 0 AND fragment_id != highlight_determining_id
                    # Regra 2: Fragmento tem ID, mas não é o ativo. Escurece.
                    is_dimmed = True

                # --- Aplica a Cor (Normal ou Dim) ---
                if is_dimmed:
                    apply_format.setForeground(self.dim_text_color)
                else:
                    # Se não for 'dim', restaura a cor.
                    # Verifica se a cor atual é a 'dim' ou inválida para decidir se restaura.
                    current_fg_brush = apply_format.foreground()
                    if current_fg_brush.style() == Qt.BrushStyle.NoBrush or current_fg_brush.color() == self.dim_text_color:
                        # Tenta restaurar a cor original do fragmento, se existir.
                        original_fg_brush = original_format.foreground()
                        if original_fg_brush.style() != Qt.BrushStyle.NoBrush:
                            apply_format.setForeground(original_fg_brush)
                        else:
                            # Se não havia cor original, usa a cor padrão do tema.
                            apply_format.setForeground(self.normal_text_color)

                # Aplica o formato calculado ao fragmento
                self.setFormat(start_pos - block_pos, length, apply_format)

            # Avança o iterador para o próximo fragmento
            iterator += 1


class EditableTabBar(QTabBar):
    edit_finished = pyqtSignal(int, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.editor = None
        self.editor_index = -1
        self.setTabsClosable(True)
    
    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.start_editing(index)
        super().mouseDoubleClickEvent(event)
    
    def start_editing(self, index):
        if self.editor:
            self.finish_editing()
        
        self.editor_index = index
        rect = self.tabRect(index)
        
        # Adjust rect to account for close button and other tab decorations
        opt = QStyleOptionTab()
        self.initStyleOption(opt, index)
        icon_width = opt.iconSize.width() if not opt.icon.isNull() else 0
        close_width = 16  # Approximate width of close button
        
        # Calculate available width for editor
        editor_width = rect.width() - icon_width - close_width - 10  # Add some padding
        if editor_width < 50:  # Minimum reasonable width
            editor_width = 50
        
        # Position editor
        editor_rect = QRect(rect)
        editor_rect.setLeft(rect.left() + 4 + icon_width)
        editor_rect.setWidth(editor_width)
        
        # Create and configure editor
        self.editor = QLineEdit(self)
        self.editor.setGeometry(editor_rect)
        self.editor.setText(self.tabText(index).replace('*', ''))
        self.editor.selectAll()
        self.editor.show()
        self.editor.setFocus()
        self.editor.returnPressed.connect(self.finish_editing)
        self.editor.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if obj == self.editor and event.type() == QEvent.Type.FocusOut:
            self.finish_editing()
            return True
        return super().eventFilter(obj, event)
    
    def finish_editing(self):
        if not self.editor:
            return
            
        new_text = self.editor.text()
        self.editor.deleteLater()
        self.editor = None
        
        if self.editor_index >= 0 and new_text.strip():
            self.edit_finished.emit(self.editor_index, new_text.strip())
        
        self.editor_index = -1
    
    def show_context_menu(self, pos):
        index = self.tabAt(pos)
        if index < 0:
            return
            
        menu = QMenu(self)
        rename_action = menu.addAction("Renomear Aba")
        action = menu.exec(self.mapToGlobal(pos))
        
        if action == rename_action:
            self.start_editing(index)


class DarkNotepad(QMainWindow):
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    ext = os.path.splitext(url.toLocalFile())[1].lower()
                    if ext in ['.txt', '.rtf', '.nxt']:
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == '.nxt':
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content_data = json.load(f)
                            self.new_tab(file_path=file_path, content_data=content_data)
                        except Exception as e:
                            QMessageBox.warning(self, 'Erro', f'Erro ao abrir arquivo NXT: {e}')
                    elif ext in ['.txt', '.rtf']:
                        self.new_tab(file_path=file_path)
        event.acceptProposedAction()

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)  # Enable drag-and-drop for the main window
        self.settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, ORG_NAME, APP_NAME)
        self.current_files = {}
        self.current_editor = None
        # Define o tema padrão ANTES de criar o popup, para que get_themed_icon funcione
        self.current_theme = "dark_xt10"
        self.format_popup = TextFormatPopup(self)
        self.extras_popup = None # Adiciona referência aqui também para gerenciamento
        # self.current_theme = "dark_xt10" # Movido para cima
        self.default_editor_font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, DEFAULT_FONT_WEIGHT)
        # Carrega configuração do word wrap do settings
        self.default_word_wrap = self.settings.value(SETTING_DEFAULT_WORDWRAP, True, type=bool)
        self.actions_with_icons = []
        self.highlighters = {} # Dicionário para highlighters
        self.read_mode_states = {} # Dicionário para rastrear o estado de modo leitura de cada editor

        user_settings = self.load_user_settings()
        # Restore theme
        theme_from_json = user_settings.get("ui/theme")
        if theme_from_json in ("dark_xt10", "dark_xt7", "light_xt10"):
            self.current_theme = theme_from_json
        else:
            self.current_theme = "dark_xt10"
        # Restore highlighter mode
        self.highlight_cursor_only = user_settings.get('highlight_cursor_only', False)

        self.format_popup = TextFormatPopup(self)
        self.extras_popup = None



        # --- Estado do Highlighter --- Refatorado
        # highlight_cursor_only is already loaded from settings above, don't reset it here
        self.active_highlight_id = 0      # ID ativo globalmente (controlado pelo botão da toolbar)
        self.current_cursor_id = 0        # ID atualmente sob o cursor do editor ativo

        self.setWindowTitle(APP_NAME)
        self.load_user_settings() # Carrega tema, fonte, estado do highlight, etc.
        self.setWindowIcon(self.get_themed_icon("app_icon"))

        # --- Restore window size from user_settings ---
        settings = self.load_user_settings()
        width = settings.get('window_width', 1000)
        height = settings.get('window_height', 700)
        self.resize(width, height)
        # Center on screen
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setup_ui() # UI setup depende de load_settings

        self.popup_timer = QTimer()
        self.popup_timer.setSingleShot(True)
        self.popup_timer.timeout.connect(self.show_format_popup)
        self.shift_pressed = False
        self.installEventFilter(self)

        self.apply_loaded_ui_settings() # Aplica visibilidade
        self.update_icons_for_theme()   # Garante ícones corretos
        self.update_highlighter_colors() # Garante cores corretas no highlighter inicial
        # Aplica o stylesheet da janela principal APÓS carregar tudo
        self.apply_current_stylesheet()

        self.load_plugins() # Adicionado

        if getattr(self, 'format_popup_mode', '') == 'statusbar':
            QTimer.singleShot(100, self.show_format_popup_statusbar)

        # --- Restaurar sessão após setup_ui ---
        QTimer.singleShot(0, self.restore_session)

    def apply_current_stylesheet(self):
        # Reaplica o stylesheet do tema atual
        if self.current_theme == "dark_xt10":
            self.apply_dark_xt10_theme()
        elif self.current_theme == "dark_xt7":
            self.apply_dark_xt7_theme()
        elif self.current_theme == "light_xt10":
            self.apply_light_xt10_theme()
        # Se adicionar mais temas, coloque aqui

    def closeEvent(self, event):
        # Salva sessão ao fechar o app
        self.save_session()
        # Save window size (not position)
        settings = self.load_user_settings()
        settings['window_width'] = self.width()
        settings['window_height'] = self.height()
        self.save_user_settings(settings)
        event.accept()

    def eventFilter(self, obj, event):
        # ... (código inalterado) ...
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Shift:
                self.shift_pressed = True
                if self.format_popup.isVisible(): self.format_popup.hide()
                self.popup_timer.stop()
            elif event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if self.search_bar_widget: self.show_and_focus_search(); return True
        elif event.type() == QEvent.Type.KeyRelease:
            if event.key() == Qt.Key.Key_Shift:
                self.shift_pressed = False
                if self.current_editor and self.current_editor.textCursor().hasSelection():
                    self.popup_timer.start(350)
        elif event.type() == QEvent.Type.MouseButtonPress:
            # Verifica se o popup de extras está visível E se a referência existe na janela principal
            if self.extras_popup and self.extras_popup.isVisible():
                # Verifica se o clique foi fora da geometria do popup de extras
                if not self.extras_popup.geometry().contains(event.globalPosition().toPoint()):
                    # Opcional: Verifica se o clique também NÃO foi no botão que o abre
                    # (para evitar fechar imediatamente se o cálculo de geometria falhar)
                    # Isso requer acesso ao botão extras_btn do format_popup ativo, o que é complexo aqui.
                    # Vamos simplificar: fechar se clicar fora da área do extras_popup.
                    print("DEBUG: Click outside ExtrasPopup, hiding it.")
                    self.extras_popup.hide()
                    # Retorna True para consumir o evento e evitar que outros widgets reajam
                    # return True # Cuidado: isso pode impedir outras interações

        return super().eventFilter(obj, event)

    # === ADIÇÃO: Funções auxiliares para diretório padrão e permitir 0 abas ===

    def get_user_settings_path(self):
        return USER_SETTINGS_FILE

    def load_user_settings(self):
        path = self.get_user_settings_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_user_settings(self, settings_dict):
        path = self.get_user_settings_path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar user_settings.json: {e}")

    def ensure_data_dir_structure(self):
        for path in [ICON_PATH, LIGHT_ICON_PATH, UNSAVED_DIR]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        if not os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump({"tabs":[], "current_index":0}, f)
        if not os.path.exists(USER_SETTINGS_FILE):
            with open(USER_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    # Substitua o método close_tab pelo abaixo para permitir 0 abas:
    def close_tab(self, index):
        if index < 0 or index >= self.tab_widget.count(): return
        editor_to_close = self.tab_widget.widget(index)
        if not editor_to_close: return
        # Confirmação se modificado
        if editor_to_close.document().isModified():
            if not self.maybe_save(editor_to_close):
                return  # Usuário cancelou
        path = self.current_files.get(editor_to_close)
        
        # Verifica se é arquivo temporário
        is_temp = False
        if path and os.path.exists(path):
            try:
                is_temp = os.path.abspath(path).startswith(os.path.abspath(UNSAVED_DIR))
            except Exception:
                pass # Assume not temporary if path check fails

        # *** NOVO: Aviso para arquivos temporários ***
        if is_temp:
            reply = QMessageBox.question(
                self,
                "Excluir Arquivo Temporário",
                "Este é um arquivo temporário e será excluído permanentemente ao fechar esta aba. Deseja continuar?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel  # Botão padrão
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return # Usuário cancelou a exclusão
        # *** Fim do NOVO: Aviso para arquivos temporários ***

        # Remove arquivo temporário apenas se estiver na pasta unsaved_files
        # Note: A verificação `is_temp` já foi feita acima.
        if is_temp:
            try: os.remove(path)
            except Exception: pass

        if editor_to_close in self.highlighters:
            del self.highlighters[editor_to_close]
        if editor_to_close in self.current_files:
            del self.current_files[editor_to_close]
        try:
            editor_to_close.selectionChanged.disconnect()
        except Exception:
            pass
        self.tab_widget.removeTab(index)
        editor_to_close.deleteLater()
        # NÃO cria nova aba automaticamente!
        if self.tab_widget.count() == 0:
            self.show_empty_state()
        self.save_session()  # Salva sessão ao fechar aba

    def get_themed_icon(self, base_name):
        icon_to_load = None
        icon_filename = f"{base_name}.png"
        if self.current_theme == "light_xt10":
            light_icon_path = os.path.join(LIGHT_ICON_PATH, icon_filename)
            if os.path.exists(light_icon_path): icon_to_load = light_icon_path
        if icon_to_load is None:
            standard_icon_path = os.path.join(ICON_PATH, icon_filename)
            if os.path.exists(standard_icon_path): icon_to_load = standard_icon_path
        return QIcon(icon_to_load) if icon_to_load else QIcon()

    def update_icons_for_theme(self):
        # Atualiza ícone da janela principal
        self.setWindowIcon(self.get_themed_icon("app_icon"))

        for item in self.actions_with_icons:
            base_name = getattr(item, '_base_icon_name', None)
            if base_name: item.setIcon(self.get_themed_icon(base_name))
        # Atualiza ícone do Salvar Como
        if hasattr(self, 'save_as_action') and hasattr(self.save_as_action, '_base_icon_name'):
            self.save_as_action.setIcon(self.get_themed_icon(self.save_as_action._base_icon_name))

        if hasattr(self, 'search_bar_widget') and self.search_bar_widget:
            prev_bn = getattr(self.search_bar_widget.prev_btn, '_base_icon_name', None)
            if prev_bn: self.search_bar_widget.prev_btn.setIcon(self.get_themed_icon(prev_bn))
            next_bn = getattr(self.search_bar_widget.next_btn, '_base_icon_name', None)
            if next_bn: self.search_bar_widget.next_btn.setIcon(self.get_themed_icon(next_bn))

        # Atualiza o estado do botão de modo leitura
        corner_widget = self.tab_widget.cornerWidget()
        if corner_widget:
            layout = corner_widget.layout()
            if layout:
                read_mode_button = layout.itemAt(0).widget()
                if read_mode_button:
                    # Verifica se o editor atual está em modo leitura
                    is_read_mode = False
                    if self.current_editor:
                        is_read_mode = self.read_mode_states.get(self.current_editor, False)
                    read_mode_button.setChecked(is_read_mode)
                    # Só seta como read-only se houver um editor ativo
                    if self.current_editor:
                        self.current_editor.setReadOnly(is_read_mode)
                    
                    # Adiciona estilo CSS para o hover
                    read_mode_button.setStyleSheet("""
                        QToolButton {
                            padding: 2px;
                            border: 1px solid transparent;
                            border-radius: 3px;
                        }
                        QToolButton:hover {
                            background-color: rgba(255, 255, 255, 0.15);
                            border: 1px solid rgba(255, 255, 255, 0.15);
                        }
                        QToolButton:checked {
                            background-color: palette(highlight);
                            border: 1px solid palette(highlight);
                        }
                    """)
                    

        if hasattr(self, 'tab_widget'):
            corner_widget = self.tab_widget.cornerWidget()
            if corner_widget:
                # Atualiza o ícone do botão de modo leitura
                layout = corner_widget.layout()
                if layout:
                    read_mode_button = layout.itemAt(0).widget()
                    if read_mode_button and hasattr(read_mode_button, '_base_icon_name'):
                        read_mode_button.setIcon(self.get_themed_icon(read_mode_button._base_icon_name))
                
                # Atualiza o botão de criar nova aba
                if layout:
                    new_tab_button = layout.itemAt(1).widget()  # O botão de nova aba está na posição 1 do layout
                    if new_tab_button and hasattr(new_tab_button, '_base_icon_name'):
                        new_tab_button.setIcon(self.get_themed_icon(new_tab_button._base_icon_name))
                        # Adiciona estilo CSS para o hover
                        new_tab_button.setStyleSheet("""
                            QToolButton {
                                padding: 2px;
                                border: 1px solid transparent;
                                border-radius: 3px;
                            }
                            QToolButton:hover {
                                background-color: rgba(255, 255, 255, 0.2);
                                border: 1px solid rgba(255, 255, 255, 0.2);
                            }
                        """)
            
            # Atualiza botão de empty_state também
            if hasattr(self, 'empty_state_widget') and self.empty_state_widget:
                for child in self.empty_state_widget.children():
                    if isinstance(child, QToolButton) and hasattr(child, '_base_icon_name'):
                        child.setIcon(self.get_themed_icon(child._base_icon_name))
                 
        # Força a recriação completa do popup de formatação para evitar problemas de atualização
        if hasattr(self, 'format_popup'):
            text_edit = self.format_popup.text_edit  # Salva a referência do editor atual
            was_visible = self.format_popup.isVisible()  # Salva o estado de visibilidade
            pos = self.format_popup.pos()  # Salva a posição atual
            
            # Remove o popup existente
            old_popup = self.format_popup
            old_popup.hide()
            old_popup.deleteLater()
            
            # Cria um novo popup com as configurações atuais
            self.format_popup = TextFormatPopup(self)
            
            # Restaura o estado do popup se necessário
            if was_visible and text_edit:
                self.format_popup.show_at(pos, text_edit)

        # Atualiza tema do popup de extras se ele existir
        if self.extras_popup:
            self.extras_popup.update_theme()

        # Atualiza o stylesheet da janela principal (não mais necessário chamar apply_current_stylesheet aqui)
        # self.apply_current_stylesheet() # Removido, chamado por _apply_theme

        # Update toolbar quick save button icon as well
        if hasattr(self, 'quick_save_action'):
            self.quick_save_action.setIcon(self.get_themed_icon("save"))

    def _apply_theme(self, palette, stylesheet, theme_name):
        # ... (código inalterado - já chama update_icons_for_theme no final) ...
        QApplication.setPalette(palette)
        self.current_theme = theme_name # Define o tema ANTES de aplicar o stylesheet e atualizar ícones

        # Define text color based on theme
        text_color = QColor()
        if self.current_theme.startswith('dark'):
            text_color = QColor(255, 255, 255)  # White for dark themes
        else:
            text_color = QColor(0, 0, 0)  # Black for light themes

        # Update stylesheet with text color
        stylesheet = stylesheet.replace('{text_color}', text_color.name())

        # Aplica o stylesheet da janela principal AGORA
        self.setStyleSheet(stylesheet)

        # Atualiza ícones e recria o popup (que usará a nova paleta/tema)
        self.update_icons_for_theme()

        # Atualiza as cores do highlighter baseado na nova paleta
        self.update_highlighter_colors()

        # Atualiza estado dos menus/botões relacionados ao tema
        if hasattr(self, 'theme_group'):
            if hasattr(self, 'dark_xt10_action'): self.dark_xt10_action.setChecked(theme_name == "dark_xt10")
            if hasattr(self, 'dark_xt7_action'): self.dark_xt7_action.setChecked(theme_name == "dark_xt7")
            if hasattr(self, 'light_xt10_action'): self.light_xt10_action.setChecked(theme_name == "light_xt10")
            # Removido: azure_action

        # Salva a configuração do tema
        self.settings.setValue(SETTING_THEME, self.current_theme)
        self.settings.sync()

        # Atualiza tema do popup de extras se ele existir
        if self.extras_popup:
            self.extras_popup.update_theme()

    # --- apply_dark_xt10_theme, apply_dark_xt7_theme, apply_light_xt10_theme ---
    # ... (código inalterado) ...
    def apply_dark_xt10_theme(self):
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30)); p.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        p.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35)); p.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30)); p.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
        p.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255)); p.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220)); p.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        # Define highlight color with proper opacity
        highlight = QColor(42, 130, 218)
        highlight.setAlpha(127)  # ~50% opacity
        houver = QColor(255, 255, 255)
        houver.setAlpha(127) #~50% Opacity
        p.setColor(QPalette.ColorRole.Highlight, highlight)
        p.setColor(QPalette.ColorRole.HighlightedText, p.color(QPalette.ColorRole.Text))
        # Add hover color with proper opacity
        p.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, highlight)
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor(120, 120, 120))
        self._apply_theme(p, self.get_dark_stylesheet("xt10"), "dark_xt10")

    def apply_dark_xt7_theme(self):
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(45, 48, 54)); p.setColor(QPalette.ColorRole.WindowText, QColor(230, 230, 230))
        p.setColor(QPalette.ColorRole.Base, QColor(55, 60, 68)); p.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 65, 73))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 48, 54)); p.setColor(QPalette.ColorRole.ToolTipText, QColor(230, 230, 230))
        p.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255)); p.setColor(QPalette.ColorRole.Button, QColor(70, 78, 90))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230)); p.setColor(QPalette.ColorRole.Link, QColor(80, 160, 240))
        highlight = QColor(52, 110, 190)
        highlight.setAlpha(80)  # 31% opacity
        p.setColor(QPalette.ColorRole.Highlight, highlight)
        p.setColor(QPalette.ColorRole.HighlightedText, p.color(QPalette.ColorRole.Text))
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor(130, 135, 145))
        self._apply_theme(p, self.get_dark_stylesheet("xt7"), "dark_xt7")

    def apply_light_xt10_theme(self):
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240)); p.setColor(QPalette.ColorRole.WindowText, QColor(10, 10, 10))
        p.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255)); p.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220)); p.setColor(QPalette.ColorRole.ToolTipText, QColor(10, 10, 10))
        p.setColor(QPalette.ColorRole.Text, QColor(10, 10, 10)); p.setColor(QPalette.ColorRole.Button, QColor(215, 215, 215))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(10, 10, 10)); p.setColor(QPalette.ColorRole.Link, QColor(0, 100, 200))
        highlight = QColor(45, 140, 235)
        highlight.setAlpha(80)  # 31% opacity
        p.setColor(QPalette.ColorRole.Highlight, highlight)
        p.setColor(QPalette.ColorRole.HighlightedText, p.color(QPalette.ColorRole.Text))
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor(140, 140, 140))
        self._apply_theme(p, self.get_light_stylesheet(), "light_xt10")

    # Removido: apply_azure_theme

    # --- get_base_stylesheet, get_dark_stylesheet, get_light_stylesheet ---
    # ... (código inalterado - já usam get_themed_icon para close_tab_button) ...
    def get_base_stylesheet(self):
         # (Sem alterações significativas aqui em relação à última versão)
         return """
            QTabWidget::pane { border: none; }
            QTabWidget::tab-bar { alignment: left; }
            QTabBar::tab { 
                border-bottom: none; 
                padding: 5px 15px; 
                margin-right: 1px;
                /* transition: background-color 0.2s, margin-top 0.2s; */
            }
            QTabBar::tab:!selected { margin-top: 2px; }
            /* A imagem do close-button é definida dinamicamente nos stylesheets específicos */
            QTabBar::close-button { 
                subcontrol-position: right; 
                border: none; 
                border-radius: 2px; 
                padding: 2px; 
                width: 16px;
                height: 16px;
                background: transparent;
            }
            QTabBar::close-button:hover { 
                background-color: rgba(255, 255, 255, 0.2);
            }
            QTabBar QToolButton {
                /* transition: all 0.2s; */
            }
            QToolBar { border: none; spacing: 3px; padding: 2px; }
        /* TOOLBAR SEPARATOR STYLING - You can modify these values to adjust appearance */
        QToolBar::separator { background-color: #555555; width: 2px; height: 4px; margin: 8px 2px; }
            QStatusBar QLabel { padding: 0 3px; margin: 0px; }
            QStatusBar::item { border: none; }

            SearchBarWidget { background-color: transparent; border: none; padding: 0; margin: 0; }
            SearchBarWidget QLineEdit { padding: 3px 5px; }

            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px;
                margin: 1px;
            }
            QToolBar QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: {text_color};
                border-radius: 3px;
            }
            QToolBar QToolButton:checked {
                background-color: rgba(255, 255, 255, 0.25);
                color: {text_color};
                border-radius: 3px;
            }
            /* Restaurado: Estilo para botão de highlight ID */
            QToolBar QToolButton#highlightIdButton { padding: 4px; }
            /* Estilo para botões de leitura e nova aba */
            QToolBar QToolButton#readModeButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: {text_color};
                border-radius: 3px;
            }
            QToolBar QToolButton#newTabButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                color: {text_color};
                border-radius: 3px;
            }


            QScrollBar:vertical { border: none; width: 10px; margin: 0px; }
            QScrollBar::handle:vertical { min-height: 20px; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; border: none; background: none;}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
            QScrollBar:horizontal { border: none; height: 10px; margin: 0px; }
            QScrollBar::handle:horizontal { min-width: 20px; border-radius: 5px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; border: none; background: none;}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
         """

    def get_dark_stylesheet(self, variant="xt10"):
        p = QApplication.palette()
        win_bg = p.color(QPalette.ColorRole.Window).name()
        base_bg = p.color(QPalette.ColorRole.Base).name()
        text_col = p.color(QPalette.ColorRole.Text).name()
        btn_bg = p.color(QPalette.ColorRole.Button).name()
        btn_text = p.color(QPalette.ColorRole.ButtonText).name()
        highlight_col = p.color(QPalette.ColorRole.Highlight).name()
        highlight_text = p.color(QPalette.ColorRole.HighlightedText).name()
        placeholder_text_col = p.color(QPalette.ColorRole.PlaceholderText).name()
        border_col = QColor(btn_bg).lighter(110).name()
        hover_bg = QColor(btn_bg).lighter(120).name()
        pressed_bg = QColor(btn_bg).lighter(110).name()
        search_inp_bg = QColor(base_bg).lighter(110).name()
        menubar_bg = QColor(win_bg).darker(115).name()
        toolbar_bg = menubar_bg
        scrollbar_bg = toolbar_bg
        scrollbar_handle = QColor(btn_bg).lighter(150).name()
        scrollbar_handle_hover = QColor(scrollbar_handle).lighter(120).name()
        close_button_hover_bg = hover_bg
        tab_selected_bg = base_bg
        tab_inactive_bg = QColor(menubar_bg).lighter(115).name()
        tab_hover_bg = QColor(tab_inactive_bg).lighter(120).name()

        xt7_specific = ""
        if variant == "xt7":
             xt7_specific = f"""
                QPushButton, QToolBar QToolButton {{ border-radius: 4px; }}
                QToolBar QToolButton:checked {{ border: 1px solid #8cacff; background-color: {pressed_bg}; }}
                QTabBar::tab {{ border-radius: 0px !important; }}
             """

        extras_popup_styles = f"""
            ExtrasPopup {{
                background-color: {win_bg};
                border: 1px solid {border_col};
                border-radius: 4px;
            }}
            ExtrasPopup QLabel {{
                color: {text_col};
                background-color: transparent;
            }}
            ExtrasPopup QFrame[frameShape="4"] {{ /* HLine */
                border: none;
                border-top: 1px solid {border_col};
                margin-top: 2px;
                margin-bottom: 2px;
            }}
            ExtrasPopup QToolButton {{ /* Botões de expansão */
                background: transparent;
                border: none;
                color: {text_col};
                padding: 0px;
            }}
            /* Estilo do Toggle Switch (QCheckBox) */
            QCheckBox#extrasToggle::indicator {{
                width: 36px; height: 18px;
            }}
            QCheckBox#extrasToggle::indicator:unchecked {{
                image: url({os.path.join(ICON_PATH, "toggle_off.png").replace('\\', '/')});
            }}
            QCheckBox#extrasToggle::indicator:unchecked:hover {{
                 image: url({os.path.join(ICON_PATH, "toggle_off_hover.png").replace('\\', '/')});
            }}
            QCheckBox#extrasToggle::indicator:checked {{
                image: url({os.path.join(ICON_PATH, "toggle_on.png").replace('\\', '/')});
            }}
            QCheckBox#extrasToggle::indicator:checked:hover {{
                 image: url({os.path.join(ICON_PATH, "toggle_on_hover.png").replace('\\', '/')});
            }}
        """

        return self.get_base_stylesheet() + f"""
        QMainWindow {{ background-color: {win_bg}; }}
        QMenuBar {{ background-color: {menubar_bg}; color: {text_col}; border-bottom: 1px solid {border_col}; }}
        QMenuBar::item {{ background-color: transparent; color: {text_col}; padding: 4px 8px;}}
        QMenuBar::item:selected {{ background-color: {hover_bg}; }}
        QMenu {{ background-color: {menubar_bg}; color: {text_col}; border: 1px solid {border_col}; }}
        QMenu::item:selected {{ background-color: {hover_bg}; }}

        QTabWidget::pane {{ background: {base_bg}; border: none; margin-top: -1px; }} /* Pull pane up */
        QTabBar::tab {{ background: {tab_inactive_bg}; color: {text_col}; border: 1px solid {border_col}; border-bottom: none; }}
        QTabBar::tab:hover {{ background: {tab_hover_bg}; }}
        QTabBar::tab:selected {{ background: {tab_selected_bg}; border-top: 2px solid {highlight_col}; border-bottom: none; }} /* Ensure no bottom border */
        QTabBar::tab:!selected {{ background: {tab_inactive_bg}; margin-top: 2px; }}
        QTabBar::close-button {{ image: url({ICON_PATH.replace('\\','/')}/close_tab_button.png); }}
        QTabBar::close-button:hover {{ background-color: {close_button_hover_bg}; image: url({ICON_PATH.replace('\\','/')}/close_tab_button.png); }}
        QToolButton#qt_tabwidget_cornerwidget {{ padding: 2px; border: none; background: transparent; }}
        QToolButton#qt_tabwidget_cornerwidget:hover {{ background: {hover_bg}; }}

        QToolBar {{ background-color: {toolbar_bg}; }}
        QToolBar QToolButton {{ color: {btn_text}; }}
        QToolBar QToolButton:hover {{ background-color: {hover_bg}; border-color: {QColor(border_col).darker(110).name()}; }}
        QToolBar QToolButton:pressed {{ background-color: {pressed_bg}; }}
        QToolBar QToolButton:checked {{ background-color: {pressed_bg}; border: 1px solid {border_col}; }}
        QToolBar QToolButton#searchToggleButton:checked {{ background-color: {pressed_bg}; border: 1px solid {border_col}; }}
        /* Restaurado: Estilo checked para botão highlight ID */
        QToolBar QToolButton#highlightIdButton:checked {{ background-color: {pressed_bg}; border: 1px solid {border_col}; }}
        QToolBar QToolButton:disabled {{ color: palette(disabled, button-text); background-color: transparent; border-color: transparent; }}

        QStatusBar {{ background-color: {toolbar_bg}; color: {text_col}; border-top: 1px solid {border_col}; }}

        QTextEdit {{
            background-color: {base_bg}; color: {text_col}; border: 1px solid {border_col}; selection-background-color: {highlight_col}; selection-color: {highlight_text}; font: {self.default_editor_font.pointSize()}pt "{self.default_editor_font.family()}";
        }}

        SearchBarWidget QLineEdit {{ background-color: {search_inp_bg}; color: {text_col}; border: 1px solid {border_col}; border-radius: 3px; selection-background-color: {highlight_col}; selection-color: {highlight_text}; }}
        SearchBarWidget QLineEdit::placeholder {{ color: {placeholder_text_col}; }}
        SearchBarWidget QToolButton {{ margin: 0 1px; }}

        QDialog {{ background-color: {win_bg}; color: {text_col}; }}
        QLabel {{ color: {text_col}; background-color: transparent; }}
        QPushButton {{ background-color: {btn_bg}; color: {btn_text}; border: 1px solid {border_col}; border-radius: 3px; padding: 5px 15px; min-height: 18px;}}
        QPushButton:hover {{ background-color: {hover_bg}; border-color: {QColor(border_col).darker(120).name()}; }}
        QPushButton:pressed {{ background-color: {pressed_bg}; }}
        QPushButton:disabled {{ background-color: {QColor(btn_bg).lighter(110).name()}; color: palette(disabled, button-text); border-color: {QColor(border_col).lighter(110).name()}; }}

        QLineEdit, QPlainTextEdit, QSpinBox, QFontComboBox {{ background-color: {search_inp_bg}; color: {text_col}; border: 1px solid {border_col}; border-radius: 3px; padding: 3px; selection-background-color: {highlight_col}; selection-color: {highlight_text}; }}
        QLineEdit:focus, QSpinBox:focus, QFontComboBox:focus {{ border: 1px solid {highlight_col}; }}
        QLineEdit::placeholder {{ color: {placeholder_text_col}; }}

        QScrollBar:vertical {{ background-color: {scrollbar_bg}; }}
        QScrollBar::handle:vertical {{ background-color: {scrollbar_handle}; border: 1px solid {border_col}; }}
        QScrollBar::handle:vertical:hover {{ background-color: {scrollbar_handle_hover}; }}
        QScrollBar:horizontal {{ background-color: {scrollbar_bg}; }}
        QScrollBar::handle:horizontal {{ background-color: {scrollbar_handle}; border: 1px solid {border_col}; }}
        QScrollBar::handle:horizontal:hover {{ background-color: {scrollbar_handle_hover}; }}
        {xt7_specific}
        {extras_popup_styles}
        """

    def get_light_stylesheet(self):
        p = QApplication.palette()
        win_bg = p.color(QPalette.ColorRole.Window).name()
        base_bg = p.color(QPalette.ColorRole.Base).name()
        text_col = p.color(QPalette.ColorRole.Text).name()
        btn_bg = p.color(QPalette.ColorRole.Button).name()
        btn_text = p.color(QPalette.ColorRole.ButtonText).name()
        highlight_col = p.color(QPalette.ColorRole.Highlight).name()
        highlight_text = p.color(QPalette.ColorRole.HighlightedText).name()
        placeholder_text_col = p.color(QPalette.ColorRole.PlaceholderText).name()
        border_col = QColor(btn_bg).darker(115).name()
        hover_bg = QColor(btn_bg).darker(110).name()
        pressed_bg = QColor(btn_bg).darker(120).name()
        search_inp_bg = QColor(base_bg).lighter(110).name()
        menubar_bg = QColor(win_bg).darker(105).name()
        toolbar_bg = menubar_bg
        scrollbar_bg = toolbar_bg
        scrollbar_handle = QColor(btn_bg).darker(180).name()  # Darker for better contrast
        scrollbar_handle_hover = QColor(scrollbar_handle).darker(120).name()
        close_button_hover_bg = hover_bg
        tab_selected_bg = base_bg
        tab_inactive_bg = QColor(menubar_bg).lighter(115).name()
        tab_hover_bg = QColor(tab_inactive_bg).lighter(120).name()

        extras_popup_styles = f"""
            ExtrasPopup {{
                background-color: {win_bg};
                border: 1px solid {border_col};
                border-radius: 4px;
            }}
            ExtrasPopup QLabel {{
                color: {text_col};
                background-color: transparent;
            }}
            ExtrasPopup QFrame[frameShape="4"] {{ /* HLine */
                border: none;
                border-top: 1px solid {border_col};
                margin-top: 2px;
                margin-bottom: 2px;
            }}
             ExtrasPopup QToolButton {{
                background: transparent;
                border: none;
                color: {text_col};
                padding: 0px;
            }}
            /* Estilo do Toggle Switch (QCheckBox) */
            QCheckBox#extrasToggle::indicator {{
                width: 36px; height: 18px;
            }}
             /* Para tema claro, talvez usar ícones específicos _light? */
            QCheckBox#extrasToggle::indicator:unchecked {{
                image: url({os.path.join(LIGHT_ICON_PATH, "toggle_off.png").replace('\\', '/')});
            }}
            QCheckBox#extrasToggle::indicator:unchecked:hover {{
                 image: url({os.path.join(LIGHT_ICON_PATH, "toggle_off_hover.png").replace('\\', '/')});
            }}
            QCheckBox#extrasToggle::indicator:checked {{
                image: url({os.path.join(LIGHT_ICON_PATH, "toggle_on.png").replace('\\', '/')});
            }}
            QCheckBox#extrasToggle::indicator:checked:hover {{
                 image: url({os.path.join(LIGHT_ICON_PATH, "toggle_on_hover.png").replace('\\', '/')});
            }}
        """

        return self.get_base_stylesheet() + f"""
        QMainWindow {{ background-color: {win_bg}; }}
        QMenuBar {{ background-color: {menubar_bg}; color: {text_col}; border-bottom: 1px solid {border_col}; }}
        QMenuBar::item {{ background-color: transparent; color: {text_col}; padding: 4px 8px;}}
        QMenuBar::item:selected {{ background-color: {hover_bg}; color: {highlight_text}; }}
        QMenu {{ background-color: {menubar_bg}; color: {text_col}; border: 1px solid {border_col}; }}
        QMenu::item:selected {{ background-color: {hover_bg}; color: {highlight_text}; }}

        QTabWidget::pane {{ background: {base_bg}; border: none; margin-top: -1px; }} /* Pull pane up */
        QTabBar::tab {{ background: {tab_inactive_bg}; color: {text_col}; border: 1px solid {border_col}; border-bottom: none;}}
        QTabBar::tab:hover {{ background: {tab_hover_bg}; }}
        QTabBar::tab:selected {{ background: {tab_selected_bg}; border-top: 2px solid {highlight_col}; border-bottom: none; }} /* Ensure no bottom border */
        QTabBar::tab:!selected {{ background: {tab_inactive_bg}; margin-top: 2px; }}
        QTabBar::close-button {{ image: url(light_icons/close_tab_button.png); }}
        QTabBar::close-button:hover {{ background-color: {close_button_hover_bg}; image: url(light_icons/close_tab_button.png); }}
        QToolButton#qt_tabwidget_cornerwidget {{ padding: 2px; border: none; background: transparent; }}
        QToolButton#qt_tabwidget_cornerwidget:hover {{ background: {hover_bg}; }}

        QToolBar {{ background-color: {toolbar_bg}; border-bottom: 1px solid {border_col}; }}
        QToolBar QToolButton {{ color: {btn_text}; }}
        QToolBar QToolButton:hover {{ background-color: {hover_bg}; border-color: {QColor(border_col).darker(110).name()}; }}
        QToolBar QToolButton:pressed {{ background-color: {pressed_bg}; }}
        QToolBar QToolButton:checked {{ background-color: {pressed_bg}; border: 1px solid {border_col}; }}
        QToolBar QToolButton#searchToggleButton:checked {{ background-color: {pressed_bg}; border: 1px solid {border_col}; }}
        /* Restaurado: Estilo checked para botão highlight ID */
        QToolBar QToolButton#highlightIdButton:checked {{ background-color: {pressed_bg}; border: 1px solid {border_col}; }}
        QToolBar QToolButton:disabled {{ color: palette(disabled, button-text); background-color: transparent; border-color: transparent; }}
        /* TOOLBAR SEPARATOR STYLING - You can modify these values to adjust appearance */
        QToolBar::separator {{ background-color: #333333; width: 2px; height: 4px; margin: 8px 4px; }}

        QStatusBar {{ background-color: {toolbar_bg}; color: {text_col}; border-top: 1px solid {border_col}; }}

        QTextEdit {{
            background-color: {base_bg}; color: {text_col}; border: 1px solid {border_col}; selection-background-color: {highlight_col}; selection-color: {highlight_text}; font: {self.default_editor_font.pointSize()}pt "{self.default_editor_font.family()}";
        }}

        SearchBarWidget QLineEdit {{ background-color: {search_inp_bg}; color: {text_col}; border: 1px solid {border_col}; border-radius: 3px; selection-background-color: {highlight_col}; selection-color: {highlight_text}; }}
        SearchBarWidget QLineEdit::placeholder {{ color: {placeholder_text_col}; }}
        SearchBarWidget QToolButton {{ margin: 0 1px; }}

        QDialog {{ background-color: {win_bg}; color: {text_col}; }}
        QLabel {{ color: {text_col}; background-color: transparent; }}
        QPushButton {{ background-color: {btn_bg}; color: {btn_text}; border: 1px solid {border_col}; border-radius: 3px; padding: 5px 15px; min-height: 18px;}}
        QPushButton:hover {{ background-color: {hover_bg}; border-color: {QColor(border_col).darker(120).name()}; }}
        QPushButton:pressed {{ background-color: {pressed_bg}; }}
        QPushButton:disabled {{ background-color: {QColor(btn_bg).lighter(110).name()}; color: palette(disabled, button-text); border-color: {QColor(border_col).lighter(110).name()}; }}

        QLineEdit, QPlainTextEdit, QSpinBox, QFontComboBox {{ background-color: {search_inp_bg}; color: {text_col}; border: 1px solid {border_col}; border-radius: 3px; padding: 3px; selection-background-color: {highlight_col}; selection-color: {highlight_text}; }}
        QLineEdit:focus, QSpinBox:focus, QFontComboBox:focus {{ border: 1px solid {highlight_col}; }}
        QLineEdit::placeholder {{ color: {placeholder_text_col}; }}

        QScrollBar:vertical {{ background-color: {scrollbar_bg}; }}
        QScrollBar::handle:vertical {{ background-color: {scrollbar_handle}; border: 1px solid {border_col}; }}
        QScrollBar::handle:vertical:hover {{ background-color: {scrollbar_handle_hover}; }}
        QScrollBar:horizontal {{ background-color: {scrollbar_bg}; }}
        QScrollBar::handle:horizontal {{ background-color: {scrollbar_handle}; border: 1px solid {border_col}; }}
        QScrollBar::handle:horizontal:hover {{ background-color: {scrollbar_handle_hover}; }}
        {extras_popup_styles}
        """

    # --- UI Setup ---
    def setup_ui(self):
     central_widget = QWidget()
     self.setCentralWidget(central_widget)
     self.central_stack = QStackedLayout(central_widget)

     # --- Tab Widget ---
     self.tab_widget = QTabWidget()
     self.tab_widget.setTabBar(EditableTabBar())
     self.tab_widget.tabBar().edit_finished.connect(self.on_tab_renamed)
     self.tab_widget.setTabsClosable(True)
     self.tab_widget.setMovable(True)
     self.tab_widget.tabCloseRequested.connect(self.close_tab)
     self.tab_widget.currentChanged.connect(lambda index: self.update_current_editor(index))
     self.central_stack.addWidget(self.tab_widget)
 
     # Cria um layout horizontal para os botões do canto
     corner_layout = QHBoxLayout()
     corner_layout.setContentsMargins(0, 0, 0, 0)
     corner_layout.setSpacing(2)
     
     # Botão de Modo Leitura
     read_mode_button = QToolButton()
     read_mode_button.setCheckable(True)
     read_mode_button.setToolTip("Ativar/Desativar Modo Leitura\nPermite visualizar o texto sem poder editá-lo")
     read_mode_button.clicked.connect(lambda: self.toggle_read_mode(self.current_editor))
     read_mode_button.setStyleSheet("""
         QToolButton {
             padding: 2px;
             border: none;
             background: transparent;
         }
         QToolButton:hover {
             background-color: rgba(255, 255, 255, 0.15);
             border: 1px solid rgba(255, 255, 255, 0.15);
             border-radius: 3px;
         }

         QToolButton:checked {
             background-color: palette(highlight);
             border: 1px solid palette(highlight);
             border-radius: 3px;
         }
     """)

     corner_layout.addWidget(read_mode_button)
     
     # Botão de Nova Aba
     corner_button = QToolButton()
     corner_button.setToolTip("Nova Aba (Ctrl+N)")
     corner_button.setAutoRaise(True)
     corner_button.setObjectName("qt_tabwidget_cornerwidget")
     corner_button.clicked.connect(self.new_tab)
     corner_layout.addWidget(corner_button)
     
     # Cria um widget para conter o layout
     corner_widget = QWidget()
     corner_widget.setLayout(corner_layout)
     self.tab_widget.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)
     
     # Atualiza os ícones dos botões após inicialização completa
     read_mode_button.setIcon(self.get_themed_icon("read_mode"))
     read_mode_button._base_icon_name = "read_mode"
     corner_button.setIcon(self.get_themed_icon("add"))
     corner_button._base_icon_name = "add"

     # --- Empty State Widget ---
     self.empty_state_widget = QWidget()
     empty_layout = QVBoxLayout(self.empty_state_widget)
     empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
     title = QLabel("Oops! Nada Aqui.")
     title.setStyleSheet("font-size: 2.2em; font-weight: bold; opacity: 0.65; color: palette(window-text);")
     title.setAlignment(Qt.AlignmentFlag.AlignCenter)
     empty_layout.addWidget(title)
     subtitle = QLabel('Crie uma "Nova Aba" para usar o Ninthpads.')
     subtitle.setStyleSheet("font-size: 1.2em; opacity: 0.45; color: palette(window-text);")
     subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
     empty_layout.addWidget(subtitle)
     empty_nova_aba_btn = QToolButton()
     empty_nova_aba_btn.setText("Nova Aba")
     empty_nova_aba_btn.setToolTip("Nova Aba (Ctrl+N)")
     empty_nova_aba_btn.setIcon(self.get_themed_icon("add"))
     empty_nova_aba_btn._base_icon_name = "add"  # Para atualização automática
     empty_nova_aba_btn.setAutoRaise(True)
     empty_nova_aba_btn.setCursor(Qt.CursorShape.PointingHandCursor)
     # Ajusta cor para tema claro
     if hasattr(self, 'current_theme') and self.current_theme == "light_xt10":
         empty_nova_aba_btn.setStyleSheet("font-size: 1.1em; padding: 8px 16px; margin-top: 16px; color: #222;")
     else:
         empty_nova_aba_btn.setStyleSheet("font-size: 1.1em; padding: 8px 16px; margin-top: 16px;")
     empty_nova_aba_btn.clicked.connect(self.new_tab)
     empty_layout.addWidget(empty_nova_aba_btn, alignment=Qt.AlignmentFlag.AlignCenter)

     self.central_stack.addWidget(self.empty_state_widget)

     # Show the correct state at startup
     self.central_stack.setCurrentWidget(self.tab_widget)

     self.create_menus()
     self.create_toolbar()
     self.create_status_bar()
     # Removido: self.new_tab()  # Só cria aba se não houver sessão

     self.apply_current_stylesheet()

    def create_menus(self):
        menu_bar = self.menuBar()
        self.actions_with_icons = []
        format_menu = menu_bar.addMenu("F&ormatar")
        self.word_wrap_action = QAction("&Quebra de Linha", self, checkable=True)
        self.word_wrap_action.setChecked(self.default_word_wrap)
        self.word_wrap_action.triggered.connect(self.toggle_default_word_wrap)
        format_menu.addAction(self.word_wrap_action)
        # [CASCADE] Aplica word wrap a todos os editores abertos após criar QAction
        if hasattr(self, 'tab_widget') and self.tab_widget.count() > 0:
            for i in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(i)
                if editor:
                    wrap_mode = QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere if self.default_word_wrap else QTextOption.WrapMode.NoWrap
                    editor.setWordWrapMode(wrap_mode)

        font_action = QAction("&Fonte Padrão...", self)
        font_action.triggered.connect(self.change_default_editor_font)
        format_menu.addAction(font_action)
        format_menu.addSeparator()

        # --- Submenu Popup de Formatação ---
        popup_menu = format_menu.addMenu("Popup de Formatação")
        self.popup_mode_group = QActionGroup(self)
        self.popup_mode_group.setExclusive(True)
        self.popup_mode_selection = QAction("Seleção (Única)", self, checkable=True)
        self.popup_mode_selection.setToolTip("Mostra o popup ao selecionar texto (exceto se shift)")
        self.popup_mode_selection.triggered.connect(lambda: self.set_format_popup_mode('selection'))
        self.popup_mode_selection._popup_mode = 'selection'
        self.popup_mode_selection.setChecked(False)
        self.popup_mode_click = QAction("Seleção + Clique", self, checkable=True)
        self.popup_mode_click.setToolTip("Mostra o popup apenas ao clicar com o botão direito sobre seleção")
        self.popup_mode_click.triggered.connect(lambda: self.set_format_popup_mode('selection_click'))
        self.popup_mode_click._popup_mode = 'selection_click'
        self.popup_mode_click.setChecked(False)
        self.popup_mode_statusbar = QAction("Barra de Status", self, checkable=True)
        self.popup_mode_statusbar.setToolTip("Popup sempre visível acima da barra de status")
        self.popup_mode_statusbar.triggered.connect(lambda: self.set_format_popup_mode('statusbar'))
        self.popup_mode_statusbar._popup_mode = 'statusbar'
        self.popup_mode_statusbar.setChecked(False)
        for act in [self.popup_mode_selection, self.popup_mode_click, self.popup_mode_statusbar]:
            self.popup_mode_group.addAction(act)
            popup_menu.addAction(act)
        # Estado inicial
        mode = getattr(self, 'format_popup_mode', None) or self.settings.value(SETTING_HIGHLIGHT_MODE, 'selection')
        self.set_format_popup_mode(mode, update_menu=True)

        format_menu.addSeparator()
        # ...existing code...

    def set_format_popup_mode(self, mode, update_menu=False):
        self.format_popup_mode = mode
        if hasattr(self, 'settings'):
            self.settings.setValue(SETTING_HIGHLIGHT_MODE, mode)
        if update_menu:
            if mode == 'selection':
                self.popup_mode_selection.setChecked(True)
            elif mode == 'selection_click':
                self.popup_mode_click.setChecked(True)
            elif mode == 'statusbar':
                self.popup_mode_statusbar.setChecked(True)
        # Atualiza popup imediatamente se necessário
        if mode == 'statusbar':
            self.show_format_popup_statusbar()
        else:
            self.format_popup.hide()

    def handle_selection_changed(self):
        sender_editor = self.sender()
        if sender_editor and sender_editor == self.current_editor:
            cursor = sender_editor.textCursor()
            mode = getattr(self, 'format_popup_mode', 'selection')
            if mode == 'statusbar':
                self.format_popup.update_format_buttons()
            # No modo seleção, só mostra o popup se:
            # 1. Não estiver com shift pressionado
            # 2. Houver uma seleção
            # 3. A seleção NÃO foi feita pela barra de busca
            if mode == 'selection':
                if (cursor.hasSelection() and 
                    not self.shift_pressed and 
                    not (hasattr(self, 'search_bar_widget') and 
                         self.search_bar_widget.search_active)):
                    self.popup_timer.start(350)
                else:
                    self.popup_timer.stop()
                    self.format_popup.hide()
            else:
                self.popup_timer.stop()
                self.format_popup.hide()

    def show_format_popup(self):
        mode = getattr(self, 'format_popup_mode', 'selection')
        if mode == "statusbar":
            self.show_format_popup_statusbar()
            return
        if mode == "selection":
            if self.shift_pressed or not self.current_editor or not self.current_editor.textCursor().hasSelection():
                if getattr(self, 'format_popup_mode', '') != 'statusbar':
                    self.format_popup.hide()
                return
            cursor = self.current_editor.textCursor()
            if cursor.hasSelection():
                if getattr(self, 'format_popup_mode', '') != 'statusbar':
                    rect = self.current_editor.cursorRect(cursor)
                    global_pos = self.current_editor.mapToGlobal(rect.bottomLeft())
                    global_pos.setY(global_pos.y() + 3)
                    self.format_popup.setWindowFlags(Qt.WindowType.Popup)
                    self.format_popup.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
                    self.format_popup.setLineWidth(1)
                    self.format_popup.show_at(global_pos, self.current_editor)
            else:
                if getattr(self, 'format_popup_mode', '') != 'statusbar':
                    self.format_popup.hide()
        elif mode == "selection_click":
            if getattr(self, 'format_popup_mode', '') != 'statusbar':
                self.format_popup.hide()

    def eventFilter(self, obj, event):
        # ...existing code...
        if event.type() == QEvent.Type.MouseButtonPress:
            if getattr(self, 'format_popup_mode', 'selection') == "selection_click":
                if event.button() == Qt.MouseButton.RightButton and self.current_editor and self.current_editor.textCursor().hasSelection():
                    if getattr(self, 'format_popup_mode', '') != 'statusbar':
                        cursor = self.current_editor.textCursor()
                        rect = self.current_editor.cursorRect(cursor)
                        global_pos = self.current_editor.mapToGlobal(rect.bottomLeft())
                        global_pos.setY(global_pos.y() + 3)
                        self.format_popup.setWindowFlags(Qt.WindowType.Popup)
                        self.format_popup.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
                        self.format_popup.setLineWidth(1)
                        self.format_popup.show_at(global_pos, self.current_editor)
                        self.format_popup.show()
                        return True
                else:
                    if getattr(self, 'format_popup_mode', '') != 'statusbar':
                        self.format_popup.hide()
            # ...existing code...
        return super().eventFilter(obj, event)

    def show_format_popup_statusbar(self):
        if not self.current_editor:
            return
        sb_rect = self.status_bar.rect()
        sb_top_left = self.status_bar.mapToGlobal(sb_rect.topLeft())
        sb_width = sb_rect.width()
        popup_width = self.format_popup.width() if self.format_popup.width() > 0 else 300
        x = sb_top_left.x() + (sb_width - popup_width) // 2
        y = sb_top_left.y() - self.format_popup.height() - 2
        self.format_popup.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self.format_popup.setMinimumSize(300, 40)
        self.format_popup.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Plain)
        self.format_popup.setLineWidth(0)
        self.format_popup.show_at(QPoint(int(x), int(y)), self.current_editor)
        self.format_popup.show()

    def create_menus(self):
        # ... (código do menu tema e arquivo inalterado) ...
        menu_bar = self.menuBar()
        self.actions_with_icons = []

        # --- Menu Tema ---
        theme_menu = menu_bar.addMenu("&Tema")
        self.theme_group = QActionGroup(self); self.theme_group.setExclusive(True)
        # Adiciona Ícones
        self.dark_xt10_action = QAction(self.get_themed_icon("oblivion"), "Oblivion", self, checkable=True); self.dark_xt10_action._base_icon_name = "oblivion"
        self.dark_xt7_action = QAction(self.get_themed_icon("midtones"), "Midtones", self, checkable=True); self.dark_xt7_action._base_icon_name = "midtones"
        self.light_xt10_action = QAction(self.get_themed_icon("light"), "Light", self, checkable=True); self.light_xt10_action._base_icon_name = "light"
        theme_actions = [self.dark_xt10_action, self.dark_xt7_action, self.light_xt10_action]
        theme_menu.addActions(theme_actions)
        for action in theme_actions:
            self.theme_group.addAction(action)
            if hasattr(action, '_base_icon_name'): # Garante que adiciona à lista
                self.actions_with_icons.append(action)
        self.theme_group.triggered.connect(self.handle_theme_change)

        # --- Menu Arquivo ---
        file_menu = menu_bar.addMenu("&Arquivo")
        file_actions = [
            ("&Nova Aba", "Ctrl+N", "new", self.new_tab),
            ("&Abrir...", "Ctrl+O", "open", self.open_file),
            ("&Salvar", "Ctrl+S", "save", self.save_to_app_dir),  # Unified save functionality
            ("Salvar &Como...", "Ctrl+Shift+S", "save_as", self.save_as_file),
            ("Abrir Arquivo &NXT...", None, "open_nxt", lambda: self.open_file(nxt_only=True)),
            ("Salvar Como Arquivo &NXT...", None, "save_nxt", self.save_nxt_to_app_dir),
            None,
            ("&Sair", "Ctrl+Q", "exit", self.close)
        ]
        self._add_actions_to_menu(file_menu, file_actions)

        # --- Menu Editar ---
        edit_menu = menu_bar.addMenu("&Editar")
        edit_actions = [
            ("&Desfazer", "Ctrl+Z", "undo", lambda: self.current_editor.undo() if self.current_editor else None),
            ("&Refazer", "Ctrl+Y", "redo", lambda: self.current_editor.redo() if self.current_editor else None),
            None,
            ("&Recortar", "Ctrl+X", "cut", lambda: self.current_editor.cut() if self.current_editor else None),
            ("&Copiar", "Ctrl+C", "copy", lambda: self.current_editor.copy() if self.current_editor else None),
            ("&Colar", "Ctrl+V", "paste", lambda: self.current_editor.paste() if self.current_editor else None),
            None,
            ("&Localizar...", "Ctrl+F", "search", self.show_and_focus_search),
            ("Selecionar &Tudo", "Ctrl+A", "select_all", lambda: self.current_editor.selectAll() if self.current_editor else None)
        ]
        self._add_actions_to_menu(edit_menu, edit_actions)

        # --- Menu Formatar ---
        format_menu = menu_bar.addMenu("F&ormatar")
        self.word_wrap_action = QAction("&Quebra de Linha", self, checkable=True)
        self.word_wrap_action.setChecked(self.default_word_wrap)
        self.word_wrap_action.triggered.connect(self.toggle_default_word_wrap)
        format_menu.addAction(self.word_wrap_action)
        # [CASCADE] Aplica word wrap a todos os editores abertos após criar QAction
        if hasattr(self, 'tab_widget') and self.tab_widget.count() > 0:
            for i in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(i)
                if editor:
                    wrap_mode = QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere if self.default_word_wrap else QTextOption.WrapMode.NoWrap
                    editor.setWordWrapMode(wrap_mode)

        font_action = QAction("&Fonte Padrão...", self)
        font_action.triggered.connect(self.change_default_editor_font)
        format_menu.addAction(font_action)
        format_menu.addSeparator()

        # --- Submenu Popup de Formatação ---
        popup_menu = format_menu.addMenu("Popup de Formatação")
        self.popup_mode_group = QActionGroup(self)
        self.popup_mode_group.setExclusive(True)
        self.popup_mode_selection = QAction("Seleção (Única)", self, checkable=True)
        self.popup_mode_selection.setToolTip("Mostra o popup ao selecionar texto (exceto se shift)")
        self.popup_mode_selection.triggered.connect(lambda: self.set_format_popup_mode('selection'))
        self.popup_mode_selection._popup_mode = 'selection'
        self.popup_mode_selection.setChecked(False)
        self.popup_mode_click = QAction("Seleção + Clique", self, checkable=True)
        self.popup_mode_click.setToolTip("Mostra o popup apenas ao clicar com o botão direito sobre seleção")
        self.popup_mode_click.triggered.connect(lambda: self.set_format_popup_mode('selection_click'))
        self.popup_mode_click._popup_mode = 'selection_click'
        self.popup_mode_click.setChecked(False)
        self.popup_mode_statusbar = QAction("Barra de Status", self, checkable=True)
        self.popup_mode_statusbar.setToolTip("Popup sempre visível acima da barra de status")
        self.popup_mode_statusbar.triggered.connect(lambda: self.set_format_popup_mode('statusbar'))
        self.popup_mode_statusbar._popup_mode = 'statusbar'
        self.popup_mode_statusbar.setChecked(False)
        for act in [self.popup_mode_selection, self.popup_mode_click, self.popup_mode_statusbar]:
            self.popup_mode_group.addAction(act)
            popup_menu.addAction(act)
        # Estado inicial
        mode = getattr(self, 'format_popup_mode', None) or self.settings.value(SETTING_HIGHLIGHT_MODE, 'selection')
        self.set_format_popup_mode(mode, update_menu=True)

        format_menu.addSeparator()

        # --- Submenu Highlighting Em ---
        highlighting_menu = format_menu.addMenu("Highlighting Em")
        
        # Grupo de radio buttons exclusivos
        self.highlight_group = QActionGroup(self)
        self.highlight_group.setExclusive(True)
        
        # Radio button para modo cursor
        self.highlight_cursor_only_action = QAction("Cursor", self, checkable=True)
        self.highlight_cursor_only_action.setToolTip("O ID sob o cursor determina qual ID é destacado em todo o documento.")
        self.highlight_cursor_only_action.triggered.connect(self.toggle_highlight_cursor_setting)
        self.highlight_group.addAction(self.highlight_cursor_only_action)
        highlighting_menu.addAction(self.highlight_cursor_only_action)
        
        # Radio button para modo highlighter
        self.highlight_global_action = QAction("Highlighter", self, checkable=True)
        self.highlight_global_action.setToolTip("O ID definido globalmente (botão na barra) é usado para destacar o texto.")
        self.highlight_global_action.triggered.connect(lambda: self.toggle_highlight_cursor_setting(False))
        self.highlight_group.addAction(self.highlight_global_action)
        highlighting_menu.addAction(self.highlight_global_action)
        
        # Define o estado inicial baseado na configuração atual
        highlight_mode = self.settings.value(SETTING_HIGHLIGHT_CURSOR_ONLY, None)
        if highlight_mode is not None:
            if isinstance(highlight_mode, str):
                if highlight_mode.lower() in ("true", "1"): self.highlight_cursor_only = True
                elif highlight_mode.lower() in ("false", "0"): self.highlight_cursor_only = False
                else:
                    try:
                        self.highlight_cursor_only = bool(int(highlight_mode))
                    except Exception:
                        self.highlight_cursor_only = bool(highlight_mode)
            else:
                self.highlight_cursor_only = bool(highlight_mode)
        if self.highlight_cursor_only:
            self.highlight_cursor_only_action.setChecked(True)
            self.toggle_highlight_cursor_setting(True)
        else:
            self.highlight_global_action.setChecked(True)
            self.toggle_highlight_cursor_setting(False)

        # --- Menu Exibir ---
        # ... (código inalterado) ...
        view_menu = menu_bar.addMenu("E&xibir")
        self.toolbar_action = QAction("Barra de &Ferramentas", self, checkable=True)
        self.toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(self.toolbar_action)
        self.statusbar_action = QAction("Barra de &Status", self, checkable=True)
        self.statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(self.statusbar_action)
        view_menu.addSeparator()
        # --- Submenu Contadores ---
        counters_menu = view_menu.addMenu("Contadores")
        # Checkbox para contagem de linhas
        self.show_line_count_action = QAction("Linhas", self, checkable=True)
        self.show_line_count_action.triggered.connect(self.toggle_status_counters)
        counters_menu.addAction(self.show_line_count_action)
        # Checkbox para contagem de caracteres
        self.show_char_count_action = QAction("Caracteres", self, checkable=True)
        self.show_char_count_action.triggered.connect(self.toggle_status_counters)
        counters_menu.addAction(self.show_char_count_action)
        # Checkbox para contagem de palavras
        self.show_word_count_action = QAction("Palavras", self, checkable=True)
        self.show_word_count_action.triggered.connect(self.toggle_status_counters)
        counters_menu.addAction(self.show_word_count_action)

        # Remove duplicate counters from the menu
        view_menu.removeAction(self.show_char_count_action)
        view_menu.removeAction(self.show_word_count_action)
        view_menu.removeAction(self.show_line_count_action)

        # --- Menu Ajuda ---
        help_menu = menu_bar.addMenu("A&juda")
        about_action = QAction(self.get_themed_icon("about"), "&Sobre", self)
        about_action.triggered.connect(self.show_about)
        about_action._base_icon_name = "about"
        help_menu.addAction(about_action)


    def _add_actions_to_menu(self, menu, actions_data):
        # ... (código inalterado) ...
        for item in actions_data:
            if item is None: menu.addSeparator()
            else:
                text, shortcut, icon_base_name, handler = item
                icon = self.get_themed_icon(icon_base_name) if icon_base_name else QIcon()
                action = QAction(icon, text, self)
                if shortcut: action.setShortcut(shortcut)
                action.triggered.connect(handler)
                if icon_base_name:
                    action._base_icon_name = icon_base_name
                    self.actions_with_icons.append(action)
                menu.addAction(action)

    def handle_theme_change(self, action):
        # ... (código inalterado) ...
        if action == self.dark_xt10_action: self.apply_dark_xt10_theme()
        elif action == self.dark_xt7_action: self.apply_dark_xt7_theme()
        elif action == self.light_xt10_action: self.apply_light_xt10_theme()
        # Atualiza todos os componentes do tema imediatamente
        self.update_theme_all()
        # Save theme choice
        settings = self.load_user_settings()
        # Store under ui/theme for compatibility
        if action == self.dark_xt10_action:
            settings['ui/theme'] = 'dark_xt10'
        elif action == self.dark_xt7_action:
            settings['ui/theme'] = 'dark_xt7'
        elif action == self.light_xt10_action:
            settings['ui/theme'] = 'light_xt10'
        self.save_user_settings(settings)

    def update_theme_all(self):
        """Reaplica o tema, stylesheet, ícones e popups."""
        # Reaplica o stylesheet da janela principal
        self.apply_current_stylesheet()
        # Atualiza ícones para o tema atual
        self.update_icons_for_theme()
        # Atualiza cores dos highlighters
        self.update_highlighter_colors()
        # Atualiza popups se existirem
        if hasattr(self, 'format_popup') and self.format_popup:
            self.format_popup.update_theme()
        if hasattr(self, 'extras_popup') and self.extras_popup:
            self.extras_popup.update_theme()
        if hasattr(self, 'update_empty_state_theme'):
            self.update_empty_state_theme()
        if getattr(self, 'format_popup_mode', '') == 'statusbar':
            QTimer.singleShot(0, self.show_format_popup_statusbar)

    def update_empty_state_theme(self):
        # Atualiza o botão do empty state para o tema atual
        if hasattr(self, 'empty_state_widget') and self.empty_state_widget:
            btns = self.empty_state_widget.findChildren(QPushButton)
            for btn in btns:
                if hasattr(btn, '_base_icon_name'):
                    btn.setIcon(self.get_themed_icon(btn._base_icon_name))
                # Atualiza stylesheet se necessário
                btn.setStyleSheet("")
            self.empty_state_widget.setStyleSheet("")

    def create_toolbar(self):
        # ... (código ações toolbar inalterado) ...
        self.toolbar = QToolBar("Barra de Ferramentas")
        # Botão de salvar (unificado)
        self.quick_save_action = QAction(self.get_themed_icon("save"), "Salvar", self)
        self.quick_save_action.setToolTip("Salvar o arquivo atual")
        self.quick_save_action.triggered.connect(self.save_to_app_dir)
        self.toolbar.addAction(self.quick_save_action)
        self.actions_with_icons.append(self.quick_save_action)

        # Botão Salvar Como (Save As) após Abrir
        self.save_as_action = QAction(self.get_themed_icon("save_as"), "Salvar Como", self)
        self.save_as_action._base_icon_name = "save_as"  # Para atualização automática
        self.save_as_action.setToolTip("Salvar Como (escolher diretório)")
        self.save_as_action.triggered.connect(self.save_as_file)
        self.toolbar.addAction(self.save_as_action)
        self.actions_with_icons.append(self.save_as_action)

        self.toolbar.setIconSize(QSize(18, 18))
        # self.toolbar.setMovable(False) # Removido - torna a toolbar móvel por padrão
        self.toolbar.setMovable(True)   # Explicitamente torna a toolbar móvel
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        toolbar_actions_data = [
            ("Nova Aba", "new", self.new_tab), ("Abrir", "open", self.open_file),
            None, ("Recortar", "cut", lambda: self.current_editor.cut() if self.current_editor else None),
            ("Copiar", "copy", lambda: self.current_editor.copy() if self.current_editor else None),
            ("Colar", "paste", lambda: self.current_editor.paste() if self.current_editor else None),
            None, ("Desfazer", "undo", lambda: self.current_editor.undo() if self.current_editor else None),
            ("Refazer", "redo", lambda: self.current_editor.redo() if self.current_editor else None),
        ]
        for item in toolbar_actions_data:
             if item is None:
                 self.toolbar.addSeparator()
             else:
                 text, icon_base_name, handler = item
                 icon = self.get_themed_icon(icon_base_name)
                 action = QAction(icon, text, self)
                 action.setStatusTip(text)
                 action.triggered.connect(handler)
                 action._base_icon_name = icon_base_name
                 self.toolbar.addAction(action)
                 self.actions_with_icons.append(action)
        # Only add the unified save button (already added above)


        self.search_bar_widget = SearchBarWidget(self)
        self.toolbar.addWidget(self.search_bar_widget)

        spacer = QWidget(); spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred); self.toolbar.addWidget(spacer)

        search_icon_base = "search"
        self.toggle_search_action = QAction(self.get_themed_icon(search_icon_base), "Mostrar/Esconder Barra de Busca", self); self.toggle_search_action.setCheckable(True)
        self.toggle_search_action.setStatusTip("Mostrar/Esconder Barra de Busca"); self.toggle_search_action.triggered.connect(self.toggle_search_bar_visibility)
        self.toggle_search_action._base_icon_name = search_icon_base; self.toolbar.addAction(self.toggle_search_action); self.actions_with_icons.append(self.toggle_search_action)
        search_toggle_button_widget = self.toolbar.widgetForAction(self.toggle_search_action)
        if search_toggle_button_widget: search_toggle_button_widget.setObjectName("searchToggleButton")

        # --- Botão Highlight ID (Toolbar) --- ÍCONE CORRIGIDO
        # Usa id_lighter.png
        highlight_id_icon_base = "id_lighter"
        # Botão NÃO é mais checkable
        self.highlight_id_action = QAction(self.get_themed_icon(highlight_id_icon_base), "Definir ID de Highlight Global", self)
        self.highlight_id_action.setToolTip(f"Define qual ID (1-{MAX_HIGHLIGHT_ID}) será destacado em todo o documento.\nDefinir como 0 desativa o highlight global.")
        self.highlight_id_action.triggered.connect(self.change_active_highlight_id) # Conecta ao novo handler
        self.highlight_id_action._base_icon_name = highlight_id_icon_base
        self.toolbar.addAction(self.highlight_id_action)
        self.actions_with_icons.append(self.highlight_id_action)
        highlight_id_button_widget = self.toolbar.widgetForAction(self.highlight_id_action)
        if highlight_id_button_widget:
            # Remove o estilo checked do CSS se existir (não é mais checkable)
            highlight_id_button_widget.setObjectName("highlightIdButton")
        # --- Fim Botão Highlight ID ---

        # --- Adicionar botão de Plugins na toolbar ---
        if hasattr(self, 'toolbar') and self.toolbar:
            self.plugins_action = QAction(self.get_themed_icon("plugin"), "Plugins", self)
            self.plugins_action.setToolTip("Gerenciar Plugins")
            self.plugins_action.triggered.connect(self.show_plugin_manager)
            self.toolbar.addSeparator()
            self.toolbar.addAction(self.plugins_action)
            self.plugins_action._base_icon_name = "plugin"
            self.actions_with_icons.append(self.plugins_action)
        # --- Fim botão de Plugins ---

    def create_status_bar(self):
        # ... (código inalterado) ...
        self.status_bar = QStatusBar(); self.setStatusBar(self.status_bar)
        self.ln_col_label = QLabel("Ln: 1, Col: 1"); self.ln_col_label.setToolTip("Linha e Coluna atuais"); self.status_bar.addPermanentWidget(self.ln_col_label)
        sep1 = QLabel("|"); self.status_bar.addPermanentWidget(sep1)
        self.chars_label = QLabel("Caracteres: 0"); self.chars_label.setToolTip("Contagem de caracteres"); self.status_bar.addPermanentWidget(self.chars_label); self.chars_label.hide()
        self.words_label = QLabel("Palavras: 0"); self.words_label.setToolTip("Contagem de palavras"); self.status_bar.addPermanentWidget(self.words_label); self.words_label.hide()
        self.lines_label = QLabel("Linhas: 0"); self.lines_label.setToolTip("Contagem de linhas"); self.status_bar.addPermanentWidget(self.lines_label); self.lines_label.hide()
        self.status_bar.showMessage("Pronto", 3000)


    # --- Tab Management ---
    def on_tab_renamed(self, index, new_name):
        """Handle tab renaming by the user. Also rename file on disk if needed."""
        editor = self.tab_widget.widget(index)
        if not editor:
            return
        # Store the custom title in editor's property
        editor.setProperty('custom_title', new_name)
        # Rename file on disk if it exists
        file_path = self.current_files.get(editor)
        if file_path and os.path.exists(file_path):
            dir_path = os.path.dirname(file_path)
            ext = os.path.splitext(file_path)[1]
            new_file_path = os.path.join(dir_path, new_name + ext)
            if new_file_path != file_path:
                try:
                    os.rename(file_path, new_file_path)
                    self.current_files[editor] = new_file_path
                except Exception as e:
                    QMessageBox.warning(self, "Erro ao renomear arquivo", f"Não foi possível renomear o arquivo:\n{e}")
        self.update_tab_title(editor, editor.document().isModified())
        # If this is a new file, update the window title
        if editor == self.current_editor:
            self.update_window_title()
        self.save_session()  # Salva sessão imediatamente ao renomear

    def get_next_temp_title(self):
        """Retorna o próximo título disponível do tipo 'Novo Arquivo (X)' sem repetir."""
        used_numbers = set()
        # Verifica abas abertas
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            custom_title = editor.property('custom_title')
            if custom_title and custom_title.startswith("Novo Arquivo ("):
                try:
                    num = int(custom_title.split("(")[-1].split(")")[0])
                    used_numbers.add(num)
                except Exception:
                    pass
        # Verifica arquivos temporários existentes
        for fname in os.listdir(UNSAVED_DIR):
            if fname.startswith("temp_") and fname.endswith(".nxt"):
                try:
                    num = int(fname.split("_")[-1].split(".")[0])
                    used_numbers.add(num)
                except Exception:
                    pass
        n = 1
        while n in used_numbers:
            n += 1
        return f"Novo Arquivo ({n})", n

    def new_tab(self, file_path=None, content_data=None):
        import json  # Garante que json está disponível
        self.hide_empty_state()
        editor = QTextEdit()
        editor.setFont(self.default_editor_font)
        editor.setTabStopDistance(editor.fontMetrics().horizontalAdvance(' ') * 4)
        palette = editor.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 0, 0, 0))
        palette.setColor(QPalette.ColorRole.HighlightedText, palette.color(QPalette.ColorRole.Text))
        editor.setPalette(palette)
        editor.setCurrentFont(self.default_editor_font)
        highlighter = IdHighlighter(editor.document(), self)
        highlighter.set_active_id(self.active_highlight_id)
        highlighter.set_cursor_id(self.current_cursor_id)
        highlighter.set_cursor_only(self.highlight_cursor_only)
        self.highlighters[editor] = highlighter
        editor.cursorPositionChanged.connect(self.update_cursor_state)
        QTimer.singleShot(0, highlighter.update_colors)
        editor.document().modificationChanged.connect(
            lambda modified, ed=editor: self.update_tab_title(ed, modified)
        )
        editor.selectionChanged.connect(self.handle_selection_changed)
        editor.cursorPositionChanged.connect(self.update_status)
        wrap_mode = QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere if self.default_word_wrap else QTextOption.WrapMode.NoWrap
        editor.setWordWrapMode(wrap_mode)
        read_mode_button = QToolButton()
        read_mode_button.setCheckable(True)
        read_mode_button.setIcon(self.get_themed_icon("read_mode"))
        read_mode_button.setToolTip("Ativar/Desativar Modo Leitura\nPermite visualizar o texto sem poder editá-lo")
        read_mode_button._base_icon_name = "read_mode"
        read_mode_button.clicked.connect(lambda: self.toggle_read_mode(editor))
        editor.setCornerWidget(read_mode_button)
        # --- Se não for arquivo externo, cria arquivo temporário em unsaved_files ---
        if not file_path and not content_data:
            temp_title, temp_num = self.get_next_temp_title()
            temp_path = os.path.join(UNSAVED_DIR, f"temp_{temp_num}.nxt")
            # Salva um arquivo NXT vazio para garantir compatibilidade
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump({"blocks": []}, f, ensure_ascii=False)
            self.current_files[editor] = temp_path
            editor.setProperty('custom_title', temp_title)
            self.update_tab_title(editor, False)
        else:
            self.current_files[editor] = file_path
        index = self.tab_widget.addTab(editor, editor.property('custom_title') or "Novo Arquivo")
        self.tab_widget.setCurrentIndex(index)
        if file_path and not content_data:
            self.load_file_into_editor(editor, file_path)
        elif content_data:
            import tempfile, json
            with tempfile.NamedTemporaryFile(delete=False, suffix='.nxt', mode='w', encoding='utf-8') as tmp:
                json.dump(content_data, tmp, ensure_ascii=False)
                tmp_path = tmp.name
            self.load_content(editor, tmp_path, format="nxt")
            os.unlink(tmp_path)
            if file_path:
                self.current_files[editor] = file_path
                editor.document().setModified(False)
                self.update_tab_title(editor, False)
        else:
            if not file_path and not content_data:
                # Já setou o título acima
                pass
            else:
                self.update_tab_title(editor, False)
        # --- Salva sessão ao criar nova aba ---
        self.save_session()

    def truncate_tab_title(self, title, max_length=16):
        """Truncates a tab title to max_length characters, adding ... if needed."""
        if len(title) <= max_length:
            return title
        return title[:max_length-3] + "..."

    def update_tab_title(self, editor, modified):
        index = self.tab_widget.indexOf(editor)
        if index == -1: 
            return
            
        # Check for custom title first
        custom_title = editor.property('custom_title')
        if custom_title:
            title = f"{custom_title}{'*' if modified else ''}"
            self.tab_widget.setTabText(index, self.truncate_tab_title(title))
            self.tab_widget.setTabToolTip(index, title)
            if editor == self.current_editor:
                self.update_window_title()
            return
            
        # Fall back to file-based title
        file_path = self.current_files.get(editor)
        base_name = os.path.basename(file_path) if file_path else "Novo Arquivo"
        if "." in base_name:
            base_name = base_name.split(".")[0]
            
        title = f"{base_name}{'*' if modified else ''}"
        self.tab_widget.setTabText(index, self.truncate_tab_title(title))
        self.tab_widget.setTabToolTip(index, file_path if file_path else title)
        if editor == self.current_editor:
            self.update_window_title()

    def update_window_title(self):
        if not self.current_editor:
            self.setWindowTitle(APP_NAME)
            return
            
        index = self.tab_widget.indexOf(self.current_editor)
        if index == -1:
            return
            
        tab_text = self.tab_widget.tabText(index)
        file_path = self.current_files.get(self.current_editor)
        
        if file_path:
            self.setWindowTitle(f"{tab_text} - {file_path} - {APP_NAME}")
        else:
            self.setWindowTitle(f"{tab_text} - {APP_NAME}")

    def save_to_app_dir(self):
        """Salva o conteúdo da aba atual no arquivo já existente, mantendo a extensão. Só cria novo se não houver path."""
        if not self.current_editor:
            return
        file_path = self.current_files.get(self.current_editor)
        if file_path and os.path.exists(file_path):
            # Salva no arquivo já existente, mantendo a extensão
            ext = os.path.splitext(file_path)[1].lower()
            fmt = "nxt" if ext == ".nxt" else "auto"
            self.save_content(self.current_editor, file_path, format=fmt)
            self.update_tab_title(self.current_editor, False)
            self.update_window_title()
        else:
            # Cria novo arquivo padrão
            self._save_to_app_dir_generic(extension=".txt", format_hint="auto")

    def save_nxt_to_app_dir(self):
        """Salva o conteúdo da aba atual, usando o caminho existente ou criando um novo arquivo .nxt, aplicando todas as regras de renomeação/título."""
        if not self.current_editor:
            return False
        
        current_index = self.tab_widget.currentIndex()
        tab_text = self.tab_widget.tabText(current_index).replace("*", "")
        
        # Generate a default name if needed
        if not tab_text or tab_text == "Novo Arquivo":
            tab_text = f"Documento_{uuid4().hex[:6]}"
        
        # Remove any existing extension
        if '.' in tab_text:
            tab_text = tab_text.rsplit('.', 1)[0]
        
        file_path = self.current_files.get(self.current_editor, "")
        original_path = file_path  # Save original path for comparison
        
        try:
            # If no file exists or path is invalid, create a new one
            if not file_path or not os.path.exists(file_path):
                file_path = os.path.join(BASE_PATH, f"{tab_text}.nxt")
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # If file exists but isn't .nxt, prepare to rename it
            elif not file_path.lower().endswith('.nxt'):
                file_path = os.path.splitext(file_path)[0] + ".nxt"
                # If target file exists and is different from source, remove it first
                if os.path.exists(file_path) and os.path.normpath(file_path) != os.path.normpath(original_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        QMessageBox.warning(self, "Erro", f"Não foi possível remover o arquivo existente: {e}")
                        return False
            
            # Save the content
            if self.save_content(self.current_editor, file_path, format="nxt"):
                # Update tab title and file mapping
                new_title = os.path.basename(file_path)
                if new_title.endswith('.nxt'):
                    new_title = new_title[:-4]
                
                self.tab_widget.setTabText(current_index, new_title)
                self.current_files[self.current_editor] = file_path
                self.update_tab_title(self.current_editor, False)
                self.update_window_title()
                return True
        
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Ocorreu um erro ao salvar o arquivo:\n{str(e)}")
            return False
        
        return False

    def _save_to_app_dir_generic(self, extension, format_hint):
        if not self.current_editor:
            return
        current_index = self.tab_widget.currentIndex()
        tab_text = self.tab_widget.tabText(current_index).replace("*", "")
        if not tab_text or tab_text == "Novo Arquivo":
            tab_text = f"Documento_{uuid4().hex[:6]}"
        # Remove qualquer extensão antiga
        if tab_text.endswith(".txt") or tab_text.endswith(".nxt"):
            tab_text = tab_text.rsplit(".", 1)[0]
        file_candidate = self.current_files.get(self.current_editor)
        # NOVO: se já existe arquivo salvo, salva no mesmo path e extensão
        if self.current_editor in self.current_files and file_candidate and isinstance(file_candidate, str) and os.path.exists(file_candidate):
            file_path = self.current_files[self.current_editor]
            # Mantém a extensão original
            ext = os.path.splitext(file_path)[1]
            if ext != extension:
                file_path = os.path.splitext(file_path)[0] + extension
                self.current_files[self.current_editor] = file_path
        else:
            file_path = os.path.join(BASE_PATH, f"{tab_text}{extension}")
            self.current_files[self.current_editor] = file_path
        # Salva o conteúdo
        self.save_content(self.current_editor, file_path, format=format_hint)
        # Atualiza título da aba
        new_title = os.path.basename(file_path)
        if new_title.endswith(extension):
            new_title = new_title[: -len(extension)]
        self.tab_widget.setTabText(current_index, new_title)
        self.current_files[self.current_editor] = file_path
        self.update_tab_title(self.current_editor, False)
        QMessageBox.information(self, "Salvo", f"Arquivo salvo em: {file_path}")
        self.update_window_title()

    def update_current_editor(self, index):
        # ... (modificado para atualizar estado do cursor na troca de aba) ...
        new_editor = None
        if index >= 0 and index < self.tab_widget.count():
            widget = self.tab_widget.widget(index)
            if isinstance(widget, QTextEdit): new_editor = widget
        if new_editor != self.current_editor:
            old_editor = self.current_editor
            self.current_editor = new_editor
            
            # Ao trocar de aba, força a atualização do estado do cursor (ID, Ln/Col etc)
            if self.current_editor:
                self.current_editor.setFocus()
                self.update_cursor_state()
                # Connect search bar to new editor if search is active
                if hasattr(self, 'search_bar_widget') and self.search_bar_widget.search_active:
                    self.search_bar_widget.connect_to_editor(self.current_editor)
                    self.search_bar_widget.update_button_state(self.search_bar_widget.search_input.text())
            else:
                # Se não houver editor ativo, reseta o ID do cursor
                self.current_cursor_id = 0
                # Atualiza status bar para estado vazio
                self.update_status()
                if hasattr(self, 'search_bar_widget'):
                    self.search_bar_widget.update_button_state("")

            self.update_window_title()
            if self.format_popup.isVisible() and getattr(self, 'format_popup_mode', 'selection') != 'statusbar':
                # Check if selection is active for popup mode
                if self.current_editor and self.current_editor.textCursor().hasSelection():
                    self.show_format_popup()
                else:
                    self.format_popup.hide()

            # Atualiza o estado do botão de modo leitura
            corner_widget = self.tab_widget.cornerWidget()
            if corner_widget:
                layout = corner_widget.layout()
                if layout:
                    read_mode_button = layout.itemAt(0).widget()
                    if read_mode_button:
                        # Get read mode state from current editor if it exists, otherwise default to False
                        is_read_mode = False
                        if self.current_editor:
                            is_read_mode = self.read_mode_states.get(self.current_editor, False)
                        read_mode_button.setChecked(is_read_mode)
                        # Only setReadOnly if we have a valid editor
                        if self.current_editor:
                            self.current_editor.setReadOnly(is_read_mode)

    # --- Formatting Popup ---
    # ... (código inalterado) ...
    def handle_selection_changed(self):
     sender_editor = self.sender()
     if sender_editor and sender_editor == self.current_editor:
        cursor = sender_editor.textCursor()
        mode = getattr(self, 'format_popup_mode', 'selection')
        if mode == 'selection':
            if cursor.hasSelection() and not self.shift_pressed:
                self.popup_timer.start(350)
            else:
                self.popup_timer.stop()
                self.format_popup.hide()
        else:
            self.popup_timer.stop()
            self.format_popup.hide()

    def show_format_popup(self):
        mode = getattr(self, 'format_popup_mode', 'selection')
        if mode == "statusbar":
            self.show_format_popup_statusbar()
            return
        if mode == "selection":
            if self.shift_pressed or not self.current_editor or not self.current_editor.textCursor().hasSelection():
                self.format_popup.hide()
                return
            cursor = self.current_editor.textCursor()
            if cursor.hasSelection():
                rect = self.current_editor.cursorRect(cursor)
                global_pos = self.current_editor.mapToGlobal(rect.bottomLeft())
                global_pos.setY(global_pos.y() + 3)
                self.format_popup.setWindowFlags(Qt.WindowType.Popup)
                self.format_popup.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
                self.format_popup.setLineWidth(1)
                self.format_popup.show_at(global_pos, self.current_editor)
            else:
                self.format_popup.hide()
        elif mode == "selection_click":
            self.format_popup.hide()

    def eventFilter(self, obj, event):
        # ...existing code...
        if event.type() == QEvent.Type.MouseButtonPress:
            if getattr(self, 'format_popup_mode', 'selection') == "selection_click":
                if event.button() == Qt.MouseButton.RightButton and self.current_editor and self.current_editor.textCursor().hasSelection():
                    cursor = self.current_editor.textCursor()
                    rect = self.current_editor.cursorRect(cursor)
                    global_pos = self.current_editor.mapToGlobal(rect.bottomLeft())
                    global_pos.setY(global_pos.y() + 3)
                    self.format_popup.setWindowFlags(Qt.WindowType.Popup)
                    self.format_popup.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
                    self.format_popup.setLineWidth(1)
                    self.format_popup.show_at(global_pos, self.current_editor)
                    self.format_popup.show()
                    return True
                else:
                    self.format_popup.hide()
            # ...existing code...
        return super().eventFilter(obj, event)

    def show_format_popup_statusbar(self):
        if not self.current_editor:
            return
        sb_rect = self.status_bar.rect()
        sb_top_left = self.status_bar.mapToGlobal(sb_rect.topLeft())
        sb_width = sb_rect.width()
        popup_width = self.format_popup.width() if self.format_popup.width() > 0 else 300
        x = sb_top_left.x() + (sb_width - popup_width) // 2
        y = sb_top_left.y() - self.format_popup.height() - 2
        self.format_popup.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self.format_popup.setMinimumSize(300, 40)
        self.format_popup.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Plain)
        self.format_popup.setLineWidth(0)
        self.format_popup.show_at(QPoint(int(x), int(y)), self.current_editor)
        self.format_popup.show()

    # --- Status Bar Update ---
    # ... (código inalterado) ...
    def toggle_read_mode(self, editor):
        """Altera o estado de modo leitura para o editor especificado."""
        is_read_mode = not self.read_mode_states.get(editor, False)
        self.read_mode_states[editor] = is_read_mode
        
        # Atualiza a interface do editor
        editor.setReadOnly(is_read_mode)
        
        # Atualiza o estado do botão de modo leitura
        if hasattr(self, 'read_mode_btn'):
            self.read_mode_btn.setChecked(is_read_mode)

    def update_status(self):
        # Chamado por update_cursor_state ou quando não há editor
        if self.current_editor:
            cursor = self.current_editor.textCursor(); line = cursor.blockNumber() + 1; col = cursor.columnNumber() + 1
            self.ln_col_label.setText(f"Ln: {line}, Col: {col}")
            # Atualiza contadores apenas se visíveis e texto mudou (otimização possível)
            if self.show_char_count_action.isChecked() or self.show_word_count_action.isChecked() or self.show_line_count_action.isChecked():
                text = self.current_editor.toPlainText()
                if self.show_char_count_action.isChecked(): self.chars_label.setText(f"Caracteres: {len(text)}")
                if self.show_word_count_action.isChecked(): words = len(text.split()) if text else 0; self.words_label.setText(f"Palavras: {words}")
                if self.show_line_count_action.isChecked(): lines = self.current_editor.document().lineCount(); self.lines_label.setText(f"Linhas: {lines}")
            # Mostra ID sob o cursor (ou 0) - pode ser útil para debug
            # self.status_bar.showMessage(f"Cursor ID: {self.current_cursor_id}", 1000)
        else:
            self.ln_col_label.setText("Ln: -, Col: -"); self.chars_label.setText("Caracteres: -")
            self.words_label.setText("Palavras: -"); self.lines_label.setText("Linhas: -")
            # self.status_bar.showMessage("", 0)

    # --- File Operations ---
    def open_file(self, nxt_only=False):
        reuse = False
        if self.current_editor and not self.current_files.get(self.current_editor) and not self.current_editor.document().isModified() and not self.current_editor.toPlainText():
            reuse = True
        last_dir = self.settings.value(SETTING_LAST_OPEN_DIR, QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation))
        name = "Sem Título"

        # Define filtros
        if nxt_only:
            filters = "Ninthpads Text File (*.nxt);;Todos os Arquivos (*)"
        else:
            filters = "Ninthpads Text File (*.nxt);;Arquivos de Texto (*.txt);;Arquivos RTF (*.rtf);;Arquivos HTML (*.html);;Todos os Arquivos (*)"

        default_suffix = ".txt" # Default para texto simples se nenhum outro for escolhido
        # Adiciona .nxt se o nome atual já for .nxt, senão deixa sem extensão para o diálogo adicionar
        if path and path.lower().endswith(".nxt"):
            base_name = name[:-4] # Remove .nxt do nome base
            title_suffix = ".nxt"
            default_suffix = ".nxt"
        elif not "." in name: # Adiciona .txt se usuário não digitou extensão
            name += default_suffix

        # Corrige filtro inicial para garantir que ele exista nos filtros
        initial_filter = "Ninthpads Text File (*.nxt)" if default_suffix == ".nxt" else "Arquivos de Texto (*.txt)"
        if initial_filter not in filters:
            initial_filter = filters.split(';;')[0]
        file_name, sel_filter = QFileDialog.getOpenFileName(self, "Abrir Arquivo", os.path.join(last_dir, name), filters, initialFilter=initial_filter)

        if file_name:
            self.settings.setValue(SETTING_LAST_OPEN_DIR, os.path.dirname(file_name))
            fmt = "plaintext"; low = file_name.lower()

            # Determina o formato baseado no filtro ou extensão
            if sel_filter == "Ninthpads Text File (*.nxt)" or low.endswith(".nxt"):
                fmt = "nxt"; file_name += ".nxt" if not low.endswith(".nxt") else ""
            elif sel_filter == "Arquivos RTF (*.rtf)" or low.endswith(".rtf"):
                fmt = "rtf"; file_name += ".rtf" if not low.endswith(".rtf") else ""
            elif sel_filter == "Arquivos HTML (*.html)" or low.endswith(".html"):
                fmt = "html"; file_name += ".html" if not low.endswith(".html") else ""
            elif not low.endswith(".txt") and "." not in os.path.basename(file_name) and (sel_filter == "Arquivos de Texto (*.txt)" or sel_filter.startswith("Todos")):
                fmt = "plaintext"; file_name += ".txt"

            # Corrige: abrir arquivo, não salvar!
            try:
                if fmt == "nxt":
                    self.load_content(self.current_editor, file_name, format="nxt")
                else:
                    self.load_content(self.current_editor, file_name, format="plaintext")
                self.current_files[self.current_editor] = file_name
                self.update_tab_title(self.current_editor, False)
                return True
            except Exception as e:
                QMessageBox.warning(self, "Erro ao abrir arquivo", f"Erro ao abrir arquivo: {e}")
                return False
        return False


    def save_as_file(self, nxt_only=False):
        if not self.current_editor: return False
        path = self.current_files.get(self.current_editor)
        name = os.path.basename(path) if path else self.tab_widget.tabText(self.tab_widget.currentIndex()).replace("*", "")
        if not name or name == "Novo Arquivo": name = "Sem Título"
        start = os.path.dirname(path) if path else self.settings.value(SETTING_LAST_SAVE_DIR, QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation))
        # Define filtros e nome padrão
        filters = "Ninthpads Text File (*.nxt);;Arquivos de Texto (*.txt);;Arquivos RTF (*.rtf);;Arquivos HTML (*.html);;Todos os Arquivos (*)"
        if nxt_only:
            filters = "Ninthpads Text File (*.nxt)"
            default_suffix = ".nxt"
            if not name.lower().endswith(".nxt"): name += default_suffix
        else:
            default_suffix = ".txt"
            if not any(name.lower().endswith(ext) for ext in [".nxt", ".txt", ".rtf", ".html"]):
                name += default_suffix
        initial_filter = "Ninthpads Text File (*.nxt)" if nxt_only else "Arquivos de Texto (*.txt)"
        file_name, sel_filter = QFileDialog.getSaveFileName(self, "Salvar Como", os.path.join(start, name), filters, initialFilter=initial_filter)
        if file_name:
            self.settings.setValue(SETTING_LAST_SAVE_DIR, os.path.dirname(file_name))
            # Decide formato e extensão baseado no filtro selecionado
            fmt = "auto"
            if sel_filter == "Ninthpads Text File (*.nxt)":
                if not file_name.lower().endswith('.nxt'):
                    file_name += '.nxt'
                fmt = "nxt"
            elif sel_filter == "Arquivos de Texto (*.txt)":
                if not file_name.lower().endswith('.txt'):
                    file_name += '.txt'
                fmt = "auto"
            elif sel_filter == "Arquivos RTF (*.rtf)":
                if not file_name.lower().endswith('.rtf'):
                    file_name += '.rtf'
                fmt = "rtf"
            elif sel_filter == "Arquivos HTML (*.html)":
                if not file_name.lower().endswith('.html'):
                    file_name += '.html'
                fmt = "html"
            else:
                # fallback: tenta deduzir pela extensão
                if file_name.lower().endswith('.nxt'):
                    fmt = "nxt"
                elif file_name.lower().endswith('.rtf'):
                    fmt = "rtf"
                elif file_name.lower().endswith('.html'):
                    fmt = "html"
                else:
                    fmt = "auto"
            # --- Salva no formato correto ---
            old_path = self.current_files.get(self.current_editor)
            was_temp = False
            
            # Verifica se era um arquivo temporário
            if old_path and os.path.exists(old_path):
                try:
                    was_temp = os.path.abspath(old_path).startswith(os.path.abspath(UNSAVED_DIR))
                except Exception:
                    was_temp = False
            
            # Garante que o diretório de destino existe
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            
            # Salva no formato apropriado
            if fmt == "nxt":
                result = self.save_content(self.current_editor, file_name, format="nxt")
            elif fmt == "rtf":
                result = self.save_content(self.current_editor, file_name, format="rtf")
            elif fmt == "html":
                result = self.save_content(self.current_editor, file_name, format="html")
            else:
                result = self.save_content(self.current_editor, file_name, format="auto")
                
            if result:
                # Remove o arquivo temporário se existir e for diferente do novo
                if was_temp and old_path and os.path.exists(old_path) and os.path.abspath(old_path) != os.path.abspath(file_name):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        print(f"Warning: Could not remove temporary file {old_path}: {e}")
                self.current_files[self.current_editor] = file_name
                # Atualiza o título da aba para o nome do arquivo externo salvo (sem extensão)
                base_title = os.path.splitext(os.path.basename(file_name))[0]
                self.current_editor.setProperty('custom_title', base_title)
                self.update_tab_title(self.current_editor, False)
                self.save_session()
                return True
            else:
                return False
        return False

    def save_file(self):
        """Salva o arquivo atual. Se o arquivo já existe, salva no formato atual (.nxt se for .nxt, senão formato padrão).
        Se o arquivo não existe, chama save_as_file() para pedir o nome do arquivo."""
        if not self.current_editor:
            return False
        
        path = self.current_files.get(self.current_editor)
        if path:
            # Se o path atual é .nxt, salva como .nxt, senão salva formato padrão
            if path.lower().endswith(".nxt"):
                return self.save_content(self.current_editor, path, format="nxt")
            else:
                return self.save_content(self.current_editor, path)  # Usa formato auto (baseado na extensão)
        else:
            return self.save_as_file()  # Pergunta o formato


    def save_content(self, editor, file_name, format="auto"):
        """Salva o conteúdo do editor em um arquivo no formato especificado.
        
        Args:
            editor: O widget QTextEdit contendo o conteúdo a ser salvo
            file_name: Caminho do arquivo de destino
            format: Formato do arquivo ("nxt", "rtf", "html" ou "auto" para texto puro)
            
        Returns:
            bool: True se o salvamento for bem-sucedido, False caso contrário
        """
        if not editor or not file_name:
            QMessageBox.warning(self, "Erro", "Editor ou nome de arquivo inválido")
            return False
        
        # Limita o número de blocos para evitar travamentos com arquivos muito grandes ao salvar NXT
        if format == "nxt" or (format == "auto" and file_name.lower().endswith('.nxt')):
            max_blocks = 10000
            try:
                total_blocks = editor.document().blockCount()
                if total_blocks > max_blocks:
                    reply = QMessageBox.question(
                        self,
                        "Arquivo Grande",
                        f"Este arquivo é muito grande ({total_blocks} blocos). "
                        f"Deseja continuar salvando? Pode levar algum tempo e consumir muita memória.",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return False
            except Exception as e:
                print(f"[WARNING] Erro ao verificar contagem de blocos: {e}")
                # Continua salvando mesmo com erro na contagem


        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_name)), exist_ok=True)
            
            # Determine format from extension if auto
            if format == "auto":
                if file_name.lower().endswith('.nxt'):
                    format = "nxt"
                elif file_name.lower().endswith('.rtf'):
                    format = "rtf"
                elif file_name.lower().endswith(('.htm', '.html')):
                    format = "html"
                else:
                    format = "txt"
            
            # Save based on format
            if format == "nxt":
                return self._save_nxt_format(editor, file_name)
            elif format == "rtf":
                return self._save_rtf_format(editor, file_name)
            elif format == "html":
                return self._save_html_format(editor, file_name)
            else:
                return self._save_plain_text(editor, file_name)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Ocorreu um erro ao salvar o arquivo:\n{str(e)}")
            return False

    def _save_nxt_format(self, editor, file_name):
        """Salva o conteúdo no formato NXT personalizado."""
        print(f"[DEBUG - NXT SAVE] Iniciando salvamento para: {file_name}")
        try:
            doc = editor.document()
            if not doc:
                 print("[DEBUG - NXT SAVE] Erro: Documento do editor inválido.")
                 raise ValueError("Documento do editor inválido")

            blocks = []

            # Process each block
            block = doc.begin()
            block_number = 0
            while block.isValid():
                print(f"[DEBUG - NXT SAVE] Processando Bloco #{block_number}")

                # Obter formato do bloco
                block_format = block.blockFormat()

                # Iterar sobre os fragmentos de formatação dentro do bloco
                fragment_list = []
                fragment_iterator = block.begin()
                fragment_index = 0
                # CORREÇÃO: Usar atEnd() e iterar com +=
                while not fragment_iterator.atEnd():
                    fragment = fragment_iterator.fragment()
                    if fragment.isValid():
                        print(f"[DEBUG - NXT SAVE] Processando Fragmento #{fragment_index} no Bloco #{block_number}")
                        print(f"[DEBUG - NXT SAVE] Fragment Text: '{fragment.text()}'")

                        char_format = fragment.charFormat()

                        # Acessar o objeto QColor do QBrush antes de chamar isValid()
                        text_color = None
                        fg_brush = char_format.foreground()
                        if fg_brush and fg_brush.style() != Qt.BrushStyle.NoBrush:
                            color_obj = fg_brush.color()
                            # CORREÇÃO AQUI: Acessar o QColor antes de isValid
                            if color_obj.isValid() and color_obj != editor.palette().color(QPalette.ColorRole.Text):
                                text_color = color_obj.name()
                                print(f"[DEBUG - NXT SAVE] Fragment Text Color: {text_color}")
                            elif not color_obj.isValid():
                                print(f"[DEBUG - NXT SAVE] Fragment Text Color (Invalid): {fg_brush.color().name()}")
                            else:
                                print(f"[DEBUG - NXT SAVE] Fragment Text Color (Default): {color_obj.name()}")

                        background_color = None
                        # --- DEBUG ADICIONAL AQUI ---
                        bg_brush = char_format.background()
                        print(f"[DEBUG - NXT SAVE] Background Brush obtido.") # Debug 1
                        if bg_brush:
                             print(f"[DEBUG - NXT SAVE] Background Brush is not None. Style: {bg_brush.style()}") # Debug 2
                             if bg_brush.style() != Qt.BrushStyle.NoBrush:
                                  print(f"[DEBUG - NXT SAVE] Background Brush style is not NoBrush.") # Debug 3
                                  bgcolor_obj = bg_brush.color()
                                  print(f"[DEBUG - NXT SAVE] Background Color Object obtido.") # Debug 4
                                  if bgcolor_obj.isValid():
                                      background_color = bgcolor_obj.name()
                                      print(f"[DEBUG - NXT SAVE] Fragment Background Color: {background_color}")
                                  elif not bgcolor_obj.isValid():
                                      print(f"[DEBUG - NXT SAVE] Fragment Background Color (Invalid): {bgcolor_obj.name()}")
                             else:
                                print(f"[DEBUG - NXT SAVE] Background Brush style IS NoBrush.") # Debug 3b
                        else:
                             print(f"[DEBUG - NXT SAVE] Background Brush IS None.") # Debug 2b
                        # --- FIM DEBUG ADICIONAL ---


                        # Capturar outras propriedades
                        print(f"[DEBUG - NXT SAVE] Capturando propriedade: bold")
                        bold = char_format.fontWeight() > QFont.Weight.Normal
                        print(f"[DEBUG - NXT SAVE] Capturando propriedade: italic")
                        italic = char_format.fontItalic()
                        print(f"[DEBUG - NXT SAVE] Capturando propriedade: underline")
                        underline = char_format.fontUnderline()
                        # CORREÇÃO: Verifica se fontStrikeOut existe antes de usar
                        print(f"[DEBUG - NXT SAVE] Capturando propriedade: strikethrough")
                        strikethrough = char_format.fontStrikeOut() if hasattr(char_format, 'fontStrikeOut') else False

                        print(f"[DEBUG - NXT SAVE] Capturando propriedade: font_family")
                        # Obtém a família da fonte diretamente do formato do caractere.
                        current_font_family = char_format.fontFamily()

                        # Decide se deve salvar a família da fonte.
                        # Salva apenas se for uma string não vazia E for diferente da fonte padrão do editor.
                        font_family_to_save = current_font_family if current_font_family and current_font_family.strip() and current_font_family != self.default_editor_font.family() else None

                        print(f"[DEBUG - NXT SAVE] Capturando propriedade: font_size")
                        font_size = char_format.fontPointSize() if char_format.fontPointSize() > 0 and char_format.fontPointSize() != self.default_editor_font.pointSize() else None

                        print(f"[DEBUG - NXT SAVE] Todas as propriedades capturadas.")

                        fragment_data = {
                            "text": fragment.text(),
                            "format": {
                                "bold": bold,
                                "italic": italic,
                                "underline": underline,
                                "strikethrough": strikethrough,
                                # Removido: "font_family": font_family,
                                "font_size": font_size,
                                "text_color": text_color,
                                "background_color": background_color
                            }
                        }

                        # Adicionar font_family ao dicionário format apenas se font_family_to_save não for None
                        if font_family_to_save:
                             fragment_data["format"]["font_family"] = font_family_to_save
                             print(f"[DEBUG - NXT SAVE] Fragment Font Family to Save: {font_family_to_save}")
                        else:
                             print(f"[DEBUG - NXT SAVE] Fragment Font Family to Save: None (Default)")

                        # Adicionar ID se existir (propriedade USER_ID_PROPERTY)
                        if char_format.hasProperty(USER_ID_PROPERTY):
                             fragment_data["format"]["id"] = char_format.property(USER_ID_PROPERTY)
                             print(f"[DEBUG - NXT SAVE] Fragment ID: {fragment_data['format']['id']}")
                            
                        # Adicionar neutral_color se definido (propriedade UserProperty + 100)
                        if char_format.hasProperty(QTextFormat.UserProperty + 100):
                             fragment_data["format"]["neutral_color"] = bool(char_format.property(QTextFormat.UserProperty + 100))
                             print(f"[DEBUG - NXT SAVE] Fragment Neutral Color: {fragment_data['format']['neutral_color']}")

                        fragment_list.append(fragment_data)
                        print(f"[DEBUG - NXT SAVE] Fragment data collected: {fragment_data}")

                    fragment_iterator += 1
                    fragment_index += 1

                block_data = {
                    "fragments": fragment_list,
                    "block_format": {
                         "alignment": int(block_format.alignment()),
                         "top_margin": block_format.topMargin(),
                         "bottom_margin": block_format.bottomMargin(),
                         "left_margin": block_format.leftMargin(),
                         "right_margin": block_format.rightMargin(),
                         "indent": block_format.indent(),
                         "line_height": block_format.lineHeight(),
                         "line_height_type": int(block_format.lineHeightType())
                    }
                }
                print(f"[DEBUG - NXT SAVE] Block format collected: {block_data['block_format']}")

                blocks.append(block_data)
                print(f"[DEBUG - NXT SAVE] Bloco #{block_number} processado com {len(fragment_list)} fragmentos.")

                block = block.next()
                block_number += 1
            
            print(f"[DEBUG - NXT SAVE] Total de blocos processados: {len(blocks)}")
            temp_file = f"{file_name}.tmp"
            print(f"[DEBUG - NXT SAVE] Salvando dados em arquivo temporário: {temp_file}")

            with open(temp_file, 'w', encoding='utf-8') as f:
                json_data = {
                    "format_version": "1.1",
                    "created": datetime.now().isoformat(),
                    "blocks": blocks
                }
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            print(f"[DEBUG - NXT SAVE] Arquivo temporário criado com sucesso. Substituindo original.")
            if os.path.exists(file_name):
                os.remove(file_name)
            os.rename(temp_file, file_name)
            
            editor.document().setModified(False)
            self.status_bar.showMessage(f"Arquivo NXT salvo: {os.path.basename(file_name)}", 5000)
            print(f"[DEBUG - NXT SAVE] Salvamento NXT concluído com sucesso para: {file_name}")

            return True
            
        except Exception as e:
            print(f"[DEBUG - NXT SAVE] Erro durante o salvamento: {str(e)}")
            if 'temp_file' in locals() and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"[DEBUG - NXT SAVE] Arquivo temporário removido: {temp_file}")
                except Exception as remove_error:
                    print(f"[DEBUG - NXT SAVE] Falha ao remover arquivo temporário {temp_file}: {remove_error}")
            return False

    def _save_rtf_format(self, editor, file_name):
        """Salva o conteúdo em formato RTF."""
        try:
            # Tenta obter o RTF do editor
            text = editor.toPlainText()
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(text)  # Implementação básica - considere usar um conversor RTF real
            
            editor.document().setModified(False)
            self.status_bar.showMessage(f"Arquivo RTF salvo: {os.path.basename(file_name)}", 5000)
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao salvar RTF: {str(e)}")
    
    def _save_html_format(self, editor, file_name):
        """Salva o conteúdo em formato HTML."""
        try:
            html = editor.toHtml()
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(html)
            
            editor.document().setModified(False)
            self.status_bar.showMessage(f"Arquivo HTML salvo: {os.path.basename(file_name)}", 5000)
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao salvar HTML: {str(e)}")
    
    def _save_plain_text(self, editor, file_name):
        """Salva o conteúdo em formato de texto puro."""
        try:
            content = editor.toPlainText()
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(content)
            
            editor.document().setModified(False)
            self.status_bar.showMessage(f"Arquivo salvo: {os.path.basename(file_name)}", 5000)
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao salvar texto puro: {str(e)}")

    def load_content(self, editor, file_name, format="auto"):
        """Loads content into the editor from a file in the specified format.
        
        Args:
            editor: The QTextEdit widget to load content into
            file_name: Path to the file to load
            format: File format ("nxt", "rtf", "html", or "auto" for plain text)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not editor or not file_name:
            self.status_bar.showMessage("Erro: Editor ou nome de arquivo inválido", 5000)
            return False

        # Verifica se o arquivo existe e é legível
        if not os.path.exists(file_name):
            QMessageBox.warning(self, "Erro", f"Arquivo não encontrado: {file_name}")
            return False
            
        if not os.access(file_name, os.R_OK):
            QMessageBox.warning(self, "Erro", f"Sem permissão para ler o arquivo: {file_name}")
            return False

        try:
            # Se for formato NXT, carrega com formatação especial
            if format == "nxt" or (format == "auto" and file_name.lower().endswith('.nxt')):
                print(f"[DEBUG - NXT LOAD] Tentando carregar arquivo NXT: {file_name}")
                try:
                    with open(file_name, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    print(f"[DEBUG - NXT LOAD] Arquivo JSON lido com sucesso.")
                    
                    # Verifica se o arquivo tem o formato esperado
                    if not isinstance(data, dict) or "blocks" not in data:
                        print(f"[DEBUG - NXT LOAD] Formato NXT inválido. Data: {data}")
                        raise ValueError("Formato de arquivo NXT inválido")
                        
                    editor.clear()
                    cursor = editor.textCursor()
                    doc = editor.document()
                    default_font = self.default_editor_font
                    # Cor padrão do texto do editor para fallback
                    default_color = editor.palette().color(QPalette.ColorRole.Text)
                    
                    blocks_data = data.get("blocks", [])
                    total_blocks_to_load = len(blocks_data)
                    print(f"[DEBUG - NXT LOAD] Encontrados {total_blocks_to_load} blocos para carregar.")

                    # Processa cada bloco de texto formatado
                    for block_index, block_data in enumerate(blocks_data):
                        print(f"[DEBUG - NXT LOAD] Processando Bloco #{block_index + 1}/{total_blocks_to_load}")
                        
                        if not isinstance(block_data, dict):
                            print(f"[DEBUG - NXT LOAD] Ignorando item de bloco inválido no índice {block_index}: {block_data}")
                            continue
                            
                        # Aplicar formatação de bloco (BlockFormat) antes de processar os fragmentos
                        block_format_dict = block_data.get("block_format", {})
                        current_block_format = QTextBlockFormat()
                        try:
                            # Verifica se é o primeiro bloco e NÃO é vazio antes de inserir um novo
                            # Isso evita uma linha extra no início
                            if block_index > 0:
                                # Se não for o primeiro bloco, insere um novo bloco ANTES de adicionar o conteúdo
                                # Isso garante que cada conjunto de fragmentos vá para um novo bloco
                                cursor.insertBlock()
                                # Atualiza o cursor para o novo bloco (o que acabamos de inserir)
                                # e aplica a formatação de bloco a ele.
                                # Não precisamos mais mover para o PreviousBlock e depois EndOfBlock
                                # Apenas inserir o bloco e aplicar o formato já posiciona o cursor corretamente
                                # no início do novo bloco.
                                # cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock) # REMOVIDO
                                # cursor.setBlockFormat(QTextBlockFormat()) # REMOVIDO - setBlockFormat abaixo fará isso
                                # cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock) # REMOVIDO

                                pass # A inserção de bloco já ocorreu

                            current_block_format.setAlignment(Qt.AlignmentFlag(block_format_dict.get("alignment", 1)))
                            current_block_format.setTopMargin(block_format_dict.get("top_margin", 0.0))
                            current_block_format.setBottomMargin(block_format_dict.get("bottom_margin", 0.0))
                            current_block_format.setLeftMargin(block_format_dict.get("left_margin", 0.0))
                            current_block_format.setRightMargin(block_format_dict.get("right_margin", 0.0))
                            current_block_format.setIndent(block_format_dict.get("indent", 0))
                            # Ignorar line_height por enquanto se for zero ou inválido para evitar problemas
                            line_height = block_format_dict.get("line_height", 0.0)
                            line_height_type = block_format_dict.get("line_height_type", 0)
                            # Aplicar line height apenas se for válido e não zero (para evitar divisão por zero ou erros)
                            if line_height > 0 and line_height_type in [0, 1, 2, 3]: # 0: Qt.TextLineHeight, 1: Qt.ProportionalHeight, 2: Qt.MinimumHeight, 3: Qt.FixedHeight
                                current_block_format.setLineHeight(line_height, QTextBlockFormat.LineHeightTypes(line_height_type))

                            # Aplica o formato do bloco ao bloco atual (que pode ser o primeiro ou um recém-inserido)
                            # Isso deve ser feito APÓS a inserção do bloco (se não for o primeiro)
                            # ou no início do primeiro bloco (se for o primeiro).
                            # Como insertBlock já cria e move para o novo bloco, e no primeiro bloco o cursor já está lá,
                            # setBlockFormat no cursor atual funciona.
                            cursor.setBlockFormat(current_block_format)
                            print(f"[DEBUG - NXT LOAD] Block format applied to current block: {block_format_dict}")

                        except Exception as e:
                            print(f"[DEBUG - NXT LOAD] Erro ao aplicar formato de bloco para {block_data}: {e}")
                            # Opcional: resetar para formato padrão em caso de erro grave
                            cursor.setBlockFormat(QTextBlockFormat())

                        # Processa cada fragmento dentro do bloco
                        fragments_list = block_data.get("fragments", [])
                        fragment_count = len(fragments_list)
                        print(f"[DEBUG - NXT LOAD] Bloco #{block_index + 1} tem {fragment_count} fragmentos.")

                        # Se há fragmentos, itera sobre eles e insere o texto com a formatação
                        if fragments_list:
                            for fragment_index, fragment_data in enumerate(fragments_list):
                                print(f"[DEBUG - NXT LOAD] Processando Fragmento #{fragment_index + 1}/{fragment_count} no Bloco #{block_index + 1}")

                                if not isinstance(fragment_data, dict):
                                    print(f"[DEBUG - NXT LOAD] Ignorando item de fragmento inválido no índice {fragment_index}: {fragment_data}")
                                    continue

                                text = fragment_data.get("text", "")
                                format_dict = fragment_data.get("format", {})

                                # Configura a formatação do texto (CharFormat) para este fragmento
                                char_format = QTextCharFormat()

                                # --- Aplicar propriedades do fragmento --- #

                                # Tratamento de cor do texto
                                try:
                                    text_color_hex = format_dict.get("text_color")
                                    neutral_color = format_dict.get("neutral_color", False)

                                    if neutral_color or not text_color_hex:
                                        char_format.clearForeground()
                                        print(f"[DEBUG - NXT LOAD] Fragment Text Color: Default (clear) for fragment: '{text}'")
                                    elif text_color_hex:
                                        color_obj = QColor(text_color_hex)
                                        if color_obj.isValid():
                                            char_format.setForeground(color_obj)
                                            print(f"[DEBUG - NXT LOAD] Fragment Text Color Applied: {text_color_hex} for fragment: '{text}'")
                                        else:
                                            print(f"[DEBUG - NXT LOAD] Fragment Text Color Invalid: {text_color_hex} for fragment: '{text}'")
                                            char_format.setForeground(default_color) # Usa cor padrão em caso de cor inválida

                                except Exception as e:
                                    print(f"[DEBUG - NXT LOAD] Erro ao processar cor do texto do fragmento '{text}': {e}")
                                    char_format.setForeground(default_color) # Fallback para cor padrão

                                # Tratamento de cor de fundo
                                try:
                                    bg_color_hex = format_dict.get("background_color")
                                    if bg_color_hex:
                                        bgcolor_obj = QColor(bg_color_hex)
                                        if bgcolor_obj.isValid():
                                            char_format.setBackground(bgcolor_obj)
                                            print(f"[DEBUG - NXT LOAD] Fragment Background Color Applied: {bg_color_hex} for fragment: '{text}'")
                                        else:
                                            print(f"[DEBUG - NXT LOAD] Fragment Background Color Invalid: {bg_color_hex} for fragment: '{text}'")
                                            char_format.clearBackground() # Usa sem cor de fundo em caso de cor inválida
                                    else: # Se bg_color_hex é None ou vazio
                                        char_format.clearBackground()
                                        print(f"[DEBUG - NXT LOAD] Fragment Background Color: Default (clear) for fragment: '{text}'")
                                except Exception as e:
                                    print(f"[DEBUG - NXT LOAD] Erro ao processar cor de fundo do fragmento '{text}': {e}")
                                    char_format.clearBackground() # Fallback para sem cor de fundo

                                # Aplicar estilos de fonte (negrito, itálico, sublinhado, tachado)
                                try:
                                    char_format.setFontWeight(QFont.Weight.Bold if format_dict.get("bold") else QFont.Weight.Normal)
                                    char_format.setFontItalic(format_dict.get("italic", False))
                                    char_format.setFontUnderline(format_dict.get("underline", False))
                                    char_format.setFontStrikeOut(format_dict.get("strikethrough", False))
                                    print(f"[DEBUG - NXT LOAD] Font styles applied for fragment '{text}': Bold={format_dict.get('bold')}, Italic={format_dict.get('italic')}, Underline={format_dict.get('underline')}, Strikethrough={format_dict.get('strikethrough')}")
                                except Exception as e:
                                    print(f"[DEBUG - NXT LOAD] Erro ao aplicar estilos de fonte do fragmento '{text}': {e}")

                                # Configura a fonte personalizada (família e tamanho)
                                try:
                                    font_family_name = format_dict.get("font_family")
                                    font_size_val = format_dict.get("font_size")

                                    # **Correção:** Use a fonte padrão do editor se a família da fonte não estiver especificada ou for igual à padrão
                                    # CORREÇÃO: Se a família da fonte existe no arquivo (não é None/vazio), APLICA ela, mesmo que seja igual à padrão atual.
                                    # Use a fonte padrão do editor SOMENTE se não houver font_family especificada no arquivo.
                                    if font_family_name and font_family_name.strip():
                                         char_format.setFontFamily(font_family_name)
                                         print(f"[DEBUG - NXT LOAD] Font Family Applied (from file): {font_family_name} for fragment: '{text}'")
                                    else:
                                          # Se for a fonte padrão ou None/vazio, defina explicitamente a família da fonte padrão do editor
                                          # CORREÇÃO: Se a família da fonte existe no arquivo (não é None/vazio), APLICA ela, mesmo que seja igual à padrão atual.
                                          # Use a fonte padrão do editor SOMENTE se não houver font_family especificada no arquivo.
                                          if font_family_name and font_family_name.strip():
                                               char_format.setFontFamily(font_family_name)
                                               print(f"[DEBUG - NXT LOAD] Font Family Applied (from file): {font_family_name} for fragment: '{text}'")
                                          else:
                                               char_format.setFontFamily(default_font.family())
                                               print(f"[DEBUG - NXT LOAD] Font Family: Default Editor Font ({default_font.family()}) for fragment: '{text}'")


                                    # **Correção:** Use o tamanho da fonte padrão do editor se o tamanho não estiver especificado, for inválido ou igual ao padrão
                                    try:
                                        if isinstance(font_size_val, (int, float)) and font_size_val > 0 and font_size_val != default_font.pointSize():
                                             char_format.setFontPointSize(font_size_val)
                                             print(f"[DEBUG - NXT LOAD] Font Size Applied: {font_size_val} for fragment: '{text}'")
                                        else:
                                            # Se for o tamanho padrão ou inválido, defina explicitamente o tamanho da fonte padrão do editor
                                            char_format.setFontPointSize(default_font.pointSize())
                                            print(f"[DEBUG - NXT LOAD] Font Size: Default Editor Size ({default_font.pointSize()}) for fragment: '{text}'")

                                    except Exception as e:
                                        print(f"[DEBUG - NXT LOAD] Erro ao configurar tamanho da fonte do fragmento '{text}': {e}")
                                        # Fallback para o tamanho padrão do editor em caso de erro
                                        char_format.setFontPointSize(default_font.pointSize())


                                except Exception as e:
                                    print(f"[DEBUG - NXT LOAD] Erro ao configurar fonte do fragmento '{text}': {e}")
                                    # Fallback para a fonte padrão do editor em caso de erro
                                    char_format.setFontFamily(default_font.family())
                                    char_format.setFontPointSize(default_font.pointSize())


                                # Adicionar ID do fragmento, se existir (propriedade USER_ID_PROPERTY)
                                try:
                                    fragment_id = format_dict.get("id") # IDs agora são por fragmento
                                    if fragment_id is not None:
                                        char_format.setProperty(USER_ID_PROPERTY, fragment_id)
                                        print(f"[DEBUG - NXT LOAD] Fragment ID Applied: {fragment_id} for fragment: '{text}'")
                                    else:
                                         # Se não tiver ID, garantir que a propriedade não esteja definida
                                        if char_format.hasProperty(USER_ID_PROPERTY):
                                             char_format.removeProperty(USER_ID_PROPERTY)
                                             print(f"[DEBUG - NXT LOAD] Fragment ID: None (Removed property) for fragment: '{text}'")
                                        else:
                                             print(f"[DEBUG - NXT LOAD] Fragment ID: None for fragment: '{text}'")

                                except Exception as e:
                                    print(f"[DEBUG - NXT LOAD] Erro ao definir ID do fragmento '{text}': {e}")
                                    # Em caso de erro, tentar remover a propriedade ID para limpar
                                    if char_format.hasProperty(USER_ID_PROPERTY):
                                         char_format.removeProperty(USER_ID_PROPERTY)
                                         print(f"[DEBUG - NXT LOAD] Fragment ID: Error (Removed property) for fragment: '{text}'")


                            # Aplicar neutral_color do fragmento, se definido (propriedade UserProperty + 100)
                            try:
                                neutral_color_prop = format_dict.get("neutral_color")
                                if neutral_color_prop is not None:
                                    char_format.setProperty(QTextFormat.UserProperty + 100, bool(neutral_color_prop))
                                    print(f"[DEBUG - NXT LOAD] Fragment Neutral Color Applied: {neutral_color_prop} for fragment: '{text}'")
                                else:
                                     # Se não tiver neutral_color, garantir que a propriedade não esteja definida
                                    if char_format.hasProperty(QTextFormat.UserProperty + 100):
                                         char_format.removeProperty(QTextFormat.UserProperty + 100)
                                         print(f"[DEBUG - NXT LOAD] Fragment Neutral Color: None (Removed property) for fragment: '{text}'")
                                    else:
                                         print(f"[DEBUG - NXT LOAD] Fragment Neutral Color: None for fragment: '{text}'")

                            except Exception as e:
                                print(f"[DEBUG - NXT LOAD] Erro ao definir neutral_color do fragmento '{text}': {e}")
                                # Em caso de erro, tentar remover a propriedade para limpar
                                if char_format.hasProperty(QTextFormat.UserProperty + 100):
                                     char_format.removeProperty(QTextFormat.UserProperty + 100)
                                     print(f"[DEBUG - NXT LOAD] Fragment Neutral Color: Error (Removed property) for fragment: '{text}'")


                            # --- Fim da aplicação de propriedades do fragmento --- #

                            # Insere o texto formatado
                            try:
                                # Define o formato de caractere para o cursor antes de inserir o texto
                                cursor.setCharFormat(char_format)
                                cursor.insertText(text) # insertText aplica o charFormat atual do cursor
                                print(f"[DEBUG - NXT LOAD] Inserted text: '{text}' with format")
                            except Exception as e:
                                print(f"[DEBUG - NXT LOAD] Erro ao inserir texto do fragmento '{text}': {e}")
                                # Em caso de erro, inserir apenas o texto sem formatação para não perder conteúdo
                                try:
                                     cursor.insertText(text)
                                     print(f"[DEBUG - NXT LOAD] Inserted text without format due to error: '{text}'")
                                except Exception as fallback_error:
                                     print(f"[DEBUG - NXT LOAD] Erro catastrófico ao inserir texto '{text}': {fallback_error}")

                        print(f"[DEBUG - NXT LOAD] Fim do processamento dos fragmentos do Bloco #{block_index + 1}.")
                        
                    # Se o bloco não tinha fragmentos, ele já é um bloco vazio devido à insertBlock no início do loop (se não for o primeiro)
                    # Se é o primeiro bloco e não tinha fragmentos, clear() e setPlainText("") já o deixaram vazio.
                    # Se é um bloco com fragmentos, o texto foi inserido.
                    # Agora, precisamos garantir que haja uma quebra de linha APÓS este bloco, se não for o último bloco.
                    if block_index < total_blocks_to_load - 1:
                         # Mova o cursor para o final do bloco atual (após todos os fragmentos)
                         cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                         # Se não for o último bloco na lista, insira uma quebra de linha
                         # Isso garante que o próximo conjunto de fragmentos (ou um bloco vazio subsequente) comece em uma nova linha.
                         cursor.insertBlock()
                         print(f"[DEBUG - NXT LOAD] Inserted block separator after Bloco #{block_index + 1}.")
                    else:
                         print(f"[DEBUG - NXT LOAD] Bloco #{block_index + 1} é o último. Não inserindo separador de bloco.")


                    print(f"[DEBUG - NXT LOAD] Bloco #{block_index + 1} processado.")


                    # A lógica de remoção da última quebra de linha extra precisa ser ajustada.
                    # A forma mais robusta é verificar o documento NO FINAL do carregamento.
                    # Move para o final do documento APENAS SE NÃO FOR O ÚLTIMO BLOCO
                    # E o próximo bloco EXISTIR. NÃO, isso é confuso.
                    # Vamos simplificar: A lógica de inserção de bloco no início do loop e a inserção de texto
                    # devem posicionar o cursor corretamente. Qualquer ajuste final de quebra de linha deve ser FEITO NO FIM DO MÉTODO.

                    print(f"[DEBUG - NXT LOAD] Finalizando carregamento NXT. Ajustando fim do documento.")
                    try:
                         # Move para o final do documento
                         cursor.movePosition(QTextCursor.MoveOperation.End)
                         # Se o último bloco *no editor* estiver vazio (geralmente por uma quebra de linha extra)
                         # E houver mais de um bloco no documento (para não remover a única linha de um arquivo vazio)
                         # E a posição final do cursor for o início de um bloco (indicando um bloco vazio no final)
                         if doc.blockCount() > 1 and cursor.currentBlock().text() == "" and cursor.atBlockStart():
                             # Remove a quebra de linha extra
                             cursor.deletePreviousChar()
                             print(f"[DEBUG - NXT LOAD] Removed extra newline at the very end.")
                         elif doc.blockCount() > 1 and cursor.atEnd() and cursor.positionInBlock() == 0:
                              # Outra forma de verificar um bloco vazio no final
                              cursor.deletePreviousChar()
                              print(f"[DEBUG - NXT LOAD] Removed extra newline at the very end (alt check).")


                    except Exception as e:
                        print(f"[DEBUG - NXT LOAD] Erro ao ajustar quebras de linha finais no final do documento: {e}")
                    
                    # Define a fonte padrão do editor após carregar o conteúdo
                    editor.setCurrentFont(default_font)
                    
                except json.JSONDecodeError as e:
                    QMessageBox.warning(self, "Erro de Formato", 
                        f"O arquivo não está em um formato NXT válido.\n\nErro: {str(e)}")
                    print(f"[DEBUG - NXT LOAD] JSON Decode Error: {e}")
                    return False
                except Exception as e:
                    QMessageBox.warning(self, "Erro ao Carregar NXT", 
                        f"Não foi possível carregar o arquivo NXT.\n\nErro: {str(e)}")
                    print(f"[DEBUG - NXT LOAD] General Error during NXT Load: {e}")
                    return False
                    
            # Para outros formatos (RTF, HTML, texto simples)
            else:
                print(f"[DEBUG - NXT LOAD] Tentando carregar arquivo como texto simples/RTF/HTML: {file_name}")
                try:
                    # Determina o formato pela extensão se não foi especificado
                    if format == "auto":
                        ext = os.path.splitext(file_name)[1].lower()
                        if ext == '.rtf':
                            format = 'rtf'
                        elif ext in ('.htm', '.html'):
                            format = 'html'
                        else:
                            format = 'txt' # Padrão para texto puro

                    with open(file_name, 'r', encoding='utf-8') as file:
                        text = file.read()
                    
                    if format == "rtf":
                        editor.setHtml(text)  # O Qt pode lidar com RTF como HTML
                        print(f"[DEBUG - NXT LOAD] Carregado como RTF.")
                    elif format == "html":
                        editor.setHtml(text)
                        print(f"[DEBUG - NXT LOAD] Carregado como HTML.")
                    else: # txt ou auto fallback
                        editor.setPlainText(text)
                        print(f"[DEBUG - NXT LOAD] Carregado como texto puro.")

                except UnicodeDecodeError:
                    # Tenta ler com um encoding alternativo se UTF-8 falhar
                    print(f"[DEBUG - NXT LOAD] Erro de decodificação UTF-8. Tentando latin-1.")
                    try:
                        with open(file_name, 'r', encoding='latin-1') as file:
                            text = file.read()
                        editor.setPlainText(text)
                        print(f"[DEBUG - NXT LOAD] Carregado com sucesso usando latin-1.")
                    except Exception as e:
                        print(f"[DEBUG - NXT LOAD] Erro ao ler o arquivo com codificação alternativa: {e}")
                        raise Exception(f"Erro ao ler o arquivo com codificação alternativa: {str(e)}")
                except Exception as e:
                     print(f"[DEBUG - NXT LOAD] Erro geral ao carregar formato não NXT: {e}")
                     raise Exception(f"Erro ao carregar arquivo não NXT: {str(e)}")
            
            # Atualiza a interface
            editor.document().setModified(False)
            self.status_bar.showMessage(f"Arquivo carregado: {os.path.basename(file_name)}", 5000)
            print(f"[DEBUG - NXT LOAD] Carregamento do arquivo {file_name} concluído com sucesso.")
            return True
            
        except Exception as e:
            error_msg = f"Não foi possível carregar o arquivo:\n{file_name}\n\nErro: {str(e)}"
            if format == "nxt":
                error_msg += "\n\nO arquivo pode estar corrompido ou em um formato não suportado."
            QMessageBox.warning(self, "Erro ao Carregar", error_msg)
            print(f"[DEBUG - NXT LOAD] Erro final no carregamento de qualquer formato: {e}")
            return False

    def save_all_files(self):
        # ... (código inalterado) ...
        saved = 0; failed = 0; cancelled = False; orig_idx = self.tab_widget.currentIndex()
        for i in range(self.tab_widget.count() - 1, -1, -1):
            editor = self.tab_widget.widget(i)
            if editor and editor.document().isModified():
                path = self.current_files.get(editor)
                if path:
                    # Salva no formato correto (nxt ou outro)
                    fmt = "nxt" if path.lower().endswith(".nxt") else "auto"
                    if self.save_content(editor, path, format=fmt): saved += 1; self.update_tab_title(editor, False)
                    else: failed += 1
                else:
                    self.tab_widget.setCurrentIndex(i); QApplication.processEvents()
                    if self.save_as_file(): saved += 1 # save_as_file pergunta formato
                    else: failed += 1; cancelled = True; break
        if not cancelled and self.tab_widget.currentIndex() != orig_idx and 0 <= orig_idx < self.tab_widget.count(): self.tab_widget.setCurrentIndex(orig_idx)
        status = [];
        if cancelled: status.append("Salvar Todos cancelado.")
        if saved > 0: status.append(f"{saved} salvo(s).")
        if failed > 0: status.append(f"{failed} falha(s).")
        if not cancelled and saved == 0 and failed == 0: status.append("Nenhuma alteração pendente.")
        self.status_bar.showMessage(" ".join(status), 5000)

    def maybe_save(self, editor):
        # ... (código inalterado) ...
        if editor and editor.document().isModified():
            orig_idx = self.tab_widget.indexOf(editor)
            if orig_idx == -1: return False
            tab_text = self.tab_widget.tabText(orig_idx).replace("*", "")
            resp = QMessageBox.warning(self, "Salvar Alterações", f"Salvar alterações em '{tab_text}'?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel, defaultButton=QMessageBox.StandardButton.Save)
            if orig_idx != self.tab_widget.currentIndex() and 0 <= self.tab_widget.currentIndex() < self.tab_widget.count() : self.tab_widget.setCurrentIndex(orig_idx); QApplication.processEvents()
            if resp == QMessageBox.StandardButton.Save:
                path = self.current_files.get(editor)
                if path: # Salva no formato existente (nxt ou outro)
                    fmt = "nxt" if path.lower().endswith(".nxt") else "auto"
                    return self.save_content(editor, path, format=fmt)
                else: # Precisa salvar como
                    self.tab_widget.setCurrentIndex(orig_idx); QApplication.processEvents(); return self.save_as_file()
            elif resp == QMessageBox.StandardButton.Cancel: return False
        return True

    # --- UI Toggles & Settings ---
    # ... (toggle_default_word_wrap, change_default_editor_font inalterados) ...
    def toggle_default_word_wrap(self):
        self.default_word_wrap = self.word_wrap_action.isChecked()
        # Aplica a todos os editores abertos
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if editor:
                wrap = QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere if self.default_word_wrap else QTextOption.WrapMode.NoWrap
                editor.setWordWrapMode(wrap)
        self.settings.setValue(SETTING_DEFAULT_WORDWRAP, self.default_word_wrap)
        self.settings.sync()

    def change_default_editor_font(self):
        font, ok = QFontDialog.getFont(self.default_editor_font, self, "Selecionar Fonte Padrão")
        if ok:
            self.default_editor_font = font
            if self.current_editor:
                self.current_editor.setFont(self.default_editor_font)
                if self.format_popup.isVisible() and self.format_popup.text_edit == self.current_editor: self.format_popup.update_format_buttons()
                # Atualização de fonte padrão nos highlighters
            self.settings.setValue(SETTING_DEFAULT_FONT, self.default_editor_font.toString())

    def toggle_toolbar(self): self.toolbar.setVisible(self.toolbar_action.isChecked())
    def toggle_statusbar(self): self.status_bar.setVisible(self.statusbar_action.isChecked())

    def toggle_status_counters(self):
        self.chars_label.setVisible(self.show_char_count_action.isChecked())
        self.words_label.setVisible(self.show_word_count_action.isChecked())
        self.lines_label.setVisible(self.show_line_count_action.isChecked()); self.update_status()

    def show_and_focus_search(self):
        if self.search_bar_widget:
            if not self.toolbar.isVisible(): 
                self.toolbar.setVisible(True)
                self.toolbar_action.setChecked(True)
            
            # Show search bar and connect to current editor
            self.search_bar_widget.set_contents_visible(True)
            self.toggle_search_action.setChecked(True)
            if self.current_editor:
                self.search_bar_widget.connect_to_editor(self.current_editor)
            
            QTimer.singleShot(50, self.search_bar_widget.focus_input)

    def toggle_search_bar_visibility(self, visible):
        if self.search_bar_widget:
            self.search_bar_widget.set_contents_visible(visible)
            if visible:
                if not self.toolbar.isVisible():
                    self.toolbar.setVisible(True)
                    self.toolbar_action.setChecked(True)
                # Connect to current editor when showing search bar
                if self.current_editor:
                    self.search_bar_widget.connect_to_editor(self.current_editor)
                QTimer.singleShot(50, self.search_bar_widget.focus_input)

    # --- Métodos Highlighter Refatorados ---

    def update_cursor_state(self):
        """Chamado quando a posição do cursor muda no editor ativo."""
        if not self.current_editor:
            return
        cursor = self.current_editor.textCursor()
        fmt_at_cursor = cursor.charFormat()
        new_cursor_id = fmt_at_cursor.property(USER_ID_PROPERTY) or 0
        self.current_cursor_id = new_cursor_id
        for highlighter in self.highlighters.values():
            highlighter.set_cursor_id(new_cursor_id)
        self.update_status()

    def update_highlighter_colors(self):
        """Atualiza as cores de todos os highlighters"""
        for editor, highlighter in self.highlighters.items():
               # Verifica se o highlighter ainda é válido (importante após fechar abas)
            if highlighter:

                if highlighter and highlighter.document():
                    highlighter.update_colors()
                    # highlighter.rehighlight() # update_colors já chama rehighlight


    def toggle_highlight_cursor_setting(self, enable_cursor_mode=True):
        self.highlight_cursor_only = enable_cursor_mode
        # Salva a configuração do modo de highlight também no user_settings.json
        user_settings = self.load_user_settings()
        user_settings[SETTING_HIGHLIGHT_CURSOR_ONLY] = bool(enable_cursor_mode)
        self.save_user_settings(user_settings)
        if hasattr(self, 'settings'):
            self.settings.setValue(SETTING_HIGHLIGHT_CURSOR_ONLY, bool(enable_cursor_mode))
            self.settings.sync()
        if enable_cursor_mode:
            self.highlight_cursor_only_action.setChecked(True)
        else:
            self.highlight_global_action.setChecked(True)
        for highlighter in self.highlighters.values():
            highlighter.set_cursor_only(enable_cursor_mode)
        self.update_highlighter_colors()
        self.update_cursor_state()

    def change_active_highlight_id(self):
        """Abre um diálogo para definir o ID ativo globalmente (0 = nenhum)."""
        current_global_id = self.active_highlight_id

        id_value, ok = QInputDialog.getInt(
            self, "Definir ID para Highlight Global",
            f"ID para destacar globalmente (0 = nenhum, 1-{MAX_HIGHLIGHT_ID}):",
            current_global_id, 0, MAX_HIGHLIGHT_ID, 1 # Min=0, Max=MAX_HIGHLIGHT_ID
        )

        if ok:
            # Usuário confirmou um novo ID (pode ser 0)
            if id_value != self.active_highlight_id:
                self.active_highlight_id = id_value

                # Atualiza todos os highlighters existentes com o novo ID global
                for editor, highlighter in self.highlighters.items():
                    highlighter.set_active_id(self.active_highlight_id)
                    # set_active_id chama rehighlight se o ID mudou

                # Salva a nova configuração de ID ativo global
                self.settings.setValue(SETTING_ACTIVE_HIGHLIGHT_ID, self.active_highlight_id)
                self.settings.sync()

        # Não há mais estado 'checked' para o botão, então nada a fazer aqui

    # --- About Dialog ---
    def show_about(self):
        # ... (código inalterado) ...
        QMessageBox.about(self, f"Sobre {APP_NAME}", f"{APP_NAME}\nVersão 0.1.0\n\nUm editor de texto com abas, temas e formatação especial.\nDe fato, uma grande conquista graças as todas essas I.As: \n\nCursor Fast \nCursor Small \nClaude 3.7 Sonnet\nClaude 3.7 (Thinking Mode)\nClaude 3.5 Sonnet \nGemini 2.0\nGemini 2.5 (Preview Edtion)\nWindsurf SWE-1 & SW-1 Lite \nCascade Base \nGPT-4o \nGPT-4.1 \nDeepSeek v1 & V3.1 \n\nSendo trabalhoso, e um agradecimento a todas elas. \n(c) 2025 {ORG_NAME}")

    # --- Settings Load/Save ---
    def load_settings(self):
     # ... (Carrega geometria, tema, fonte, word wrap - restaurado para highlight) ...
     geom = self.settings.value(SETTING_GEOMETRY)
     if geom:
        if isinstance(geom, QByteArray):
            self.restoreGeometry(geom)
     else:
        scr = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(scr.x() + 50, scr.y() + 50, 900, 600)

     saved_theme = self.settings.value(SETTING_THEME, "dark_xt10")
     if saved_theme == "dark_xt7":
        self.apply_dark_xt7_theme()
     elif saved_theme == "light_xt10":
        self.apply_light_xt10_theme()
     else:
        self.apply_dark_xt10_theme()

     font_str = self.settings.value(SETTING_DEFAULT_FONT)
     temp_font = QFont()
     if isinstance(font_str, str) and temp_font.fromString(font_str):
        self.default_editor_font = temp_font
     else:
        self.default_editor_font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, DEFAULT_FONT_WEIGHT)
    
     self.default_word_wrap = self.settings.value(SETTING_DEFAULT_WORDWRAP, True, type=bool)

    # --- Restaurado: Carrega configuração do Highlighter ---
     self.highlight_cursor_only = bool(self.settings.value(SETTING_HIGHLIGHT_CURSOR_ONLY, False))
     self.active_highlight_id = self.settings.value(SETTING_ACTIVE_HIGHLIGHT_ID, 0, type=int)
    # --- Fim Highlighter ---
            
    # Load window geometry from user settings
     saved_size = self.load_user_settings().get("geometry_size", [1024, 768])
     if isinstance(saved_size, list) and len(saved_size) == 2:
        width, height = saved_size
     else:
        width, height = 1024, 768  # Reasonable default size
    
    # Calculate center position on screen
     screen = QApplication.primaryScreen().availableGeometry()
     x = (screen.width() - width) // 2
     y = (screen.height() - height) // 2

    # Apply geometry
     self.setGeometry(x, y, width, height)



    def apply_loaded_ui_settings(self):
        # ... (Aplica visibilidade toolbar/statusbar/search/counters - restaurado para highlight) ...
        tb_vis = self.settings.value(SETTING_TOOLBAR_VISIBLE, True, type=bool)
        self.toolbar.setVisible(tb_vis)
        self.toolbar_action.setChecked(tb_vis)
        sb_vis = self.settings.value(SETTING_STATUSBAR_VISIBLE, True, type=bool)
        self.status_bar.setVisible(sb_vis)
        self.statusbar_action.setChecked(sb_vis)
        # Se quiser definir ícone para todas as abas, faça assim:
        # for i in range(self.tab_widget.count()):
        #     self.tab_widget.setTabIcon(i, self.get_themed_icon("novo_icone"))

    def get_plugins_dir(self):
        plugins_dir = str(BASE_PATH / "plugins")
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir, exist_ok=True)
        return plugins_dir

    def load_plugins(self):
        import importlib.util
        plugins_dir = self.get_plugins_dir()
        for fname in os.listdir(plugins_dir):
            if fname.endswith('.py'):
                plugin_path = os.path.join(plugins_dir, fname)
                json_path = os.path.splitext(plugin_path)[0]+'.json'
                active = True
                if os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                            active = meta.get('active', True)
                    except Exception:
                        pass
                if not active:
                    continue
                try:
                    spec = importlib.util.spec_from_file_location(fname[:-3], plugin_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, 'setup'):
                        mod.setup(self)
                except Exception as e:
                    print(f"Erro ao carregar plugin {fname}: {e}")

    def show_plugin_manager(self):
        """Opens the plugin manager dialog."""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QPushButton, 
                                   QFileDialog, QMessageBox, QHBoxLayout, QLabel)
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Gerenciar Plugins")
        layout = QVBoxLayout(dlg)
        
        plugin_list = QListWidget()
        plugins_dir = self.get_plugins_dir()
        
        # Build plugin list with metadata
        plugin_entries = []
        for fname in os.listdir(plugins_dir):
            if fname.endswith('.py') or fname.endswith('.json'):
                base = os.path.splitext(fname)[0]
                meta = {
                    'name': base,
                    'version': '',
                    'active': True,
                    'type': fname.split('.')[-1]
                }
                if fname.endswith('.json'):
                    try:
                        with open(os.path.join(plugins_dir, fname), 'r', encoding='utf-8') as f:
                            j = json.load(f)
                            meta['name'] = j.get('name', base)
                            meta['version'] = j.get('version', '')
                            meta['active'] = j.get('active', True)
                    except Exception:
                        pass
                plugin_entries.append((fname, meta))
                
        # Remove duplicates (prefer .json over .py)
        unique = {}
        for fname, meta in plugin_entries:
            unique[meta['name']] = (fname, meta)
            
        for fname, meta in unique.values():
            status = 'Ativo' if meta.get('active', True) else 'Desativado'
            display = f"{meta['name']} [{meta['type']}] v{meta.get('version','')} - {status}"
            plugin_list.addItem(display)
            
        layout.addWidget(QLabel("Plugins instalados:"))
        layout.addWidget(plugin_list)
        
        btns = QHBoxLayout()
        btn_import = QPushButton("Importar Plugin (.py/.json)")
        btn_remove = QPushButton("Remover Plugin")
        btn_toggle = QPushButton("Ativar/Desativar")
        btns.addWidget(btn_import)
        btns.addWidget(btn_remove)
        btns.addWidget(btn_toggle)
        layout.addLayout(btns)
        
        info_label = QLabel("")
        layout.addWidget(info_label)
        
        def import_plugin():
            file, _ = QFileDialog.getOpenFileName(self, "Escolher plugin", "", "Plugin Files (*.py *.json)")
            if file:
                import shutil
                shutil.copy(file, plugins_dir)
                dlg.accept()
                QMessageBox.information(self, "Plugin importado", "Plugin importado com sucesso! Reinicie o app para aplicar.")
                
        def remove_plugin():
            idx = plugin_list.currentRow()
            if idx >= 0:
                fname, meta = list(unique.values())[idx]
                path = os.path.join(plugins_dir, fname)
                if os.path.exists(path):
                    os.remove(path)
                # Remove both .json/.py files
                base = os.path.splitext(fname)[0]
                for ext in ['.py', '.json']:
                    p = os.path.join(plugins_dir, base+ext)
                    if os.path.exists(p):
                        os.remove(p)
                dlg.accept()
                QMessageBox.information(self, "Removido", "Plugin removido. Reinicie o app para aplicar.")
                
        def toggle_plugin():
            idx = plugin_list.currentRow()
            if idx >= 0:
                fname, meta = list(unique.values())[idx]
                base = os.path.splitext(fname)[0]
                json_path = os.path.join(plugins_dir, base+'.json')
                data = meta.copy()
                data['active'] = not meta.get('active', True)
                if not os.path.exists(json_path):
                    # Create minimal json
                    data['name'] = base
                    data['type'] = 'py'
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    info_label.setText("Status alterado. Reinicie o app para aplicar.")
                except Exception as e:
                    info_label.setText(f"Erro ao atualizar: {e}")
                    
        btn_import.clicked.connect(import_plugin)
        btn_remove.clicked.connect(remove_plugin)
        btn_toggle.clicked.connect(toggle_plugin)
        
        layout.addWidget(QLabel("Para ativar/desativar um plugin, clique em Ativar/Desativar e reinicie o app para aplicar."))
        dlg.exec()

    def show_empty_state(self):
     self.central_stack.setCurrentWidget(self.empty_state_widget)

    def hide_empty_state(self):
     self.central_stack.setCurrentWidget(self.tab_widget)

    def load_file_into_editor(self, editor, file_path):
        """Loads a file into the editor."""
        if not editor or not file_path:
            return False
        
        try:
            # Determine format based on extension
            ext = os.path.splitext(file_path)[1].lower()
            fmt = "nxt" if ext == ".nxt" else "auto"
            
            # Load the content
            if self.load_content(editor, file_path, format=fmt):
                self.current_files[editor] = file_path
                self.update_tab_title(editor, False)
                return True
            return False
        except Exception as e:
            QMessageBox.warning(self, "Erro ao Carregar", 
                f"Não foi possível carregar:\n{file_path}\n\nErro: {str(e)}")
            return False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_statusbar_popup_position()

    def moveEvent(self, event):
        super().moveEvent(event)
        self._update_statusbar_popup_position()

    def _update_statusbar_popup_position(self):
        if getattr(self, 'format_popup_mode', '') == 'statusbar' and self.format_popup.isVisible():
            self.show_format_popup_statusbar()

    def save_session(self):
        """Salva o estado atual das abas no SESSION_FILE."""
        session = {"tabs": [], "current_index": self.tab_widget.currentIndex()}
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            file_path = self.current_files.get(editor)
            custom_title = editor.property('custom_title') or ""
            is_temp = False
            if file_path and os.path.abspath(file_path).startswith(os.path.abspath(UNSAVED_DIR)):
                is_temp = True
            session["tabs"].append({
                "file_path": file_path,
                "title": custom_title,
                "is_temp": is_temp
            })
        try:
            with open(SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar sessão: {e}")

    def restore_session(self):
        """Restaura as abas a partir do SESSION_FILE ao iniciar."""
        if not os.path.exists(SESSION_FILE):
            self.show_empty_state()
            return
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                session = json.load(f)
        except Exception as e:
            print(f"Erro ao restaurar sessão: {e}")
            self.show_empty_state()
            return
        tabs = session.get("tabs", [])
        current_index = session.get("current_index", 0)
        if not tabs:
            self.show_empty_state()
            return
        self.tab_widget.clear()
        self.current_files.clear()
        self.highlighters.clear()
        for tab in tabs:
            file_path = tab.get("file_path")
            title = tab.get("title", "")
            is_temp = tab.get("is_temp", False)
            if not file_path or not os.path.exists(file_path):
                print(f"Arquivo não encontrado ao restaurar: {file_path}")
                continue
            self.new_tab(file_path=file_path)
            editor = self.tab_widget.widget(self.tab_widget.count()-1)
            if title:
                editor.setProperty('custom_title', title)
                self.update_tab_title(editor, False)
        if self.tab_widget.count() > 0:
            self.tab_widget.setCurrentIndex(min(current_index, self.tab_widget.count()-1))
        else:
            self.show_empty_state()

    def close_tab(self, index):
        if index < 0 or index >= self.tab_widget.count(): return
        editor_to_close = self.tab_widget.widget(index)
        if not editor_to_close: return
        # Confirmação se modificado
        if editor_to_close.document().isModified():
            if not self.maybe_save(editor_to_close):
                return  # Usuário cancelou
        path = self.current_files.get(editor_to_close)
        
        # Verifica se é arquivo temporário
        is_temp = False
        if path and os.path.exists(path):
            try:
                is_temp = os.path.abspath(path).startswith(os.path.abspath(UNSAVED_DIR))
            except Exception:
                pass # Assume not temporary if path check fails

        # *** NOVO: Aviso para arquivos temporários ***
        if is_temp:
            reply = QMessageBox.question(
                self,
                "Excluir Arquivo Temporário",
                "Este é um arquivo temporário e será excluído permanentemente ao fechar esta aba. Deseja continuar?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel  # Botão padrão
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return # Usuário cancelou a exclusão
        # *** Fim do NOVO: Aviso para arquivos temporários ***

        # Remove arquivo temporário apenas se estiver na pasta unsaved_files
        # Note: A verificação `is_temp` já foi feita acima.
        if is_temp:
            try: os.remove(path)
            except Exception: pass

        if editor_to_close in self.highlighters:
            del self.highlighters[editor_to_close]
        if editor_to_close in self.current_files:
            del self.current_files[editor_to_close]
        try:
            editor_to_close.selectionChanged.disconnect()
        except Exception:
            pass
        self.tab_widget.removeTab(index)
        editor_to_close.deleteLater()
        # NÃO cria nova aba automaticamente!
        if self.tab_widget.count() == 0:
            self.show_empty_state()
        self.save_session()  # Salva sessão ao fechar aba


if __name__ == "__main__":
    # ... (Verifica/Cria pastas icons e light_icons - inalterado) ...
    for path in [ICON_PATH, LIGHT_ICON_PATH]:
        if not os.path.exists(path):
            try:
                os.makedirs(path); print(f"INFO: Created directory: {path}")
                if path == ICON_PATH: print("INFO: Place standard/dark icons here (e.g., new.png, app_icon.png).")
                elif path == LIGHT_ICON_PATH: print("INFO: Place light theme icons here (same names, e.g., new.png, app_icon.png).")
            except Exception as e: print(f"WARNING: Could not create directory: {path} - Error: {e}")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    notepad = DarkNotepad()
    notepad.show()
    # Centraliza o popup após o show inicial se o modo statusbar estiver ativo
    if getattr(notepad, 'format_popup_mode', '') == 'statusbar':
        QTimer.singleShot(0, notepad.show_format_popup_statusbar)
    # Aplica o tema Azure imediatamente após o show()
    #if notepad.current_theme == "azure":
    #    notepad.apply_azure_theme()
    # Se quiser forçar o Azure SEMPRE, basta descomentar a linha abaixo:
    # notepad.apply_azure_theme()
    # Aplica o stylesheet inicial após o show() para garantir que a UI está pronta
    # QTimer.singleShot(0, lambda: apply_initial_stylesheet(notepad)) # Movido para __init__

    sys.exit(app.exec())