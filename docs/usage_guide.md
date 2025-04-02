# 语音转字幕小帮手 - 使用指南

## 📌 基本介绍
一款基于 ElevenLabs API 的音频转字幕工具，支持生成带时间轴的字幕文件（SRT）和纯文本（TXT/JSON）。

## 🛠️ 安装步骤

### 方式一：源码运行
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行程序
python src/main_optimized.py
```

### 方式二：使用编译版

```bash
# 运行构建脚本（Windows）
packaging/build_advanced.bat
# 生成的可执行文件将出现在项目根目录
```

### 方式三：直接从[releases](https://github.com/fuxiaomoke/yuriyakuki/releases)下载打包好的exe程序解压运行


## 🎯 核心功能

| 功能           | 说明                             |
| -------------- | -------------------------------- |
| 多语言识别     | 支持中文、英文、日语等主流语言   |
| 说话人分离     | 自动区分不同说话人（需设置人数） |
| 非语音事件标记 | 识别背景音效/音乐等非语音内容    |
| 三种输出格式   | SRT/TXT/JSON 一键导出            |

## 🖥️ 界面操作指南
1. **API 设置**  
   - 输入有效的 ElevenLabs API Key（格式： `sk_...`）

2. **文件设置**  
   📂 支持格式：`.mp3`/`.wav`/`.ogg`/`.m4a`/`.flac`

3. **高级设置**  
   ```
   ▸ 语言：auto（自动检测）或手动指定  
   ▸ 说话人数：1-32人  
   ▸ 时间戳粒度：word/character/none  
   ▸ 质量模式：standard/enhanced  
   ```

4. **开始转换**  
   ✅ 进度条显示实时转换进度  
   💾 结果自动保存到音频文件所在目录

## 📂 输出文件说明
```bash
原始文件：test.mp3
生成文件：
  ├── test_20250401_2212.json  # 完整识别数据
  ├── test_20250401_2212.srt   # 标准字幕格式
  └── test_20250401_2212.txt   # 纯文本内容
```

## ❓ 常见问题
### Q1: 如何获取API Key？
访问 [ElevenLabs官网](https://elevenlabs.io/) 注册后获取

### Q2: 转换失败的可能原因
- API Key 无效或配额不足
- 音频文件损坏或格式不支持
- 网络连接异常

## 🚀 高级技巧
- 对于长音频文件，建议选择`enhanced`质量模式
- 多人对话场景请准确设置说话人数
- 需要保留背景音效时勾选"导出非语音SE"
