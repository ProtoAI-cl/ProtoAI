
FINGERS = {
    "index_finger": "Dedo índice",
    "middle_finger": "Dedo medio",
    "ring_finger": "Dedo anular",
    "pinky_finger": "Dedo meñique",
    "lower_thumb": "Gordo bajo",
    "upper_thumb": "Gordo alto"
}

CLOSE_HAND = [
    {"engine": "index_finger", "value": 1},
    {"engine": "middle_finger", "value": 1},
    {"engine": "ring_finger", "value": 1},
    {"engine": "pinky_finger", "value": 1},
    {"engine": "lower_thumb", "value": 1},
    {"engine": "upper_thumb", "value": 1}
]

OPEN_HAND = [
    {"engine": "upper_thumb", "value": 0},
    {"engine": "lower_thumb", "value": 0},
    {"engine": "index_finger", "value": 0},
    {"engine": "middle_finger", "value": 0},
    {"engine": "ring_finger", "value": 0},
    {"engine": "pinky_finger", "value": 0},
]

PINCH_GRIP = [
    {"engine": "upper_thumb", "value": 1},
    {"engine": "lower_thumb", "value": 0.8},
    {"engine": "index_finger", "value": 0.50},
    {"engine": "middle_finger", "value": 0},
    {"engine": "ring_finger", "value": 0},
    {"engine": "pinky_finger", "value": 0},
]
