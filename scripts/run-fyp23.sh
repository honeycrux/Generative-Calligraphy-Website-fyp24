cd fyp23-container

conda run -n fyp23-container --no-capture-output \
    fastapi run app.py --port 6723 --root-path /fyp23

# Equivalent to:
# conda activate fyp23-container
# fastapi run app.py --port 6723 --root-path /fyp23
