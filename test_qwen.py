#!/usr/bin/env python3
"""
Qwen API 配置测试脚本
用于测试 DashScope API 是否配置正确
"""

import os
import sys

def test_dashscope_import():
    """测试dashscope库是否安装"""
    print("=" * 50)
    print("测试1: 检查 dashscope 库")
    print("=" * 50)
    try:
        import dashscope
        print("✅ dashscope 已安装")
        print(f"   版本: {dashscope.__version__ if hasattr(dashscope, '__version__') else '未知'}")
        return True
    except ImportError:
        print("❌ dashscope 未安装")
        print("   请运行: pip install dashscope")
        return False

def test_api_key():
    """测试API Key是否设置"""
    print("\n" + "=" * 50)
    print("测试2: 检查 API Key")
    print("=" * 50)
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if api_key:
        print(f"✅ 环境变量已设置")
        print(f"   API Key: {api_key[:10]}...{api_key[-5:]}")
        return api_key
    else:
        print("⚠️  环境变量未设置")
        api_key = input("请输入你的 DashScope API Key (或按Enter跳过): ").strip()
        if api_key:
            return api_key
        else:
            print("ℹ️  将使用代码中的API Key（如果有）")
            return None

def test_api_call(api_key):
    """测试API调用"""
    print("\n" + "=" * 50)
    print("测试3: 调用 Qwen API")
    print("=" * 50)
    
    try:
        import dashscope
        from dashscope import Generation
        
        if api_key:
            dashscope.api_key = api_key
        
        print("正在调用 Qwen API...")
        
        response = Generation.call(
            model='qwen-plus',
            messages=[{
                'role': 'system',
                'content': '你是一个测试助手'
            }, {
                'role': 'user',
                'content': '请回复"测试成功！"'
            }],
            result_format='message'
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            print("✅ API 调用成功！")
            print(f"   响应: {content}")
            return True
        else:
            print(f"❌ API 调用失败")
            print(f"   错误码: {response.code}")
            print(f"   错误信息: {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False

def test_different_models(api_key):
    """测试不同模型"""
    print("\n" + "=" * 50)
    print("测试4: 测试不同模型")
    print("=" * 50)
    
    try:
        import dashscope
        from dashscope import Generation
        
        if api_key:
            dashscope.api_key = api_key
        
        models = ['qwen-turbo', 'qwen-plus', 'qwen-max']
        
        for model in models:
            print(f"\n测试模型: {model}")
            try:
                response = Generation.call(
                    model=model,
                    messages=[{
                        'role': 'user',
                        'content': '你好'
                    }],
                    result_format='message'
                )
                
                if response.status_code == 200:
                    print(f"  ✅ {model} 可用")
                else:
                    print(f"  ❌ {model} 不可用: {response.message}")
            except Exception as e:
                print(f"  ❌ {model} 错误: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def show_api_guide():
    """显示获取API Key的指南"""
    print("\n" + "=" * 50)
    print("📚 如何获取 DashScope API Key")
    print("=" * 50)
    print("""
1. 访问阿里云百炼平台：https://bailian.console.aliyun.com/
2. 注册/登录阿里云账号
3. 进入"API-KEY管理"页面
4. 点击"创建新的API-KEY"
5. 复制生成的Key

💡 提示：新用户通常有免费额度可以测试
    """)

def main():
    print("\n🧪 Qwen API 配置测试工具")
    print("=" * 50)
    
    # 测试1: 检查库安装
    if not test_dashscope_import():
        print("\n请先安装 dashscope:")
        print("  pip install dashscope")
        show_api_guide()
        return
    
    # 测试2: 检查API Key
    api_key = test_api_key()
    
    # 测试3: 测试API调用
    if not test_api_call(api_key):
        print("\n💡 可能的原因：")
        print("  1. API Key 不正确")
        print("  2. 未开通 DashScope 服务")
        print("  3. 账户余额不足")
        print("  4. 网络连接问题")
        show_api_guide()
        return
    
    # 测试4: 测试不同模型
    test_different_models(api_key)
    
    # 总结
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)
    print("\n现在你可以运行游戏了:")
    print("  python app_qwen.py")
    print("\n然后在浏览器打开: http://localhost:8800")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已中断")
        sys.exit(0)
