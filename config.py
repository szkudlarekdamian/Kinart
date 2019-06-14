# HAND INITIALIZATION
# # Interwał (w sekundach), z jakim sprawdzana będzie obecność dłoni w InitBox
CHECKING_FOR_HAND_INTERVAL = 1

# # Ile razy z rzędu musi zostać znaleziona dłoń w InitBox (powiązane z interwałem powyżej)
HOW_MANY_TIMES_HAND_MUST_BE_FOUND = 5

# # Minimalna wartość odległości z sensorów Kinect, aby obiekt znalazł się w InitBox (im niższa wartość, tym bliżej
# musimy być kamery)
MINIMUM_VALUE_TO_CONSIDER_HAND = 14

# # Maksymalna wartość odległości z sensorów Kinect, aby obiekt znalazł się w InitBox (im wyższa wartość, tym dalej
# # musimy być kamery)
MAXIMUM_VALUE_TO_CONSIDER_HAND = 17

# # Bok kwadratowego wycinka obrazu, z którego zostaje obliczona mediana, przy inicjalizacji dłoni
MEDIAN_SQUARE_SIDE = 30


# BOUNDING BOXES STYLE
# # Kolor kwadratu, wspomagającego inicjalizację dłoni - oznaczony jako InitBox
BOUNDING_BOX_COLOR_INIT = (177, 187, 223)

# # Kolor środka kwadratu, wspomagającego inicjalizację dłoni
CENTER_POINT_COLOR_INIT = (118, 100, 245)

# # Kolor kwadratu, wspomagającego wizualizację śledzenia dłoni - oznaczony jako TrackingBox
BOUNDING_BOX_COLOR_TRACKING = (173, 245, 145)

# # Kolor środka kwadratu, wspomagającego wizualizację śledzenia dłoni
CENTER_POINT_COLOR_TRACKING = (239, 237, 191)

# # Szerokość obramowania, InitBox i TrackingBox
BOUNDING_BOX_BORDER_WIDTH = 4


# HAND TRACKING PARAMETERS
# # Maksymalna wartość odległości z sensorów Kinect, która nie jest usuwana z obrazu
FURTHEST_DISTANCE = 31

# # Minimalna wartość odległości z sensorów Kinect, która nie jest usuwana z obrazu
CLOSEST_DISTANCE = 12


# VISUALS
# # Czy InitBox ma być wyświetlany w trakcie śledzenia dłoni
SHOW_INIT_BOX_DURING_TRACKING = False

# # Czy pomocniczy kontur dłoni ma być wyświetlany w InitBox
SHOW_INIT_HAND_CONTOUR = True
