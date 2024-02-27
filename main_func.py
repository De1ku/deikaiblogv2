from openai import AsyncOpenAI
import requests
import os
from dotenv import load_dotenv
from google_images_search import GoogleImagesSearch

class InstagramPublish:
    def __init__(self) -> None:
        load_dotenv()
        self.instagram_id = os.environ.get("INSTAGRAM_ID")
        self.graph_api_token = os.environ.get("GRAPH_API_TOKEN")
        self.graph_url = 'https://graph.facebook.com/v18.0/'
    
    def graph_token_change(self, new_token):
        self.graph_api_token = new_token
        result = f"Токен был изменен. Новый токен:\n {self.graph_api_token}"
        print(result)
        return result
    
    async def upload_photo(self, photo, caption = "без подписи"): #"Загрузка" в инстаграм
        url = self.graph_url + self.instagram_id + "/media"
        params = {'access_token': self.graph_api_token,
                  'image_url': photo,
                  'caption': caption}
        response = requests.post(url, params=params)
        response = response.json()
        print(response)
        creation_id = response['id']
        return creation_id
    
    async def instagram_publish(self, creation_id):
        url = self.graph_url + self.instagram_id + '/media_publish'
        params = {'access_token': self.graph_api_token,
                 'creation_id': creation_id}
        response = requests.post(url,params=params)
        print(response)
        response = response.json()
        print(response)
        return response

class openAIapi:
    def __init__(self) -> None:
        load_dotenv()
        #openai.api_key = os.environ.get("OPENAI_TOKEN")
        self.client = AsyncOpenAI(api_key = os.environ.get("OPENAI_TOKEN"))
        self.engine = 'gpt-3.5-turbo'
    
    async def makeCompletion(self, prompt="Спорт"):
        completion = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"Напиши пост в инстаграм на тему: {prompt}. Выражай мысль не наигранно, а реалистично, как будто ты человек, который ведет блог на подобные темы.",
                    }
                ],
                temperature=0.5,
                max_tokens=1500
            )
        
        answer = completion.choices[0].message.content
        print(f"Вопрос: {prompt}\nОтвет:\n{answer}")
        return answer

class GoogleSearch:
    def __init__(self) -> None:
        self.gis = GoogleImagesSearch('AIzaSyD-OncdP0uryLlfbQnY1Aq2vTCKwu1-VoE', '85778be1713294f72')

    async def google_web_search(self, query = 'кофе'): #поиск картинок в гугле через google_image_search
        search_params = {
            'q': query,
            'num': 10,
            'searchType':'image',
            'fileType':'jpg'
        }
        image = self.gis.search(search_params=search_params)
        image_urls = []
        for image in self.gis.results():
            image_urls.append(image.url)
        # return random.choice(image_urls)
        return image_urls
