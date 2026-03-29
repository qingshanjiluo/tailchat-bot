#!/usr/bin/env python3
"""
消息调度系统演示脚本
演示如何使用JSON指令控制机器人主动发送消息
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from browser_client import TailChatBrowserClient
from message_scheduler import MessageScheduler, Action, ActionType


async def demo_single_instruction():
    """演示单个JSON指令"""
    print("=" * 60)
    print("演示1: 单个JSON指令")
    print("=" * 60)
    
    # 创建浏览器客户端（模拟）
    client = TailChatBrowserClient()
    
    # 创建调度器
    scheduler = MessageScheduler(client)
    
    # 单个JSON指令示例
    single_instruction = '''{
        "action_type": "send_group_message",
        "target": "68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
        "content": "这是一个测试消息，来自消息调度系统！",
        "mentions": ["测试用户"],
        "delay_seconds": 2
    }'''
    
    print(f"指令: {single_instruction}")
    print("执行中...")
    
    # 在实际环境中，这里会真正执行
    # success = await scheduler.execute_json_instruction(single_instruction)
    # print(f"结果: {'成功' if success else '失败'}")
    
    print("✅ 演示完成（模拟执行）")
    print()


async def demo_batch_instructions():
    """演示批量JSON指令"""
    print("=" * 60)
    print("演示2: 批量JSON指令")
    print("=" * 60)
    
    # 创建浏览器客户端（模拟）
    client = TailChatBrowserClient()
    
    # 创建调度器
    scheduler = MessageScheduler(client)
    
    # 批量JSON指令示例
    batch_instructions = '''[
        {
            "action_type": "navigate_to_group",
            "target": "https://chat.mk49.cyou/main/group/68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
            "content": "",
            "delay_seconds": 1
        },
        {
            "action_type": "send_group_message",
            "target": "68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
            "content": "第一条消息：大家好！",
            "delay_seconds": 3
        },
        {
            "action_type": "mention_user",
            "target": "68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
            "content": "有什么问题需要帮忙吗？",
            "mentions": ["用户A", "用户B"],
            "delay_seconds": 5
        }
    ]'''
    
    print(f"批量指令: {batch_instructions[:100]}...")
    print("执行中...")
    
    # 在实际环境中，这里会真正执行
    # success = await scheduler.execute_json_instruction(batch_instructions)
    # print(f"结果: {'成功' if success else '失败'}")
    
    print("✅ 演示完成（模拟执行）")
    print()


async def demo_direct_action():
    """演示直接使用Action对象"""
    print("=" * 60)
    print("演示3: 直接使用Action对象")
    print("=" * 60)
    
    # 创建浏览器客户端（模拟）
    client = TailChatBrowserClient()
    
    # 创建调度器
    scheduler = MessageScheduler(client)
    
    # 直接创建Action对象
    action = Action(
        action_type=ActionType.SEND_GROUP_MESSAGE,
        target="68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
        content="直接使用Action对象发送的消息",
        mentions=["管理员"],
        delay_seconds=1
    )
    
    print(f"Action对象: {action}")
    print("执行中...")
    
    # 在实际环境中，这里会真正执行
    # success = await scheduler.execute_action(action)
    # print(f"结果: {'成功' if success else '失败'}")
    
    print("✅ 演示完成（模拟执行）")
    print()


async def demo_file_instructions():
    """演示从文件读取JSON指令"""
    print("=" * 60)
    print("演示4: 从文件读取JSON指令")
    print("=" * 60)
    
    # 检查示例文件是否存在
    example_file = Path(__file__).parent / "example_instructions.json"
    if not example_file.exists():
        print(f"❌ 示例文件不存在: {example_file}")
        return
    
    # 读取文件内容
    with open(example_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"从文件读取: {example_file.name}")
    print(f"文件描述: {data.get('description', '无描述')}")
    print(f"包含指令数量: {len(data.get('instructions', []))}")
    
    # 提取第一个指令作为示例
    if data.get('instructions'):
        first_instruction = data['instructions'][0]
        print(f"\n第一个指令:")
        print(f"  名称: {first_instruction.get('name', '未命名')}")
        print(f"  描述: {first_instruction.get('description', '无描述')}")
        print(f"  类型: {first_instruction.get('action_type', '未知')}")
        print(f"  目标: {first_instruction.get('target', '无目标')}")
        print(f"  内容: {first_instruction.get('content', '无内容')[:50]}...")
    
    print("\n✅ 文件读取演示完成")
    print()


async def demo_integration_with_bot():
    """演示与主机器人的集成"""
    print("=" * 60)
    print("演示5: 与主机器人的集成")
    print("=" * 60)
    
    print("集成方式:")
    print("1. 在主机器人初始化时创建MessageScheduler实例")
    print("2. 启动调度器: await scheduler.start()")
    print("3. 可以通过以下方式发送指令:")
    print("   - scheduler.execute_json_instruction(json_str)")
    print("   - scheduler.schedule_json_instruction(json_str)")
    print("   - scheduler.execute_action(action)")
    print("   - scheduler.schedule_action(action)")
    print("4. 在机器人关闭时停止调度器: await scheduler.stop()")
    
    print("\n示例代码片段:")
    print("    # 在main_browser.py的initialize方法中:")
    print("    self.scheduler = MessageScheduler(self.client)")
    print("    await self.scheduler.start()")
    print("    ")
    print("    # 发送指令示例:")
    print('    instruction = \'\'\'{')
    print('        "action_type": "send_group_message",')
    print('        "target": "群组ID",')
    print('        "content": "消息内容"')
    print('    }\'\'\'')
    print("    await self.scheduler.execute_json_instruction(instruction)")
    
    print("\n✅ 集成演示完成")
    print()


def show_usage_examples():
    """显示使用示例"""
    print("=" * 60)
    print("使用示例")
    print("=" * 60)
    
    print("\n1. 基本使用:")
    print("    from message_scheduler import MessageScheduler")
    print("    ")
    print("    # 创建调度器")
    print("    scheduler = MessageScheduler(browser_client)")
    print("    ")
    print("    # 启动调度器")
    print("    await scheduler.start()")
    print("    ")
    print("    # 执行JSON指令")
    print('    json_instruction = \'\'\'{')
    print('        "action_type": "send_group_message",')
    print('        "target": "群组ID",')
    print('        "content": "消息内容",')
    print('        "delay_seconds": 5')
    print('    }\'\'\'')
    print("    await scheduler.execute_json_instruction(json_instruction)")
    
    print("\n2. 支持的action_type:")
    print("   - send_group_message: 发送群组消息")
    print("   - send_direct_message: 发送私信")
    print("   - navigate_to_group: 导航到群组")
    print("   - mention_user: @提及用户")
    print("   - scheduled_message: 定时消息")
    print("   - reply_to_message: 回复消息")
    
    print("\n3. 定时重复消息:")
    print('    {')
    print('        "action_type": "scheduled_message",')
    print('        "target": "群组ID",')
    print('        "content": "每日提醒",')
    print('        "delay_seconds": 60,')
    print('        "repeat_interval": 86400,  # 24小时')
    print('        "max_repeats": 7  # 重复7次')
    print('    }')
    
    print("\n4. 批量执行:")
    print('    [')
    print('        {')
    print('            "action_type": "navigate_to_group",')
    print('            "target": "群组URL",')
    print('            "delay_seconds": 1')
    print('        },')
    print('        {')
    print('            "action_type": "send_group_message",')
    print('            "target": "群组ID",')
    print('            "content": "第一条消息",')
    print('            "delay_seconds": 3')
    print('        }')
    print('    ]')


async def main():
    """主函数"""
    print("TailChat AI 消息调度系统演示")
    print("=" * 60)
    
    try:
        # 运行各个演示
        await demo_single_instruction()
        await demo_batch_instructions()
        await demo_direct_action()
        await demo_file_instructions()
        await demo_integration_with_bot()
        
        # 显示使用示例
        show_usage_examples()
        
        print("=" * 60)
        print("所有演示完成！")
        print("\n下一步:")
        print("1. 运行主机器人: python main_browser.py")
        print("2. 机器人启动后会自动创建消息调度器")
        print("3. 可以通过API或文件向调度器发送JSON指令")
        print("4. 查看 example_instructions.json 获取更多示例")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())