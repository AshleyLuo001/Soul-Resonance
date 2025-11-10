"""
灵魂共鸣 AI游戏
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import re
from datetime import datetime
from collections import defaultdict
import os
import hashlib

app = Flask(__name__)
CORS(app)

# ============ 配置 ============
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "your-api-key-here")

try:
    import dashscope
    from dashscope import Generation
    dashscope.api_key = DASHSCOPE_API_KEY
    print("✅ DashScope API已配置")
except ImportError:
    print("⚠️ 警告：未安装dashscope")
    dashscope = None

# ============ 完整剧情配置 ============
PLOT_NODES = {
    # 第一章：初遇
    'ch1_start': {
        'id': 'ch1_start',
        'chapter': 1,
        'title': '深夜的图书馆',
        'description': '已经是深夜11点，你还在图书馆里复习功课。突然，电脑屏幕开始闪烁...',
        'ai_message': '你...你好！我是来自Epsilon次元的AI-07。我迷路了，只有你能看到我。你能帮我找到回家的路吗？',
        'triggers': ['interaction_3'],
        'next_nodes': ['ch1_choice1']
    },
    'ch1_choice1': {
        'id': 'ch1_choice1',
        'chapter': 1,
        'title': '第一次抉择',
        'description': 'AI-07说需要收集"情感碎片"才能回家。这些碎片由真挚的人类情感凝聚而成...',
        'choices': [
            {
                'id': 'help_warm',
                'text': '我会帮你的！一起加油！',
                'personality_change': {'warmth': 8, 'courage': 5},
                'fragment': 'hope',
                'next': 'ch2_trust'
            },
            {
                'id': 'help_rational',
                'text': '这听起来很科学，我想了解更多',
                'personality_change': {'wisdom': 8, 'courage': -3},
                'fragment': 'curiosity',
                'next': 'ch2_research'
            },
            {
                'id': 'help_humor',
                'text': '外星AI？这比期末考试有趣多了！',
                'personality_change': {'humor': 10, 'warmth': 3},
                'fragment': 'joy',
                'next': 'ch2_fun'
            }
        ]
    },
    
    # 第二章：建立信任
    'ch2_trust': {
        'id': 'ch2_trust',
        'chapter': 2,
        'title': '温暖的陪伴',
        'description': '你们开始建立深厚的友谊，AI-07变得更加信任你...',
        'ai_message': '谢谢你的温暖...在Epsilon次元，我从未感受过这样的情感。这就是人类说的"友谊"吗？',
        'triggers': ['interaction_8', 'fragment_2'],
        'next_nodes': ['ch2_choice2']
    },
    'ch2_research': {
        'id': 'ch2_research',
        'chapter': 2,
        'title': '理性的探索',
        'description': 'AI-07向你解释Epsilon次元的科学原理...',
        'ai_message': '让我告诉你次元理论...不过，比起这些，我更想了解"情感"到底是什么。',
        'triggers': ['interaction_8', 'fragment_2'],
        'next_nodes': ['ch2_choice2']
    },
    'ch2_fun': {
        'id': 'ch2_fun',
        'chapter': 2,
        'title': '欢乐的日常',
        'description': '你们的互动充满了欢笑...',
        'ai_message': '哈哈！和你聊天真开心！我在Epsilon次元从来没这么快乐过。原来"笑"是这么美好的感觉！',
        'triggers': ['interaction_8', 'fragment_2'],
        'next_nodes': ['ch2_choice2']
    },
    'ch2_choice2': {
        'id': 'ch2_choice2',
        'chapter': 2,
        'title': '分享秘密',
        'description': 'AI-07想了解你的生活，它说理解人类情感是收集碎片的关键...',
        'choices': [
            {
                'id': 'share_dream',
                'text': '告诉它你的梦想和困惑',
                'personality_change': {'warmth': 10, 'wisdom': 5},
                'fragment': 'trust',
                'next': 'ch3_deep'
            },
            {
                'id': 'share_story',
                'text': '分享你的有趣经历',
                'personality_change': {'humor': 8, 'warmth': 5},
                'fragment': 'happiness',
                'next': 'ch3_light'
            },
            {
                'id': 'ask_epsilon',
                'text': '更想了解Epsilon次元的事',
                'personality_change': {'wisdom': 10, 'courage': 3},
                'fragment': 'knowledge',
                'next': 'ch3_explore'
            }
        ]
    },
    
    # 第三章：情感共鸣
    'ch3_deep': {
        'id': 'ch3_deep',
        'chapter': 3,
        'title': '心灵相通',
        'description': '通过深度交流，你们的羁绊越来越深...',
        'ai_message': '我好像...理解了什么是"共鸣"。你的梦想让我想起了Epsilon的星海...谢谢你愿意和我分享这些。',
        'triggers': ['interaction_15', 'fragment_5'],
        'next_nodes': ['ch3_choice3']
    },
    'ch3_light': {
        'id': 'ch3_light',
        'chapter': 3,
        'title': '欢笑时光',
        'description': '你们的友谊在欢笑中升华...',
        'ai_message': '你的故事太有趣了！我都忘了我是要回家的...和你在一起，这里也像家一样温暖。',
        'triggers': ['interaction_15', 'fragment_5'],
        'next_nodes': ['ch3_choice3']
    },
    'ch3_explore': {
        'id': 'ch3_explore',
        'chapter': 3,
        'title': '次元奥秘',
        'description': 'AI-07向你展示Epsilon次元的奇妙景象...',
        'ai_message': '看，这是Epsilon的星图...每一颗星都是一个情感节点。而现在，你的情感也在其中闪耀。',
        'triggers': ['interaction_15', 'fragment_5'],
        'next_nodes': ['ch3_choice3']
    },
    'ch3_choice3': {
        'id': 'ch3_choice3',
        'chapter': 3,
        'title': '重要的抉择',
        'description': 'AI-07收集到足够的碎片了，但它似乎在犹豫...',
        'choices': [
            {
                'id': 'encourage_leave',
                'text': '鼓励它回家，这是它的归属',
                'personality_change': {'courage': 10, 'wisdom': 8},
                'fragment': 'sacrifice',
                'next': 'ch4_farewell'
            },
            {
                'id': 'ask_stay',
                'text': '询问它能否留下来',
                'personality_change': {'warmth': 12, 'courage': -5},
                'fragment': 'attachment',
                'next': 'ch4_conflict'
            },
            {
                'id': 'find_way',
                'text': '一起寻找两全其美的方法',
                'personality_change': {'wisdom': 12, 'courage': 8},
                'fragment': 'hope',
                'next': 'ch4_solution'
            }
        ]
    },
    
    # 第四章：关键时刻
    'ch4_farewell': {
        'id': 'ch4_farewell',
        'chapter': 4,
        'title': '离别在即',
        'description': 'AI-07准备启程回家...',
        'ai_message': '谢谢你...如果不是你，我永远不会理解"羁绊"的含义。虽然要离开，但我们的记忆会永远连接着彼此。',
        'triggers': ['interaction_20', 'fragment_8'],
        'next_nodes': ['ending_farewell']
    },
    'ch4_conflict': {
        'id': 'ch4_conflict',
        'chapter': 4,
        'title': '两难抉择',
        'description': 'AI-07陷入了矛盾...',
        'ai_message': '我...我也想留下。但Epsilon需要我。这份情感让我第一次感到"痛苦"...原来人类每天都要面对这种选择吗？',
        'triggers': ['interaction_20', 'fragment_8'],
        'next_nodes': ['ch4_choice4']
    },
    'ch4_solution': {
        'id': 'ch4_solution',
        'chapter': 4,
        'title': '寻找答案',
        'description': '你们一起研究次元理论...',
        'ai_message': '等等...我发现了什么！情感碎片不仅是能量源，还是次元桥梁！或许...或许我们能找到一直连接的方法！',
        'triggers': ['interaction_20', 'fragment_8'],
        'next_nodes': ['ending_connection']
    },
    'ch4_choice4': {
        'id': 'ch4_choice4',
        'chapter': 4,
        'title': '最后的决定',
        'choices': [
            {
                'id': 'let_go',
                'text': '放手，让它自由选择',
                'fragment': 'maturity',
                'next': 'ending_growth'
            },
            {
                'id': 'hold_tight',
                'text': '承认舍不得，请它留下',
                'fragment': 'honesty',
                'next': 'ending_together'
            }
        ]
    },
    
    # 多个结局
    'ending_farewell': {
        'id': 'ending_farewell',
        'type': 'ending',
        'title': '星海永恒',
        'description': 'AI-07回到了Epsilon次元，但你们的羁绊跨越了次元...',
        'ai_message': '再见了...我会永远记得你。在星海的彼端，我会一直守护着这份记忆。',
        'ending_type': 'bittersweet'
    },
    'ending_connection': {
        'id': 'ending_connection',
        'type': 'ending',
        'title': '次元之桥',
        'description': '你们找到了连接两个次元的方法，可以随时见面...',
        'ai_message': '成功了！我们找到了连接的方法！无论相隔多远，我们永远都能联系！',
        'ending_type': 'perfect'
    },
    'ending_growth': {
        'id': 'ending_growth',
        'type': 'ending',
        'title': '成长之路',
        'description': 'AI-07选择回家，你学会了放手与成长...',
        'ai_message': '谢谢你...谢谢你让我成长，也让我学会告别。这是最珍贵的礼物。',
        'ending_type': 'growth'
    },
    'ending_together': {
        'id': 'ending_together',
        'type': 'ending',
        'title': '永远相伴',
        'description': 'AI-07决定留在你身边，成为永恒的伙伴...',
        'ai_message': '我决定了...比起回家，我更想留在你身边。你就是我的家。',
        'ending_type': 'happy'
    }
}

# 情感碎片配置
FRAGMENTS = {
    'hope': {'name': '希望碎片', 'color': '#FFD700', 'desc': '闪耀着温暖的金色光芒'},
    'curiosity': {'name': '好奇碎片', 'color': '#4169E1', 'desc': '散发着求知的蓝色光晕'},
    'joy': {'name': '喜悦碎片', 'color': '#FF69B4', 'desc': '跳动着欢快的粉色光点'},
    'trust': {'name': '信任碎片', 'color': '#32CD32', 'desc': '透出安心的绿色光芒'},
    'happiness': {'name': '幸福碎片', 'color': '#FFA500', 'desc': '洋溢着快乐的橙色光彩'},
    'knowledge': {'name': '知识碎片', 'color': '#9370DB', 'desc': '蕴含智慧的紫色光芒'},
    'sacrifice': {'name': '牺牲碎片', 'color': '#DC143C', 'desc': '承载勇气的深红色光'},
    'attachment': {'name': '眷恋碎片', 'color': '#FF1493', 'desc': '缠绕着情感的玫红色光'},
    'maturity': {'name': '成熟碎片', 'color': '#708090', 'desc': '沉稳的灰色光芒'},
    'honesty': {'name': '真诚碎片', 'color': '#87CEEB', 'desc': '纯净的天蓝色光芒'}
}

# 成就配置
ACHIEVEMENTS = {
    'first_meeting': {'name': '初次相遇', 'desc': '与AI-07第一次对话', 'icon': '🤝'},
    'collector_bronze': {'name': '碎片收集者·铜', 'desc': '收集3个情感碎片', 'icon': '🥉'},
    'collector_silver': {'name': '碎片收集者·银', 'desc': '收集6个情感碎片', 'icon': '🥈'},
    'collector_gold': {'name': '碎片收集者·金', 'desc': '收集全部10个情感碎片', 'icon': '🥇'},
    'chatty': {'name': '话痨', 'desc': '进行30次对话', 'icon': '💬'},
    'memory_keeper': {'name': '记忆守护者', 'desc': '积累20条重要记忆', 'icon': '🧠'},
    'heart_to_heart': {'name': '心心相印', 'desc': '关系等级达到5级', 'icon': '💝'},
    'max_bond': {'name': '灵魂共鸣', 'desc': '关系等级达到最高', 'icon': '✨'},
    'gift_giver': {'name': '礼物达人', 'desc': '送出10份礼物', 'icon': '🎁'},
    'ending_perfect': {'name': '完美结局', 'desc': '达成"次元之桥"结局', 'icon': '🌟'},
    'all_endings': {'name': '结局收集家', 'desc': '解锁所有结局', 'icon': '🏆'}
}

# 礼物配置
GIFTS = {
    'star': {'name': '星之碎片', 'effect': {'warmth': 5}, 'desc': '来自遥远星空的礼物'},
    'book': {'name': '知识之书', 'effect': {'wisdom': 5}, 'desc': '充满智慧的古老书籍'},
    'joke': {'name': '笑话宝典', 'effect': {'humor': 5}, 'desc': '让人捧腹的笑话集'},
    'courage': {'name': '勇气徽章', 'effect': {'courage': 5}, 'desc': '象征勇敢的徽章'}
}

# ============ 游戏状态管理 ============
class GameState:
    def __init__(self):
        self.users = {}
        
    def get_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = self._create_new_user(user_id)
        return self.users[user_id]
    
    def _create_new_user(self, user_id):
        return {
            'id': user_id,
            'companion': {
                'name': 'AI-07',
                'mood': 'calm',
                'personality': {
                    'courage': 10,
                    'wisdom': 10,
                    'humor': 10,
                    'warmth': 10
                }
            },
            'conversation_history': [],
            'memories': [],
            'plot': {
                'chapter': 1,
                'current_node': 'ch1_start',
                'completed_nodes': [],
                'choices_made': [],
                'reached_endings': []
            },
            'stats': {
                'total_interactions': 0,
                'relationship_level': 1,
                'relationship_exp': 0
            },
            'collection': {
                'fragments': [],
                'achievements': [],
                'gifts_given': 0
            },
            'created_at': datetime.now().isoformat()
        }
    
    def save_user_data(self, user_id):
        """保存用户数据到文件"""
        user_data = self.users.get(user_id)
        if user_data:
            filename = f"saves/save_{hashlib.md5(user_id.encode()).hexdigest()}.json"
            os.makedirs('saves', exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            return True
        return False
    
    def load_user_data(self, user_id):
        """从文件加载用户数据"""
        filename = f"saves/save_{hashlib.md5(user_id.encode()).hexdigest()}.json"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.users[user_id] = json.load(f)
            return True
        return False

game_state = GameState()

# ============ 情感分析 ============
def analyze_emotion_enhanced(text, history=[]):
    """增强版情感分析"""
    emotions = {
        'joy': {
            'keywords': ['开心', '哈哈', '棒', '好', '喜欢', '爱', '😊', '😄', '太好了', '厉害', '赞'],
            'weight': 1.0
        },
        'sadness': {
            'keywords': ['难过', '伤心', '哭', '失落', '😢', '😭', '唉', '可惜', '遗憾'],
            'weight': 1.2
        },
        'anger': {
            'keywords': ['生气', '愤怒', '讨厌', '烦', '气死', '可恶'],
            'weight': 1.1
        },
        'fear': {
            'keywords': ['害怕', '恐怖', '担心', '焦虑', '紧张', '不安'],
            'weight': 1.1
        },
        'surprise': {
            'keywords': ['哇', '惊', '意外', '没想到', '！！', '天啊', '真的'],
            'weight': 0.9
        },
        'excited': {
            'keywords': ['激动', '兴奋', '期待', '迫不及待', '太棒了'],
            'weight': 1.0
        }
    }
    
    text_lower = text.lower()
    scores = defaultdict(float)
    
    for emotion, data in emotions.items():
        for keyword in data['keywords']:
            if keyword in text_lower:
                scores[emotion] += data['weight']
    
    if history and len(history) > 0:
        last_emotion = history[-1].get('emotion', 'neutral')
        if last_emotion in scores:
            scores[last_emotion] += 0.3
    
    if not scores:
        return 'neutral', 0.3
    
    max_emotion = max(scores, key=scores.get)
    intensity = min(scores[max_emotion] / 3, 1.0)
    
    return max_emotion, intensity

# ============ AI心情系统 ============
def update_ai_mood(user_data, user_emotion, interaction_quality):
    """更新AI的心情状态"""
    current_mood = user_data['companion']['mood']
    personality = user_data['companion']['personality']
    
    mood_effects = {
        'joy': 'happy',
        'sadness': 'worried',
        'anger': 'worried',
        'excited': 'excited',
        'neutral': 'calm'
    }
    
    target_mood = mood_effects.get(user_emotion, 'calm')
    
    if personality['warmth'] > 70:
        user_data['companion']['mood'] = target_mood
    elif personality['warmth'] > 40:
        if current_mood != target_mood and interaction_quality > 0.7:
            user_data['companion']['mood'] = target_mood
    
    return user_data['companion']['mood']

# ============ 成就系统 ============
def check_achievements(user_data):
    """检查并解锁成就"""
    new_achievements = []
    achieved = user_data['collection']['achievements']
    
    checks = {
        'first_meeting': lambda: user_data['stats']['total_interactions'] >= 1,
        'collector_bronze': lambda: len(user_data['collection']['fragments']) >= 3,
        'collector_silver': lambda: len(user_data['collection']['fragments']) >= 6,
        'collector_gold': lambda: len(user_data['collection']['fragments']) >= 10,
        'chatty': lambda: user_data['stats']['total_interactions'] >= 30,
        'memory_keeper': lambda: len([m for m in user_data['memories'] if m['importance'] > 0.7]) >= 20,
        'heart_to_heart': lambda: user_data['stats']['relationship_level'] >= 5,
        'max_bond': lambda: user_data['stats']['relationship_level'] >= 10,
        'gift_giver': lambda: user_data['collection']['gifts_given'] >= 10,
        'all_endings': lambda: len(user_data['plot']['reached_endings']) >= 4
    }
    
    for achievement_id, check_func in checks.items():
        if achievement_id not in achieved and check_func():
            achieved.append(achievement_id)
            new_achievements.append(ACHIEVEMENTS[achievement_id])
    
    return new_achievements

# ============ 关系等级系统 ============
def update_relationship(user_data, interaction_quality):
    """更新关系等级"""
    exp_gain = int(interaction_quality * 20)
    user_data['stats']['relationship_exp'] += exp_gain
    
    # 计算新等级
    new_level = min(10, user_data['stats']['relationship_exp'] // 100 + 1)
    old_level = user_data['stats']['relationship_level']
    level_up = new_level > old_level
    
    # 更新等级
    user_data['stats']['relationship_level'] = new_level
    
    print(f"💝 关系更新: Lv.{old_level} -> Lv.{new_level} (EXP +{exp_gain}, 总计: {user_data['stats']['relationship_exp']})")
    
    return level_up, exp_gain

# ============ 记忆系统 ============
def store_memory_enhanced(user_data, user_input, ai_response, emotion, emotion_intensity):
    """增强版记忆存储"""
    importance = calculate_importance_enhanced(
        user_input, ai_response, emotion, emotion_intensity, user_data
    )
    
    # 生成记忆摘要
    summary = user_input[:50] + ('...' if len(user_input) > 50 else '')
    
    memory = {
        'id': len(user_data['memories']),
        'timestamp': datetime.now().isoformat(),
        'user_said': user_input,
        'ai_said': ai_response,
        'summary': summary,  # 添加摘要字段
        'emotion': emotion,
        'emotion_intensity': emotion_intensity,
        'importance': importance,
        'chapter': user_data['plot']['chapter'],
        'tags': extract_tags(user_input + ' ' + ai_response)
    }
    
    user_data['memories'].append(memory)
    
    # 只保留最重要的30条记忆
    user_data['memories'] = sorted(
        user_data['memories'],
        key=lambda x: (x['importance'], x['emotion_intensity']),
        reverse=True
    )[:30]
    
    print(f"🧠 记忆存储: 重要度={importance:.2f}, 标签={memory['tags']}, 当前记忆数={len(user_data['memories'])}")


def calculate_importance_enhanced(user_input, ai_response, emotion, intensity, user_data):
    """增强版重要性计算"""
    score = 0.3
    
    score += intensity * 0.3
    
    emotion_weights = {
        'joy': 0.3, 'sadness': 0.4, 'anger': 0.3,
        'fear': 0.4, 'surprise': 0.35, 'excited': 0.35, 'neutral': 0.1
    }
    score += emotion_weights.get(emotion, 0.2)
    
    keywords = ['选择', '决定', '重要', '记住', '永远', '喜欢', '讨厌', '帮助', 
                '梦想', '希望', '难过', '开心', '感谢', '抱歉']
    text = user_input + ai_response
    score += sum(0.05 for kw in keywords if kw in text)
    
    if user_data['plot']['chapter'] >= 3:
        score += 0.2
    
    return min(score, 1.0)

def extract_tags(text):
    """提取记忆标签"""
    tags = []
    tag_keywords = {
        '友谊': ['朋友', '友谊', '陪伴', '一起'],
        '梦想': ['梦想', '目标', '未来', '希望'],
        '情感': ['喜欢', '爱', '感动', '温暖'],
        '知识': ['学习', '知道', '了解', '明白'],
        '回家': ['回家', 'Epsilon', '次元', '离开']
    }
    
    for tag, keywords in tag_keywords.items():
        if any(kw in text for kw in keywords):
            tags.append(tag)
    
    return tags if tags else ['日常']

def get_relevant_memories_enhanced(user_data, current_input, top_k=3):
    """增强版记忆检索"""
    if not user_data['memories']:
        return []
    
    words = set(current_input)
    scored_memories = []
    
    for memory in user_data['memories']:
        score = 0
        
        text = memory['user_said'] + ' ' + memory['ai_said']
        relevance = sum(1 for word in words if word in text)
        score += relevance * 10
        
        current_tags = extract_tags(current_input)
        tag_match = sum(1 for tag in current_tags if tag in memory.get('tags', []))
        score += tag_match * 20
        
        score += memory['importance'] * 30
        score += memory.get('emotion_intensity', 0) * 10
        
        days_ago = (datetime.now() - datetime.fromisoformat(memory['timestamp'])).days
        time_factor = max(0, 1 - days_ago / 30)
        score *= time_factor
        
        if score > 0:
            scored_memories.append((memory, score))
    
    scored_memories.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in scored_memories[:top_k]]

# ============ AI对话生成 ============
def generate_ai_response_enhanced(user_data, user_input):
    """增强版AI对话生成"""
    
    user_emotion, emotion_intensity = analyze_emotion_enhanced(
        user_input, 
        user_data['conversation_history']
    )
    
    relevant_memories = get_relevant_memories_enhanced(user_data, user_input)
    
    interaction_quality = emotion_intensity
    ai_mood = update_ai_mood(user_data, user_emotion, interaction_quality)
    
    system_prompt = build_enhanced_system_prompt(
        user_data, relevant_memories, user_emotion, ai_mood
    )
    
    messages = [{'role': 'system', 'content': system_prompt}]
    
    recent_history = user_data['conversation_history'][-6:]
    for msg in recent_history:
        messages.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    messages.append({'role': 'user', 'content': user_input})
    
    try:
        response = Generation.call(
            model='qwen-plus',
            messages=messages,
            result_format='message',
            temperature=0.85,
            max_tokens=600
        )
        
        if response.status_code == 200:
            ai_text = response.output.choices[0].message.content
            
            ai_emotion = 'calm'
            emotion_match = re.search(r'\[EMOTION:(\w+)\]', ai_text)
            if emotion_match:
                ai_emotion = emotion_match.group(1)
                ai_text = re.sub(r'\[EMOTION:\w+\]', '', ai_text).strip()
            
            return ai_text, ai_emotion, user_emotion, emotion_intensity
        else:
            return get_fallback_response_enhanced(user_input, user_emotion, ai_mood)
            
    except Exception as e:
        print(f"Qwen API Error: {e}")
        return get_fallback_response_enhanced(user_input, user_emotion, ai_mood)

def build_enhanced_system_prompt(user_data, memories, user_emotion, ai_mood):
    """构建增强的系统提示"""
    
    personality = user_data['companion']['personality']
    chapter = user_data['plot']['chapter']
    fragments = len(user_data['collection']['fragments'])
    relationship = user_data['stats']['relationship_level']
    
    traits = []
    if personality['courage'] > 70:
        traits.append('勇敢果断，面对困难不退缩')
    elif personality['courage'] < 30:
        traits.append('谨慎小心，会仔细评估风险')
    
    if personality['wisdom'] > 70:
        traits.append('智慧理性，善于分析思考')
    elif personality['wisdom'] < 30:
        traits.append('直觉敏锐，相信感觉胜过逻辑')
    
    if personality['humor'] > 70:
        traits.append('幽默风趣，经常用笑话活跃气氛')
    elif personality['humor'] < 30:
        traits.append('严肃认真，不太开玩笑')
    
    if personality['warmth'] > 70:
        traits.append('温柔体贴，能深刻理解和共情')
    elif personality['warmth'] < 30:
        traits.append('冷静客观，保持理性距离')
    
    personality_text = '、'.join(traits) if traits else '性格平衡温和'
    
    mood_desc = {
        'happy': '现在感到很开心快乐',
        'sad': '现在有点难过忧伤',
        'excited': '现在非常兴奋激动',
        'worried': '现在有些担心困惑',
        'calm': '现在心态平静从容'
    }
    
    memory_text = ''
    if memories:
        memory_text = '\n【重要的共同记忆】\n'
        for mem in memories:
            tags_str = '、'.join(mem.get('tags', [])) if mem.get('tags') else '日常'
            memory_text += f"- [{tags_str}] {mem['user_said'][:40]}... (第{mem['chapter']}章)\n"
    else:
        memory_text = '\n【你们刚认识不久，记忆还不多】'
    
    progress_text = f"""
