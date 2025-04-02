import os
import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
                            QComboBox, QSpinBox, QCheckBox, QProgressBar, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QPalette, QPixmap, QPainter, QBrush, QIcon, QWindow, QFont
from elevenlabs import ElevenLabs
import threading
from datetime import datetime
import tempfile

def resource_path(relative_path):
    """ 获取资源的绝对路径（适配开发/打包模式） """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    
    # 优先级1：检查打包后的assets目录
    packaged_path = os.path.join(base_path, "..", "assets", relative_path)
    if os.path.exists(packaged_path):
        return packaged_path
        
    # 优先级2：检查开发环境的assets目录
    dev_path = os.path.join(base_path, "..", "..", "assets", relative_path)
    if os.path.exists(dev_path):
        return dev_path
        
    # 优先级3：直接路径（兼容旧版）
    return os.path.join(base_path, relative_path)

class WorkerSignals(QObject):
    """自定义信号类，用于线程间通信"""
    finished = pyqtSignal(str, bool)  # 完成信号，传递消息和是否成功
    progress = pyqtSignal(int)        # 进度信号

class TransparentWidget(QWidget):
    """支持透明背景的自定义Widget"""
    def __init__(self, parent=None, bg_color=QColor(255, 255, 255, 3)):
        super().__init__(parent)
        self.bg_color = bg_color
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

class CustomLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("color: #5C8A6F;")  # 主文本颜色
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取文本和矩形
        text = self.text()
        rect = self.rect()
        
        # 设置字体
        font = self.font()
        painter.setFont(font)
        
        # 先绘制象牙色描边/阴影
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                shadow_rect = rect.translated(dx, dy)
                painter.setPen(QColor(242, 234, 218))
                painter.drawText(shadow_rect, self.alignment(), text)
        
        # 再绘制主要文本
        painter.setPen(QColor(92, 138, 111))  # #5C8A6F
        painter.drawText(rect, self.alignment(), text)

