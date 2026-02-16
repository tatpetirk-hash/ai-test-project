import os
import json
import requests
from typing import List, Dict, Optional

class MovieRecommendationOpenrouter:
    def __init__(self, api_token: str):
        """
        Инициализация системы рекомендаций фильмов с использованием Openrouter API
        
        Args:
            api_token (str): Токен доступа к Openrouter API
        """
        self.api_token = api_token
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
    
    def get_movie_recommendations(self, user_preferences: str, liked_movies: Optional[List[str]] = None) -> Optional[str]:
        """
        Получение рекомендаций фильмов через Openrouter API
        
        Args:
            user_preferences (str): Описание предпочтений пользователя
            liked_movies (List[str], optional): Список фильмов, которые понравились пользователю
            
        Returns:
            Optional[str]: Рекомендации фильмов или None в случае ошибки
        """
        try:
            # Формируем промпт для AI
            prompt = self._create_recommendation_prompt(user_preferences, liked_movies)
            
            # Подготавливаем запрос к API
            payload = {
                "model": "tngtech/deepseek-r1t-chimera:free",
                "messages": [
                    {
                        "role": "system",
                        "content": """Ты - эксперт по рекомендации фильмов. 
Твоя задача - предлагать пользователю фильмы, основываясь на его предпочтениях и вкусах.
Рекомендуй 3-5 фильмов с кратким описанием каждого (1-2 предложения).
Структура ответа:
1. Название фильма (Год) - Краткое описание
2. Название фильма (Год) - Краткое описание
и так далее."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            # Отправляем запрос
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Проверяем ответ
            if response.status_code == 200:
                data = response.json()
                recommendation = data['choices'][0]['message']['content']
                
                
                return recommendation
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"Сообщение: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка при получении рекомендаций: {e}")
            return None
    
    def _create_recommendation_prompt(self, user_preferences: str, liked_movies: Optional[List[str]] = None) -> str:
        """Создает промпт для рекомендации фильмов"""
        prompt = f"Пользователь ищет фильмы по следующим предпочтениям: {user_preferences}"
        
        if liked_movies and len(liked_movies) > 0:
            prompt += f"\n\nПользователю понравились следующие фильмы: {', '.join(liked_movies)}"
            prompt += "\n\nПожалуйста, порекомендуй фильмы, похожие по стилю и тематике на понравившиеся фильмы, учитывая его предпочтения."
        else:
            prompt += "\n\nПожалуйста, порекомендуй фильмы, соответствующие этим предпочтениям."
        
        return prompt
    
    def get_genre_based_recommendations(self, genre: str, mood: Optional[str] = None) -> Optional[str]:
        """
        Рекомендации на основе жанра и настроения
        
        Args:
            genre (str): Жанр фильмов
            mood (str, optional): Настроение/атмосфера
            
        Returns:
            Optional[str]: Рекомендации фильмов
        """
        preferences = f"жанр: {genre}"
        if mood:
            preferences += f", настроение: {mood}"
        
        return self.get_movie_recommendations(preferences)
    
    def get_mood_based_recommendations(self, mood: str, time_of_day: Optional[str] = None) -> Optional[str]:
        """
        Рекомендации на основе настроения и времени суток
        
        Args:
            mood (str): Настроение (расслабляющий, энергичный, меланхоличный и т.д.)
            time_of_day (str, optional): Время суток (вечер, выходные, обед и т.д.)
            
        Returns:
            Optional[str]: Рекомендации фильмов
        """
        preferences = f"настроение: {mood}"
        if time_of_day:
            preferences += f", время просмотра: {time_of_day}"
        
        return self.get_movie_recommendations(preferences)
    
    
    def interactive_mode(self):
        """Интерактивный режим работы"""
        print("🎬 AI Помощник по рекомендации фильмов")
        print("========================================")
        print("Доступные команды:")
        print("- 'жанр' - рекомендации по жанру")
        print("- 'настроение' - рекомендации по настроению") 
        print("- 'предпочтения' - рекомендации по описанию предпочтений")
        print("- 'стоп' - выход")
        print("=" * 50)
        
        liked_movies = []
        
        while True:
            try:
                command = input("\n🤖 Выберите команду или опишите что хотите посмотреть: ").strip().lower()
                
                if command == 'стоп':
                    print("До новых встреч! Приятного просмотра! 🍿")
                    break
                elif command == 'жанр':
                    genre = input("Введите жанр (комедия, драма, фантастика, ужасы и т.д.): ").strip()
                    mood = input("Введите настроение (необязательно): ").strip()
                    mood = mood if mood else None
                    
                    print("🤔 Думаю над рекомендациями...")
                    recommendation = self.get_genre_based_recommendations(genre, mood if mood else None)
                    
                    if recommendation:
                        print(f"\n📋 Рекомендации по жанру '{genre}':")
                        print(recommendation)
                    else:
                        print("❌ Не удалось получить рекомендации")
                        
                elif command == 'настроение':
                    mood = input("Введите настроение (расслабляющий, энергичный, меланхоличный и т.д.): ").strip()
                    time = input("Время просмотра (вечер, выходные и т.д., необязательно): ").strip()
                    time = time if time else None
                    
                    print("🤔 Думаю над рекомендациями...")
                    recommendation = self.get_mood_based_recommendations(mood, time if time else None)
                    
                    if recommendation:
                        print(f"\n📋 Рекомендации для настроения '{mood}':")
                        print(recommendation)
                    else:
                        print("❌ Не удалось получить рекомендации")
                        
                elif command == 'предпочтения':
                    preferences = input("Опишите что вы хотите посмотреть (жанры, настроение, актеры, сюжет и т.д.): ").strip()
                    liked_input = input("Фильмы, которые вам понравились (через запятую, необязательно): ").strip()
                    
                    liked_movies_list = [movie.strip() for movie in liked_input.split(',')] if liked_input else None
                    
                    print("🤔 Думаю над рекомендациями...")
                    recommendation = self.get_movie_recommendations(preferences, liked_movies_list if liked_movies_list else None)
                    
                    if recommendation:
                        print(f"\n📋 Рекомендации для вас:")
                        print(recommendation)
                    else:
                        print("❌ Не удалось получить рекомендации")
                else:
                    # Обрабатываем как свободное описание предпочтений
                    print("🤔 Думаю над рекомендациями...")
                    recommendation = self.get_movie_recommendations(command, liked_movies)
                    
                    if recommendation:
                        print(f"\n📋 Рекомендации для вас:")
                        print(recommendation)
                    else:
                        print("❌ Не удалось получить рекомендации")
                        
            except KeyboardInterrupt:
                print("\n\nДо новых встреч! Приятного просмотра! 🍿")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")


def main():
    """Главная функция"""
    # Получаем API токен из переменной окружения или просим пользователя
    api_token = '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'
    
    if not api_token:
        print("🔑 Для работы скрипта необходим API токен Openrouter")
        print("Получить токен можно на: https://openrouter.ai/keys")
        api_token = input("Введите ваш API токен: ").strip()
        
        if not api_token:
            print("❌ Токен не введен. Работа скрипта завершена.")
            return
    
    # Создаем экземпляр системы рекомендаций
    movie_recommender = MovieRecommendationOpenrouter(api_token)
    
    # Запускаем интерактивный режим
    movie_recommender.interactive_mode()


if __name__ == "__main__":
    main()