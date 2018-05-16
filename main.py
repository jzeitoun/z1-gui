from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', '550')
Config.set('graphics', 'height', '240')
Config.set('kivy', 'exit_on_escape', 0)
#Config.set('kivy', 'default_font', [
#    'Avenir-Light',
#    '/Users/blakjak/Library/Fonts/Avenir-Light.ttf', # regular
#    '/Users/blakjak/Library/Fonts/Avenir-LightOblique.ttf', # italic
#    '/Users/blakjak/Library/Fonts/Avenir-Book.ttf', # bold
#    '/Users/blakjak/Library/Fonts/Avenir-BookOblique.ttf', # bold-italic
#])

from kivy.app import App
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty, ListProperty, StringProperty, \
    ReferenceListProperty, BooleanProperty, ObjectProperty
from kivy.graphics import Rectangle, Color
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.animation import Animation

# Add hover behavior
from hoverable import HoverBehavior
from kivy.factory import Factory
Factory.register('HoverBehavior', HoverBehavior)

from functools import partial

import time
import sys
import os

from plyer import filechooser

if sys.version_info[0] < 3:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser

_ROOT = '/Users/blakjak/Desktop'

secondary_color = [20/255.0, 20/255.0, 19/255.0, 1]
dropdown_highlight = [1, 1, 1, 0.15]
text_color = [1, 1, 1, 1]
match_color = [61/255.0, 192/255.0, 244/255.0, 1]

_box = '''
#: set secondary_color [20/255.0, 20/255.0, 19/255.0, 1]
BoxLayout:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_size[1]
    canvas.before:
        Color:
            rgba: secondary_color
        Rectangle:
            pos: self.pos
            size: self.size
'''

#def get_root_widget(widget):
#    '''
#    Recursive function to get the root widget from within any child widget.
#    '''
#    if isinstance(widget, RootWidget):
#        return widget
#    elif isinstance(widget, type(Window)):
#        for child in widget.children:
#            if isinstance(child, RootWidget):
#                return child
#        return None
#    else:
#        return get_root_widget(widget.parent)

class ProfileService(EventDispatcher):
    '''
    Simple service for managing profiles.
    '''

    active_profile = StringProperty('')
    profiles = ListProperty([])

    left_488 = NumericProperty(0)
    right_488 = NumericProperty(0)
    left_405 = NumericProperty(0)
    right_405 = NumericProperty(0)
    left_561 = NumericProperty(0)
    right_561 = NumericProperty(0)
    left_638 = NumericProperty(0)
    right_638 = NumericProperty(0)

    saved_offsets = ListProperty([])
    applied_offsets = ListProperty([])
    current_offsets = ReferenceListProperty(
            left_488, right_488, left_405, right_405, left_561, right_561,
            left_638, right_638
            )

    def __init__(self, path, initial_profile='default', **kwargs):
        super(ProfileService, self).__init__(**kwargs)
        self._path = self._ensure_file(path)
        self._config = ConfigParser()
        self._config.read(self._path)
        self.set_profile(initial_profile)
        self.profiles = filter(lambda x: 'file_path' not in x, self._config.sections())

    @property
    def parameters(self):
        keys = list(
            filter(
                lambda attr: attr.startswith('left_') or attr.startswith('right_'), dir(self)
                )
            )
        return {key: getattr(self, key) for key in keys}

    def _ensure_file(self, path):
        if not os.path.isfile(path):
            open(path, 'w').close()
        return path

    def set_profile(self, section):
        if hasattr(section, 'text'):
            section = section.text
        self.active_profile = section
        for item in self._config.items(section):
            param,val = item
            setattr(self, param, round(float(val), 6))
        self.saved_offsets = self.current_offsets

    def save_profile(self, widget=None):
        print('Profile saved.')
        #self.saved_offsets = self.current_offsets
        for param,val in self.parameters.items():
            self._config.set(self.active_profile, param, str(val))
        with open(self._path, 'r+') as f:
            self._config.write(f)

    def add_profile(self, widget):
        section = widget.text
        if section in self._config.sections():
            return
        self.profiles.append(section)
        self._config.add_section(section)
        for param,val in self.parameters.items():
            self._config.set(section, param, str(val))
        self.save_profile()
        self.set_profile(section)

    def delete_profile(self, section):
        self._config.remove_section(section)
        self.save_profile()

