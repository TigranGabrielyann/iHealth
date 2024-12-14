# iHealth Demo Application

## **Overview**
The iHealth Demo Application is a Python-based prototype demonstrating:
- **Distance Mode**: Calculates the distance from the camera to the user’s face using real-time video processing.
- **Eye Blink Detection Mode**: Detects whether eyes are open or closed using facial recognition.

---

## **Features**
1. **Distance Estimation**:
   - Detects faces and calculates distance.
   - Displays a warning when the user is too close.
2. **Eye Blink Detection**:
   - Identifies open or closed eyes using Haar cascades.
3. **Interactive UI**:
   - Simple navigation with real-time feedback.

---

## **Installation**

### **Required Packages**
- OpenCV
- Kivy

### **Setup Environment**
Create environment
```
conda create -n iHealth-env python==3.12
```
Activate environment 
```
conda activate iHealth-env 
```
Install packages
```
pip install opencv-python
pip install kivy
```

### **To Run**
Clone the repository 
```
git clone https://github.com/TigranGabrielyann/iHealth.git
```

Go to project directory
```
cd iHealth 
```

To run the code
```
python camera_app.py
```
