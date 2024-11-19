# Projection Game
Playing in the real world.

## Description
The goal for this project was to create a Game that is player with your hands using only the RGB webcam in your notebook. For that an algorithm for hand tracking needed to be created that works in realtime while running on Notebooks without a huge GPU.

The result is a playing experience that is more direct as the tracking doesn't require an extra device to be hold, click or move. This makes it more engaging than traditional input methods.

Possible Solutions include Color Tracking of the Hand, Training Models to track the hand position as well as using pre-trained models. The Final decision fell on pre-trained models together with some projection logic, as this resulted in the best accuracy while still having good performance. Specifically the project uses mediapipe hand pose estimation together with some manual cleanup, smoothing and later a set of homography to map the hands to the playing field.

A big problem with the Development was that many models of research papers for pose estimation were either not publicly accessible or not easy to use. This means that there are some potentially better options which just could be tested and therefor were not considered in the final program.

### Evaluation Criterias

To have a good playing experience the **FPS** of the game and the tracking itself are important. The different models (Movenet, Blazepose, yolo4, yolo7, openpose...) were evaluated and compared under these criteria. Multipose, 3D vs 2D tracking and observed accuracy were also taken into account to make the decision.

Performance of the entire program was also evaluated and improved over multiple iterations. For this mainly cProfile was used to create an overview over the different functions and how long they took. Based on this a few points were found where optimization was possible. This included the Camera handler which in turn was turned async and some of the algorithms that could be optimized as well.

For a good feel at least ~20 FPS for the model are needed. Importantly, the 1% lows should be close to this as well because they drastically increase the feel of lag if they are low. The final solution still has some lags but manages to keep the FPS at over 30/second (which is manually limited to 30FPS to keep a stable playing experience).


### Most important Files

`src/game/player_controller/`
* `CameraPlayerPositionManager.py` 
	holds the logic to get the current player position. It also makes the input data smoother to reduce lag and uses Homography to project the player onto the playing field.
* `MovenetHumanPoseEstimator.py`
	Is used by the Games and holds the logic to get the pose of the hands from the current image. For multiplayer (currently not working) it also has the ability to separate the found points into different people.
`src/models`
* `CameraFrame.py`
	Is used to get the Images from the camera. It takes the camera pictures async to decrease the lag produced by the camera. This lag was located using cProfile.
* `Model.py` + `Config.py`
	Are used for the state management and settings.
`src/views`
	Holds the logic for the GUI itself, including view selection, setup and switching between the games.

## Future Developments

In the future more Games can be added making the project even more versatile. Additionally, the second game mode of playing with the feet using a project screen pointed at the floor could make it even more fun and easier to use.
Finally, a multiplayer mode, which is currently only performance limited, would further increase the possible usages. 

(Cleaning up the unused components, which are still present as reference for further development)


## Installation
```
python3.10 -m pip install -r requirements.txt
```


## Usage

```
python3.10 __main__.py
```

First you will see some Setup Views for the camera and playing field.
After that you can select a Game (not all are working, yet).
Enjoy playing, a bit further away makes in easier.

## Dev Setup
```
python3.10 -m pip install -r requirements-dev.txt
```
and then run
```
pre-commit install
pre-commit autoupdate
pre-commit run --all-files
```


## Acknowledgements

Mediapipe Handtracking  
https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python

Homography  
https://docs.opencv.org/4.x/d9/dab/tutorial_homography.html

Tkinter Docs (for the GUI)  
https://tkdocs.com/index.html

cProfile  
https://docs.python.org/3/library/profile.html

snakeviz for cProfile  
https://jiffyclub.github.io/snakeviz/


