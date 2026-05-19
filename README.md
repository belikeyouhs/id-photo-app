# 证件照生成工具

一个基于 Web 的证件照生成应用，支持人脸检测、自动抠图、背景替换和多种证件照尺寸输出。

## 功能特性

- **人脸检测**：自动识别上传图片中的人脸
- **智能抠图**：使用 AI 模型自动去除背景
- **背景替换**：支持白色、蓝色、红色及自定义背景色
- **多种尺寸**：一寸、二寸、小一寸、护照等标准证件照尺寸
- **实时预览**：上传后立即预览，生成后即时下载
- **拖拽上传**：支持拖拽图片到页面上传

## 技术栈

### 后端
- **FastAPI**：高性能 Python Web 框架
- **OpenCV**：图像处理与人脸检测
- **rembg**：基于深度学习的背景移除
- **Pillow**：图像处理库

### 前端
- 原生 HTML/CSS/JavaScript
- 响应式设计
- 拖拽上传交互

## 项目结构

```
id-photo-app/
├── app/                    # 后端应用
│   ├── main.py            # FastAPI 应用入口
│   ├── config.py          # 配置参数（尺寸、颜色等）
│   ├── routers/           # API 路由
│   │   └── photo.py       # 证件照处理 API
│   ├── services/          # 业务逻辑
│   │   ├── face_detector.py  # 人脸检测服务
│   │   ├── background.py     # 背景处理服务
│   │   └── crop.py           # 图片裁剪服务
│   └── models/            # 数据模型
├── frontend/              # 前端页面
│   ├── index.html         # 主页面
│   ├── css/               # 样式文件
│   └── js/                # JavaScript 脚本
├── uploads/               # 上传文件临时存储
├── outputs/               # 生成结果输出目录
├── tests/                 # 测试文件
├── requirements.txt       # Python 依赖
├── run.py                 # 启动脚本
└── start.bat              # Windows 快速启动脚本
```

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装与运行

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd id-photo-app
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   python run.py
   ```

4. **访问应用**
   
   打开浏览器访问：http://localhost:8000

### Windows 快速启动

双击运行 `start.bat`，自动完成依赖安装和服务启动。

## API 接口

### 生成证件照

```http
POST /api/photo/generate
Content-Type: multipart/form-data

Parameters:
- file: 图片文件 (JPEG/PNG, 最大 10MB)
- size: 证件照尺寸 (1inch/2inch/small_1inch/passport)
- bg_color: 背景色 (white/blue/red/hex color)
```

### 健康检查

```http
GET /health
```

## 支持的证件照尺寸

| 名称 | 尺寸 | 像素 |
|------|------|------|
| 一寸 | 25×35mm | 295×413 |
| 二寸 | 35×49mm | 413×579 |
| 小一寸 | 22×32mm | 260×378 |
| 护照 | 33×48mm | 390×567 |

## 测试

```bash
pip install -r requirements-test.txt
pytest
```

## 配置说明

配置项位于 `app/config.py`：

- `MAX_FILE_SIZE`：最大上传文件大小（默认 10MB）
- `ALLOWED_EXTENSIONS`：允许的图片格式
- `FACE_CONFIDENCE_THRESHOLD`：人脸检测置信度阈值

## 许可证

MIT License