class RootWidget(Widget):

    profile_service = ObjectProperty(
            ProfileService(os.path.join(_ROOT, 'z1_profiles.cfg'))
            )
    file_path = StringProperty('')

    def setup(self):
        self.dropdown = CustomDropDown(
                id='profile_dropdown', container=Builder.load_string(_box),
                max_height=150
                )
        self.dropdown_button = self.ids.dropdown_button
        self.profile_input = NewProfileInput(id='profile_input')
        self.profile_input.ids.child.bind(focus=self.focus_change)
        self.profile_input.ids.child.bind(on_text_validate=self.profile_service.add_profile)
        self.ids.directory_button.bind(on_release=self.select_directory)
        self.ids.apply_button.bind(on_release=self.apply_offsets)
        self.ids.save_button.bind(on_release=self.save_profile)
        for param,val in self.profile_service.parameters.items():
            self.ids[param].value = round(val, 6)
            self.ids[param].bind(value=self.profile_service.setter(param))
            self.profile_service.bind(**{param: self.ids[param].setter('value')})
        self.profile_service.bind(current_offsets=self.check_saved_status)
        self.profile_service.bind(saved_offsets=self.check_saved_status)
        self.check_saved_status()
        self.profile_service.bind(current_offsets=self.check_applied_status)
        self.profile_service.bind(profiles=self.update_dropdown)
        self.profile_service.bind(active_profile=self.change_profile)
        self.update_dropdown(self.profile_service.profiles, initial=True)
        create_profile_button = DropDownOption(id='CREATE', text='Create new profile...', height=25,
            image_source="plus.png")
        create_profile_button.bind(on_release=self.create_profile)
        self.dropdown.add_widget(create_profile_button)
        if 'file_path' in self.profile_service._config.sections():
            self.file_path = self.profile_service._config.get('file_path', 'value')


    @property
    def current_dropdown_widgets(self):
        return {widget.id: widget for widget in self.dropdown.children[0].children if hasattr(widget, 'id')}

    def update_dropdown(self, *largs, **kwargs):
        index = 0 if 'initial' in kwargs else 1
        if len(largs) > 1:
            instance, largs = largs
        else:
            largs = largs[0]
        for widget_id in self.current_dropdown_widgets.keys():
            if not widget_id in largs and widget_id is not 'CREATE':
                self.dropdown.remove_widget(self.current_dropdown_widgets[widget_id])
        for item in largs:
            if not item in self.current_dropdown_widgets.keys():
                new_item = DropDownOption(id=item, text=item, height=25)
                new_item.bind(on_release=self.profile_service.set_profile)
                self.dropdown.add_widget(new_item, index)

    def create_profile(self, widget):
        self.ids.dropdown_holder.remove_widget(self.dropdown_button)
        self.ids.dropdown_holder.add_widget(self.profile_input)
        self.profile_input.ids.child.focus = True
        self.dropdown.dismiss()

    def change_profile(self, instance, *args):
        self.ids.dropdown_holder.remove_widget(self.profile_input)
        if not self.dropdown_button.parent:
            self.ids.dropdown_holder.add_widget(self.dropdown_button)
        self.dropdown.dismiss()
        self.changed_profile = True

    def save_profile(self, widget):
        self.profile_service.saved_offsets = self.profile_service.current_offsets
        self.ids.save_button.ids.icon.color = match_color
        self.profile_service.save_profile()

    def focus_change(self, instance, focus):
        if not focus and not self.changed_profile:
            self.change_profile(None)
        self.changed_profile = False

    def select_directory(self, widget):
        widget.on_leave() # Prevent bubble from showing
        path_list = filechooser.choose_dir()
        if path_list:
            self.file_path = path_list[0]
        if not self.file_path:
            widget.ids.icon.color = text_color
        else:
            widget.ids.icon.color = match_color
        if not 'file_path' in self.profile_service._config.sections():
            self.profile_service._config.add_section('file_path')
        self.profile_service._config.set('file_path', 'value', self.file_path)
        self.profile_service.save_profile()

    def apply_offsets(self, widget):
        self.profile_service.applied_offsets = self.profile_service.current_offsets
        if not self.file_path == '':
            widget.ids.icon.color = match_color
            with open(os.path.join(self.file_path, 'LightsheetOffsetDefault.txt'), 'w') as f:
                f.writelines([
                        "'Light sheet base offset in Z :\n",
                        "'Wavelength\tOffset Left\tOffset Right\n",
                         '\t488\t' + str(self.profile_service.left_488) + '\t' + str(self.profile_service.right_488) + '\n',
                         '\t405\t' + str(self.profile_service.left_405) + '\t' + str(self.profile_service.right_405) + '\n',
                         '\t561\t' + str(self.profile_service.left_561) + '\t' + str(self.profile_service.right_561) + '\n',
                         '\t638\t' + str(self.profile_service.left_638) + '\t' + str(self.profile_service.right_638) + '\n',
                        ])
        else:
            widget.ids.icon.color = text_color

    def check_applied_status(self, *widget):
        print('Checked applied status')
        if self.profile_service.applied_offsets == self.profile_service.current_offsets:
            self.ids.apply_button.ids.icon.color = match_color
        else:
            self.ids.apply_button.ids.icon.color = text_color

    def check_saved_status(self, *widget):
        print('{} = {}'.format(
            self.profile_service.saved_offsets,
            self.profile_service.current_offsets
            )
            )
        if self.profile_service.saved_offsets == self.profile_service.current_offsets:
            self.ids.save_button.ids.icon.color = match_color
        else:
            self.ids.save_button.ids.icon.color = text_color

    def on_file_path(self, instance, *args):
        print('File change detected.')
        if self.file_path:
            self.ids.directory_button.ids.icon.color = match_color



