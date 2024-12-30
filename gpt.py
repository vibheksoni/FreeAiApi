from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional, Union
import re
import time
import random
import logging
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

class ChatGPTClient:
    def __init__(self, log_level: Union[int, None] = logging.INFO, log_file: str = "chatgpt.log") -> None:
        """
        Args:
            log_level: Logging level (logging.INFO, logging.DEBUG, etc.). None to disable logging
            log_file: Path to log file
        """
        self.setup_logging(log_level, log_file)
        self.options = ChromeOptions()
        self.driver = Chrome(options=self.options)
        self.init_session()
    
    def __del__(self) -> None:
        self.driver.quit()

    def setup_logging(self, log_level: Union[int, None], log_file: str) -> None:
        """
        Args:
            log_level: Logging level or None to disable
            log_file: Path to log file
        """
        if log_level is not None:
            logging.basicConfig(
                level=log_level,
                filename=log_file,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        self.logger = logging.getLogger(__name__) if log_level is not None else None

    def log(self, level: int, message: str) -> None:
        """
        Args:
            level: Logging level
            message: Log message
        """
        if self.logger:
            self.logger.log(level, message)

    def init_session(self) -> None:
        """
        Initialize ChatGPT session
        """
        try:
            self.driver.get("https://chatgpt.com/")
            time.sleep(3)
            self.check_login_page()
        except WebDriverException as e:
            self.log(logging.ERROR, f"Failed to initialize session: {str(e)}")
            raise

    def wait_for_response(self, timeout: int = 120) -> bool:
        """
        Args:
            timeout: Maximum time to wait in seconds
        Returns:
            bool: True if response received, False if timeout
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Stop streaming']")
                    time.sleep(0.5)
                    continue
                except:
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='send-button']")
                        time.sleep(2)
                        return True
                    except:
                        time.sleep(0.5)
            
            self.log(logging.WARNING, "Response timeout reached")
            return False
            
        except Exception as e:
            self.log(logging.ERROR, f"Error waiting for response: {str(e)}")
            return False

    def send_message(
        self,
        message: str,
        typing_speed: Tuple[float, float] = (0.01, 0.08),
        word_pause: Tuple[float, float] = (0.1, 0.4),
        initial_pause: float = 1.0,
        end_pause: float = 0.5,
        mistake_chance: float = 0.0,
        human_correct: bool = True,
        wait_for_reply: bool = True,
        reply_timeout: int = 120
    ) -> bool:
        """
        Args:
            message: Message to send
            typing_speed: (min, max) seconds between keystrokes
            word_pause: (min, max) seconds between words
            initial_pause: Seconds to wait before typing
            end_pause: Seconds to wait before sending
            mistake_chance: Probability of typos (0-1)
            human_correct: Whether to correct typos
            wait_for_reply: Whether to wait for response
            reply_timeout: Timeout for response in seconds
        Returns:
            bool: True if message sent successfully
        """
        try:
            textbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "prompt-textarea"))
            )
            
            textbox.clear()
            time.sleep(initial_pause)
            
            for i, word in enumerate(message.split()):
                for char in word:
                    if mistake_chance > 0 and random.random() < mistake_chance:
                        wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                        textbox.send_keys(wrong_char)
                        if human_correct:
                            time.sleep(random.uniform(0.1, 0.3))
                            textbox.send_keys(Keys.BACKSPACE)
                            time.sleep(random.uniform(0.1, 0.2))
                    
                    textbox.send_keys(char)
                    time.sleep(random.uniform(typing_speed[0], typing_speed[1]))
                
                if i < len(message.split()) - 1:
                    textbox.send_keys(' ')
                    time.sleep(random.uniform(word_pause[0], word_pause[1]))
            
            time.sleep(end_pause)
            textbox.send_keys(Keys.RETURN)
            
            self.log(logging.INFO, f"Message sent: {message[:50]}...")
            
            if wait_for_reply:
                return self.wait_for_response(timeout=reply_timeout)
            return True
            
        except Exception as e:
            self.log(logging.ERROR, f"Error sending message: {str(e)}")
            return False

    def get_messages(self) -> List[Message]:
        """
        Returns:
            List[Message]: List of messages in the conversation
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flex-col"))
            )
            
            conversation = []
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            for element in soup.find_all(attrs={"data-message-author-role": True}):
                try:
                    role = element.get('data-message-author-role')
                    content = self._parse_message_content(element, role)
                    conversation.append(Message(role=role, content=content))
                except Exception as e:
                    self.log(logging.ERROR, f"Error parsing message: {str(e)}")
                    continue
            
            return conversation
            
        except Exception as e:
            self.log(logging.ERROR, f"Error getting messages: {str(e)}")
            return []

    def _parse_message_content(self, element: BeautifulSoup, role: str) -> str:
        """
        Args:
            element: BeautifulSoup element containing message
            role: Message role (user/assistant)
        Returns:
            str: Parsed message content
        """
        if role == "user":
            content_div = element.find('div', class_='whitespace-pre-wrap')
            return content_div.get_text() if content_div else ""
        
        markdown_div = element.find('div', class_='markdown')
        if not markdown_div:
            return ""
            
        content = []
        for child in markdown_div.children:
            if child.name == 'pre':
                content.append(self._parse_code_block(child))
            elif child.name in ['p', 'h2', 'h3']:
                text = child.get_text().strip()
                if text:
                    prefix = '#' * (int(child.name[1]) if child.name[0] == 'h' else 0)
                    content.append(f"{prefix} {text}" if prefix else text)
            elif child.name in ['ol', 'ul']:
                for li in child.find_all('li'):
                    content.append(f"- {li.get_text().strip()}")
            elif child.name or str(child).strip():
                content.append(str(child).strip())
                
        return '\n\n'.join(content)

    def _parse_code_block(self, pre_element: BeautifulSoup) -> str:
        """
        Args:
            pre_element: BeautifulSoup pre element
        Returns:
            str: Formatted code block
        """
        code_container = pre_element.find('div', class_='contain-inline-size')
        if not code_container:
            return ""
            
        lang = self._detect_language(code_container)
        code_div = code_container.find('div', class_='overflow-y-auto')
        if not code_div:
            return ""
            
        return f"```{lang}\n{code_div.get_text().strip()}\n```"

    def _detect_language(self, container: BeautifulSoup) -> str:
        """
        Args:
            container: BeautifulSoup element containing code
        Returns:
            str: Detected language or empty string
        """
        header_div = container.select_one('div.flex.items-center')
        if header_div:
            header_text = header_div.get_text().strip().lower()
            if header_text and header_text != "copy code":
                return header_text
                
        code_elem = container.find('code')
        if code_elem and code_elem.get('class'):
            lang_class = code_elem.get('class')[0]
            if lang_class.startswith('language-'):
                return lang_class.replace('language-', '')
                
        return ""

    def check_login_page(self) -> bool:
        """
        Returns:
            bool: True if login handled successfully
        """
        try:
            if '/auth/login' in self.driver.current_url:
                try_first = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "button.btn.btn-ghost div.flex.items-center"))
                )
                try_first.click()
                
                WebDriverWait(self.driver, 5).until(
                    lambda x: 'https://chatgpt.com/' == self.driver.current_url)
                time.sleep(2)
                return True
                
            return True
            
        except Exception as e:
            self.log(logging.ERROR, f"Error on login page: {str(e)}")
            return False