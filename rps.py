import cv2
import mediapipe as mp
import random
import time

class HandShapeGame:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
        
        self.player_score = 0
        self.computer_score = 0
        self.rounds_played = 0
        self.last_detection_time = time.time()
        self.round_start_time = time.time()
        self.display_result_until = 0
        
        # Add new state variables for detection window
        self.detection_mode = False
        self.detection_start_time = 0
        self.detection_window = 1.0  # 1 second detection window
        
        self.hand_shapes = {
            'rock': self.is_rock,
            'paper': self.is_paper,
            'scissors': self.is_scissors
        }

    def get_finger_positions(self, landmarks):
        return {finger: landmarks[getattr(self.mp_hands.HandLandmark, finger)].y for finger in dir(self.mp_hands.HandLandmark) if finger.endswith("_TIP")}
    
    def is_rock(self, landmarks):
        positions = self.get_finger_positions(landmarks)
        return (
            positions['INDEX_FINGER_TIP'] > landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
            positions['MIDDLE_FINGER_TIP'] > landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
            positions['RING_FINGER_TIP'] > landmarks[self.mp_hands.HandLandmark.RING_FINGER_PIP].y and
            positions['PINKY_TIP'] > landmarks[self.mp_hands.HandLandmark.PINKY_PIP].y and
            landmarks[self.mp_hands.HandLandmark.THUMB_TIP].x < landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_DIP].x
        )
    
    def is_paper(self, landmarks):
        positions = self.get_finger_positions(landmarks)
        return all(positions[f] < landmarks[getattr(self.mp_hands.HandLandmark, f.replace('_TIP', '_MCP'))].y for f in positions)
    
    def is_scissors(self, landmarks):
        positions = self.get_finger_positions(landmarks)
        return (positions['INDEX_FINGER_TIP'] < landmarks[self.mp_hands.HandLandmark.INDEX_FINGER_MCP].y and
                positions['MIDDLE_FINGER_TIP'] < landmarks[self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y)
    
    def detect_hand_shape(self, landmarks):
        for shape, detector in self.hand_shapes.items():
            if detector(landmarks):
                return shape
        return None
    
    def play_round(self, player_choice):
        computer_choice = random.choice(list(self.hand_shapes.keys()))
        results = {
            ('rock', 'scissors'): "You Win!",
            ('scissors', 'paper'): "You Win!",
            ('paper', 'rock'): "You Win!",
            ('rock', 'paper'): "Computer Wins!",
            ('scissors', 'rock'): "Computer Wins!",
            ('paper', 'scissors'): "Computer Wins!"
        }
        result = results.get((player_choice, computer_choice), "Tie!")
        
        if "You Win" in result:
            self.player_score += 1
        elif "Computer Wins" in result:
            self.computer_score += 1
        
        self.display_result_until = time.time() + 3  # Show result for 3 seconds
        return computer_choice, result
    
    def run_game(self):
        cap = cv2.VideoCapture(0)
        
        # Variables to store the last detected choices and result
        player_choice = None
        computer_choice = None
        game_result = None
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            cv2.putText(frame, f"Player: {self.player_score}  Computer: {self.computer_score}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Calculate remaining time in countdown phase
            timer = int(7 - (time.time() - self.round_start_time))
            
            # Handle different game states
            if timer > 0:
                # Countdown phase
                cv2.putText(frame, f"Get ready: {timer}", (10, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                self.detection_mode = False
                
            elif timer <= 0 and not self.detection_mode:
                # Transition to detection phase
                self.detection_mode = True
                self.detection_start_time = time.time()
                cv2.putText(frame, "SHOW YOUR HAND!", (10, 100),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
            elif self.detection_mode:
                # Active detection phase
                remaining_detection_time = self.detection_window - (time.time() - self.detection_start_time)
                
                if remaining_detection_time > 0:
                    # Still in detection window
                    cv2.putText(frame, f"DETECTING: {remaining_detection_time:.1f}s", (10, 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Process hand landmarks if detected
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                            
                            # Get the current shape (for display only)
                            current_shape = self.detect_hand_shape(hand_landmarks.landmark)
                            if current_shape:
                                cv2.putText(frame, f"Detecting: {current_shape}", (10, 150),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                    
                else:
                    # Detection window ended, determine final hand shape
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            player_choice = self.detect_hand_shape(hand_landmarks.landmark)
                            
                    # If a valid gesture was detected, play the round
                    if player_choice:
                        computer_choice, game_result = self.play_round(player_choice)
                    else:
                        # No valid gesture detected
                        game_result = "No gesture detected!"
                        computer_choice = "None"
                    
                    # Reset for next round
                    self.last_detection_time = time.time()
                    self.round_start_time = time.time()
                    self.detection_mode = False
                    
            # Display round results if within the display time window
            if time.time() < self.display_result_until:
                cv2.putText(frame, f"You: {player_choice} | Computer: {computer_choice}", (10, frame.shape[0] - 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, game_result, (10, frame.shape[0] - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('Hand Shape Rock-Paper-Scissors', frame)
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = HandShapeGame()
    game.run_game()