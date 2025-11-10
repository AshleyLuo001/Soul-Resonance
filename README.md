

# Soul-Resonance
game designed for soul app

# 🚀 快速开始

欢迎使用《灵魂共鸣》AI游戏 

## ⚡ 3步启动

### 1️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 2️⃣ 获取API Key

访问阿里云百炼平台：https://bailian.console.aliyun.com/

1. 注册/登录阿里云账号
2. 开通 DashScope 服务
3. 创建 API Key
4. 复制你的API Key

### 3️⃣ 设置API Key

**方法1：环境变量**
```bash
export DASHSCOPE_API_KEY="sk-xxx"
```

**方法2：直接修改代码**
在 `app_qwen.py` 第14行：
```python
DASHSCOPE_API_KEY = "sk-xxx"  # 替换为你的key
```

### 4️⃣ 启动游戏
```bash
bash start.sh
```

然后访问：http://localhost:8800

---

## 🎯 模型选择

在 `app_qwen.py` 第212行可以更换模型：

```python
response = Generation.call(
    model='qwen-plus',  # 可选：qwen-turbo, qwen-max, qwen-plus
    messages=messages,
    ...
)
```

### 模型对比

| 模型 | 速度 | 质量 | 成本 | 推荐场景 |
|------|------|------|------|---------|
| qwen-turbo | ⭐⭐⭐ | ⭐⭐ | 💰 | 快速测试 |
| qwen-plus | ⭐⭐ | ⭐⭐⭐ | 💰💰 | 平衡选择（推荐）|
| qwen-max | ⭐ | ⭐⭐⭐⭐ | 💰💰💰 | 最佳效果 |

---


## 📝 使用的文件

- `app_qwen.py` - 后端
- `index.html` - 前端界面
- `requirements.txt` - 依赖

---

## 🧪 测试API

```python
# test_qwen.py
import dashscope
from dashscope import Generation

dashscope.api_key = "your-key"

response = Generation.call(
    model='qwen-plus',
    messages=[{
        'role': 'user',
        'content': '你好！'
    }],
    result_format='message'
)

print(response.output.choices[0].message.content)
```

运行测试：
```bash
python test_qwen.py
```

---

## 🆘 常见问题

### Q1: 提示"InvalidApiKey"？
**A:** 
- 检查API Key是否正确
- 确认是否开通了DashScope服务
- 尝试重新创建API Key

### Q2: 提示"InsufficientBalance"？
**A:** 
- 账户余额不足
- 新用户注册后会有免费额度
- 可以在阿里云控制台充值

### Q3: 响应速度慢？
**A:** 
- 换成 qwen-turbo 模型
- 检查网络连接
- 减少max_tokens参数

### Q4: 中文乱码？
**A:** 
- 确保文件编码为UTF-8
- Windows用户可能需要设置 `chcp 65001`

### Q5: 想使用本地部署的Qwen？
**A:** 
需要修改代码，使用Transformers库：
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen-7B-Chat")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen-7B-Chat")
```

---

祝你使用愉快！🎊
