from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.widget import Widget
import cv2

# Constants for distance estimation
KNOWN_DISTANCE = 50.0  # Assumed distance in cm
KNOWN_WIDTH = 14.0     # Average face width in cm
WARNING_DISTANCE = 30.0  # Threshold distance for warning

# Function to calculate focal length dynamically
def calculate_focal_length(known_distance, known_width, measured_width):
    return (measured_width * known_distance) / known_width

# Function to calculate distance
def calculate_distance(focal_length, object_width_in_frame):
    return (KNOWN_WIDTH * focal_length) / object_width_in_frame

class MainMenu(BoxLayout):
    def __init__(self, switch_mode_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20

        with self.canvas.before:
            Color(0.078, 0.129, 0.239, 1)
            
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        title = Label(text="Select Mode", font_size='24sp', bold=True, color=(1, 1, 1, 1))
        self.add_widget(title)

        distance_mode_button = Button(text="Distance Mode", font_size='18sp', size_hint=(1, 0.2))
        distance_mode_button.bind(on_press=lambda x: switch_mode_callback('distance'))
        self.add_widget(distance_mode_button)

        eye_mode_button = Button(text="Eye Blink Detection", font_size='18sp', size_hint=(1, 0.2))
        eye_mode_button.bind(on_press=lambda x: switch_mode_callback('eye'))
        self.add_widget(eye_mode_button)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

class DistanceMode(BoxLayout):
    def __init__(self, go_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        self.go_back_callback = go_back_callback

        with self.canvas.before:
            Color(0.078, 0.129, 0.239, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Header Section
        header = BoxLayout(size_hint_y=0.1, padding=5, spacing=5)
        title_label = Label(text="Distance Measurement Mode", font_size='24sp', bold=True, color=(1, 1, 1, 1))
        header.add_widget(title_label)
        self.add_widget(header)

        # Camera feed display
        self.image = Image(size_hint_y=0.7)
        self.add_widget(self.image)

        # Warning label
        self.warning_label = Label(text="", font_size='20sp', color=(1, 0, 0, 1), size_hint_y=0.1)
        self.add_widget(self.warning_label)

        # Initialize OpenCV video capture
        self.capture = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.focal_length = None

        # Footer Section with Buttons
        footer = BoxLayout(size_hint_y=0.1, padding=5, spacing=5)
        back_button = Button(text="Back", size_hint_x=0.3, background_color=(0.89, 0.89, 0.89, 1), font_size='18sp')
        back_button.bind(on_press=self.on_go_back)
        footer.add_widget(Widget())  # Spacer
        footer.add_widget(back_button)
        footer.add_widget(Widget())  # Spacer
        self.add_widget(footer)

        # Schedule updates for the camera feed
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def update_frame(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        warning_displayed = False

        for (x, y, w, h) in faces:
            # Draw rectangle around detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Calculate focal length dynamically if not set
            if self.focal_length is None:
                self.focal_length = calculate_focal_length(KNOWN_DISTANCE, KNOWN_WIDTH, w)

            # Calculate distance
            distance = calculate_distance(self.focal_length, w)
            cv2.putText(frame, f"Distance: {distance:.2f} cm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Display warning if too close
            if distance < WARNING_DISTANCE:
                self.warning_label.text = "Warning: Too Close!"
                warning_displayed = True

        # Clear warning if no faces are too close
        if not warning_displayed:
            self.warning_label.text = ""

        # Convert image to Kivy texture
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

    def on_go_back(self, instance=None):
        self.capture.release()
        self.go_back_callback()

    def on_stop(self):
        # Release the camera on app stop
        if self.capture.isOpened():
            self.capture.release()

class EyeBlinkMode(BoxLayout):
    def __init__(self, go_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        self.go_back_callback = go_back_callback

        with self.canvas.before:
            Color(0.078, 0.129, 0.239, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Header Section
        header = BoxLayout(size_hint_y=0.1, padding=5, spacing=5)
        title_label = Label(text="Eye Blink Detection Mode", font_size='24sp', bold=True, color=(1, 1, 1, 1))
        header.add_widget(title_label)
        self.add_widget(header)

        # Camera feed display
        self.image = Image(size_hint_y=0.7)
        self.add_widget(self.image)

        # Status label
        self.status_label = Label(text="", font_size='20sp', color=(1, 1, 1, 1), size_hint_y=0.1)
        self.add_widget(self.status_label)

        # Initialize OpenCV video capture
        self.capture = cv2.VideoCapture(0)

        # Footer Section with Buttons
        footer = BoxLayout(size_hint_y=0.1, padding=5, spacing=5)
        back_button = Button(text="Back", size_hint_x=0.3, background_color=(0.89, 0.89, 0.89, 1), font_size='18sp')
        back_button.bind(on_press=self.on_go_back)
        footer.add_widget(Widget())  # Spacer
        footer.add_widget(back_button)
        footer.add_widget(Widget())  # Spacer
        self.add_widget(footer)

        # Load OpenCV Haar Cascade for face and eyes
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')

        # Schedule updates for the camera feed
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def update_frame(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale image
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Draw rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Region of interest (ROI) for eyes
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            # Detect eyes in the ROI
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:  # At least two eyes detected
                self.status_label.text = "Eyes Open"

                # Draw rectangles around eyes
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                
            else:
                self.status_label.text = "Eyes Closed"

        # Convert the frame to a texture for Kivy display
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.image.texture = texture

    def on_go_back(self, instance=None):
        self.capture.release()
        self.go_back_callback()

    def on_stop(self):
        # Release the camera on app stop
        if self.capture.isOpened():
            self.capture.release()


class CameraApp(App):
    def build(self):
        self.root_widget = BoxLayout()
        self.switch_to_menu()
        return self.root_widget

    def switch_to_menu(self, instance=None):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(MainMenu(self.switch_mode))

    def switch_mode(self, mode):
        self.root_widget.clear_widgets()
        if mode == 'distance':
            self.root_widget.add_widget(DistanceMode(self.switch_to_menu))
        elif mode == 'eye':
            self.root_widget.add_widget(EyeBlinkMode(self.switch_to_menu))

if __name__ == '__main__':
    CameraApp().run()
