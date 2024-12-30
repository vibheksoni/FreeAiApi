"""
Name: Vibhek Soni
Age: 19
Github: https://github.com/vibheksoni
"""
import requests, uuid, json, mimetypes
from typing import List, Optional

CREATE_CONVERSATION_URL = "https://x.com/i/api/graphql/{}/CreateGrokConversation"
ADD_RESPONSE_URL = "https://api.x.com/2/grok/add_response.json"
UPLOAD_FILE_URL = "https://x.com/i/api/2/grok/attachment.json"

class GrokMessages:
    """
    Represents a collection of conversation results parsed from raw JSON lines.
    """
    class Result:
        """
        Represents a single result entry with optional fields like message, query, feedbackLabels, etc.
        """
        def __init__(
            self,
            sender: str,
            message: Optional[str] = None,
            query: Optional[str] = None,
            feedback_labels: Optional[List[dict]] = None,
            follow_up_suggestions: Optional[List[dict]] = None,
            tools_used: Optional[dict] = None,
            cited_web_results: Optional[List[dict]] = None,
            web_results: Optional[List[dict]] = None,
            media_post_ids: Optional[List[str]] = None,
            post_ids: Optional[List[str]] = None
        ) -> None:
            self.sender = sender
            self.message = message
            self.query = query
            self.feedback_labels = feedback_labels
            self.follow_up_suggestions = follow_up_suggestions
            self.tools_used = tools_used
            self.cited_web_results = cited_web_results
            self.web_results = web_results
            self.media_post_ids = media_post_ids
            self.post_ids = post_ids

        def __repr__(self) -> str:
            return f"<Result(sender={self.sender}, message={self.message})>"

    def __init__(self, raw_data: str) -> None:
        """
        Parse the provided raw JSONL data into a collection of Result objects.
        """
        self.raw_data = raw_data
        self.results: List[GrokMessages.Result] = []
        self._parse_raw_data()

    def _parse_raw_data(self) -> None:
        """
        Split the raw data by lines and convert each line to a Result object stored in self.results.
        """
        lines = self.raw_data.splitlines()
        for line in lines:
            if line.strip():
                parsed = json.loads(line)
                result_data = parsed.get("result", {})
                result = self.Result(
                    sender=result_data.get("sender"),
                    message=result_data.get("message"),
                    query=result_data.get("query"),
                    feedback_labels=result_data.get("feedbackLabels"),
                    follow_up_suggestions=result_data.get("followUpSuggestions"),
                    tools_used=result_data.get("toolsUsed"),
                    cited_web_results=result_data.get("citedWebResults"),
                    web_results=result_data.get("webResults"),
                    media_post_ids=result_data.get("xMediaPostIds"),
                    post_ids=result_data.get("xPostIds"),
                )
                self.results.append(result)

    def get_message_tokens(self) -> List[str]:
        """
        Return a list of message tokens from the parsed results.
        """
        return [result.message for result in self.results if result.message]

    def get_full_message(self) -> str:
        """
        Return the full message from the parsed results.
        """
        return ''.join(self.get_message_tokens())

    def get_queries(self) -> List[str]:
        """
        Return all query strings from the parsed results.
        """
        return [result.query for result in self.results if result.query]

    def get_feedback_labels(self) -> List[dict]:
        """
        Return a list of feedback label objects.
        """
        return [result.feedback_labels for result in self.results if result.feedback_labels]

    def get_follow_up_suggestions(self) -> List[dict]:
        """
        Return a list of follow-up suggestion objects.
        """
        return [result.follow_up_suggestions for result in self.results if result.follow_up_suggestions]

    def get_tools_used(self) -> List[dict]:
        """
        Return a list of tools used (metadata) from the parsed results.
        """
        return [result.tools_used for result in self.results if result.tools_used]

    def get_cited_web_results(self) -> List[dict]:
        """
        Return a list of cited web results.
        """
        return [result.cited_web_results for result in self.results if result.cited_web_results]

    def get_web_results(self) -> List[dict]:
        """
        Return a list of web results.
        """
        return [result.web_results for result in self.results if result.web_results]

    def get_media_post_ids(self) -> List[List[str]]:
        """
        Return a list of lists containing media post IDs.
        """
        return [result.media_post_ids for result in self.results if result.media_post_ids]

    def get_post_ids(self) -> List[List[str]]:
        """
        Return a list of lists containing post IDs.
        """
        return [result.post_ids for result in self.results if result.post_ids]

