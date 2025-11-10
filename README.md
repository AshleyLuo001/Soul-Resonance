

# 🤖 Soul-Resonance · 灵魂共鸣
![本地图片](./images/封面.jpg "fm")

# 🚀 快速开始

欢迎使用《灵魂共鸣》AI游戏 
情感记忆型AI伙伴 - 一个能记住玩家所有互动、根据情感状态动态调整剧情的智能游戏伙伴。
#### 对话1：打招呼
```
你好AI-07！你看起来有点紧张，别担心~
```
**观察点：** 
- AI会根据你的友善态度调整语气
- 右侧性格条的"温暖"会略微上升

#### 对话2：表达好奇
```
你说的情感碎片到底是什么？
```
**观察点：**
- AI会开始解释背景故事
- "智慧"属性可能会上升
- 这段对话会被记录为重要记忆

#### 对话3：做出承诺
```
我会帮你的！我们一起找到回家的路！
```
**观察点：**
- "勇气"和"温暖"会显著上升
- 互动次数达到3次，即将触发剧情！
## 🎯 展示亮点时刻

### 亮点1：情感识别
输入不同情绪的话，观察AI的反应：

```
开心："太棒了！！！" → AI会分享你的快乐
难过："我今天考试没考好..." → AI会安慰你
担心："这样做会不会有危险？" → AI会给你信心
```

### 亮点2：记忆引用
在后续对话中，AI会提到之前的内容：

```
你：还记得我之前说的吗？
AI：当然记得！你说过会帮我找到回家的路，这让我很感动...
```

### 亮点3：性格变化
做出多个同类选择后，观察性格条的变化：

- 连续选择勇敢的选项 → 勇气条会明显增长
- AI的对话风格会变得更加果断
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

- `app.py` - 后端
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

祝您使用愉快！🎊 
