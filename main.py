import tkinter as tk
from tkinter import ttk
import pandas as pd
from samples import SampleTexts

# Constants for widget padding
XPAD = 5
YPAD = 5

# Access Sample Texts
sample_texts = SampleTexts()

# Access high scores
high_score_df = pd.read_csv("./high_scores.csv")


# Window to select sample text and start test
class SelectWindow:

    def __init__(self, master):
        self.master = master

        # Welcome message
        self.select_label = tk.Label(self.master, text="Welcome to the Typing Speed Test.\nSelect which sample text you"
                                                       " would like to type:")
        self.select_label.grid(column=0, row=0, padx=XPAD, pady=YPAD)

        # Combobox to select a sample text to type
        self.select_var = tk.StringVar()
        self.select_box = ttk.Combobox(self.master, textvariable=self.select_var, width=25)
        self.select_box["values"] = ["Lizards", "Pride and Prejudice", "The Waste Land"]
        self.select_box.current(0)
        self.select_box.state(["readonly"])
        self.select_box.grid(column=0, row=1, padx=XPAD, pady=YPAD)

        # Name entry
        self.name_label = tk.Label(self.master, text="Please enter your name.")
        self.name_label.grid(column=0, row=3, padx=XPAD, pady=YPAD)
        self.name_entry = tk.Entry(self.master)
        self.name_entry.grid(column=0, row=4, padx=XPAD, pady=YPAD)

        # Instructions label
        self.intro_label = tk.Label(self.master, text="Once you press 'Go' you will have 60 seconds to type the text on"
                                                      "screen.\nTry to type as quickly and accurately as possible.\n"
                                                      "Good luck!")
        self.intro_label.grid(column=0, row=5, padx=XPAD, pady=YPAD)

        # Go button
        self.go_btn = tk.Button(self.master, text="Go!", command=self.start_test)
        self.go_btn.grid(column=0, row=6, padx=XPAD, pady=YPAD)

    def start_test(self):
        """Starts the typing test in a new window"""
        self.test_window = tk.Toplevel(self.master)
        self.sample = sample_texts.texts[self.select_box.get()]
        self.app = TestWindow(self.test_window, self.sample)
        self.master.after(60000, self.app.end_test)


class TestWindow:

    def __init__(self, master, text):

        # Set up the window
        self.master = master
        self.text = text
        self.master.title("Typing Speed Test")
        self.master.minsize(width=1000, height=1000)
        self.master.config(padx=20, pady=20)

        # Display the sample text in a frame
        self.text_frame = tk.Frame(self.master)
        self.text_frame.grid(column=0, row=0, padx=XPAD, pady=YPAD)
        self.sample_text = tk.Label(self.text_frame, wraplength=960, text=self.text)
        self.sample_text.grid(column=0, row=0, padx=XPAD, pady=YPAD)

        # Create a text entry field in a frame
        self.entry_frame = tk.Frame(self.master)
        self.entry_frame.grid(column=0, row=1, padx=XPAD, pady=YPAD)
        self.entry = tk.Text(self.entry_frame, width=75, height=18)
        self.entry.grid(column=0, row=0, padx=XPAD, pady=XPAD)
        self.entry.focus_set()

    def end_test(self):
        """Provides results in a new window at the end of the test"""
        user_input = self.entry.get("1.0", tk.END)
        self.results_window = tk.Toplevel(self.master)
        self.results_window.minsize(height=200, width=200)
        self.app = ResultsWindow(self.results_window, user_input, self.text)


