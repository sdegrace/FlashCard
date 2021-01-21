import tkinter as tk
from PIL import Image, ImageTk
from random import choices, choice, shuffle
from functools import partial
from os.path import isdir, isfile
from os import listdir


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

class Quiz(tk.Frame):

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Return>", self.check_answer)
        self.image_categories = []
        self.category_weights = []
        for name in listdir('.'):
            if isdir(name) and name[0] != '.' and name != 'default_image':
                if not isfile('./' + name + '/score.txt'):
                    with open('./' + name + '/score.txt', 'w') as file:
                        file.write(str(5))
                    self.image_categories.append(name)
                    self.category_weights.append(5)
                else:
                    with open('./' + name + '/score.txt') as file:
                        score = file.read()
                        score = int(score)
                    self.image_categories.append(name)
                    self.category_weights.append(score)

        self.given_answer = tk.StringVar()
        self.load_images()
        self.build_question_type_selector()
        self.build_question_answer_container()
        self.build_question_panel()
        self.build_answer_panel()
        self.pack()
        self.choose_next_question()

    def on_closing(self):
        for item, score in zip(self.image_categories, self.category_weights):
            with open('./' + item + '/score.txt', 'w') as file:
                file.write(str(score))
        root.destroy()

    def load_images(self):
        path = './default_image/default_image.png'
        load = Image.open(path)
        self.default_image = ImageTk.PhotoImage(load)

        path = './default_image/correct.png'
        load = Image.open(path)
        self.correct_image = ImageTk.PhotoImage(load)

        path = './default_image/incorrect.png'
        load = Image.open(path)
        self.incorrect_image = ImageTk.PhotoImage(load)

    def build_question_type_selector(self):
        self.question_type_selector_frame = tk.Frame(master=self)
        self.question_type_selector_frame.pack(side=tk.LEFT)

    def build_question_answer_container(self):
        self.question_answer_frame = tk.Frame(master=self)
        self.question_answer_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

    def build_question_panel(self):
        self.question_frame = tk.Frame(master=self.question_answer_frame)
        self.image = tk.Label(master=self.question_frame, image=self.default_image)
        self.image.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.question_prompt = tk.StringVar()
        self.question_prompt.set("Loading...")
        tk.Label(master=self.question_frame, textvariable=self.question_prompt).pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.question_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def build_answer_panel(self):
        self.answer_frame = tk.Frame(master=self.question_answer_frame)
        self.answer_frame.pack(side=tk.BOTTOM)

    @staticmethod
    def get_image(name):
        assert isdir(name)
        options = [option for option in listdir(name) if option[-3:] != 'txt']
        image = Image.open('./' + name + '/' + choice(options))
        image = ImageTk.PhotoImage(image)
        return image

    def get_random_name_and_image(self):
        name = choices(self.image_categories, self.category_weights)[0]
        image = self.get_image(name)
        return name, image

    def check_answer(self, e=None):
        if self.given_answer.get() == self.true_answer:
            i = self.image_categories.index(self.true_answer)
            self.category_weights[i] = max(1, self.category_weights[i] - 1)
            self.image.configure(image=self.correct_image)
            self.given_answer.set('')
            self.root.update()
            self.after(1500)
            self.choose_next_question()
        else:
            self.image.configure(image=self.incorrect_image)
            i = self.image_categories.index(self.true_answer)
            self.category_weights[i] = min(5, self.category_weights[i] + 1)
            self.given_answer.set('')
            self.root.update()
            self.after(1500)
            self.choose_next_question()
        print(self.image_categories)
        print(self.category_weights)
    def choose_next_question(self):
        question_funcs = [self.multiple_choice_question, self.freeform_question]
        question = choice(question_funcs)
        question()

    def freeform_question(self):
        name, image = self.get_random_name_and_image()
        self.true_answer = name
        self.question_prompt.set("Please enter the answer below...")
        self.image.configure(image=image)
        self.image.image = image
        clear_frame(self.answer_frame)

        tk.Entry(master=self.answer_frame, textvariable=self.given_answer).pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        tk.Button(master=self.answer_frame, text='Check Answer', command=self.check_answer).pack(side=tk.LEFT, fill=tk.BOTH)

    def set_answer(self, answer):
        self.given_answer.set(answer)
        self.check_answer()

    def multiple_choice_question(self):
        name, image = self.get_random_name_and_image()
        self.true_answer = name
        self.question_prompt.set('Choose the correct item...')
        self.image.configure(image=image)
        self.image.image = image
        clear_frame(self.answer_frame)

        options = choices([item for item in self.image_categories if item != self.true_answer], k=3) + [self.true_answer]
        for option in options:
            tk.Button(master=self.answer_frame, text=option, command=partial(self.set_answer, option)).pack(side=tk.LEFT)

root = tk.Tk()
# root.geometry("640x480+300+300")
app = Quiz(root)
root.mainloop()