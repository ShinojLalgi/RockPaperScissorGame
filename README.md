# Rock-Paper-Scissors Game

A real-time Rock-Paper-Scissors using hand gesture detection with **MediaPipe** and **OpenCV**. Play against your computer using just your webcam!

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🚀 Quick Start

```bash
git clone https://github.com/ShinojLalgi/RockPaperScissorGame.git
cd RockPaperScissorGame
pip install opencv-python mediapipe
python rps.py
```

---

## 🎮 How to Play

1. Wait for the **7-second countdown**
2. Show your gesture to the camera:
   - ✊ **Rock**: Closed fist
   - ✋ **Paper**: Open hand  
   - ✌️ **Scissors**: Peace sign
3. Computer picks randomly, winner displayed with scores
4. Press `q` to quit

---

## 🛠 Requirements

- Python 3.7+
- OpenCV 4.5+
- MediaPipe 0.8+
- Webcam

---

## 🧠 How It Works

- **MediaPipe Hands** tracks 21 hand landmarks
- Gesture classification based on finger positions
- Real-time detection with visual feedback
- Standard Rock-Paper-Scissors rules apply

---

## 📁 Files

```
├── rps.py              # Main game file
├── requirements.txt    # Dependencies
└── README.md          # This file
```

---

**Made with ❤️ and Python**