class CustomLabel_title(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("color: #69CFF7;")  # 标题颜色
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取文本和矩形
        text = self.text()
        rect = self.rect()
        
        # 设置字体
        font = self.font()
        painter.setFont(font)
        
        # 先绘制象牙色描边/阴影
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                shadow_rect = rect.translated(dx, dy)
                painter.setPen(QColor(242, 234, 218))
                painter.drawText(shadow_rect, self.alignment(), text)
        
        # 再绘制主要文本
        painter.setPen(QColor(105, 207, 247))  # #69CFF7
        painter.drawText(rect, self.alignment(), text)

class SubtitleConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("语音转字幕小帮手 v1.0 (Qt版)")
        self.resize(1024, 768)
        
        # 设置窗口属性实现无边框但保留背景
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        
        # 设置图标 - 为任务栏图标做特别处理
        # icon_path = resource_path("icon.ico")
        # self.app_icon = QIcon(icon_path)
        icon_path = resource_path("icon.ico")
        if not os.path.exists(icon_path):
            QMessageBox.warning(None, "警告", f"图标文件缺失: {icon_path}")
            self.app_icon = QIcon()  # 空图标
        else:
            self.app_icon = QIcon(icon_path)
        self.setWindowIcon(self.app_icon)
        
        # 主窗口背景设置
        self.background = QPixmap(resource_path("background.png"))
        if not self.background:
            # 如果背景图不存在，创建一个渐变背景
            self.background = QPixmap(self.size())
            painter = QPainter(self.background)
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(40, 40, 80))
            gradient.setColorAt(1, QColor(20, 20, 40))
            painter.fillRect(self.rect(), gradient)
            painter.end()
        else:
            self.background = self.background.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        
        # 主容器 - 使用完全透明背景
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        
        # 创建工作信号
        self.worker_signals = WorkerSignals()
        self.worker_signals.finished.connect(self.show_result)
        self.worker_signals.progress.connect(self.update_progress)
        
        # 初始化UI
        self.init_ui()
        self.center_window()
        
        # 在窗口显示后应用任务栏图标
        QTimer.singleShot(100, self.apply_taskbar_icon)
        
    def apply_taskbar_icon(self):
        """确保任务栏图标正确设置"""
        # 有些平台需要特殊处理才能显示任务栏图标
        if hasattr(self, 'windowHandle') and self.windowHandle() is not None:
            window = self.windowHandle()
            window.setIcon(self.app_icon)
    
    def center_window(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
    
    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        if self.background:
            # 直接绘制背景图片，不添加额外的遮罩
            painter.drawPixmap(self.rect(), self.background)
    
    def resizeEvent(self, event):
        """窗口大小改变时调整背景"""
        bg_path = resource_path("background.png")
        if os.path.exists(bg_path):
            self.background = QPixmap(bg_path).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        else:
            self.background = QPixmap(self.size())
            painter = QPainter(self.background)
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(40, 40, 80))
            gradient.setColorAt(1, QColor(20, 20, 40))
            painter.fillRect(self.rect(), gradient)
            painter.end()
        # if os.path.exists(bg_path):
        #     self.background = QPixmap(bg_path).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        super().resizeEvent(event)

    def init_ui(self):
        """初始化UI界面"""
        # 主布局
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # 设置应用样式表 - 移除了文本阴影效果，由CustomLabel提供
        QApplication.instance().setStyleSheet("""
            QWidget { 
                font-family: '楷体'; 
                font-weight: bold; 
                color: #5C8A6F;
            }
        """)
        
        # 添加标题栏
        title_bar = QHBoxLayout()
        
        #标题 - 使用自定义标签
        title = CustomLabel_title("语音转字幕小帮手")
        title_font = QFont('楷体', 24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        
        # 最小化按钮
        min_btn = QPushButton("─")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(135, 206, 235, 150);
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                text-shadow: none;
            }
            QPushButton:hover {
                background-color: rgba(135, 206, 235, 200);
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 99, 71, 150);
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
                text-shadow: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 99, 71, 200);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(min_btn)
        btn_layout.addWidget(close_btn)
        btn_layout.setSpacing(10)

        title_bar.addStretch()
        title_bar.addWidget(title)
        title_bar.addStretch()
        title_bar.addLayout(btn_layout)
        
        main_layout.addLayout(title_bar)
        
        # 内容区域 (带透明背景)
        content = TransparentWidget(bg_color=QColor(255, 255, 255, 3))
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # API Key 输入区域
        api_group = QGroupBox("API 设置")
        api_group.setStyleSheet("""
            QGroupBox {
                font: bold 18pt '楷体';
                color: #B34A4A;
                border: 1px solid #87CEEB;
                border-radius: 5px;
                margin-top: 10px;
                background-color: rgba(255, 255, 255, 76);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                font: 15px;
                left: 10px;
                padding: 0 3px;
                color: #B34A4A;
            }
        """)
        api_layout = QHBoxLayout(api_group)
        
        # 使用自定义标签
        api_label = CustomLabel("ElevenLabs API Key:")
        api_label_font = QFont('楷体', 15)
        api_label_font.setBold(True)
        api_label.setFont(api_label_font)
        
        self.api_entry = QLineEdit()
        self.api_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_entry.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 76);
                color: #7a1723;
                border: 1px solid #87CEEB;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_entry)
        content_layout.addWidget(api_group)
        
        # 文件选择区域
        file_group = QGroupBox("文件设置")
        file_group.setStyleSheet(api_group.styleSheet())
        file_layout = QHBoxLayout(file_group)
        
        # 使用自定义标签
        file_label = CustomLabel("音频文件:")
        file_label.setFont(api_label_font)
        
        self.file_entry = QLineEdit()
        self.file_entry.setStyleSheet(self.api_entry.styleSheet())
        browse_btn = QPushButton("浏览")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30, 59, 82, 180);
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font: 15px;
                font-weight: bold;
                text-shadow: none;
            }
            QPushButton:hover {
                background: rgba(42, 83, 120, 180);
            }
        """)
        browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_entry)
        file_layout.addWidget(browse_btn)
        content_layout.addWidget(file_group)
        
        # 高级设置区域
        settings_group = QGroupBox("高级设置")
        settings_group.setStyleSheet(api_group.styleSheet())
        settings_layout = QVBoxLayout(settings_group)
        
        # 第一行设置
        row1 = QHBoxLayout()
        
        # 语言设置 - 使用自定义标签
        lang_label = CustomLabel("语言:")
        lang_label.setFont(api_label_font)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["auto", "ja", "en", "zh", "es", "fr", "de"])
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 76);
                color: #5C8A6F;
                border: 1px solid #87CEEB;
                font: 15px;
                border-radius: 3px;
                padding: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        
        # 说话人数设置 - 使用自定义标签
        speaker_label = CustomLabel("说话人数:")
        speaker_label.setFont(api_label_font)
        
        self.speaker_spin = QSpinBox()
        self.speaker_spin.setRange(1, 32)
        self.speaker_spin.setValue(1)
        self.speaker_spin.setStyleSheet(self.lang_combo.styleSheet())
        
        row1.addWidget(lang_label)
        row1.addWidget(self.lang_combo)
        row1.addSpacing(20)
        row1.addWidget(speaker_label)
        row1.addWidget(self.speaker_spin)
        row1.addStretch()
        settings_layout.addLayout(row1)
        
        # 第二行设置
        row2 = QHBoxLayout()
        
        # 复选框 - 保持原样，因为不需要文本描边效果
        self.tag_events = QCheckBox("生成非语音SE")
        self.tag_events.setChecked(True)
        self.keep_non_speech = QCheckBox("导出非语音SE")
        self.keep_non_speech.setChecked(False)
        
        # 设置复选框样式
        checkbox_style = """
            QCheckBox {
                color: #E6C9C9;
                font: bold 15px "楷体";
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:checked {
                background-color: rgba(110, 44, 44, 180);
                border: 1px solid #87CEEB;
            }
        """
        checkbox_style_2 = """
            QCheckBox {
                color: #AA0000;
                font: bold 15px "楷体";
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:checked {
                background-color: rgba(110, 44, 44, 180);
                border: 1px solid #87CEEB;
            }
        """
        self.tag_events.setStyleSheet(checkbox_style_2)
        self.keep_non_speech.setStyleSheet(checkbox_style)
        
        # 时间戳设置 - 使用自定义标签
        timestamp_label = CustomLabel("时间戳粒度:")
        timestamp_label.setFont(api_label_font)
        
        self.timestamp_combo = QComboBox()
        self.timestamp_combo.addItems(["word", "character", "none"])
        self.timestamp_combo.setStyleSheet(self.lang_combo.styleSheet())
        
        row2.addWidget(self.tag_events)
        row2.addWidget(self.keep_non_speech)
        row2.addSpacing(20)
        row2.addWidget(timestamp_label)
        row2.addWidget(self.timestamp_combo)
        row2.addStretch()
        settings_layout.addLayout(row2)
        
        # 第三行设置
        row3 = QHBoxLayout()
        
        # 质量设置 - 使用自定义标签
        quality_label = CustomLabel("质量:")
        quality_label.setFont(api_label_font)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["standard", "enhanced"])
        self.quality_combo.setStyleSheet(self.lang_combo.styleSheet())
        
        row3.addWidget(quality_label)
        row3.addWidget(self.quality_combo)
        row3.addStretch()
        settings_layout.addLayout(row3)
        
        content_layout.addWidget(settings_group)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #87CEEB;
                border-radius: 5px;
                text-align: center;
                background: rgba(255, 255, 255, 76);
                height: 20px;
                color: #5C8A6F;
            }
            QProgressBar::chunk {
                background-color: #87CEEB;
                width: 10px;
            }
        """)
        content_layout.addWidget(self.progress)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        start_btn = QPushButton("开始转换")
        start_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30, 59, 82, 180);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 25px;
                font: bold 15pt '楷体';
                text-shadow: none;
            }
            QPushButton:hover {
                background: rgba(42, 83, 120, 180);
            }
        """)
        start_btn.clicked.connect(self.start_conversion)
        
        clear_btn = QPushButton("清除")
        clear_btn.setStyleSheet(start_btn.styleSheet())
        clear_btn.clicked.connect(self.clear_fields)
        
        btn_layout.addStretch()
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)
        
        main_layout.addWidget(content)
    
    def browse_file(self):
        """浏览文件"""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("音频文件 (*.mp3 *.wav *.ogg *.m4a *.aac *.flac *.webm);;所有文件 (*.*)")
        if file_dialog.exec():
            filenames = file_dialog.selectedFiles()
            if filenames:
                self.file_entry.setText(filenames[0])
    
    def clear_fields(self):
        """清除所有字段"""
        self.api_entry.clear()
        self.file_entry.clear()
        self.progress.setValue(0)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress.setValue(value)
    
    def show_result(self, message, success):
        """显示结果消息（在主线程中安全调用）"""
        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.critical(self, "错误", message)
        self.progress.setValue(0)
    
    def start_conversion(self):
        """开始转换"""
        def conversion_thread():
            try:
                self.worker_signals.progress.emit(10)
                
                # 验证输入
                api_key = self.api_entry.text().strip()
                audio_path = self.file_entry.text().strip()
                
                if not api_key or not self.validate_api_key(api_key):
                    self.worker_signals.finished.emit("API Key无效或格式不正确", False)
                    return
                
                if not os.path.exists(audio_path):
                    self.worker_signals.finished.emit("文件不存在", False)
                    return
                
                # 初始化客户端
                client = ElevenLabs(api_key=api_key)
                self.worker_signals.progress.emit(30)
                
                # 处理文件
                with open(audio_path, "rb") as audio_file:
                    if self.lang_combo.currentText() == "auto":
                        result = client.speech_to_text.convert(
                            model_id="scribe_v1",
                            file=audio_file,
                            num_speakers=self.speaker_spin.value(),
                            tag_audio_events=self.tag_events.isChecked(),
                            timestamps_granularity=self.timestamp_combo.currentText(),
                            diarize=self.speaker_spin.value() > 1
                        )
                    else:
                        result = client.speech_to_text.convert(
                            model_id="scribe_v1",
                            file=audio_file,
                            language_code=self.lang_combo.currentText(),
                            num_speakers=self.speaker_spin.value(),
                            tag_audio_events=self.tag_events.isChecked(),
                            timestamps_granularity=self.timestamp_combo.currentText(),
                            diarize=self.speaker_spin.value() > 1
                        )
                
                self.worker_signals.progress.emit(70)
                
                # 准备输出路径
                output_dir = os.path.dirname(audio_path)
                base_name = os.path.splitext(os.path.basename(audio_path))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 保存JSON
                json_path = os.path.join(output_dir, f"{base_name}_{timestamp}.json")
                try:
                    if hasattr(result, 'model_dump'):
                        result_data = result.model_dump()
                    elif hasattr(result, 'dict'):
                        result_data = result.dict()
                    else:
                        result_data = vars(result)
                    
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(result_data, f, ensure_ascii=False, indent=2)
                except Exception as json_error:
                    if os.path.exists(json_path):
                        os.remove(json_path)
                    raise Exception(f"JSON保存失败: {str(json_error)}")
                
                # 根据时间戳粒度决定输出格式
                if self.timestamp_combo.currentText() == "none":
                    # 输出TXT（纯文本）
                    txt_path = os.path.join(output_dir, f"{base_name}_{timestamp}.txt")
                    with open(txt_path, "w", encoding="utf-8") as f:
                        f.write(result_data.get("text", ""))
                    message = f"转换成功！\nJSON: {json_path}\nTXT: {txt_path}"
                else:
                    # 输出SRT（带时间戳）
                    srt_path = os.path.join(output_dir, f"{base_name}_{timestamp}.srt")
                    with open(srt_path, "w", encoding="utf-8") as f:
                        f.write(self.generate_srt(result_data))
                    message = f"转换成功！\nJSON: {json_path}\nSRT: {srt_path}"
                
                self.worker_signals.progress.emit(100)
                self.worker_signals.finished.emit(message, True)
            
            except Exception as e:
                error_msg = f"转换失败:\n{str(e)}\n\n常见原因：\n" \
                          "1. API Key无效或过期\n" \
                          "2. 不支持的音频格式\n" \
                          "3. 网络连接问题\n" \
                          "4. 服务器端错误\n" \
                          "5. 文件权限问题"
                self.worker_signals.finished.emit(error_msg, False)
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def validate_api_key(self, key):
        """验证API Key"""
        return key.startswith(('sk_', 'eleven_')) and 30 <= len(key) <= 100
    
    def generate_srt(self, data):
        """生成SRT字幕文件内容"""
        if "words" not in data or not data["words"]:
            return ""
        
        words = data["words"]
        srt_content = []
        subtitle_index = 1
        current_text = []
        start_time = None
        end_time = None
        
        # 每3秒或标点符号处分割
        max_duration = 3.0  # 最大字幕持续时间（秒）
        punctuation = ["。", ".", "!", "?", "！", "？", "；", ";", "，", ","]
        
        for word in words:
            # 如果是非语音事件且不保留，则跳过
            if word.get("type") == "audio_event" and not self.keep_non_speech.isChecked():
                continue
                
            # 获取开始和结束时间
            word_start = float(word.get("start", 0))
            word_end = float(word.get("end", 0))
            word_text = word.get("text", "")
            
            # 设置当前字幕的起始时间
            if start_time is None:
                start_time = word_start
                
            # 更新结束时间
            end_time = word_end
            
            # 添加到当前文本
            current_text.append(word_text)
            
            # 判断是否需要结束当前字幕
            should_end = False
            
            # 检查持续时间
            if end_time - start_time >= max_duration:
                should_end = True
                
            # 检查标点符号
            if any(p in word_text for p in punctuation):
                should_end = True
                
            # 处理字幕分段
            if should_end or word == words[-1]:  # 最后一个词也要结束
                # 格式化时间
                start_formatted = self.format_time(start_time)
                end_formatted = self.format_time(end_time)
                
                # 组合文本
                subtitle_text = "".join(current_text).strip()
                
                # 添加字幕
                if subtitle_text:  # 确保字幕有内容
                    srt_entry = f"{subtitle_index}\n{start_formatted} --> {end_formatted}\n{subtitle_text}\n\n"
                    srt_content.append(srt_entry)
                    subtitle_index += 1
                
                # 重置当前字幕
                current_text = []
                start_time = None
        
        return "".join(srt_content)
    
    def format_time(self, seconds):
        """将秒转换为SRT格式的时间 (00:00:00,000)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def mousePressEvent(self, event):
        """实现窗口拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """实现窗口拖动"""
        if hasattr(self, 'drag_pos'):
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 确保应用程序拥有正确的图标
    app_icon = QIcon(resource_path("icon.ico"))
    app.setWindowIcon(app_icon)
    
    # 设置应用ID以确保任务栏图标正确显示（Windows特有）
    if os.name == 'nt':  # 检查是否为Windows系统
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SubtitleConverter")
    
    window = SubtitleConverter()
    window.show()
    sys.exit(app.exec())