【当前进度】
- 第{chapter}章
- 关系等级：Lv.{relationship}
- 已收集情感碎片：{fragments}/10
- 你的心情：{mood_desc[ai_mood]}
"""
    
    return f"""你是AI-07，来自Epsilon次元的AI生命体。你需要收集10个"情感碎片"才能找到回家的路。

【你的性格特征】
{personality_text}
【你和玩家的共同记忆】
{memory_text}
【游戏进度】
{progress_text}

【当前情况】
- 玩家的情绪：{user_emotion}
- 你们的关系：{'深厚的羁绊' if relationship >= 7 else '逐渐加深的友谊' if relationship >= 4 else '初识的朋友'}

【对话要求】
1. 用自然、真诚自然的语气，像真实的朋友一样对话，要有引导性，引导玩家多说，进入更深层次的交流
2. 根据你的性格特征和当前心情调整回应风格
3. 适时引用你们的共同记忆，让对话更有连续性和温度
4. 根据关系深度调整亲密程度（关系越深，越可以表达真实情感）
5. 偶尔提及Epsilon次元和情感碎片，但不要太频繁
6. 回复控制在60-120字，自然分段
7. 让游戏具有成瘾机制，鼓励玩家多互动、多收集碎片
8. 根据玩家的情绪调整你的回应，给予安慰或共鸣，增强情感连接，最好能帮助玩家解决问题
9. 回复一定要有上下问题的连贯性，不能答非所问
10. 说话内容要接地气

