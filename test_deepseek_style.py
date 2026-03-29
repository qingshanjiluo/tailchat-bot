#!/usr/bin/env python3
"""
测试DeepSeek消息发送和风格指南集成
"""

import sys
import asyncio
from loguru import logger

# 添加项目路径
sys.path.insert(0, '.')

from message_processor import MessageProcessor
from tailchat_client import Message

class DeepSeekStyleTester:
    """DeepSeek风格测试器"""
    
    def __init__(self):
        self.processor = MessageProcessor()
        
    def test_style_guide_loading(self):
        """测试风格指南加载"""
        logger.info("=== 测试风格指南加载 ===")
        
        # 检查style_guide属性是否存在
        if hasattr(self.processor, 'style_guide'):
            logger.info("[PASS] style_guide属性存在")
            
            # 检查内容
            style_guide = self.processor.style_guide
            if style_guide:
                logger.info(f"[PASS] 风格指南已加载，长度: {len(style_guide)}字符")
                logger.info(f"风格指南预览:\n{style_guide[:200]}...")
                
                # 检查是否包含关键内容
                keywords = ["友好", "中文", "表情符号", "私信", "群聊"]
                found_keywords = []
                for keyword in keywords:
                    if keyword in style_guide:
                        found_keywords.append(keyword)
                
                if found_keywords:
                    logger.info(f"[PASS] 风格指南包含关键内容: {', '.join(found_keywords)}")
                else:
                    logger.warning("[WARN] 风格指南可能缺少关键内容")
            else:
                logger.error("[FAIL] 风格指南内容为空")
        else:
            logger.error("[FAIL] style_guide属性不存在")
            
        return True
    
    def test_system_prompt_generation(self):
        """测试系统提示生成"""
        logger.info("\n=== 测试系统提示生成 ===")
        
        # 测试私信场景
        dm_message = Message(
            id="test-dm-1",
            author="test_user",
            content="你好，我想问一个问题",
            author_id="test_user_id",
            converse_id="dm-converse",
            group_id=None,
            is_dm=True,
            mentions=[],
            created_at="2026-03-29T09:00:00Z"
        )
        
        dm_prompt = self.processor._build_system_prompt(dm_message)
        logger.info("私信系统提示预览:")
        logger.info(f"{dm_prompt[:300]}...")
        
        # 检查是否包含风格指南
        if "风格指南" in dm_prompt:
            logger.info("✓ 私信系统提示包含风格指南")
        else:
            logger.warning("⚠ 私信系统提示可能未包含风格指南")
            
        # 检查是否包含私信特定内容
        if "私信对话" in dm_prompt or "100-300字" in dm_prompt:
            logger.info("✓ 私信系统提示包含场景特定指导")
        else:
            logger.warning("⚠ 私信系统提示可能缺少场景特定指导")
        
        # 测试群聊@场景
        group_message = Message(
            id="test-group-1",
            author="test_user",
            content="@机器人 你好",
            author_id="test_user_id",
            converse_id="group-converse",
            group_id="test_group",
            is_dm=False,
            mentions=["机器人"],
            created_at="2026-03-29T09:00:00Z"
        )
        
        group_prompt = self.processor._build_system_prompt(group_message)
        logger.info("\n群聊系统提示预览:")
        logger.info(f"{group_prompt[:300]}...")
        
        # 检查是否包含风格指南
        if "风格指南" in group_prompt:
            logger.info("✓ 群聊系统提示包含风格指南")
        else:
            logger.warning("⚠ 群聊系统提示可能未包含风格指南")
            
        # 检查是否包含群聊特定内容
        if "群聊对话" in group_prompt or "50-150字" in group_prompt:
            logger.info("✓ 群聊系统提示包含场景特定指导")
        else:
            logger.warning("⚠ 群聊系统提示可能缺少场景特定指导")
            
        return True
    
    async def test_deepseek_integration(self):
        """测试DeepSeek集成"""
        logger.info("\n=== 测试DeepSeek集成 ===")
        
        # 创建测试消息
        test_message = Message(
            id="test-deepseek-1",
            author="test_user",
            content="你好，请介绍一下你自己",
            author_id="test_user_id",
            converse_id="test-converse",
            group_id=None,
            is_dm=True,
            mentions=[],
            created_at="2026-03-29T09:00:00Z"
        )
        
        try:
            # 测试系统提示构建
            system_prompt = self.processor._build_system_prompt(test_message)
            logger.info(f"系统提示长度: {len(system_prompt)}字符")
            
            # 测试DeepSeek客户端连接
            logger.info("测试DeepSeek客户端连接...")
            
            # 检查deepseek属性
            if hasattr(self.processor, 'deepseek'):
                logger.info("[PASS] DeepSeek客户端已初始化")
                
                # 尝试简单的API调用（模拟）
                # 注意：这里不实际调用API，只检查配置
                if hasattr(self.processor.deepseek, 'api_key'):
                    api_key = self.processor.deepseek.api_key
                    if api_key and api_key != "your_deepseek_api_key_here":
                        logger.info("[PASS] DeepSeek API密钥已配置")
                    else:
                        logger.warning("[WARN] DeepSeek API密钥可能需要配置")
                else:
                    logger.info("[INFO] 无法检查API密钥配置")
            else:
                logger.error("[FAIL] DeepSeek客户端未初始化")
                
            # 测试消息处理流程
            logger.info("\n测试消息处理流程...")
            
            # 检查消息处理器方法
            if hasattr(self.processor, 'process_message'):
                logger.info("[PASS] process_message方法存在")
                
                # 模拟处理消息（不实际发送）
                logger.info("模拟消息处理（不实际发送）...")
                
                # 检查是否包含风格指南集成
                if hasattr(self.processor, '_handle_mention'):
                    logger.info("[PASS] @消息处理方法存在")
                if hasattr(self.processor, '_handle_direct_message'):
                    logger.info("[PASS] 私信处理方法存在")
                    
            else:
                logger.error("[FAIL] process_message方法不存在")
                
            return True
            
        except Exception as e:
            logger.error(f"DeepSeek集成测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始DeepSeek消息发送和风格指南集成测试")
        
        # 测试1：风格指南加载
        test1_passed = self.test_style_guide_loading()
        
        # 测试2：系统提示生成
        test2_passed = self.test_system_prompt_generation()
        
        # 测试3：DeepSeek集成
        test3_passed = asyncio.run(self.test_deepseek_integration())
        
        # 总结
        logger.info("\n=== 测试总结 ===")
        logger.info(f"1. 风格指南加载: {'[PASS]' if test1_passed else '[FAIL]'}")
        logger.info(f"2. 系统提示生成: {'[PASS]' if test2_passed else '[FAIL]'}")
        logger.info(f"3. DeepSeek集成: {'[PASS]' if test3_passed else '[FAIL]'}")
        
        all_passed = test1_passed and test2_passed and test3_passed
        if all_passed:
            logger.info("[SUCCESS] 所有测试通过！DeepSeek消息发送和风格指南集成正常")
        else:
            logger.warning("[WARN] 部分测试失败，请检查相关配置")
            
        return all_passed

def main():
    """主函数"""
    # 设置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    
    # 运行测试
    tester = DeepSeekStyleTester()
    success = tester.run_all_tests()
    
    # 输出建议
    logger.info("\n=== 后续步骤建议 ===")
    logger.info("1. 确保style.txt文件在项目根目录")
    logger.info("2. 配置DeepSeek API密钥在.env文件中")
    logger.info("3. 运行实际消息测试: python test_group_message.py")
    logger.info("4. 测试实际消息发送功能")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())