class Grok:
    """
    Provides methods to manage Grok interactions such as creating conversations, uploading files, and sending messages.
    """
    def __init__(
        self,
        account_bearer_token: str,
        x_csrf_token: str,
        cookies: str
    ) -> None:
        """
        Initialize a requests session and store relevant headers.
        """
        self.session = requests.Session()
        self.client_uuid = uuid.uuid4().hex
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {account_bearer_token}",
            "content-type": "application/json",
            "cookie": cookies,
            "origin": "https://x.com",
            "priority": "u=1, i",
            "referer": "https://x.com/i/grok",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "x-client-uuid": self.client_uuid,
            "x-csrf-token": x_csrf_token,
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "en"
        }
        self.session.headers = headers
        self.conversation_info = {
            "data": {
                "create_grok_conversation": {
                    "conversation_id": ""
                }
            }
        }
    
    def create_conversation(self) -> None:
        """
        Create a new Grok conversation and store the conversation info.
        """
        query_id = "6cmfJY3d7EPWuCSXWrkOFg"
        data = {"variables":{},"queryId":query_id}
        response = self.session.post(CREATE_CONVERSATION_URL.format(query_id), json=data)
        self.conversation_info = response.json()
        print(self.conversation_info)
    
    def upload_file(self, file_path: str) -> dict:
        """
        Upload a file and return the JSON response containing mediaId and URL.
        """
        original_content_type = self.session.headers.get("content-type")
        if "content-type" in self.session.headers:
            del self.session.headers["content-type"]
        
        content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        with open(file_path, "rb") as f:
            file_path = file_path.replace('\\', '/')
            filename = file_path.split('/')[-1]
            try:
                files = {
                    "image": (
                        filename,    
                        f,           
                        content_type 
                    )
                }
            except Exception as e:
                raise Exception(f"Error preparing file upload: {str(e)}")
            response = self.session.post(UPLOAD_FILE_URL, files=files)
            response_json = response.json()
            media_id = response_json[0]["mediaId"]
            response_json[0]["url"] = f"https://api.x.com/2/grok/attachment.json?mediaId={media_id}"
            self.session.headers["content-type"] = original_content_type
            return response_json
    
    def create_message(
        self, 
        model_name: str, 
        imageGenerateCount:int = 1,
        returnSearchResults: bool = True,
        returnCitations: bool = True,
        eagerTweets: bool = True,
        serverHistory: bool = True
    ) -> dict:
        """
        Create a template for the conversation payload using the specified Grok model.
        """
        return {
            "responses": [],
            "systemPromptName": "",
            "grokModelOptionId": model_name,
            "conversationId": self.conversation_info["data"]["create_grok_conversation"]["conversation_id"],
            "returnSearchResults": returnSearchResults,
            "returnCitations": returnCitations,
            "promptMetadata": {
                "promptSource": "NATURAL",
                "action": "INPUT"
            },
            "imageGenerationCount": imageGenerateCount, # Seems like you can get more than one image at a time
            "requestFeatures": {
                "eagerTweets": eagerTweets,
                "serverHistory": serverHistory
            }
        }

    def add_user_message(
        self,
        request_data: dict,
        message: str,
        sender: int = 1,
        file_attachments: List[str] = []
    ) -> None:
        """
        Append a user message, optionally with file attachments, to the request payload.
        """
        request_data["responses"].append({
            "message": message,
            "sender": sender,
            "fileAttachments": file_attachments
        })
    
    def send(self, request_data: dict) -> str:
        """
        Send the conversation payload to the server and return the response text.
        """
        response = self.session.post(ADD_RESPONSE_URL, json=request_data)
        return response.text