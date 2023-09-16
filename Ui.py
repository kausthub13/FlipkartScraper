import time

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView


class InputForm(BoxLayout):
    def __init__(self, **kwargs):
        super(InputForm, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.pincode_input = TextInput(hint_text="Enter Pincode")
        self.threads_input = TextInput(hint_text="Enter Number of Threads")

        self.folder_chooser = FileChooserListView()

        self.submit_button = Button(text="Submit")
        self.submit_button.bind(on_press=self.on_submit)

        self.add_widget(self.pincode_input)
        self.add_widget(self.threads_input)
        self.add_widget(self.folder_chooser)
        self.add_widget(self.submit_button)

    def on_submit(self, instance):
        pincode = self.pincode_input.text
        threads = self.threads_input.text
        folder_path = self.folder_chooser.path

        # You can use these values outside of the application.
        # For example, print them to the console:
        print(f"Pincode: {pincode}, Threads: {threads}, Folder: {folder_path}")

        # Close the application
        App.get_running_app().stop()


class MyApp(App):
    def build(self):
        return InputForm()


if __name__ == '__main__':
    MyApp().run()
    print('He')
    time.sleep(100)