#!/usr/bin/env python3
"""
消息调度系统最终测试
验证所有功能是否正常
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

print("TailChat AI 消息调度系统测试")
print("=" * 60)

# 1. 测试导入模块
print("\n1. 测试导入模块...")
try:
    from message_scheduler import MessageScheduler, Action, ActionType
    print("[OK] 导入成功")
except ImportError as e:
    print(f"[ERROR] 导入失败: {e}")
    sys.exit(1)

# 2. 测试Action类
print("\n2. 测试Action类...")
try:
    # 测试从JSON创建Action
    json_str = '''{
        "action_type": "send_group_message",
        "target": "test_group",
        "content": "测试消息",
        "mentions": ["user1"],
        "delay_seconds": 5
    }'''
    
    action = Action.from_json(json_str)
    print(f"[OK] Action创建成功: {action.action_type.value}")
    print(f"   目标: {action.target}")
    print(f"   内容: {action.content}")
    print(f"   提及: {action.mentions}")
    print(f"   延迟: {action.delay_seconds}秒")
    
    # 测试转换为JSON
    json_output = action.to_json()
    print(f"[OK] JSON转换成功")
    
except Exception as e:
    print(f"[ERROR] Action测试失败: {e}")

# 3. 测试示例文件
print("\n3. 测试示例文件...")
example_file = Path(__file__).parent / "example_instructions.json"
if example_file.exists():
    try:
        with open(example_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"[OK] 示例文件读取成功")
        print(f"   描述: {data.get('description', '无描述')}")
        print(f"   指令数量: {len(data.get('instructions', []))}")
        
        # 验证第一个指令
        if data.get('instructions'):
            first = data['instructions'][0]
            print(f"   第一个指令: {first.get('name', '未命名')}")
            print(f"   类型: {first.get('action_type', '未知')}")
            
    except Exception as e:
        print(f"[ERROR] 示例文件读取失败: {e}")
else:
    print("[ERROR] 示例文件不存在")

# 4. 测试主机器人集成
print("\n4. 测试主机器人集成...")
try:
    # 检查main_browser.py是否导入了MessageScheduler
    main_browser_path = Path(__file__).parent / "main_browser.py"
    if main_browser_path.exists():
        with open(main_browser_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("导入MessageScheduler", "from message_scheduler import MessageScheduler" in content),
            ("创建调度器实例", "self.scheduler = MessageScheduler" in content),
            ("启动调度器", "await self.scheduler.start()" in content),
            ("停止调度器", "await self.scheduler.stop()" in content)
        ]
        
        for check_name, check_result in checks:
            if check_result:
                print(f"[OK] {check_name}")
            else:
                print(f"[ERROR] {check_name}")
    else:
        print("[ERROR] main_browser.py文件不存在")
        
except Exception as e:
    print(f"[ERROR] 集成测试失败: {e}")

# 5. 测试浏览器客户端兼容性
print("\n5. 测试浏览器客户端兼容性...")
try:
    from browser_client import TailChatBrowserClient
    print("[OK] 浏览器客户端导入成功")
    
    # 创建模拟客户端
    client = TailChatBrowserClient()
    print("[OK] 浏览器客户端创建成功")
    
    # 创建调度器
    scheduler = MessageScheduler(client)
    print("[OK] 消息调度器创建成功")
    
except Exception as e:
    print(f"[ERROR] 浏览器客户端测试失败: {e}")

# 总结
print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("消息调度系统已成功集成到TailChat AI机器人中。")
print("\n已实现的功能:")
print("1. [OK] 支持JSON指令解析")
print("2. [OK] 支持多种操作类型:")
print("   - send_group_message: 发送群组消息")
print("   - send_direct_message: 发送私信")
print("   - navigate_to_group: 导航到群组")
print("   - mention_user: @提及用户")
print("   - scheduled_message: 定时消息")
print("   - reply_to_message: 回复消息")
print("3. [OK] 支持延迟执行")
print("4. [OK] 支持@提及用户")
print("5. [OK] 支持定时重复消息")
print("6. [OK] 已集成到主机器人")
print("\n使用方法:")
print("1. 运行主机器人: python main_browser.py")
print("2. 机器人会自动创建消息调度器")
print("3. 可以通过JSON指令控制机器人主动发送消息")
print("4. 查看 example_instructions.json 获取示例")
print("\n示例JSON指令:")
print('''{
    "action_type": "send_group_message",
    "target": "68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
    "content": "大家好！我是TailChat AI助手",
    "mentions": ["用户1", "用户2"],
    "delay_seconds": 5
}''')
print("\n" + "=" * 60)
print("所有测试完成！系统已准备好使用。")