from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.lang import Builder
from math import radians, sin, degrees, asin
from kivy.uix.textinput import TextInput


class TabNavigableInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_widget = None

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'tab' and self.parent_widget:
            Clock.schedule_once(lambda dt: self.parent_widget.handle_tab(self), 0.05)
            return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class IncrementalWidget(BoxLayout):
    def __init__(self, **kwargs):
        Builder.load_file("incremental_widget.kv")
        super().__init__(**kwargs)
        Clock.schedule_once(self._delayed_init)

    def _delayed_init(self, *args):
        self.points = []
        self.add_point()

    def handle_tab(self, instance):
        for row_index, row in enumerate(self.points):
            inputs = [row['time'], row['incl'], row['speed'], row['asc']]
            if instance in inputs:
                current_index = inputs.index(instance)
                if current_index < len(inputs) - 1:
                    inputs[current_index + 1].focus = True
                else:
                    if row_index + 1 < len(self.points):
                        self.points[row_index + 1]['time'].focus = True
                    else:
                        self.add_point()
                        Clock.schedule_once(lambda dt: setattr(self.points[-1]['time'], 'focus', True), 0.05)
                break

    def add_point(self):
        grid = self.ids.points_grid

        ti_time = TabNavigableInput(hint_text='s', multiline=False, input_filter='float')
        ti_incl = TabNavigableInput(hint_text='°', multiline=False, input_filter=None)
        ti_speed = TabNavigableInput(hint_text='km/h', multiline=False, input_filter=None)
        ti_asc = TabNavigableInput(hint_text='m/h', multiline=False, input_filter=None)

        for ti in [ti_time, ti_incl, ti_speed, ti_asc]:
            ti.parent_widget = self

        btn = Button(text="Supprimer", size_hint_x=None, width=100)

        row = {'time': ti_time, 'incl': ti_incl, 'speed': ti_speed, 'asc': ti_asc, 'btn': btn}
        self.points.append(row)

        def remove_row(instance):
            for widget in [ti_time, ti_incl, ti_speed, ti_asc, btn]:
                grid.remove_widget(widget)
            self.points.remove(row)

        def on_change(instance, value):
            self.recalculate(row)

        for widget in [ti_time, ti_incl, ti_speed, ti_asc]:
            widget.bind(text=on_change)

        btn.bind(on_press=remove_row)

        for widget in [ti_time, ti_incl, ti_speed, ti_asc, btn]:
            grid.add_widget(widget)

    
    
    
    def recalculate(self, row):
        def parse(text):
            try:
                return float(text)
            except:
                return None

        v_text = row['speed'].text.strip().lower()
        i_text = row['incl'].text.strip().lower()
        a_text = row['asc'].text.strip().lower()

        is_nc = lambda txt: txt == 'nc'

        v = None if is_nc(v_text) else parse(v_text)
        i = None if is_nc(i_text) else parse(i_text)
        a = None if is_nc(a_text) else parse(a_text)

        # Réinitialiser tous les champs à éditables et fond blanc
        for field in [row['incl'], row['speed'], row['asc']]:
            field.readonly = False
            field.background_color = (1, 1, 1, 1)

        # Si champ marqué 'nc', alors le calculer, verrouiller et griser
        if is_nc(a_text) and v is not None and i is not None:
            a_calc = v * sin(radians(i))
            row['asc'].text = f"{a_calc:.2f}"
            row['asc'].readonly = True
            row['asc'].background_color = (0.7, 0.7, 0.7, 1)

        elif is_nc(v_text) and a is not None and i is not None and sin(radians(i)) != 0:
            v_calc = a / sin(radians(i))
            row['speed'].text = f"{v_calc:.2f}"
            row['speed'].readonly = True
            row['speed'].background_color = (0.7, 0.7, 0.7, 1)

        elif is_nc(i_text) and a is not None and v is not None and v != 0:
            try:
                i_calc = degrees(asin(a / v))
                row['incl'].text = f"{i_calc:.2f}"
                row['incl'].readonly = True
                row['incl'].background_color = (0.7, 0.7, 0.7, 1)
            except:
                pass