class HintButton(HoverBehavior, Button):

    bubbles = False

    image_source = StringProperty('')
    bubble_text = StringProperty('')
    arrow_pos = StringProperty('')

    def on_enter(self):
        if hasattr(type(self), 'hide_countdown'):
            type(self).hide_countdown.cancel()
        if type(self).bubbles:
            self.show_bubble()
        else:
            type(self).show_countdown = Clock.schedule_once(self.show_bubble, 1)

    def on_leave(self):
        if hasattr(type(self), 'show_countdown'):
            type(self).show_countdown.cancel()
        type(self).hide_countdown = Clock.schedule_once(self.hide_bubble, 1)
        self.ids.bubble.opacity = 0

    def show_bubble(self, *args):
        type(self).bubbles = True
        self.ids.bubble.opacity = 1

    def hide_bubble(self, *args):
        type(self).bubbles = False

class DropDownButton(ButtonBehavior, BoxLayout): pass

class NewProfileInput(BoxLayout): pass

class CustomDropDown(DropDown):

    def open(self, widget):
        '''Open the dropdown list and attach it to a specific widget.
        Depending on the position of the widget within the window and
        the height of the dropdown, the dropdown might be above or below
        that widget.
        '''
        # ensure we are not already attached
        if self.attach_to is not None:
            self.dismiss()

        # we will attach ourself to the main window, so ensure the
        # widget we are looking for have a window
        self._win = widget.get_parent_window()
        if self._win is None:
            raise DropDownException(
                'Cannot open a dropdown list on a hidden widget')

        self.attach_to = widget
        widget.bind(pos=self._reposition, size=self._reposition)
        self._reposition()


        # attach ourself to the main window and ensure opacity is 0
        self.opacity = 0
        self._win.add_widget(self)

        open_animation = Animation(opacity=1, duration=.1)
        open_animation.start(self)

class DropDownOption(ButtonBehavior, HoverBehavior, BoxLayout):

    text = StringProperty('')
    image_source = StringProperty('')
    icon = BooleanProperty(False)

    def on_enter(self):
        with self.canvas.before:
            Color(*dropdown_highlight)
            Rectangle(pos=self.pos, size=self.size)

    def on_leave(self):
        with self.canvas.before:
            Color(*secondary_color)
            Rectangle(pos=self.pos, size=self.size)

class OffsetInput(BoxLayout):

    precision = NumericProperty(2)
    value = NumericProperty(None)

    def start_press(self, method):
        Clock.schedule_once(eval(method)) # run once on initial click
        self.long = Clock.schedule_once(partial(self.long_press, method), .3) # schedule long press

    def long_press(self, method, dt):
        self.event = Clock.schedule_interval(eval(method), .1)

    def end_press(self):
        if hasattr(self, 'long'):
            self.long.cancel()
            self.__delattr__('long')
        if hasattr(self, 'event'):
            self.event.cancel()
            self.__delattr__('event')

    def increment(self, dt):
        new_value = self.value + 1.0/10**self.precision
        self.value = round(new_value, 6)

    def decrement(self, dt):
        new_value = self.value - 1.0/10**self.precision
        self.value = round(new_value, 6)


class MainApp(App):

    def build(self):
        root = RootWidget()
        root.setup()
        return root


if __name__ == '__main__':
    MainApp().run()
