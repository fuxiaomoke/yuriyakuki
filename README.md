# 语音转字幕小帮手 - 使用说明

## 工具简介

语音转字幕小帮手是一个基于 PyQt6 和 ElevenLabs API 的图形界面工具，能够将音频文件转换为字幕文件（SRT/TXT格式）并附带JSON格式的详细转录结果。

## 功能特点

- 🎙️ 支持多种音频格式（MP3, WAV, OGG, M4A, AAC, FLAC, WEBM）
- 🌍 多语言支持（自动检测或手动选择）
- 👥 支持多人对话识别
- ⏱️ 可生成带时间戳的字幕（SRT格式）
- 📝 可导出纯文本（TXT格式）
- 🏷️ 支持标记非语音事件（如音效）
- 🎨 美观的图形用户界面

## 系统要求

- Windows

## 快速开始

### 1. 获取API Key

在使用本工具前，您需要获取ElevenLabs API Key：
1. 访问 [ElevenLabs官网](https://elevenlabs.io/)
2. 注册账号并登录
3. 在个人设置中找到API Key，并创建一个新的API Key
(2025.4.9之后，官网重新制定了API价格，由免费转为付费，需按照个人需求订阅，比如我现在用的是5$的档，每个月12.5h)

### 2. 运行发布的工具

```bash
语音转字幕小帮手 v0.1.1.exe
```

### 3. 界面操作说明

![](https://github.com/fuxiaomoke/yuriyakuki/blob/main/assets/screenshot.png)

1. **API设置**
   - 输入您的ElevenLabs API Key

2. **文件设置**
   - 点击"浏览"按钮选择音频文件
   - 支持格式：MP3, WAV, OGG, M4A, AAC, FLAC, WEBM

3. **高级设置**
   - **语言**：选择音频语言或"auto"自动检测
   - **说话人数**：设置音频中的说话人数（1-32人）
   - **生成非语音SE**：标记音频中的非语音事件（如音效）
   - **导出非语音SE**：在输出的内容中包含非语音事件
   - **时间戳粒度**：选择"word"（单词级）、"character"（字符级）或"none"（无时间戳）
   - **质量**：选择"standard"（标准）或"enhanced"（增强）质量

4. **操作按钮**
   - **开始转换**：开始处理音频文件
   - **清除**：清除所有输入字段

### 4. 输出文件

转换完成后，工具会在音频文件所在目录生成：
- `.json` 文件：包含详细的转录结果
- `.srt` 或 `.txt` 文件：根据设置生成带时间戳的字幕或纯文本

## 常见问题

### Q: 转换失败可能是什么原因？
常见原因如下：
1. API Key无效或过期
2. 账户当月配额不足
3. 不支持的音频格式
4. 网络连接问题
5. 服务器端错误
6. 文件权限问题

### Q: 如何选择时间戳粒度？
根据你的需求：
- 选择"word"或"character"会生成带时间戳的SRT文件
- 选择"none"会生成纯文本TXT文件

### Q: 为什么不支持批量处理？
考虑过，但由于官方API不支持白嫖的免费用户的批量的请求，添加批处理功能也不会加快响应速度，遂放弃了。

## 注意事项

1. 请确保您的API Key有效且有足够的配额（2025.4.9之后白嫖不了了，我现在用的是5$的档，每个月12.5h）
2. 长时间音频文件可能需要较长时间处理
3. 多人对话识别准确度取决于音频质量

## 技术支持

如有任何问题或建议，请联系开发者。

---

**版本**: v0.1.1
**最后更新**: 2025-04-02
