from tkinter import *
from tkinter.ttk import Combobox
import ttkbootstrap as ttk
from tkinter import messagebox
from time import time
import json

WINDOW_W = 700
WINDOW_H = 600


class TypeMachine:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")

        self.high_score = 0
        self.current_score = 0
        self.test_time = 60
        self.start_time = None
        self.word_count = 0
        self.error_count = 0
        self.current_text = ""
        self.options = ["Easy", "Medium", "Hard"]
        self.text = {}

        self.difficulty = None
        self.text_entry = None
        self.highest_score_label = None
        self.current_score_label = None
        self.text_display = None
        self.timer_label = None
        self.start_button = None
        self.confirm_button = None

        self.previous_input_correct = False

        self.setup_ui()
        self.load_highest_score()
        self.load_text()
        self.update_current_score()

    def setup_ui(self):
        style = ttk.Style('superhero')
        self.root = style.master
        self.root.config(padx=50, pady=50)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - WINDOW_W / 2)
        center_y = int(screen_height / 2 - WINDOW_H / 2)
        self.root.geometry(f'{WINDOW_W}x{WINDOW_H}+{center_x}+{center_y}')

        self.highest_score_label = Label(self.root, text="", font=("Arial", 12))
        self.highest_score_label.grid(column=0, row=0, columnspan=3, sticky=W + N, pady=20)

        self.current_score_label = Label(self.root, text="", font=("Arial", 12))
        self.current_score_label.grid(column=1, row=1, columnspan=3, pady=10)

        self.difficulty = StringVar(self.root)
        difficulty_menu = Combobox(self.root, textvariable=self.difficulty,
                                   values=self.options, state="readonly",
                                   width=10)
        self.difficulty.set("Easy")
        difficulty_menu.grid(column=1, row=2, pady=10)

        self.confirm_button = Button(self.root, text="Confirm", command=self.load_text, width=15)
        self.confirm_button.grid(column=2, row=2, pady=10)

        self.timer_label = Label(self.root, text="Timer: 60 seconds", font=("Arial", 12))
        self.timer_label.grid(column=3, row=2, pady=10)

        self.text_display = Text(self.root, font=("Arial", 16), wrap="word", height=10, width=50)
        self.text_display.grid(column=1, row=3, columnspan=3, pady=10)

        self.text_entry = Entry(self.root, font=("Arial", 16), width=50)
        self.text_entry.grid(column=1, row=4, columnspan=3, pady=10)
        self.text_entry.focus_set()

        self.start_button = Button(self.root, text="Start", command=self.start_test_event, width=15)
        self.start_button.grid(column=1, row=5, columnspan=3, pady=10)

        self.update_current_score()

        self.text_entry.bind("<Key>", lambda event: self.count_words())

    def load_text(self):
        try:
            selected_difficulty = self.difficulty.get()
            if not selected_difficulty:
                return ""

            with open("content.txt", "r", encoding="utf-8") as text_file:
                all_texts = json.load(text_file)
                for difficulty, text_data in all_texts.items():
                    if difficulty == selected_difficulty:
                        self.current_text = text_data
                        self.text_display.delete("1.0", END)
                        self.text_display.insert("1.0", self.current_text)
                        return self.current_text
                messagebox.showerror('Error', 'No text found for selected difficulty.')
                return ""
        except FileNotFoundError:
            messagebox.showerror('Error', 'No such file exists.')
            return ""

    def start_test_event(self):
        if self.difficulty:
            self.load_text()
            self.start_test()
        else:
            messagebox.showerror('Error', 'Please select a difficulty.')

    def start_test(self):
        self.start_time = time()
        self.count_words()
        self.update_current_score()
        self.update_timer_label()

    def update_current_score(self):
        self.calculate_typing_speed()
        self.current_score_label.config(text=f"Current Record: {self.current_score:.0f} words/Min")
        self.root.after(5000, self.update_current_score)
        self.calculate_typing_speed()

    def calculate_typing_speed(self):
        if self.start_time is not None:
            elapsed_time = time() - self.start_time
            if elapsed_time > 0:
                current_speed = self.word_count / elapsed_time
                self.current_score = current_speed

    def update_timer_label(self):
        remaining_time = self.test_time - (time() - self.start_time)
        seconds = max(0, int(remaining_time))
        self.timer_label.config(text=f"Timer: {seconds} seconds")
        if remaining_time > 0:
            self.root.after(1000, self.update_timer_label)
        else:
            self.count_words()
            self.show_typing_speed_message()

    def show_typing_speed_message(self):
        words_per_minute = self.word_count / self.test_time
        messagebox.showinfo('Typing Speed', f'Finished!'
                                            f'\nYour typing speed is {words_per_minute:.0f} words per minute.')

    def load_highest_score(self):
        try:
            with open('high_score.json', 'r') as f:
                self.high_score = json.load(f)
        except FileNotFoundError:
            self.high_score = 0
        self.highest_score_label.config(text=f"Highest Record: {self.high_score:.0f} words/Min")

    def update_highest_result(self):
        words_per_minute = self.word_count / self.test_time
        if words_per_minute > self.high_score:
            self.high_score = words_per_minute
            with open('high_score.json', 'w') as f:
                json.dump(self.high_score, f)
        self.highest_score_label.config(
            text=f"Typing Speed: {words_per_minute:.0f} words/Min"
                 f"\nError Count: {self.error_count}")

    def count_words(self):
        typed_text = self.text_entry.get()
        if typed_text == self.current_text[:len(typed_text)]:
            if not self.previous_input_correct:
                self.error_count = max(0, self.error_count - 1)
                self.previous_input_correct = True
        else:
            if self.previous_input_correct:
                self.previous_input_correct = False
                self.error_count += 1

        self.word_count += len(typed_text.split())
        self.update_highest_result()
