from openai import OpenAI
from ..core.config import ConfigManager


class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端。
    """
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        config = ConfigManager.get_instance()
        
        # 使用传入的参数，如果未提供则从配置中获取
        self.model = model or config.ai_config.get('local_model', 'gpt-3.5-turbo')
        self.api_key = api_key or config.ai_config.get('api_key', '')
        self.base_url = base_url or config.ai_config.get('base_url', 'https://api.openai.com/v1')  # 从配置中获取基础URL
        
        # 创建OpenAI客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """调用LLM API来生成回应。"""
        print("正在调用大语言模型...")
        try:
            messages = []
            
            # 添加系统提示词（如果存在）
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            
            # 添加用户提示词
            messages.append({'role': 'user', 'content': prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False
            )
            answer = response.choices[0].message.content
            print("大语言模型响应成功。")
            return answer
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return "错误:调用语言模型服务时出错。"
    
    def set_model(self, model: str):
        """动态设置模型"""
        self.model = model
    
    def set_base_url(self, base_url: str):
        """动态设置基础URL"""
        self.base_url = base_url
        # 重新创建客户端以使用新的基础URL
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)