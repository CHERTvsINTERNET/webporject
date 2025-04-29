class InfTempl:
    def __init__(self):
        self.title = 'Нет такой информации'
        self.photo = '../static/quizzes/test.jpg'
        self.theme = 'Отсутствует'

    def update(self, title, theme='Отсутствует', photo='../static/quizzes/test.jpg'):
        self.title = title.capitalize()
        self.theme = theme.capitalize()
        self.photo = photo
