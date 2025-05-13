# QUIZZESHERE

+ [Основная информация](#основная-информация)
+ [Доступные возможности](#доступные-возможности)
    + [Список реализованных вещей ](#Список-доступных-вещей)
    + [Квизы](#квизы)
        + [Создание](#создание)
        + [Управление](#управление)
        + [Решение](#решение)
        + [После прохождение](#после-прохождения)
    + [Меню](#меню)
+ [О проекте](#о-проекте)
    + [Пример кода](#пример-кода)
    + [Авторы](#авторы)

---

## Основная информация

QUIZZESHERE - *Эдьютейнмен* (образовательно-развлекательный) сервис квизов (викторин).   
[![Python](https://img.shields.io/badge/Python-3.9-gold?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-red?style=for-the-badge&logo=SQLAlchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Flask](https://img.shields.io/badge/Flask-blue?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/en/stable/)
[![Bootsrtap](https://img.shields.io/badge/Bootstrap-blue?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)



-----

## Доступные возможности

### Список доступных вещей

+ Форма регистрации аккаунта, входа в аккаунт
+ Главное меню
+ Профиль
+ О нас
+ Создание квиза
+ Выбор квиза
+ Прохождение квиза
+ Показ результатов

---

### Квизы

#### Создание

Для создания нужно указать следующее: название, описание, тема и приложить обложку (фото). Далее, нужно добавить
необходимое
количество вопросов. В каждом вопросе нужно добавить: сам вопрос, приложить поясняющее фото, добавить 2-4 варианта
ответов
и выбрать правильный вариант.

#### Управление

До публикации квиза, все сохраненные данные остаются в виде черновика. Имеется возможность вернуться позже к его
созданию.
В любой момент можно удалить свой квиз.

#### Решение

Решение квиза представляет собой интуитивно понятную конструкцию. Человек выбирает подходящий, по его мнению, ответ
нажатием на него.

#### После прохождения

Человек должен оценить пройденный квиз (только при первом прохождении). Затем, будет показана таблица состоящая из
ответа человека (красный - неправильный ответ, зелёный - правильный), правильного ответа и баллов поставленных за ответ.
А также общая информация о квизе.    

---

### Меню

+ Из меню можно попасть в любую часть сайта.
+ Используя гипперссылки в шапке можно попасть в профиль (профиль, логин, регистрация), "о нас", главное меню
+ Нажав на большой плюс можно попасть на форму составления квиза
+ В поиск может быть введен id квиза - прямое переопределение на квиз или какая-либо часть его названия,
  тогда человек попадет на страницу поиска
+ Следующий блок - [рекомендации](#пример-кода). Они составляются на основе пройденных квизов ранее
+ Далее расположились топы квизов по рейтингу за месяц и неделю. В него попадают квизы имеющие наибольший рейтинг
  за определенный момент времени, которые прошли хотя бы два человека  
  P.S: Все названия квизов - кликабельны

---

## О проекте

Данный проект был сделан в ходе обучения в [**Яндекс лицее**](https://lyceum.yandex.ru/)

### Пример кода

В примере ниже, мы составляем рекомендацию человеку исходя из его интересов   
Находим самые популярны темы у человека (по количеству прохождений) и составляем список не пройденных квизов с такой же
темой. Если не пройденных квизов данной темы нет, то берем вторую по прохождению и так далее
recommendation_main_theme - объект класса ```InfTempl```

``` python
class InfTempl:
    def __init__(self):
        self.title = 'Нет такой информации'
        self.photo = '../static/quizzes/test.jpg'
        self.theme = 'Отсутствует'
        self.rating = -1
        self.id = 0

    def update(self, title, theme='Отсутствует', photo='../static/quizzes/test.jpg', rating=-1, id=0):
        self.title = title.capitalize()
        self.theme = theme.capitalize()
        self.photo = photo
        self.rating = rating
        self.id = id
```

``` python
complited = db_sess.query(association_table_passage).filter_by(users=current_user.id)
if complited:
    complited_quizzes = list(map(lambda x: x.quizzes, complited))
    all_themes = [db_sess.query(Quiz).get(id).themes[0].name for id in complited_quizzes]
    for el in sorted(list(set(all_themes)), key=lambda x: all_themes.count(x), reverse=True):
        res_list = list(
            filter(
                lambda x: x.themes[0].name == el and x.id not in complited_quizzes,
                db_sess.query(Quiz).all()
            )
        )
        if res_list:
            result = choice(res_list)
            recommendation_main_theme.update(
                title=result.name, theme=result.themes[0].name, rating=round(result.rating, 1), id=result.id
            )
            break
   ```         

### Авторы

[**CHERT (Ilya)**](https://github.com/CHERTvsINTERNET) и [**DIVERSIUM (Konstantin)**](https://github.com/DIVERSIUMx)