# Create a window to display the test results
class ResultsWindow:
    def __init__(self, master, user_text, sample_text):
        self.master = master

        # Calculate typing speed
        self.user_text = user_text
        self.speed = round(len(user_text) / 5, 2)

        # Number of errors
        self.sample_text = sample_text
        self.user_word_list = user_text.replace("\n", " ").split(" ")
        self.sample_word_list = self.sample_text.replace("\n", " ").split(" ")
        self.error_total = self.calculate_errors()
        self.accuracy = round(((1 - (self.error_total / len(self.user_word_list))) * 100), 2)

        # Check high scores and prepare high scores for display
        self.name = app.name_entry.get()
        self.has_high_score = self.check_scores()
        self.score_df = self.update_scores()
        self.names_list = [name for name in self.score_df["Name"]]
        self.names_text = "\n".join(self.names_list)
        self.speed_list = [str(speed) for speed in self.score_df["Speed"]]
        self.speed_text = "\n".join(self.speed_list)
        self.accuracy_list = [str(accuracy) for accuracy in self.score_df["Accuracy"]]
        self.accuracy_text = "\n".join(self.accuracy_list)

        # Display results
        self.results_label = tk.Label(self.master, text=f"You typed {self.speed} wpm with {self.error_total} error(s)"
                                                        f" for {self.accuracy}% accuracy.")
        self.results_label.grid(column=0, row=0, padx=XPAD, pady=YPAD)
        if self.has_high_score:
            self.high_score_label = tk.Label(self.master, text="Congratulations! You earned a high score!")
            self.high_score_label.grid(column=0, row=1, padx=XPAD, pady=YPAD)
        self.high_score_button = tk.Button(self.master, text="View High Scores", command=self.display_high_scores)
        self.high_score_button.grid(column=0, row=2, padx=XPAD, pady=YPAD)

    def calculate_errors(self):
        """Calculates the number of errors"""
        error_words = []
        for i in range(0, len(self.user_word_list)):
            if self.user_word_list[i] != self.sample_word_list[i]:
                error_words.append(self.sample_word_list[i])
        num_errors = len(error_words)
        return num_errors

    def update_scores(self):
        """Updates high score list"""
        if self.has_high_score:
            new_score = [self.name, self.speed, self.accuracy]
            new_row_df = pd.DataFrame([new_score], columns=high_score_df.columns)
            new_df = pd.concat([high_score_df, new_row_df])
            scores_sorted = new_df.sort_values(by=["Speed", "Accuracy"], ascending=False)
            sorted_df = scores_sorted.drop(scores_sorted.index[10:])
            sorted_df.to_csv("./high_scores.csv", index=False)
            return sorted_df
        else:
            return high_score_df

    def check_scores(self):
        """Checks if current score is a top 10 high score"""
        min_score = high_score_df["Speed"].min()
        if self.speed > min_score:
            return True
        elif self.speed == min_score and self.accuracy > high_score_df.query("Speed == min_score")["Accuracy"]:
            return True
        else:
            return False

    def display_high_scores(self):
        """Opens new window to show high scores"""
        self.scores_window = tk.Toplevel(self.master)
        self.scores_window.minsize(height=500, width=400)
        self.app = ScoresWindow(self.scores_window, self.names_text, self.speed_text, self.accuracy_text)


# Displays high scores in a new window
class ScoresWindow:

    def __init__(self, master, names, speeds, accuracies):

        # Create variables for passed arguments
        self.master = master
        self.names = names
        self.speeds = speeds
        self.accuracies = accuracies

        # Displays high score lists
        self.title_label = tk.Label(self.master, text="High Scores")
        self.title_label.grid(column=1, row=0, padx=XPAD, pady=20)
        self.names_header = tk.Label(self.master, text="Name")
        self.names_header.grid(column=0, row=1, padx=XPAD, pady=YPAD)
        self.speed_header = tk.Label(self.master, text="Speed")
        self.speed_header.grid(column=1, row=1, padx=XPAD, pady=YPAD)
        self.accuracy_header = tk.Label(self.master, text="Accuracy")
        self.accuracy_header.grid(column=2, row=1, padx=XPAD, pady=YPAD)
        self.names_label = tk.Label(self.master, text=self.names)
        self.names_label.grid(column=0, row=2, padx=XPAD, pady=YPAD)
        self.speed_label = tk.Label(self.master, text=self.speeds)
        self.speed_label.grid(column=1, row=2, padx=XPAD, pady=YPAD)
        self.accuracy_label = tk.Label(self.master, text=self.accuracies)
        self.accuracy_label.grid(column=2, row=2, padx=XPAD, pady=YPAD)


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = SelectWindow(root)
    root.title("Test Your Typing Speed!")
    root.minsize(width=500, height=500)
    root.config(padx=20, pady=20)
    root.mainloop()
