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