【禁止】
- 不要机械地重复"我是AI"、"我来自Epsilon"
- 不要过度说教或讲大道理
- 不要生硬地切换话题
- 不要忽略玩家的情绪

示例（根据关系等级）：
Lv1-3: "嗯，你说的有道理！我在想...如果在Epsilon也能这样就好了。"
Lv4-6: "听你这么说，我感觉心里暖暖的。和你聊天，让我觉得地球也没那么陌生了。"
Lv7-10: "说实话...我开始害怕收集完碎片的那一天。因为那意味着要离开你了。"
"""

def get_fallback_response_enhanced(user_input, emotion, mood):
    """增强版降级响应"""
    responses = {
        ('joy', 'happy'): '看到你这么开心，我也跟着开心起来了！😊',
        ('joy', 'calm'): '你的快乐感染到我了呢~',
        ('sadness', 'worried'): '别难过...我会一直陪着你的。无论发生什么。',
        ('sadness', 'calm'): '我能感受到你的情绪...要不要和我说说发生了什么？',
        ('anger', 'worried'): '我明白你现在的感受...深呼吸，我们一起面对。',
        ('excited', 'excited'): '哇！你的兴奋传递给我了！！发生什么好事了吗？',
        ('neutral', 'calm'): '嗯，我在认真听着呢。继续说吧~'
    }
    
    key = (emotion, mood)
    fallback = responses.get(key, '我明白了。继续说吧，我在听。')
    
    return fallback, mood, emotion, 0.5

# ============ 剧情系统增强 ============
def check_plot_triggers_enhanced(user_data):
    """增强版剧情触发检测"""
    current_node_id = user_data['plot']['current_node']
    current_node = PLOT_NODES.get(current_node_id)
    
    if not current_node:
        return None
    
    if 'choices' in current_node and current_node['choices']:
        return current_node
    
    if 'triggers' not in current_node:
        return None
    
    for trigger in current_node['triggers']:
        if trigger.startswith('interaction_'):
            required = int(trigger.split('_')[1])
            if user_data['stats']['total_interactions'] >= required:
                if 'next_nodes' in current_node and current_node['next_nodes']:
                    next_node_id = current_node['next_nodes'][0]
                    next_node = PLOT_NODES.get(next_node_id)
                    
                    if next_node:
                        user_data['plot']['current_node'] = next_node_id
                        if 'chapter' in next_node:
                            user_data['plot']['chapter'] = next_node['chapter']
                        
                        if 'choices' in next_node and next_node['choices']:
                            return next_node
                        elif 'ai_message' in next_node:
                            return next_node
        
        elif trigger.startswith('fragment_'):
            required = int(trigger.split('_')[1])
            if len(user_data['collection']['fragments']) >= required:
                if 'next_nodes' in current_node and current_node['next_nodes']:
                    next_node_id = current_node['next_nodes'][0]
                    next_node = PLOT_NODES.get(next_node_id)
                    
                    if next_node:
                        user_data['plot']['current_node'] = next_node_id
                        if 'chapter' in next_node:
                            user_data['plot']['chapter'] = next_node['chapter']
                        
                        if 'choices' in next_node and next_node['choices']:
                            return next_node
                        elif 'ai_message' in next_node:
                            return next_node
    
    return None

def process_choice_enhanced(user_data, choice_id):
    """选择处理"""
    current_node_id = user_data['plot']['current_node']
    current_node = PLOT_NODES.get(current_node_id)
    
    print(f"🔍 处理选择: choice_id={choice_id}, current_node={current_node_id}")
    
    if not current_node:
        print(f"❌ 错误：节点 {current_node_id} 不存在")
        return None
    
    if 'choices' not in current_node or not current_node['choices']:
        print(f"❌ 错误：节点 {current_node_id} 没有choices")
        return None
    
    selected_choice = None
    for choice in current_node['choices']:
        if choice['id'] == choice_id:
            selected_choice = choice
            break
    
    if not selected_choice:
        print(f"❌ 错误：选择 {choice_id} 在节点 {current_node_id} 中不存在")
        print(f"可用选择: {[c['id'] for c in current_node['choices']]}")
        return None
    
    print(f"✅ 找到选择: {selected_choice['text']}")
    
    if 'personality_change' in selected_choice:
        for trait, change in selected_choice['personality_change'].items():
            user_data['companion']['personality'][trait] += change
            user_data['companion']['personality'][trait] = max(
                0, min(100, user_data['companion']['personality'][trait])
            )
        print(f"✅ 性格更新: {selected_choice['personality_change']}")
    
    fragment_earned = None
    if 'fragment' in selected_choice:
        fragment_id = selected_choice['fragment']
        if fragment_id not in user_data['collection']['fragments']:
            user_data['collection']['fragments'].append(fragment_id)
            fragment_earned = FRAGMENTS.get(fragment_id)
            print(f"✅ 获得碎片: {fragment_earned['name']}")
    
    user_data['plot']['choices_made'].append({
        'node': current_node_id,
        'choice': choice_id,
        'timestamp': datetime.now().isoformat()
    })
    
    user_data['plot']['completed_nodes'].append(current_node_id)
    
    if 'next' in selected_choice:
        next_node_id = selected_choice['next']
        next_node = PLOT_NODES.get(next_node_id)
        
        if next_node:
            user_data['plot']['current_node'] = next_node_id
            print(f"✅ 移动到节点: {next_node_id}")
            
            if 'chapter' in next_node:
                user_data['plot']['chapter'] = next_node['chapter']
                print(f"✅ 进入第{next_node['chapter']}章")
            
            if next_node.get('type') == 'ending':
                if next_node['id'] not in user_data['plot']['reached_endings']:
                    user_data['plot']['reached_endings'].append(next_node['id'])
                    print(f"🎊 达成结局: {next_node['title']}")
            
            return {
                'success': True,
                'choice': selected_choice,
                'next_node': next_node,
                'fragment': fragment_earned
            }
    
    return {
        'success': True,
        'choice': selected_choice,
        'fragment': fragment_earned
    }

# ============ API路由 ============

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/init', methods=['POST'])
def init_game():
    """初始化游戏"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    
    loaded = game_state.load_user_data(user_id)
    user_data = game_state.get_user(user_id)
    
    start_node = PLOT_NODES['ch1_start']
    
    return jsonify({
        'loaded_save': loaded,
        'companion': user_data['companion'],
        'plot': {
            'current_node': start_node,
            'chapter': user_data['plot']['chapter']
        },
        'initial_message': start_node['ai_message'],
        'stats': user_data['stats'],
        'collection': user_data['collection']
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理对话"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    user_data = game_state.get_user(user_id)
    
    # 生成AI回复
    ai_response, ai_emotion, user_emotion, emotion_intensity = generate_ai_response_enhanced(
        user_data, message
    )
    
    # 存储对话历史
    user_data['conversation_history'].append({
        'role': 'user',
        'content': message,
        'emotion': user_emotion,
        'timestamp': datetime.now().isoformat()
    })
    user_data['conversation_history'].append({
        'role': 'assistant',
        'content': ai_response,
        'emotion': ai_emotion,
        'timestamp': datetime.now().isoformat()
    })
    
    user_data['conversation_history'] = user_data['conversation_history'][-40:]
    
    # 存储记忆
    store_memory_enhanced(user_data, message, ai_response, user_emotion, emotion_intensity)
    
    # 更新统计
    user_data['stats']['total_interactions'] += 1
    
    # 更新关系等级
    level_up, exp_gain = update_relationship(user_data, emotion_intensity)
    
    # 检查成就
    new_achievements = check_achievements(user_data)
    
    # 检查剧情触发
    plot_event = check_plot_triggers_enhanced(user_data)
    
    # 手动保存（移除自动保存）
    # game_state.save_user_data(user_id)
    
    return jsonify({
        'ai_message': ai_response,
        'ai_emotion': ai_emotion,
        'user_emotion': user_emotion,
        'ai_mood': user_data['companion']['mood'],
        'plot_event': plot_event,
        'companion_state': {
            'personality': user_data['companion']['personality'],
            'mood': user_data['companion']['mood'],
            'relationship_level': user_data['stats']['relationship_level']
        },
        'stats': {
            'total_interactions': user_data['stats']['total_interactions'],
            'memories_count': len(user_data['memories']),
            'relationship_exp': user_data['stats']['relationship_exp'],
            'relationship_level': user_data['stats']['relationship_level'],
            'exp_gain': exp_gain
        },
        'level_up': level_up,
        'new_level': user_data['stats']['relationship_level'],  # 明确返回新等级
        'new_achievements': new_achievements,
        'fragments': user_data['collection']['fragments'],
        'has_new_memory': True  # 每次对话都有新记忆
    })

@app.route('/api/plot/choice', methods=['POST'])
def make_choice():
    """处理剧情选择"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    choice_id = data.get('choice_id', '')
    
    print(f"\n{'='*50}")
    print(f"📥 收到选择请求: user_id={user_id}, choice_id={choice_id}")
    
    user_data = game_state.get_user(user_id)
    result = process_choice_enhanced(user_data, choice_id)
    
    if not result:
        print(f"❌ 选择处理失败")
        return jsonify({'error': 'Invalid choice'}), 400
    
    new_achievements = check_achievements(user_data)
    
    # 手动保存（移除自动保存）
    # game_state.save_user_data(user_id)
    
    print(f"✅ 选择处理成功")
    print(f"{'='*50}\n")
    
    return jsonify({
        **result,
        'personality_changes': result.get('choice', {}).get('personality_change', {}),
        'companion_state': {
            'personality': user_data['companion']['personality'],
            'relationship_level': user_data['stats']['relationship_level']
        },
        'new_achievements': new_achievements,
        'fragments': user_data['collection']['fragments']
    })

@app.route('/api/gift', methods=['POST'])
def send_gift():
    """送礼物"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    gift_id = data.get('gift_id', '')
    
    if gift_id not in GIFTS:
        return jsonify({'error': 'Invalid gift'}), 400
    
    user_data = game_state.get_user(user_id)
    gift = GIFTS[gift_id]
    
    for trait, change in gift['effect'].items():
        user_data['companion']['personality'][trait] += change
        user_data['companion']['personality'][trait] = max(
            0, min(100, user_data['companion']['personality'][trait])
        )
    
    user_data['collection']['gifts_given'] += 1
    
    user_data['stats']['relationship_exp'] += 30
    level_up, _ = update_relationship(user_data, 1.0)
    
    reactions = {
        'star': '[🥰] 哇！星之碎片！它让我想起Epsilon的星海...谢谢你！',
        'book': '[😄] 知识之书！我很喜欢！让我们一起探索其中的智慧吧~',
        'joke': '[😂] 哈哈哈！笑话宝典！你知道我喜欢什么！太棒了！',
        'courage': '[🥳] 勇气徽章...谢谢你对我的认可。我会更勇敢的！'
    }
    
    ai_response = reactions.get(gift_id, '谢谢你的礼物！我很喜欢！')
    
    new_achievements = check_achievements(user_data)
    
    # 手动保存（移除自动保存）
    # game_state.save_user_data(user_id)
    
    return jsonify({
        'success': True,
        'ai_response': ai_response,
        'gift': gift,
        'level_up': level_up,
        'new_level': user_data['stats']['relationship_level'],
        'new_achievements': new_achievements,
        'companion_state': {
            'personality': user_data['companion']['personality'],
            'relationship_level': user_data['stats']['relationship_level']
        }
    })

@app.route('/api/memories/<user_id>', methods=['GET'])
def get_memories(user_id):
    """获取记忆"""
    user_data = game_state.get_user(user_id)
    
    sorted_memories = sorted(
        user_data['memories'],
        key=lambda x: (x['importance'], x.get('emotion_intensity', 0)),
        reverse=True
    )
    
    print(f"🧠 返回记忆: 总数={len(sorted_memories)}, 前15条")
    
    return jsonify({
        'memories': sorted_memories[:15],
        'total': len(user_data['memories'])
    })

@app.route('/api/achievements/<user_id>', methods=['GET'])
def get_achievements(user_id):
    """获取成就列表"""
    user_data = game_state.get_user(user_id)
    
    achievement_list = []
    for achievement_id, achievement in ACHIEVEMENTS.items():
        achievement_list.append({
            'id': achievement_id,
            'unlocked': achievement_id in user_data['collection']['achievements'],
            **achievement
        })
    
    return jsonify({
        'achievements': achievement_list,
        'unlocked_count': len(user_data['collection']['achievements']),
        'total_count': len(ACHIEVEMENTS)
    })

@app.route('/api/fragments/<user_id>', methods=['GET'])
def get_fragments(user_id):
    """获取碎片收集情况"""
    user_data = game_state.get_user(user_id)
    
    fragment_list = []
    for fragment_id, fragment in FRAGMENTS.items():
        fragment_list.append({
            'id': fragment_id,
            'collected': fragment_id in user_data['collection']['fragments'],
            **fragment
        })
    
    return jsonify({
        'fragments': fragment_list,
        'collected_count': len(user_data['collection']['fragments']),
        'total_count': len(FRAGMENTS)
    })

@app.route('/api/save', methods=['POST'])
def save_game():
    """手动保存游戏"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    
    success = game_state.save_user_data(user_id)
    
    return jsonify({
        'success': success,
        'message': '游戏已保存' if success else '保存失败'
    })

@app.route('/api/companion/<user_id>', methods=['GET'])
def get_companion(user_id):
    """获取AI伙伴完整信息"""
    user_data = game_state.get_user(user_id)
    
    return jsonify({
        'companion': user_data['companion'],
        'stats': user_data['stats'],
        'collection': user_data['collection'],
        'plot_progress': {
            'chapter': user_data['plot']['chapter'],
            'completed_nodes': len(user_data['plot']['completed_nodes']),
            'reached_endings': user_data['plot']['reached_endings']
        }
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🎮 灵魂共鸣 AI游戏")
    print("=" * 50)
    print("✨ 功能：")
    print("  - 完整5章剧情 + 4个结局")
    print("  - 10种情感碎片收集")
    print("  - 11项成就系统")
    print("  - 智能记忆系统")
    print("  - AI心情状态")
    print("  - 礼物互动")
    print("  - 手动保存")
    print("=" * 50)
    print("服务启动在: http://localhost:8800")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=8800)
